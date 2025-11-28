"""
Short-Term Memory

Session-based memory for temporary context.
"""
from typing import Dict, Any, List, Optional
import time
import logging

logger = logging.getLogger(__name__)


class ShortTermMemory:
    """
    Short-term memory for session context.
    
    Characteristics:
    - Fast access
    - Limited capacity
    - Automatic expiration
    - In-memory storage
    """
    
    def __init__(self, capacity: int = 100, ttl_seconds: int = 3600):
        self.capacity = capacity
        self.ttl_seconds = ttl_seconds
        self.store: List[Dict[str, Any]] = []
    
    def add(self, content: Any, metadata: Dict[str, Any] = None):
        """Add item to short-term memory."""
        item = {
            "content": content,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        
        self.store.append(item)
        
        # Enforce capacity
        if len(self.store) > self.capacity:
            self.store.pop(0)
        
        # Clean expired items
        self._clean_expired()
    
    def get_recent(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get most recent items."""
        self._clean_expired()
        return self.store[-count:]
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Simple text search in memory."""
        self._clean_expired()
        results = []
        
        for item in self.store:
            content_str = str(item["content"])
            if query.lower() in content_str.lower():
                results.append(item)
        
        return results
    
    def clear(self):
        """Clear all short-term memory."""
        self.store.clear()
        logger.info("Short-term memory cleared")
    
    def _clean_expired(self):
        """Remove expired items."""
        current_time = time.time()
        self.store = [
            item for item in self.store
            if current_time - item["timestamp"] < self.ttl_seconds
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "count": len(self.store),
            "capacity": self.capacity,
            "ttl_seconds": self.ttl_seconds
        }
