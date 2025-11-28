"""
Vector Store

Embedding and semantic search for memory.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector storage for semantic search.
    
    Uses in-memory storage by default.
    Can be extended to use Chroma, FAISS, or other vector DBs.
    """
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.vectors: List[Dict[str, Any]] = []
        self.use_external = False
        
        # Try to import vector DB
        try:
            import chromadb
            self.chroma_client = chromadb.Client()
            self.collection = self.chroma_client.create_collection("sros_memory")
            self.use_external = True
            logger.info("Using Chroma for vector storage")
        except ImportError:
            logger.info("Using in-memory vector storage (install chromadb for better performance)")
    
    def add(self, id: str, text: str, metadata: Dict[str, Any] = None):
        """Add text with embedding."""
        if self.use_external:
            self.collection.add(
                ids=[id],
                documents=[text],
                metadatas=[metadata or {}]
            )
        else:
            # In-memory fallback
            self.vectors.append({
                "id": id,
                "text": text,
                "metadata": metadata or {}
            })
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Semantic search by query."""
        if self.use_external:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            return self._format_results(results)
        else:
            # Simple text matching fallback
            matches = []
            for item in self.vectors:
                if query.lower() in item["text"].lower():
                    matches.append(item)
                    if len(matches) >= limit:
                        break
            return matches
    
    def delete(self, id: str):
        """Delete vector by ID."""
        if self.use_external:
            self.collection.delete(ids=[id])
        else:
            self.vectors = [v for v in self.vectors if v["id"] != id]
    
    def _format_results(self, results: Dict) -> List[Dict[str, Any]]:
        """Format Chroma results."""
        formatted = []
        if results and "documents" in results:
            for i, doc in enumerate(results["documents"][0]):
                formatted.append({
                    "id": results["ids"][0][i],
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if "metadatas" in results else {}
                })
        return formatted
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        return {
            "count": len(self.vectors) if not self.use_external else "N/A",
            "dimension": self.dimension,
            "backend": "chroma" if self.use_external else "in-memory"
        }
