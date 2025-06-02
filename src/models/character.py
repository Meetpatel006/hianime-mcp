"""Character and voice actor related models."""
from dataclasses import dataclass

@dataclass
class Character:
    """Character information."""
    id: str = ""
    poster: str = ""
    name: str = ""
    cast: str = ""

@dataclass
class VoiceActor:
    """Voice actor information."""
    id: str = ""
    poster: str = ""
    name: str = ""
    cast: str = ""

@dataclass
class CharacterVoiceActor:
    """Combined character and voice actor information."""
    character: Character
    voiceActor: VoiceActor
