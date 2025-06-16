"""Anime details scraping functionality."""
from typing import Dict, Optional, Union
import json
import cloudscraper
from bs4 import BeautifulSoup

from src.management import get_logger
from src.utils.constants import SRC_BASE_URL
from src.utils.config import Config

# Configure logging
logger = get_logger("AnimeAboutInfo")


def get_anime_about_info(anime_id: str) -> Optional[Dict[str, Union[Dict, bool]]]:
    """Get detailed information about an anime."""
    if not anime_id.strip() or "-" not in anime_id:
        raise ValueError("Invalid anime id")

    # Construct URL properly
    anime_url = f"{SRC_BASE_URL}/{anime_id}"
    
    try:
        # Use cloudscraper to bypass Cloudflare protection with more robust settings
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            },
            delay=10,  # Add delay to avoid rate limiting
            interpreter='js2py'  # Use js2py interpreter for better compatibility
        )
        
        scraper.headers.update(Config.get_headers())
        
        response = scraper.get(anime_url)
        response.raise_for_status()
        
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
                "seasons": []
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
        
        # Extract main content using multiple selector strategies
        content = soup.select_one("#ani_detail .container .anis-content")
        
        if not content:
            # Fallback strategies if the primary selector fails
            ani_detail = soup.select_one("#ani_detail")
            if ani_detail:
                # Try to find anis-content directly in ani_detail
                content = ani_detail.select_one(".anis-content")
                if not content:
                    # Try ani_detail-stage > anis-content
                    ani_detail_stage = ani_detail.select_one(".ani_detail-stage")
                    if ani_detail_stage:
                        content = ani_detail_stage.select_one(".anis-content")
                        if not content:
                            # Try to find container in ani_detail-stage then anis-content
                            container = ani_detail_stage.select_one(".container")
                            if container:
                                content = container.select_one(".anis-content")
            else:
                # If ani_detail not found, try to find anis-content directly in the soup
                content = soup.select_one(".anis-content")

            # If still not found, try the aggressive approach (walking up from .film-poster)
            if not content:
                film_poster = soup.select_one(".film-poster")
                if film_poster:
                    parent = film_poster.parent
                    while parent and parent.name != 'body':
                        if 'anis-content' in parent.get('class', []):
                            content = parent
                            break
                        parent = parent.parent

        if content:
            # Basic info
            name_elem = content.select_one(".anisc-detail .film-name.dynamic-name")
            if name_elem:
                result["data"]["anime"]["info"]["name"] = name_elem.text.strip()
            
            desc_elem = content.select_one(".anisc-detail .film-description .text")
            if desc_elem:
                result["data"]["anime"]["info"]["description"] = desc_elem.text.strip()
            
            # Extract poster - ensure we're using the same selector as test_advanced.py
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
                
                # Type and Duration - use the method from test_advanced.py
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
                    result["data"]["anime"]["info"]["stats"]["episodes"]["sub"] = int(sub_eps.text.strip())
                
                if dub_eps:    
                    result["data"]["anime"]["info"]["stats"]["episodes"]["dub"] = int(dub_eps.text.strip())
                    
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

            
            return result
        else:
            logger.warning("Could not find main content section")
            return {
                "success": False,
                "error": "Could not find anime content section using any known selectors.",
                "anime_id": anime_id,
                "url": anime_url
            }
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

# if __name__ == "__main__":
#     # Test with a known anime ID.
#     # Replace with an ID that was previously failing if known,
#     # otherwise use a common one.
#     test_anime_id = "attack-on-titan-112"  # Example ID
#     logger.info(f"Attempting to fetch info for anime ID: {test_anime_id}")

#     # Ensure logger is configured for standalone execution
#     try:
#         info = get_anime_about_info(test_anime_id)
#         if info and info.get("success"):
#              logger.info(f"Successfully fetched data for {test_anime_id}:")
#              import json
#              print(json.dumps(info, indent=2))
#         elif info:
#              logger.error(f"Failed to fetch data for {test_anime_id}:")
#              import json
#              print(json.dumps(info, indent=2))
#         else:
#              logger.error(f"No information returned for {test_anime_id} (function returned None).")
#     except ValueError as ve:
#          logger.error(f"ValueError during test: {ve}")
#     except Exception as e:
#          logger.error(f"An unexpected error occurred during test: {e}", exc_info=True)
