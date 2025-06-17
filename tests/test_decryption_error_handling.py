"""Test decryption error handling improvements."""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.management import get_logger

# Configure logging
logger = get_logger("TestDecryptionErrors")


async def test_episode_sources_with_potential_decryption_errors():
    """Test episode sources with potential decryption errors."""
    try:
        logger.info("Testing episode sources with improved decryption error handling...")
        
        from src.scrapers.animeEpisodeSrcs import get_all_anime_episode_sources
        
        # Use a real episode ID that might have decryption issues
        episode_id = "solo-leveling-season-2-arise-from-the-shadow-19413?ep=135478"
        category = "sub"
        
        result = await get_all_anime_episode_sources(episode_id, category)
        
        if result.get("success"):
            data = result.get("data", {})
            logger.info(f"✓ Episode sources request completed")
            logger.info(f"  - Episode ID: {data.get('episodeId')}")
            logger.info(f"  - Category: {data.get('category')}")
            logger.info(f"  - Total servers: {data.get('totalServers')}")
            logger.info(f"  - Successful servers: {data.get('successfulServers')}")
            logger.info(f"  - Failed servers: {data.get('failedServers')}")
            
            # Check for decryption-related failures
            failed_list = data.get('failedServersList', [])
            decryption_failures = []
            
            for failed in failed_list:
                error = failed.get('error', '')
                if 'decryption' in error.lower() or 'padding' in error.lower() or 'encrypt' in error.lower():
                    decryption_failures.append(failed)
                    logger.info(f"  📛 Decryption issue with {failed.get('serverName')}: {error}")
                else:
                    logger.info(f"  ⚠ Other error with {failed.get('serverName')}: {error}")
            
            if decryption_failures:
                logger.info(f"✓ Detected {len(decryption_failures)} decryption-related failures with improved error messages")
            else:
                logger.info("✓ No decryption failures detected")
            
            # Check successful servers
            sources = data.get('sources', {})
            for server_name, server_data in sources.items():
                source_count = len(server_data.get('sources', []))
                logger.info(f"  ✅ {server_name}: {source_count} sources")
            
        else:
            logger.error(f"✗ Request failed: {result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def test_decrypt_data_error_handling():
    """Test the decrypt_data function error handling."""
    try:
        logger.info("Testing decrypt_data error handling...")
        
        from src.scrapers.extractor.megacloud_getsrcs import decrypt_data
        
        # Test with invalid data that should cause padding error
        try:
            result = decrypt_data("invalid_base64_data", "test_key")
            logger.warning("Expected decryption to fail but it succeeded")
            return False
        except Exception as e:
            if "Failed to decrypt data" in str(e):
                logger.info(f"✓ Proper error handling: {str(e)}")
                return True
            else:
                logger.warning(f"Unexpected error format: {str(e)}")
                return False
        
    except Exception as e:
        logger.error(f"✗ Test failed: {str(e)}")
        return False


def main():
    """Run decryption error handling tests."""
    logger.info("Starting decryption error handling tests...")
    
    tests = [
        ("Decrypt Data Error Handling", test_decrypt_data_error_handling),
        ("Episode Sources with Decryption Errors", lambda: asyncio.run(test_episode_sources_with_potential_decryption_errors())),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} test passed")
            else:
                logger.error(f"✗ {test_name} test failed")
        except Exception as e:
            logger.error(f"✗ {test_name} test crashed: {str(e)}")
    
    logger.info(f"\n--- Decryption Error Handling Test Results ---")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All decryption error handling tests passed!")
    else:
        logger.warning(f"⚠ {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
