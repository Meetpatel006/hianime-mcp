from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
import requests
from bs4 import BeautifulSoup
import json
import cloudscraper

from src.management import get_logger
from src.utils.constants import SRC_BASE_URL, USER_AGENT_HEADER, ACCEPT_HEADER, ACCEPT_ENCODING_HEADER
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
logger = get_logger("AnimeAboutInfo")

@dataclass
class AnimeStats:
    rating: Optional[str] = None
    quality: Optional[str] = None
    episodes: Dict[str, Optional[int]] = field(default_factory=lambda: {"sub": None, "dub": None})
    type: Optional[str] = None
    duration: Optional[str] = None

@dataclass
class PromotionalVideo:
    title: Optional[str] = None
    source: Optional[str] = None
    thumbnail: Optional[str] = None

@dataclass
class Character:
    id: str = ""
    poster: str = ""
    name: str = ""
    cast: str = ""

@dataclass
class VoiceActor:
    id: str = ""
    poster: str = ""
    name: str = ""
    cast: str = ""

@dataclass
class CharacterVoiceActor:
    character: Character
    voiceActor: VoiceActor

@dataclass
class AnimeInfo:
    id: Optional[str] = None
    anilistId: Optional[int] = None
    malId: Optional[int] = None
    name: Optional[str] = None
    poster: Optional[str] = None
    description: Optional[str] = None
    stats: AnimeStats = field(default_factory=AnimeStats)
    promotionalVideos: List[PromotionalVideo] = field(default_factory=list)
    charactersVoiceActors: List[CharacterVoiceActor] = field(default_factory=list)

@dataclass
class Season:
    id: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    poster: Optional[str] = None
    isCurrent: bool = False

@dataclass
class RecommendedAnime:
    id: Optional[str] = None
    name: Optional[str] = None
    jname: Optional[str] = None
    poster: Optional[str] = None
    type: Optional[str] = None
    duration: Optional[str] = None
    episodes: Dict[str, Optional[int]] = field(default_factory=lambda: {"sub": None, "dub": None, "total": None})

@dataclass
class AnimeAboutInfo:
    success: bool = True
    data: Dict[str, Union[Dict[str, Union[AnimeInfo, Dict[str, List[str]]]], List[Union[Season, RecommendedAnime]]]] = field(default_factory=lambda: {
        "anime": {
            "info": AnimeInfo(),
            "moreInfo": {
                "genres": [],
                "studios": []
            }
        },
        "seasons": [],
        "mostPopularAnimes": [],
        "relatedAnimes": [],
        "recommendedAnimes": []
    })

def extract_season_info(element: BeautifulSoup) -> Season:
    """Extract season information from HTML element."""
    season = Season()
    
    # Extract season ID
    season.id = extract_href_id(element, "a")
    
    # Extract season name/title
    name = extract_text(element, ".title")
    if name:
        season.title = name
        season.name = name
    
    # Extract season poster
    poster_elem = element.select_one(".season-poster")
    if poster_elem and "style" in poster_elem.attrs:
        style = poster_elem["style"]
        if "background-image: url(" in style:
            season.poster = style.split("url(")[1].split(")")[0].strip("'\"")
    
    # Check if current season
    season.isCurrent = "active" in element.get("class", [])
    
    return season

def extract_character_voice_actor(element: BeautifulSoup) -> Optional[CharacterVoiceActor]:
    """Extract character and voice actor information from HTML element."""
    char_name = extract_text(element, ".pi-name a")
    char_role = extract_text(element, ".pi-cast")
    
    if not (char_name and char_role):
        return None
    
    # Extract character info
    char = Character(
        id=extract_href_id(element, ".pi-name a") or "",
        name=char_name,
        cast=char_role,
        poster=extract_attribute(element, ".per-info.ltr .pi-avatar img", "data-src") or ""
    )
    
    # Extract voice actor info
    va = VoiceActor(
        id=extract_href_id(element, ".per-info.rtl .pi-detail a") or "",
        name=extract_text(element, ".per-info.rtl .pi-detail a") or "",
        cast=extract_text(element, ".per-info.rtl .pi-cast") or "",
        poster=extract_attribute(element, ".per-info.rtl .pi-avatar img", "data-src") or ""
    )
    
    return CharacterVoiceActor(character=char, voiceActor=va)

def extract_promotional_video(element: BeautifulSoup) -> Optional[PromotionalVideo]:
    """Extract promotional video information from HTML element."""
    title = extract_text(element, ".sii-title")
    if not title:
        return None
    
    return PromotionalVideo(
        title=title,
        source=element.get("data-src", "").strip(),
        thumbnail=extract_attribute(element, "img", "src")
    )

def get_anime_about_info(anime_id: str) -> AnimeAboutInfo:
    """Get detailed information about an anime."""
    if not anime_id.strip() or "-" not in anime_id:
        raise ValueError("Invalid anime id")

    # Construct URL properly
    anime_url = f"{SRC_BASE_URL}/{anime_id}"
    logger.debug(f"Fetching URL: {anime_url}")
    
    try:
        # Use cloudscraper to bypass Cloudflare protection
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        # Set headers
        scraper.headers.update({
            'User-Agent': USER_AGENT_HEADER,
            'Accept': ACCEPT_HEADER,
            'Accept-Encoding': ACCEPT_ENCODING_HEADER,
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
        
        response = scraper.get(anime_url)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')
        result = AnimeAboutInfo()
        
        # Set the anime id field
        result.data["anime"]["info"].id = anime_id
        
        # Extract sync data for IDs
        sync_data = soup.find("script", id="syncData")
        if sync_data and sync_data.text:
            try:
                sync_json = json.loads(sync_data.text)
                result.data["anime"]["info"].anilistId = safe_int_extract(sync_json.get("anilist_id", "0"))
                result.data["anime"]["info"].malId = safe_int_extract(sync_json.get("mal_id", "0"))
            except json.JSONDecodeError:
                logger.warning("Failed to parse sync data as JSON")
        
        # Extract main content
        content = soup.select_one("#ani_detail .container .anis-content")
        if content:
            # Extract base info
            info = result.data["anime"]["info"]
            anime_info = extract_base_anime_info(content)
            info.name = anime_info.get("name")
            info.poster = anime_info.get("poster")
            
            # Extract description
            info.description = extract_text(content, ".anisc-detail .film-description .text")
            
            # Extract stats
            stats = content.select_one(".film-stats")
            if stats:
                info.stats.rating = extract_text(stats, ".tick .tick-pg")
                info.stats.quality = extract_text(stats, ".tick .tick-quality")
                
                # Type and Duration
                tick_type = extract_text(stats, ".tick")
                if tick_type:
                    type_text = tick_type.strip().replace("\n", " ").split()
                    if len(type_text) >= 2:
                        info.stats.type = type_text[-2]
                        info.stats.duration = type_text[-1]
                
                # Episodes
                eps = extract_episodes(stats)
                info.stats.episodes["sub"] = eps.sub
                info.stats.episodes["dub"] = eps.dub
            
            # Extract genres and studios
            result.data["anime"]["moreInfo"]["genres"] = [
                genre.text.strip() for genre in content.select(".anisc-info .item-list a")
            ]
            result.data["anime"]["moreInfo"]["studios"] = [
                studio.text.strip() for studio in content.select(".anisc-info .item-title a.name")
            ]
            
            # Extract seasons
            seasons = []
            for season_elem in soup.select(".block_area-seasons .os-item"):
                season = extract_season_info(season_elem)
                if season.id:  # Only add if we got a valid ID
                    seasons.append(season)
            result.data["seasons"] = seasons
            
            # Extract characters and voice actors
            cva_list = []
            for char_elem in soup.select(".block-actors-content .bac-item"):
                cva = extract_character_voice_actor(char_elem)
                if cva:
                    cva_list.append(cva)
            result.data["anime"]["info"].charactersVoiceActors = cva_list
            
            # Extract promotional videos
            promo_list = []
            for promo_elem in soup.select(".block_area-promotions-list .item"):
                promo = extract_promotional_video(promo_elem)
                if promo:
                    promo_list.append(promo)
            result.data["anime"]["info"].promotionalVideos = promo_list
            
            # Extract recommended animes
            recommended = []
            for rec_elem in soup.select(".block_area_category .flw-item"):
                anime_info = extract_base_anime_info(rec_elem)
                if anime_info:
                    rec = RecommendedAnime(
                        id=anime_info.get("id"),
                        name=anime_info.get("name"),
                        jname=anime_info.get("jname"),
                        poster=anime_info.get("poster"),
                        type=anime_info.get("type")
                    )
                    
                    duration = extract_text(rec_elem, ".fd-infor .fdi-duration")
                    if duration:
                        rec.duration = duration.strip()
                    
                    # Extract episodes
                    eps = extract_episodes(rec_elem)
                    rec.episodes["sub"] = eps.sub
                    rec.episodes["dub"] = eps.dub
                    rec.episodes["total"] = eps.total
                    
                    recommended.append(rec)
            
            result.data["recommendedAnimes"] = recommended
            
            return result
        else:
            logger.warning("Could not find main content section")
            return None
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise
