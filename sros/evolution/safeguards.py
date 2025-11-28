"""
Safeguards Module

Implements fail-safes and safety controls for the evolution loop.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class Safeguards:
    """
    Safety controls for the self-evolution loop.
    
    Implements:
    - Rate limiting
    - Kill switches
    - Anomaly detection
    - Operator controls
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Limits
        self.max_proposals_per_day = self.config.get("max_proposals_per_day", 10)
        self.max_files_per_proposal = self.config.get("max_files_per_proposal", 5)
        self.max_lines_per_proposal = self.config.get("max_lines_per_proposal", 500)
        
        # Kill switches
        self.emergency_stop_active = False
        self.forbidden_targets = self.config.get("forbidden_targets", [
            "secrets",
            "production_data",
            ".env",
            "credentials"
        ])
        
        # Counters
        self.proposals_today = 0
        self.last_reset_day = None
    
    def check_proposal_allowed(self, proposal) -> tuple[bool, str]:
        """
        Check if a proposal is allowed.
        
        Returns:
            (allowed, reason)
        """
        # Check emergency stop
        if self.emergency_stop_active:
            return False, "Emergency stop is active"
        
        # Check daily limit
        if self.proposals_today >= self.max_proposals_per_day:
            return False, f"Daily proposal limit reached ({self.max_proposals_per_day})"
        
        # Check file count
        if len(proposal.target_files) > self.max_files_per_proposal:
            return False, f"Too many files ({len(proposal.target_files)} > {self.max_files_per_proposal})"
        
        # Check forbidden targets
        for target in proposal.target_files:
            if any(forbidden in target.lower() for forbidden in self.forbidden_targets):
                return False, f"Forbidden target: {target}"
        
        return True, "OK"
    
    def activate_emergency_stop(self, reason: str = ""):
        """Activate emergency stop."""
        logger.critical(f"EMERGENCY STOP ACTIVATED: {reason}")
        self.emergency_stop_active = True
    
    def deactivate_emergency_stop(self):
        """Deactivate emergency stop (requires operator action)."""
        logger.warning("Emergency stop deactivated")
        self.emergency_stop_active = False
    
    def increment_proposal_count(self):
        """Increment daily proposal counter."""
        self.proposals_today += 1
    
    def reset_daily_counters(self):
        """Reset daily counters."""
        self.proposals_today = 0
        logger.info("Daily proposal counter reset")
