"""Pytest configuration and fixtures."""
import os
import sys
import pytest
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

@pytest.fixture(scope="session")
def server_process(request):
    """Start the MCP server for testing."""
    import subprocess
    import time
    
    # Start server process
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    
    def cleanup():
        process.terminate()
        process.wait(timeout=5)
    
    request.addfinalizer(cleanup)
    return process

@pytest.fixture(scope="session")
def test_data():
    """Provide test data for anime tests."""
    return {
        "valid_anime_id": "spy-x-family",
        "invalid_anime_id": "not-a-real-anime-123",
        "test_spotlightanime": {
            "rank": 1,
            "id": "test-anime",
            "name": "Test Anime",
            "description": "Test description",
            "poster": "test.jpg",
            "jname": "テストアニメ",
            "episodes": {"sub": 12, "dub": 10},
            "type": "TV",
            "other_info": ["Info 1", "Info 2"]
        },
        "test_trendinganime": {
            "rank": 1,
            "id": "test-anime",
            "name": "Test Anime",
            "jname": "テストアニメ",
            "poster": "test.jpg"
        }
    }
