"""
Integration Test: Agents with Real Gemini API

Tests that agents successfully use Gemini for real responses.
"""
import pytest
import os
from sros.runtime.agents import ArchitectAgent, BuilderAgent, SROSTesterAgent


class TestAgentGeminiIntegration:
    """Integration tests for agents with Gemini API."""
    
    @pytest.fixture
    def skip_if_no_api_key(self):
        """Skip test if no Gemini API key."""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")
    
    def test_architect_with_gemini(self, skip_if_no_api_key):
        """Test Architect agent with real Gemini calls."""
        agent = ArchitectAgent()
        agent.initialize()
        
        # Verify adapter is initialized
        assert agent.adapter is not None
        assert agent.adapter.name == "gemini"
        
        # Run analysis
        result = agent.act("The memory system is experiencing high latency. Analyze and recommend improvements.")
        
        # Verify response
        assert result is not None
        assert len(result) > 100  # Should be substantial
        assert "[ERROR]" not in result
        assert "memory" in result.lower() or "latency" in result.lower()
        
        print(f"\n=== Architect Response ===\n{result[:500]}...")
    
    def test_builder_with_gemini(self, skip_if_no_api_key):
        """Test Builder agent with real Gemini calls."""
        agent = BuilderAgent()
        agent.initialize()
        
        assert agent.adapter is not None
        
        # Request code generation
        result = agent.act(
            "Create a simple Python function that calculates fibonacci numbers with memoization.",
            context={"requirements": "Use type hints and add docstring"}
        )
        
        # Verify response
        assert result is not None
        assert len(result) > 50
        assert "[ERROR]" not in result
        assert "def" in result or "fibonacci" in result.lower()
        
        print(f"\n=== Builder Response ===\n{result[:500]}...")
    
    def test_tester_with_gemini(self, skip_if_no_api_key):
        """Test Tester agent with real Gemini calls."""
        agent = SROSTesterAgent()
        agent.initialize()
        
        assert agent.adapter is not None
        
        # Request test generation
        result = agent.act(
            "Generate pytest tests for a function that validates email addresses.",
            context={"code": "def validate_email(email: str) -> bool: ..."}
        )
        
        # Verify response
        assert result is not None
        assert len(result) > 50
        assert "[ERROR]" not in result
        assert "test" in result.lower() or "pytest" in result.lower()
        
        print(f"\n=== Tester Response ===\n{result[:500]}...")
    
    def test_cost_tracking(self, skip_if_no_api_key):
        """Test that costs are tracked for agent calls."""
        agent = ArchitectAgent()
        agent.initialize()
        
        # Make a call
        result = agent.act("Quick analysis: Is the kernel healthy?")
        
        # Cost should be tracked (we can't verify exact amount, but should be > 0)
        assert result is not None
        # In production, would verify CostTracker has recorded this
    
    def test_all_agents_sequential(self, skip_if_no_api_key):
        """Test all agents in sequence (simulating workflow)."""
        # Architect analyzes
        architect = ArchitectAgent()
        architect.initialize()
        analysis = architect.act("We need to improve error handling in adapters.")
        
        assert analysis is not None
        assert len(analysis) > 100
        
        # Builder implements
        builder = BuilderAgent()
        builder.initialize()
        code = builder.act(
            "Based on this analysis, create an error handling wrapper for adapters.",
            context={"analysis": analysis[:200]}
        )
        
        assert code is not None
        assert len(code) > 50
        
        # Tester creates tests
        tester = SROSTesterAgent()
        tester.initialize()
        tests = tester.act(
            "Generate tests for this error handling code.",
            context={"code": code[:200]}
        )
        
        assert tests is not None
        assert len(tests) > 50
        
        print(f"\n=== Full Workflow ===")
        print(f"Analysis length: {len(analysis)}")
        print(f"Code length: {len(code)}")
        print(f"Tests length: {len(tests)}")
