"""
SRX Agent SRXML model.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .srxml_base import SRXMLBase


@dataclass
class AgentIdentity:
    """
    Agent identity block.
    """
    system_name: str
    purpose: str
    persona: Optional[str] = None


@dataclass(kw_only=True)
class SRXAgent(SRXMLBase):
    """
    SRX Agent prompt definition.
    
    Represents an SRXML agent document with role, mode, identity, and objectives.
    """
    role: str = ""
    mode: str = ""  # PLANNING, EXECUTION, VERIFICATION, etc.
    identity: AgentIdentity = field(default_factory=lambda: AgentIdentity("", ""))
    inputs: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    high_level_model: Optional[Dict[str, Any]] = None
    laws: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.identity, dict):
            self.identity = AgentIdentity(**self.identity)
