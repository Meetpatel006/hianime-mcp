#!/usr/bin/env python3
"""Test script to verify the server fixes work correctly."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.homePages import HomePageScraper
from src.management import get_logger

# Set up logging
logger = get_logger("ServerTest")

def test_home_page_scraper():
    """Test the HomePageScraper directly."""
    try:
        logger.info("Testing HomePageScraper...")
        
        scraper = HomePageScraper()
        result = scraper.get_home_page()
        
        logger.info(f"✓ Successfully scraped homepage")
        logger.info(f"  - Spotlight animes: {len(result.spotlightAnimes)}")
        logger.info(f"  - Trending animes: {len(result.trendingAnimes)}")
        logger.info(f"  - Genres: {len(result.genres)}")
        
        if result.spotlightAnimes:
            first_spotlight = result.spotlightAnimes[0]
            logger.info(f"  - First spotlight: {first_spotlight.name}")
        
        if result.trendingAnimes:
            first_trending = result.trendingAnimes[0]
            logger.info(f"  - First trending: {first_trending.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ HomePageScraper test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def test_mcp_tool():
    """Test the MCP tool function."""
    try:
        logger.info("Testing MCP tool function...")
        
        # Import the tool function
        from src.scrapers.homePages import get_home_page
        
        # Create a mock context (the function doesn't actually use it)
        class MockContext:
            pass
        
        ctx = MockContext()
        result = get_home_page(ctx)
        
        logger.info(f"✓ Successfully called MCP tool")
        logger.info(f"  - Spotlight animes: {len(result.get('spotlightAnimes', []))}")
        logger.info(f"  - Trending animes: {len(result.get('trendingAnimes', []))}")
        logger.info(f"  - Genres: {len(result.get('genres', []))}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ MCP tool test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all tests."""
    logger.info("=== Starting Server Fix Tests ===")
    
    tests = [
        ("HomePageScraper Direct", test_home_page_scraper),
        ("MCP Tool Function", test_mcp_tool)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            if test_func():
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
        logger.info("🎉 All server fix tests passed!")
        logger.info("The server should now work without Unicode encoding errors.")
    else:
        logger.warning(f"⚠️  {failed} test(s) failed")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
