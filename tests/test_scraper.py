import requests
import logging
import sys
import os
import cloudscraper
from bs4 import BeautifulSoup

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.constants import SRC_BASE_URL, USER_AGENT_HEADER, ACCEPT_HEADER, ACCEPT_ENCODING_HEADER

# Set up logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

try:
    print("Starting direct HTTP request test...")
    anime_id = "attack-on-titan-112"
    anime_url = f"{SRC_BASE_URL}/{anime_id}"
      # Use cloudscraper to bypass Cloudflare protection
    scraper = cloudscraper.create_scraper()
    scraper.headers.update({
        "User-Agent": USER_AGENT_HEADER,
        "Accept": ACCEPT_HEADER,
        "Accept-Encoding": ACCEPT_ENCODING_HEADER
    })
    
    response = scraper.get(anime_url)
    response.raise_for_status()
    
    print(f"Response status: {response.status_code}")
    html_content = response.text
    
    # Save HTML content to file for inspection
    with open("anime_page.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"HTML content saved to anime_page.html (length: {len(html_content)})")
    
    # Try to parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check for basic elements
    body = soup.find("body")
    print(f"Found body tag: {body is not None}")
    
    if body:
        sync_data = body.find("script", id="syncData")
        print(f"Found syncData: {sync_data is not None}")
        
        # Test both old and new selectors
        ani_detail_old = soup.select_one("#ani_detail .container .anis-content")
        ani_detail_new = soup.select_one("#ani_detail .anis-content")
        print(f"Found anime detail content (old selector): {ani_detail_old is not None}")
        print(f"Found anime detail content (new selector): {ani_detail_new is not None}")

        if ani_detail_new:
            # Test extracting some basic info
            name_elem = ani_detail_new.select_one(".anisc-detail .film-name.dynamic-name")
            print(f"Found anime name: {name_elem.text.strip() if name_elem else 'Not found'}")

            desc_elem = ani_detail_new.select_one(".anisc-detail .film-description .text")
            print(f"Found description: {'Yes' if desc_elem else 'No'}")

            genres = ani_detail_new.select(".anisc-info .item-list a")
            print(f"Found genres: {[g.text.strip() for g in genres[:3]]}...")  # Show first 3
    
except Exception as e:
    print(f"Error occurred: {type(e).__name__}: {e}")
