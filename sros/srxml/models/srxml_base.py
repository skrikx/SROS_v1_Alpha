"""
Base SRXML data structures.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass(kw_only=True)
class SRXMLLocks:
    """
    SROS execution locks for determinism and safety.
    """
    one_pass_lock: bool = False
    drift_lock: bool = False
    seed_lock: bool = False
    seed: Optional[str] = None


@dataclass(kw_only=True)
class SRXMLBase:
    """
    Base class for all SRXML documents.
    
    All SRXML documents (agents, workflows, policies) inherit these fields.
    """
    id: str
    version: str
    tenant: str
    xmlns: str = "https://srx.sros/schema/v1"
    runtime: Optional[str] = None
    locks: SRXMLLocks = field(default_factory=SRXMLLocks)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.locks, dict):
            self.locks = SRXMLLocks(**self.locks)
