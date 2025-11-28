"""
SR8 Workflow SRXML model.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .srxml_base import SRXMLBase


@dataclass
class WorkflowStep:
    """
    Individual workflow step.
    """
    id: str
    order: int
    instruction: str
    agent: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class WorkflowIdentity:
    """
    Workflow identity block.
    """
    system_name: str
    purpose: str


@dataclass(kw_only=True)
class SR8Workflow(SRXMLBase):
    """
    SR8 Workflow definition.
    
    Represents an SRXML workflow document with steps, checks, and output contracts.
    """
    role: str = ""
    mode: str = ""
    identity: WorkflowIdentity = field(default_factory=lambda: WorkflowIdentity("", ""))
    context: List[str] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    steps: List[WorkflowStep] = field(default_factory=list)
    checks: List[str] = field(default_factory=list)
    output_contract: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.identity, dict):
            self.identity = WorkflowIdentity(**self.identity)
        if self.steps and isinstance(self.steps[0], dict):
            self.steps = [WorkflowStep(**s) if isinstance(s, dict) else s for s in self.steps]
