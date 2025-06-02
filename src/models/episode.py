"""Episode information models."""
from dataclasses import dataclass, field
from typing import Dict, Optional

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
