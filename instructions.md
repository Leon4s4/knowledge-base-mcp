# Knowledge Base MCP Instructions

You have access to a persistent knowledge base system via the Model Context Protocol (MCP) at the endpoint knowledge-base. Use the following tools:

**kb_save**: Store a new memory or piece of knowledge. Parameters: content (required, the knowledge to save), memory_type (optional, one of: environment, code_snippet, operational, architectural), tags (optional, list of tags for categorization).

**kb_search**: Search for relevant memories using semantic similarity. Parameters: query (required, search query), limit (optional, max results 1-10, default 5), memory_type (optional, filter by type), include_metadata (optional, include details like creation date and access count, default true).

**kb_list**: List all saved memories with optional filtering. Parameters: memory_type (optional, filter by type), limit (optional, max entries 1-50, default 10), include_content (optional, show full content vs summary, default false).

**kb_delete**: Delete a memory from the knowledge base. Parameters: memory_id (required, full or partial ID from kb_list - supports partial matching for convenience).

## Memory Types
- **environment**: Environment-specific information (configs, setups, dependencies)
- **code_snippet**: Code examples, functions, and implementation details  
- **operational**: Operational procedures, workflows, and processes
- **architectural**: System architecture, design patterns, and structural information
- **general**: Default type for miscellaneous information

## Usage Tips
- Use **kb_save** to store important information you want to remember across conversations
- Use **kb_search** to find relevant memories when answering questions or solving problems
- Use **kb_list** to browse existing memories and get IDs for deletion
- Use **kb_delete** with partial IDs (like first 8 characters) for easy cleanup
- Memory types help organize and filter knowledge - choose the most appropriate type
- The system automatically extracts metadata like technologies, URLs, and creation timestamps
- Access counts track how often memories are retrieved via search

Use these tools to build a persistent knowledge base that enhances your ability to assist users with consistent, contextual information across sessions.
