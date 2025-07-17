# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Knowledge Base MCP (Model Context Protocol) Server - a mem0-like memory system for GitHub Copilot that provides persistent knowledge storage and retrieval using local ChromaDB. The server enables GitHub Copilot to save and retrieve contextual information about development environments.

## Key Commands

### Testing and Development
```bash
# Install dependencies
pip install -r requirements.txt

# Test server functionality
python test_server.py

# Test initial knowledge loading
python test_initial_knowledge.py

# Run usage examples
python examples.py

# Start the MCP server
python kb_server.py
```

### No Build/Lint Commands
This is a pure Python project with no formal build, lint, or test runner configuration. Tests are run directly as Python scripts.

## Architecture

### Core Components
- **kb_server.py**: Main FastMCP server with ChromaDB integration
- **ChromaDB**: Local vector database for semantic search using `all-MiniLM-L6-v2` embeddings
- **FastMCP**: MCP server framework for tool definitions

### Key Tools
- `kb_save`: Save memories with automatic metadata extraction
- `kb_search`: Semantic search with vector similarity
- `kb_list`: List all saved memories with filtering
- `kb_delete`: Remove memories by ID

### Memory Types
- **Environment**: URLs, configurations, dashboard locations
- **Code Snippet**: Code examples and patterns
- **Operational**: Troubleshooting steps and fixes
- **Architectural**: Design decisions and system patterns

### Data Flow
1. Content saved via `kb_save` → metadata extraction → ChromaDB storage
2. Search queries → vector embedding → similarity search → ranked results
3. All data stored locally in `kb_data/` directory

## Configuration

### Environment Variables
- `KB_DATA_DIR`: ChromaDB storage directory (default: `./kb_data`)
- `KB_INITIAL_FILE`: Optional initial knowledge file to bootstrap database

### Integration Points
- Claude Desktop: `claude_desktop_config.json` template provided
- VS Code GitHub Copilot: MCP server configuration for tool integration

## Key Files
- **kb_server.py**: Main server implementation with all MCP tools
- **test_server.py**: Functionality testing script
- **test_initial_knowledge.py**: Tests for bootstrap knowledge loading
- **examples.py**: Usage demonstration script
- **initial_knowledge.txt**: Example bootstrap knowledge file
- **kb_data/**: ChromaDB persistent storage (auto-created)