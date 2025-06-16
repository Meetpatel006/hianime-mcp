"""Tests for anime about info scraping functionality."""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.animeAboutInfo import get_anime_about_info


class TestAnimeAboutInfo:
    """Test cases for anime about info scraping."""
    
    def test_invalid_anime_id_empty(self):
        """Test that empty anime ID raises ValueError."""
        with pytest.raises(ValueError, match="Anime ID cannot be empty"):
            get_anime_about_info("")
    
    def test_invalid_anime_id_none(self):
        """Test that None anime ID raises ValueError."""
        with pytest.raises(ValueError, match="Anime ID cannot be empty"):
            get_anime_about_info(None)
    
    def test_invalid_anime_id_whitespace(self):
        """Test that whitespace-only anime ID raises ValueError."""
        with pytest.raises(ValueError, match="Anime ID cannot be empty"):
            get_anime_about_info("   ")
    
    @patch('scrapers.animeAboutInfo.cloudscraper.create_scraper')
    def test_anime_id_validation_warning(self, mock_scraper):
        """Test that anime ID without hyphens generates warning."""
        # Mock the scraper to raise a 404 error (more realistic for invalid ID)
        mock_scraper_instance = Mock()
        mock_scraper_instance.headers = {}
        mock_scraper_instance.get.side_effect = Exception("404 Client Error: Not Found")
        mock_scraper.return_value = mock_scraper_instance

        # This should generate a warning and then raise a ValueError due to 404
        with pytest.raises(ValueError, match="Anime with ID 'invalidid' not found"):
            get_anime_about_info("invalidid")
    
    @patch('scrapers.animeAboutInfo.cloudscraper.create_scraper')
    def test_successful_scraping_with_fallback_selector(self, mock_scraper):
        """Test successful scraping when main selector fails but fallback works."""
        # Create mock HTML with content in a fallback location
        mock_html = """
        <html>
            <body>
                <div class="anis-content">
                    <div class="anisc-detail">
                        <div class="film-name dynamic-name">Test Anime</div>
                        <div class="film-description">
                            <div class="text">Test description</div>
                        </div>
                    </div>
                    <div class="film-stats">
                        <div class="tick">
                            <span class="tick-pg">PG-13</span>
                            <span class="tick-quality">HD</span>
                        </div>
                    </div>
                    <div class="anisc-info">
                        <div class="item-list">
                            <a>Action</a>
                            <a>Adventure</a>
                        </div>
                    </div>
                </div>
                <script id="syncData">{"anilist_id": "123", "mal_id": "456"}</script>
            </body>
        </html>
        """
        
        # Mock the scraper and response
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status.return_value = None
        
        mock_scraper_instance = Mock()
        mock_scraper_instance.get.return_value = mock_response
        mock_scraper_instance.headers = {}
        mock_scraper.return_value = mock_scraper_instance
        
        result = get_anime_about_info("test-anime-123")
        
        # Should successfully extract data using fallback selector
        assert result is not None
        assert result["success"] is True
        assert result["data"]["anime"]["info"].name == "Test Anime"
        assert result["data"]["anime"]["info"].description == "Test description"
        assert result["data"]["anime"]["info"].anilistId == 123
        assert result["data"]["anime"]["info"].malId == 456
        assert "Action" in result["data"]["anime"]["moreInfo"]["genres"]
        assert "Adventure" in result["data"]["anime"]["moreInfo"]["genres"]
    
    @patch('scrapers.animeAboutInfo.cloudscraper.create_scraper')
    def test_no_content_found(self, mock_scraper):
        """Test handling when no content is found with any selector."""
        # Create mock HTML with no recognizable content
        mock_html = """
        <html>
            <body>
                <div class="unrelated-content">Nothing here</div>
            </body>
        </html>
        """
        
        # Mock the scraper and response
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status.return_value = None
        
        mock_scraper_instance = Mock()
        mock_scraper_instance.get.return_value = mock_response
        mock_scraper_instance.headers = {}
        mock_scraper.return_value = mock_scraper_instance
        
        result = get_anime_about_info("test-anime-123")
        
        # Should return None when no content is found
        assert result is None
    
    @patch('scrapers.animeAboutInfo.cloudscraper.create_scraper')
    def test_http_404_error(self, mock_scraper):
        """Test handling of 404 errors."""
        # Mock the scraper to raise a 404 error
        mock_scraper_instance = Mock()
        mock_scraper_instance.headers = {}
        mock_scraper_instance.get.side_effect = Exception("404 Not Found")
        mock_scraper.return_value = mock_scraper_instance
        
        with pytest.raises(ValueError, match="Anime with ID 'test-anime-123' not found"):
            get_anime_about_info("test-anime-123")
    
    @patch('scrapers.animeAboutInfo.cloudscraper.create_scraper')
    def test_http_403_error(self, mock_scraper):
        """Test handling of 403 errors."""
        # Mock the scraper to raise a 403 error
        mock_scraper_instance = Mock()
        mock_scraper_instance.headers = {}
        mock_scraper_instance.get.side_effect = Exception("403 Forbidden")
        mock_scraper.return_value = mock_scraper_instance
        
        with pytest.raises(ValueError, match="Access forbidden for anime 'test-anime-123'"):
            get_anime_about_info("test-anime-123")
    
    @patch('scrapers.animeAboutInfo.cloudscraper.create_scraper')
    def test_timeout_error(self, mock_scraper):
        """Test handling of timeout errors."""
        # Mock the scraper to raise a timeout error
        mock_scraper_instance = Mock()
        mock_scraper_instance.headers = {}
        mock_scraper_instance.get.side_effect = Exception("timeout occurred")
        mock_scraper.return_value = mock_scraper_instance
        
        with pytest.raises(ValueError, match="Timeout when fetching anime 'test-anime-123'"):
            get_anime_about_info("test-anime-123")
    
    @patch('scrapers.animeAboutInfo.cloudscraper.create_scraper')
    def test_anime_id_cleanup(self, mock_scraper):
        """Test that anime ID is properly cleaned up."""
        # Mock the scraper and response
        mock_response = Mock()
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status.return_value = None
        
        mock_scraper_instance = Mock()
        mock_scraper_instance.get.return_value = mock_response
        mock_scraper_instance.headers = {}
        mock_scraper.return_value = mock_scraper_instance
        
        # Test with leading/trailing slashes
        get_anime_about_info("/test-anime-123/")
        
        # Verify the URL was constructed correctly (without extra slashes)
        expected_url = "https://hianime.sx/test-anime-123"
        mock_scraper_instance.get.assert_called_with(expected_url)


if __name__ == "__main__":
    pytest.main([__file__])
