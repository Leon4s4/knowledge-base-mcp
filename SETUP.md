# Knowledge Base MCP Server - Setup Guide

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test the server**:
   ```bash
   python test_server.py
   ```

3. **Run examples**:
   ```bash
   python examples.py
   ```

4. **Start the server**:
   ```bash
   python kb_server.py
   ```

## GitHub Copilot Integration

### For VS Code (Recommended)

Add to your MCP configuration or VS Code settings:

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

### For Claude Desktop (Testing)

Copy `claude_desktop_config.json` to your Claude Desktop config directory and update the paths:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## Usage with GitHub Copilot

### Saving Memories

In GitHub Copilot, you can save memories using the `kb_save` tool:

```
#kb_save we use splunk at https://company.splunkcloud.com for logging
#kb_save when dynatrace fails, use DT_DISABLE flag and restart
#kb_save here's our test pattern: ```python
def test_api():
    assert response.status_code == 200
```
```

### Automatic Retrieval

GitHub Copilot will automatically search your knowledge base when you ask questions:

- "How do I check application logs?" → Returns Splunk dashboard info
- "How to fix dynatrace issues?" → Returns troubleshooting steps
- "Show me testing patterns" → Returns saved code snippets

### Manual Search

You can also explicitly search:

```
#kb_search logging dashboard
#kb_search graphql testing
#kb_search troubleshooting steps
```

## Features

✅ **Local Storage**: All data stored locally, no cloud dependencies  
✅ **Semantic Search**: Vector-based similarity search using ChromaDB  
✅ **Smart Metadata**: Auto-extracts technologies, URLs, and categorizes content  
✅ **Memory Types**: Environment, Code Snippets, Operational, Architectural  
✅ **Fast Performance**: Sub-500ms search with local embeddings  
✅ **Corporate Compliant**: No external API calls required  

## File Structure

```
kb-mcp/
├── kb_server.py                  # Main MCP server
├── test_server.py                # Functionality tests
├── test_initial_knowledge.py     # Initial knowledge loading tests
├── examples.py                   # Usage examples
├── requirements.txt              # Dependencies
├── initial_knowledge.txt         # Example initial knowledge file
├── claude_desktop_config.json    # Claude config template
├── README.md                     # Documentation
├── SETUP.md                      # This file
├── PRD-Knowledge-Base-MCP.md     # Product requirements
└── kb_data/                      # ChromaDB storage (auto-created)
```

## Troubleshooting

### Server Won't Start
- Check Python version: `python --version` (requires 3.9+)
- Install dependencies: `pip install -r requirements.txt`
- Check permissions on kb_data directory

### Poor Search Results
- Use specific keywords in searches
- Save more descriptive content
- Include technology names and URLs

### GitHub Copilot Not Finding Tools
- Verify MCP configuration paths are absolute
- Restart VS Code after configuration changes
- Check that server starts without errors

## Advanced Configuration

### Environment Variables

- `KB_DATA_DIR`: Custom data directory (default: `./kb_data`)
- `KB_INITIAL_FILE`: Path to initial knowledge file (optional)

### Bootstrap with Initial Knowledge

Create an `initial_knowledge.txt` file with your existing knowledge:

```
we use splunk at https://company.splunkcloud.com for logging

our grafana dashboard is at https://monitoring.company.com

when dynatrace fails, use DT_DISABLE flag and restart
```

Entries should be separated by double newlines. The server will automatically load these on startup.

### Custom Embedding Models

The server uses ChromaDB's default embeddings. To use different models, modify the embedding function in `init_database()`.

## Support

For issues or questions:
1. Check the examples in `examples.py`
2. Run `python test_server.py` to verify functionality
3. Review server logs for error messages