"""Models for anime data structures."""

from .episode import EpisodeInfo, EpisodeStats
from .character import Character, VoiceActor, CharacterVoiceActor
from .media import (
    PromotionalVideo,
    Season,
    HomePage,
    Top10Anime
)
from .anime import (
    BaseAnime,
    AnimeStats,
    Anime,
    SpotlightAnime,
    TrendingAnime,
    RecommendedAnime
)

__all__ = [
    # Episode models
    'EpisodeInfo',
    'EpisodeStats',
    
    # Character models
    'Character',
    'VoiceActor',
    'CharacterVoiceActor',
    
    # Media models
    'PromotionalVideo',
    'Season',
    'HomePage',
    'Top10Anime',
    
    # Anime models
    'BaseAnime',
    'AnimeStats',
    'Anime',
    'SpotlightAnime',
    'TrendingAnime',
    'RecommendedAnime'
]
