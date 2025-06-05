import requests
import logging
import sys
import cloudscraper
from bs4 import BeautifulSoup
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
        
        ani_detail = soup.select_one("#ani_detail .container .anis-content")
        print(f"Found anime detail content: {ani_detail is not None}")
    
except Exception as e:
    print(f"Error occurred: {type(e).__name__}: {e}")
