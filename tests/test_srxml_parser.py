"""
Test SRXML Parser

Tests for SRXMLParser including dict parsing and typed object conversion.
"""
import pytest
from pathlib import Path
from sros.srxml.parser import SRXMLParser
from sros.srxml.models import SRXAgent, SR8Workflow, GovernancePolicy


class TestSRXMLParser:
    """Test suite for SRXML parser."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return SRXMLParser()
    
    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory."""
        return Path(__file__).parent / "fixtures"
    
    def test_parse_workflow_to_dict(self, parser, fixtures_dir):
        """Test parsing workflow to dictionary."""
        workflow_path = fixtures_dir / "sample_workflow.srxml"
        result = parser.parse(str(workflow_path))
        
        assert result["tag"] == "workflow"
        assert "@id" in result
        assert "step" in result
    
    def test_parse_agent_to_dict(self, parser, fixtures_dir):
        """Test parsing agent to dictionary."""
        agent_path = fixtures_dir / "sample_agent_prompt.srxml"
        result = parser.parse(str(agent_path))
        
        assert result["tag"] == "agent"
        assert "name" in result
        assert result["name"]["#text"] == "Test Agent"
    
    def test_parse_workflow_to_object(self, parser, fixtures_dir):
        """Test parsing workflow to typed object."""
        workflow_path = fixtures_dir / "sample_workflow.srxml"
        workflow = parser.parse_to_object(str(workflow_path))
        
        assert isinstance(workflow, SR8Workflow)
        assert workflow.id == "test.workflow.1"
        assert len(workflow.steps) == 2
        assert workflow.steps[0].id == "step1"
    
    def test_parse_with_locks(self, parser, fixtures_dir):
        """Test parsing with execution locks."""
        workflow_path = fixtures_dir / "sample_workflow.srxml"
        workflow = parser.parse_to_object(str(workflow_path))
        
        assert hasattr(workflow, 'locks')
        assert isinstance(workflow.locks.one_pass_lock, bool)
    
    def test_parse_nonexistent_file(self, parser):
        """Test parsing nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            parser.parse("nonexistent.srxml")
    
    def test_parse_unknown_document_type(self, parser, tmp_path):
        """Test parsing unknown document type raises error."""
        unknown_file = tmp_path / "unknown.srxml"
        unknown_file.write_text(
            '<?xml version="1.0"?>'
            '<unknown_type id="test" version="1.0.0" tenant="default"/>'
        )
        
        with pytest.raises(ValueError, match="Unknown SRXML document type"):
            parser.parse_to_object(str(unknown_file))
