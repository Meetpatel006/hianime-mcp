"""Anime episode servers scraping functionality."""
import cloudscraper
from bs4 import BeautifulSoup
from typing import Optional

from src.management import get_logger
from src.utils.constants import SRC_BASE_URL, SRC_AJAX_URL
from src.utils.config import Config
from src.models import ScrapedEpisodeServers, EpisodeServer

# Configure logging
logger = get_logger("AnimeEpisodeServers")


class HiAnimeError(Exception):
    """Custom exception for anime scraping errors."""
    def __init__(self, message: str, context: str, status_code: int):
        super().__init__(message)
        self.context = context
        self.status_code = status_code

    @classmethod
    def wrap_error(cls, error: Exception, context: str):
        """Wrap an existing error with HiAnimeError."""
        if isinstance(error, cls):
            return error
        return cls(str(error), context, 500)


# Server ID to name mapping based on memories
SERVER_ID_MAP = {
    1: "rapidcloud",
    3: "streamtape",
    4: "vidstreaming",
    5: "streamsb",
    6: "megacloud"
}


def map_server_name(server_name: str, server_id: Optional[int]) -> str:
    """
    Map server name to proper name based on server ID.

    Args:
        server_name: Original server name from HTML
        server_id: Server ID number

    Returns:
        Mapped server name or original name if no mapping found
    """
    if server_id and server_id in SERVER_ID_MAP:
        return SERVER_ID_MAP[server_id]

    # Fallback to original name if no mapping found
    return server_name


def get_episode_servers(episode_id: str) -> ScrapedEpisodeServers:
    """
    Get available servers for an anime episode.
    
    Args:
        episode_id: The episode ID in format 'anime-title?ep=12345'
        
    Returns:
        ScrapedEpisodeServers object containing server information
        
    Raises:
        HiAnimeError: If episode_id is invalid or scraping fails
    """
    # Initialize result structure
    result = ScrapedEpisodeServers(
        sub=[],
        dub=[],
        raw=[],
        episodeId=episode_id,
        episodeNo=0
    )
    
    try:
        # Validate episode_id
        if not episode_id.strip() or "?ep=" not in episode_id:
            raise HiAnimeError(
                "invalid anime episode id",
                get_episode_servers.__name__,
                400
            )
        
        # Extract episode ID parameter
        ep_id = episode_id.split("?ep=")[1]
        
        # Create scraper instance
        scraper = cloudscraper.create_scraper()
        scraper.headers.update(Config.get_headers())
        
        # Make request to get episode servers
        ajax_url = f"{SRC_AJAX_URL}/v2/episode/servers?episodeId={ep_id}"
        referer_url = f"{SRC_BASE_URL}/watch/{episode_id}"
        
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": referer_url,
        }
        
        logger.info(f"Fetching episode servers from: {ajax_url}")
        response = scraper.get(ajax_url, headers=headers)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        if "html" not in data:
            raise HiAnimeError(
                "Invalid response format - missing html field",
                get_episode_servers.__name__,
                500
            )
        
        # Parse HTML content
        soup = BeautifulSoup(data["html"], 'html.parser')
        
        # Extract episode number
        ep_no_selector = ".server-notice strong"
        ep_no_elem = soup.select_one(ep_no_selector)
        if ep_no_elem:
            try:
                ep_no_text = ep_no_elem.get_text().strip()
                # Extract number from text like "Episode 1" or "Ep 1"
                ep_no_parts = ep_no_text.split()
                if ep_no_parts:
                    result.episodeNo = int(ep_no_parts[-1])
            except (ValueError, IndexError):
                logger.warning(f"Could not parse episode number from: {ep_no_elem.get_text()}")
                result.episodeNo = 0
        
        # Extract sub servers
        sub_servers = soup.select(".ps_-block.ps_-block-sub.servers-sub .ps__-list .server-item")
        for server_elem in sub_servers:
            server_link = server_elem.select_one("a")
            if server_link:
                original_server_name = server_link.get_text().lower().strip()
                server_id_attr = server_elem.get("data-server-id")
                server_id = None
                if server_id_attr:
                    try:
                        server_id = int(server_id_attr.strip())
                    except ValueError:
                        logger.warning(f"Invalid server ID: {server_id_attr}")

                # Map server name using server ID
                mapped_server_name = map_server_name(original_server_name, server_id)

                result.sub.append(EpisodeServer(
                    serverName=mapped_server_name,
                    serverId=server_id
                ))
        
        # Extract dub servers
        dub_servers = soup.select(".ps_-block.ps_-block-sub.servers-dub .ps__-list .server-item")
        for server_elem in dub_servers:
            server_link = server_elem.select_one("a")
            if server_link:
                original_server_name = server_link.get_text().lower().strip()
                server_id_attr = server_elem.get("data-server-id")
                server_id = None
                if server_id_attr:
                    try:
                        server_id = int(server_id_attr.strip())
                    except ValueError:
                        logger.warning(f"Invalid server ID: {server_id_attr}")

                # Map server name using server ID
                mapped_server_name = map_server_name(original_server_name, server_id)

                result.dub.append(EpisodeServer(
                    serverName=mapped_server_name,
                    serverId=server_id
                ))
        
        # Extract raw servers
        raw_servers = soup.select(".ps_-block.ps_-block-sub.servers-raw .ps__-list .server-item")
        for server_elem in raw_servers:
            server_link = server_elem.select_one("a")
            if server_link:
                original_server_name = server_link.get_text().lower().strip()
                server_id_attr = server_elem.get("data-server-id")
                server_id = None
                if server_id_attr:
                    try:
                        server_id = int(server_id_attr.strip())
                    except ValueError:
                        logger.warning(f"Invalid server ID: {server_id_attr}")

                # Map server name using server ID
                mapped_server_name = map_server_name(original_server_name, server_id)

                result.raw.append(EpisodeServer(
                    serverName=mapped_server_name,
                    serverId=server_id
                ))
        
        logger.info(f"Successfully scraped episode servers: sub={len(result.sub)}, dub={len(result.dub)}, raw={len(result.raw)}")
        return result
        
    except Exception as err:
        raise HiAnimeError.wrap_error(err, get_episode_servers.__name__)
