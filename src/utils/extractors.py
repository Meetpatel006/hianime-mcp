"""Utility functions for extracting anime data from HTML elements."""
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass

@dataclass
class EpisodeInfo:
    sub: Optional[int] = None
    dub: Optional[int] = None
    total: Optional[int] = None

def extract_episodes(element: Tag) -> EpisodeInfo:
    """Extract episode information from an HTML element."""
    sub_ep = element.select_one(".tick-sub")
    dub_ep = element.select_one(".tick-dub")
    total_ep = element.select_one(".tick-eps")
    
    return EpisodeInfo(
        sub=int(sub_ep.text.strip()) if sub_ep else None,
        dub=int(dub_ep.text.strip()) if dub_ep else None,
        total=int(total_ep.text.strip()) if total_ep else None
    )

def extract_base_anime_info(element: Tag) -> Dict[str, Any]:
    """Extract common anime information from an HTML element."""
    info = {}
    
    # Extract name
    name_elem = element.select_one(".dynamic-name")
    if name_elem:
        info["name"] = name_elem.text.strip()
        if "data-jname" in name_elem.attrs:
            info["jname"] = name_elem["data-jname"].strip()
    
    # Extract poster
    poster = element.select_one(".film-poster-img")
    if poster:
        if "src" in poster.attrs:
            info["poster"] = poster["src"].strip()
        elif "data-src" in poster.attrs:
            info["poster"] = poster["data-src"].strip()
    
    # Extract type
    type_elem = element.select_one(".fd-infor .tick-item.tick-type")
    if type_elem:
        info["type"] = type_elem.text.strip()
    
    # Extract ID from href
    link = element.select_one("a")
    if link and "href" in link.attrs:
        href = link["href"]
        if href.startswith("/"):
            info["id"] = href.strip("/")
    
    return info

def safe_int_extract(text: Optional[str]) -> Optional[int]:
    """Safely extract integer from text."""
    if not text:
        return None
    try:
        return int(text.strip())
    except (ValueError, TypeError):
        return None

def extract_text(element: Tag, selector: str) -> Optional[str]:
    """Safely extract text from an element using a CSS selector."""
    found = element.select_one(selector)
    return found.text.strip() if found else None

def extract_attribute(element: Tag, selector: str, attribute: str) -> Optional[str]:
    """Safely extract an attribute from an element using a CSS selector."""
    found = element.select_one(selector)
    return found[attribute].strip() if found and attribute in found.attrs else None

def extract_href_id(element: Tag, selector: str) -> Optional[str]:
    """Extract ID from href attribute."""
    href = extract_attribute(element, selector, "href")
    if href and href.startswith("/"):
        return href.strip("/")
    return None
