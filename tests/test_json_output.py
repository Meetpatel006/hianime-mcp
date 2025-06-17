"""Test to show the JSON output format with hianimeid field."""
import asyncio
import sys
import os
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.management import get_logger

# Configure logging
logger = get_logger("TestJSONOutput")


async def test_json_output():
    """Test and display the JSON output format."""
    try:
        logger.info("Testing JSON output format...")
        
        # Import the tool function
        from main import get_episode_servers as mcp_get_episode_servers
        
        # Create a mock context
        class MockContext:
            pass
        
        ctx = MockContext()
        episode_id = "attack-on-titan-112?ep=3303"
        
        result = await mcp_get_episode_servers(ctx, episode_id)
        
        if result.get("success"):
            logger.info("✓ Successfully retrieved episode servers")
            
            # Pretty print the JSON output
            print("\n" + "="*50)
            print("JSON OUTPUT FORMAT:")
            print("="*50)
            print(json.dumps(result, indent=2))
            print("="*50)
            
            # Show specific examples
            data = result.get("data", {})
            if data.get("sub"):
                print("\nExample Sub Server:")
                sub_server = data["sub"][0]
                print(f"  serverName: \"{sub_server['serverName']}\"")
                print(f"  serverId: {sub_server['serverId']}")
                print(f"  hianimeid: \"{sub_server['hianimeid']}\"")
            
            return True
        else:
            logger.error(f"✗ Failed to get episode servers: {result.get('error')}")
            return False
        
    except Exception as e:
        logger.error(f"✗ Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def main():
    """Run the JSON output test."""
    logger.info("Starting JSON output test...")
    
    success = asyncio.run(test_json_output())
    
    if success:
        logger.info("✓ JSON output test completed successfully")
    else:
        logger.error("✗ JSON output test failed")


if __name__ == "__main__":
    main()
