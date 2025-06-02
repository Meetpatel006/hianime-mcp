import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP, Context

# Constants
BASE_URL = "https://hianimez.to"
HOME_URL = f"{BASE_URL}/home"

# Data classes for type safety
@dataclass
class AnimeEpisodes:
    sub: Optional[int] = None
    dub: Optional[int] = None

@dataclass
class SpotlightAnime:
    rank: Optional[int] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    poster: Optional[str] = None
    jname: Optional[str] = None  # Japanese name
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
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_home_page(self) -> HomePage:
        try:
            response = self.session.get(HOME_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            result = HomePage(
                spotlightAnimes=[],
                trendingAnimes=[],
                latestEpisodeAnimes=[],
                topUpcomingAnimes=[],
                top10Animes=Top10Anime(),
                topAiringAnimes=[],
                mostPopularAnimes=[],
                mostFavoriteAnimes=[],
                latestCompletedAnimes=[],
                genres=[]
            )

            # Extract spotlight animes
            spotlight_items = soup.select("#slider .swiper-wrapper .swiper-slide")
            for item in spotlight_items:
                other_info = [info.text.strip() for info in item.select(".deslide-item-content .sc-detail .scd-item")[:-1]]
                
                rank_text = item.select_one(".deslide-item-content .desi-sub-text")
                rank = int(rank_text.text.strip().split()[0][1:]) if rank_text else None
                
                anime = SpotlightAnime(
                    rank=rank,
                    id=item.select_one(".deslide-item-content .desi-buttons a")["href"].strip("/"),
                    name=item.select_one(".deslide-item-content .desi-head-title.dynamic-name").text.strip(),
                    description=item.select_one(".deslide-item-content .desi-description").text.split("[")[0].strip(),
                    poster=item.select_one(".deslide-cover .deslide-cover-img .film-poster-img")["data-src"].strip(),
                    jname=item.select_one(".deslide-item-content .desi-head-title.dynamic-name")["data-jname"].strip(),
                    type=other_info[0] if other_info else None,
                    otherInfo=other_info
                )
                
                # Extract episodes
                sub_ep = item.select_one(".deslide-item-content .sc-detail .scd-item .tick-item.tick-sub")
                dub_ep = item.select_one(".deslide-item-content .sc-detail .scd-item .tick-item.tick-dub")
                
                anime.episodes = AnimeEpisodes(
                    sub=int(sub_ep.text.strip()) if sub_ep else None,
                    dub=int(dub_ep.text.strip()) if dub_ep else None
                )
                
                result.spotlightAnimes.append(anime)

            # Extract trending animes
            trending_items = soup.select("#trending-home .swiper-wrapper .swiper-slide")
            for item in trending_items:
                rank = int(item.select_one(".item .number").find().text.strip())
                
                # Extract episodes
                sub_ep = item.select_one(".item .tick-item.tick-sub")
                dub_ep = item.select_one(".item .tick-item.tick-dub")
                
                anime = TrendingAnime(
                    rank=rank,
                    id=item.select_one(".item .film-poster")["href"].strip("/"),
                    name=item.select_one(".item .number .film-title.dynamic-name").text.strip(),
                    jname=item.select_one(".item .number .film-title.dynamic-name")["data-jname"].strip(),
                    poster=item.select_one(".item .film-poster .film-poster-img")["data-src"].strip(),
                    episodes=AnimeEpisodes(
                        sub=int(sub_ep.text.strip()) if sub_ep else None,
                        dub=int(dub_ep.text.strip()) if dub_ep else None
                    ),
                    type=item.select_one(".item .fd-infor .tick-item.tick-type").text.strip() if item.select_one(".item .fd-infor .tick-item.tick-type") else None
                )
                result.trendingAnimes.append(anime)

            # Extract genres
            genre_items = soup.select("#main-sidebar .block_area.block_area_sidebar.block_area-genres .sb-genre-list li")
            result.genres = [genre.text.strip() for genre in genre_items]

            return result

        except Exception as e:
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
        raise Exception(f"Failed to get homepage: {str(e)}")

