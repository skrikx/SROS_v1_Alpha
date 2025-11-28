"""
Filesystem Storage Adapter

Provides local filesystem storage capabilities.
"""
from typing import Any, Dict, Optional
import os
import json
import logging
from ..base import StorageAdapter, AdapterResult, AdapterError

logger = logging.getLogger(__name__)


class FilesystemAdapter(StorageAdapter):
    """
    Adapter for local filesystem storage.
    """
    
    def __init__(self, name: str = "filesystem", config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.base_path = config.get("base_path", "./data") if config else "./data"
    
    def initialize(self) -> bool:
        """Initialize filesystem adapter."""
        try:
            # Create base directory if it doesn't exist
            os.makedirs(self.base_path, exist_ok=True)
            self._initialized = True
            logger.info(f"Filesystem adapter initialized at: {self.base_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize filesystem adapter: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if adapter is healthy."""
        return self._initialized and os.path.exists(self.base_path)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return adapter metadata."""
        return {
            "name": self.name,
            "type": "storage",
            "provider": "Filesystem",
            "base_path": self.base_path,
            "initialized": self._initialized
        }
    
    def get(self, key: str) -> AdapterResult:
        """Retrieve data by key."""
        if not self._initialized:
            raise AdapterError("Adapter not initialized", adapter_type="storage")
        
        file_path = self._get_file_path(key)
        
        if not os.path.exists(file_path):
            return AdapterResult(
                success=False,
                data=None,
                error=f"Key not found: {key}"
            )
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return AdapterResult(
                success=True,
                data=data.get("value"),
                metadata=data.get("metadata", {}),
                size=os.path.getsize(file_path)
            )
        except Exception as e:
            logger.error(f"Failed to read key {key}: {e}")
            return AdapterResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    def put(self, key: str, value: Any, metadata: Dict[str, Any] = None) -> AdapterResult:
        """Store data with key."""
        if not self._initialized:
            raise AdapterError("Adapter not initialized", adapter_type="storage")
        
        file_path = self._get_file_path(key)
        
        # Create directory if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            data = {
                "value": value,
                "metadata": metadata or {}
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return AdapterResult(
                success=True,
                data={"key": key},
                size=os.path.getsize(file_path)
            )
        except Exception as e:
            logger.error(f"Failed to write key {key}: {e}")
            return AdapterResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    def delete(self, key: str) -> AdapterResult:
        """Delete data by key."""
        if not self._initialized:
            raise AdapterError("Adapter not initialized", adapter_type="storage")
        
        file_path = self._get_file_path(key)
        
        if not os.path.exists(file_path):
            return AdapterResult(
                success=False,
                data=None,
                error=f"Key not found: {key}"
            )
        
        try:
            os.remove(file_path)
            return AdapterResult(
                success=True,
                data={"key": key, "deleted": True}
            )
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return AdapterResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    def list(self, prefix: str = "") -> AdapterResult:
        """List keys with optional prefix."""
        if not self._initialized:
            raise AdapterError("Adapter not initialized", adapter_type="storage")
        
        try:
            keys = []
            search_path = os.path.join(self.base_path, prefix) if prefix else self.base_path
            
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith('.json'):
                        rel_path = os.path.relpath(os.path.join(root, file), self.base_path)
                        key = rel_path.replace('.json', '').replace(os.sep, '/')
                        keys.append(key)
            
            return AdapterResult(
                success=True,
                data={"keys": keys, "count": len(keys)}
            )
        except Exception as e:
            logger.error(f"Failed to list keys: {e}")
            return AdapterResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        file_path = self._get_file_path(key)
        return os.path.exists(file_path)
    
    def _get_file_path(self, key: str) -> str:
        """Convert key to file path."""
        # Sanitize key
        safe_key = key.replace('..', '').replace('\\', '/')
        return os.path.join(self.base_path, f"{safe_key}.json")
