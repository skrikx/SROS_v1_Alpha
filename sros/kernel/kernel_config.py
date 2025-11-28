import yaml
import os
from typing import Dict, Any

class KernelConfig:
    """
    Single source of truth for SROS configuration.
    """
    def __init__(self, config_path: str = "sros_config.yml"):
        self.config_path = config_path
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            print(f"WARNING: Config file {self.config_path} not found. Using defaults.")
            return {}
        
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f) or {}

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a config value using dot notation (e.g., "kernel.daemons.telemetry").
        """
        keys = key_path.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def get_section(self, section: str) -> Dict[str, Any]:
        return self._data.get(section, {})
