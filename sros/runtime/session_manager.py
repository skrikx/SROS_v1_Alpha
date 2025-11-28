import uuid
import time
from typing import Dict, Any, Optional

class SessionManager:
    """
    Manages Runtime Sessions.
    """
    def __init__(self, kernel_context):
        self.kernel = kernel_context
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, user_id: str, tenant_id: str) -> str:
        session_id = str(uuid.uuid4())
        session_data = {
            "id": session_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "start_time": time.time(),
            "status": "active",
            "memory_context": {}
        }
        self.sessions[session_id] = session_data
        
        # Register with Kernel State
        self.kernel.state.register_session(session_id, {"user": user_id, "tenant": tenant_id})
        
        self.kernel.event_bus.publish("runtime", "session.created", {"session_id": session_id})
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(session_id)

    def close_session(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id]["status"] = "closed"
            self.sessions[session_id]["end_time"] = time.time()
            self.kernel.event_bus.publish("runtime", "session.closed", {"session_id": session_id})
