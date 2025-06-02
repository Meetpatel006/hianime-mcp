"""Common anime-related data models."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .episode import EpisodeInfo

@dataclass
class BaseAnime:
    """Base class for all anime types."""
    id: Optional[str] = None
    name: Optional[str] = None
    jname: Optional[str] = None
    poster: Optional[str] = None
    type: Optional[str] = None

@dataclass
class AnimeStats:
    """Statistics for an anime."""
    rating: Optional[str] = None
    quality: Optional[str] = None
    episodes: Dict[str, Optional[int]] = field(default_factory=lambda: {"sub": None, "dub": None})
    type: Optional[str] = None
    duration: Optional[str] = None

@dataclass
class Anime(BaseAnime):
    """Standard anime model."""
    duration: Optional[str] = None
    rating: Optional[str] = None
    episodes: EpisodeInfo = field(default_factory=EpisodeInfo)

@dataclass
class SpotlightAnime(BaseAnime):
    """Featured anime with additional spotlight-specific fields."""
    rank: Optional[int] = None
    description: Optional[str] = None
    episodes: EpisodeInfo = field(default_factory=EpisodeInfo)
    otherInfo: List[str] = field(default_factory=list)

@dataclass
class TrendingAnime(BaseAnime):
    """Trending anime with rank information."""
    episodes: EpisodeInfo = field(default_factory=EpisodeInfo)
    rank: int = 0  # Default to 0 instead of making it required

@dataclass
class RecommendedAnime(BaseAnime):
    """Recommended anime with episode information."""
    duration: Optional[str] = None
    episodes: Dict[str, Optional[int]] = field(default_factory=lambda: {"sub": None, "dub": None, "total": None})
