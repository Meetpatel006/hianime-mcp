"""Test the anime episode sources scraper."""
import asyncio
import json
from src.management import get_logger
from src.scrapers.animeEpisodeSrcs import get_anime_episode_sources, Servers

# Configure logging
logger = get_logger("TestEpisodeSources")

async def test_episode_sources_direct():
    """Test the episode sources scraper directly."""
    try:
        logger.info("Testing episode sources scraper directly...")
        
        # Test with a sample episode ID (you may need to adjust this)
        episode_id = "attack-on-titan-112?ep=3303"
        server = Servers.VidStreaming
        category = "sub"
        
        result = await get_anime_episode_sources(episode_id, server, category)
        
        if result.get("success"):
            logger.info("✓ Successfully retrieved episode sources")
            logger.info(f"  - Episode ID: {episode_id}")
            logger.info(f"  - Server: {server}")
            logger.info(f"  - Category: {category}")
            
            data = result.get("data", {})
            if "sources" in data:
                logger.info(f"  - Sources found: {len(data['sources'])}")
            if "anilistID" in data:
                logger.info(f"  - AniList ID: {data['anilistID']}")
            if "malID" in data:
                logger.info(f"  - MAL ID: {data['malID']}")
        else:
            logger.error(f"✗ Failed to retrieve episode sources: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Episode sources test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

async def test_episode_sources_invalid_input():
    """Test the episode sources scraper with invalid input."""
    try:
        logger.info("Testing episode sources scraper with invalid input...")
        
        # Test with invalid episode ID
        result = await get_anime_episode_sources("invalid-episode-id", "VidStreaming", "sub")
        
        if not result.get("success"):
            logger.info("✓ Correctly handled invalid episode ID")
            return True
        else:
            logger.error("✗ Should have failed with invalid episode ID")
            return False
        
    except Exception as e:
        logger.error(f"✗ Invalid input test failed: {str(e)}")
        return False

async def test_episode_sources_different_servers():
    """Test the episode sources scraper with different servers."""
    try:
        logger.info("Testing episode sources scraper with different servers...")
        
        episode_id = "attack-on-titan-112?ep=3303"
        servers = [Servers.VidStreaming, Servers.VidCloud]
        
        for server in servers:
            logger.info(f"Testing server: {server}")
            result = await get_anime_episode_sources(episode_id, server, "sub")
            
            if result.get("success"):
                logger.info(f"✓ Successfully retrieved sources from {server}")
            else:
                logger.warning(f"⚠ Failed to retrieve sources from {server}: {result.get('error')}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Different servers test failed: {str(e)}")
        return False

async def main():
    """Run all tests."""
    logger.info("=== Starting Episode Sources Tests ===")
    
    tests = [
        ("Episode Sources Direct", test_episode_sources_direct),
        ("Episode Sources Invalid Input", test_episode_sources_invalid_input),
        ("Episode Sources Different Servers", test_episode_sources_different_servers)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            if await test_func():
                passed += 1
                logger.info(f"✓ {test_name} test PASSED")
            else:
                failed += 1
                logger.error(f"✗ {test_name} test FAILED")
        except Exception as e:
            failed += 1
            logger.error(f"✗ {test_name} test FAILED with exception: {e}")
    
    logger.info(f"\n=== Test Results ===")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total: {passed + failed}")
    
    if failed == 0:
        logger.info("🎉 All tests passed!")
    else:
        logger.warning(f"⚠ {failed} test(s) failed")

if __name__ == "__main__":
    asyncio.run(main())
