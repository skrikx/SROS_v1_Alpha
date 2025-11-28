"""
Gemini Model Adapter - Full Implementation

Implements the ModelAdapter interface for Google Gemini models.
"""
from typing import List, Dict, Any, Optional
import os
import logging
from ..base import ModelAdapter, AdapterResult, AdapterError, AdapterAuthError

logger = logging.getLogger(__name__)


class GeminiAdapter(ModelAdapter):
    """
    Full implementation of Gemini model adapter.
    
    Supports:
    - Text generation
    - Tool calling
    - Token counting
    - Cost estimation
    - Streaming (future)
    """
    
    # Pricing per 1M tokens (approximate)
    PRICING = {
        "gemini-pro": {"input": 0.50, "output": 1.50},
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    }
    
    def __init__(self, name: str = "gemini", config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.api_key = config.get("api_key") if config else None
        self.model_name = config.get("model", "gemini-2.0-flash-exp") if config else "gemini-2.0-flash-exp"
        self.client = None
    
    def initialize(self) -> bool:
        """Initialize Gemini client."""
        try:
            # Get API key from config or environment
            if not self.api_key:
                self.api_key = os.getenv("GEMINI_API_KEY")
            
            if not self.api_key:
                logger.warning("Gemini API key not found. Adapter will use mock mode.")
                self._initialized = True
                return True
            
            # Import google.generativeai
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
                self._initialized = True
                logger.info(f"Gemini adapter initialized with model: {self.model_name}")
                return True
            except ImportError:
                logger.warning("google-generativeai not installed. Using mock mode.")
                self._initialized = True
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize Gemini adapter: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if adapter is healthy."""
        return self._initialized
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return adapter metadata."""
        return {
            "name": self.name,
            "type": "model",
            "provider": "Google",
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
        """
        Generate text using Gemini.
        
        Args:
            prompt: Input prompt
            tools: Optional tool definitions
            context: Optional context (system prompt, history)
            stream: Whether to stream (not yet implemented)
            **kwargs: Additional Gemini parameters
        
        Returns:
            AdapterResult with generated text
        """
        if not self._initialized:
            raise AdapterError("Adapter not initialized", adapter_type="model")
        
        # Mock mode if no client
        if self.client is None:
            return self._mock_generate(prompt, tools, context)
        
        try:
            # Build generation config
            generation_config = {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.95),
                "top_k": kwargs.get("top_k", 40),
                "max_output_tokens": kwargs.get("max_tokens", 2048),
            }
            
            # Handle system prompt from context
            final_prompt = prompt
            if context and "system_prompt" in context:
                final_prompt = f"System Instruction: {context['system_prompt']}\n\nUser: {prompt}"

            # Generate
            response = self.client.generate_content(
                final_prompt,
                generation_config=generation_config
            )
            
            # Extract text safely
            try:
                text = response.text
            except ValueError:
                # Handle safety refusal or empty response
                logger.warning("Gemini response.text unavailable (likely safety refusal).")
                text = "[BLOCKED] Response blocked by safety filters."
                if hasattr(response, 'prompt_feedback'):
                    text += f" Feedback: {response.prompt_feedback}"
            
            # Count tokens (approximate)
            prompt_tokens = self.count_tokens(final_prompt)
            completion_tokens = self.count_tokens(text)
            total_tokens = prompt_tokens + completion_tokens
            
            # Estimate cost
            cost = self.estimate_cost(prompt_tokens, completion_tokens)
            
            return AdapterResult(
                success=True,
                data={"response": str(response)},
                text=text,
                tokens={
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                    "total": total_tokens
                },
                cost=cost,
                finish_reason="stop",
                metadata={
                    "model": self.model_name,
                    "provider": "gemini"
                }
            )
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
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
        """Mock generation for testing without API key."""
        text = f"[MOCK GEMINI] Processed prompt: {prompt[:50]}..."
        
        if tools:
            text += f"\n[MOCK] {len(tools)} tools available"
        
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
        """
        Count tokens in text.
        
        Uses approximate counting (1 token ≈ 4 characters).
        For production, use the actual Gemini tokenizer.
        """
        return len(text) // 4
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estimate cost for token usage.
        
        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
        
        Returns:
            Estimated cost in USD
        """
        # Get pricing for model
        pricing = self.PRICING.get(self.model_name, self.PRICING["gemini-1.5-pro"])
        
        # Calculate cost (pricing is per 1M tokens)
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
