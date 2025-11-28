"""
Test Ouroboros Evolution Loop

Tests for self-evolution loop orchestration and safety.
"""
import pytest
from sros.evolution.ouroboros import OuroborosLoop, EvolutionProposal, LoopStage
from sros.evolution.observer import Observer
from sros.evolution.analyzer import Analyzer
from sros.evolution.proposer import Proposer
from sros.evolution.safeguards import Safeguards


class TestOuroborosLoop:
    """Test suite for Ouroboros loop."""
    
    @pytest.fixture
    def loop(self):
        """Create loop instance."""
        config = {
            "enabled": True,
            "max_concurrent": 3,
            "require_human_approval": False  # Disable for testing
        }
        loop = OuroborosLoop(config)
        
        # Inject components
        loop.observer = Observer()
        loop.analyzer = Analyzer()
        loop.proposer = Proposer()
        
        return loop
    
    def test_initialization(self, loop):
        """Test loop initialization."""
        assert loop.enabled
        assert loop.max_concurrent_proposals == 3
    
    def test_safety_constraints(self, loop):
        """Test safety constraint checking."""
        assert loop._check_safety_constraints()
        
        # Add max proposals
        for i in range(3):
            loop.active_proposals.append(
                EvolutionProposal(
                    id=f"test-{i}",
                    title="Test",
                    description="Test",
                    rationale="Test",
                    stage=LoopStage.PROPOSE
                )
            )
        
        # Should fail now
        assert not loop._check_safety_constraints()
    
    def test_emergency_stop(self, loop):
        """Test emergency stop."""
        loop.emergency_stop()
        
        assert not loop.enabled
        assert loop.config["emergency_stop"]
        assert len(loop.active_proposals) == 0
    
    def test_get_status(self, loop):
        """Test status retrieval."""
        status = loop.get_status()
        
        assert "enabled" in status
        assert "active_proposals" in status
        assert status["enabled"] == True


class TestSafeguards:
    """Test suite for safeguards."""
    
    @pytest.fixture
    def safeguards(self):
        """Create safeguards instance."""
        return Safeguards(config={
            "max_proposals_per_day": 5,
            "max_files_per_proposal": 3
        })
    
    def test_check_proposal_allowed(self, safeguards):
        """Test proposal allowance check."""
        proposal = EvolutionProposal(
            id="test",
            title="Test",
            description="Test",
            rationale="Test",
            stage=LoopStage.PROPOSE,
            target_files=["file1.py", "file2.py"]
        )
        
        allowed, reason = safeguards.check_proposal_allowed(proposal)
        assert allowed
        assert reason == "OK"
    
    def test_check_too_many_files(self, safeguards):
        """Test rejection of proposals with too many files."""
        proposal = EvolutionProposal(
            id="test",
            title="Test",
            description="Test",
            rationale="Test",
            stage=LoopStage.PROPOSE,
            target_files=["f1.py", "f2.py", "f3.py", "f4.py"]
        )
        
        allowed, reason = safeguards.check_proposal_allowed(proposal)
        assert not allowed
        assert "Too many files" in reason
    
    def test_check_forbidden_target(self, safeguards):
        """Test rejection of forbidden targets."""
        proposal = EvolutionProposal(
            id="test",
            title="Test",
            description="Test",
            rationale="Test",
            stage=LoopStage.PROPOSE,
            target_files=["secrets.yml"]
        )
        
        allowed, reason = safeguards.check_proposal_allowed(proposal)
        assert not allowed
        assert "Forbidden target" in reason
    
    def test_emergency_stop(self, safeguards):
        """Test emergency stop activation."""
        safeguards.activate_emergency_stop("Test reason")
        
        assert safeguards.emergency_stop_active
        
        proposal = EvolutionProposal(
            id="test",
            title="Test",
            description="Test",
            rationale="Test",
            stage=LoopStage.PROPOSE
        )
        
        allowed, reason = safeguards.check_proposal_allowed(proposal)
        assert not allowed
        assert "Emergency stop" in reason
