"""Vector database utilities using ChromaDB."""

import json
import uuid
from typing import Optional

try:
    import chromadb
except ImportError:
    chromadb = None

from src.config import get_settings

settings = get_settings()


class VectorDatabase:
    """Vector database manager using ChromaDB."""

    def __init__(self):
        """Initialize vector database."""
        if chromadb is None:
            raise ImportError("chromadb is not installed")
        
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name
        )

    async def add_embedding(
        self,
        user_id: str,
        content: str,
        embedding_type: str = "memory",
        reference_id: Optional[str] = None,
    ) -> str:
        """Add content to vector database."""
        embedding_id = str(uuid.uuid4())
        
        self.collection.add(
            ids=[embedding_id],
            documents=[content],
            metadatas=[{
                "user_id": user_id,
                "type": embedding_type,
                "reference_id": reference_id or embedding_id,
            }]
        )
        
        return embedding_id

    async def search(
        self,
        user_id: str,
        query: str,
        embedding_type: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search for similar content."""
        where_filter = {"user_id": {"$eq": user_id}}
        
        if embedding_type:
            where_filter["type"] = {"$eq": embedding_type}
        
        results = self.collection.query(
            query_texts=[query],
            where=where_filter,
            n_results=limit,
        )
        
        documents = []
        if results and results["documents"] and results["documents"][0]:
            for doc, distance in zip(results["documents"][0], results["distances"][0]):
                documents.append({
                    "content": doc,
                    "score": 1 - distance,  # Convert distance to similarity
                })
        
        return documents

    async def delete_embedding(self, embedding_id: str) -> bool:
        """Delete an embedding."""
        try:
            self.collection.delete(ids=[embedding_id])
            return True
        except Exception:
            return False

    async def update_embedding(
        self,
        embedding_id: str,
        content: str,
        metadata: dict,
    ) -> bool:
        """Update an embedding."""
        try:
            self.collection.update(
                ids=[embedding_id],
                documents=[content],
                metadatas=[metadata],
            )
            return True
        except Exception:
            return False


# Global vector database instance
vector_db: Optional[VectorDatabase] = None


async def get_vector_db() -> Optional[VectorDatabase]:
    """Get vector database instance."""
    global vector_db
    if vector_db is None:
        try:
            vector_db = VectorDatabase()
        except ImportError:
            return None
    return vector_db
