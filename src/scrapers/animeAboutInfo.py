"""Anime details scraping functionality."""
from typing import Dict, Optional, Union
import json
import cloudscraper
from bs4 import BeautifulSoup

from src.management import get_logger
from src.utils.constants import SRC_BASE_URL
from src.utils.config import Config
from src.utils import (
    extract_episodes,
    extract_base_anime_info,
    extract_text,
    extract_attribute,
    extract_href_id,
    safe_int_extract
)
from src.models import (
    AnimeStats,
    AnimeInfo,
    Season,
    RecommendedAnime,
    PromotionalVideo,
    Character,
    VoiceActor,
    CharacterVoiceActor,
    EpisodeInfo
)

# Configure logging
logger = get_logger("AnimeAboutInfo")


def get_anime_about_info(anime_id: str) -> Optional[Dict[str, Union[Dict, bool]]]:
    """Get detailed information about an anime."""
    if not anime_id.strip() or "-" not in anime_id:
        raise ValueError("Invalid anime id")

    # Construct URL properly
    anime_url = f"{SRC_BASE_URL}/{anime_id}"
    logger.debug(f"Fetching URL: {anime_url}")
    
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
        
        # Add comprehensive headers that match the test_advanced.py file
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
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive',
            'DNT': '1'  # Do Not Track
        })
        
        response = scraper.get(anime_url)
        response.raise_for_status()
        
        # Check response status and headers
        logger.debug(f"Status: {response.status_code}")
        logger.debug(f"Content-Type: {response.headers.get('Content-Type', '')}")
        logger.debug(f"Response content length: {len(response.text)}")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')

        # Debug: Save the HTML content for inspection when selector fails
        logger.debug(f"Response content type: {response.headers.get('content-type', 'unknown')}")
        logger.debug(f"Response encoding: {response.encoding}")
        logger.debug(f"HTML content preview (first 500 chars): {response.text[:500]}")

        # Save full HTML for debugging if needed
        try:
            with open(f"debug_anime_{anime_id.replace('/', '_')}.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            logger.debug(f"Saved debug HTML to debug_anime_{anime_id.replace('/', '_')}.html")
        except Exception as e:
            logger.debug(f"Could not save debug HTML: {e}")
        
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
        
        # Extract main content using a more robust approach
        logger.debug("Attempting to find main content section")
        
        # First, try the most reliable selector from test_advanced.py
        content = soup.select_one("#ani_detail .container .anis-content")
        if content:
            logger.debug("Found content with selector: #ani_detail .container .anis-content")
        else:
            logger.debug("Selector #ani_detail .container .anis-content failed. Trying other fallbacks.")
            # Fallback strategies if the primary selector fails
            ani_detail = soup.select_one("#ani_detail")
            if ani_detail:
                logger.debug("Found #ani_detail section. Trying child selectors.")
                # Try to find anis-content directly in ani_detail
                content = ani_detail.select_one(".anis-content")
                if content:
                    logger.debug("Found content with selector: #ani_detail .anis-content")
                else:
                    # Try ani_detail-stage > anis-content
                    ani_detail_stage = ani_detail.select_one(".ani_detail-stage")
                    if ani_detail_stage:
                        content = ani_detail_stage.select_one(".anis-content")
                        if content:
                            logger.debug("Found content with selector: #ani_detail .ani_detail-stage .anis-content")
                        else:
                            # Try to find container in ani_detail-stage then anis-content
                            container = ani_detail_stage.select_one(".container")
                            if container:
                                content = container.select_one(".anis-content")
                                if content:
                                    logger.debug("Found content with selector: #ani_detail .ani_detail-stage .container .anis-content")
            else:
                # If ani_detail not found, try to find anis-content directly in the soup
                logger.debug("#ani_detail section not found. Trying .anis-content globally.")
                content = soup.select_one(".anis-content")
                if content:
                    logger.debug("Found content with global selector: .anis-content")

            # If still not found, try the aggressive approach (walking up from .film-poster)
            if not content:
                logger.debug("Standard selectors failed, trying more aggressive approach by walking up from .film-poster")
                film_poster = soup.select_one(".film-poster")
                if film_poster:
                    parent = film_poster.parent
                    while parent and parent.name != 'body':
                        if 'anis-content' in parent.get('class', []):
                            content = parent
                            logger.debug("Found content by walking up from .film-poster")
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
                        "jname": None,
                        "poster": None,
                        "type": None,
                        "duration": None,
                        "episodes": {
                            "sub": None,
                            "dub": None,
                            "total": None
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
                    
                    # Extract poster - match test_advanced.py selector
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
            
            logger.debug(f"Successfully extracted anime info for: {result['data']['anime']['info']['name']}")
            return result
        else:
            logger.warning("Could not find main content section")
            logger.debug(f"Page title: {soup.title.text if soup.title else 'No title found'}")
            
            # Log some basic page structure for debugging
            main_sections = soup.select("div[id], section[id], main[id]")
            logger.debug(f"Found main sections: {[elem.get('id', elem.name) for elem in main_sections[:10]]}")

            # Check if ani_detail exists but anis-content is missing
            ani_detail = soup.select_one("#ani_detail")
            if ani_detail:
                logger.debug("Found #ani_detail section")
                # Log the structure of ani_detail
                logger.debug(f"ani_detail children: {[child.name for child in ani_detail.children if child.name]}")
                
                # Check for container
                container = ani_detail.select_one(".container")
                if container:
                    logger.debug("Found .container in #ani_detail")
                    logger.debug(f"container children: {[child.name for child in container.children if child.name]}")
                
                # Check for ani_detail-stage
                ani_detail_stage = ani_detail.select_one(".ani_detail-stage")
                if ani_detail_stage:
                    logger.debug("Found .ani_detail-stage in #ani_detail")
                    logger.debug(f"ani_detail-stage children: {[child.name for child in ani_detail_stage.children if child.name]}")
                
                # Look for any content-related classes
                content_classes = ani_detail.select("[class*=content], [class*=detail], [class*=info]")
                logger.debug(f"Found content-related classes: {[elem.get('class') for elem in content_classes[:5]]}")
            else:
                logger.debug("Could not find #ani_detail section")
                
                # Try to find any anime-related elements
                anime_elements = soup.select(".film-poster, .film-name, .film-stats, .film-description")
                if anime_elements:
                    logger.debug(f"Found anime-related elements: {[elem.name for elem in anime_elements[:5]]}")
                    logger.debug(f"First anime element parents: {[parent.name for parent in anime_elements[0].parents if parent.name != 'html' and parent.name != 'body'][:3]}")
            
            # Try to save the HTML for debugging
            try:
                debug_filename = f"debug_anime_{anime_id.replace('/', '_')}_error.html"
                with open(debug_filename, "w", encoding="utf-8") as f:
                    f.write(response.text)
                logger.debug(f"Saved debug HTML to {debug_filename}")
            except Exception as e:
                logger.debug(f"Could not save debug HTML: {e}")
            
            # Return a structured error result instead of None
            # Enhanced error message
            error_message = "Could not find anime content section using any known selectors."
            # Check if the primary selector was specifically the point of failure earlier
            # (This check is implicitly handled by the refined selector logic and logging)
            # The logging already shows the sequence of attempts.
            # We can make the returned error message more direct.

            # If the first selector tried was the specific one from test_advanced.py and it failed,
            # we can reflect this. However, the previous step already made that the first attempt.
            # The existing logs will show "Selector #ani_detail .container .anis-content failed."
            # So, the generic message is appropriate here as it means ALL attempts failed.

            return {
                "success": False,
                "error": error_message, # Keep it general as all selectors failed
                "anime_id": anime_id,
                "url": anime_url,
                "debug_html_file": f"debug_anime_{anime_id.replace('/', '_')}_error.html" # Add filename to output
            }
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    # Test with a known anime ID.
    # Replace with an ID that was previously failing if known,
    # otherwise use a common one.
    test_anime_id = "attack-on-titan-112"  # Example ID
    logger.info(f"Attempting to fetch info for anime ID: {test_anime_id}")

    # Ensure logger is configured for standalone execution
    from src.management import setup_logging
    setup_logging() # Call this if not already configured globally for standalone script run

    try:
        info = get_anime_about_info(test_anime_id)
        if info and info.get("success"):
            logger.info(f"Successfully fetched data for {test_anime_id}:")
            import json
            print(json.dumps(info, indent=2))
        elif info:
            logger.error(f"Failed to fetch data for {test_anime_id}:")
            import json
            print(json.dumps(info, indent=2))
        else:
            logger.error(f"No information returned for {test_anime_id} (function returned None).")
    except ValueError as ve:
        logger.error(f"ValueError during test: {ve}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during test: {e}", exc_info=True)