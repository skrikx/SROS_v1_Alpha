import threading
import time
from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class PlaneStatus:
    status: str = "stopped" # stopped, starting, running, degraded, error
    last_updated: float = 0.0

class KernelState:
    """
    Thread-safe state manager for the SROS Kernel.
    """
    def __init__(self):
        self._lock = threading.RLock()
        self._planes: Dict[str, PlaneStatus] = {
            "kernel": PlaneStatus(),
            "runtime": PlaneStatus(),
            "governance": PlaneStatus(),
            "mirroros": PlaneStatus()
        }
        self._sessions: Dict[str, Any] = {}
        self._start_time = time.time()

    def update_plane_status(self, plane: str, status: str):
        with self._lock:
            if plane in self._planes:
                self._planes[plane].status = status
                self._planes[plane].last_updated = time.time()

    def get_plane_status(self, plane: str) -> str:
        with self._lock:
            return self._planes.get(plane, PlaneStatus()).status

    def register_session(self, session_id: str, metadata: Dict[str, Any]):
        with self._lock:
            self._sessions[session_id] = metadata

    def get_uptime(self) -> float:
        return time.time() - self._start_time

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "uptime": self.get_uptime(),
                "planes": {k: v.status for k, v in self._planes.items()},
                "active_sessions": len(self._sessions)
            }
