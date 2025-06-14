import cloudscraper
import json
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_anime_info(anime_id):
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )
    
    # Set headers
    scraper.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    })
    
    url = f"https://hianime.sx/{anime_id}"
    logger.debug(f"Fetching URL: {url}")
    
    try:
        # Make the request
        response = scraper.get(url)
        response.raise_for_status()
        
        # Check response status and headers
        logger.debug(f"Status: {response.status_code}")
        logger.debug(f"Headers: {dict(response.headers)}")
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        logger.debug(f"Content-Type: {content_type}")
        
        # Save full response content for debugging
        with open("anime_sample.txt", "w", encoding='utf-8') as f:
            f.write(response.text)
        logger.debug(f"Wrote {len(response.text)} bytes to anime_sample.txt")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Initialize result structure
        result = {
            "success": True,
            "data": {
                "anime": {
                    "info": {
                        "id": anime_id,
                        "anilistId": None,
                        "malId": None,
                        "name": None,
                        "poster": None,
                        "description": None,
                        "stats": {
                            "rating": None,
                            "quality": None,
                            "episodes": {
                                "sub": None,
                                "dub": None
                            },
                            "type": None,
                            "duration": None
                        },
                        "promotionalVideos": [],
                        "charactersVoiceActors": []
                    },
                    "moreInfo": {
                        "genres": [],
                        "studios": []
                    }
                },
                "seasons": [],
                "mostPopularAnimes": [],
                "relatedAnimes": [],
                "recommendedAnimes": []
            }
        }
        
        # Extract sync data for IDs
        sync_data = soup.find("script", id="syncData")
        if sync_data and sync_data.text:
            try:
                sync_json = json.loads(sync_data.text)
                result["data"]["anime"]["info"]["anilistId"] = int(sync_json.get("anilist_id", 0)) or None
                result["data"]["anime"]["info"]["malId"] = int(sync_json.get("mal_id", 0)) or None
            except json.JSONDecodeError:
                logger.warning("Failed to parse sync data as JSON")
        
        # Extract main content
        content = soup.select_one("#ani_detail .container .anis-content")
        if content:
            # Basic info
            name_elem = content.select_one(".anisc-detail .film-name.dynamic-name")
            if name_elem:
                result["data"]["anime"]["info"]["name"] = name_elem.text.strip()
            
            desc_elem = content.select_one(".anisc-detail .film-description .text")
            if desc_elem:
                result["data"]["anime"]["info"]["description"] = desc_elem.text.strip()
            
            # Extract poster
            poster_elem = content.select_one(".film-poster .film-poster-img")
            if poster_elem:
                if "src" in poster_elem.attrs:
                    result["data"]["anime"]["info"]["poster"] = poster_elem["src"].strip()
                elif "data-src" in poster_elem.attrs:
                    result["data"]["anime"]["info"]["poster"] = poster_elem["data-src"].strip()
            
            # Stats
            stats = content.select_one(".film-stats")
            if stats:
                # Rating
                tick_pg = stats.select_one(".tick .tick-pg")
                if tick_pg:
                    result["data"]["anime"]["info"]["stats"]["rating"] = tick_pg.text.strip()
                
                # Quality
                tick_quality = stats.select_one(".tick .tick-quality")
                if tick_quality:
                    result["data"]["anime"]["info"]["stats"]["quality"] = tick_quality.text.strip()
                
                # Type and Duration
                tick_type = stats.select_one(".tick")
                if tick_type:
                    type_text = tick_type.text.strip().replace("\n", " ").split()
                    if len(type_text) >= 2:
                        result["data"]["anime"]["info"]["stats"]["type"] = type_text[-2]
                        result["data"]["anime"]["info"]["stats"]["duration"] = type_text[-1]
                
                # Episodes
                sub_eps = stats.select_one(".tick .tick-sub")
                dub_eps = stats.select_one(".tick .tick-dub")
                
                if sub_eps:
                    try:
                        result["data"]["anime"]["info"]["stats"]["episodes"]["sub"] = int(sub_eps.text.strip())
                    except ValueError:
                        pass
                
                if dub_eps:
                    try:
                        result["data"]["anime"]["info"]["stats"]["episodes"]["dub"] = int(dub_eps.text.strip())
                    except ValueError:
                        pass
            
            # Extract genres
            genres = content.select(".anisc-info .item-list a")
            if genres:
                result["data"]["anime"]["moreInfo"]["genres"] = [genre.text.strip() for genre in genres]
            
            # Extract studios
            studios = content.select(".anisc-info .item-title a.name")
            if studios:
                result["data"]["anime"]["moreInfo"]["studios"] = [studio.text.strip() for studio in studios]
            
            # Extract seasons
            seasons = soup.select(".block_area-seasons .os-item")
            if seasons:
                for season in seasons:
                    season_obj = {
                        "id": None,
                        "name": None,
                        "title": None,
                        "poster": None,
                        "isCurrent": False
                    }
                    
                    # Extract season ID
                    season_link = season.select_one("a")
                    if season_link and "href" in season_link.attrs:
                        season_obj["id"] = season_link["href"].strip("/")
                    
                    # Extract season name
                    name = season.select_one(".title")
                    if name:
                        season_obj["title"] = name.text.strip()
                        season_obj["name"] = name.text.strip()
                    
                    # Extract season poster
                    poster = season.select_one(".season-poster")
                    if poster and "style" in poster.attrs:
                        style = poster["style"]
                        if "background-image: url(" in style:
                            season_obj["poster"] = style.split("url(")[1].split(")")[0].strip("'\"")
                    
                    if "active" in season.get("class", []):
                        season_obj["isCurrent"] = True
                    
                    result["data"]["seasons"].append(season_obj)
            
            # Extract characters and voice actors
            characters = soup.select(".block-actors-content .bac-item")
            if characters:
                for char in characters:
                    char_name = char.select_one(".pi-name a")
                    char_role = char.select_one(".pi-cast")
                    voice_actor_name = char.select_one(".per-info.rtl .pi-detail a")
                    voice_actor_role = char.select_one(".per-info.rtl .pi-cast")
                    
                    if char_name and char_role:
                        # Extract character ID from href
                        char_id = ""
                        if "href" in char_name.attrs:
                            href = char_name["href"]
                            if href.startswith("/character/"):
                                char_id = href.split("/")[-1]
                        
                        # Extract voice actor ID from href
                        va_id = ""
                        if voice_actor_name and "href" in voice_actor_name.attrs:
                            va_href = voice_actor_name["href"]
                            if va_href.startswith("/people/"):
                                va_id = va_href.split("/")[-1]
                        
                        char_obj = {
                            "character": {
                                "id": char_id,
                                "poster": "",
                                "name": char_name.text.strip(),
                                "cast": char_role.text.strip()
                            },
                            "voiceActor": {
                                "id": va_id,
                                "poster": "",
                                "name": voice_actor_name.text.strip() if voice_actor_name else "",
                                "cast": voice_actor_role.text.strip() if voice_actor_role else ""
                            }
                        }
                        
                        # Extract character poster
                        char_poster = char.select_one(".per-info.ltr .pi-avatar img")
                        if char_poster and "data-src" in char_poster.attrs:
                            char_obj["character"]["poster"] = char_poster["data-src"].strip()
                        
                        # Extract voice actor poster
                        va_poster = char.select_one(".per-info.rtl .pi-avatar img")
                        if va_poster and "data-src" in va_poster.attrs:
                            char_obj["voiceActor"]["poster"] = va_poster["data-src"].strip()
                        
                        result["data"]["anime"]["info"]["charactersVoiceActors"].append(char_obj)
            
            # Extract promotional videos
            promos = soup.select(".block_area-promotions-list .item")
            if promos:
                for promo in promos:
                    title = promo.select_one(".sii-title")
                    if title:
                        promo_obj = {
                            "title": title.text.strip(),
                            "source": None,
                            "thumbnail": None
                        }
                        
                        # Extract promo source
                        if "data-src" in promo.attrs:
                            promo_obj["source"] = promo["data-src"].strip()
                        
                        # Extract promo thumbnail
                        thumbnail = promo.select_one("img")
                        if thumbnail and "src" in thumbnail.attrs:
                            promo_obj["thumbnail"] = thumbnail["src"].strip()
                        
                        result["data"]["anime"]["info"]["promotionalVideos"].append(promo_obj)
            
            # Extract recommended anime
            recommended = soup.select(".block_area_category .flw-item")
            if recommended:
                for rec in recommended:
                    rec_obj = {
                        "id": None,
                        "name": None,
                        "poster": None,
                        "type": None,
                        "episodes": {
                            "sub": None,
                            "dub": None
                        }
                    }
                    
                    # Extract full ID from href
                    name_link = rec.select_one(".film-name .dynamic-name")
                    if name_link and "href" in name_link.attrs:
                        href = name_link["href"]
                        if href.startswith("/"):
                            rec_obj["id"] = href.strip("/")
                    
                    # Extract name and Japanese name
                    if name_link:
                        rec_obj["name"] = name_link.text.strip()
                        if "data-jname" in name_link.attrs:
                            rec_obj["jname"] = name_link["data-jname"].strip()
                    
                    # Extract poster
                    poster = rec.select_one(".film-poster-img")
                    if poster and "data-src" in poster.attrs:
                        rec_obj["poster"] = poster["data-src"].strip()
                    
                    # Extract type and duration
                    type_elem = rec.select_one(".fd-infor .fdi-item")
                    duration_elem = rec.select_one(".fd-infor .fdi-duration")
                    
                    if type_elem:
                        rec_obj["type"] = type_elem.text.strip()
                    if duration_elem:
                        rec_obj["duration"] = duration_elem.text.strip()
                    
                    # Extract episodes
                    sub_eps = rec.select_one(".tick .tick-sub")
                    dub_eps = rec.select_one(".tick .tick-dub")
                    total_eps = rec.select_one(".tick .tick-eps")
                    
                    if sub_eps:
                        try:
                            rec_obj["episodes"]["sub"] = int(sub_eps.text.strip())
                        except ValueError:
                            pass
                    
                    if dub_eps:
                        try:
                            rec_obj["episodes"]["dub"] = int(dub_eps.text.strip())
                        except ValueError:
                            pass
                    
                    if total_eps:
                        try:
                            rec_obj["episodes"]["total"] = int(total_eps.text.strip())
                        except ValueError:
                            pass
                    
                    result["data"]["recommendedAnimes"].append(rec_obj)
            
            return result
        else:
            logger.warning("Could not find main content section")
            return None
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    result = get_anime_info("attack-on-titan-112")
    if result:
        print("\nExtracted Anime Information:")
        print(json.dumps(result, indent=2))
