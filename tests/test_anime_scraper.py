# from scrapers.animeAboutInfo import get_anime_about_info
from src.scrapers.animeAboutInfo import get_anime_about_info
import logging
import sys
import cloudscraper
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_anime_scraper():
    try:
        logger.info("Testing anime scraper...")
        
        # Create a cloudscraper session with proper browser settings
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        # Set headers
        scraper.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Get anime info
        result = get_anime_about_info("attack-on-titan-112")
        
        # Print key information
        logger.info("\nResult summary:")
        if result and result.get("success"):
            data = result["data"]
            anime_info = data["anime"]["info"]
            logger.info(f"Anime ID: {anime_info.id}")
            logger.info(f"Anime Name: {anime_info.name}")
            logger.info(f"Description: {anime_info.description[:100] if anime_info.description else None}")
            logger.info(f"Stats: {anime_info.stats}")
            logger.info(f"Number of seasons: {len(data['seasons'])}")
            logger.info(f"Number of related animes: {len(data['relatedAnimes'])}")
            logger.info(f"Number of popular animes: {len(data['mostPopularAnimes'])}")
            logger.info(f"Number of recommended animes: {len(data['recommendedAnimes'])}")
        else:
            logger.error("Failed to get anime information or result was unsuccessful")
        
        return result
        
    except Exception as e:
        logger.error(f"Error occurred: {type(e).__name__}: {e}")
        raise

if __name__ == "__main__":
    test_anime_scraper()
