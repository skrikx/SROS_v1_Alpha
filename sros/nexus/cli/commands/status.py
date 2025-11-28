"""
Status CLI Commands

Commands for system status.
"""
import argparse
from sros.adapters.registry import get_registry
from sros.governance import CostTracker
from sros.mirroros import TelemetryCollector


def register_commands(parser: argparse.ArgumentParser):
    """Register status subcommands."""
    subparsers = parser.add_subparsers(dest="action", help="Status actions")
    
    # System command
    subparsers.add_parser("system", help="Get system status")
    
    # Adapters command
    subparsers.add_parser("adapters", help="Get adapter status")
    
    # Costs command
    subparsers.add_parser("costs", help="Get cost summary")


def execute(args: argparse.Namespace) -> dict:
    """Execute status command."""
    if args.action == "system" or args.action is None:
        return get_system_status()
    elif args.action == "adapters":
        return get_adapter_status()
    elif args.action == "costs":
        return get_cost_status()
    else:
        return {"error": "Unknown status action"}


def get_system_status() -> dict:
    """Get overall system status."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "tenant": "PlatXP",
        "environment": "dev",
        "components": {
            "kernel": "running",
            "runtime": "ready",
            "governance": "active",
            "mirroros": "observing"
        }
    }


def get_adapter_status() -> dict:
    """Get adapter status."""
    registry = get_registry()
    adapters = registry.list_adapters()
    
    return {
        "status": "success",
        "adapters": adapters
    }


def get_cost_status() -> dict:
    """Get cost status."""
    tracker = CostTracker()
    budget_status = tracker.check_budget()
    usage_report = tracker.get_usage_report()
    
    return {
        "status": "success",
        "budget": budget_status,
        "usage": usage_report
    }
