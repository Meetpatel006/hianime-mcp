"""Test the new all episode sources functionality."""
import asyncio
import sys
import os
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.management import get_logger

# Configure logging
logger = get_logger("TestAllEpisodeSources")


async def test_all_episode_sources_direct():
    """Test the all episode sources scraper directly."""
    try:
        logger.info("Testing all episode sources scraper directly...")
        
        # Import the function
        from src.scrapers.animeEpisodeSrcs import get_all_anime_episode_sources
        
        episode_id = "attack-on-titan-112?ep=3303"
        category = "sub"
        
        result = await get_all_anime_episode_sources(episode_id, category)
        
        if result.get("success"):
            logger.info(f"✓ Successfully retrieved sources from all servers")
            data = result.get("data", {})
            logger.info(f"  - Episode ID: {data.get('episodeId')}")
            logger.info(f"  - Category: {data.get('category')}")
            logger.info(f"  - Episode No: {data.get('episodeNo')}")
            logger.info(f"  - Total servers: {data.get('totalServers')}")
            logger.info(f"  - Successful servers: {data.get('successfulServers')}")
            logger.info(f"  - Failed servers: {data.get('failedServers')}")
            
            sources = data.get('sources', {})
            logger.info(f"  - Sources available from: {list(sources.keys())}")
            
            # Show details for each server
            for server_name, server_data in sources.items():
                logger.info(f"    {server_name}:")
                logger.info(f"      - Server ID: {server_data.get('serverId')}")
                logger.info(f"      - HiAnime ID: {server_data.get('hianimeid')}")
                logger.info(f"      - Sources count: {len(server_data.get('sources', []))}")
            
            failed_list = data.get('failedServersList', [])
            if failed_list:
                logger.info("  Failed servers:")
                for failed in failed_list:
                    logger.info(f"    - {failed.get('serverName')}: {failed.get('error')}")
        else:
            logger.error(f"✗ Failed to get all episode sources: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ All episode sources test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


async def test_mcp_tool_updated():
    """Test the updated MCP tool function."""
    try:
        logger.info("Testing updated MCP tool function...")
        
        # Import the tool function
        from main import get_anime_episode_sources as mcp_get_anime_episode_sources
        
        # Create a mock context
        class MockContext:
            pass
        
        ctx = MockContext()
        episode_id = "attack-on-titan-112?ep=3303"
        category = "sub"
        
        result = await mcp_get_anime_episode_sources(ctx, episode_id, category)
        
        if result.get("success"):
            logger.info(f"✓ Successfully called updated MCP tool")
            data = result.get("data", {})
            logger.info(f"  - Episode ID: {data.get('episodeId')}")
            logger.info(f"  - Category: {data.get('category')}")
            logger.info(f"  - Total servers: {data.get('totalServers')}")
            logger.info(f"  - Successful servers: {data.get('successfulServers')}")
            logger.info(f"  - Failed servers: {data.get('failedServers')}")
            
            sources = data.get('sources', {})
            logger.info(f"  - Sources from servers: {list(sources.keys())}")
        else:
            logger.error(f"✗ MCP tool returned error: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ MCP tool test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


async def test_different_categories():
    """Test with different categories."""
    try:
        logger.info("Testing different categories...")
        
        from src.scrapers.animeEpisodeSrcs import get_all_anime_episode_sources
        
        episode_id = "attack-on-titan-112?ep=3303"
        categories = ["sub", "dub"]
        
        for category in categories:
            logger.info(f"Testing category: {category}")
            result = await get_all_anime_episode_sources(episode_id, category)
            
            if result.get("success"):
                data = result.get("data", {})
                logger.info(f"  ✓ {category}: {data.get('successfulServers')} successful, {data.get('failedServers')} failed")
            else:
                logger.warning(f"  ⚠ {category}: {result.get('error')}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Different categories test failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    logger.info("Starting all episode sources tests...")
    
    tests = [
        ("All Episode Sources Direct", test_all_episode_sources_direct),
        ("Updated MCP Tool", test_mcp_tool_updated),
        ("Different Categories", test_different_categories),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            if asyncio.run(test_func()):
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
