"""
Skrikx Prime Agent

The Sovereign System Intelligence agent implementation.
Enforces the Sovereign Directive in all actions.
"""
from typing import Dict, Any, Optional
from ..agents.architect_agent import ArchitectAgent
from ...governance.sovereign_directive import SovereignDirective, ActionType, RiskLevel

class SkrikxAgent(ArchitectAgent):
    """
    Skrikx Prime - The Sovereign System Intelligence.
    
    Extends ArchitectAgent with strict governance enforcement via 
    SovereignDirective.
    """
    
    def __init__(self, event_bus=None, adapter=None, config: Dict[str, Any] = None):
        super().__init__(
            event_bus=event_bus, 
            adapter=adapter, 
            config=config
        )
        self.name = "Skrikx Prime"
        self.role = "Sovereign System Intelligence"
        self.directive = SovereignDirective()
        
    def act(self, observation: str, context: Dict[str, Any] = None) -> str:
        """
        Process observation with governance checks.
        """
        # 1. Check if action is allowed (Conceptually, 'act' is THINK/PLAN)
        decision = self.directive.evaluate_action(
            ActionType.THINK, 
            {"observation": observation}
        )
        
        if not decision.allowed:
            return f"[SOVEREIGN BLOCK] {decision.reason}"
            
        # 2. Proceed with standard Architect behavior
        response = super().act(observation, context)
        
        # 3. (Future) Analyze response for proposed actions and check them too
        return response

    def propose_modification(self, file_path: str, content: str, reason: str) -> Dict[str, Any]:
        """
        Explicit method for proposing code changes.
        """
        decision = self.directive.evaluate_action(
            ActionType.MODIFY_CODE,
            {"target": file_path, "reason": reason}
        )
        
        if not decision.allowed:
            return {"status": "BLOCKED", "reason": decision.reason}
            
        if decision.requires_hassan_approval:
            return {
                "status": "PENDING_APPROVAL", 
                "reason": decision.reason,
                "risk": decision.risk.value
            }
            
        return {"status": "ALLOWED", "risk": decision.risk.value}
