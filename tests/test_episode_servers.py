"""Test the episode servers scraper functionality."""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.management import get_logger
from src.scrapers.animeEpisodeServers import get_episode_servers, HiAnimeError

# Configure logging
logger = get_logger("TestEpisodeServers")


def test_episode_servers_scraper():
    """Test the episode servers scraper with a known episode."""
    try:
        logger.info("Testing episode servers scraper...")
        
        # Use a known episode ID (Attack on Titan example)
        episode_id = "attack-on-titan-112?ep=3303"
        
        result = get_episode_servers(episode_id)
        
        logger.info(f"✓ Successfully scraped episode servers")
        logger.info(f"  - Episode ID: {result.episodeId}")
        logger.info(f"  - Episode No: {result.episodeNo}")
        logger.info(f"  - Sub servers: {len(result.sub)}")
        logger.info(f"  - Dub servers: {len(result.dub)}")
        logger.info(f"  - Raw servers: {len(result.raw)}")
        
        # Print server details
        if result.sub:
            logger.info("  Sub servers:")
            for i, server in enumerate(result.sub):
                logger.info(f"    {i+1}. {server.serverName} (ID: {server.serverId})")
        
        if result.dub:
            logger.info("  Dub servers:")
            for i, server in enumerate(result.dub):
                logger.info(f"    {i+1}. {server.serverName} (ID: {server.serverId})")
        
        if result.raw:
            logger.info("  Raw servers:")
            for i, server in enumerate(result.raw):
                logger.info(f"    {i+1}. {server.serverName} (ID: {server.serverId})")
        
        return True
        
    except HiAnimeError as e:
        logger.error(f"✗ HiAnimeError: {e.context} - {str(e)} (Status: {e.status_code})")
        return False
    except Exception as e:
        logger.error(f"✗ Episode servers scraper test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def test_invalid_episode_id():
    """Test the episode servers scraper with invalid episode ID."""
    try:
        logger.info("Testing episode servers scraper with invalid episode ID...")
        
        # Test with invalid episode ID
        invalid_episode_id = "invalid-episode-id"
        
        try:
            result = get_episode_servers(invalid_episode_id)
            logger.error("✗ Expected HiAnimeError but got result")
            return False
        except HiAnimeError as e:
            logger.info(f"✓ Correctly caught HiAnimeError: {e.context} - {str(e)}")
            return True
        
    except Exception as e:
        logger.error(f"✗ Invalid episode ID test failed: {str(e)}")
        return False


async def test_mcp_tool():
    """Test the MCP tool function."""
    try:
        logger.info("Testing MCP tool function...")

        # Import the tool function
        from main import get_episode_servers as mcp_get_episode_servers

        # Create a mock context (the function doesn't actually use it)
        class MockContext:
            pass

        ctx = MockContext()
        episode_id = "attack-on-titan-112?ep=3303"

        result = await mcp_get_episode_servers(ctx, episode_id)

        if result.get("success"):
            logger.info(f"✓ Successfully called MCP tool")
            data = result.get("data", {})
            logger.info(f"  - Episode ID: {data.get('episodeId')}")
            logger.info(f"  - Episode No: {data.get('episodeNo')}")
            logger.info(f"  - Sub servers: {len(data.get('sub', []))}")
            logger.info(f"  - Dub servers: {len(data.get('dub', []))}")
            logger.info(f"  - Raw servers: {len(data.get('raw', []))}")
        else:
            logger.error(f"✗ MCP tool returned error: {result.get('error')}")
            return False

        return True

    except Exception as e:
        logger.error(f"✗ MCP tool test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


async def test_mcp_all_servers_tool():
    """Test the MCP all servers tool function."""
    try:
        logger.info("Testing MCP all servers tool function...")

        # Import the tool function
        from main import get_all_episode_servers as mcp_get_all_episode_servers

        # Create a mock context (the function doesn't actually use it)
        class MockContext:
            pass

        ctx = MockContext()
        episode_id = "attack-on-titan-112?ep=3303"

        # Test sub category
        result = await mcp_get_all_episode_servers(ctx, episode_id, "sub")

        if result.get("success"):
            logger.info(f"✓ Successfully called MCP all servers tool for sub")
            data = result.get("data", {})
            logger.info(f"  - Episode ID: {data.get('episodeId')}")
            logger.info(f"  - Episode No: {data.get('episodeNo')}")
            logger.info(f"  - Category: {data.get('category')}")
            logger.info(f"  - Total servers: {data.get('totalServers')}")

            servers = data.get('servers', [])
            for i, server in enumerate(servers):
                logger.info(f"    {i+1}. {server.get('serverName')} (ID: {server.get('serverId')})")
        else:
            logger.error(f"✗ MCP all servers tool returned error: {result.get('error')}")
            return False

        return True

    except Exception as e:
        logger.error(f"✗ MCP all servers tool test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def main():
    """Run all tests."""
    logger.info("Starting episode servers tests...")
    
    tests = [
        ("Episode Servers Scraper", test_episode_servers_scraper),
        ("Invalid Episode ID", test_invalid_episode_id),
        ("MCP Tool", lambda: asyncio.run(test_mcp_tool())),
        ("MCP All Servers Tool", lambda: asyncio.run(test_mcp_all_servers_tool())),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} test passed")
            else:
                logger.error(f"✗ {test_name} test failed")
        except Exception as e:
            logger.error(f"✗ {test_name} test crashed: {str(e)}")
    
    logger.info(f"\n--- Test Results ---")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
    else:
        logger.warning(f"⚠ {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
