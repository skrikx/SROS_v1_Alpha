"""
Observer Module

Collects data from MirrorOS, telemetry, and codebase for evolution analysis.
"""
from typing import Dict, Any, List
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Observer:
    """
    Observes the SROS system and collects improvement signals.
    
    Data sources:
    - MirrorOS drift detector
    - Telemetry trends
    - Code TODOs/FIXMEs
    - Manual feedback from codex
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.repo_root = self.config.get("repo_root", "./")
        self.trace_path = self.config.get("trace_path", "./data/traces")
    
    def collect(self) -> Dict[str, Any]:
        """
        Collect all observation data.
        
        Returns:
            Dictionary with observations from all sources
        """
        logger.info("Collecting observations from all sources")
        
        observations = {
            "drift_signals": self._collect_drift_signals(),
            "telemetry_trends": self._collect_telemetry_trends(),
            "code_todos": self._collect_code_todos(),
            "manual_feedback": self._collect_manual_feedback(),
            "test_failures": self._collect_test_failures(),
        }
        
        return observations
    
    def _collect_drift_signals(self) -> List[Dict[str, Any]]:
        """Collect drift detection signals from MirrorOS."""
        logger.debug("Collecting drift signals")
        
        # In production, would query MirrorOS drift detector
        # For now, return mock data
        return [
            {
                "type": "performance_degradation",
                "component": "workflow_engine",
                "severity": "medium",
                "description": "Workflow execution time increased 15% over 7 days"
            },
            {
                "type": "error_rate_increase",
                "component": "adapter_registry",
                "severity": "low",
                "description": "Adapter initialization failures up 5%"
            }
        ]
    
    def _collect_telemetry_trends(self) -> Dict[str, Any]:
        """Collect telemetry trends over time."""
        logger.debug("Collecting telemetry trends")
        
        # In production, would query telemetry database
        return {
            "avg_response_time_ms": 250,
            "error_rate": 0.02,
            "memory_usage_mb": 512,
            "adapter_calls_per_hour": 1200,
            "cost_per_day_usd": 15.50
        }
    
    def _collect_code_todos(self) -> List[Dict[str, Any]]:
        """Scan codebase for TODO, FIXME, HACK comments."""
        logger.debug("Scanning codebase for TODOs")
        
        todos = []
        
        # Scan Python files
        repo_path = Path(self.repo_root)
        for py_file in repo_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line_upper = line.upper()
                        if any(marker in line_upper for marker in ["TODO", "FIXME", "HACK"]):
                            todos.append({
                                "file": str(py_file.relative_to(repo_path)),
                                "line": line_num,
                                "text": line.strip(),
                                "type": self._classify_todo(line_upper)
                            })
            except Exception as e:
                logger.debug(f"Error reading {py_file}: {e}")
        
        logger.info(f"Found {len(todos)} TODO/FIXME/HACK comments")
        return todos
    
    def _classify_todo(self, line: str) -> str:
        """Classify TODO type."""
        if "FIXME" in line or "BUG" in line:
            return "bug"
        elif "HACK" in line or "WORKAROUND" in line:
            return "technical_debt"
        elif "TODO" in line:
            return "enhancement"
        return "unknown"
    
    def _collect_manual_feedback(self) -> List[Dict[str, Any]]:
        """Collect manual feedback from codex or feedback files."""
        logger.debug("Collecting manual feedback")
        
        # In production, would query codex for feedback entries
        return [
            {
                "source": "user_feedback",
                "priority": "high",
                "description": "Need better error messages in adapter failures"
            }
        ]
    
    def _collect_test_failures(self) -> List[Dict[str, Any]]:
        """Collect recent test failures."""
        logger.debug("Collecting test failures")
        
        # In production, would parse test results
        return []
