"""Test error handling and cancellation scenarios."""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.management import get_logger

# Configure logging
logger = get_logger("TestErrorHandling")


async def test_timeout_handling():
    """Test that timeouts are handled gracefully."""
    try:
        logger.info("Testing timeout handling...")
        
        from src.scrapers.animeEpisodeSrcs import get_all_anime_episode_sources
        
        # Use a valid episode ID
        episode_id = "attack-on-titan-112?ep=3303"
        category = "sub"
        
        # Test with a very short timeout to simulate timeout scenario
        try:
            result = await asyncio.wait_for(
                get_all_anime_episode_sources(episode_id, category),
                timeout=1.0  # Very short timeout to force timeout
            )
            logger.warning("Expected timeout but got result")
            return False
        except asyncio.TimeoutError:
            logger.info("✓ Timeout handled correctly")
            return True
        
    except Exception as e:
        logger.error(f"✗ Timeout test failed: {str(e)}")
        return False


async def test_cancellation_handling():
    """Test that cancellation is handled gracefully."""
    try:
        logger.info("Testing cancellation handling...")
        
        from src.scrapers.animeEpisodeSrcs import get_all_anime_episode_sources
        
        episode_id = "attack-on-titan-112?ep=3303"
        category = "sub"
        
        # Create a task and cancel it after a short delay
        task = asyncio.create_task(get_all_anime_episode_sources(episode_id, category))
        
        # Wait a bit then cancel
        await asyncio.sleep(2.0)
        task.cancel()
        
        try:
            await task
            logger.warning("Expected cancellation but task completed")
            return False
        except asyncio.CancelledError:
            logger.info("✓ Cancellation handled correctly")
            return True
        
    except Exception as e:
        logger.error(f"✗ Cancellation test failed: {str(e)}")
        return False


async def test_invalid_episode_id():
    """Test handling of invalid episode IDs."""
    try:
        logger.info("Testing invalid episode ID handling...")
        
        from src.scrapers.animeEpisodeSrcs import get_all_anime_episode_sources
        
        # Test with invalid episode ID
        invalid_episode_id = "invalid-episode-id"
        category = "sub"
        
        result = await get_all_anime_episode_sources(invalid_episode_id, category)
        
        if not result.get("success"):
            logger.info("✓ Invalid episode ID handled correctly")
            return True
        else:
            logger.warning("Expected error for invalid episode ID but got success")
            return False
        
    except Exception as e:
        logger.info(f"✓ Invalid episode ID caused expected exception: {str(e)}")
        return True


async def test_mcp_tool_error_handling():
    """Test MCP tool error handling."""
    try:
        logger.info("Testing MCP tool error handling...")
        
        from main import get_anime_episode_sources as mcp_tool
        
        class MockContext:
            pass
        
        ctx = MockContext()
        
        # Test with invalid episode ID
        result = await mcp_tool(ctx, "invalid-id", "sub")
        
        if not result.get("success"):
            logger.info("✓ MCP tool error handling works correctly")
            logger.info(f"  Error: {result.get('error')}")
            return True
        else:
            logger.warning("Expected error but got success")
            return False
        
    except Exception as e:
        logger.error(f"✗ MCP tool error test failed: {str(e)}")
        return False


def main():
    """Run error handling tests."""
    logger.info("Starting error handling tests...")
    
    tests = [
        ("Invalid Episode ID", test_invalid_episode_id),
        ("MCP Tool Error Handling", test_mcp_tool_error_handling),
        ("Timeout Handling", test_timeout_handling),
        ("Cancellation Handling", test_cancellation_handling),
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
    
    logger.info(f"\n--- Error Handling Test Results ---")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All error handling tests passed!")
    else:
        logger.warning(f"⚠ {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
