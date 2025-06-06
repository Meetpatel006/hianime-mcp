"""MCP server implementation for anime scraping."""
import os
import sys
import asyncio
from mcp.server.fastmcp import FastMCP, Context

from src.management import get_logger
from src.scrapers import HomePageScraper
from src.scrapers.animeAboutInfo import get_anime_about_info as scrape_anime_about_info
from src.utils.config import Config

# Configure logging
logger = get_logger("AnimeMCP")

# Create an MCP server
mcp = FastMCP("Anime Assistant")

# Initialize the Aniwatch scraper
try:
    home_page_scraper = HomePageScraper()
except Exception as e:
    logger.error(f"Failed to initialize Aniwatch scraper: {str(e)}")
    sys.exit(1)

# Add Aniwatch tools
@mcp.tool()
async def get_home_page(ctx: Context) -> dict:
    """Get anime information from Aniwatch homepage."""
    try:
        result = home_page_scraper.get_home_page()
        return {
            "spotlightAnimes": [
                {
                    "rank": anime.rank,
                    "id": anime.id.split("/")[-1] if anime.id and "/" in anime.id else anime.id,
                    "name": anime.name,
                    "description": anime.description,
                    "poster": anime.poster,
                    "jname": anime.jname,
                    "episodes": {
                        "sub": anime.episodes.sub,
                        "dub": anime.episodes.dub
                    },
                    "type": anime.type,
                    "otherInfo": {
                        "type": anime.otherInfo[0] if len(anime.otherInfo) > 0 else None,
                        "duration": anime.otherInfo[1] if len(anime.otherInfo) > 1 else None,
                        "releaseDate": anime.otherInfo[2] if len(anime.otherInfo) > 2 else None,
                        "quality": anime.otherInfo[3] if len(anime.otherInfo) > 3 else None
                    }
                }
                for anime in result.spotlightAnimes
            ],
            "trendingAnimes": [
                {
                    "rank": anime.rank,
                    "id": anime.id.split("/")[-1] if anime.id and "/" in anime.id else anime.id,
                    "name": anime.name,
                    "poster": anime.poster,
                    "jname": anime.jname,
                    "episodes": {
                        "sub": anime.episodes.sub,
                        "dub": anime.episodes.dub
                    },
                    "type": anime.type
                }
                for anime in result.trendingAnimes
            ],
            "genres": result.genres
        }
    except Exception as e:
        logger.error(f"Error getting home page: {str(e)}")
        raise

@mcp.tool()
async def get_trending_anime(ctx: Context) -> dict:
    """Get trending anime from Aniwatch homepage."""
    try:
        result = home_page_scraper.get_home_page()
        return {
            "animes": [
                {
                    "rank": anime.rank,
                    "id": anime.id.split("/")[-1] if anime.id and "/" in anime.id else anime.id,
                    "name": anime.name,
                    "poster": anime.poster,
                    "jname": anime.jname,
                    "episodes": {
                        "sub": anime.episodes.sub,
                        "dub": anime.episodes.dub
                    },
                    "type": anime.type
                }
                for anime in result.trendingAnimes
            ]
        }
    except Exception as e:
        logger.error(f"Error getting trending anime: {str(e)}")
        raise

@mcp.tool()
async def get_anime_genres(ctx: Context) -> dict:
    """Get available anime genres from Aniwatch."""
    try:
        result = home_page_scraper.get_home_page()
        return {"genres": result.genres}
    except Exception as e:
        logger.error(f"Error getting anime genres: {str(e)}")
        raise

@mcp.tool()
async def get_anime_recommendations(ctx: Context) -> dict:
    """Get anime recommendations based on current trends."""
    try:
        result = home_page_scraper.get_home_page()
        spotlight = result.spotlightAnimes[0] if result.spotlightAnimes else None
        trending = result.trendingAnimes[0] if result.trendingAnimes else None
        
        return {
            "spotlight": {
                "id": spotlight.id.split("/")[-1] if spotlight.id and "/" in spotlight.id else spotlight.id,
                "name": spotlight.name,
                "description": spotlight.description,
                "poster": spotlight.poster,
                "jname": spotlight.jname,
                "episodes": {
                    "sub": spotlight.episodes.sub,
                    "dub": spotlight.episodes.dub
                },
                "type": spotlight.type,
                "otherInfo": {
                    "type": spotlight.otherInfo[0] if spotlight.otherInfo and len(spotlight.otherInfo) > 0 else None,
                    "duration": spotlight.otherInfo[1] if spotlight.otherInfo and len(spotlight.otherInfo) > 1 else None,
                    "releaseDate": spotlight.otherInfo[2] if spotlight.otherInfo and len(spotlight.otherInfo) > 2 else None,
                    "quality": spotlight.otherInfo[3] if spotlight.otherInfo and len(spotlight.otherInfo) > 3 else None
                }
            } if spotlight else None,
            "trending": {
                "id": trending.id,
                "name": trending.name,
                "poster": trending.poster,
                "jname": trending.jname,
                "episodes": {
                    "sub": trending.episodes.sub,
                    "dub": trending.episodes.dub
                },
                "type": trending.type
            } if trending else None
        }
    except Exception as e:
        logger.error(f"Error getting anime recommendations: {str(e)}")
        raise

@mcp.tool()
async def get_anime_about_info(ctx: Context, anime_id: str = "") -> dict:
    """Get detailed information about an anime."""
    try:
        if not anime_id:
            raise ValueError("anime_id is required")
        
        result = scrape_anime_about_info(anime_id)
        
        # Ensure we have a valid result
        if not result or not result.data:
            raise ValueError("Failed to fetch anime information")
            
        return {
            "success": True,
            "data": {
                "anime": {
                    "info": {
                        "id": result.data["anime"]["info"].id,
                        "anilistId": result.data["anime"]["info"].anilistId,
                        "malId": result.data["anime"]["info"].malId,
                        "name": result.data["anime"]["info"].name,
                        "poster": result.data["anime"]["info"].poster,
                        "description": result.data["anime"]["info"].description,
                        "stats": {
                            "rating": result.data["anime"]["info"].stats.rating,
                            "quality": result.data["anime"]["info"].stats.quality,
                            "episodes": {
                                "sub": result.data["anime"]["info"].stats.episodes.get("sub"),
                                "dub": result.data["anime"]["info"].stats.episodes.get("dub")
                            },
                            "type": result.data["anime"]["info"].stats.type,
                            "duration": result.data["anime"]["info"].stats.duration
                        },
                        "promotionalVideos": [
                            {
                                "title": video.title,
                                "source": video.source,
                                "thumbnail": video.thumbnail
                            }
                            for video in result.data["anime"]["info"].promotionalVideos
                        ],
                        "charactersVoiceActors": [
                            {
                                "character": {
                                    "id": cva.character.id,
                                    "poster": cva.character.poster,
                                    "name": cva.character.name,
                                    "cast": cva.character.cast
                                },
                                "voiceActor": {
                                    "id": cva.voiceActor.id,
                                    "poster": cva.voiceActor.poster,
                                    "name": cva.voiceActor.name,
                                    "cast": cva.voiceActor.cast
                                }
                            }
                            for cva in result.data["anime"]["info"].charactersVoiceActors
                        ]
                    },
                    "moreInfo": {
                        "genres": result.data["anime"]["moreInfo"]["genres"],
                        "studios": result.data["anime"]["moreInfo"]["studios"]
                    }
                },
                "seasons": [
                    {
                        "id": season.id,
                        "name": season.name,
                        "title": season.title,
                        "poster": season.poster,
                        "isCurrent": season.isCurrent
                    }
                    for season in result.data["seasons"]
                ],
                "mostPopularAnimes": result.data["mostPopularAnimes"],
                "relatedAnimes": result.data["relatedAnimes"],
                "recommendedAnimes": [
                    {
                        "id": anime.id,
                        "name": anime.name,
                        "jname": anime.jname,
                        "poster": anime.poster,
                        "type": anime.type,
                        "duration": anime.duration,
                        "episodes": {
                            "sub": anime.episodes.get("sub"),
                            "dub": anime.episodes.get("dub"),
                            "total": anime.episodes.get("total")
                        }
                    }
                    for anime in result.data["recommendedAnimes"]
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error getting anime about info: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    try:
        logger.info("Starting MCP server...")
        # Apply configuration
        if Config.DEBUG_MODE:
            logger.info("Running in debug mode")
        mcp.run()
    except Exception as e:
        logger.error(f"Failed to run server: {str(e)}")
        sys.exit(1)
