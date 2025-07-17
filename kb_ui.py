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
    action = st.sidebar.selectbox(
        "Choose action",
        ["Add Memory", "Search", "List Memories", "Delete Memory"],
    )

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
        st.subheader("List Memories")
        mtype = st.selectbox(
            "Memory Type",
            ["", "environment", "code_snippet", "operational", "architectural"],
        )
        limit = st.number_input("Limit", min_value=1, max_value=50, value=10)
        include_content = st.checkbox("Include full content", value=False)
        if st.button("List"):
            result = run_async(
                kb_list(
                    memory_type=mtype or None,
                    limit=int(limit),
                    include_content=include_content,
                )
            )
            st.markdown(result)

    elif action == "Delete Memory":
        st.subheader("Delete Memory")
        mem_id = st.text_input("Memory ID (full or partial)")
        if st.button("Delete"):
            result = run_async(kb_delete(mem_id))
            st.write(result)


if __name__ == "__main__":
    main()
