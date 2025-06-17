"""MCP server implementation for anime scraping."""
import os
import sys
import asyncio
from mcp.server.fastmcp import FastMCP, Context
from starlette.responses import JSONResponse

from src.management import get_logger
from src.scrapers import HomePageScraper
from src.scrapers.animeAboutInfo import get_anime_about_info as scrape_anime_about_info
from src.scrapers.animeEpisodeSrcs import get_all_anime_episode_sources as scrape_all_anime_episode_sources
from src.scrapers.animeEpisodeServers import get_episode_servers as scrape_episode_servers
from src.utils.config import Config

from starlette.applications import Starlette
from starlette.routing import Mount, Host
from src.utils.extractors import safe_select

# Configure logging
logger = get_logger("AnimeMCP")

# Create an MCP server
mcp = FastMCP("Anime Assistant")
app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app()),
    ]
)

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
        logger.info(f"Received request for anime ID: '{anime_id}'")
        logger.debug(f"Calling scrape_anime_about_info with ID: '{anime_id}'")
        
        if not anime_id:
            logger.error("Empty anime_id received")
            return {
                "success": False,
                "error": "anime_id is required"
            }

        result = scrape_anime_about_info(anime_id)

        # Ensure we have a valid result
        if not result:
            logger.error(f"No result from scraping for anime_id: {anime_id}")
            return {
                "success": False,
                "error": "Failed to fetch anime information - no data returned"
            }
        
        # Check if result is already in the expected format
        if isinstance(result, dict):
            # If result already has success key, check if it's successful
            if "success" in result:
                if result["success"] is False and "error" in result:
                    # Log the specific error from the scraper
                    logger.error(f"Scraper error: {result['error']}")
                    return result
                return result
            
            # If result has data key, it's properly formatted
            if "data" in result:
                # Make sure success is set to true
                result["success"] = True
                return result
            
            # If result has error key but no success key, it's an error result
            if "error" in result:
                result["success"] = False
                logger.error(f"Scraper error: {result['error']}")
                return result
            
            # If result doesn't have expected structure, return error
            logger.error(f"Invalid result structure from scraping: result keys={list(result.keys())}")
            return {
                "success": False,
                "error": "Invalid data structure returned from scraper"
            }
        
        # If result is not a dict, return error
        logger.error(f"Invalid result type from scraping: {type(result)}")
        return {
            "success": False,
            "error": "Invalid data type returned from scraper"
        }
            
    except Exception as e:
        logger.error(f"Error getting anime about info: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_anime_episode_sources(ctx: Context, episode_id: str = "", category: str = "sub") -> dict:
    """Get anime episode streaming sources from ALL available servers for the specified category."""
    try:
        logger.info(f"Received request for episode sources: episode_id='{episode_id}', category='{category}'")

        if not episode_id:
            logger.error("Empty episode_id received")
            return {
                "success": False,
                "error": "episode_id is required"
            }

        if "?ep=" not in episode_id:
            logger.error(f"Invalid episode_id format: {episode_id}")
            return {
                "success": False,
                "error": "episode_id must be in format 'anime-title?ep=12345'"
            }

        if category not in ["sub", "dub", "raw"]:
            logger.error(f"Invalid category: {category}")
            return {
                "success": False,
                "error": "category must be one of: sub, dub, raw"
            }

        # Add timeout to prevent hanging connections
        try:
            result = await asyncio.wait_for(
                scrape_all_anime_episode_sources(episode_id, category),
                timeout=90.0  # 90 second timeout for multiple servers (45s per server * 2 servers max in parallel)
            )
        except asyncio.TimeoutError:
            logger.error(f"Timeout while fetching episode sources for {episode_id}")
            return {
                "success": False,
                "error": "Request timed out while fetching episode sources from all servers"
            }

        if not result:
            logger.error(f"No result from scraping for episode_id: {episode_id}")
            return {
                "success": False,
                "error": "Failed to fetch episode sources - no data returned"
            }

        logger.info(f"Successfully retrieved episode sources from all servers for {episode_id}")
        return result

    except asyncio.CancelledError:
        logger.warning(f"Request cancelled for episode_id: {episode_id}")
        # Don't return a response for cancelled requests - let the cancellation propagate
        raise
    except Exception as e:
        logger.error(f"Error getting anime episode sources: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_episode_servers(ctx: Context, episode_id: str = "") -> dict:
    """Get available servers for an anime episode."""
    try:
        logger.info(f"Received request for episode servers: episode_id='{episode_id}'")

        if not episode_id:
            logger.error("Empty episode_id received")
            return {
                "success": False,
                "error": "episode_id is required"
            }

        if "?ep=" not in episode_id:
            logger.error(f"Invalid episode_id format: {episode_id}")
            return {
                "success": False,
                "error": "episode_id must be in format 'anime-title?ep=12345'"
            }

        result = scrape_episode_servers(episode_id)
        logger.info(f"Successfully retrieved episode servers for {episode_id}")

        # Convert dataclass to dict for JSON serialization
        return {
            "success": True,
            "data": {
                "sub": [{"serverName": server.serverName, "serverId": server.serverId, "hianimeid": server.hianimeid} for server in result.sub],
                "dub": [{"serverName": server.serverName, "serverId": server.serverId, "hianimeid": server.hianimeid} for server in result.dub],
                "raw": [{"serverName": server.serverName, "serverId": server.serverId, "hianimeid": server.hianimeid} for server in result.raw],
                "episodeId": result.episodeId,
                "episodeNo": result.episodeNo
            }
        }

    except Exception as e:
        logger.error(f"Error getting episode servers: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_all_episode_servers(ctx: Context, episode_id: str = "", category: str = "sub") -> dict:
    """Get all available servers for an anime episode in a specific category."""
    try:
        logger.info(f"Received request for all episode servers: episode_id='{episode_id}', category='{category}'")

        if not episode_id:
            logger.error("Empty episode_id received")
            return {
                "success": False,
                "error": "episode_id is required"
            }

        if "?ep=" not in episode_id:
            logger.error(f"Invalid episode_id format: {episode_id}")
            return {
                "success": False,
                "error": "episode_id must be in format 'anime-title?ep=12345'"
            }

        if category not in ["sub", "dub", "raw"]:
            logger.error(f"Invalid category: {category}")
            return {
                "success": False,
                "error": "category must be one of: sub, dub, raw"
            }

        result = scrape_episode_servers(episode_id)
        logger.info(f"Successfully retrieved episode servers for {episode_id}")

        # Get servers for the specified category
        if category == "sub":
            servers = result.sub
        elif category == "dub":
            servers = result.dub
        else:  # raw
            servers = result.raw

        # Convert dataclass to dict for JSON serialization
        return {
            "success": True,
            "data": {
                "episodeId": result.episodeId,
                "episodeNo": result.episodeNo,
                "category": category,
                "servers": [{"serverName": server.serverName, "serverId": server.serverId, "hianimeid": server.hianimeid} for server in servers],
                "totalServers": len(servers)
            }
        }

    except Exception as e:
        logger.error(f"Error getting all episode servers: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# mcp.run()

# Start the server when this script is run directly
if __name__ == "__main__":
    import uvicorn

    # Log the startup
    logger.info("Starting Anime MCP server...")

    # Run the app with uvicorn with improved configuration
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=False,  # Reduce log noise
        timeout_keep_alive=30,  # Keep connections alive for 30 seconds
        timeout_graceful_shutdown=10  # Graceful shutdown timeout
    )