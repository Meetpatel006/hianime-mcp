"""Anime scraping functionality."""

from .homePages import HomePageScraper
from .animeAboutInfo import get_anime_about_info

__all__ = [
    'HomePageScraper',
    'get_anime_about_info'
]
