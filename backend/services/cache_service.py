"""
Redis Cache Service for RealDiag
Provides distributed caching with fallback to in-memory cache
"""

import os
import logging
import pickle
import json
from typing import Any, Optional
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)

# Try to import Redis
try:
    import redis
    from redis import Redis, ConnectionError as RedisConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("Redis not available - using in-memory cache fallback")
    REDIS_AVAILABLE = False
    Redis = None
    RedisConnectionError = Exception

# In-memory cache fallback
_memory_cache = {}
_memory_cache_ttl = {}


class CacheService:
    """
    Distributed cache service with Redis backend and in-memory fallback.
    Automatically serializes/deserializes Python objects.
    """
    
    def __init__(self):
        self.redis_client = None
        self.use_redis = False
        
        if REDIS_AVAILABLE:
            redis_url = os.getenv("REDIS_URL") or os.getenv("REDIS_TLS_URL")
            
            if redis_url:
                try:
                    # Configure Redis client
                    self.redis_client = redis.from_url(
                        redis_url,
                        decode_responses=False,  # We'll handle serialization
                        socket_connect_timeout=5,
                        socket_timeout=5,
                        retry_on_timeout=True,
                        health_check_interval=30
                    )
                    
                    # Test connection
                    self.redis_client.ping()
                    self.use_redis = True
                    logger.info("✅ Redis cache connected successfully")
                    
                except (RedisConnectionError, Exception) as e:
                    logger.warning(f"⚠️  Redis connection failed: {e}. Using in-memory cache.")
                    self.redis_client = None
                    self.use_redis = False
            else:
                logger.info("ℹ️  Redis URL not configured. Using in-memory cache.")
        
        if not self.use_redis:
            logger.info("📦 Using in-memory cache (not distributed)")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache. Returns None if not found or expired."""
        try:
            if self.use_redis and self.redis_client:
                # Get from Redis
                value = self.redis_client.get(key)
                if value:
                    return pickle.loads(value)
                return None
            else:
                # Get from memory cache
                import time
                if key in _memory_cache:
                    # Check TTL
                    if key in _memory_cache_ttl:
                        if time.time() > _memory_cache_ttl[key]:
                            # Expired
                            del _memory_cache[key]
                            del _memory_cache_ttl[key]
                            return None
                    return _memory_cache[key]
                return None
                
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache with TTL (time to live) in seconds.
        Default TTL: 1 hour (3600 seconds)
        """
        try:
            if self.use_redis and self.redis_client:
                # Set in Redis with expiration
                serialized = pickle.dumps(value)
                self.redis_client.setex(key, ttl, serialized)
                return True
            else:
                # Set in memory cache
                import time
                _memory_cache[key] = value
                _memory_cache_ttl[key] = time.time() + ttl
                return True
                
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.delete(key)
                return True
            else:
                if key in _memory_cache:
                    del _memory_cache[key]
                if key in _memory_cache_ttl:
                    del _memory_cache_ttl[key]
                return True
                
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern. Returns number of keys deleted."""
        try:
            if self.use_redis and self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # Clear from memory cache
                keys_to_delete = [k for k in _memory_cache.keys() if pattern.replace('*', '') in k]
                for key in keys_to_delete:
                    del _memory_cache[key]
                    if key in _memory_cache_ttl:
                        del _memory_cache_ttl[key]
                return len(keys_to_delete)
                
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        if self.use_redis and self.redis_client:
            try:
                info = self.redis_client.info()
                return {
                    "type": "redis",
                    "connected": True,
                    "keys": self.redis_client.dbsize(),
                    "memory_used": info.get("used_memory_human", "unknown"),
                    "hits": info.get("keyspace_hits", 0),
                    "misses": info.get("keyspace_misses", 0)
                }
            except Exception as e:
                return {"type": "redis", "connected": False, "error": str(e)}
        else:
            return {
                "type": "memory",
                "connected": True,
                "keys": len(_memory_cache),
                "memory_used": "unknown"
            }


# Global cache instance
cache = CacheService()


def cache_response(key_prefix: str, ttl: int = 3600):
    """
    Decorator to cache function responses.
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds (default 1 hour)
    
    Example:
        @cache_response("symptom_search", ttl=1800)
        async def search_symptoms(symptoms, age, sex):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key from arguments
            cache_key_data = f"{key_prefix}:{str(args)}:{str(kwargs)}"
            cache_key = hashlib.md5(cache_key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT for {key_prefix}")
                return cached_value
            
            # Cache miss - call function
            logger.debug(f"Cache MISS for {key_prefix}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key from arguments
            cache_key_data = f"{key_prefix}:{str(args)}:{str(kwargs)}"
            cache_key = hashlib.md5(cache_key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT for {key_prefix}")
                return cached_value
            
            # Cache miss - call function
            logger.debug(f"Cache MISS for {key_prefix}")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            
            return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
