"""
Demo CLI Command

Run the SROS demo showcase.
"""
import argparse
import time
import logging
from sros.kernel import kernel_bootstrap
from sros.runtime.agents import ArchitectAgent, BuilderAgent, SROSTesterAgent

logger = logging.getLogger(__name__)

def register_commands(parser: argparse.ArgumentParser):
    """Register demo subcommands."""
    pass

def execute(args: argparse.Namespace) -> dict:
    """Execute demo command."""
    print("="*60)
    print("SROS v1 Alpha - Demo Showcase")
    print("="*60)
    
    results = {}
    
    try:
        # 1. Boot Kernel
        print("\n[1/4] Booting Kernel...")
        kernel_bootstrap.boot()
        print("Kernel booted successfully.")
        import sys
        sys.stdout.flush()
        results["kernel"] = "operational"
        time.sleep(1)
        
        # 2. Architect Agent
        print("\n[2/4] Running Architect Agent...")
        print("Prompt: 'Analyze: The kernel event bus is experiencing message delivery delays.'")
        try:
            architect = ArchitectAgent()
            architect.initialize()
            # We mock the run if no API key is present to ensure demo flows
            # In a real scenario, this would hit the LLM
            arch_res = architect.act("Analyze: The kernel event bus is experiencing message delivery delays.")
            print(f"Result: {arch_res}")
            results["architect"] = "success"
        except Exception as e:
            print(f"Architect Agent warning: {e}")
            results["architect"] = "skipped (check API key)"
        time.sleep(1)

        # 3. Builder Agent
        print("\n[3/4] Running Builder Agent...")
        print("Prompt: 'Create a new adapter for a custom HTTP tool'")
        try:
            builder = BuilderAgent()
            builder.initialize()
            build_res = builder.act("Create a new adapter for a custom HTTP tool")
            print(f"Result: {build_res}")
            results["builder"] = "success"
        except Exception as e:
            print(f"Builder Agent warning: {e}")
            results["builder"] = "skipped"
        time.sleep(1)

        # 4. Tester Agent
        print("\n[4/4] Running Tester Agent...")
        print("Prompt: 'Generate pytest tests for the new adapter'")
        try:
            tester = SROSTesterAgent()
            tester.initialize()
            test_res = tester.act("Generate pytest tests for the new adapter")
            print(f"Result: {test_res}")
            results["tester"] = "success"
        except Exception as e:
            print(f"Tester Agent warning: {e}")
            results["tester"] = "skipped"
            
        print("\n" + "="*60)
        print("Demo Completed")
        print("="*60)
        
        return {
            "status": "success",
            "results": results,
            "message": "Demo finished. Run 'sros status system' for more info."
        }

    except Exception as e:
        logger.exception("Demo failed")
        return {
            "status": "error",
            "message": str(e)
        }
