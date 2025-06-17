"""Episode information models."""
from dataclasses import dataclass, field
from typing import Dict, Optional, List

@dataclass
class EpisodeInfo:
    """Basic episode information including sub and dub counts."""
    sub: Optional[int] = None
    dub: Optional[int] = None
    total: Optional[int] = None

@dataclass
class EpisodeStats:
    """Extended episode information with additional statistics."""
    sub: Optional[int] = None
    dub: Optional[int] = None
    raw: Optional[int] = None
    total: Optional[int] = None
    current: Optional[int] = None
    last_updated: Optional[str] = None

@dataclass
class EpisodeServer:
    """Information about an episode server."""
    serverName: str
    serverId: Optional[int] = None
    hianimeid: Optional[str] = None

@dataclass
class ScrapedEpisodeServers:
    """Scraped episode servers data structure."""
    sub: List[EpisodeServer] = field(default_factory=list)
    dub: List[EpisodeServer] = field(default_factory=list)
    raw: List[EpisodeServer] = field(default_factory=list)
    episodeId: str = ""
    episodeNo: int = 0
