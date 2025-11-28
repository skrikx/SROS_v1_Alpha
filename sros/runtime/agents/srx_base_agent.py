from typing import List, Dict, Any
import uuid

class SRXBaseAgent:
    """
    Base class for all SRX Agents.
    """
    def __init__(self, name: str, role: str, kernel_context):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.kernel = kernel_context
        self.memory = kernel_context.memory
        self.event_bus = kernel_context.event_bus

    def act(self, observation: str) -> str:
        """
        Main agent loop: Observe -> Think -> Act.
        """
        self.event_bus.publish("runtime", "agent.thinking", {"agent_id": self.id, "observation": observation})
        
        response = ""
        if hasattr(self, 'adapter') and self.adapter:
            result = self.adapter.generate(observation)
            response = result.get("text", "")
        else:
            # Fallback
            response = f"I am {self.name} ({self.role}). I received: {observation}"
        
        self.event_bus.publish("runtime", "agent.acted", {"agent_id": self.id, "response": response})
        return response
