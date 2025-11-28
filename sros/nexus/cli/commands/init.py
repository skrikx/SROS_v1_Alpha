"""
Init CLI Command

Initialize SROS configuration and environment.
"""
import argparse
import os
import yaml

DEFAULT_CONFIG = {
    "system": {
        "name": "sros-instance",
        "version": "1.0.0",
        "environment": "dev"
    },
    "kernel": {
        "tick_rate": 10,
        "log_level": "INFO"
    },
    "memory": {
        "backend": "local",
        "path": "./memory_store"
    }
}

def register_commands(parser: argparse.ArgumentParser):
    """Register init subcommands."""
    # No subcommands for init, it's a leaf command
    pass

def execute(args: argparse.Namespace) -> dict:
    """Execute init command."""
    config_path = "sros_config.yml"
    
    if os.path.exists(config_path):
        return {
            "status": "skipped",
            "message": f"Configuration file {config_path} already exists."
        }
    
    try:
        with open(config_path, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
        
        # Also ensure memory directory exists
        os.makedirs("memory_store", exist_ok=True)
        
        return {
            "status": "success",
            "message": f"Initialized SROS. Created {config_path} and memory_store/."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize: {e}"
        }
