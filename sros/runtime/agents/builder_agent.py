"""
Builder Agent

Code generation and modification agent for SROS evolution.
"""
from typing import Dict, Any
from .agent_base import AgentBase
import logging

logger = logging.getLogger(__name__)


class BuilderAgent(AgentBase):
    """
    Builder Agent - Code generation and modification.
    
    Responsibilities:
    - Generate code from design briefs
    - Create patches and diffs
    - Refactor existing code
    - Implement new features
    """
    
    def __init__(self, event_bus=None, adapter=None, config: Dict[str, Any] = None):
        super().__init__(
            agent_id="builder.sros.v1",
            name="SROS Builder",
            role="Code Builder",
            event_bus=event_bus,
            adapter=adapter,
            config=config
        )
    
    def act(self, observation: str, context: Dict[str, Any] = None) -> str:
        """
        Generate or modify code based on design brief.
        
        Args:
            observation: Design brief or code modification request
            context: Optional context (existing code, constraints)
        
        Returns:
            Generated code or patch
        """
        self.publish_event("agent.thinking", {"task": observation[:100]})
        
        if not self.adapter:
            logger.error("No adapter available for Builder agent")
            return "[ERROR] Builder agent requires a model adapter to function."
        
        try:
            prompt = self._build_builder_prompt(observation, context)
            
            result = self.adapter.generate(
                prompt,
                context={"system_prompt": "You are an expert Python developer building SROS components."},
                temperature=0.3,  # Lower temperature for code generation
                max_tokens=4096
            )
            
            if result.success:
                response = result.text
                
                # Log cost
                logger.info(f"Builder generation cost: ${result.cost:.6f} ({result.tokens['total']} tokens)")
                
                self.publish_event("agent.acted", {
                    "response": response[:100],
                    "cost": result.cost,
                    "tokens": result.tokens['total']
                })
                
                return response
            else:
                logger.error(f"Builder generation failed: {result.error}")
                return f"[ERROR] Code generation failed: {result.error}"
                
        except Exception as e:
            logger.error(f"Builder agent error: {e}")
            return f"[ERROR] Unexpected error: {e}"
    
    def _build_builder_prompt(self, observation: str, context: Dict[str, Any] = None) -> str:
        """Build prompt for code generation."""
        
        context_str = ""
        if context:
            if "existing_code" in context:
                context_str += f"\n\nExisting Code:\n```python\n{context['existing_code']}\n```"
            if "requirements" in context:
                context_str += f"\n\nRequirements:\n{context['requirements']}"
            if "constraints" in context:
                context_str += f"\n\nConstraints:\n{context['constraints']}"
        
        prompt = f"""You are the SROS Builder Agent, responsible for generating production-quality Python code.

SROS Coding Standards:
- Use type hints for all functions
- Add comprehensive docstrings
- Follow PEP 8 style guide
- Include error handling
- Add logging where appropriate
- Write clean, maintainable code

Your Task:
{observation}
{context_str}

Please provide:

1. **Complete, Working Code**
   - Fully implemented, not stubs
   - Proper imports
   - Type hints
   - Docstrings

2. **Error Handling**
   - Try/except blocks where needed
   - Meaningful error messages
   - Logging for errors

3. **Code Quality**
   - Clean, readable code
   - Appropriate comments
   - Follow SROS patterns

4. **Testing Considerations**
   - Note any edge cases
   - Suggest test scenarios

Output only the code, properly formatted. Use markdown code blocks with ```python."""
        
        return prompt

