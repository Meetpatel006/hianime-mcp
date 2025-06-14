"""Quick test script for scrapers."""
from src.scrapers.homePages import HomePageScraper
# from  import HomePageScraper

def main():
    """Test the home page scraper and print some info."""
    print("Testing HomePageScraper...")
    scraper = HomePageScraper()
    result = scraper.get_home_page()
    
    print(f"Trending Animes: {len(result.trendingAnimes)}")
    print(f"Genres: {len(result.genres)}")
    
    print("\nFirst 3 Trending Anime:")
    for i, anime in enumerate(result.trendingAnimes[:3]):
        print(f"{i+1}. {anime.name} (ID: {anime.id})")
    
    print("\nFirst 10 Genres:")
    for i, genre in enumerate(result.genres[:10]):
        print(f"{i+1}. {genre}")

if __name__ == "__main__":
    main()
