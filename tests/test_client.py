"""Test client for the anime MCP server."""
import asyncio
from typing import Any, Dict
from mcp.client import Client

async def test_anime_info():
    """Test fetching anime information."""
    async with Client() as client:
        print("\n=== Testing Anime Homepage ===")
        try:
            # Get homepage data
            result = await client.call("get_home_page")
            if result.get("spotlight_animes"):
                print("\nSpotlight Animes:")
                for anime in result["spotlight_animes"][:2]:  # Show first 2
                    print(f"- {anime['name']} ({anime['jname']})")
                    print(f"  Type: {anime['type']}")
                    print(f"  Episodes: Sub={anime['episodes']['sub']}, Dub={anime['episodes']['dub']}")
            
            if result.get("trending_animes"):
                print("\nTrending Animes:")
                for anime in result["trending_animes"][:3]:  # Show first 3
                    print(f"- {anime['name']} (Rank: {anime['rank']})")
            
            if result.get("genres"):
                print("\nAvailable Genres:")
                print(", ".join(result["genres"][:10]))  # Show first 10 genres
        
        except Exception as e:
            print(f"Error getting homepage: {str(e)}")

        # Get detailed anime info
        print("\n=== Testing Anime Details ===")
        try:
            # Use first spotlight anime ID
            anime_id = result["spotlight_animes"][0]["id"]
            print(f"Fetching details for anime ID: {anime_id}")
            
            details = await client.call("get_anime_about_info", anime_id=anime_id)
            if details["success"]:
                info = details["data"]["anime"]["info"]
                print(f"\nAnime Information:")
                print(f"Name: {info['name']}")
                print(f"Description: {info['description'][:200]}...")  # First 200 chars
                
                if info.get("stats"):
                    stats = info["stats"]
                    print(f"\nStats:")
                    print(f"Rating: {stats.get('rating', 'N/A')}")
                    print(f"Quality: {stats.get('quality', 'N/A')}")
                    print(f"Type: {stats.get('type', 'N/A')}")
                    print(f"Duration: {stats.get('duration', 'N/A')}")
                
                if details["data"]["anime"]["moreInfo"]:
                    more_info = details["data"]["anime"]["moreInfo"]
                    print(f"\nGenres: {', '.join(more_info['genres'])}")
                    print(f"Studios: {', '.join(more_info['studios'])}")
                
                if details["data"].get("recommendedAnimes"):
                    print(f"\nRecommended Anime Count: {len(details['data']['recommendedAnimes'])}")
            
        except Exception as e:
            print(f"Error getting anime details: {str(e)}")

async def test_error_handling():
    """Test error handling with invalid requests."""
    async with Client() as client:
        print("\n=== Testing Error Handling ===")
        
        # Test with invalid anime ID
        try:
            await client.call("get_anime_about_info", anime_id="invalid-id")
        except Exception as e:
            print(f"Expected error with invalid ID: {str(e)}")

if __name__ == "__main__":
    print("Starting MCP Client Tests...")
    
    # Run tests
    asyncio.run(test_anime_info())
    asyncio.run(test_error_handling())
    
    print("\nTests completed.")
