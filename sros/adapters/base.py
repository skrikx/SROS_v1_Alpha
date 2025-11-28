"""
Base Adapter Interfaces for SROS v1

Enforces Law 1: Models are adapters, SROS is the OS.
All external integrations (models, tools, storage) go through these interfaces.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class AdapterType(Enum):
    """Adapter type classification."""
    MODEL = "model"
    TOOL = "tool"
    STORAGE = "storage"


@dataclass
class AdapterResult:
    """
    Standardized response from any adapter.
    """
    success: bool
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    # Model-specific fields
    text: Optional[str] = None
    tokens: Optional[Dict[str, int]] = None  # {prompt, completion, total}
    cost: Optional[float] = None
    finish_reason: Optional[str] = None
    
    # Tool-specific fields
    status_code: Optional[int] = None
    
    # Storage-specific fields
    size: Optional[int] = None


class AdapterError(Exception):
    """Base exception for all adapter errors."""
    def __init__(self, message: str, adapter_type: str, details: Dict[str, Any] = None):
        super().__init__(message)
        self.adapter_type = adapter_type
        self.details = details or {}


class AdapterTimeoutError(AdapterError):
    """Raised when adapter operation times out."""
    pass


class AdapterAuthError(AdapterError):
    """Raised when adapter authentication fails."""
    pass


class AdapterQuotaError(AdapterError):
    """Raised when adapter quota is exceeded."""
    pass


class BaseAdapter(ABC):
    """
    Base class for all SROS adapters.
    """
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self._initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the adapter. Returns True if successful."""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if adapter is healthy and ready."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Return adapter metadata (version, capabilities, etc.)."""
        pass


class ModelAdapter(BaseAdapter):
    """
    Base interface for LLM model adapters.
    
    All model adapters (Gemini, OpenAI, local LLM) must implement this interface.
    """
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        tools: Optional[List[Dict]] = None,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs
    ) -> AdapterResult:
        """
        Generate text from the model.
        
        Args:
            prompt: The input prompt
            tools: Optional list of tool definitions
            context: Optional context (system prompt, history, etc.)
            stream: Whether to stream the response
            **kwargs: Model-specific parameters
        
        Returns:
            AdapterResult with text, tokens, cost, and metadata
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        pass
    
    @abstractmethod
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost for token usage."""
        pass


class ToolAdapter(BaseAdapter):
    """
    Base interface for tool adapters.
    
    Tools include HTTP clients, browsers, GitHub API, etc.
    """
    
    @abstractmethod
    def invoke(
        self,
        tool_name: str,
        args: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AdapterResult:
        """
        Invoke a tool with given arguments.
        
        Args:
            tool_name: Name of the tool to invoke
            args: Tool arguments
            context: Optional execution context
        
        Returns:
            AdapterResult with tool output
        """
        pass
    
    @abstractmethod
    def list_tools(self) -> List[str]:
        """List available tools."""
        pass


class StorageAdapter(BaseAdapter):
    """
    Base interface for storage adapters.
    
    Storage includes filesystems, S3, GCS, databases, etc.
    """
    
    @abstractmethod
    def get(self, key: str) -> AdapterResult:
        """Retrieve data by key."""
        pass
    
    @abstractmethod
    def put(self, key: str, value: Any, metadata: Dict[str, Any] = None) -> AdapterResult:
        """Store data with key."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> AdapterResult:
        """Delete data by key."""
        pass
    
    @abstractmethod
    def list(self, prefix: str = "") -> AdapterResult:
        """List keys with optional prefix."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass
