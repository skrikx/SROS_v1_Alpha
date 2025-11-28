"""
Long-Term Memory

Persistent memory with vector search capabilities.
"""
from typing import Dict, Any, List, Optional
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LongTermMemory:
    """
    Long-term memory with persistence.
    
    Characteristics:
    - Persistent storage
    - Unlimited capacity
    - Semantic search (with vector store)
    - Structured indexing
    """
    
    def __init__(self, storage_path: str = "./data/memory/long_term"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_path / "index.json"
        self.index = self._load_index()
    
    def add(self, key: str, content: Any, metadata: Dict[str, Any] = None):
        """Add item to long-term memory."""
        item = {
            "content": content,
            "metadata": metadata or {},
            "key": key
        }
        
        # Save to file
        item_file = self.storage_path / f"{key}.json"
        with open(item_file, 'w') as f:
            json.dump(item, f, indent=2)
        
        # Update index
        self.index[key] = {
            "file": str(item_file),
            "metadata": metadata or {}
        }
        self._save_index()
        
        logger.debug(f"Added to long-term memory: {key}")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve item by key."""
        if key not in self.index:
            return None
        
        item_file = Path(self.index[key]["file"])
        if not item_file.exists():
            return None
        
        with open(item_file, 'r') as f:
            return json.load(f)
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memory by text query."""
        results = []
        
        for key in self.index.keys():
            item = self.get(key)
            if item:
                content_str = str(item["content"])
                if query.lower() in content_str.lower():
                    results.append(item)
                    if len(results) >= limit:
                        break
        
        return results
    
    def list_keys(self) -> List[str]:
        """List all memory keys."""
        return list(self.index.keys())
    
    def delete(self, key: str):
        """Delete item from memory."""
        if key in self.index:
            item_file = Path(self.index[key]["file"])
            if item_file.exists():
                item_file.unlink()
            del self.index[key]
            self._save_index()
            logger.debug(f"Deleted from long-term memory: {key}")
    
    def _load_index(self) -> Dict[str, Any]:
        """Load memory index."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        """Save memory index."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "count": len(self.index),
            "storage_path": str(self.storage_path)
        }
