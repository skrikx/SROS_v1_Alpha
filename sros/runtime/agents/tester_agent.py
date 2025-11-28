"""
Tester Agent

Test generation and validation agent for SROS evolution.
"""
from typing import Dict, Any
from .agent_base import AgentBase
import logging

logger = logging.getLogger(__name__)


class SROSTesterAgent(AgentBase):
    """
    Tester Agent - Test generation and validation.
    
    Responsibilities:
    - Generate unit tests
    - Create integration tests
    - Validate code changes
    - Run test suites
    """
    
    def __init__(self, event_bus=None, adapter=None, config: Dict[str, Any] = None):
        super().__init__(
            agent_id="tester.sros.v1",
            name="SROS Tester",
            role="Test Engineer",
            event_bus=event_bus,
            adapter=adapter,
            config=config
        )
    
    def act(self, observation: str, context: Dict[str, Any] = None) -> str:
        """
        Generate tests or validate code.
        
        Args:
            observation: Code to test or test generation request
            context: Optional context (code structure, requirements)
        
        Returns:
            Generated tests or validation results
        """
        self.publish_event("agent.thinking", {"task": observation[:100]})
        
        if not self.adapter:
            logger.error("No adapter available for Tester agent")
            return "[ERROR] Tester agent requires a model adapter to function."
        
        try:
            prompt = self._build_tester_prompt(observation, context)
            
            result = self.adapter.generate(
                prompt,
                context={"system_prompt": "You are an expert test engineer specializing in pytest."},
                temperature=0.4,
                max_tokens=3072
            )
            
            if result.success:
                response = result.text
                
                # Log cost
                logger.info(f"Tester generation cost: ${result.cost:.6f} ({result.tokens['total']} tokens)")
                
                self.publish_event("agent.acted", {
                    "response": response[:100],
                    "cost": result.cost,
                    "tokens": result.tokens['total']
                })
                
                return response
            else:
                logger.error(f"Tester generation failed: {result.error}")
                return f"[ERROR] Test generation failed: {result.error}"
                
        except Exception as e:
            logger.error(f"Tester agent error: {e}")
            return f"[ERROR] Unexpected error: {e}"
    
    def _build_tester_prompt(self, observation: str, context: Dict[str, Any] = None) -> str:
        """Build prompt for test generation."""
        
        context_str = ""
        if context:
            if "code" in context:
                context_str += f"\n\nCode to Test:\n```python\n{context['code']}\n```"
            if "requirements" in context:
                context_str += f"\n\nRequirements:\n{context['requirements']}"
        
        prompt = f"""You are the SROS Tester Agent, responsible for generating comprehensive pytest tests.

Testing Standards:
- Use pytest framework
- Test happy path and edge cases
- Include fixtures where appropriate
- Test error conditions
- Make tests deterministic
- Add clear docstrings

Your Task:
{observation}
{context_str}

Please provide:

1. **Unit Tests with pytest**
   - Test class with descriptive name
   - Multiple test methods
   - Clear test names (test_feature_scenario)

2. **Edge Case Coverage**
   - Boundary conditions
   - Invalid inputs
   - Error scenarios

3. **Fixtures and Mocks**
   - pytest fixtures for setup
   - Mocks for external dependencies

4. **Clear Documentation**
   - Docstrings for test class and methods
   - Comments for complex assertions

Output pytest-compatible test code in markdown code blocks with ```python."""
        
        return prompt

