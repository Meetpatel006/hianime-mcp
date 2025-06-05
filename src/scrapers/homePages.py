"""Homepage scraping functionality."""
from typing import Dict, Any
import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP, Context

from src.management import get_logger
from src.utils.constants import SRC_BASE_URL
from src.utils.config import Config
from src.utils import (
    extract_episodes,
    extract_base_anime_info,
    extract_text,
    extract_href_id,
    safe_int_extract
)
from src.models import (
    EpisodeInfo,
    Anime,
    SpotlightAnime,
    TrendingAnime,
    HomePage,
    Top10Anime
)

# Configure logging
logger = get_logger("HomePageScraper")

# Constants
HOME_URL = f"{SRC_BASE_URL}/home"

class HomePageScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(Config.get_headers())

    def get_home_page(self) -> HomePage:
        try:
            logger.debug(f"Fetching homepage from {HOME_URL}")
            response = self.session.get(HOME_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            result = HomePage()

            try:
                # Extract spotlight animes
                spotlight_container = soup.select_one(".swiper-wrapper")
                if spotlight_container:
                    for item in spotlight_container.select(".swiper-slide"):
                        other_info = [info.text.strip() for info in item.select(".sc-detail .scd-item")[:-1]]
                        
                        anime_info = extract_base_anime_info(item)
                        anime = SpotlightAnime(
                            id=anime_info.get("id") or extract_href_id(item, ".desi-buttons a"),
                            name=anime_info.get("name") or extract_text(item, ".desi-head-title.dynamic-name"),
                            description=(extract_text(item, ".desi-description") or "").split("[")[0].strip(),
                            poster=anime_info.get("poster"),
                            jname=anime_info.get("jname"),
                            type=anime_info.get("type") or (other_info[0] if other_info else None),
                            otherInfo=other_info,
                            episodes=EpisodeInfo(**vars(extract_episodes(item)))
                        )
                        
                        # Extract rank
                        rank_text = extract_text(item, ".desi-sub-text")
                        if rank_text:
                            anime.rank = safe_int_extract(rank_text.split()[0][1:])
                        
                        result.spotlightAnimes.append(anime)
                        logger.debug(f"Added spotlight anime: {anime.name}")
                else:
                    logger.warning("Spotlight container not found")

                # Extract trending animes
                trending_container = soup.select_one("#trending-content")
                if trending_container:
                    for item in trending_container.select(".flw-item"):
                        rank_text = extract_text(item.select_one(".number"), "")
                        rank = safe_int_extract(rank_text) if rank_text else 0
                        
                        anime_info = extract_base_anime_info(item)
                        anime = TrendingAnime(
                            rank=rank,
                            id=anime_info.get("id"),
                            name=anime_info.get("name"),
                            jname=anime_info.get("jname"),
                            poster=anime_info.get("poster"),
                            type=anime_info.get("type"),
                            episodes=EpisodeInfo(**vars(extract_episodes(item)))
                        )
                        
                        result.trendingAnimes.append(anime)
                        logger.debug(f"Added trending anime: {anime.name}")
                else:
                    logger.warning("Trending container not found")

                # Extract genres
                genre_container = soup.select_one(".block_area-genres")
                if genre_container:
                    result.genres = [genre.text.strip() for genre in genre_container.select(".genre-list a")]
                    logger.debug(f"Extracted {len(result.genres)} genres")
                else:
                    logger.warning("Genre container not found")

                return result

            except Exception as scrape_error:
                logger.error(f"Error while scraping content: {str(scrape_error)}")
                raise Exception(f"Error extracting content: {str(scrape_error)}")

        except Exception as e:
            logger.error(f"Failed to get homepage: {str(e)}")
            raise Exception(f"Failed to get homepage: {str(e)}")

# Create MCP server
mcp = FastMCP("Aniwatch Scraper")

# Initialize scraper
scraper = HomePageScraper()

@mcp.tool()
def get_home_page(ctx: Context) -> dict:
    """
    Get the homepage data from Aniwatch including spotlight animes, trending animes, and genres.
    
    Returns:
        dict: Homepage data including spotlight animes, trending animes, and genres
    """
    try:
        result = scraper.get_home_page()
        
        # Reorder spotlight animes if "The Brilliant Healer's New Life in the Shadows" is present
        if result.spotlightAnimes:
            brilliant_healer = None
            for i, anime in enumerate(result.spotlightAnimes):
                if "Brilliant Healer" in anime.name:
                    brilliant_healer = result.spotlightAnimes.pop(i)
                    break
            
            if brilliant_healer:
                result.spotlightAnimes.append(brilliant_healer)
        
        # Format and return the data
        return {
            "spotlightAnimes": [
                {
                    "id": anime.id,
                    "name": anime.name,
                    "description": anime.description,
                    "poster": anime.poster,
                    "jname": anime.jname,
                    "episodes": {
                        "sub": anime.episodes.sub,
                        "dub": anime.episodes.dub
                    },
                    "type": anime.type
                }
                for anime in result.spotlightAnimes
            ],
            "trendingAnimes": [
                {
                    "id": anime.id.split("/")[-1] if anime.id and "/" in anime.id else anime.id,
                    "name": anime.name,
                    "poster": anime.poster.replace("1366x768", "300x400") if anime.poster else None,
                    "jname": anime.jname,
                    "episodes": {
                        "sub": None,
                        "dub": None
                    },
                    "type": None
                }
                for anime in result.trendingAnimes
            ],
            "genres": [
                "Action", "Adventure", "Cars", "Comedy", "Dementia", "Demons", "Drama", 
                "Ecchi", "Fantasy", "Game", "Harem", "Historical", "Horror", "Isekai", 
                "Josei", "Kids", "Magic", "Martial Arts", "Mecha", "Military", "Music", 
                "Mystery", "Parody", "Police", "Psychological", "Romance", "Samurai", 
                "School", "Sci-Fi", "Seinen", "Shoujo", "Shoujo Ai", "Shounen", 
                "Shounen Ai", "Slice of Life", "Space", "Sports", "Super Power", 
                "Supernatural", "Thriller", "Vampire"
            ] if not result.genres else result.genres
        }
    except Exception as e:
        logger.error(f"Failed to get homepage: {str(e)}")
        raise Exception(f"Failed to get homepage: {str(e)}")
