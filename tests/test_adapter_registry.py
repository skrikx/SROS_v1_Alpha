"""
Test Adapter Registry

Tests for adapter registration, selection, and tenant-aware routing.
"""
import pytest
from sros.adapters.registry import AdapterRegistry
from sros.adapters.base import ModelAdapter, AdapterResult, AdapterError


class MockModelAdapter(ModelAdapter):
    """Mock model adapter for testing."""
    
    def initialize(self):
        self._initialized = True
        return True
    
    def health_check(self):
        return True
    
    def get_metadata(self):
        return {"name": self.name, "type": "model"}
    
    def generate(self, prompt, tools=None, context=None, stream=False, **kwargs):
        return AdapterResult(
            success=True,
            data={"mock": True},
            text=f"Mock response to: {prompt}"
        )
    
    def count_tokens(self, text):
        return len(text) // 4
    
    def estimate_cost(self, prompt_tokens, completion_tokens):
        return 0.0


class TestAdapterRegistry:
    """Test suite for adapter registry."""
    
    @pytest.fixture
    def registry(self):
        """Create fresh registry."""
        return AdapterRegistry()
    
    def test_register_adapter(self, registry):
        """Test registering an adapter."""
        registry.register("model", "mock", MockModelAdapter)
        
        adapters = registry.list_adapters("model")
        assert "mock" in adapters["model"]
    
    def test_get_adapter(self, registry):
        """Test getting an adapter instance."""
        registry.register("model", "mock", MockModelAdapter)
        
        adapter = registry.get_adapter("model", "mock")
        assert isinstance(adapter, MockModelAdapter)
        assert adapter._initialized
    
    def test_get_adapter_caching(self, registry):
        """Test adapter instance caching."""
        registry.register("model", "mock", MockModelAdapter)
        
        adapter1 = registry.get_adapter("model", "mock")
        adapter2 = registry.get_adapter("model", "mock")
        
        assert adapter1 is adapter2
    
    def test_get_adapter_tenant_override(self, registry):
        """Test tenant-specific adapter selection."""
        registry.register("model", "mock1", MockModelAdapter)
        registry.register("model", "mock2", MockModelAdapter)
        
        # Set tenant override
        registry.set_config({
            "tenant1.model.default": "mock2"
        })
        
        adapter = registry.get_adapter("model", "default", tenant="tenant1")
        assert adapter.name == "mock2"
    
    def test_get_adapter_fallback(self, registry):
        """Test fallback when adapter not found."""
        registry.register("model", "mock", MockModelAdapter)
        
        registry.set_config({
            "fallbacks": {
                "model": ["mock"]
            }
        })
        
        # Request nonexistent adapter, should fallback to mock
        adapter = registry.get_adapter("model", "nonexistent")
        assert adapter.name == "mock"
    
    def test_get_adapter_not_found(self, registry):
        """Test error when adapter not found and no fallback."""
        with pytest.raises(AdapterError, match="Adapter not found"):
            registry.get_adapter("model", "nonexistent")
    
    def test_list_adapters(self, registry):
        """Test listing all adapters."""
        registry.register("model", "mock1", MockModelAdapter)
        registry.register("model", "mock2", MockModelAdapter)
        
        adapters = registry.list_adapters()
        assert "model" in adapters
        assert len(adapters["model"]) == 2
    
    def test_clear_instances(self, registry):
        """Test clearing cached instances."""
        registry.register("model", "mock", MockModelAdapter)
        
        adapter1 = registry.get_adapter("model", "mock")
        registry.clear_instances()
        adapter2 = registry.get_adapter("model", "mock")
        
        assert adapter1 is not adapter2
