# Knowledge Base MCP Server - Product Requirements Document

## Overview

A Model Context Protocol (MCP) server that provides intelligent memory and knowledge storage capabilities for GitHub Copilot, similar to mem0.ai. The server acts as an external memory system that GitHub Copilot can use to save and retrieve contextual information about your development environment, enhancing its responses with persistent knowledge about your specific setup, tools, and solutions.

**Key Concept**: GitHub Copilot calls this MCP server to save memories and retrieve relevant context, creating a personalized knowledge base that improves over time.

## Goals

- **Primary**: Create a mem0-like memory system that enhances GitHub Copilot with persistent contextual knowledge
- **Secondary**: Enable seamless saving and retrieval of environment-specific information through natural language
- **Tertiary**: Build a growing knowledge base that makes GitHub Copilot responses more accurate and personalized
- **Compliance**: Work within corporate constraints allowing only GitHub Copilot or local models

## Target Users

- **Primary**: Enterprise developers limited to GitHub Copilot for LLM interactions
- **Secondary**: Development teams needing persistent context across sessions
- **Tertiary**: Organizations requiring local-only knowledge storage for security compliance

## Core Features

### 1. Memory Storage (`kb_save` tool)
- **Trigger**: User types `#kb_save <memory content>` in GitHub Copilot
- **Content Types**: 
  - **Environment configs**: "we use splunk on the cloud at https://company.splunkcloud.com"
  - **Code snippets**: "here's how to create mutation tests for graphql: ```csharp [code] ```"
  - **Operational knowledge**: "when dynatrace fails in tanzu, use DT_DISABLE flag and restart"
  - **Tool locations**: "our grafana dashboard is at https://grafana.internal.com"
  - **Architecture decisions**: "we use graphql to expose dynamics 365 data"
- **Metadata**: Automatic extraction of domains, technologies, file types, timestamps
- **Processing**: Generate embeddings using local embedding models (no external API calls)

### 2. Memory Retrieval (`kb_search` tool)
- **Automatic Trigger**: GitHub Copilot automatically calls this when user asks questions
- **Semantic Search**: Vector-based similarity to find relevant memories
- **Context Enhancement**: Returns memories that enhance Copilot's response accuracy
- **Smart Filtering**: Prioritizes recent, relevant, and frequently accessed memories
- **Example Flow**: 
  - User: "How do I debug graphql issues?"
  - Copilot calls `kb_search("graphql debugging")`
  - Returns: GraphQL code snippets + Splunk dashboard URL + Previous solutions

### 3. Data Architecture
- **Vector Database**: ChromaDB with persistent client (local storage only)
- **Embedding Model**: Sentence Transformers (local, no API calls)
- **Storage**: ChromaDB handles all data persistence (vectors, metadata, documents)
- **Schema**:
  ```
  Memory Entry:
  - id: string
  - document: string (raw memory content)
  - metadata: {
      memory_type: enum(environment, code_snippet, operational, architectural),
      technologies: array[string] (auto-extracted: graphql, dynatrace, etc),
      urls: array[string] (auto-extracted links),
      language: string (for code snippets),
      access_count: int (usage tracking),
      created_at: timestamp,
      last_accessed: timestamp
    }
  - embedding: vector (auto-generated locally)
  ```

## Technical Specifications

### MCP Server Implementation
- **Language**: Python 3.9+
- **Framework**: MCP Python SDK
- **Protocol**: MCP 1.0 specification
- **Tools**:
  - `kb_save`: Save knowledge with automatic metadata extraction
  - `kb_search`: Semantic search with filtering options
  - `kb_list`: List saved knowledge entries
  - `kb_delete`: Remove knowledge entries

### Integration Requirements
- **ChromaDB**: In-process vector database with persistent storage
- **Sentence Transformers**: Local embedding generation (no external APIs)
- **Local Storage**: All data stored locally for corporate compliance
- **GitHub Copilot**: Primary and only LLM integration point
- **MCP Protocol**: Standard Model Context Protocol for tool communication

### Performance Requirements
- **Search Latency**: < 500ms for semantic search
- **Storage**: Support for 10,000+ knowledge entries
- **Memory**: Efficient embedding caching and retrieval

## User Experience

### Workflow Integration
1. **Saving Memories**: Developer types `#kb_save we use splunk at https://company.splunkcloud.com` in GitHub Copilot
2. **GitHub Copilot**: Calls MCP server's `kb_save` tool to persist this memory
3. **Later Sessions**: Developer asks "How do I check application logs?"
4. **Automatic Retrieval**: GitHub Copilot calls `kb_search("application logs")` 
5. **Enhanced Response**: Copilot responds with general logging advice + "Check your Splunk dashboard at https://company.splunkcloud.com"

### Tool Usage Examples
```python
# User types in GitHub Copilot: "#kb_save we use graphql to expose dynamics 365 data"
# GitHub Copilot calls:
kb_save(
  content="we use graphql to expose dynamics 365 data",
  memory_type="architectural"
)

# User types in GitHub Copilot: "#kb_save here's our graphql mutation test pattern: ```csharp [test code] ```"
kb_save(
  content="here's our graphql mutation test pattern: ```csharp [test code] ```",
  memory_type="code_snippet"
)

# Later, user asks: "How do I test graphql mutations?"
# GitHub Copilot automatically calls:
kb_search(
  query="graphql mutation testing",
  limit=3
)
# Returns relevant code snippets and architectural context
```

## Success Metrics

- **Effectiveness**: Retrieval accuracy (relevant results in top 3)
- **Performance**: Search response time < 500ms
- **Integration**: Usage within GitHub Copilot workflows

## Implementation Phases

### Phase 1: Core MVP
- Basic `kb_save` and `kb_search` tools
- ChromaDB with local sentence transformer embeddings
- GitHub Copilot MCP integration
- Memory persistence and retrieval

### Phase 2: Enhanced Features
- Automatic technology extraction (graphql, dynatrace, etc.)
- URL and code snippet detection
- Memory usage analytics and optimization
- Smart memory ranking based on access patterns

### Phase 3: Advanced Capabilities
- Memory categories and namespacing
- Automated memory extraction from documentation
- Integration with local LLM models as backup
- Memory export/import for team sharing

## Architecture Decisions

### Storage Strategy
- **Local-first**: All data stored locally for privacy and speed
- **In-process database**: ChromaDB runs as Python library, no containers needed
- **Unified storage**: ChromaDB handles vectors, metadata, and documents in single persistent store

### Security & Privacy
- **Local storage**: No cloud dependencies for sensitive code
- **Encryption**: At-rest encryption for stored knowledge
- **Access control**: File-system level permissions

### Scalability Considerations
- **Horizontal scaling**: Support for multiple project knowledge bases
- **Performance optimization**: Embedding caching and efficient vector search
- **Data management**: Automated cleanup of old/unused entries

## Dependencies

- **ChromaDB**: Vector database with persistent client
- **Sentence Transformers**: Local embedding model (all-MiniLM-L6-v2)
- **MCP Python SDK**: Official Python MCP server implementation
- **Python 3.9+**: Runtime environment
- **No External APIs**: Fully local operation for corporate compliance

## Risks & Mitigation

- **Storage growth**: Implement memory cleanup and archiving strategies
- **Search accuracy**: Fine-tune local embedding models for technical content
- **Corporate compliance**: Ensure all data stays local, no external API calls
- **Memory conflicts**: Handle duplicate or contradictory memories gracefully

## Future Enhancements

- **Multi-modal memories**: Images, diagrams, screenshots of dashboards
- **Team memory sharing**: Export/import memories across team members
- **Memory analytics**: Track which memories are most valuable
- **Smart memory suggestions**: Proactively suggest saving important context

## Comparison to mem0.ai

| Feature | mem0.ai | This MCP Server |
|---------|---------|----------------|
| **Memory Storage** | ✅ Cloud-based | ✅ Local-only |
| **LLM Integration** | ✅ Multiple providers | ✅ GitHub Copilot only |
| **Corporate Compliance** | ❌ External APIs | ✅ Fully local |
| **Semantic Search** | ✅ Advanced | ✅ Local embeddings |
| **Memory Types** | ✅ Flexible | ✅ Technical-focused |
| **Cost** | 💰 API costs | ✅ Free (local) |