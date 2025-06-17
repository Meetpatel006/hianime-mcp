"""Simple test to show the new all sources functionality."""
import asyncio
import sys
import os
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.management import get_logger

# Configure logging
logger = get_logger("TestSimpleAllSources")


async def test_simple_all_sources():
    """Simple test to show the new functionality."""
    try:
        logger.info("Testing new all sources functionality...")
        
        # Import the function
        from src.scrapers.animeEpisodeSrcs import get_all_anime_episode_sources
        
        episode_id = "attack-on-titan-112?ep=3303"
        category = "sub"
        
        result = await get_all_anime_episode_sources(episode_id, category)
        
        if result.get("success"):
            logger.info(f"✓ Successfully retrieved sources from all servers")
            data = result.get("data", {})
            
            print("\n" + "="*60)
            print("NEW ALL EPISODE SOURCES FUNCTIONALITY")
            print("="*60)
            print(f"Episode ID: {data.get('episodeId')}")
            print(f"Category: {data.get('category')}")
            print(f"Episode No: {data.get('episodeNo')}")
            print(f"Total servers: {data.get('totalServers')}")
            print(f"Successful servers: {data.get('successfulServers')}")
            print(f"Failed servers: {data.get('failedServers')}")
            print("="*60)
            
            sources = data.get('sources', {})
            print(f"\nSources from {len(sources)} servers:")
            
            for server_name, server_data in sources.items():
                print(f"\n📺 {server_name.upper()}:")
                print(f"   - Server ID: {server_data.get('serverId')}")
                print(f"   - HiAnime ID: {server_data.get('hianimeid')}")
                print(f"   - Sources: {len(server_data.get('sources', []))}")
                print(f"   - Has headers: {'Yes' if server_data.get('headers') else 'No'}")
                
                # Show first source URL (truncated)
                sources_list = server_data.get('sources', [])
                if sources_list:
                    url = sources_list[0].get('url', '')
                    if len(url) > 80:
                        url = url[:80] + "..."
                    print(f"   - Sample URL: {url}")
            
            print("\n" + "="*60)
            print("KEY BENEFITS:")
            print("✓ No need to specify individual servers")
            print("✓ Automatically fetches from ALL available servers")
            print("✓ Only requires episode_id and category parameters")
            print("✓ Provides sources from multiple servers for redundancy")
            print("="*60)
            
        else:
            logger.error(f"✗ Failed: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def main():
    """Run the simple test."""
    logger.info("Starting simple all sources test...")
    
    success = asyncio.run(test_simple_all_sources())
    
    if success:
        logger.info("✓ Test completed successfully")
        print("\n🎉 The new functionality is working perfectly!")
        print("Users now only need to provide episode_id and category!")
    else:
        logger.error("✗ Test failed")


if __name__ == "__main__":
    main()
