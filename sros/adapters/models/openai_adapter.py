"""
OpenAI Model Adapter - Full Implementation

Implements the ModelAdapter interface for OpenAI models (GPT-4, GPT-3.5, etc.).
"""
from typing import List, Dict, Any, Optional
import os
import logging
from ..base import ModelAdapter, AdapterResult, AdapterError

logger = logging.getLogger(__name__)


class OpenAIAdapter(ModelAdapter):
    """
    Full implementation of OpenAI model adapter.
    
    Supports:
    - GPT-4, GPT-3.5-turbo, and other OpenAI models
    - Tool calling (function calling)
    - Token counting
    - Cost estimation
    """
    
    # Pricing per 1M tokens
    PRICING = {
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    }
    
    def __init__(self, name: str = "openai", config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.api_key = config.get("api_key") if config else None
        self.model_name = config.get("model", "gpt-4-turbo") if config else "gpt-4-turbo"
        self.client = None
    
    def initialize(self) -> bool:
        """Initialize OpenAI client."""
        try:
            if not self.api_key:
                self.api_key = os.getenv("OPENAI_API_KEY")
            
            if not self.api_key:
                logger.warning("OpenAI API key not found. Adapter will use mock mode.")
                self._initialized = True
                return True
            
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self._initialized = True
                logger.info(f"OpenAI adapter initialized with model: {self.model_name}")
                return True
            except ImportError:
                logger.warning("openai package not installed. Using mock mode.")
                self._initialized = True
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI adapter: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if adapter is healthy."""
        return self._initialized
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return adapter metadata."""
        return {
            "name": self.name,
            "type": "model",
            "provider": "OpenAI",
            "model": self.model_name,
            "capabilities": ["text_generation", "tool_calling", "vision"],
            "initialized": self._initialized,
            "mock_mode": self.client is None
        }
    
    def generate(
        self,
        prompt: str,
        tools: Optional[List[Dict]] = None,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs
    ) -> AdapterResult:
        """Generate text using OpenAI."""
        if not self._initialized:
            raise AdapterError("Adapter not initialized", adapter_type="model")
        
        if self.client is None:
            return self._mock_generate(prompt, tools, context)
        
        try:
            # Build messages
            messages = []
            if context and context.get("system_prompt"):
                messages.append({"role": "system", "content": context["system_prompt"]})
            messages.append({"role": "user", "content": prompt})
            
            # Build request
            request_params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048),
            }
            
            if tools:
                request_params["tools"] = tools
            
            # Generate
            response = self.client.chat.completions.create(**request_params)
            
            # Extract response
            message = response.choices[0].message
            text = message.content or ""
            
            # Get token usage
            usage = response.usage
            tokens = {
                "prompt": usage.prompt_tokens,
                "completion": usage.completion_tokens,
                "total": usage.total_tokens
            }
            
            # Estimate cost
            cost = self.estimate_cost(tokens["prompt"], tokens["completion"])
            
            return AdapterResult(
                success=True,
                data={"response": response},
                text=text,
                tokens=tokens,
                cost=cost,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "model": self.model_name,
                    "provider": "openai"
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return AdapterResult(
                success=False,
                data=None,
                error=str(e),
                metadata={"model": self.model_name}
            )
    
    def _mock_generate(
        self,
        prompt: str,
        tools: Optional[List[Dict]],
        context: Optional[Dict[str, Any]]
    ) -> AdapterResult:
        """Mock generation for testing."""
        text = f"[MOCK OPENAI] Processed prompt: {prompt[:50]}..."
        
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
            cost=0.0,
            finish_reason="stop",
            metadata={"model": self.model_name, "mock": True}
        )
    
    def count_tokens(self, text: str) -> int:
        """Count tokens (approximate)."""
        return len(text) // 4
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost for token usage."""
        pricing = self.PRICING.get(self.model_name, self.PRICING["gpt-4-turbo"])
        
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
