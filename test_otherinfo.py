"""Test script to verify the otherInfo structure."""
from src.scrapers.homePages import HomePageScraper
import json

def main():
    """Test the structured otherInfo output."""
    print("Testing otherInfo structure...")
    scraper = HomePageScraper()
    result = scraper.get_home_page()
    
    # Check spotlight anime otherInfo structure
    if result.spotlightAnimes:
        print("\nSpotlight Anime otherInfo:")
        anime = result.spotlightAnimes[0]
        
        # Original format
        print(f"\nOriginal format (array):")
        print(f"otherInfo: {anime.otherInfo}")
        
        # New structured format
        print(f"\nNew structured format (object):")
        structured_other_info = {
            "type": anime.otherInfo[0] if len(anime.otherInfo) > 0 else None,
            "duration": anime.otherInfo[1] if len(anime.otherInfo) > 1 else None,
            "releaseDate": anime.otherInfo[2] if len(anime.otherInfo) > 2 else None,
            "quality": anime.otherInfo[3] if len(anime.otherInfo) > 3 else None
        }
        print(json.dumps(structured_other_info, indent=2))
    else:
        print("No spotlight anime found")

if __name__ == "__main__":
    main()
