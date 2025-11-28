"""
Evolution Package

Self-improvement system for SROS (Ouroboros).
"""
from .ouroboros import OuroborosLoop, EvolutionProposal, LoopStage
from .observer import Observer
from .analyzer import Analyzer
from .proposer import Proposer
from .safeguards import Safeguards

__all__ = [
    'OuroborosLoop',
    'EvolutionProposal',
    'LoopStage',
    'Observer',
    'Analyzer',
    'Proposer',
    'Safeguards',
]
