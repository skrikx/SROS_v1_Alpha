"""
Analyzer Module

Synthesizes observations into actionable improvement opportunities.
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class Analyzer:
    """
    Analyzes observations and identifies improvement opportunities.
    
    Uses Architect Agent (when available) to synthesize pain points.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.architect_agent = None  # Will be injected
    
    def analyze(self, observations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze observations and rank improvement opportunities.
        
        Args:
            observations: Data from Observer
        
        Returns:
            List of pain points ranked by priority
        """
        logger.info("Analyzing observations for improvement opportunities")
        
        pain_points = []
        
        # Analyze drift signals
        for signal in observations.get("drift_signals", []):
            pain_points.append({
                "type": "drift",
                "priority": self._severity_to_priority(signal.get("severity", "low")),
                "component": signal.get("component"),
                "description": signal.get("description"),
                "source": "mirroros_drift"
            })
        
        # Analyze code TODOs
        todos = observations.get("code_todos", [])
        if todos:
            # Group by type
            bugs = [t for t in todos if t["type"] == "bug"]
            debt = [t for t in todos if t["type"] == "technical_debt"]
            
            if bugs:
                pain_points.append({
                    "type": "bugs",
                    "priority": 8,
                    "count": len(bugs),
                    "description": f"{len(bugs)} FIXME/BUG comments in codebase",
                    "source": "code_scan",
                    "details": bugs[:5]  # Top 5
                })
            
            if debt:
                pain_points.append({
                    "type": "technical_debt",
                    "priority": 5,
                    "count": len(debt),
                    "description": f"{len(debt)} HACK/WORKAROUND comments in codebase",
                    "source": "code_scan",
                    "details": debt[:5]
                })
        
        # Analyze telemetry trends
        telemetry = observations.get("telemetry_trends", {})
        if telemetry.get("error_rate", 0) > 0.05:
            pain_points.append({
                "type": "reliability",
                "priority": 9,
                "description": f"Error rate at {telemetry['error_rate']:.1%}",
                "source": "telemetry"
            })
        
        # Analyze manual feedback
        for feedback in observations.get("manual_feedback", []):
            pain_points.append({
                "type": "user_feedback",
                "priority": self._priority_to_score(feedback.get("priority", "medium")),
                "description": feedback.get("description"),
                "source": "manual"
            })
        
        # Sort by priority (descending)
        pain_points.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        logger.info(f"Identified {len(pain_points)} pain points")
        return pain_points
    
    def _severity_to_priority(self, severity: str) -> int:
        """Convert severity to priority score (0-10)."""
        mapping = {
            "critical": 10,
            "high": 8,
            "medium": 5,
            "low": 3
        }
        return mapping.get(severity.lower(), 5)
    
    def _priority_to_score(self, priority: str) -> int:
        """Convert priority label to score."""
        mapping = {
            "critical": 10,
            "high": 8,
            "medium": 5,
            "low": 3
        }
        return mapping.get(priority.lower(), 5)
