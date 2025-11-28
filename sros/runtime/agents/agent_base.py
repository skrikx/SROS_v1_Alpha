"""
Enhanced Agent Base

Improved base class for all SRX agents with lifecycle management.
"""
from typing import Dict, Any, Optional
from abc import abstractmethod
import logging
import os

logger = logging.getLogger(__name__)


class AgentBase:
    """
    Enhanced base class for all SRX agents.
    
    Provides:
    - Lifecycle management (initialize, shutdown)
    - Adapter injection
    - EventBus integration
    - State management
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        event_bus=None,
        adapter=None,
        config: Dict[str, Any] = None
    ):
        self.id = agent_id
        self.name = name
        self.role = role
        self.event_bus = event_bus
        self.adapter = adapter
        self.config = config or {}
        
        self._initialized = False
        self._state = {}
        
        logger.info(f"Agent created: {self.name} ({self.role})")
    
    def initialize(self) -> bool:
        """
        Initialize the agent.
        
        Auto-initializes Gemini adapter if not provided and API key available.
        """
        # Auto-initialize adapter if not provided
        if self.adapter is None:
            self.adapter = self._auto_initialize_adapter()
        
        self._initialized = True
        logger.info(f"Agent initialized: {self.name} (adapter: {self.adapter.name if self.adapter else 'none'})")
        return True
    
    def _auto_initialize_adapter(self):
        """Auto-initialize Gemini adapter from environment."""
        try:
            from sros.adapters.models import GeminiAdapter
            
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                adapter = GeminiAdapter(config={
                    "api_key": api_key,
                    "model": "gemini-2.0-flash-exp"
                })
                adapter.initialize()
                logger.info(f"Auto-initialized Gemini adapter for {self.name}")
                return adapter
            else:
                logger.warning(f"No GEMINI_API_KEY found for {self.name}, adapter will be None")
                return None
        except Exception as e:
            logger.error(f"Failed to auto-initialize adapter for {self.name}: {e}")
            return None
    
    def shutdown(self):
        """
        Shutdown the agent and cleanup resources.
        """
        self._initialized = False
        logger.info(f"Agent shutdown: {self.name}")
    
    @abstractmethod
    def act(self, observation: str, context: Dict[str, Any] = None) -> str:
        """
        Process an observation and return an action/response.
        
        Args:
            observation: Input observation or task
            context: Optional context dictionary
        
        Returns:
            Agent's response or action
        """
        pass
    
    def set_adapter(self, adapter):
        """Set or update the model adapter."""
        self.adapter = adapter
        logger.debug(f"Adapter set for {self.name}: {adapter.name if adapter else None}")
    
    def set_event_bus(self, event_bus):
        """Set or update the event bus."""
        self.event_bus = event_bus
    
    def publish_event(self, event_type: str, payload: Dict[str, Any]):
        """Publish an event to the event bus."""
        if self.event_bus:
            self.event_bus.publish("runtime", event_type, {
                "agent_id": self.id,
                "agent_name": self.name,
                **payload
            })
    
    def get_state(self, key: str, default=None):
        """Get agent state value."""
        return self._state.get(key, default)
    
    def set_state(self, key: str, value: Any):
        """Set agent state value."""
        self._state[key] = value
    
    def is_initialized(self) -> bool:
        """Check if agent is initialized."""
        return self._initialized

