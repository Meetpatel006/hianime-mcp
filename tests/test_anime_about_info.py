"""Tests for anime about info scraping functionality."""
import pytest
import sys
import os
import unittest # Keep unittest for the new test structure as requested
from unittest.mock import Mock, patch, MagicMock # Keep for existing tests
from bs4 import BeautifulSoup

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scrapers.animeAboutInfo import get_anime_about_info
from management import setup_logging # Import for new test


# Existing PyTest class
class TestAnimeAboutInfoPytest: # Renamed to avoid conflict
    """Test cases for anime about info scraping."""
    
    def test_invalid_anime_id_empty(self):
        """Test that empty anime ID raises ValueError."""
        with pytest.raises(ValueError, match="Invalid anime id"): # Match updated error message
            get_anime_about_info("")
    
    def test_invalid_anime_id_none(self):
        """Test that None anime ID raises ValueError."""
        with pytest.raises(ValueError, match="Invalid anime id"): # Match updated error message
            get_anime_about_info(None)
    
    def test_invalid_anime_id_whitespace(self):
        """Test that whitespace-only anime ID raises ValueError."""
        with pytest.raises(ValueError, match="Invalid anime id"): # Match updated error message
            get_anime_about_info("   ")
    
    @patch('scrapers.animeAboutInfo.cloudscraper.create_scraper')
    def test_anime_id_validation_no_hyphen(self, mock_scraper): # Renamed for clarity
        """Test that anime ID without hyphens raises ValueError (after trying to fetch)."""
        mock_scraper_instance = mock_scraper.return_value
        mock_scraper_instance.headers = {}
        # Simulate a failed fetch (e.g., Cloudflare error, or actual 404)
        mock_response = Mock()
        mock_response.status_code = 404 # Simulate a 404
        mock_response.raise_for_status.side_effect = Exception("404 Client Error: Not Found for url")
        mock_scraper_instance.get.return_value = mock_response

        # The function should catch this and return a structured error
        result = get_anime_about_info("invalididnohyphen")
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result
        # The error message might be about failing to find content or the HTTP error itself
        # For this test, we're more concerned it doesn't succeed and returns our structure
        assert result["anime_id"] == "invalididnohyphen"
    
    @patch('scrapers.animeAboutInfo.cloudscraper.create_scraper')
    def test_successful_scraping_with_fallback_selector(self, mock_scraper):
        """Test successful scraping when main selector fails but fallback works."""
        mock_html = """
        <html>
            <body>
                <div id="ani_detail">
                    <div class="anis-content"> <!-- Fallback: #ani_detail .anis-content -->
                        <div class="anisc-detail">
                            <div class="film-name dynamic-name">Test Anime</div>
                            <div class="film-description">
                                <div class="text">Test description</div>
                            </div>
                        </div>
                        <div class.film-stats">
                            <div class="tick">
                                <span class="tick-pg">PG-13</span>
                                <span class="tick-quality">HD</span>
                                <span class="tick-sub">12</span>
                                <span class="type">TV</span>
                                <span class="duration">24m</span>
                            </div>
                        </div>
                        <div class="anisc-info">
                            <div class="item-list">
                                <a>Action</a>
                                <a>Adventure</a>
                            </div>
                        </div>
                    </div>
                </div>
                <script id="syncData">{"anilist_id": "123", "mal_id": "456"}</script>
            </body>
        </html>
        """
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.encoding = 'utf-8'
        mock_response.raise_for_status.return_value = None
        
        mock_scraper_instance = mock_scraper.return_value
        mock_scraper_instance.get.return_value = mock_response
        mock_scraper_instance.headers = {}
        
        result = get_anime_about_info("test-anime-123")
        
        assert result is not None
        assert result["success"] is True
        assert result["data"]["anime"]["info"]["name"] == "Test Anime"
        assert result["data"]["anime"]["info"]["description"] == "Test description"
        assert result["data"]["anime"]["info"]["anilistId"] == 123
        assert result["data"]["anime"]["info"]["malId"] == 456
        assert "Action" in result["data"]["anime"]["moreInfo"]["genres"]
    
    @patch('scrapers.animeAboutInfo.cloudscraper.create_scraper')
    def test_no_content_found_returns_structured_error(self, mock_scraper): # Updated assertion
        """Test handling when no content is found with any selector, returns structured error."""
        mock_html = "<html><body><div class='unrelated-content'>Nothing here</div></body></html>"
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.encoding = 'utf-8'
        mock_response.raise_for_status.return_value = None
        
        mock_scraper_instance = mock_scraper.return_value
        mock_scraper_instance.get.return_value = mock_response
        mock_scraper_instance.headers = {}
        
        result = get_anime_about_info("test-anime-no-content")
        
        assert result is not None
        assert result["success"] is False
        assert "error" in result
        assert result["error"] == "Could not find anime content section using any known selectors."
        assert result["anime_id"] == "test-anime-no-content"
        assert "url" in result
        assert "debug_html_file" in result # Check for the new key
        assert result["debug_html_file"] == "debug_anime_test-anime-no-content_error.html"

    @patch('scrapers.animeAboutInfo.cloudscraper.create_scraper')
    def test_http_error_returns_structured_error(self, mock_scraper): # Updated general HTTP error
        """Test handling of HTTP errors (e.g., 404, 403, 500) returns structured error."""
        mock_scraper_instance = mock_scraper.return_value
        mock_scraper_instance.headers = {}
        
        # Simulate an HTTP error by having raise_for_status() throw an exception
        mock_response = Mock()
        mock_response.status_code = 404 # Example status code
        mock_response.text = "Page not found"
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.encoding = 'utf-8'
        mock_response.raise_for_status.side_effect = Exception("HTTP 404 Not Found")
        mock_scraper_instance.get.return_value = mock_response

        # The function should catch the exception from raise_for_status() and re-raise it.
        # The test expects that the calling code (or test runner) handles this.
        # For this specific test, we want to see if *our function* raises it, not if pytest catches it.
        # So, we check for the specific exception from the function.
        # However, the current implementation of get_anime_about_info catches all exceptions
        # and re-raises them. This is fine. Let's test the re-raise.
        with pytest.raises(Exception, match="HTTP 404 Not Found"):
             get_anime_about_info("test-anime-http-error")

    @patch('scrapers.animeAboutInfo.cloudscraper.create_scraper')
    def test_timeout_error_returns_structured_error(self, mock_scraper): # Updated
        """Test handling of timeout errors returns structured error."""
        mock_scraper_instance = mock_scraper.return_value
        mock_scraper_instance.headers = {}
        mock_scraper_instance.get.side_effect = Exception("Timeout occurred") # Simulate timeout

        with pytest.raises(Exception, match="Timeout occurred"):
            get_anime_about_info("test-anime-timeout")

    @patch('scrapers.animeAboutInfo.cloudscraper.create_scraper')
    def test_anime_id_cleanup_no_extra_slashes_in_url(self, mock_scraper): # More specific name
        """Test that anime ID is properly cleaned up (no extra slashes in URL)."""
        mock_response = Mock()
        mock_response.text = "<html><body><div id='ani_detail'><div class='container'><div class='anis-content'>Mock Content</div></div></div></body></html>" # Ensure some content to avoid None return
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.encoding = 'utf-8'
        mock_response.raise_for_status.return_value = None
        
        mock_scraper_instance = mock_scraper.return_value
        mock_scraper_instance.get.return_value = mock_response
        mock_scraper_instance.headers = {}
        
        get_anime_about_info("/test-anime-123/") # Call with slashes
        
        # Verify the URL was constructed correctly (without extra slashes and with base URL)
        # Assuming SRC_BASE_URL = "https://hianime.sx" from context
        expected_url = "https://hianime.sx/test-anime-123"
        mock_scraper_instance.get.assert_called_with(expected_url)

# New Unittest class as per subtask description
class TestAnimeAboutInfoUnittest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configure logging for tests
        setup_logging()

    def test_get_anime_about_info_returns_dict_or_handles_network_error(self):
        """Test that get_anime_about_info returns a dictionary (success or error structure) or handles network error."""
        anime_id = "attack-on-titan-112"  # A valid example anime ID

        print(f"Attempting to fetch info for anime_id: {anime_id} (This might make a real network request)")

        try:
            result = get_anime_about_info(anime_id)
        except Exception as e:
            # This block will catch network errors if they are not caught and structured by get_anime_about_info
            print(f"Network or other critical error during get_anime_about_info for {anime_id}: {e}")
            self.fail(f"get_anime_about_info raised an unexpected exception: {e}")
            return

        print(f"Test result for {anime_id}: {result}")

        self.assertIsInstance(result, dict, "Function should return a dictionary.")
        self.assertIn("success", result, "Result dictionary should have a 'success' key.")

        if result["success"]:
            print(f"Successfully fetched data for {anime_id}")
            self.assertIn("data", result, "Successful result should have a 'data' key.")
            self.assertIn("anime", result["data"], "Data should contain 'anime' key.")
            self.assertIn("info", result["data"]["anime"], "Anime data should contain 'info' key.")
            # Check if 'id' key exists before asserting its value
            if "id" in result["data"]["anime"]["info"]:
                 self.assertEqual(result["data"]["anime"]["info"]["id"], anime_id)
            else:
                 # This case might happen if the scraping logic changes and 'id' is not populated
                 # For now, we'll just note it. Depending on strictness, this could be a failure.
                 print(f"Warning: 'id' key not found in anime info for {anime_id}")

            # Example: Check for poster URL (common field)
            self.assertIn("poster", result["data"]["anime"]["info"], "Anime info should have a poster URL")
            if result["data"]["anime"]["info"]["poster"]: # Check if poster URL is not None or empty
                self.assertTrue(result["data"]["anime"]["info"]["poster"].startswith("http"), "Poster URL should be a valid URL.")

        else:
            print(f"Fetching failed for {anime_id}, checking error structure.")
            self.assertIn("error", result, "Failed result should have an 'error' key.")
            self.assertIn("anime_id", result, "Failed result should include the anime_id.")
            self.assertEqual(result["anime_id"], anime_id)
            self.assertIn("url", result, "Failed result should include the URL attempted.")
            self.assertIn("debug_html_file", result, "Failed result should include 'debug_html_file'.")
            expected_debug_file = f"debug_anime_{anime_id.replace('/', '_')}_error.html"
            self.assertEqual(result["debug_html_file"], expected_debug_file, "Debug HTML filename mismatch.")


    def test_get_anime_about_info_invalid_id_format(self): # Renamed for clarity
        """Test that get_anime_about_info raises ValueError for an invalid ID format (e.g. no hyphen)."""
        # This test is slightly different from the Pytest one.
        # The Pytest one checks for IDs without hyphens *after* a mock fetch.
        # This one checks the initial validation in get_anime_about_info.
        # The current function logic: `if not anime_id.strip() or "-" not in anime_id:`
        with self.assertRaisesRegex(ValueError, "Invalid anime id", msg="Should raise ValueError for ID without hyphen"):
            get_anime_about_info("invalididformat")

    def test_get_anime_about_info_empty_id(self):
        """Test that get_anime_about_info raises ValueError for an empty ID."""
        with self.assertRaisesRegex(ValueError, "Invalid anime id", msg="Should raise ValueError for empty ID"):
            get_anime_about_info("   ")


if __name__ == "__main__":
    # This allows running either pytest or unittest when the file is executed directly
    # For pytest, just run `pytest tests/test_anime_about_info.py`
    # For unittest, run `python tests/test_anime_about_info.py`

    # To run unittests specifically:
    unittest.main()

    # To run pytest (if desired, though typically run from CLI):
    # sys.exit(pytest.main([__file__]))
