"""
Proposer Module

Generates concrete improvement proposals from pain points.
"""
from typing import Dict, Any, List
import time
import uuid
import logging
from .ouroboros import EvolutionProposal, LoopStage

logger = logging.getLogger(__name__)


class Proposer:
    """
    Generates improvement proposals.
    
    Uses Builder Agent (when available) to create code changes.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.builder_agent = None  # Will be injected
        self.max_proposals_per_cycle = self.config.get("max_proposals_per_cycle", 3)
    
    def generate_proposals(self, pain_points: List[Dict[str, Any]]) -> List[EvolutionProposal]:
        """
        Generate improvement proposals from pain points.
        
        Args:
            pain_points: Ranked list of improvement opportunities
        
        Returns:
            List of EvolutionProposal objects
        """
        logger.info(f"Generating proposals for top {self.max_proposals_per_cycle} pain points")
        
        proposals = []
        
        # Take top N pain points
        for pain_point in pain_points[:self.max_proposals_per_cycle]:
            proposal = self._create_proposal(pain_point)
            if proposal:
                proposals.append(proposal)
        
        logger.info(f"Generated {len(proposals)} proposals")
        return proposals
    
    def _create_proposal(self, pain_point: Dict[str, Any]) -> EvolutionProposal:
        """Create a proposal from a pain point."""
        
        proposal_id = f"EVOL-{uuid.uuid4().hex[:8]}"
        
        # Generate proposal based on type
        pain_type = pain_point.get("type")
        
        if pain_type == "bugs":
            return self._create_bug_fix_proposal(proposal_id, pain_point)
        elif pain_type == "technical_debt":
            return self._create_refactor_proposal(proposal_id, pain_point)
        elif pain_type == "drift":
            return self._create_performance_proposal(proposal_id, pain_point)
        elif pain_type == "user_feedback":
            return self._create_feature_proposal(proposal_id, pain_point)
        else:
            return self._create_generic_proposal(proposal_id, pain_point)
    
    def _create_bug_fix_proposal(self, proposal_id: str, pain_point: Dict[str, Any]) -> EvolutionProposal:
        """Create a bug fix proposal."""
        
        details = pain_point.get("details", [])
        target_files = list(set(d["file"] for d in details if "file" in d))
        
        return EvolutionProposal(
            id=proposal_id,
            title=f"Fix {pain_point.get('count', 0)} bugs identified in code scan",
            description=pain_point.get("description", ""),
            rationale="Addressing FIXME/BUG comments improves code quality and reliability",
            stage=LoopStage.PROPOSE,
            target_files=target_files,
            created_at=time.time(),
            updated_at=time.time(),
            metadata={
                "pain_point_type": "bugs",
                "priority": pain_point.get("priority", 5),
                "source": pain_point.get("source")
            }
        )
    
    def _create_refactor_proposal(self, proposal_id: str, pain_point: Dict[str, Any]) -> EvolutionProposal:
        """Create a refactoring proposal."""
        
        details = pain_point.get("details", [])
        target_files = list(set(d["file"] for d in details if "file" in d))
        
        return EvolutionProposal(
            id=proposal_id,
            title=f"Refactor {pain_point.get('count', 0)} technical debt items",
            description=pain_point.get("description", ""),
            rationale="Removing HACK/WORKAROUND code improves maintainability",
            stage=LoopStage.PROPOSE,
            target_files=target_files,
            created_at=time.time(),
            updated_at=time.time(),
            metadata={
                "pain_point_type": "technical_debt",
                "priority": pain_point.get("priority", 5)
            }
        )
    
    def _create_performance_proposal(self, proposal_id: str, pain_point: Dict[str, Any]) -> EvolutionProposal:
        """Create a performance improvement proposal."""
        
        component = pain_point.get("component", "unknown")
        
        return EvolutionProposal(
            id=proposal_id,
            title=f"Optimize {component} performance",
            description=pain_point.get("description", ""),
            rationale="Address performance drift detected by MirrorOS",
            stage=LoopStage.PROPOSE,
            target_modules=[component],
            created_at=time.time(),
            updated_at=time.time(),
            metadata={
                "pain_point_type": "drift",
                "priority": pain_point.get("priority", 5),
                "component": component
            }
        )
    
    def _create_feature_proposal(self, proposal_id: str, pain_point: Dict[str, Any]) -> EvolutionProposal:
        """Create a feature/enhancement proposal."""
        
        return EvolutionProposal(
            id=proposal_id,
            title="User-requested enhancement",
            description=pain_point.get("description", ""),
            rationale="Address user feedback",
            stage=LoopStage.PROPOSE,
            created_at=time.time(),
            updated_at=time.time(),
            metadata={
                "pain_point_type": "user_feedback",
                "priority": pain_point.get("priority", 5)
            }
        )
    
    def _create_generic_proposal(self, proposal_id: str, pain_point: Dict[str, Any]) -> EvolutionProposal:
        """Create a generic proposal."""
        
        return EvolutionProposal(
            id=proposal_id,
            title="System improvement",
            description=pain_point.get("description", ""),
            rationale="Address identified pain point",
            stage=LoopStage.PROPOSE,
            created_at=time.time(),
            updated_at=time.time(),
            metadata={
                "pain_point_type": pain_point.get("type"),
                "priority": pain_point.get("priority", 5)
            }
        )
