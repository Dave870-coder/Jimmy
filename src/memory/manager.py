"""Memory system for storing and retrieving user memories."""

import json
import uuid
from typing import Optional

from src.config import get_settings

settings = get_settings()


class MemoryManager:
    """Manager for user memories."""

    def __init__(self):
        """Initialize memory manager."""
        self.memories: dict = {}
        self.embeddings: dict = {}

    async def store_memory(
        self,
        user_id: str,
        title: str,
        content: str,
        memory_type: str,
        category: Optional[str] = None,
        importance: int = 5,
    ) -> str:
        """Store a memory for a user."""
        memory_id = str(uuid.uuid4())
        
        memory = {
            "id": memory_id,
            "user_id": user_id,
            "title": title,
            "content": content,
            "type": memory_type,
            "category": category,
            "importance": importance,
            "created_at": str(__import__("datetime").datetime.utcnow()),
        }
        
        self.memories[memory_id] = memory
        return memory_id

    async def retrieve_memory(self, memory_id: str) -> Optional[dict]:
        """Retrieve a memory by ID."""
        return self.memories.get(memory_id)

    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 10,
    ) -> list[dict]:
        """Search memories using semantic search."""
        # TODO: Implement vector search using ChromaDB
        results = []
        for memory in self.memories.values():
            if memory["user_id"] == user_id:
                if query.lower() in memory["content"].lower():
                    results.append(memory)
        
        return results[:limit]

    async def update_memory(
        self,
        memory_id: str,
        **kwargs
    ) -> Optional[dict]:
        """Update a memory."""
        if memory_id not in self.memories:
            return None
        
        memory = self.memories[memory_id]
        for key, value in kwargs.items():
            if key in memory:
                memory[key] = value
        
        return memory

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        if memory_id in self.memories:
            del self.memories[memory_id]
            return True
        return False

    async def get_user_memories(self, user_id: str, limit: int = 100) -> list[dict]:
        """Get all memories for a user."""
        return [
            m for m in self.memories.values()
            if m["user_id"] == user_id
        ][:limit]


# Global memory manager instance
memory_manager = MemoryManager()
