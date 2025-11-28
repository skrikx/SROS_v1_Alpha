"""
Architect Agent

System design and analysis agent for SROS evolution.
"""
from typing import Dict, Any
from .agent_base import AgentBase
import logging

logger = logging.getLogger(__name__)


class ArchitectAgent(AgentBase):
    """
    Architect Agent - System design and analysis.
    
    Responsibilities:
    - Analyze pain points and observations
    - Design system improvements
    - Create design briefs
    - Evaluate architectural trade-offs
    """
    
    def __init__(self, event_bus=None, adapter=None, config: Dict[str, Any] = None):
        super().__init__(
            agent_id="architect.sros.v1",
            name="SROS Architect",
            role="System Architect",
            event_bus=event_bus,
            adapter=adapter,
            config=config
        )
    
    def act(self, observation: str, context: Dict[str, Any] = None) -> str:
        """
        Analyze observations and create design recommendations.
        
        Args:
            observation: Pain points or system observations
            context: Optional context (telemetry, traces, etc.)
        
        Returns:
            Design brief or architectural recommendation
        """
        self.publish_event("agent.thinking", {"observation": observation[:100]})
        
        if not self.adapter:
            logger.error("No adapter available for Architect agent")
            return "[ERROR] Architect agent requires a model adapter to function."
        
        try:
            # Build architect-specific prompt
            prompt = self._build_architect_prompt(observation, context)
            
            # Generate response using Gemini
            result = self.adapter.generate(
                prompt,
                context={"system_prompt": "You are a senior system architect for SROS, an AI operating system."},
                temperature=0.7,
                max_tokens=2048
            )
            
            if result.success:
                response = result.text
                
                # Log cost
                logger.info(f"Architect analysis cost: ${result.cost:.6f} ({result.tokens['total']} tokens)")
                
                self.publish_event("agent.acted", {
                    "response": response[:100],
                    "cost": result.cost,
                    "tokens": result.tokens['total']
                })
                
                return response
            else:
                logger.error(f"Architect generation failed: {result.error}")
                return f"[ERROR] Analysis failed: {result.error}"
                
        except Exception as e:
            logger.error(f"Architect agent error: {e}")
            return f"[ERROR] Unexpected error: {e}"
    
    def _build_architect_prompt(self, observation: str, context: Dict[str, Any] = None) -> str:
        """Build detailed prompt for architectural analysis."""
        
        context_str = ""
        if context:
            if "telemetry" in context:
                context_str += f"\n\nTelemetry Data:\n{context['telemetry']}"
            if "drift_signals" in context:
                context_str += f"\n\nDrift Signals:\n{context['drift_signals']}"
            if "pain_points" in context:
                context_str += f"\n\nPain Points:\n{context['pain_points']}"
        
        prompt = f"""You are the SROS Architect Agent, responsible for system design and analysis.

SROS Architecture Overview:
- Four Planes: Kernel, Runtime, Governance, MirrorOS
- Core Principles: Law 1 (models are adapters), observability, self-improvement
- Components: Agents, Workflows, Memory (short/long/codex), Adapters, Evolution Loop

Your Task:
Analyze the following observation and provide architectural recommendations.

Observation:
{observation}
{context_str}

Please provide a structured analysis with:

1. **Root Cause Analysis**
   - What is the underlying issue?
   - Which SROS components are affected?
   - What are the symptoms vs. root causes?

2. **Proposed Solution Design**
   - High-level architectural approach
   - Which components need changes?
   - How does this align with SROS principles?

3. **Architectural Trade-offs**
   - Benefits of this approach
   - Potential drawbacks or risks
   - Alternative approaches considered

4. **Implementation Approach**
   - Recommended implementation order
   - Dependencies and prerequisites
   - Testing strategy

Be specific, actionable, and grounded in SROS architecture."""
        
        return prompt

