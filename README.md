# Knowledge Base MCP Server

A mem0-like memory system for GitHub Copilot that provides persistent knowledge storage and retrieval capabilities using local ChromaDB. This MCP server enables GitHub Copilot to save and retrieve contextual information about your development environment, enhancing its responses with persistent knowledge.

## Features

- 🧠 **Persistent Memory**: Save development knowledge, code snippets, and environmental configurations
- 🔍 **Semantic Search**: Vector-based similarity search using local embeddings
- 🏷️ **Smart Categorization**: Automatic extraction of technologies, URLs, and memory types
- 🔒 **Local Storage**: All data stored locally for corporate compliance
- ⚡ **Fast Retrieval**: Sub-500ms search performance
- 🎯 **GitHub Copilot Integration**: Designed specifically for Copilot workflows
- 🌐 **Streamlit UI**: Web interface for searching and managing memories

## Memory Types

- **Environment**: Configuration, URLs, dashboard locations
- **Code Snippet**: Code examples, patterns, implementations
- **Operational**: Troubleshooting steps, fixes, operational knowledge
- **Architectural**: Design decisions, patterns, system architecture

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd kb-mcp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server**:
   ```bash
   python kb_server.py
   ```
   This also launches a Streamlit UI at [http://localhost:8501](http://localhost:8501) for managing memories.

## GitHub Copilot Integration

### Configure Claude Desktop (for testing)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "knowledge-base": {
      "command": "python",
      "args": ["/absolute/path/to/kb-mcp/kb_server.py"],
      "env": {
        "KB_DATA_DIR": "/absolute/path/to/kb-mcp/kb_data"
      }
    }
  }
}
```

### VS Code GitHub Copilot Configuration

Add to your VS Code settings or MCP configuration:

```json
{
  "mcpServers": {
    "knowledge-base": {
      "command": "python",
      "args": ["/absolute/path/to/kb-mcp/kb_server.py"],
      "env": {
        "KB_DATA_DIR": "/absolute/path/to/kb-mcp/kb_data",
        "KB_INITIAL_FILE": "/absolute/path/to/kb-mcp/initial_knowledge.txt"
      }
    }
  }
}
```

## Usage Examples

### Saving Memories

In GitHub Copilot, use the `kb_save` tool:

```
#kb_save we use splunk on the cloud at https://company.splunkcloud.com
#kb_save when dynatrace fails in tanzu, use DT_DISABLE flag and restart the instance
#kb_save here's our graphql mutation test pattern: ```csharp
[Test]
public async Task TestGraphQLMutation() {
    // test code here
}
```
```

### Searching Knowledge

GitHub Copilot will automatically search when you ask questions:

```
"How do I check application logs?"
→ Copilot calls kb_search("application logs")
→ Returns Splunk dashboard URL + previous solutions
```

### Manual Search

You can also explicitly search:

```
#kb_search graphql testing
#kb_search dynatrace troubleshooting
#kb_search dashboard urls
```

## Available Tools

### `kb_save`
Save a memory to the knowledge base.
- **content**: The memory content to save
- **memory_type**: Optional type (environment, code_snippet, operational, architectural)
- **tags**: Optional list of tags for categorization

### `kb_search`
Search for relevant memories.
- **query**: Search query
- **limit**: Maximum results (default: 5)
- **memory_type**: Filter by type
- **include_metadata**: Include detailed metadata

### `kb_list`
List all saved memories.
- **memory_type**: Filter by type
- **limit**: Maximum entries (default: 10)
- **include_content**: Show full content vs summary

### `kb_delete`
Delete a memory by ID.
- **memory_id**: Full or partial memory ID

## Configuration

### Environment Variables

- `KB_DATA_DIR`: Directory for ChromaDB storage (default: `./kb_data`)
- `KB_INITIAL_FILE`: Optional path to initial knowledge file to load on startup
- `KB_UI_PORT`: Port for the Streamlit UI (default: `8501`)

### Initial Knowledge File

You can bootstrap the knowledge base with pre-existing information by providing an initial knowledge file. The file should contain knowledge entries separated by double newlines (`\n\n`).

**Example `initial_knowledge.txt`:**
```
we use splunk on the cloud at https://company.splunkcloud.com for application logging

our grafana dashboard is at https://grafana.internal.com/dashboards

when dynatrace fails in tanzu, use DT_DISABLE flag and restart the instance

here's our graphql test pattern:
```csharp
[Test]
public async Task TestAPI() {
    // test code here
}
```
```

**Features:**
- ✅ Automatic metadata extraction (technologies, URLs, memory types)
- ✅ Entries marked with `source: initial_knowledge` 
- ✅ Loads only on first startup (won't duplicate entries)
- ✅ Supports all content types (code, configs, operational knowledge)

### Embedding Model

The server uses `all-MiniLM-L6-v2` by default for local embeddings. This provides:
- Fast inference
- Good semantic understanding
- No external API calls
- Small memory footprint

## Data Storage

All data is stored locally in ChromaDB format:
- **Vector embeddings**: For semantic search
- **Document content**: Raw memory text
- **Metadata**: Extracted technologies, URLs, timestamps, access counts

## Performance

- **Search latency**: < 500ms typical
- **Storage capacity**: 10,000+ memories
- **Memory usage**: ~200MB for model + data
- **Embedding generation**: ~10ms per memory

## Security & Privacy

- ✅ **Local-only storage**: No cloud dependencies
- ✅ **No external APIs**: Embeddings generated locally
- ✅ **File-system permissions**: Standard OS-level access control
- ✅ **Corporate compliant**: Designed for enterprise environments

## Troubleshooting

### Server Won't Start
- Check Python version (3.9+ required)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check data directory permissions

### Poor Search Results
- Ensure memories are saved with clear, descriptive content
- Use specific technology keywords
- Try different search terms

### Memory Not Found
- Use `kb_list` to see all saved memories
- Check memory type filters
- Verify memory was actually saved (check for success message)

## Development

### Project Structure
```
kb-mcp/
├── kb_server.py                  # Main MCP server
├── test_server.py                # Functionality tests
├── test_initial_knowledge.py     # Initial knowledge loading tests
├── examples.py                   # Usage demonstrations
├── requirements.txt              # Python dependencies
├── initial_knowledge.txt         # Example initial knowledge file
├── claude_desktop_config.json    # Configuration template
├── README.md                     # Complete documentation
├── SETUP.md                      # Quick setup guide
├── PRD-Knowledge-Base-MCP.md     # Product requirements
└── kb_data/                      # ChromaDB storage (created automatically)
```

### Adding New Features

The server uses FastMCP for easy tool development:

```python
@mcp.tool()
async def new_tool(param: str) -> str:
    """Tool description."""
    # Implementation
    return "Result"
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]