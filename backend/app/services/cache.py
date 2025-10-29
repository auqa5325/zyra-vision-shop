"""
Cache service for recommendations
"""

import time
from typing import Dict, Any, Optional, Tuple
from uuid import UUID


class RecommendationCache:
    """Simple in-memory cache for recommendations with TTL"""
    
    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.ttl_seconds = ttl_seconds
    
    def _make_key(self, user_id: Optional[UUID], query: Optional[str], alpha: float, k: int) -> str:
        """Create cache key from parameters"""
        user_str = str(user_id) if user_id else "anonymous"
        query_str = query or "none"
        return f"rec:{user_str}:{query_str}:{alpha}:{k}"
    
    def get(self, user_id: Optional[UUID], query: Optional[str], alpha: float, k: int) -> Optional[Any]:
        """Get cached recommendation"""
        key = self._make_key(user_id, query, alpha, k)
        
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                return data
            else:
                # Expired, remove from cache
                del self.cache[key]
        
        return None
    
    def set(self, user_id: Optional[UUID], query: Optional[str], alpha: float, k: int, data: Any) -> None:
        """Cache recommendation"""
        key = self._make_key(user_id, query, alpha, k)
        self.cache[key] = (data, time.time())
    
    def clear(self) -> None:
        """Clear all cached data"""
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed items"""
        current_time = time.time()
        expired_keys = []
        
        for key, (_, timestamp) in self.cache.items():
            if current_time - timestamp >= self.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)


# Global cache instance
recommendation_cache = RecommendationCache(ttl_seconds=300)  # 5 minutes

