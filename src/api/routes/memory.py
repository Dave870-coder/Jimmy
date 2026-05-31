"""API routes for memory management."""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from src.memory.manager import memory_manager
from src.schemas import MemoryCreate, MemoryResponse, MemoryUpdate

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


@router.post("/store", response_model=MemoryResponse)
async def store_memory(user_id: str, memory: MemoryCreate):
    """Store a memory for a user."""
    memory_id = await memory_manager.store_memory(
        user_id=user_id,
        title=memory.title,
        content=memory.content,
        memory_type=memory.memory_type,
        category=memory.category,
        importance=memory.importance,
    )
    
    stored = await memory_manager.retrieve_memory(memory_id)
    
    return MemoryResponse(
        id=memory_id,
        user_id=user_id,
        title=memory.title,
        content=memory.content,
        memory_type=memory.memory_type,
        importance=memory.importance,
        created_at=datetime.utcnow(),
    )


@router.get("/{user_id}", response_model=list[MemoryResponse])
async def get_user_memories(user_id: str, limit: int = 100):
    """Get all memories for a user."""
    memories = await memory_manager.get_user_memories(user_id, limit)
    
    return [
        MemoryResponse(
            id=m["id"],
            user_id=m["user_id"],
            title=m["title"],
            content=m["content"],
            memory_type=m["type"],
            importance=m["importance"],
            created_at=datetime.fromisoformat(m["created_at"]),
        )
        for m in memories
    ]


@router.post("/search", response_model=list[MemoryResponse])
async def search_memories(user_id: str, query: str, limit: int = 10):
    """Search memories using semantic search."""
    results = await memory_manager.search_memories(user_id, query, limit)
    
    return [
        MemoryResponse(
            id=m["id"],
            user_id=m["user_id"],
            title=m["title"],
            content=m["content"],
            memory_type=m["type"],
            importance=m["importance"],
            created_at=datetime.fromisoformat(m["created_at"]),
        )
        for m in results
    ]


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(memory_id: str, memory: MemoryUpdate):
    """Update a memory."""
    update_data = memory.model_dump(exclude_unset=True)
    updated = await memory_manager.update_memory(memory_id, **update_data)
    
    if not updated:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    return MemoryResponse(
        id=updated["id"],
        user_id=updated["user_id"],
        title=updated["title"],
        content=updated["content"],
        memory_type=updated["type"],
        importance=updated["importance"],
        created_at=datetime.fromisoformat(updated["created_at"]),
    )


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(memory_id: str):
    """Delete a memory."""
    success = await memory_manager.delete_memory(memory_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
