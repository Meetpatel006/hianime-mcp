"""Anime episode sources scraping functionality."""
import requests
import urllib.parse
from bs4 import BeautifulSoup
import json
import asyncio
from typing import Dict, Any, Optional

# Import previously converted modules
from src.scrapers.extractor.rapidcloud import RapidCloud
from src.scrapers.extractor.streamsb import StreamSB
from src.scrapers.extractor.streamtape import StreamTape
from src.scrapers.extractor.megacloud import MegaCloud
from src.utils.constants import SRC_BASE_URL, SRC_AJAX_URL, USER_AGENT_HEADER
from src.management import get_logger

# Configure logging
logger = get_logger("AnimeEpisodeSources")

class HiAnimeError(Exception):
    """Custom exception for anime scraping errors."""
    def __init__(self, message: str, context: str, status_code: int):
        super().__init__(message)
        self.context = context
        self.status_code = status_code

# Enum for AnimeServers
class Servers:
    VidStreaming = "VidStreaming"
    VidCloud = "VidCloud"
    StreamSB = "StreamSB"
    StreamTape = "StreamTape"

# retrieveServerId function from the prompt
def retrieveServerId(soup: BeautifulSoup, index: int, category: str):
    server_item = soup.select_one(f".ps_-block.ps_-block-sub.servers-{category} > .ps__-list .server-item[data-server-id=\"{index}\"]")
    if server_item:
        return server_item.get("data-id")
    return None

async def _getAnimeEpisodeSources(
    episode_id: str,
    server: str = Servers.VidStreaming,
    category: str = "sub"
):
    if episode_id.startswith("http"):
        server_url = episode_id # In Python, we can directly use the string URL
        if server == Servers.VidStreaming or server == Servers.VidCloud:
            # MegaCloud extract2 is async
            extracted_data = await MegaCloud().extract3(server_url)
            return {
                "headers": {"Referer": urllib.parse.urlparse(server_url).scheme + "://" + urllib.parse.urlparse(server_url).netloc + "/"},
                **extracted_data,
            }
        elif server == Servers.StreamSB:
            # StreamSB extract is not async in the converted version, but let's keep it consistent with TS
            sources = StreamSB().extract(server_url, True)
            return {
                "headers": {
                    "Referer": server_url,
                    "watchsb": "streamsb",
                    "User-Agent": USER_AGENT_HEADER,
                },
                "sources": sources,
            }
        elif server == Servers.StreamTape:
            # StreamTape extract is not async in the converted version
            sources = StreamTape().extract(server_url)
            return {
                "headers": {
                    "Referer": server_url,
                    "User-Agent": USER_AGENT_HEADER,
                },
                "sources": sources,
            }
        else: # RapidCloud
            # RapidCloud extract is async
            extracted_data = await RapidCloud().extract(server_url)
            return {
                "headers": {"Referer": server_url},
                **extracted_data,
            }

    ep_id_full_url = f"{SRC_BASE_URL}/watch/{episode_id}"
    logger.info(f"EPISODE_ID: {ep_id_full_url}")

    try:
        # Extract the actual episode ID from the URL for the AJAX call
        # Assuming episodeId format is like 'some-anime-title-episode-1?ep=12345'
        ep_id_param = episode_id.split("?ep=")[1] if "?ep=" in episode_id else episode_id

        resp = requests.get(
            f"{SRC_AJAX_URL}/v2/episode/servers?episodeId={ep_id_param}",
            headers={
                "Referer": ep_id_full_url,
                "X-Requested-With": "XMLHttpRequest",
            },
            timeout=10  # Add timeout to prevent hanging
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.json()["html"], 'html.parser')

        server_id = None

        logger.info(f"THE SERVER: {server}")

        if server == Servers.VidCloud:
            server_id = retrieveServerId(soup, 1, category)
            if not server_id: raise Exception("RapidCloud not found")
        elif server == Servers.VidStreaming:
            server_id = retrieveServerId(soup, 4, category)
            logger.info(f"SERVER_ID: {server_id}")
            if not server_id: raise Exception("VidStreaming not found")
        elif server == Servers.StreamSB:
            server_id = retrieveServerId(soup, 5, category)
            if not server_id: raise Exception("StreamSB not found")
        elif server == Servers.StreamTape:
            server_id = retrieveServerId(soup, 3, category)
            if not server_id: raise Exception("StreamTape not found")

        # Fetch sources link
        sources_resp = requests.get(
            f"{SRC_AJAX_URL}/v2/episode/sources?id={server_id}",
            timeout=10  # Add timeout to prevent hanging
        )
        sources_resp.raise_for_status()
        link = sources_resp.json()["link"]
        logger.info(f"THE LINK: {link}")

        return await _getAnimeEpisodeSources(link, server, category)

    except requests.exceptions.RequestException as e:
        raise HiAnimeError.wrapError(e, "_getAnimeEpisodeSources")
    except Exception as err:
        raise HiAnimeError.wrapError(err, "_getAnimeEpisodeSources")


async def getAnimeEpisodeSources(
    episode_id: str,
    server: str,
    category: str
):
    if not episode_id or "?ep=" not in episode_id:
        raise HiAnimeError(
            "invalid anime episode id",
            "getAnimeEpisodeSources",
            400
        )
    if not category.strip():
        raise HiAnimeError(
            "invalid anime episode category",
            "getAnimeEpisodeSources",
            400
        )

    mal_id = None
    anilist_id = None

    anime_url = f"{SRC_BASE_URL}/watch/{episode_id.split('?ep=')[0]}"

    try:
        # Concurrently fetch episode sources and anime page data
        episode_src_data_task = _getAnimeEpisodeSources(episode_id, server, category)
        anime_src_req_task = asyncio.to_thread(requests.get, anime_url, headers={
            "Referer": SRC_BASE_URL,
            "User-Agent": USER_AGENT_HEADER,
            "X-Requested-With": "XMLHttpRequest",
        }, timeout=10)

        episode_src_data, anime_src_resp = await asyncio.gather(
            episode_src_data_task, anime_src_req_task
        )
        anime_src_resp.raise_for_status()

        logger.info(f"EPISODE_SRC_DATA: {json.dumps(episode_src_data)}")

        soup = BeautifulSoup(anime_src_resp.text, 'html.parser')

        try:
            sync_data_script = soup.find("script", id="syncData")
            if sync_data_script and sync_data_script.string:
                sync_data = json.loads(sync_data_script.string)
                anilist_id = int(sync_data.get("anilist_id")) if sync_data.get("anilist_id") else None
                mal_id = int(sync_data.get("mal_id")) if sync_data.get("mal_id") else None
        except Exception as err:
            logger.info(f"Error parsing syncData: {err}")
            anilist_id = None
            mal_id = None

        episode_src_data["anilistID"] = anilist_id
        episode_src_data["malID"] = mal_id

        return episode_src_data

    except requests.exceptions.RequestException as e:
        raise HiAnimeError.wrapError(e, "getAnimeEpisodeSources")
    except Exception as err:
        raise HiAnimeError.wrapError(err, "getAnimeEpisodeSources")

# Helper for HiAnimeError to wrap errors (assuming it's a static method)
# If HiAnimeError is a class, this needs to be a method of the class
# For now, let's define it as a standalone function or ensure it's part of the class
if not hasattr(HiAnimeError, 'wrapError'):
    def _wrap_error(err, context):
        if isinstance(err, HiAnimeError):
            return err
        return HiAnimeError(str(err), context, 500) # Default to 500 for unknown errors
    HiAnimeError.wrapError = staticmethod(_wrap_error)


async def get_anime_episode_sources(episode_id: str, server: str = "VidStreaming", category: str = "sub") -> Dict[str, Any]:
    """
    Get anime episode sources for streaming.

    Args:
        episode_id: The episode ID in format 'anime-title?ep=12345'
        server: The streaming server to use (VidStreaming, VidCloud, StreamSB, StreamTape)
        category: The category (sub or dub)

    Returns:
        Dictionary containing episode sources and metadata
    """
    try:
        logger.info(f"Getting episode sources for: {episode_id}, server: {server}, category: {category}")

        # Validate server parameter
        valid_servers = [Servers.VidStreaming, Servers.VidCloud, Servers.StreamSB, Servers.StreamTape]
        if server not in valid_servers:
            logger.warning(f"Invalid server '{server}', defaulting to VidStreaming")
            server = Servers.VidStreaming

        # Validate category parameter
        if category not in ["sub", "dub"]:
            logger.warning(f"Invalid category '{category}', defaulting to sub")
            category = "sub"

        result = await getAnimeEpisodeSources(episode_id, server, category)
        logger.info(f"Successfully retrieved episode sources for {episode_id}")

        return {
            "success": True,
            "data": result
        }

    except HiAnimeError as e:
        logger.error(f"HiAnimeError getting episode sources: {e.context} - {str(e)} (Status: {e.status_code})")
        return {
            "success": False,
            "error": str(e),
            "context": e.context,
            "status_code": e.status_code
        }
    except Exception as e:
        logger.error(f"Unexpected error getting episode sources: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "context": "get_anime_episode_sources"
        }


async def get_all_anime_episode_sources(episode_id: str, category: str = "sub") -> Dict[str, Any]:
    """
    Get anime episode sources from ALL available servers for a specific category.

    Args:
        episode_id: The episode ID in format 'anime-title?ep=12345'
        category: The category (sub, dub, or raw)

    Returns:
        Dictionary containing sources from all available servers and metadata
    """
    try:
        logger.info(f"Getting ALL episode sources for: {episode_id}, category: {category}")

        # Validate category parameter
        if category not in ["sub", "dub", "raw"]:
            logger.warning(f"Invalid category '{category}', defaulting to sub")
            category = "sub"

        # First, get the list of available servers for this episode and category
        from .animeEpisodeServers import get_episode_servers
        servers_result = get_episode_servers(episode_id)

        # Get servers for the specified category
        if category == "sub":
            available_servers = servers_result.sub
        elif category == "dub":
            available_servers = servers_result.dub
        else:  # raw
            available_servers = servers_result.raw

        if not available_servers:
            logger.warning(f"No servers available for category '{category}'")
            return {
                "success": True,
                "data": {
                    "episodeId": episode_id,
                    "category": category,
                    "servers": [],
                    "totalServers": 0,
                    "sources": {}
                }
            }

        # Map server IDs to server names for the episode sources scraper
        server_id_to_name = {
            1: Servers.VidCloud,    # rapidcloud
            3: Servers.StreamTape,  # streamtape
            4: Servers.VidStreaming, # vidstreaming
            5: Servers.StreamSB,    # streamsb
            6: Servers.VidCloud,    # megacloud (uses same extractor as rapidcloud)
        }

        sources_data = {}
        successful_servers = []
        failed_servers = []

        # Fetch sources from each available server with individual timeouts
        for server in available_servers:
            server_name = server.serverName
            server_id = server.serverId
            hianimeid = server.hianimeid

            try:
                # Map server ID to the appropriate server name for the scraper
                scraper_server = server_id_to_name.get(server_id, Servers.VidStreaming)

                logger.info(f"Fetching sources from {server_name} (ID: {server_id}, Scraper: {scraper_server})")

                # Get sources for this specific server with timeout
                server_result = await asyncio.wait_for(
                    getAnimeEpisodeSources(episode_id, scraper_server, category),
                    timeout=45.0  # 45 second timeout per server
                )

                sources_data[server_name] = {
                    "serverName": server_name,
                    "serverId": server_id,
                    "hianimeid": hianimeid,
                    "sources": server_result.get("sources", []),
                    "headers": server_result.get("headers", {}),
                    "anilistID": server_result.get("anilistID"),
                    "malID": server_result.get("malID")
                }

                successful_servers.append(server_name)
                logger.info(f"✓ Successfully fetched sources from {server_name}")

            except asyncio.TimeoutError:
                logger.warning(f"✗ Timeout fetching sources from {server_name} (45s limit)")
                failed_servers.append({
                    "serverName": server_name,
                    "serverId": server_id,
                    "hianimeid": hianimeid,
                    "error": "Request timed out after 45 seconds"
                })
            except asyncio.CancelledError:
                logger.warning(f"✗ Request cancelled while fetching from {server_name}")
                # Don't add to failed servers, just re-raise the cancellation
                raise
            except Exception as e:
                logger.warning(f"✗ Failed to fetch sources from {server_name}: {str(e)}")
                failed_servers.append({
                    "serverName": server_name,
                    "serverId": server_id,
                    "hianimeid": hianimeid,
                    "error": str(e)
                })

        logger.info(f"Successfully retrieved sources from {len(successful_servers)} servers, {len(failed_servers)} failed")

        return {
            "success": True,
            "data": {
                "episodeId": episode_id,
                "category": category,
                "episodeNo": servers_result.episodeNo,
                "totalServers": len(available_servers),
                "successfulServers": len(successful_servers),
                "failedServers": len(failed_servers),
                "sources": sources_data,
                "failedServersList": failed_servers
            }
        }

    except asyncio.CancelledError:
        logger.warning(f"Request cancelled while getting all episode sources for {episode_id}")
        # Re-raise cancellation to let it propagate properly
        raise

    except Exception as e:
        logger.error(f"Unexpected error getting all episode sources: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "context": "get_all_anime_episode_sources"
        }

# # Example Usage
# async def main():
#     # Example usage (replace with actual episode ID and server)
#     episode_id = "attack-on-titan-112?ep=3303"
#     server = Servers.VidStreaming
#     category = "sub"

#     try:
#         sources = await getAnimeEpisodeSources(episode_id, server, category)
#         print(json.dumps(sources, indent=4))
#     except HiAnimeError as e:
#         print(f"HiAnimeError: {e.context} (Status: {e.status_code})")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")

# if __name__ == "__main__":
#     asyncio.run(main())


