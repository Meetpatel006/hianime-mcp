from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
import requests
from bs4 import BeautifulSoup
import logging
import json
import cloudscraper
from src.utils.constants import SRC_BASE_URL, USER_AGENT_HEADER, ACCEPT_HEADER, ACCEPT_ENCODING_HEADER
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
                result.data["anime"]["info"].anilistId = int(sync_json.get("anilist_id", 0)) or None
                result.data["anime"]["info"].malId = int(sync_json.get("mal_id", 0)) or None
            except json.JSONDecodeError:
                logger.warning("Failed to parse sync data as JSON")
        
        # Extract main content
        content = soup.select_one("#ani_detail .container .anis-content")
        if content:
            # Basic info
            name_elem = content.select_one(".anisc-detail .film-name.dynamic-name")
            if name_elem:
                result.data["anime"]["info"].name = name_elem.text.strip()
            
            desc_elem = content.select_one(".anisc-detail .film-description .text")
            if desc_elem:
                result.data["anime"]["info"].description = desc_elem.text.strip()
            
            # Extract poster
            poster_elem = content.select_one(".film-poster .film-poster-img")
            if poster_elem:
                if "src" in poster_elem.attrs:
                    result.data["anime"]["info"].poster = poster_elem["src"].strip()
                elif "data-src" in poster_elem.attrs:
                    result.data["anime"]["info"].poster = poster_elem["data-src"].strip()
            
            # Stats
            stats = content.select_one(".film-stats")
            if stats:
                # Rating
                tick_pg = stats.select_one(".tick .tick-pg")
                if tick_pg:
                    result.data["anime"]["info"].stats.rating = tick_pg.text.strip()
                
                # Quality
                tick_quality = stats.select_one(".tick .tick-quality")
                if tick_quality:
                    result.data["anime"]["info"].stats.quality = tick_quality.text.strip()
                
                # Type and Duration
                tick_type = stats.select_one(".tick")
                if tick_type:
                    type_text = tick_type.text.strip().replace("\n", " ").split()
                    if len(type_text) >= 2:
                        result.data["anime"]["info"].stats.type = type_text[-2]
                        result.data["anime"]["info"].stats.duration = type_text[-1]
                
                # Episodes
                sub_eps = stats.select_one(".tick .tick-sub")
                dub_eps = stats.select_one(".tick .tick-dub")
                
                if sub_eps:
                    try:
                        result.data["anime"]["info"].stats.episodes["sub"] = int(sub_eps.text.strip())
                    except ValueError:
                        pass
                
                if dub_eps:
                    try:
                        result.data["anime"]["info"].stats.episodes["dub"] = int(dub_eps.text.strip())
                    except ValueError:
                        pass
            
            # Extract genres
            genres = content.select(".anisc-info .item-list a")
            if genres:
                result.data["anime"]["moreInfo"]["genres"] = [genre.text.strip() for genre in genres]
            
            # Extract studios
            studios = content.select(".anisc-info .item-title a.name")
            if studios:
                result.data["anime"]["moreInfo"]["studios"] = [studio.text.strip() for studio in studios]
            
            # Extract seasons
            seasons = soup.select(".block_area-seasons .os-item")
            if seasons:
                for season in seasons:
                    season_obj = Season()
                    
                    # Extract season ID
                    season_link = season.select_one("a")
                    if season_link and "href" in season_link.attrs:
                        season_obj.id = season_link["href"].strip("/")
                    
                    # Extract season name
                    name = season.select_one(".title")
                    if name:
                        season_obj.title = name.text.strip()
                        season_obj.name = name.text.strip()
                    
                    # Extract season poster
                    poster = season.select_one(".season-poster")
                    if poster and "style" in poster.attrs:
                        style = poster["style"]
                        if "background-image: url(" in style:
                            season_obj.poster = style.split("url(")[1].split(")")[0].strip("'\"")
                    
                    if "active" in season.get("class", []):
                        season_obj.isCurrent = True
                    
                    result.data["seasons"].append(season_obj)
            
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
                        
                        char_obj = Character(
                            id=char_id,
                            name=char_name.text.strip(),
                            cast=char_role.text.strip()
                        )
                        
                        va_obj = VoiceActor(
                            id=va_id,
                            name=voice_actor_name.text.strip() if voice_actor_name else "",
                            cast=voice_actor_role.text.strip() if voice_actor_role else ""
                        )
                        
                        # Extract character poster
                        char_poster = char.select_one(".per-info.ltr .pi-avatar img")
                        if char_poster and "data-src" in char_poster.attrs:
                            char_obj.poster = char_poster["data-src"].strip()
                        
                        # Extract voice actor poster
                        va_poster = char.select_one(".per-info.rtl .pi-avatar img")
                        if va_poster and "data-src" in va_poster.attrs:
                            va_obj.poster = va_poster["data-src"].strip()
                        
                        result.data["anime"]["info"].charactersVoiceActors.append(
                            CharacterVoiceActor(character=char_obj, voiceActor=va_obj)
                        )
            
            # Extract promotional videos
            promos = soup.select(".block_area-promotions-list .item")
            if promos:
                for promo in promos:
                    title = promo.select_one(".sii-title")
                    if title:
                        promo_obj = PromotionalVideo(title=title.text.strip())
                        
                        # Extract promo source
                        if "data-src" in promo.attrs:
                            promo_obj.source = promo["data-src"].strip()
                        
                        # Extract promo thumbnail
                        thumbnail = promo.select_one("img")
                        if thumbnail and "src" in thumbnail.attrs:
                            promo_obj.thumbnail = thumbnail["src"].strip()
                        
                        result.data["anime"]["info"].promotionalVideos.append(promo_obj)
            
            # Extract recommended anime
            recommended = soup.select(".block_area_category .flw-item")
            if recommended:
                for rec in recommended:
                    rec_obj = RecommendedAnime()
                    
                    # Extract full ID from href
                    name_link = rec.select_one(".film-name .dynamic-name")
                    if name_link and "href" in name_link.attrs:
                        href = name_link["href"]
                        if href.startswith("/"):
                            rec_obj.id = href.strip("/")
                    
                    # Extract name and Japanese name
                    if name_link:
                        rec_obj.name = name_link.text.strip()
                        if "data-jname" in name_link.attrs:
                            rec_obj.jname = name_link["data-jname"].strip()
                    
                    # Extract poster
                    poster = rec.select_one(".film-poster-img")
                    if poster and "data-src" in poster.attrs:
                        rec_obj.poster = poster["data-src"].strip()
                    
                    # Extract type and duration
                    type_elem = rec.select_one(".fd-infor .fdi-item")
                    duration_elem = rec.select_one(".fd-infor .fdi-duration")
                    
                    if type_elem:
                        rec_obj.type = type_elem.text.strip()
                    if duration_elem:
                        rec_obj.duration = duration_elem.text.strip()
                    
                    # Extract episodes
                    sub_eps = rec.select_one(".tick .tick-sub")
                    dub_eps = rec.select_one(".tick .tick-dub")
                    total_eps = rec.select_one(".tick .tick-eps")
                    
                    if sub_eps:
                        try:
                            rec_obj.episodes["sub"] = int(sub_eps.text.strip())
                        except ValueError:
                            pass
                    
                    if dub_eps:
                        try:
                            rec_obj.episodes["dub"] = int(dub_eps.text.strip())
                        except ValueError:
                            pass
                    
                    if total_eps:
                        try:
                            rec_obj.episodes["total"] = int(total_eps.text.strip())
                        except ValueError:
                            pass
                    
                    result.data["recommendedAnimes"].append(rec_obj)
            
            return result
        else:
            logger.warning("Could not find main content section")
            return None
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise

def extract_most_popular_animes(soup: BeautifulSoup, selector: str) -> List[Dict]:
    """Extract most popular animes from the page."""
    animes = []
    for item in soup.select(selector):
        anime = {}
        link = item.select_one("a")
        if link and "href" in link.attrs:
            anime["id"] = link["href"].split("/")[-1]
        
        name_elem = item.select_one(".dynamic-name")
        if name_elem:
            anime["name"] = name_elem.text.strip()
        
        img = item.select_one("img")
        if img and "data-src" in img.attrs:
            anime["poster"] = img["data-src"]
        
        type_elem = item.select_one(".fd-infor .tick-item")
        if type_elem:
            anime["type"] = type_elem.text.strip()
        
        rating_elem = item.select_one(".fd-infor .tick-rate")
        if rating_elem:
            anime["rating"] = rating_elem.text.strip()
        
        if anime:
            animes.append(anime)
    return animes

def extract_animes(soup: BeautifulSoup, selector: str) -> List[Dict]:
    """Extract animes from the page."""
    animes = []
    for item in soup.select(selector):
        anime = {}
        link = item.select_one("a")
        if link and "href" in link.attrs:
            anime["id"] = link["href"].split("/")[-1]
        
        name_elem = item.select_one(".dynamic-name")
        if name_elem:
            anime["name"] = name_elem.text.strip()
        
        img = item.select_one("img")
        if img and "data-src" in img.attrs:
            anime["poster"] = img["data-src"]
        
        type_elem = item.select_one(".fd-infor .tick-item")
        if type_elem:
            anime["type"] = type_elem.text.strip()
        
        rating_elem = item.select_one(".fd-infor .tick-rate")
        if rating_elem:
            anime["rating"] = rating_elem.text.strip()
        
        if anime:
            animes.append(anime)
    return animes
