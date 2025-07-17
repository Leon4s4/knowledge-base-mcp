#!/usr/bin/env python3
"""
Knowledge Base MCP Server

A mem0-like memory system for GitHub Copilot that provides persistent 
knowledge storage and retrieval capabilities using local ChromaDB.
"""

import asyncio
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("knowledge-base")

# Global variables for database connection
chroma_client: Optional[chromadb.PersistentClient] = None
collection: Optional[chromadb.Collection] = None

# Configuration
KB_DATA_DIR = os.getenv("KB_DATA_DIR", "./kb_data")
KB_INITIAL_FILE = os.getenv("KB_INITIAL_FILE", None)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "knowledge_base"


def init_database():
    """Initialize ChromaDB with built-in embeddings."""
    global chroma_client, collection
    
    # Create data directory if it doesn't exist
    os.makedirs(KB_DATA_DIR, exist_ok=True)
    
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(
        path=KB_DATA_DIR,
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True,
            is_persistent=True,
            persist_directory=KB_DATA_DIR
        )
    )
    
    # Create embedding function (uses default model)
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    # Get or create collection with embedding function
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=default_ef,
        metadata={"description": "Knowledge base for development memories"}
    )
    
    print(f"Knowledge Base initialized at: {KB_DATA_DIR}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Embedding: Default ChromaDB embeddings")
    
    # Load initial knowledge file if specified
    if KB_INITIAL_FILE:
        load_initial_knowledge(KB_INITIAL_FILE)


def load_initial_knowledge(file_path: str):
    """Load initial knowledge from a text file."""
    if not collection:
        print("❌ Cannot load initial knowledge: Database not initialized")
        return
    
    try:
        if not os.path.exists(file_path):
            print(f"⚠️ Initial knowledge file not found: {file_path}")
            return
        
        # Check if initial knowledge was already loaded
        existing = collection.get(
            where={"source": "initial_knowledge"},
            limit=1
        )
        
        if existing["ids"]:
            print(f"ℹ️ Initial knowledge already loaded ({len(existing['ids'])} entries found), skipping...")
            return
        
        print(f"📖 Loading initial knowledge from: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            print("⚠️ Initial knowledge file is empty")
            return
        
        # Split content by double newlines to separate entries
        entries = [entry.strip() for entry in content.split('\n\n') if entry.strip()]
        
        if not entries:
            print("⚠️ No knowledge entries found in file")
            return
        
        loaded_count = 0
        for i, entry in enumerate(entries):
            try:
                # Generate unique ID for each entry
                entry_id = f"initial_{i}_{uuid.uuid4().hex[:8]}"
                
                # Extract metadata
                metadata = extract_metadata(entry)
                metadata["source"] = "initial_knowledge"
                metadata["initial_load"] = True
                
                # Store in ChromaDB
                collection.add(
                    ids=[entry_id],
                    documents=[entry],
                    metadatas=[metadata]
                )
                
                loaded_count += 1
                
            except Exception as e:
                print(f"⚠️ Failed to load entry {i+1}: {str(e)}")
                continue
        
        print(f"✅ Loaded {loaded_count} knowledge entries from initial file")
        
    except Exception as e:
        print(f"❌ Error loading initial knowledge: {str(e)}")


def extract_metadata(content: str) -> Dict[str, Any]:
    """Extract metadata from content automatically."""
    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_accessed": datetime.now(timezone.utc).isoformat(),
        "access_count": 0,
        "technologies": "",
        "urls": "",
        "language": "",
        "memory_type": "general"
    }
    
    # Extract URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, content)
    if urls:
        metadata["urls"] = ",".join(urls)
    
    # Extract code blocks and detect language
    code_pattern = r'```(\w+)?\n(.*?)```'
    code_matches = re.findall(code_pattern, content, re.DOTALL)
    if code_matches:
        metadata["memory_type"] = "code_snippet"
        for lang, _ in code_matches:
            if lang:
                metadata["language"] = lang
                break
    
    # Extract technologies (common ones)
    tech_keywords = [
        "graphql", "sql", "postgresql", "mysql", "mongodb", "redis",
        "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
        "react", "vue", "angular", "node", "python", "java", "csharp",
        "javascript", "typescript", "go", "rust", "c++",
        "splunk", "dynatrace", "grafana", "prometheus", "jenkins",
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "tanzu", "pcf", "openshift", "helm", "istio", "envoy"
    ]
    
    content_lower = content.lower()
    found_techs = [tech for tech in tech_keywords if tech in content_lower]
    metadata["technologies"] = ",".join(found_techs) if found_techs else ""
    
    # Determine memory type based on content
    if any(keyword in content_lower for keyword in ["config", "configuration", "environment", "env"]):
        metadata["memory_type"] = "environment"
    elif any(keyword in content_lower for keyword in ["architecture", "design", "decision", "pattern"]):
        metadata["memory_type"] = "architectural"
    elif any(keyword in content_lower for keyword in ["error", "fix", "troubleshoot", "debug", "restart"]):
        metadata["memory_type"] = "operational"
    elif urls or "dashboard" in content_lower:
        if metadata["memory_type"] == "general":
            metadata["memory_type"] = "environment"
    
    return metadata


@mcp.tool(
    annotations={
        "title": "Save Knowledge",
        "description": "Save a memory or piece of knowledge to the knowledge base",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False
    }
)
async def kb_save(
    content: str, 
    memory_type: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """Save knowledge to the persistent memory store.
    
    Args:
        content: The content/memory to save
        memory_type: Optional type of memory (environment, code_snippet, operational, architectural)
        tags: Optional list of tags for categorization
    """
    if not collection:
        return "Error: Knowledge base not initialized"
    
    try:
        # Generate unique ID
        memory_id = str(uuid.uuid4())
        
        # Extract metadata
        metadata = extract_metadata(content)
        
        # Override memory type if provided
        if memory_type and memory_type in ["environment", "code_snippet", "operational", "architectural"]:
            metadata["memory_type"] = memory_type
        
        # Add tags if provided
        if tags:
            metadata["tags"] = ",".join(tags)
        
        # Store in ChromaDB (embeddings auto-generated)
        collection.add(
            ids=[memory_id],
            documents=[content],
            metadatas=[metadata]
        )
        
        techs = metadata['technologies'].split(',') if metadata['technologies'] else []
        return f"✅ Memory saved successfully!\nID: {memory_id}\nType: {metadata['memory_type']}\nTechnologies: {', '.join(techs) if techs else 'None'}"
        
    except Exception as e:
        return f"❌ Error saving memory: {str(e)}"


@mcp.tool(
    annotations={
        "title": "Search Knowledge",
        "description": "Search the knowledge base for relevant memories",
        "readOnlyHint": True,
        "openWorldHint": False,
        "idempotentHint": True
    }
)
async def kb_search(
    query: str,
    limit: int = 5,
    memory_type: Optional[str] = None,
    include_metadata: bool = True
) -> str:
    """Search for relevant knowledge in the memory store.
    
    Args:
        query: Search query to find relevant memories
        limit: Maximum number of results to return (default: 5)
        memory_type: Filter by memory type (environment, code_snippet, operational, architectural)
        include_metadata: Whether to include metadata in results
    """
    if not collection:
        return "Error: Knowledge base not initialized"
    
    try:
        # Build where clause for filtering
        where_clause = {}
        if memory_type:
            where_clause["memory_type"] = memory_type
        
        # Search in ChromaDB (embeddings auto-generated for query)
        results = collection.query(
            query_texts=[query],
            n_results=min(limit, 10),  # Cap at 10 results
            where=where_clause if where_clause else None,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results["documents"] or not results["documents"][0]:
            return "🔍 No relevant memories found for your query."
        
        # Format results
        formatted_results = []
        documents = results["documents"][0]
        metadatas = results["metadatas"][0] if results["metadatas"] else []
        distances = results["distances"][0] if results["distances"] else []
        
        for i, doc in enumerate(documents):
            result = f"📝 **Memory {i+1}**:\n{doc}"
            
            if include_metadata and i < len(metadatas):
                metadata = metadatas[i]
                result += f"\n\n📊 **Details:**"
                result += f"\n- Type: {metadata.get('memory_type', 'Unknown')}"
                result += f"\n- Created: {metadata.get('created_at', 'Unknown')}"
                
                if metadata.get('technologies'):
                    techs = metadata['technologies'].split(',') if metadata['technologies'] else []
                    if techs:
                        result += f"\n- Technologies: {', '.join(techs)}"
                
                if metadata.get('urls'):
                    urls = metadata['urls'].split(',') if metadata['urls'] else []
                    if urls:
                        result += f"\n- URLs: {', '.join(urls)}"
                
                if i < len(distances):
                    similarity = 1 - distances[i]  # Convert distance to similarity
                    result += f"\n- Relevance: {similarity:.2%}"
                
                # Update access count
                try:
                    current_count = metadata.get('access_count', 0)
                    metadata['access_count'] = current_count + 1
                    metadata['last_accessed'] = datetime.now(timezone.utc).isoformat()
                except Exception:
                    pass  # Ignore metadata update errors
            
            formatted_results.append(result)
        
        response = f"🔍 **Found {len(documents)} relevant memories:**\n\n"
        response += "\n\n" + "="*50 + "\n\n".join(formatted_results)
        
        return response
        
    except Exception as e:
        return f"❌ Error searching memories: {str(e)}"


@mcp.tool(
    annotations={
        "title": "List Knowledge",
        "description": "List all saved memories with optional filtering",
        "readOnlyHint": True,
        "openWorldHint": False,
        "idempotentHint": True
    }
)
async def kb_list(
    memory_type: Optional[str] = None,
    limit: int = 10,
    include_content: bool = False
) -> str:
    """List saved memories in the knowledge base.
    
    Args:
        memory_type: Filter by memory type (environment, code_snippet, operational, architectural)
        limit: Maximum number of entries to return
        include_content: Whether to include full content (default: False, shows summary only)
    """
    if not collection:
        return "Error: Knowledge base not initialized"
    
    try:
        # Build where clause for filtering
        where_clause = {}
        if memory_type:
            where_clause["memory_type"] = memory_type
        
        # Get entries from ChromaDB
        results = collection.get(
            where=where_clause if where_clause else None,
            limit=min(limit, 50),  # Cap at 50 entries
            include=["documents", "metadatas"]
        )
        
        if not results["ids"]:
            filter_msg = f" with type '{memory_type}'" if memory_type else ""
            return f"📝 No memories found{filter_msg}."
        
        # Format results
        formatted_entries = []
        for i, memory_id in enumerate(results["ids"]):
            doc = results["documents"][i] if i < len(results["documents"]) else ""
            metadata = results["metadatas"][i] if i < len(results["metadatas"]) else {}
            
            # Create summary
            if include_content:
                content = doc
            else:
                content = doc[:100] + "..." if len(doc) > 100 else doc
            
            entry = f"**{i+1}.** `{memory_id[:8]}...`\n"
            entry += f"📝 {content}\n"
            entry += f"🏷️ Type: {metadata.get('memory_type', 'Unknown')}"
            
            if metadata.get('technologies'):
                techs = metadata['technologies'].split(',') if metadata['technologies'] else []
                if techs:
                    entry += f" | Tech: {', '.join(techs[:3])}"
            
            entry += f"\n📅 Created: {metadata.get('created_at', 'Unknown')[:10]}"
            
            if metadata.get('access_count', 0) > 0:
                entry += f" | Accessed: {metadata['access_count']} times"
            
            formatted_entries.append(entry)
        
        response = f"📚 **Knowledge Base ({len(results['ids'])} entries"
        if memory_type:
            response += f", type: {memory_type}"
        response += "):**\n\n"
        
        response += "\n\n".join(formatted_entries)
        
        return response
        
    except Exception as e:
        return f"❌ Error listing memories: {str(e)}"


@mcp.tool(
    annotations={
        "title": "Delete Knowledge",
        "description": "Delete a memory from the knowledge base",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False
    }
)
async def kb_delete(memory_id: str) -> str:
    """Delete a memory from the knowledge base.
    
    Args:
        memory_id: The ID of the memory to delete (can be partial ID from kb_list)
    """
    if not collection:
        return "Error: Knowledge base not initialized"
    
    try:
        # Get all IDs to find matches
        all_results = collection.get(include=["documents", "metadatas"])
        
        # Find matching IDs (support partial ID matching)
        matching_ids = []
        for full_id in all_results["ids"]:
            if memory_id.lower() in full_id.lower():
                matching_ids.append(full_id)
        
        if not matching_ids:
            return f"❌ No memory found with ID containing: {memory_id}"
        
        if len(matching_ids) > 1:
            return f"❌ Multiple memories match '{memory_id}'. Please use a more specific ID:\n" + \
                   "\n".join([f"- {mid[:16]}..." for mid in matching_ids[:5]])
        
        # Delete the memory
        memory_to_delete = matching_ids[0]
        collection.delete(ids=[memory_to_delete])
        
        return f"✅ Memory deleted successfully: {memory_to_delete[:16]}..."
        
    except Exception as e:
        return f"❌ Error deleting memory: {str(e)}"


async def main():
    """Initialize and run the MCP server."""
    print("🧠 Initializing Knowledge Base MCP Server...")
    
    try:
        # Initialize database
        init_database()
        
        print("✅ Knowledge Base MCP Server ready!")
        print("📡 Running on stdio transport...")
        
        # Run the server
        await mcp.run(transport="stdio")
        
    except KeyboardInterrupt:
        print("\n👋 Knowledge Base MCP Server shutting down...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())