"""Homepage scraping functionality."""
from typing import Dict, Any
import gzip
import io
import zlib
import cloudscraper
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
    SpotlightAnime,
    TrendingAnime,
    HomePage
)

# Configure logging
logger = get_logger("HomePageScraper")

# Constants
HOME_URL = f"{SRC_BASE_URL}/home"

class HomePageScraper:
    def __init__(self):
        self.session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        self.session.headers.update(Config.get_headers())

    def _process_html_content(self, response) -> str:
        """Process and decompress HTML content from response."""
        # First try to use response.text which handles encoding automatically
        try:
            html_content = response.text
            if html_content and '<html' in html_content.lower():
                logger.debug(f"Valid HTML content received from response.text (length: {len(html_content)})")
                return html_content
        except Exception as e:
            logger.debug(f"Failed to get content from response.text: {str(e)}")

        # Fallback to manual content processing
        html_content = response.content

        try:
            # Try to decompress if it's gzipped
            if html_content.startswith(b'\x1f\x8b\x08'):  # gzip magic number
                html_content = gzip.decompress(html_content)
                logger.debug("Decompressed gzipped content")
            elif response.headers.get('content-encoding') == 'gzip':
                # Cloudscraper might have already decompressed
                logger.debug("Content was gzipped but already decompressed by cloudscraper")
            elif html_content.startswith(b'\x78\x9c'):  # zlib magic number
                try:
                    html_content = zlib.decompress(html_content)
                    logger.debug("Decompressed zlib content")
                except zlib.error:
                    logger.debug("Not zlib compressed")
            # Try deflate decompression
            elif html_content.startswith(b'\x78'):  # deflate magic number variants
                try:
                    html_content = zlib.decompress(html_content, -zlib.MAX_WBITS)
                    logger.debug("Decompressed deflate content")
                except zlib.error:
                    logger.debug("Not deflate compressed")
            else:
                logger.debug("Content is not compressed")
        except Exception as e:
            logger.warning(f"Decompression failed, using raw content: {str(e)}")

        # Ensure we have text with better encoding handling
        if isinstance(html_content, bytes):
            # Try multiple encoding strategies
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    html_content = html_content.decode(encoding)
                    logger.debug(f"Successfully decoded content using {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # Last resort: use utf-8 with error replacement
                html_content = html_content.decode('utf-8', errors='replace')
                logger.debug("Decoded bytes to text with error replacement")

        # Validate HTML content with safe logging
        if html_content and '<html' in html_content.lower():
            logger.debug(f"Valid HTML content received (length: {len(html_content)})")
        else:
            logger.warning("HTML content appears to be invalid or empty")
            # Safe preview logging - only show printable characters
            if html_content:
                safe_preview = ''.join(c if c.isprintable() else '?' for c in html_content[:200])
                logger.debug(f"Content preview (safe): {safe_preview}")
            else:
                logger.debug("Content is None or empty")

        return html_content

    def _extract_spotlight_animes(self, soup: BeautifulSoup) -> list:
        """Extract spotlight animes using improved BeautifulSoup parsing."""
        spotlight_animes = []

        # Multiple selector strategies for spotlight container
        spotlight_selectors = [
            ".swiper-wrapper",
            "#slider .swiper-wrapper",
            ".spotlight-container .swiper-wrapper",
            ".hero-slider .swiper-wrapper"
        ]

        spotlight_container = None
        for selector in spotlight_selectors:
            spotlight_container = soup.select_one(selector)
            if spotlight_container:
                logger.debug(f"Found spotlight container with selector: {selector}")
                break

        if not spotlight_container:
            logger.warning("No spotlight container found with any selector")
            return spotlight_animes

        # Extract spotlight items with improved parsing
        spotlight_items = spotlight_container.select(".swiper-slide")
        logger.debug(f"Found {len(spotlight_items)} spotlight items")

        for item in spotlight_items:
            try:
                # Extract other info with better error handling
                other_info_elements = item.select(".sc-detail .scd-item")
                other_info = []
                for elem in other_info_elements[:-1]:  # Exclude last item
                    text = elem.get_text(strip=True)
                    if text:
                        other_info.append(text)

                # Extract base anime info using utility function
                anime_info = extract_base_anime_info(item)

                # Extract additional spotlight-specific data
                anime_id = anime_info.get("id") or extract_href_id(item, ".desi-buttons a")
                name = anime_info.get("name") or extract_text(item, ".desi-head-title.dynamic-name")

                # Extract description with better text processing
                description_elem = item.select_one(".desi-description")
                description = ""
                if description_elem:
                    description = description_elem.get_text(strip=True)
                    # Remove content after "[" if present (usually contains spoiler warnings)
                    if "[" in description:
                        description = description.split("[")[0].strip()

                # Create SpotlightAnime object
                anime = SpotlightAnime(
                    id=anime_id,
                    name=name,
                    description=description,
                    poster=anime_info.get("poster"),
                    jname=anime_info.get("jname"),
                    type=anime_info.get("type") or (other_info[0] if other_info else None),
                    otherInfo=other_info,
                    episodes=EpisodeInfo(**vars(extract_episodes(item)))
                )

                # Extract rank with improved parsing
                rank_elem = item.select_one(".desi-sub-text")
                if rank_elem:
                    rank_text = rank_elem.get_text(strip=True)
                    if rank_text and rank_text.startswith("#"):
                        anime.rank = safe_int_extract(rank_text[1:])

                if anime.name:  # Only add if we have a name
                    spotlight_animes.append(anime)
                    logger.debug(f"Added spotlight anime: {anime.name}")

            except Exception as e:
                logger.error(f"Error processing spotlight anime item: {str(e)}")
                continue

        return spotlight_animes

    def _extract_trending_animes(self, soup: BeautifulSoup) -> list:
        """Extract trending animes using improved BeautifulSoup parsing."""
        trending_animes = []

        # Multiple selector strategies for trending anime containers
        trending_selectors = [
            ".block_area_category",
            ".block_area-realtime",
            ".film_list-wrap",
            ".trending-section",
            ".popular-section"
        ]

        trend_items = []

        # Try each selector strategy
        for selector in trending_selectors:
            containers = soup.select(selector)
            for container in containers:
                items = container.select(".flw-item")
                if items:
                    trend_items = items
                    logger.debug(f"Found {len(trend_items)} trending items with selector: {selector}")
                    break
            if trend_items:
                break

        if not trend_items:
            # Fallback: search for any .flw-item elements
            trend_items = soup.select(".flw-item")
            logger.debug(f"Fallback: Found {len(trend_items)} .flw-item elements")

        if not trend_items:
            logger.warning("No trending anime items found with any selector")
            return trending_animes

        # Process trending items with improved parsing
        for i, item in enumerate(trend_items):
            try:
                # Extract rank with multiple strategies
                rank = None

                # Try to find explicit rank number
                rank_selectors = [".number", ".rank", ".position", ".item-number"]
                for rank_selector in rank_selectors:
                    rank_elem = item.select_one(rank_selector)
                    if rank_elem:
                        rank_text = rank_elem.get_text(strip=True)
                        rank = safe_int_extract(rank_text)
                        if rank:
                            break

                # Use position as rank if no explicit rank found
                if not rank:
                    rank = i + 1

                # Extract base anime info
                anime_info = extract_base_anime_info(item)

                # Enhanced ID extraction with multiple fallback strategies
                anime_id = anime_info.get("id")
                if not anime_id:
                    # Try film-detail link
                    detail_link = item.select_one(".film-detail a[href]")
                    if detail_link and detail_link.get("href"):
                        href = detail_link["href"]
                        if href.startswith("/"):
                            anime_id = href.strip("/")

                    # Try any link with href
                    if not anime_id:
                        any_link = item.select_one("a[href]")
                        if any_link and any_link.get("href"):
                            href = any_link["href"]
                            if href.startswith("/"):
                                anime_id = href.strip("/")

                # Clean up the ID
                if anime_id:
                    # Remove "watch/" prefix if present
                    if anime_id.startswith("watch/"):
                        anime_id = anime_id[6:]
                    # Remove query parameters
                    if "?" in anime_id:
                        anime_id = anime_id.split("?")[0]
                    # Remove trailing slashes
                    anime_id = anime_id.strip("/")

                # Create TrendingAnime object
                anime = TrendingAnime(
                    rank=rank,
                    id=anime_id,
                    name=anime_info.get("name"),
                    jname=anime_info.get("jname"),
                    poster=anime_info.get("poster"),
                    type=anime_info.get("type"),
                    episodes=EpisodeInfo(**vars(extract_episodes(item)))
                )

                if anime.name and anime.id:  # Only add if we have both name and ID
                    trending_animes.append(anime)
                    logger.debug(f"Added trending anime: {anime.name} (rank: {rank})")

            except Exception as e:
                logger.error(f"Error processing trending anime item: {str(e)}")
                continue

        return trending_animes

    def _extract_genres(self, soup: BeautifulSoup) -> list:
        """Extract genres using improved BeautifulSoup parsing."""
        # Multiple selector strategies for genre containers
        genre_selectors = [
            "#sidebar_subs_genre .nav-link",
            ".genre-list .nav-link",
            ".sidebar-genre .nav-link",
            ".genre-container a",
            ".genres-list a"
        ]

        extracted_genres = []

        for selector in genre_selectors:
            genre_elements = soup.select(selector)
            if genre_elements:
                extracted_genres = [
                    elem.get_text(strip=True)
                    for elem in genre_elements
                    if elem.get_text(strip=True)
                ]
                if extracted_genres:
                    logger.debug(f"Extracted {len(extracted_genres)} genres with selector: {selector}")
                    break

    def get_home_page(self) -> HomePage:
        try:
            logger.debug(f"Fetching homepage from {HOME_URL}")
            response = self.session.get(HOME_URL)
            response.raise_for_status()

            # Process HTML content
            html_content = self._process_html_content(response)

            # Parse with BeautifulSoup using lxml parser for better performance
            try:
                soup = BeautifulSoup(html_content, 'lxml')
                logger.debug("Using lxml parser")
            except:
                soup = BeautifulSoup(html_content, 'html.parser')
                logger.debug("Fallback to html.parser")

            result = HomePage()

            try:
                # Extract spotlight animes using improved method
                result.spotlightAnimes = self._extract_spotlight_animes(soup)                # Extract trending animes using improved method
                result.trendingAnimes = self._extract_trending_animes(soup)

                # Extract genres using improved method
                result.genres = self._extract_genres(soup)

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
        return {            "spotlightAnimes": [                {
                    "id": anime.id.split("/")[-1] if anime.id and "/" in anime.id else anime.id,
                    "name": anime.name,
                    "description": anime.description,
                    "poster": anime.poster,
                    "jname": anime.jname,
                    "episodes": {
                        "sub": anime.episodes.sub,
                        "dub": anime.episodes.dub
                    },
                    "type": anime.type,
                    "otherInfo": {
                        "type": anime.otherInfo[0] if len(anime.otherInfo) > 0 else None,
                        "duration": anime.otherInfo[1] if len(anime.otherInfo) > 1 else None,
                        "releaseDate": anime.otherInfo[2] if len(anime.otherInfo) > 2 else None,
                        "quality": anime.otherInfo[3] if len(anime.otherInfo) > 3 else None
                    }
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
            ],            "genres": result.genres
        }
    except Exception as e:
        logger.error(f"Failed to get homepage: {str(e)}")
        raise Exception(f"Failed to get homepage: {str(e)}")
