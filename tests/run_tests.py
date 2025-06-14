"""Run all test files in the tests directory."""
import asyncio
import importlib
import sys
from typing import Callable, Coroutine

TEST_MODULES = [
    "test_anime_scraper",
    "test_api_otherinfo", 
    "test_client",
    "test_extraction",
    "test_scraper",
    "test_otherinfo",
    "test_spotlight_id"
]

async def run_async_test(test_func: Callable[[], Coroutine]):
    """Run an async test function."""
    try:
        await test_func()
        print(f"✓ {test_func.__name__} passed")
        return True
    except Exception as e:
        print(f"✗ {test_func.__name__} failed: {str(e)}")
        return False

def run_sync_test(test_func: Callable):
    """Run a sync test function."""
    try:
        test_func()
        print(f"✓ {test_func.__name__} passed") 
        return True
    except Exception as e:
        print(f"✗ {test_func.__name__} failed: {str(e)}")
        return False

async def main():
    """Run all tests."""
    passed = 0
    failed = 0
    
    for module_name in TEST_MODULES:
        print(f"\n=== Running {module_name} ===")
        try:
            module = importlib.import_module(f"tests.{module_name}")
        except ImportError:
            print(f"Module {module_name} not found")
            continue
            
        for name, obj in vars(module).items():
            if name.startswith("test_"):
                if asyncio.iscoroutinefunction(obj):
                    success = await run_async_test(obj)
                else:
                    success = run_sync_test(obj)
                    
                if success:
                    passed += 1
                else:
                    failed += 1
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    sys.exit(failed > 0)

if __name__ == "__main__":
    asyncio.run(main())
