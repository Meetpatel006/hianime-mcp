"""Utility functions for extracting anime data from HTML elements."""
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup, Tag, ResultSet
from dataclasses import dataclass
from src.management import get_logger

# Configure logging
logger = get_logger("Extractors")

@dataclass
class EpisodeInfo:
    sub: Optional[int] = None
    dub: Optional[int] = None
    total: Optional[int] = None

def safe_select(element: Tag, selector: str) -> ResultSet:
    """Safely perform CSS selection with error handling."""
    if not element:
        return []
    try:
        return element.select(selector)
    except Exception as e:
        logger.error(f"Failed to use selector '{selector}': {str(e)}")
        return []

def safe_select_one(element: Tag, selector: str) -> Optional[Tag]:
    """Safely perform CSS selection for a single element with error handling."""
    if not element:
        return None
    try:
        return element.select_one(selector)
    except Exception as e:
        logger.error(f"Failed to use selector '{selector}': {str(e)}")
        return None

def extract_episodes(element: Tag) -> EpisodeInfo:
    """Extract episode information from an HTML element."""
    try:
        sub_ep = safe_select_one(element, ".tick-sub, .tick .sub")
        dub_ep = safe_select_one(element, ".tick-dub, .tick .dub")
        total_ep = safe_select_one(element, ".tick-eps, .tick .total")
        
        return EpisodeInfo(
            sub=safe_int_extract(sub_ep.text if sub_ep else None),
            dub=safe_int_extract(dub_ep.text if dub_ep else None),
            total=safe_int_extract(total_ep.text if total_ep else None)
        )
    except Exception as e:
        logger.error(f"Failed to extract episodes: {str(e)}")
        return EpisodeInfo()

def extract_base_anime_info(element: Tag) -> Dict[str, Any]:
    """Extract common anime information from an HTML element."""
    info = {}
    
    try:
        # Extract name with multiple selector possibilities
        name_elem = safe_select_one(element, ".dynamic-name, .film-name, .flw-item .film-detail .film-name")
        if name_elem:
            info["name"] = name_elem.text.strip()
            if hasattr(name_elem, 'attrs') and "data-jname" in name_elem.attrs:
                info["jname"] = name_elem["data-jname"].strip()
            
        # If no name found, try a more generic approach
        if not info.get("name"):
            any_title = safe_select_one(element, "a[title]")
            if any_title and "title" in any_title.attrs:
                info["name"] = any_title["title"].strip()
        
        # Extract poster with fallback selectors
        poster = safe_select_one(element, ".film-poster-img, .poster-img, img, .film-poster img")
        if poster:
            if hasattr(poster, 'attrs'):
                if "src" in poster.attrs:
                    info["poster"] = poster["src"].strip()
                elif "data-src" in poster.attrs:
                    info["poster"] = poster["data-src"].strip()
                elif "data-original" in poster.attrs:
                    info["poster"] = poster["data-original"].strip()
        
        # Extract type with fallback selectors
        type_elem = safe_select_one(element, ".fd-infor .tick-item.tick-type, .tick .type, .fdi-type")
        if type_elem:
            info["type"] = type_elem.text.strip()
        
        # Extract ID from href
        link = safe_select_one(element, "a[href]")
        if link and hasattr(link, 'attrs') and "href" in link.attrs:
            href = link["href"]
            if href.startswith("/"):
                info["id"] = href.strip("/")
        
        return info
    except Exception as e:
        logger.error(f"Failed to extract base anime info: {str(e)}")
        return info

def safe_int_extract(text: Optional[str]) -> Optional[int]:
    """Safely extract integer from text."""
    if not text:
        return None
    try:
        # Remove any non-numeric characters and convert
        cleaned = ''.join(c for c in text if c.isdigit())
        return int(cleaned) if cleaned else None
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to extract integer from '{text}': {str(e)}")
        return None

def extract_text(element: Tag, selector: str = None) -> Optional[str]:
    """Safely extract text from an element using a CSS selector.
    If selector is None, use the element directly."""
    try:
        if not element:
            return None
            
        if selector:
            element = safe_select_one(element, selector)
        
        return element.text.strip() if element else None
    except Exception as e:
        logger.error(f"Failed to extract text with selector '{selector}': {str(e)}")
        return None

def extract_attribute(element: Tag, selector: str, attribute: str) -> Optional[str]:
    """Safely extract an attribute from an element using a CSS selector."""
    try:
        found = safe_select_one(element, selector)
        if found and attribute in found.attrs:
            return found[attribute].strip()
    except Exception as e:
        logger.error(f"Failed to extract attribute '{attribute}' with selector '{selector}': {str(e)}")
    return None

def extract_href_id(element: Tag, selector: str) -> Optional[str]:
    """Extract ID from href attribute."""
    try:
        href = extract_attribute(element, selector, "href")
        if href and href.startswith("/"):
            return href.strip("/")
    except Exception as e:
        logger.error(f"Failed to extract href ID with selector '{selector}': {str(e)}")
    return None
