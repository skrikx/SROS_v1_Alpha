"""
Policy Enforcer

Enforces governance policies on adapter calls and evolution proposals.
"""
from typing import Dict, Any, Optional
import logging
from .policy_engine import PolicyEngine, PolicyResult

logger = logging.getLogger(__name__)


class PolicyEnforcer:
    """
    Enforces governance policies across SROS operations.
    
    Integration points:
    - Pre-call checks for adapters
    - Post-call validation
    - Evolution proposal gates
    - Cost and quota enforcement
    """
    
    def __init__(self, policy_engine: PolicyEngine = None):
        self.policy_engine = policy_engine or PolicyEngine()
        self.enforcement_mode = "strict"  # strict, permissive, audit
        self._call_count = 0
    
    def check_adapter_call(
        self,
        adapter_type: str,
        adapter_name: str,
        context: Dict[str, Any] = None
    ) -> PolicyResult:
        """
        Check if adapter call is allowed by policy.
        
        Args:
            adapter_type: Type of adapter (model, tool, storage)
            adapter_name: Name of adapter
            context: Call context (tenant, user, etc.)
        
        Returns:
            PolicyResult indicating if call is allowed
        """
        action = f"adapter.{adapter_type}.{adapter_name}"
        
        # Evaluate policy
        result = self.policy_engine.evaluate(action, context or {})
        
        if not result.allowed and self.enforcement_mode == "strict":
            logger.warning(f"Policy denied adapter call: {action} - {result.reason}")
        elif not result.allowed and self.enforcement_mode == "audit":
            logger.info(f"Policy would deny (audit mode): {action} - {result.reason}")
            # Allow in audit mode
            result.allowed = True
        
        self._call_count += 1
        return result
    
    def check_evolution_proposal(self, proposal) -> PolicyResult:
        """
        Check if evolution proposal is allowed.
        
        Args:
            proposal: EvolutionProposal object
        
        Returns:
            PolicyResult indicating if proposal is allowed
        """
        action = "evolution.proposal"
        context = {
            "proposal_id": proposal.id,
            "target_files": len(proposal.target_files),
            "priority": proposal.metadata.get("priority", 5)
        }
        
        result = self.policy_engine.evaluate(action, context)
        
        if not result.allowed:
            logger.warning(f"Policy denied evolution proposal: {proposal.id} - {result.reason}")
        
        return result
    
    def record_call(
        self,
        adapter_type: str,
        adapter_name: str,
        result: Any,
        context: Dict[str, Any] = None
    ):
        """
        Record adapter call for audit and telemetry.
        
        Args:
            adapter_type: Type of adapter
            adapter_name: Name of adapter
            result: Call result
            context: Call context
        """
        # This would integrate with MirrorOS witness
        logger.debug(f"Recorded call: {adapter_type}/{adapter_name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enforcement statistics."""
        return {
            "total_calls": self._call_count,
            "enforcement_mode": self.enforcement_mode
        }
