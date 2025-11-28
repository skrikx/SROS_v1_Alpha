"""
Test Sovereign Directive

Verify governance logic and integration.
"""
import pytest
import os
from sros.governance.sovereign_directive import SovereignDirective, ActionType, RiskLevel, DirectiveDecision
from sros.governance.sovereign_audit_log import SovereignAuditLog

class TestSovereignDirective:
    """Test suite for Sovereign Directive."""
    
    @pytest.fixture
    def directive(self, tmp_path):
        """Create directive with temp audit log."""
        log_path = tmp_path / "test_audit.jsonl"
        audit_log = SovereignAuditLog(str(log_path))
        return SovereignDirective(audit_log=audit_log)
        
    def test_allow_low_risk(self, directive):
        """Test allowed low risk action."""
        decision = directive.evaluate_action(
            ActionType.READ,
            {"target": "sros/kernel/kernel.py"}
        )
        
        assert decision.allowed
        assert not decision.requires_hassan_approval
        assert decision.risk == RiskLevel.LOW
        
    def test_block_forbidden_scope(self, directive):
        """Test blocking forbidden scope."""
        decision = directive.evaluate_action(
            ActionType.READ,
            {"target": "/etc/passwd"}
        )
        
        assert not decision.allowed
        assert decision.risk == RiskLevel.CRITICAL
        assert "Forbidden domain" in decision.reason or "Law SCOPE.2" in decision.reason
        
    def test_flag_high_risk_modification(self, directive):
        """Test flagging high risk modification."""
        decision = directive.evaluate_action(
            ActionType.MODIFY_CODE,
            {"target": "sros/governance/policy.py"}
        )
        
        assert decision.allowed
        assert decision.requires_hassan_approval
        assert decision.risk == RiskLevel.HIGH
        
    def test_audit_logging(self, directive):
        """Test that decisions are logged."""
        directive.evaluate_action(ActionType.READ, {"target": "test"})
        
        logs = directive.audit_log.get_recent_logs(1)
        assert len(logs) == 1
        assert logs[0]["type"] == "DECISION"
        assert logs[0]["context"]["target"] == "test"
