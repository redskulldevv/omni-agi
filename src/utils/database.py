from typing import Any, Dict, List, Optional
import redis
from contextlib import contextmanager

class Database:
    """Database operations wrapper supporting both Redis and future expansions."""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        
    def set(self, key: str, value: Any, expire: Optional[int] = None):
        """Set a key-value pair with optional expiration."""
        self.redis.set(key, value, ex=expire)
        
    def get(self, key: str) -> Optional[str]:
        """Get value for a key."""
        return self.redis.get(key)
        
    def delete(self, key: str):
        """Delete a key."""
        self.redis.delete(key)
        
    @contextmanager
    def lock(self, lock_name: str, expire: int = 60):
        """Distributed lock implementation."""
        lock = self.redis.lock(f"lock:{lock_name}", timeout=expire)
        try:
            lock.acquire()
            yield
        finally:
            lock.release()
            
    def store_memory(self, key: str, memory: Dict[str, Any], ttl: Optional[int] = None):
        """Store agent memory with optional TTL."""
        self.redis.hmset(f"memory:{key}", memory)
        if ttl:
            self.redis.expire(f"memory:{key}", ttl)
            
    def get_memory(self, key: str) -> Dict[str, Any]:
        """Retrieve agent memory."""
        return self.redis.hgetall(f"memory:{key}")
