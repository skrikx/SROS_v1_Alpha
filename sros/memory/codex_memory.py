"""
Codex Memory

Knowledge base and structured knowledge packs.
"""
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class KnowledgePack:
    """
    Structured knowledge unit.
    """
    def __init__(self, pack_id: str, name: str, content: Dict[str, Any]):
        self.id = pack_id
        self.name = name
        self.content = content
        self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "metadata": self.metadata
        }


class CodexMemory:
    """
    Codex memory for structured knowledge.
    
    Characteristics:
    - Structured knowledge packs
    - Hierarchical organization
    - Version tracking
    - Import/export capabilities
    """
    
    def __init__(self, storage_path: str = "./data/memory/codex"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.packs: Dict[str, KnowledgePack] = {}
        self._load_packs()
    
    def add_pack(self, pack: KnowledgePack):
        """Add knowledge pack to codex."""
        self.packs[pack.id] = pack
        self._save_pack(pack)
        logger.info(f"Added knowledge pack: {pack.name}")
    
    def get_pack(self, pack_id: str) -> Optional[KnowledgePack]:
        """Get knowledge pack by ID."""
        return self.packs.get(pack_id)
    
    def list_packs(self) -> List[str]:
        """List all pack IDs."""
        return list(self.packs.keys())
    
    def search_packs(self, query: str) -> List[KnowledgePack]:
        """Search packs by name or content."""
        results = []
        for pack in self.packs.values():
            if query.lower() in pack.name.lower():
                results.append(pack)
            elif query.lower() in str(pack.content).lower():
                results.append(pack)
        return results
    
    def delete_pack(self, pack_id: str):
        """Delete knowledge pack."""
        if pack_id in self.packs:
            pack_file = self.storage_path / f"{pack_id}.json"
            if pack_file.exists():
                pack_file.unlink()
            del self.packs[pack_id]
            logger.info(f"Deleted knowledge pack: {pack_id}")
    
    def _load_packs(self):
        """Load all knowledge packs from storage."""
        for pack_file in self.storage_path.glob("*.json"):
            try:
                with open(pack_file, 'r') as f:
                    data = json.load(f)
                    pack = KnowledgePack(
                        pack_id=data["id"],
                        name=data["name"],
                        content=data["content"]
                    )
                    pack.metadata = data.get("metadata", {})
                    self.packs[pack.id] = pack
            except Exception as e:
                logger.error(f"Error loading pack {pack_file}: {e}")
    
    def _save_pack(self, pack: KnowledgePack):
        """Save knowledge pack to storage."""
        pack_file = self.storage_path / f"{pack.id}.json"
        with open(pack_file, 'w') as f:
            json.dump(pack.to_dict(), f, indent=2)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get codex statistics."""
        return {
            "pack_count": len(self.packs),
            "storage_path": str(self.storage_path)
        }
