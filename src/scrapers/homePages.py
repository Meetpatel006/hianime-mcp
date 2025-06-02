from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP, Context

from src.management import get_logger
from src.utils.constants import SRC_BASE_URL
from src.utils.config import Config
from src.utils import (
    EpisodeInfo as BaseEpisodeInfo,
    extract_episodes,
    extract_base_anime_info,
    extract_text,
    extract_attribute,
    extract_href_id,
    safe_int_extract
)

# Configure logging
logger = get_logger("HomePageScraper")

# Constants
HOME_URL = f"{SRC_BASE_URL}/home"

# Data classes for type safety
@dataclass
class AnimeEpisodes(BaseEpisodeInfo):
    """Extend base episode info for compatibility."""
    pass

@dataclass
class SpotlightAnime:
    rank: Optional[int] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    poster: Optional[str] = None
    jname: Optional[str] = None
    episodes: AnimeEpisodes = field(default_factory=AnimeEpisodes)
    type: Optional[str] = None
    otherInfo: List[str] = field(default_factory=list)

@dataclass
class TrendingAnime:
    rank: int
    id: Optional[str] = None
    name: Optional[str] = None
    jname: Optional[str] = None
    poster: Optional[str] = None
    episodes: AnimeEpisodes = field(default_factory=AnimeEpisodes)
    type: Optional[str] = None

@dataclass
class Anime:
    id: Optional[str] = None
    name: Optional[str] = None
    jname: Optional[str] = None
    poster: Optional[str] = None
    duration: Optional[str] = None
    type: Optional[str] = None
    rating: Optional[str] = None
    episodes: AnimeEpisodes = field(default_factory=AnimeEpisodes)

@dataclass
class Top10Anime:
    today: List[Anime] = field(default_factory=list)
    week: List[Anime] = field(default_factory=list)
    month: List[Anime] = field(default_factory=list)

@dataclass
class HomePage:
    spotlightAnimes: List[SpotlightAnime] = field(default_factory=list)
    trendingAnimes: List[TrendingAnime] = field(default_factory=list)
    latestEpisodeAnimes: List[Anime] = field(default_factory=list)
    topUpcomingAnimes: List[Anime] = field(default_factory=list)
    top10Animes: Top10Anime = field(default_factory=Top10Anime)
    topAiringAnimes: List[Anime] = field(default_factory=list)
    mostPopularAnimes: List[Anime] = field(default_factory=list)
    mostFavoriteAnimes: List[Anime] = field(default_factory=list)
    latestCompletedAnimes: List[Anime] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)

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
                    episodes=AnimeEpisodes(**vars(extract_episodes(item)))
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
                rank = safe_int_extract(rank_text) if rank_text else None
                
                if not rank:
                    continue
                
                anime_info = extract_base_anime_info(item)
                anime = TrendingAnime(
                    rank=rank,
                    id=anime_info.get("id"),
                    name=anime_info.get("name"),
                    jname=anime_info.get("jname"),
                    poster=anime_info.get("poster"),
                    type=anime_info.get("type"),
                    episodes=AnimeEpisodes(**vars(extract_episodes(item)))
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
