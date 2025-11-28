"""
Ouroboros - SROS Self-Evolution Loop

The controlled self-improvement system where SROS analyzes its own code,
telemetry, and traces to propose improvements.

CRITICAL: This loop is powerful and dangerous. It must be:
- Sandboxed
- Governed by strict policies
- Subject to human approval gates
- Fully auditable via MirrorOS
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LoopStage(Enum):
    """Stages of the self-evolution loop."""
    OBSERVE = "observe"
    ANALYZE = "analyze"
    PROPOSE = "propose"
    SIMULATE = "simulate"
    REVIEW = "review"
    RECORD = "record"


@dataclass
class EvolutionProposal:
    """
    A proposed change to SROS itself.
    """
    id: str
    title: str
    description: str
    rationale: str
    stage: LoopStage
    
    # Targets
    target_files: List[str] = field(default_factory=list)
    target_modules: List[str] = field(default_factory=list)
    target_modules: List[str] = field(default_factory=list)


class OuroborosLoop:
    """
    The main self-evolution loop controller.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.max_concurrent_proposals = self.config.get("max_concurrent", 5)
        self.require_human_approval = self.config.get("require_approval", True)
        
        # Components (injected)
        self.observer = None
        self.analyzer = None
        self.proposer = None
        self.simulator = None
        self.reviewer = None
        self.recorder = None
        self.directive = None
        
        # State
        self.active_proposals: List[EvolutionProposal] = []
        self.proposal_history: List[EvolutionProposal] = []
    def run_cycle(self) -> List[EvolutionProposal]:
        """
        Run one complete evolution cycle.
        
        Returns:
            List of proposals created/updated in this cycle
        """
        if not self.enabled:
            logger.warning("Ouroboros Loop is disabled")
            return []
        
        if not self._check_safety_constraints():
            logger.error("Safety constraints violated. Aborting cycle.")
            return []
        
        logger.info("Starting Ouroboros evolution cycle")
        
        # Stage 1: Observe
        observations = self._observe()
        
        # Stage 2: Analyze
        pain_points = self._analyze(observations)
        
        # Stage 3: Propose
        proposals = self._propose(pain_points)
        
        # Stage 4: Simulate
        for proposal in proposals:
            self._simulate(proposal)
        
        # Stage 5: Review
        for proposal in proposals:
            self._review(proposal)
        
        # Stage 6: Record
        for proposal in proposals:
            self._record(proposal)
        
        logger.info(f"Evolution cycle complete. {len(proposals)} proposals generated.")
        return proposals
    
    def _observe(self) -> Dict[str, Any]:
        """Stage 1: Collect observations."""
        if not self.observer:
            logger.warning("Observer not configured")
            return {}
        
        logger.info("[OBSERVE] Collecting telemetry, traces, and code signals")
        return self.observer.collect()
    
    def _analyze(self, observations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Stage 2: Analyze observations for improvement opportunities."""
        if not self.analyzer:
            logger.warning("Analyzer not configured")
            return []
        
        logger.info("[ANALYZE] Synthesizing pain points and opportunities")
        return self.analyzer.analyze(observations)
    
    def _propose(self, pain_points: List[Dict[str, Any]]) -> List[EvolutionProposal]:
        """Stage 3: Generate improvement proposals."""
        if not self.proposer:
            logger.warning("Proposer not configured")
            return []
        
        logger.info(f"[PROPOSE] Generating proposals for {len(pain_points)} pain points")
        proposals = self.proposer.generate_proposals(pain_points)
        
        # Governance Check: Filter proposals via Sovereign Directive
        allowed_proposals = []
        for p in proposals:
            decision = self.directive.evaluate_action(
                ActionType.EVOLVE_STRUCTURE,
                {"target": p.target_files, "reason": p.rationale}
            )
            
            if decision.allowed:
                if decision.requires_hassan_approval:
                    p.requires_approval = True
                    logger.info(f"Proposal {p.id} flagged for Sovereign Approval: {decision.reason}")
                allowed_proposals.append(p)
            else:
                logger.warning(f"Proposal {p.id} BLOCKED by Sovereign Directive: {decision.reason}")

        # Add to active proposals
        self.active_proposals.extend(allowed_proposals)
        
        return allowed_proposals
    
    def _simulate(self, proposal: EvolutionProposal):
        """Stage 4: Simulate proposal in sandbox."""
        if not self.simulator:
            logger.warning("Simulator not configured")
            return
        
        logger.info(f"[SIMULATE] Testing proposal: {proposal.id}")
        proposal.simulation_results = self.simulator.run(proposal)
        proposal.stage = LoopStage.SIMULATE
    
    def _review(self, proposal: EvolutionProposal):
        """Stage 5: Human/governance review."""
        if not self.reviewer:
            logger.warning("Reviewer not configured")
            return
        
        logger.info(f"[REVIEW] Submitting proposal for review: {proposal.id}")
        
        if self.require_human_approval:
            # Create review dossier and wait for human approval
            self.reviewer.request_approval(proposal)
        else:
            # Auto-approve if configured (DANGEROUS)
            proposal.approved = True
            proposal.reviewer = "auto"
        
        proposal.stage = LoopStage.REVIEW
    
    def _record(self, proposal: EvolutionProposal):
        """Stage 6: Record to MirrorOS."""
        if not self.recorder:
            logger.warning("Recorder not configured")
            return
        
        logger.info(f"[RECORD] Recording proposal to MirrorOS: {proposal.id}")
        self.recorder.record(proposal)
        
        # Move to history
        self.proposal_history.append(proposal)
        if proposal in self.active_proposals:
            self.active_proposals.remove(proposal)
        
        proposal.stage = LoopStage.RECORD
    
    def _check_safety_constraints(self) -> bool:
        """
        Check safety constraints before running cycle.
        
        Returns:
            True if safe to proceed
        """
        # Check max concurrent proposals
        if len(self.active_proposals) >= self.max_concurrent_proposals:
            logger.warning(f"Max concurrent proposals reached: {len(self.active_proposals)}")
            return False
        
        # Check if loop is in emergency stop state
        if self.config.get("emergency_stop", False):
            logger.error("Emergency stop activated")
            return False
        
        return True
    
    def emergency_stop(self):
        """Immediately halt all evolution activities."""
        logger.critical("EMERGENCY STOP ACTIVATED")
        self.enabled = False
        self.config["emergency_stop"] = True
        
        # Clear active proposals
        self.active_proposals.clear()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current loop status."""
        return {
            "enabled": self.enabled,
            "active_proposals": len(self.active_proposals),
            "total_proposals": len(self.proposal_history),
            "max_concurrent": self.max_concurrent_proposals,
            "require_approval": self.require_human_approval,
            "emergency_stop": self.config.get("emergency_stop", False)
        }
