"""Test file for HomePageScraper HTML functionality."""
import logging
import sys
import json
import os
from src.scrapers.homePages import HomePageScraper
from src.models import HomePage, SpotlightAnime, TrendingAnime

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_home_scraper_basic():
    """Test basic HomePageScraper functionality."""
    try:
        logger.info("Testing HomePageScraper basic functionality...")
        
        scraper = HomePageScraper()
        result = scraper.get_home_page()
        
        # Verify result type
        assert isinstance(result, HomePage), f"Expected HomePage object, got {type(result)}"
        
        # Test spotlight animes
        logger.info(f"Spotlight Animes: {len(result.spotlightAnimes)}")
        if result.spotlightAnimes:
            first_spotlight = result.spotlightAnimes[0]
            logger.info(f"First spotlight anime: {first_spotlight.name}")
            logger.info(f"Spotlight anime ID: {first_spotlight.id}")
            logger.info(f"Spotlight anime description: {first_spotlight.description[:100] if first_spotlight.description else 'None'}...")
            
            # Verify spotlight anime structure
            assert hasattr(first_spotlight, 'name'), "Spotlight anime missing name"
            assert hasattr(first_spotlight, 'id'), "Spotlight anime missing id"
            assert hasattr(first_spotlight, 'poster'), "Spotlight anime missing poster"
        
        # Test trending animes
        logger.info(f"Trending Animes: {len(result.trendingAnimes)}")
        if result.trendingAnimes:
            first_trending = result.trendingAnimes[0]
            logger.info(f"First trending anime: {first_trending.name}")
            logger.info(f"Trending anime ID: {first_trending.id}")
            logger.info(f"Trending anime rank: {first_trending.rank}")
            
            # Verify trending anime structure
            assert hasattr(first_trending, 'name'), "Trending anime missing name"
            assert hasattr(first_trending, 'id'), "Trending anime missing id"
            assert hasattr(first_trending, 'rank'), "Trending anime missing rank"
        
        # Test genres
        logger.info(f"Genres: {len(result.genres)}")
        if result.genres:
            logger.info(f"First 10 genres: {result.genres[:10]}")
            
            # Verify genres
            assert len(result.genres) > 0, "No genres found"
            assert all(isinstance(genre, str) for genre in result.genres), "All genres should be strings"
        
        logger.info("✓ Basic HomePageScraper test passed")
        return True
        
    except Exception as e:
        logger.error(f"Basic HomePageScraper test failed: {type(e).__name__}: {e}")
        return False

def test_home_scraper_data_quality():
    """Test data quality and completeness of HomePageScraper."""
    try:
        logger.info("Testing HomePageScraper data quality...")
        
        scraper = HomePageScraper()
        result = scraper.get_home_page()
        
        # Test spotlight anime data quality
        valid_spotlight_count = 0
        for anime in result.spotlightAnimes:
            if anime.name and anime.id:
                valid_spotlight_count += 1
                logger.debug(f"Valid spotlight anime: {anime.name} (ID: {anime.id})")
        
        logger.info(f"Valid spotlight animes: {valid_spotlight_count}/{len(result.spotlightAnimes)}")
        
        # Test trending anime data quality
        valid_trending_count = 0
        for anime in result.trendingAnimes:
            if anime.name and anime.id:
                valid_trending_count += 1
                logger.debug(f"Valid trending anime: {anime.name} (ID: {anime.id}, Rank: {anime.rank})")
        
        logger.info(f"Valid trending animes: {valid_trending_count}/{len(result.trendingAnimes)}")
        
        # Test genre data quality
        valid_genres = [genre for genre in result.genres if genre and len(genre.strip()) > 0]
        logger.info(f"Valid genres: {len(valid_genres)}/{len(result.genres)}")
        
        # Quality assertions
        assert valid_spotlight_count > 0, "No valid spotlight animes found"
        assert valid_trending_count > 0, "No valid trending animes found"
        assert len(valid_genres) > 10, "Too few valid genres found"
        
        logger.info("✓ Data quality test passed")
        return True
        
    except Exception as e:
        logger.error(f"Data quality test failed: {type(e).__name__}: {e}")
        return False

def test_home_scraper_html_content():
    """Test HTML content handling in HomePageScraper."""
    try:
        logger.info("Testing HomePageScraper HTML content handling...")
        
        scraper = HomePageScraper()
        
        # Test that no corrupted HTML file is created
        html_file_path = "home_page.html"
        if os.path.exists(html_file_path):
            os.remove(html_file_path)
        
        # Run the scraper
        result = scraper.get_home_page()
        
        # Check if HTML file was created and if it's valid
        if os.path.exists(html_file_path):
            with open(html_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if content is valid HTML
            if content.startswith('<!DOCTYPE html>') or '<html' in content.lower():
                logger.info("✓ Valid HTML file created")
                logger.info(f"HTML file size: {len(content)} characters")
            else:
                logger.warning("HTML file exists but content appears invalid")
                logger.debug(f"Content preview: {content[:200]}")
        else:
            logger.info("✓ No HTML file created (as expected with current implementation)")
        
        # Verify scraper still works regardless of file creation
        assert isinstance(result, HomePage), "Scraper should return HomePage object"
        assert len(result.spotlightAnimes) > 0 or len(result.trendingAnimes) > 0, "Should extract some anime data"
        
        logger.info("✓ HTML content handling test passed")
        return True
        
    except Exception as e:
        logger.error(f"HTML content handling test failed: {type(e).__name__}: {e}")
        return False

def test_home_scraper_json_output():
    """Test JSON serialization of HomePageScraper output."""
    try:
        logger.info("Testing HomePageScraper JSON output...")
        
        scraper = HomePageScraper()
        result = scraper.get_home_page()
        
        # Convert to dictionary format (similar to MCP tool output)
        json_data = {
            "spotlightAnimes": [
                {
                    "id": anime.id,
                    "name": anime.name,
                    "description": anime.description,
                    "poster": anime.poster,
                    "jname": anime.jname,
                    "episodes": {
                        "sub": anime.episodes.sub,
                        "dub": anime.episodes.dub
                    },
                    "type": anime.type,
                    "rank": anime.rank,
                    "otherInfo": anime.otherInfo
                }
                for anime in result.spotlightAnimes
            ],
            "trendingAnimes": [
                {
                    "id": anime.id,
                    "name": anime.name,
                    "poster": anime.poster,
                    "jname": anime.jname,
                    "episodes": {
                        "sub": anime.episodes.sub,
                        "dub": anime.episodes.dub
                    },
                    "type": anime.type,
                    "rank": anime.rank
                }
                for anime in result.trendingAnimes
            ],
            "genres": result.genres
        }
        
        # Test JSON serialization
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
        logger.info(f"JSON output size: {len(json_str)} characters")
        
        # Test JSON deserialization
        parsed_data = json.loads(json_str)
        
        # Verify structure
        assert "spotlightAnimes" in parsed_data, "Missing spotlightAnimes in JSON"
        assert "trendingAnimes" in parsed_data, "Missing trendingAnimes in JSON"
        assert "genres" in parsed_data, "Missing genres in JSON"
        
        logger.info(f"JSON contains {len(parsed_data['spotlightAnimes'])} spotlight animes")
        logger.info(f"JSON contains {len(parsed_data['trendingAnimes'])} trending animes")
        logger.info(f"JSON contains {len(parsed_data['genres'])} genres")
        
        # Save JSON output for inspection
        with open("home_page_output.json", "w", encoding="utf-8") as f:
            f.write(json_str)
        logger.info("✓ JSON output saved to home_page_output.json")
        
        logger.info("✓ JSON output test passed")
        return True
        
    except Exception as e:
        logger.error(f"JSON output test failed: {type(e).__name__}: {e}")
        return False

def run_all_tests():
    """Run all HomePageScraper tests."""
    logger.info("=== Starting HomePageScraper Tests ===")
    
    tests = [
        ("Basic Functionality", test_home_scraper_basic),
        ("Data Quality", test_home_scraper_data_quality),
        ("HTML Content Handling", test_home_scraper_html_content),
        ("JSON Output", test_home_scraper_json_output)
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
        logger.info("🎉 All tests passed!")
    else:
        logger.warning(f"⚠️  {failed} test(s) failed")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
