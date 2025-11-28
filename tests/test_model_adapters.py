"""
Test Model Adapters

Tests for Gemini, OpenAI, and Local LLM adapters.
"""
import pytest
from sros.adapters.models.gemini_adapter import GeminiAdapter
from sros.adapters.models.openai_adapter import OpenAIAdapter
from sros.adapters.models.local_llm_adapter import LocalLLMAdapter
from sros.adapters.base import AdapterResult


class TestGeminiAdapter:
    """Test suite for Gemini adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create Gemini adapter in mock mode."""
        adapter = GeminiAdapter(config={})
        adapter.initialize()
        return adapter
    
    def test_initialize(self, adapter):
        """Test adapter initialization."""
        assert adapter._initialized
        assert adapter.health_check()
    
    def test_generate(self, adapter):
        """Test text generation."""
        result = adapter.generate("Hello, world!")
        
        assert isinstance(result, AdapterResult)
        assert result.success
        assert result.text is not None
        assert result.tokens is not None
    
    def test_count_tokens(self, adapter):
        """Test token counting."""
        tokens = adapter.count_tokens("Hello, world!")
        assert tokens > 0
    
    def test_estimate_cost(self, adapter):
        """Test cost estimation."""
        cost = adapter.estimate_cost(100, 50)
        assert cost >= 0.0
    
    def test_get_metadata(self, adapter):
        """Test metadata retrieval."""
        metadata = adapter.get_metadata()
        assert metadata["type"] == "model"
        assert metadata["provider"] == "Google"


class TestOpenAIAdapter:
    """Test suite for OpenAI adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create OpenAI adapter in mock mode."""
        adapter = OpenAIAdapter(config={})
        adapter.initialize()
        return adapter
    
    def test_initialize(self, adapter):
        """Test adapter initialization."""
        assert adapter._initialized
    
    def test_generate(self, adapter):
        """Test text generation."""
        result = adapter.generate("Hello, world!")
        
        assert isinstance(result, AdapterResult)
        assert result.success
        assert result.text is not None
    
    def test_get_metadata(self, adapter):
        """Test metadata retrieval."""
        metadata = adapter.get_metadata()
        assert metadata["provider"] == "OpenAI"


class TestLocalLLMAdapter:
    """Test suite for Local LLM adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create Local LLM adapter."""
        adapter = LocalLLMAdapter(config={"model": "llama2"})
        adapter.initialize()
        return adapter
    
    def test_initialize(self, adapter):
        """Test adapter initialization."""
        assert adapter._initialized
    
    def test_generate(self, adapter):
        """Test text generation."""
        result = adapter.generate("Hello, world!")
        
        assert isinstance(result, AdapterResult)
        assert result.success
        assert result.cost == 0.0  # Local models have no cost
    
    def test_get_metadata(self, adapter):
        """Test metadata retrieval."""
        metadata = adapter.get_metadata()
        assert metadata["provider"] == "Local"
        assert metadata["model"] == "llama2"
