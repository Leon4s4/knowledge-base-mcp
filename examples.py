#!/usr/bin/env python3
"""
Example usage of the Knowledge Base MCP Server
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path to import our server
sys.path.insert(0, str(Path(__file__).parent))

from kb_server import init_database, kb_save, kb_search, kb_list, kb_delete

async def run_examples():
    """Run example operations with the Knowledge Base."""
    print("🚀 Knowledge Base MCP Server Examples")
    print("=" * 50)
    
    # Initialize database
    print("\n1️⃣ Initializing Knowledge Base...")
    init_database()
    
    # Example 1: Save environment information
    print("\n2️⃣ Saving environment information...")
    result = await kb_save(
        content="we use splunk on the cloud at https://company.splunkcloud.com for application logs and monitoring",
        memory_type="environment"
    )
    print(f"Result: {result}")
    
    # Example 2: Save operational knowledge
    print("\n3️⃣ Saving operational knowledge...")
    result = await kb_save(
        content="when dynatrace fails in tanzu, use DT_DISABLE flag and restart the instance. Check logs in /var/log/dynatrace",
        memory_type="operational"
    )
    print(f"Result: {result}")
    
    # Example 3: Save code snippet
    print("\n4️⃣ Saving code snippet...")
    result = await kb_save(
        content="""here's our graphql mutation test pattern:
```csharp
[Test]
public async Task TestGraphQLMutation() {
    var mutation = @"
        mutation CreateUser($input: UserInput!) {
            createUser(input: $input) {
                id
                name
                email
            }
        }";
    
    var request = new GraphQLRequest
    {
        Query = mutation,
        Variables = new { input = new { name = "John", email = "john@test.com" } }
    };
    
    var result = await client.SendMutationAsync(request);
    Assert.IsNotNull(result.Data);
    Assert.IsNull(result.Errors);
}
```""",
        memory_type="code_snippet",
        tags=["testing", "mutation", "best-practice"]
    )
    print(f"Result: {result}")
    
    # Example 4: Save architectural decision
    print("\n5️⃣ Saving architectural decision...")
    result = await kb_save(
        content="we use graphql to expose dynamics 365 data. Authentication is handled via Azure AD tokens. Rate limiting is 1000 requests per minute per client.",
        memory_type="architectural"
    )
    print(f"Result: {result}")
    
    # Example 5: Search for logging-related memories
    print("\n6️⃣ Searching for logging information...")
    result = await kb_search(
        query="application logs monitoring",
        limit=3
    )
    print(f"Search Result:\n{result}")
    
    # Example 6: Search for testing information
    print("\n7️⃣ Searching for testing information...")
    result = await kb_search(
        query="graphql testing patterns",
        limit=2
    )
    print(f"Search Result:\n{result}")
    
    # Example 7: Search for troubleshooting info
    print("\n8️⃣ Searching for troubleshooting information...")
    result = await kb_search(
        query="dynatrace restart fix",
        memory_type="operational"
    )
    print(f"Search Result:\n{result}")
    
    # Example 8: List all memories
    print("\n9️⃣ Listing all memories...")
    result = await kb_list(limit=10)
    print(f"All Memories:\n{result}")
    
    # Example 9: List only code snippets
    print("\n🔟 Listing code snippets...")
    result = await kb_list(
        memory_type="code_snippet",
        include_content=True
    )
    print(f"Code Snippets:\n{result}")
    
    print("\n✅ Examples completed!")
    print("\n" + "=" * 50)
    print("💡 Usage Tips:")
    print("- Use specific keywords in your searches")
    print("- Save context about your specific environment")
    print("- Include URLs, flags, and specific steps in operational knowledge")
    print("- Tag code snippets with relevant technologies")
    print("- GitHub Copilot will automatically call kb_search when you ask questions!")

if __name__ == "__main__":
    asyncio.run(run_examples())