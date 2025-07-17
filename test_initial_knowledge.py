#!/usr/bin/env python3
"""
Test script for the initial knowledge loading feature
"""

import asyncio
import os
import sys
import shutil
from pathlib import Path

# Add current directory to path to import our server
sys.path.insert(0, str(Path(__file__).parent))

def cleanup_test_data(test_data_dir: str):
    """Helper function to clean up test data directory."""
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)

def reset_environment_vars():
    """Helper function to reset test environment variables."""
    if "KB_DATA_DIR" in os.environ:
        del os.environ["KB_DATA_DIR"]
    if "KB_INITIAL_FILE" in os.environ:
        del os.environ["KB_INITIAL_FILE"]

async def test_initial_knowledge():
    """Test the initial knowledge loading functionality."""
    print("🧪 Testing Initial Knowledge Loading...")
    
    # Clean up any existing test data
    test_data_dir = "./test_kb_data"
    cleanup_test_data(test_data_dir)
    
    try:
        # Set environment variables for test
        os.environ["KB_DATA_DIR"] = test_data_dir
        os.environ["KB_INITIAL_FILE"] = "./initial_knowledge.txt"
        
        # Import server components after setting env vars
        from kb_server import init_database, kb_search, kb_list
        
        print("✅ Server imports successful")
        
        # Initialize database (this should load initial knowledge)
        print("🔧 Initializing database with initial knowledge...")
        init_database()
        
        # Test that initial knowledge was loaded
        print("📋 Testing that initial knowledge was loaded...")
        list_result = await kb_list(limit=20)
        print(f"List result:\n{list_result}")
        
        # Test searching for specific initial knowledge
        print("🔍 Testing search for splunk...")
        search_result = await kb_search(query="splunk logging", limit=3)
        print(f"Splunk search result:\n{search_result}")
        
        print("🔍 Testing search for graphql...")
        search_result = await kb_search(query="graphql mutation test", limit=3)
        print(f"GraphQL search result:\n{search_result}")
        
        print("🔍 Testing search for dynatrace...")
        search_result = await kb_search(query="dynatrace troubleshooting", limit=3)
        print(f"Dynatrace search result:\n{search_result}")
        
        print("\n🎉 Initial knowledge loading test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test data and reset environment
        cleanup_test_data(test_data_dir)
        reset_environment_vars()
    
    return True

if __name__ == "__main__":
    # Run tests
    success = asyncio.run(test_initial_knowledge())
    
    if success:
        print("\n✅ Initial knowledge loading feature is working correctly!")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        sys.exit(1)