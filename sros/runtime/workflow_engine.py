from typing import Dict, Any
import asyncio
from ..srxml.parser import SRXMLParser

class WorkflowEngine:
    """
    Executes SRXML Workflows.
    """
    def __init__(self, event_bus, witness):
        self.event_bus = event_bus
        self.witness = witness
        self.parser = SRXMLParser()

    async def execute(self, workflow_def: Any, context: Dict[str, Any] = None):
        """
        Executes a workflow definition.
        """
        # Handle both dict and object (SR8Workflow)
        if hasattr(workflow_def, 'id'):
            workflow_id = workflow_def.id
            steps = workflow_def.steps
        else:
            workflow_id = workflow_def.get("@id", "unknown")
            steps = workflow_def.get("step", [])
            if not isinstance(steps, list):
                steps = [steps]

        print(f"[WorkflowEngine] Starting workflow: {workflow_id}")
        
        self.witness.record("workflow.start", {"workflow_id": workflow_id})
        
        for step in steps:
            # Handle both dict and object (WorkflowStep)
            if hasattr(step, 'id'):
                step_id = step.id
                agent_id = step.agent
                instruction = step.instruction
            else:
                step_id = step.get("@id")
                agent_id = step.get("@agent")
                instruction = step.get("input", {}).get("#text", "")
            
            print(f"  [STEP] {step_id}: {instruction}")
            self.witness.record("workflow.step", {"step_id": step_id, "agent": agent_id})
            
            # Simulate agent execution
            # In a real implementation, we would look up the agent from a registry
            # and call agent.act(). For this harness, we simulate it.
            
            self.event_bus.publish("runtime", "agent.thinking", {"agent": agent_id, "input": instruction})
            
            # Simulate processing time
            await asyncio.sleep(0.1)
            
            response = f"Processed {instruction}"
            self.event_bus.publish("runtime", "agent.acted", {"agent": agent_id, "response": response})
            
        self.witness.record("workflow.end", {"workflow_id": workflow_id})
        print(f"[WorkflowEngine] Workflow {workflow_id} completed.")
