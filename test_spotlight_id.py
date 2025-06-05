"""Test script to verify the format of spotlight anime IDs."""
from src.scrapers.homePages import HomePageScraper
import json

def main():
    """Test the spotlight anime ID format."""
    print("Testing spotlight anime ID format...")
    scraper = HomePageScraper()
    result = scraper.get_home_page()
    
    # Format data using the same logic as in the API
    formatted_result = {
        "spotlightAnimes": [
            {
                "id": anime.id.split("/")[-1] if anime.id and "/" in anime.id else anime.id,
                "name": anime.name
            }
            for anime in result.spotlightAnimes[:3]  # Just take first 3 for brevity
        ]
    }
    
    # Check if the formatting is correct
    print("\nFirst 3 Spotlight Anime IDs:")
    for anime in formatted_result["spotlightAnimes"]:
        print(f"- {anime['name']}: {anime['id']}")
        # Verify no "watch/" prefix
        if "watch/" in anime["id"]:
            print(f"  ERROR: ID still contains 'watch/' prefix: {anime['id']}")
        # Verify the ID contains a dash and numbers (typical format for anime-name-12345)
        if "-" in anime["id"] and any(c.isdigit() for c in anime["id"]):
            print(f"  CORRECT: ID has the expected format")
        else:
            print(f"  WARNING: ID might not have the expected format")

if __name__ == "__main__":
    main()
