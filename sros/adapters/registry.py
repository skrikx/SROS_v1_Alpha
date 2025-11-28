"""
Adapter Registry

Manages registration, discovery, and selection of adapters.
Supports tenant-aware and environment-aware adapter selection.
"""
from typing import Dict, Type, Optional, Any
from .base import BaseAdapter, AdapterType, AdapterError
import logging

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """
    Central registry for all SROS adapters.
    
    Supports:
    - Registration by type and name
    - Tenant-aware selection
    - Environment-aware selection
    - Fallback logic
    """
    
    def __init__(self):
        self._adapters: Dict[str, Dict[str, Type[BaseAdapter]]] = {
            "model": {},
            "tool": {},
            "storage": {}
        }
        self._instances: Dict[str, BaseAdapter] = {}
        self._config: Dict[str, Any] = {}
    
    def register(
        self,
        adapter_type: str,
        name: str,
        adapter_class: Type[BaseAdapter]
    ):
        """
        Register an adapter class.
        
        Args:
            adapter_type: Type of adapter (model, tool, storage)
            name: Unique name for this adapter
            adapter_class: The adapter class to register
        """
        if adapter_type not in self._adapters:
            raise ValueError(f"Invalid adapter type: {adapter_type}")
        
        self._adapters[adapter_type][name] = adapter_class
        logger.info(f"Registered {adapter_type} adapter: {name}")
    
    def get_adapter(
        self,
        adapter_type: str,
        name: str,
        tenant: str = "default",
        env: str = "dev",
        config: Dict[str, Any] = None
    ) -> BaseAdapter:
        """
        Get an adapter instance.
        
        Args:
            adapter_type: Type of adapter
            name: Adapter name
            tenant: Tenant ID for tenant-specific selection
            env: Environment (dev, staging, prod)
            config: Optional adapter configuration
        
        Returns:
            Initialized adapter instance
        """
        # Check for tenant-specific override
        tenant_key = f"{tenant}.{adapter_type}.{name}"
        if tenant_key in self._config:
            name = self._config[tenant_key]
        
        # Check for environment-specific override
        env_key = f"{env}.{adapter_type}.{name}"
        if env_key in self._config:
            name = self._config[env_key]
        
        # Get adapter class
        if adapter_type not in self._adapters:
            raise AdapterError(
                f"Unknown adapter type: {adapter_type}",
                adapter_type=adapter_type
            )
        
        if name not in self._adapters[adapter_type]:
            # Try fallback
            fallback_name = self._get_fallback(adapter_type, name)
            if fallback_name:
                logger.warning(f"Adapter {name} not found, using fallback: {fallback_name}")
                name = fallback_name
            else:
                raise AdapterError(
                    f"Adapter not found: {adapter_type}/{name}",
                    adapter_type=adapter_type,
                    details={"name": name, "available": list(self._adapters[adapter_type].keys())}
                )
        
        # Create instance key
        instance_key = f"{adapter_type}.{name}.{tenant}.{env}"
        
        # Return cached instance if exists
        if instance_key in self._instances:
            return self._instances[instance_key]
        
        # Create new instance
        adapter_class = self._adapters[adapter_type][name]
        adapter = adapter_class(name=name, config=config or {})
        
        # Initialize
        if not adapter.initialize():
            raise AdapterError(
                f"Failed to initialize adapter: {adapter_type}/{name}",
                adapter_type=adapter_type
            )
        
        # Cache instance
        self._instances[instance_key] = adapter
        
        return adapter
    
    def set_config(self, config: Dict[str, Any]):
        """
        Set registry configuration.
        
        Config format:
        {
            "tenant1.model.default": "gemini",
            "prod.model.default": "openai",
            "fallbacks": {
                "model": ["gemini", "openai", "local"],
                "tool": ["http"],
                "storage": ["filesystem"]
            }
        }
        """
        self._config = config
    
    def _get_fallback(self, adapter_type: str, name: str) -> Optional[str]:
        """Get fallback adapter name."""
        fallbacks = self._config.get("fallbacks", {}).get(adapter_type, [])
        for fallback in fallbacks:
            if fallback in self._adapters[adapter_type] and fallback != name:
                return fallback
        return None
    
    def list_adapters(self, adapter_type: Optional[str] = None) -> Dict[str, list]:
        """List all registered adapters."""
        if adapter_type:
            return {adapter_type: list(self._adapters.get(adapter_type, {}).keys())}
        return {k: list(v.keys()) for k, v in self._adapters.items()}
    
    def clear_instances(self):
        """Clear all cached adapter instances."""
        self._instances.clear()


# Global registry instance
_global_registry = AdapterRegistry()


def get_registry() -> AdapterRegistry:
    """Get the global adapter registry."""
    return _global_registry
