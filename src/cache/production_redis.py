"""
Production-scale caching configuration for 7 million users.
Handles high-throughput scenarios with Redis.
"""

import json
import asyncio
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
import logging
from redis.asyncio import Redis, ConnectionPool, RedisCluster
from redis.exceptions import RedisError, ConnectionError
from functools import wraps
import time

logger = logging.getLogger(__name__)

class CacheConfig:
    """Redis cache configuration for enterprise scale."""
    
    # Connection pool settings
    POOL_SIZE = 50
    MAX_CONNECTIONS = 200
    SOCKET_KEEPALIVE = True
    SOCKET_KEEPALIVE_OPTIONS = {1: (1, 10)}  # TCP_KEEPIDLE=10
    
    # Timeout settings
    SOCKET_CONNECT_TIMEOUT = 5
    SOCKET_TIMEOUT = 5
    
    # Retry settings
    RETRY_ON_TIMEOUT = True
    MAX_RETRIES = 3
    RETRY_DELAY = 0.1
    
    # TTL (Time To Live) settings
    USER_SESSION_TTL = 86400  # 24 hours
    RATE_LIMIT_TTL = 3600    # 1 hour
    AI_RESPONSE_TTL = 3600   # 1 hour
    GLOBAL_CACHE_TTL = 86400 # 24 hours
    
    # Cache keys format
    USER_SESSION_KEY = "session:{user_id}"
    RATE_LIMIT_KEY = "rate_limit:{user_id}:{metric}"
    AI_CACHE_KEY = "ai_cache:{hash}"
    CONVERSATION_KEY = "conv:{conversation_id}"

class RedisManager:
    """Manages Redis connections for production scale."""
    
    def __init__(self, redis_url: str, use_cluster: bool = False):
        """Initialize Redis manager."""
        self.redis_url = redis_url
        self.use_cluster = use_cluster
        self.redis: Optional[Redis] = None
        self.pool: Optional[ConnectionPool] = None
        self.is_connected = False
    
    async def initialize(self):
        """Initialize Redis connection pool."""
        try:
            if self.use_cluster:
                # Redis Cluster for massive scale
                self.redis = RedisCluster.from_url(
                    self.redis_url,
                    max_connections=CacheConfig.MAX_CONNECTIONS,
                    socket_keepalive=CacheConfig.SOCKET_KEEPALIVE,
                    socket_connect_timeout=CacheConfig.SOCKET_CONNECT_TIMEOUT,
                )
            else:
                # Standard Redis connection pool
                self.pool = ConnectionPool.from_url(
                    self.redis_url,
                    max_connections=CacheConfig.MAX_CONNECTIONS,
                    socket_keepalive=CacheConfig.SOCKET_KEEPALIVE,
                    socket_connect_timeout=CacheConfig.SOCKET_CONNECT_TIMEOUT,
                    socket_timeout=CacheConfig.SOCKET_TIMEOUT,
                    decode_responses=True,
                )
                self.redis = Redis(connection_pool=self.pool)
            
            # Test connection
            await self.redis.ping()
            self.is_connected = True
            logger.info("✅ Redis connected successfully")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.is_connected = False
            raise
    
    async def close(self):
        """Close Redis connection pool."""
        if self.redis:
            await self.redis.close()
            if self.pool:
                await self.pool.disconnect()
            self.is_connected = False
            logger.info("Redis connection closed")
    
    async def _retry_operation(self, operation, *args, **kwargs):
        """Retry operation with exponential backoff."""
        last_error = None
        for attempt in range(CacheConfig.MAX_RETRIES):
            try:
                return await operation(*args, **kwargs)
            except (ConnectionError, TimeoutError) as e:
                last_error = e
                if attempt < CacheConfig.MAX_RETRIES - 1:
                    delay = CacheConfig.RETRY_DELAY * (2 ** attempt)
                    await asyncio.sleep(delay)
                continue
        
        raise last_error or RedisError("Max retries exceeded")
    
    # User Session Management
    async def set_user_session(self, user_id: int, session_data: Dict[str, Any]):
        """Cache user session."""
        key = CacheConfig.USER_SESSION_KEY.format(user_id=user_id)
        value = json.dumps(session_data)
        
        await self._retry_operation(
            self.redis.setex,
            key,
            CacheConfig.USER_SESSION_TTL,
            value
        )
    
    async def get_user_session(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve user session."""
        key = CacheConfig.USER_SESSION_KEY.format(user_id=user_id)
        
        data = await self._retry_operation(self.redis.get, key)
        return json.loads(data) if data else None
    
    async def delete_user_session(self, user_id: int):
        """Delete user session."""
        key = CacheConfig.USER_SESSION_KEY.format(user_id=user_id)
        await self._retry_operation(self.redis.delete, key)
    
    # Rate Limiting
    async def check_rate_limit(self, user_id: int, metric: str, limit: int, window: int) -> bool:
        """Check if user exceeded rate limit."""
        key = CacheConfig.RATE_LIMIT_KEY.format(user_id=user_id, metric=metric)
        
        count = await self._retry_operation(self.redis.incr, key)
        
        if count == 1:
            await self._retry_operation(self.redis.expire, key, window)
        
        return count <= limit
    
    async def get_rate_limit_remaining(self, user_id: int, metric: str, limit: int) -> int:
        """Get remaining requests for user."""
        key = CacheConfig.RATE_LIMIT_KEY.format(user_id=user_id, metric=metric)
        
        count = await self._retry_operation(self.redis.get, key)
        current = int(count) if count else 0
        
        return max(0, limit - current)
    
    # AI Response Caching
    async def cache_ai_response(self, query_hash: str, response: Dict[str, Any]):
        """Cache AI response."""
        key = CacheConfig.AI_CACHE_KEY.format(hash=query_hash)
        value = json.dumps(response)
        
        await self._retry_operation(
            self.redis.setex,
            key,
            CacheConfig.AI_RESPONSE_TTL,
            value
        )
    
    async def get_cached_ai_response(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached AI response."""
        key = CacheConfig.AI_CACHE_KEY.format(hash=query_hash)
        
        data = await self._retry_operation(self.redis.get, key)
        return json.loads(data) if data else None
    
    # Conversation Management
    async def add_to_conversation(self, conversation_id: str, message: Dict[str, Any]):
        """Add message to conversation cache."""
        key = CacheConfig.CONVERSATION_KEY.format(conversation_id=conversation_id)
        
        await self._retry_operation(
            self.redis.rpush,
            key,
            json.dumps(message)
        )
        
        # Keep conversation cache for 24 hours
        await self._retry_operation(
            self.redis.expire,
            key,
            CacheConfig.USER_SESSION_TTL
        )
    
    async def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get entire conversation from cache."""
        key = CacheConfig.CONVERSATION_KEY.format(conversation_id=conversation_id)
        
        messages = await self._retry_operation(self.redis.lrange, key, 0, -1)
        return [json.loads(msg) for msg in messages] if messages else []
    
    # Metrics & Monitoring
    async def increment_metric(self, metric_name: str, value: int = 1):
        """Increment metric counter."""
        key = f"metric:{metric_name}"
        
        await self._retry_operation(self.redis.incrby, key, value)
        await self._retry_operation(self.redis.expire, key, 86400)  # 24h TTL
    
    async def get_metric(self, metric_name: str) -> int:
        """Get metric value."""
        key = f"metric:{metric_name}"
        
        value = await self._retry_operation(self.redis.get, key)
        return int(value) if value else 0
    
    # Utility Methods
    async def health_check(self) -> bool:
        """Check Redis health."""
        try:
            await self._retry_operation(self.redis.ping)
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    async def clear_user_data(self, user_id: int):
        """Clear all cached data for a user."""
        pattern = f"*{user_id}*"
        keys = await self._retry_operation(self.redis.keys, pattern)
        
        if keys:
            await self._retry_operation(self.redis.delete, *keys)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis statistics."""
        try:
            info = await self._retry_operation(self.redis.info)
            return {
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory_human"),
                "connected": True,
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}

# Decorator for caching function results
def cache_result(ttl: int = 3600):
    """Decorator to cache function results in Redis."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key from function name and args
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            try:
                cached = await redis_manager.get_cached_ai_response(cache_key)
                if cached:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            try:
                await redis_manager.cache_ai_response(cache_key, result)
            except Exception as e:
                logger.warning(f"Cache write failed: {e}")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

# Global cache manager instance
redis_manager: Optional[RedisManager] = None

async def init_cache(redis_url: str):
    """Initialize global cache manager."""
    global redis_manager
    redis_manager = RedisManager(redis_url)
    await redis_manager.initialize()

async def close_cache():
    """Close cache manager."""
    global redis_manager
    if redis_manager:
        await redis_manager.close()
