from typing import Dict, Any, List

class ContextBuilder:
    """
    Builds the context window for Agents.
    """
    def __init__(self, kernel_context):
        self.kernel = kernel_context

    def build_context(self, agent_id: str, session_id: str, task: str) -> str:
        """
        Constructs the prompt/context for an agent.
        """
        # 1. Get Session Info
        session = self.kernel.session_manager.get_session(session_id)
        
        # 2. Get Short Term Memory
        # stm = self.kernel.memory.read("short_term", session_id)
        
        # 3. Get Relevant Codex (Placeholder)
        # codex_docs = self.kernel.codex.search("sros_core", task)
        
        # 4. Assemble
        context = f"System: You are an SRX Agent running in SROS v1.\n"
        context += f"Session: {session_id}\n"
        context += f"Task: {task}\n"
        
        return context
