"""
SROS CLI - Main Entry Point

Command-line interface for SROS operations.
"""
import argparse
import sys
import logging
from .commands import kernel, agent, workflow, memory, status, init, demo
from .formatter import Formatter

logger = logging.getLogger(__name__)


class SROSCLI:
    """Main CLI application."""
    
    def __init__(self):
        self.formatter = Formatter()
        self.parser = self._build_parser()
    
    def _build_parser(self) -> argparse.ArgumentParser:
        """Build argument parser."""
        parser = argparse.ArgumentParser(
            prog="sros",
            description="SROS - Sovereign Runtime Operating System",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Enable verbose output"
        )
        
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Init command
        init_parser = subparsers.add_parser("init", help="Initialize SROS configuration")
        init.register_commands(init_parser)

        # Kernel commands
        kernel_parser = subparsers.add_parser("kernel", help="Kernel management")
        kernel.register_commands(kernel_parser)
        
        # Agent commands
        agent_parser = subparsers.add_parser("agent", help="Agent operations")
        agent.register_commands(agent_parser)
        
        # Workflow commands
        workflow_parser = subparsers.add_parser("workflow", help="Workflow execution")
        workflow.register_commands(workflow_parser)
        
        # Memory commands
        memory_parser = subparsers.add_parser("memory", help="Memory operations")
        memory.register_commands(memory_parser)
        
        # Status command
        status_parser = subparsers.add_parser("status", help="System status")
        status.register_commands(status_parser)

        # Demo command
        demo_parser = subparsers.add_parser("run-demo", help="Run SROS demo showcase")
        demo.register_commands(demo_parser)

        # Dashboard command
        dashboard_parser = subparsers.add_parser("dashboard", help="Telemetry dashboard")
        dashboard_parser.add_argument("action", choices=["serve"], help="Action to perform")
        
        return parser
    
    def run(self, args=None):
        """Run CLI with given arguments."""
        parsed_args = self.parser.parse_args(args)
        
        # Configure logging
        if parsed_args.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        
        # Set output format
        self.formatter.json_mode = parsed_args.json
        
        # Execute command
        if not parsed_args.command:
            self.parser.print_help()
            return 0
        
        try:
            if parsed_args.command == "init":
                result = init.execute(parsed_args)
            elif parsed_args.command == "kernel":
                result = kernel.execute(parsed_args)
            elif parsed_args.command == "agent":
                result = agent.execute(parsed_args)
            elif parsed_args.command == "workflow":
                result = workflow.execute(parsed_args)
            elif parsed_args.command == "memory":
                result = memory.execute(parsed_args)
            elif parsed_args.command == "status":
                result = status.execute(parsed_args)
            elif parsed_args.command == "run-demo":
                result = demo.execute(parsed_args)
            elif parsed_args.command == "dashboard":
                if parsed_args.action == "serve":
                    from ..api.server import start_server
                    print("Starting SROS Dashboard on http://localhost:8001...")
                    start_server(port=8001)
                    return 0
            else:
                self.formatter.error(f"Unknown command: {parsed_args.command}")
                return 1
            
            # Format and print result
            self.formatter.output(result)
            return 0
            
        except Exception as e:
            self.formatter.error(f"Error: {e}")
            if parsed_args.verbose:
                import traceback
                traceback.print_exc()
            return 1


def main():
    """CLI entry point."""
    cli = SROSCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
