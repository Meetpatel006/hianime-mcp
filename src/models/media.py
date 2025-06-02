"""Media-related models for videos and promotional content."""
from dataclasses import dataclass, field
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .anime import (
        Anime,
        SpotlightAnime,
        TrendingAnime
    )

@dataclass
class PromotionalVideo:
    """Promotional video information."""
    title: Optional[str] = None
    source: Optional[str] = None
    thumbnail: Optional[str] = None

@dataclass
class Season:
    """Season information."""
    id: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    poster: Optional[str] = None
    isCurrent: bool = False

@dataclass
class HomePage:
    """Homepage information containing various anime lists."""
    spotlightAnimes: List['SpotlightAnime'] = field(default_factory=list)
    trendingAnimes: List['TrendingAnime'] = field(default_factory=list)
    latestEpisodeAnimes: List['Anime'] = field(default_factory=list)
    topUpcomingAnimes: List['Anime'] = field(default_factory=list)
    top10Animes: 'Top10Anime' = field(default_factory=lambda: Top10Anime())
    topAiringAnimes: List['Anime'] = field(default_factory=list)
    mostPopularAnimes: List['Anime'] = field(default_factory=list)
    mostFavoriteAnimes: List['Anime'] = field(default_factory=list)
    latestCompletedAnimes: List['Anime'] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)

@dataclass
class Top10Anime:
    """Top 10 anime lists by time period."""
    today: List['Anime'] = field(default_factory=list)
    week: List['Anime'] = field(default_factory=list)
    month: List['Anime'] = field(default_factory=list)
