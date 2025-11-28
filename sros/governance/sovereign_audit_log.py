"""
Sovereign Audit Log

Immutable logging for Sovereign Directive decisions and self-modifications.
"""
import logging
import json
import time
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class SovereignAuditLog:
    """
    Maintains a persistent log of all governance decisions and 
    system self-modifications.
    """
    
    def __init__(self, log_path: str = "sros_audit.jsonl"):
        self.log_path = Path(log_path)
        self._ensure_log_exists()
        
    def _ensure_log_exists(self):
        if not self.log_path.exists():
            self.log_path.touch()
            
    def log_decision(self, decision: Any, context: Dict[str, Any]):
        """Log a governance decision."""
        entry = {
            "timestamp": time.time(),
            "type": "DECISION",
            "decision": {
                "allowed": decision.allowed,
                "requires_approval": decision.requires_hassan_approval,
                "risk": decision.risk.value if hasattr(decision.risk, 'value') else str(decision.risk),
                "reason": decision.reason
            },
            "context": context
        }
        self._append_entry(entry)
        
    def log_modification(self, details: Dict[str, Any]):
        """Log a self-modification event."""
        entry = {
            "timestamp": time.time(),
            "type": "MODIFICATION",
            "details": details
        }
        self._append_entry(entry)
        
    def _append_entry(self, entry: Dict[str, Any]):
        """Append entry to JSONL file."""
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write to audit log: {e}")
            
    def get_recent_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent log entries."""
        logs = []
        if not self.log_path.exists():
            return logs
            
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines[-limit:]):
                    logs.append(json.loads(line))
        except Exception as e:
            logger.error(f"Failed to read audit log: {e}")
            
        return logs
