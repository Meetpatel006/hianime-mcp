"""Test the otherInfo structure in API responses."""
import asyncio
import json
from mcp.server.fastmcp import Context

from src.scrapers.homePages import HomePageScraper
import main  # Import the main module with API functions

async def test_api_otherinfo():
    """Test the structure of otherInfo in API responses."""
    print("Testing API otherInfo structure...")
    
    # Create a mock context
    context = Context(
        args={},
        invocation_id="test_invocation",
        parent_invocation_id=None,
        conversation_id="test_conversation",
        request_id="test_request"
    )
    
    # Call get_home_page API function
    try:
        home_result = await main.get_home_page(context)
        if home_result.get("spotlightAnimes"):
            print("\nAPI Home Page - Spotlight Anime otherInfo:")
            anime = home_result["spotlightAnimes"][0]
            if "otherInfo" in anime:
                print(json.dumps(anime["otherInfo"], indent=2))
            else:
                print("No otherInfo found in spotlightAnimes")
    except Exception as e:
        print(f"Error calling get_home_page API: {str(e)}")
    
    # Call get_anime_recommendations API function
    try:
        recommendations = await main.get_anime_recommendations(context)
        if recommendations.get("spotlight"):
            print("\nAPI Recommendations - Spotlight Anime otherInfo:")
            if "otherInfo" in recommendations["spotlight"]:
                print(json.dumps(recommendations["spotlight"]["otherInfo"], indent=2))
            else:
                print("No otherInfo found in recommendations spotlight")
    except Exception as e:
        print(f"Error calling get_anime_recommendations API: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_api_otherinfo())
