#!/usr/bin/env python3
"""
Test script for the Knowledge Base MCP Server
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

# Add current directory to path to import our server
sys.path.insert(0, str(Path(__file__).parent))

@pytest.mark.asyncio
async def test_server():
    """Test the MCP server functionality."""
    print("🧪 Testing Knowledge Base MCP Server...")
    
    try:
        # Import server components
        from kb_server import mcp, init_database, kb_save, kb_search, kb_list
        
        print("✅ Server imports successful")
        
        # Initialize database
        print("🔧 Initializing database...")
        init_database()
        print("✅ Database initialization successful")
        
        # Test saving a memory
        print("💾 Testing memory save...")
        save_result = await kb_save(
            content="we use splunk on the cloud at https://company.splunkcloud.com for logging",
            memory_type="environment"
        )
        print(f"Save result: {save_result}")
        
        # Test saving a code snippet
        print("💾 Testing code snippet save...")
        code_result = await kb_save(
            content="""here's our graphql mutation test pattern:
```csharp
[Test]
public async Task TestGraphQLMutation() {
    var result = await client.SendMutationAsync(request);
    Assert.IsNotNull(result.Data);
}
```""",
            memory_type="code_snippet"
        )
        print(f"Code save result: {code_result}")
        
        # Test searching
        print("🔍 Testing memory search...")
        search_result = await kb_search(
            query="logging dashboard",
            limit=3
        )
        print(f"Search result: {search_result}")
        
        # Test listing
        print("📋 Testing memory list...")
        list_result = await kb_list(limit=5)
        print(f"List result: {list_result}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_server())