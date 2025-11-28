from typing import Any, Dict, Optional, List

class InMemoryBackend:
    """
    Simple in-memory storage for development and testing.
    """
    def __init__(self):
        self._store: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    def put(self, key: str, value: Any):
        self._store[key] = value

    def delete(self, key: str):
        if key in self._store:
            del self._store[key]

    def list_keys(self, prefix: str = "") -> List[str]:
        return [k for k in self._store.keys() if k.startswith(prefix)]
