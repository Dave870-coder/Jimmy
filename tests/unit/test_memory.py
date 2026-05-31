"""Unit tests for memory management."""

import pytest
from src.memory.manager import memory_manager


@pytest.mark.asyncio
async def test_store_memory():
    """Test storing a memory."""
    user_id = "test_user_id"
    memory_id = await memory_manager.store_memory(
        user_id=user_id,
        title="Test Memory",
        content="This is a test memory",
        memory_type="fact",
        importance=5,
    )
    
    assert memory_id is not None
    assert len(memory_id) > 0


@pytest.mark.asyncio
async def test_retrieve_memory():
    """Test retrieving a memory."""
    user_id = "test_user_id"
    memory_id = await memory_manager.store_memory(
        user_id=user_id,
        title="Test Memory",
        content="This is a test memory",
        memory_type="fact",
        importance=5,
    )
    
    memory = await memory_manager.retrieve_memory(memory_id)
    assert memory is not None
    assert memory["title"] == "Test Memory"


@pytest.mark.asyncio
async def test_search_memories():
    """Test searching memories."""
    user_id = "test_user_id"
    
    # Store test memories
    await memory_manager.store_memory(
        user_id=user_id,
        title="Python Memory",
        content="Python is a programming language",
        memory_type="fact",
    )
    
    # Search
    results = await memory_manager.search_memories(user_id, "python")
    assert len(results) > 0
