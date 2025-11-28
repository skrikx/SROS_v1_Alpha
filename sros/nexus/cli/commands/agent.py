"""
Agent CLI Commands

Commands for agent operations.
"""
import argparse
from sros.runtime.agents import ArchitectAgent, BuilderAgent, SROSTesterAgent


def register_commands(parser: argparse.ArgumentParser):
    """Register agent subcommands."""
    subparsers = parser.add_subparsers(dest="action", help="Agent actions")
    
    # List command
    subparsers.add_parser("list", help="List available agents")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run an agent")
    run_parser.add_argument("agent_name", help="Agent name (architect, builder, tester)")
    run_parser.add_argument("task", help="Task for the agent")


def execute(args: argparse.Namespace) -> dict:
    """Execute agent command."""
    if args.action == "list":
        return list_agents()
    elif args.action == "run":
        return run_agent(args.agent_name, args.task)
    else:
        return {"error": "Unknown agent action"}


def list_agents() -> dict:
    """List available agents."""
    return {
        "agents": [
            {"name": "architect", "role": "System Architect", "status": "available"},
            {"name": "builder", "role": "Code Builder", "status": "available"},
            {"name": "tester", "role": "Test Engineer", "status": "available"}
        ]
    }


def run_agent(agent_name: str, task: str) -> dict:
    """Run an agent with a task."""
    try:
        if agent_name == "architect":
            agent = ArchitectAgent()
        elif agent_name == "builder":
            agent = BuilderAgent()
        elif agent_name == "tester":
            agent = SROSTesterAgent()
        else:
            return {"error": f"Unknown agent: {agent_name}"}
        
        agent.initialize()
        result = agent.act(task)
        
        return {
            "status": "success",
            "agent": agent_name,
            "result": result
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
