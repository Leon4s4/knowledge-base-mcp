#!/usr/bin/env python3
"""Streamlit UI for managing the Knowledge Base."""

import asyncio
from pathlib import Path

import streamlit as st

from kb_server import (
    init_database,
    kb_save,
    kb_search,
    kb_list,
    kb_delete,
)

# Initialize the database connection
init_database()


def run_async(coro):
    """Utility to run async functions from Streamlit callbacks."""
    return asyncio.run(coro)


def main() -> None:
    st.title("Knowledge Base MCP")
    st.sidebar.markdown("## Actions")
    
    # Use buttons instead of selectbox
    if st.sidebar.button("Add Memory", use_container_width=True):
        st.session_state.action = "Add Memory"
    if st.sidebar.button("Search", use_container_width=True):
        st.session_state.action = "Search"
    if st.sidebar.button("List Memories", use_container_width=True):
        st.session_state.action = "List Memories"
    if st.sidebar.button("Delete Memory", use_container_width=True):
        st.session_state.action = "Delete Memory"
    
    # Initialize default action if not set
    if "action" not in st.session_state:
        st.session_state.action = "List Memories"
    
    action = st.session_state.action

    if action == "Add Memory":
        st.subheader("Add Memory")
        content = st.text_area("Content")
        memory_type = st.selectbox(
            "Memory Type",
            ["general", "environment", "code_snippet", "operational", "architectural"],
        )
        tags_str = st.text_input("Tags (comma separated)")
        if st.button("Save"):
            tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else None
            result = run_async(
                kb_save(
                    content=content,
                    memory_type=memory_type if memory_type != "general" else None,
                    tags=tags,
                )
            )
            st.success(result)

    elif action == "Search":
        st.subheader("Search")
        query = st.text_input("Query")
        limit = st.number_input("Limit", min_value=1, max_value=20, value=5)
        mtype = st.selectbox(
            "Memory Type Filter",
            ["", "environment", "code_snippet", "operational", "architectural"],
        )
        if st.button("Search"):
            result = run_async(
                kb_search(query=query, limit=int(limit), memory_type=mtype or None)
            )
            st.markdown(result)

    elif action == "List Memories":
        st.subheader("All Memories")
        
        # Filtering options in columns
        col1, col2 = st.columns(2)
        
        with col1:
            mtype = st.selectbox(
                "Filter by Type",
                ["All", "environment", "code_snippet", "operational", "architectural"],
                index=0
            )
        
        with col2:
            page_size = st.selectbox(
                "Items per page",
                [10, 20, 50],
                index=0
            )
        
        # Initialize pagination state
        if "page_number" not in st.session_state:
            st.session_state.page_number = 1
        
        # Get memories data directly from kb_server
        from kb_server import collection
        if collection:
            try:
                # Build where clause for filtering
                where_clause = {}
                if mtype != "All":
                    where_clause["memory_type"] = mtype
                
                # Get entries from ChromaDB
                results = collection.get(
                    where=where_clause if where_clause else None,
                    limit=page_size,
                    include=["documents", "metadatas"]
                )
                
                if results["ids"]:
                    # Display memories as cards
                    st.markdown("---")
                    
                    # Define memory type colors
                    type_colors = {
                        'environment': '🌐',
                        'code_snippet': '💻', 
                        'operational': '⚙️',
                        'architectural': '🏗️',
                        'general': '📝'
                    }
                    
                    # Create cards using Streamlit containers and columns
                    for idx in range(len(results["ids"])):
                        memory_id = results["ids"][idx]
                        doc = results["documents"][idx] if idx < len(results["documents"]) else ""
                        metadata = results["metadatas"][idx] if idx < len(results["metadatas"]) else {}
                        memory_type = metadata.get('memory_type', 'general')
                        
                        # Create card container
                        with st.container():
                            # Card header with type badge and date
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{type_colors.get(memory_type, '📝')} {memory_type.title()}**")
                            with col2:
                                st.caption(metadata.get('created_at', '')[:10])
                            
                            # Card content
                            content_preview = doc[:150] + ('...' if len(doc) > 150 else '')
                            st.write(content_preview)
                            
                            # Card footer with ID and actions
                            col1, col2, col3 = st.columns([3.5, 1, 1])
                            with col1:
                                st.caption(f"ID: {memory_id[:8]}... | Accessed: {metadata.get('access_count', 0)} times")
                            with col2:
                                if st.button("✏️ Edit", key=f"edit_{memory_id}", help="View and edit memory", use_container_width=True):
                                    st.session_state.selected_memory_id = memory_id
                                    st.session_state.action = "Memory Details"
                                    st.rerun()
                            with col3:
                                if st.button("🗑️ Delete", key=f"delete_{memory_id}", help="Delete memory", use_container_width=True):
                                    # Quick delete with confirmation
                                    if f"confirm_delete_{memory_id}" not in st.session_state:
                                        st.session_state[f"confirm_delete_{memory_id}"] = True
                                        st.rerun()
                            
                            # Show delete confirmation if needed
                            if f"confirm_delete_{memory_id}" in st.session_state:
                                st.warning("⚠️ Are you sure you want to delete this memory?")
                                col1, col2, col3 = st.columns([1, 1, 2])
                                with col1:
                                    if st.button("Yes, Delete", key=f"confirm_yes_{memory_id}", type="primary"):
                                        try:
                                            from kb_server import collection
                                            collection.delete(ids=[memory_id])
                                            st.success("Memory deleted!")
                                            del st.session_state[f"confirm_delete_{memory_id}"]
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error deleting memory: {str(e)}")
                                with col2:
                                    if st.button("Cancel", key=f"confirm_no_{memory_id}"):
                                        del st.session_state[f"confirm_delete_{memory_id}"]
                                        st.rerun()
                            
                            # Visual separator between cards
                            st.divider()
                else:
                    st.info("No memories found. Click 'Add Memory' to get started!")
                    
            except Exception as e:
                st.error(f"Error loading memories: {str(e)}")
        else:
            st.error("Database not initialized")
        
        # Pagination controls with proper spacing
        st.markdown("---")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            if st.button("← Previous Page", disabled=st.session_state.page_number <= 1, use_container_width=True):
                st.session_state.page_number -= 1
                st.rerun()
        
        with col2:
            st.markdown(f"<div style='text-align: center; padding: 8px; font-weight: bold;'>Page {st.session_state.page_number}</div>", unsafe_allow_html=True)
        
        with col3:
            if st.button("Next Page →", use_container_width=True):
                st.session_state.page_number += 1
                st.rerun()

    elif action == "Delete Memory":
        st.subheader("Delete Memory")
        mem_id = st.text_input("Memory ID (full or partial)")
        if st.button("Delete"):
            result = run_async(kb_delete(mem_id))
            st.success(result)
    
    elif action == "Memory Details":
        if "selected_memory_id" in st.session_state:
            memory_id = st.session_state.selected_memory_id
            
            # Get memory details
            from kb_server import collection
            if collection:
                try:
                    # Get the specific memory
                    results = collection.get(
                        ids=[memory_id],
                        include=["documents", "metadatas"]
                    )
                    
                    if results["ids"]:
                        doc = results["documents"][0]
                        metadata = results["metadatas"][0]
                        
                        # Header with back button
                        col1, col2 = st.columns([2, 6])
                        with col1:
                            if st.button("← Back to List", use_container_width=True):
                                st.session_state.action = "List Memories"
                                st.rerun()
                        
                        with col2:
                            st.subheader("Memory Details")
                        
                        # Memory info
                        memory_type = metadata.get('memory_type', 'general')
                        type_colors = {
                            'environment': '🌐',
                            'code_snippet': '💻', 
                            'operational': '⚙️',
                            'architectural': '🏗️',
                            'general': '📝'
                        }
                        
                        st.markdown(f"**Type:** {type_colors.get(memory_type, '📝')} {memory_type}")
                        st.markdown(f"**ID:** `{memory_id}`")
                        st.markdown(f"**Created:** {metadata.get('created_at', 'Unknown')}")
                        st.markdown(f"**Last Accessed:** {metadata.get('last_accessed', 'Unknown')}")
                        st.markdown(f"**Access Count:** {metadata.get('access_count', 0)}")
                        
                        if metadata.get('technologies'):
                            techs = metadata['technologies'].split(',')
                            st.markdown(f"**Technologies:** {', '.join(techs)}")
                        
                        if metadata.get('urls'):
                            urls = metadata['urls'].split(',')
                            st.markdown("**URLs:**")
                            for url in urls:
                                st.markdown(f"- {url}")
                        
                        st.markdown("---")
                        
                        # Edit form
                        st.subheader("Edit Memory")
                        
                        new_content = st.text_area("Content", value=doc, height=200)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            new_memory_type = st.selectbox(
                                "Memory Type",
                                ["general", "environment", "code_snippet", "operational", "architectural"],
                                index=["general", "environment", "code_snippet", "operational", "architectural"].index(memory_type) if memory_type in ["general", "environment", "code_snippet", "operational", "architectural"] else 0
                            )
                        
                        with col2:
                            tags_str = st.text_input("Tags (comma separated)", value=metadata.get('tags', ''))
                        
                        # Action buttons
                        st.markdown("---")
                        st.markdown("### Actions")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("💾 Update Memory", use_container_width=True):
                                # Delete old memory and create new one
                                try:
                                    # Delete old
                                    collection.delete(ids=[memory_id])
                                    
                                    # Create new with same ID but updated content
                                    from kb_server import extract_metadata
                                    new_metadata = extract_metadata(new_content)
                                    new_metadata["memory_type"] = new_memory_type
                                    if tags_str:
                                        new_metadata["tags"] = tags_str
                                    
                                    # Preserve some original metadata
                                    new_metadata["created_at"] = metadata.get("created_at")
                                    new_metadata["access_count"] = metadata.get("access_count", 0)
                                    
                                    collection.add(
                                        ids=[memory_id],
                                        documents=[new_content],
                                        metadatas=[new_metadata]
                                    )
                                    
                                    st.success("Memory updated successfully!")
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"Error updating memory: {str(e)}")
                        
                        with col2:
                            if st.button("🗑️ Delete Memory", use_container_width=True):
                                try:
                                    collection.delete(ids=[memory_id])
                                    st.success("Memory deleted successfully!")
                                    st.session_state.action = "List Memories"
                                    if "selected_memory_id" in st.session_state:
                                        del st.session_state.selected_memory_id
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting memory: {str(e)}")
                        
                        with col3:
                            if st.button("📋 Copy ID", use_container_width=True):
                                st.code(memory_id)
                                st.info("Memory ID copied above!")
                    
                    else:
                        st.error("Memory not found")
                        st.session_state.action = "List Memories"
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error loading memory: {str(e)}")
            else:
                st.error("Database not initialized")
        else:
            st.error("No memory selected")
            st.session_state.action = "List Memories"
            st.rerun()


if __name__ == "__main__":
    main()
