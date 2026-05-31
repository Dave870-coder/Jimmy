"""
Optimized queries for large-scale database (700M+ records).
Designed for maximum performance with indexed lookups and efficient joins.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, text, and_, or_
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class LargeScaleQueries:
    """Optimized query operations for 700M+ records."""
    
    @staticmethod
    async def get_recent_messages(
        user_id: int,
        limit: int = 100,
        session: Session = None
    ) -> List[Dict]:
        """
        Get recent messages for a user (fast with index on created_at).
        
        Uses indexed column for O(log n) lookup.
        """
        try:
            from src.database.models import Message
            
            query = select(Message).where(
                and_(
                    Message.user_id == user_id,
                    Message.is_deleted == False
                )
            ).order_by(
                Message.created_at.desc()
            ).limit(limit)
            
            result = await session.execute(query)
            messages = result.scalars().all()
            
            logger.debug(f"Retrieved {len(messages)} recent messages for user {user_id}")
            return [m.to_dict() for m in messages]
        
        except Exception as e:
            logger.error(f"Error fetching recent messages: {e}")
            return []
    
    @staticmethod
    async def get_conversation_messages(
        conversation_id: int,
        offset: int = 0,
        limit: int = 50,
        session: Session = None
    ) -> List[Dict]:
        """
        Get messages in a conversation with pagination (uses partitioned table).
        
        Partitioning automatically filters to relevant monthly tables.
        """
        try:
            from src.database.models import Message
            
            query = select(Message).where(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.is_deleted == False
                )
            ).order_by(
                Message.created_at.desc()
            ).offset(offset).limit(limit)
            
            result = await session.execute(query)
            messages = result.scalars().all()
            
            logger.debug(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
            return [m.to_dict() for m in messages]
        
        except Exception as e:
            logger.error(f"Error fetching conversation messages: {e}")
            return []
    
    @staticmethod
    async def get_messages_by_date_range(
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: Session = None
    ) -> List[Dict]:
        """
        Query messages in date range (uses table partitioning for efficiency).
        
        Partition pruning automatically reads only needed monthly partitions.
        """
        try:
            from src.database.models import Message
            
            query = select(Message).where(
                and_(
                    Message.user_id == user_id,
                    Message.created_at >= start_date,
                    Message.created_at <= end_date,
                    Message.is_deleted == False
                )
            ).order_by(Message.created_at.desc())
            
            result = await session.execute(query)
            messages = result.scalars().all()
            
            logger.debug(f"Retrieved {len(messages)} messages in date range for user {user_id}")
            return [m.to_dict() for m in messages]
        
        except Exception as e:
            logger.error(f"Error fetching messages by date range: {e}")
            return []
    
    @staticmethod
    async def search_messages_by_content(
        conversation_id: int,
        search_text: str,
        limit: int = 20,
        session: Session = None
    ) -> List[Dict]:
        """
        Full-text search in messages (uses PostgreSQL GIN index).
        
        Fast for substring matching on indexed content.
        """
        try:
            from src.database.models import Message
            
            # Use ILIKE for case-insensitive substring search
            search_pattern = f"%{search_text}%"
            
            query = select(Message).where(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.content.ilike(search_pattern),
                    Message.is_deleted == False
                )
            ).order_by(
                Message.created_at.desc()
            ).limit(limit)
            
            result = await session.execute(query)
            messages = result.scalars().all()
            
            logger.debug(f"Found {len(messages)} messages matching '{search_text}'")
            return [m.to_dict() for m in messages]
        
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return []
    
    @staticmethod
    async def get_conversation_summary(
        conversation_id: int,
        session: Session = None
    ) -> Optional[Dict]:
        """
        Get conversation summary (uses materialized view for fast access).
        
        Materialized view pre-aggregates counts for instant response.
        """
        try:
            # Use raw SQL for materialized view
            query = text("""
            SELECT 
                id,
                user_id,
                title,
                message_count,
                user_messages,
                assistant_messages,
                last_message_at,
                total_tokens_used
            FROM conversation_stats
            WHERE id = :conversation_id
            """)
            
            result = await session.execute(
                query,
                {"conversation_id": conversation_id}
            )
            
            row = result.fetchone()
            if row:
                return {
                    "id": row[0],
                    "user_id": row[1],
                    "title": row[2],
                    "message_count": row[3],
                    "user_messages": row[4],
                    "assistant_messages": row[5],
                    "last_message_at": row[6],
                    "total_tokens_used": row[7]
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error fetching conversation summary: {e}")
            return None
    
    @staticmethod
    async def get_user_stats(
        user_id: int,
        session: Session = None
    ) -> Optional[Dict]:
        """
        Get user statistics (uses materialized view).
        
        Fast aggregation queries from pre-computed view.
        """
        try:
            query = text("""
            SELECT 
                id,
                username,
                conversation_count,
                message_count,
                last_message_at,
                total_tokens_used
            FROM user_stats
            WHERE id = :user_id
            """)
            
            result = await session.execute(
                query,
                {"user_id": user_id}
            )
            
            row = result.fetchone()
            if row:
                return {
                    "user_id": row[0],
                    "username": row[1],
                    "conversation_count": row[2],
                    "message_count": row[3],
                    "last_message_at": row[4],
                    "total_tokens_used": row[5]
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error fetching user stats: {e}")
            return None
    
    @staticmethod
    async def get_user_memory(
        user_id: int,
        key: Optional[str] = None,
        session: Session = None
    ) -> Dict[str, Any]:
        """
        Get user memory/preferences (fast key-value lookup).
        
        O(log n) lookup using indexed key column.
        """
        try:
            from src.database.models import Memory
            
            if key:
                query = select(Memory).where(
                    and_(
                        Memory.user_id == user_id,
                        Memory.key == key
                    )
                )
                result = await session.execute(query)
                memory = result.scalars().first()
                return {memory.key: memory.value} if memory else {}
            
            else:
                query = select(Memory).where(
                    Memory.user_id == user_id
                )
                result = await session.execute(query)
                memories = result.scalars().all()
                return {m.key: m.value for m in memories}
        
        except Exception as e:
            logger.error(f"Error fetching user memory: {e}")
            return {}
    
    @staticmethod
    async def bulk_insert_messages(
        messages: List[Dict],
        session: Session = None
    ) -> int:
        """
        Efficient bulk insert for large number of messages.
        
        Optimized for high-throughput inserts.
        """
        try:
            from src.database.models import Message
            
            inserted_count = 0
            
            # Batch inserts in chunks
            batch_size = 1000
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i+batch_size]
                
                for msg in batch:
                    session.add(Message(**msg))
                
                session.commit()
                inserted_count += len(batch)
            
            logger.info(f"Bulk inserted {inserted_count} messages")
            return inserted_count
        
        except Exception as e:
            logger.error(f"Error in bulk insert: {e}")
            session.rollback()
            return 0
    
    @staticmethod
    async def get_hot_data_cache(
        cache_key: str,
        session: Session = None
    ) -> Optional[Dict]:
        """
        Get frequently accessed data from cache (fast JSONB lookup).
        
        Used for hot data that changes infrequently.
        """
        try:
            from src.database.models import Cache
            
            query = select(Cache).where(
                and_(
                    Cache.cache_key == cache_key,
                    Cache.expires_at > datetime.now()
                )
            )
            
            result = await session.execute(query)
            cache = result.scalars().first()
            
            return cache.cache_value if cache else None
        
        except Exception as e:
            logger.error(f"Error fetching cache: {e}")
            return None
    
    @staticmethod
    async def set_hot_data_cache(
        cache_key: str,
        cache_value: Dict,
        ttl_hours: int = 24,
        session: Session = None
    ) -> bool:
        """
        Set cache value for frequently accessed data.
        
        Auto-expires after TTL.
        """
        try:
            from src.database.models import Cache
            
            # Remove old entry if exists
            await session.execute(
                select(Cache).where(Cache.cache_key == cache_key).delete()
            )
            
            # Insert new entry
            cache = Cache(
                cache_key=cache_key,
                cache_value=cache_value,
                ttl=timedelta(hours=ttl_hours),
                expires_at=datetime.now() + timedelta(hours=ttl_hours)
            )
            session.add(cache)
            session.commit()
            
            return True
        
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    @staticmethod
    async def cleanup_old_data(
        days_old: int = 365,
        session: Session = None
    ) -> int:
        """
        Archive or delete old messages (for data retention policies).
        
        Soft-delete by marking is_deleted=true.
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            query = text("""
            UPDATE messages 
            SET is_deleted = true, deleted_at = CURRENT_TIMESTAMP
            WHERE created_at < :cutoff_date AND is_deleted = false
            """)
            
            result = await session.execute(
                query,
                {"cutoff_date": cutoff_date}
            )
            session.commit()
            
            deleted_count = result.rowcount
            logger.info(f"Marked {deleted_count} old messages as deleted")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0
    
    @staticmethod
    async def get_analytics(
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        session: Session = None
    ) -> List[Dict]:
        """
        Get analytics for a user (uses partitioned analytics table).
        
        Partition pruning reads only relevant monthly partitions.
        """
        try:
            from src.database.models import Analytics
            
            query = select(Analytics).where(
                and_(
                    Analytics.user_id == user_id,
                    Analytics.created_at >= start_date,
                    Analytics.created_at <= end_date
                )
            )
            
            result = await session.execute(query)
            analytics = result.scalars().all()
            
            return [a.to_dict() for a in analytics]
        
        except Exception as e:
            logger.error(f"Error fetching analytics: {e}")
            return []


# Export main query class
__all__ = ['LargeScaleQueries']
