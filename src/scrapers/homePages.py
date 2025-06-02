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

            # Extract spotlight animes
            for item in soup.select("#slider .swiper-wrapper .swiper-slide"):
                other_info = [info.text.strip() for info in item.select(".deslide-item-content .sc-detail .scd-item")[:-1]]
                
                anime_info = extract_base_anime_info(item)
                anime = SpotlightAnime(
                    id=anime_info.get("id") or extract_href_id(item, ".deslide-item-content .desi-buttons a"),
                    name=anime_info.get("name") or extract_text(item, ".deslide-item-content .desi-head-title.dynamic-name"),
                    description=(extract_text(item, ".deslide-item-content .desi-description") or "").split("[")[0].strip(),
                    poster=anime_info.get("poster"),
                    jname=anime_info.get("jname"),
                    type=anime_info.get("type") or (other_info[0] if other_info else None),
                    otherInfo=other_info,
                    episodes=EpisodeInfo(**vars(extract_episodes(item)))
                )
                
                # Extract rank
                rank_text = extract_text(item, ".deslide-item-content .desi-sub-text")
                if rank_text:
                    anime.rank = safe_int_extract(rank_text.split()[0][1:])
                
                result.spotlightAnimes.append(anime)
                logger.debug(f"Added spotlight anime: {anime.name}")

            # Extract trending animes
            for item in soup.select("#trending-home .swiper-wrapper .swiper-slide"):
                rank_text = extract_text(item.select_one(".item .number"), "")
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

            # Extract genres
            genre_items = soup.select("#main-sidebar .block_area.block_area_sidebar.block_area-genres .sb-genre-list li")
            result.genres = [genre.text.strip() for genre in genre_items]
            logger.debug(f"Extracted {len(result.genres)} genres")

            return result

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
        return {
            "spotlight_animes": [
                {
                    "rank": anime.rank,
                    "id": anime.id,
                    "name": anime.name,
                    "description": anime.description,
                    "poster": anime.poster,
                    "jname": anime.jname,
                    "episodes": {
                        "sub": anime.episodes.sub,
                        "dub": anime.episodes.dub
                    },
                    "type": anime.type,
                    "other_info": anime.otherInfo
                }
                for anime in result.spotlightAnimes
            ],
            "trending_animes": [
                {
                    "rank": anime.rank,
                    "id": anime.id,
                    "name": anime.name,
                    "jname": anime.jname,
                    "poster": anime.poster
                }
                for anime in result.trendingAnimes
            ],
            "genres": result.genres
        }
    except Exception as e:
        logger.error(f"Failed to get homepage: {str(e)}")
        raise Exception(f"Failed to get homepage: {str(e)}")
