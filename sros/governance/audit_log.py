import time
import json
import os

class AuditLog:
    """
    Secure, append-only log for governance events.
    """
    def __init__(self, log_path: str = "./data/audit.log"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def log(self, actor: str, action: str, resource: str, decision: str, reason: str = ""):
        entry = {
            "timestamp": time.time(),
            "actor": actor,
            "action": action,
            "resource": resource,
            "decision": decision,
            "reason": reason
        }
        
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
