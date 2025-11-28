"""
Governance Policy SRXML model.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .srxml_base import SRXMLBase


@dataclass
class PolicyRule:
    """
    Individual policy rule.
    """
    id: str
    effect: str  # allow, deny, modify
    condition: str
    actions: List[str] = field(default_factory=list)
    priority: int = 100


@dataclass
class PolicyScope:
    """
    Policy scope definition.
    """
    tenants: List[str] = field(default_factory=list)
    agents: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)


@dataclass(kw_only=True)
class GovernancePolicy(SRXMLBase):
    """
    Governance Policy definition.
    
    Represents an SRXML policy document with rules, scope, and enforcement.
    """
    name: str = ""
    description: str = ""
    scope: PolicyScope = field(default_factory=PolicyScope)
    rules: List[PolicyRule] = field(default_factory=list)
    enforcement_mode: str = "strict"  # strict, permissive, audit
    
    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.scope, dict):
            self.scope = PolicyScope(**self.scope)
        if self.rules and isinstance(self.rules[0], dict):
            self.rules = [PolicyRule(**r) if isinstance(r, dict) else r for r in self.rules]
