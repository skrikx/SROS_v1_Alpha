"""
Enhanced Memory Router

Routes memory operations across short-term, long-term, and codex layers.
"""
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MemoryRouter:
    """
    Routes memory operations across multiple layers.
    
    Layers:
    - short: Session memory (fast, temporary)
    - long: Persistent memory (slow, permanent)
    - codex: Knowledge packs (structured, versioned)
    """
    
    def __init__(self):
        self.short_term = None
        self.long_term = None
        self.codex = None
        self.vector_store = None
        
        # Legacy in-memory store for backward compatibility
        self.memory_store: Dict[str, Any] = {}
    
    def initialize_layers(self, short_term, long_term, codex, vector_store=None):
        """Initialize memory layers."""
        self.short_term = short_term
        self.long_term = long_term
        self.codex = codex
        self.vector_store = vector_store
        logger.info("Memory layers initialized")
    
    def read(self, query: str = None, layer: str = "short", key: str = None) -> list:
        """
        Read from memory layer.
        
        Args:
            query: Text query for search
            layer: Memory layer (short, long, codex)
            key: Specific key to retrieve
        
        Returns:
            List of matching items
        """
        if layer == "short" and self.short_term:
            if query:
                return self.short_term.search(query)
            else:
                return self.short_term.get_recent(10)
        
        elif layer == "long" and self.long_term:
            if key:
                item = self.long_term.get(key)
                return [item] if item else []
            elif query:
                return self.long_term.search(query)
            else:
                return []
        
        elif layer == "codex" and self.codex:
            if query:
                packs = self.codex.search_packs(query)
                return [p.to_dict() for p in packs]
            else:
                return []
        
        else:
            # Fallback to legacy store
            results = []
            for k, v in self.memory_store.items():
                if k.startswith(f"{layer}:"):
                    if query and query in v.get('content', ''):
                        results.append(v)
                    elif key and k == f"{layer}:{key}":
                        results.append(v)
            return results
    
    def write(self, content: Any, layer: str = "short", key: str = None, metadata: dict = None):
        """
        Write to memory layer.
        
        Args:
            content: Content to store
            layer: Memory layer
            key: Optional key
            metadata: Optional metadata
        """
        if layer == "short" and self.short_term:
            self.short_term.add(content, metadata)
        
        elif layer == "long" and self.long_term:
            if not key:
                import uuid
                key = str(uuid.uuid4())
            self.long_term.add(key, content, metadata)
            
            # Also add to vector store if available
            if self.vector_store:
                self.vector_store.add(key, str(content), metadata)
        
        elif layer == "codex" and self.codex:
            # Codex requires structured knowledge packs
            logger.warning("Use codex.add_pack() for codex layer")
        
        else:
            # Fallback to legacy store
            if key is None:
                key = str(len(self.memory_store))
            full_key = f"{layer}:{key}"
            self.memory_store[full_key] = {
                'content': content,
                'metadata': metadata or {}
            }
    
    def semantic_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic search across all layers using vector store.
        """
        if self.vector_store:
            return self.vector_store.search(query, limit)
        else:
            # Fallback to text search
            results = []
            if self.short_term:
                results.extend(self.short_term.search(query))
            if self.long_term:
                results.extend(self.long_term.search(query, limit))
            return results[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all memory layers."""
        stats = {}
        if self.short_term:
            stats["short_term"] = self.short_term.get_stats()
        if self.long_term:
            stats["long_term"] = self.long_term.get_stats()
        if self.codex:
            stats["codex"] = self.codex.get_stats()
        if self.vector_store:
            stats["vector_store"] = self.vector_store.get_stats()
        return stats
