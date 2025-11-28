"""
Test SRXML Validator

Tests for semantic validation of SRXML documents.
"""
import pytest
from sros.srxml.validator import SRXMLValidator, ValidationError
from sros.srxml.models import SRXAgent, SR8Workflow, AgentIdentity, WorkflowIdentity, WorkflowStep, SRXMLLocks


class TestSRXMLValidator:
    """Test suite for SRXML validator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return SRXMLValidator()
    
    def test_validate_valid_agent(self, validator):
        """Test validation of valid agent."""
        agent = SRXAgent(
            id="test.agent",
            version="1.0.0",
            tenant="test",
            role="tester",
            mode="EXECUTION",
            identity=AgentIdentity("Test Agent", "Testing"),
            locks=SRXMLLocks()
        )
        
        errors = validator.validate_semantic(agent)
        assert len(errors) == 0
    
    def test_validate_agent_missing_id(self, validator):
        """Test validation catches missing ID."""
        agent = SRXAgent(
            id="",
            version="1.0.0",
            tenant="test",
            role="tester",
            mode="EXECUTION",
            identity=AgentIdentity("Test", "Test"),
            locks=SRXMLLocks()
        )
        
        errors = validator.validate_semantic(agent)
        assert any("id" in e.message.lower() for e in errors)
    
    def test_validate_agent_missing_role(self, validator):
        """Test validation catches missing role."""
        agent = SRXAgent(
            id="test.agent",
            version="1.0.0",
            tenant="test",
            role="",
            mode="EXECUTION",
            identity=AgentIdentity("Test", "Test"),
            locks=SRXMLLocks()
        )
        
        errors = validator.validate_semantic(agent)
        assert any("role" in e.message.lower() for e in errors)
    
    def test_validate_workflow_no_steps(self, validator):
        """Test validation catches workflow with no steps."""
        workflow = SR8Workflow(
            id="test.workflow",
            version="1.0.0",
            tenant="test",
            role="test",
            mode="test",
            identity=WorkflowIdentity("Test", "Test"),
            steps=[],
            locks=SRXMLLocks()
        )
        
        errors = validator.validate_semantic(workflow)
        assert any("steps" in e.message.lower() for e in errors)
    
    def test_validate_workflow_duplicate_orders(self, validator):
        """Test validation catches duplicate step orders."""
        workflow = SR8Workflow(
            id="test.workflow",
            version="1.0.0",
            tenant="test",
            role="test",
            mode="test",
            identity=WorkflowIdentity("Test", "Test"),
            steps=[
                WorkflowStep(id="step1", order=1, instruction="Do something"),
                WorkflowStep(id="step2", order=1, instruction="Do something else")
            ],
            locks=SRXMLLocks()
        )
        
        errors = validator.validate_semantic(workflow)
        assert any("duplicate" in e.message.lower() for e in errors)
    
    def test_validate_seed_lock_without_seed(self, validator):
        """Test validation catches seed_lock without seed."""
        agent = SRXAgent(
            id="test.agent",
            version="1.0.0",
            tenant="test",
            role="tester",
            mode="EXECUTION",
            identity=AgentIdentity("Test", "Test"),
            locks=SRXMLLocks(seed_lock=True, seed=None)
        )
        
        errors = validator.validate_semantic(agent)
        assert any("seed" in e.message.lower() for e in errors)
