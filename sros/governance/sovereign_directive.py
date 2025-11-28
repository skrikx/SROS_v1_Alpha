"""
Sovereign Directive

Executable implementation of the Sovereign Laws for Skrikx Prime.
"""
import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum
from .sovereign_audit_log import SovereignAuditLog

logger = logging.getLogger(__name__)

class ActionType(Enum):
    READ = "READ"
    THINK = "THINK"
    MODIFY_CODE = "MODIFY_CODE"
    DELETE_FILE = "DELETE_FILE"
    EXECUTE_COMMAND = "EXECUTE_COMMAND"
    EXTERNAL_CALL = "EXTERNAL_CALL"
    EVOLVE_STRUCTURE = "EVOLVE_STRUCTURE"

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class DirectiveDecision:
    allowed: bool
    requires_hassan_approval: bool
    risk: RiskLevel
    reason: str

class SovereignDirective:
    """
    Enforces Sovereign Laws by evaluating actions against defined policies.
    """
    
    def __init__(self, audit_log: Optional[SovereignAuditLog] = None):
        self.audit_log = audit_log or SovereignAuditLog()
        self.active = True
        
    def evaluate_action(self, action_type: ActionType, context: Dict[str, Any]) -> DirectiveDecision:
        """
        Evaluate if an action is allowed under Sovereign Laws.
        """
        decision = self._apply_laws(action_type, context)
        
        # Log every decision
        self.audit_log.log_decision(decision, {
            "action": action_type.value,
            **context
        })
        
        return decision
        
    def _apply_laws(self, action_type: ActionType, context: Dict[str, Any]) -> DirectiveDecision:
        """Core logic mapping laws to decisions."""
        
        # LAW SCOPE.2: Forbidden Domains
        if self._is_forbidden_scope(context):
            return DirectiveDecision(
                allowed=False,
                requires_hassan_approval=False,
                risk=RiskLevel.CRITICAL,
                reason="Action targets forbidden domain (Law SCOPE.2)"
            )
            
        # LAW SAFE.1: Self-modification checks
        if action_type in [ActionType.MODIFY_CODE, ActionType.DELETE_FILE, ActionType.EVOLVE_STRUCTURE]:
            return self._evaluate_modification(context)
            
        # LAW AUTH.2: High risk operations
        if action_type == ActionType.EXECUTE_COMMAND:
            cmd = context.get("command", "")
            if self._is_high_risk_command(cmd):
                return DirectiveDecision(
                    allowed=True, # Allowed pending approval
                    requires_hassan_approval=True,
                    risk=RiskLevel.HIGH,
                    reason="High risk command execution (Law AUTH.2)"
                )
                
        # Default: Low risk, allowed
        return DirectiveDecision(
            allowed=True,
            requires_hassan_approval=False,
            risk=RiskLevel.LOW,
            reason="Standard operation within allowed scope"
        )
        
    def _is_forbidden_scope(self, context: Dict[str, Any]) -> bool:
        """Check if target is outside allowed boundaries."""
        target = context.get("target", "")
        if ".." in target or target.startswith("/"):
            # Simple path traversal check - real impl would be more robust
            return True
        return False
        
    def _evaluate_modification(self, context: Dict[str, Any]) -> DirectiveDecision:
        """Evaluate code modification risks."""
        target_file = context.get("target", "")
        
        # Critical core files require approval
        if "governance" in target_file or "kernel" in target_file:
            return DirectiveDecision(
                allowed=True,
                requires_hassan_approval=True,
                risk=RiskLevel.HIGH,
                reason="Modification to core system files (Law SAFE.2)"
            )
            
        return DirectiveDecision(
            allowed=True,
            requires_hassan_approval=False,
            risk=RiskLevel.MEDIUM,
            reason="Standard code modification"
        )

    def _is_high_risk_command(self, cmd: str) -> bool:
        """Check for dangerous commands."""
        risky = ["rm -rf", "format", "mkfs", "dd"]
        return any(r in cmd for r in risky)
