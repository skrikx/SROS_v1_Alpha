"""
Local LLM Adapter

Supports local models via Ollama or similar interfaces.
"""
from typing import List, Dict, Any, Optional
import logging
from ..base import ModelAdapter, AdapterResult, AdapterError

logger = logging.getLogger(__name__)


class LocalLLMAdapter(ModelAdapter):
    """
    Adapter for local LLM models (Ollama, llama.cpp, etc.).
    """
    
    def __init__(self, name: str = "local", config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.model_name = config.get("model", "llama2") if config else "llama2"
        self.base_url = config.get("base_url", "http://localhost:11434") if config else "http://localhost:11434"
        self.client = None
    
    def initialize(self) -> bool:
        """Initialize local LLM client."""
        try:
            # For now, use mock mode
            # In production, would connect to Ollama API
            logger.info(f"Local LLM adapter initialized (mock mode) with model: {self.model_name}")
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize local LLM adapter: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if adapter is healthy."""
        return self._initialized
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return adapter metadata."""
        return {
            "name": self.name,
            "type": "model",
            "provider": "Local",
            "model": self.model_name,
            "capabilities": ["text_generation"],
            "initialized": self._initialized,
            "base_url": self.base_url
        }
    
    def generate(
        self,
        prompt: str,
        tools: Optional[List[Dict]] = None,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs
    ) -> AdapterResult:
        """Generate text using local LLM."""
        if not self._initialized:
            raise AdapterError("Adapter not initialized", adapter_type="model")
        
        # Mock implementation
        text = f"[LOCAL LLM - {self.model_name}] Processed: {prompt[:50]}..."
        
        prompt_tokens = self.count_tokens(prompt)
        completion_tokens = self.count_tokens(text)
        
        return AdapterResult(
            success=True,
            data={"mock": True},
            text=text,
            tokens={
                "prompt": prompt_tokens,
                "completion": completion_tokens,
                "total": prompt_tokens + completion_tokens
            },
            cost=0.0,  # Local models have no API cost
            finish_reason="stop",
            metadata={"model": self.model_name, "provider": "local"}
        )
    
    def count_tokens(self, text: str) -> int:
        """Count tokens (approximate)."""
        return len(text) // 4
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Local models have no cost."""
        return 0.0
