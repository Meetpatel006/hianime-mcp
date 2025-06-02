"""Anime MCP Client Library."""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict
from mcp.client import Client

class AnimeEpisodes(TypedDict):
    """Episode information."""
    sub: Optional[int]
    dub: Optional[int]

class SpotlightAnime(TypedDict):
    """Spotlight anime information."""
    rank: Optional[int]
    id: str
    name: str
    description: str
    poster: str
    jname: str
    episodes: AnimeEpisodes
    type: str
    other_info: List[str]

class TrendingAnime(TypedDict):
    """Trending anime information."""
    rank: int
    id: str
    name: str
    jname: str
    poster: str

class HomePageResponse(TypedDict):
    """Homepage API response."""
    spotlight_animes: List[SpotlightAnime]
    trending_animes: List[TrendingAnime]
    genres: List[str]

class AnimeStats(TypedDict):
    """Anime statistics."""
    rating: Optional[str]
    quality: Optional[str]
    type: Optional[str]
    duration: Optional[str]

class AnimeInfo(TypedDict):
    """Detailed anime information."""
    id: str
    name: str
    description: str
    stats: AnimeStats

class AnimeResponse(TypedDict):
    """Anime details API response."""
    success: bool
    data: Dict[str, Any]

class AnimeClient:
    """Client for the Anime MCP Server."""

    def __init__(self):
        """Initialize the client."""
        self.client = Client()

    async def __aenter__(self):
        """Enter async context."""
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def initialize(self):
        """Initialize the connection to the server."""
        await self.client.initialize()

    async def get_home_page(self) -> HomePageResponse:
        """
        Get homepage information including spotlight and trending anime.

        Returns:
            HomePageResponse: Homepage data including spotlight animes, trending animes, and genres
        
        Example:
            ```python
            async with AnimeClient() as client:
                await client.initialize()
                home_data = await client.get_home_page()
                
                # Access spotlight animes
                for anime in home_data["spotlight_animes"]:
                    print(f"Spotlight: {anime['name']}")
                
                # Access trending animes
                for anime in home_data["trending_animes"]:
                    print(f"Trending: {anime['name']} (Rank: {anime['rank']})")
            ```
        """
        return await self.client.call("get_home_page")

    async def get_anime_details(self, anime_id: str) -> AnimeResponse:
        """
        Get detailed information about a specific anime.

        Args:
            anime_id: The ID of the anime to fetch

        Returns:
            AnimeResponse: Detailed anime information including stats, characters, and recommendations
        
        Example:
            ```python
            async with AnimeClient() as client:
                await client.initialize()
                anime_data = await client.get_anime_details("spy-x-family")
                
                if anime_data["success"]:
                    info = anime_data["data"]["anime"]["info"]
                    print(f"Name: {info['name']}")
                    print(f"Description: {info['description']}")
            ```
        """
        return await self.client.call("get_anime_about_info", anime_id=anime_id)

@dataclass
class PrintOptions:
    """Options for print formatting."""
    show_description: bool = True
    max_description_length: int = 200
    show_stats: bool = True
    show_genres: bool = True
    show_recommendations: bool = False

def print_anime_info(info: AnimeInfo, options: PrintOptions = PrintOptions()):
    """Print anime information in a formatted way."""
    print(f"\nAnime: {info['name']}")
    
    if options.show_description and info.get('description'):
        desc = info['description']
        if len(desc) > options.max_description_length:
            desc = desc[:options.max_description_length] + "..."
        print(f"\nDescription:\n{desc}")
    
    if options.show_stats and info.get('stats'):
        stats = info['stats']
        print("\nStats:")
        print(f"Rating: {stats.get('rating', 'N/A')}")
        print(f"Quality: {stats.get('quality', 'N/A')}")
        print(f"Type: {stats.get('type', 'N/A')}")
        print(f"Duration: {stats.get('duration', 'N/A')}")

def print_homepage(data: HomePageResponse):
    """Print homepage information in a formatted way."""
    if data.get("spotlight_animes"):
        print("\n=== Spotlight Animes ===")
        for anime in data["spotlight_animes"]:
            print(f"\n- {anime['name']} ({anime['jname']})")
            print(f"  Type: {anime['type']}")
            print(f"  Episodes: Sub={anime['episodes']['sub']}, Dub={anime['episodes']['dub']}")
    
    if data.get("trending_animes"):
        print("\n=== Trending Animes ===")
        for anime in data["trending_animes"]:
            print(f"- {anime['name']} (Rank: {anime['rank']})")
    
    if data.get("genres"):
        print("\n=== Available Genres ===")
        print(", ".join(data["genres"]))

async def main():
    """Example usage of the client."""
    async with AnimeClient() as client:
        await client.initialize()
        
        # Get and print homepage
        print("Fetching homepage...")
        home_data = await client.get_home_page()
        print_homepage(home_data)
        
        # Get and print anime details
        if home_data["spotlight_animes"]:
            anime_id = home_data["spotlight_animes"][0]["id"]
            print(f"\nFetching details for anime: {anime_id}")
            
            details = await client.get_anime_details(anime_id)
            if details["success"]:
                info = details["data"]["anime"]["info"]
                print_anime_info(info)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
