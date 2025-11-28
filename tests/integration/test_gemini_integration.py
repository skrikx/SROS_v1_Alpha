"""
Integration Test: Adapter with Real Gemini API

Tests adapter with actual Gemini API using provided key.
"""
import pytest
import os
from sros.adapters.models.gemini_adapter import GeminiAdapter
from sros.adapters.base import AdapterResult


class TestGeminiIntegration:
    """Integration tests with real Gemini API."""
    
    @pytest.fixture
    def adapter(self):
        """Create Gemini adapter with API key."""
        # API key should be in environment
        adapter = GeminiAdapter(config={
            "api_key": os.getenv("GEMINI_API_KEY"),
            "model": "gemini-2.0-flash-exp"
        })
        adapter.initialize()
        return adapter
    
    def test_real_generation(self, adapter):
        """Test real text generation."""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")
        
        result = adapter.generate("Say 'Hello SROS' in exactly 2 words.")
        
        assert isinstance(result, AdapterResult)
        assert result.success
        assert result.text is not None
        assert len(result.text) > 0
        assert result.tokens is not None
        assert result.cost >= 0.0
        
        print(f"\nGenerated: {result.text}")
        print(f"Tokens: {result.tokens}")
        print(f"Cost: ${result.cost:.6f}")
    
    def test_cost_estimation(self, adapter):
        """Test cost estimation accuracy."""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")
        
        result = adapter.generate("Count to 5.")
        
        assert result.success
        assert result.cost > 0.0
        
        # Verify cost calculation
        estimated_cost = adapter.estimate_cost(
            result.tokens["prompt"],
            result.tokens["completion"]
        )
        
        assert abs(result.cost - estimated_cost) < 0.000001
