"""
Telemetry Collector

Collects and aggregates telemetry data from all SROS components.
"""
from typing import Dict, Any, List
import time
import logging

logger = logging.getLogger(__name__)


class TelemetryCollector:
    """
    Collects telemetry from SROS components.
    
    Features:
    - Metric aggregation
    - Event collection
    - Performance monitoring
    - Dashboard data API
    """
    
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []
        self._start_time = time.time()
    
    def record_metric(
        self,
        source: str,
        metric_name: str,
        value: float,
        tags: Dict[str, str] = None
    ):
        """
        Record a metric.
        
        Args:
            source: Source component
            metric_name: Metric name
            value: Metric value
            tags: Optional tags
        """
        entry = {
            "timestamp": time.time(),
            "source": source,
            "metric": metric_name,
            "value": value,
            "tags": tags or {}
        }
        
        self.metrics.append(entry)
    
    def record_event(
        self,
        source: str,
        event_type: str,
        payload: Dict[str, Any] = None
    ):
        """
        Record an event.
        
        Args:
            source: Source component
            event_type: Event type
            payload: Event payload
        """
        entry = {
            "timestamp": time.time(),
            "source": source,
            "event_type": event_type,
            "payload": payload or {}
        }
        
        self.events.append(entry)
    
    def get_metrics(
        self,
        source: str = None,
        metric_name: str = None,
        since: float = None
    ) -> List[Dict[str, Any]]:
        """
        Query metrics.
        
        Args:
            source: Filter by source
            metric_name: Filter by metric name
            since: Filter by timestamp
        
        Returns:
            List of matching metrics
        """
        results = []
        
        for metric in self.metrics:
            if source and metric["source"] != source:
                continue
            if metric_name and metric["metric"] != metric_name:
                continue
            if since and metric["timestamp"] < since:
                continue
            
            results.append(metric)
        
        return results
    
    def get_events(
        self,
        source: str = None,
        event_type: str = None,
        since: float = None
    ) -> List[Dict[str, Any]]:
        """Query events."""
        results = []
        
        for event in self.events:
            if source and event["source"] != source:
                continue
            if event_type and event["event_type"] != event_type:
                continue
            if since and event["timestamp"] < since:
                continue
            
            results.append(event)
        
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get telemetry summary."""
        uptime = time.time() - self._start_time
        
        # Count metrics by source
        metric_counts = {}
        for metric in self.metrics:
            source = metric["source"]
            metric_counts[source] = metric_counts.get(source, 0) + 1
        
        # Count events by type
        event_counts = {}
        for event in self.events:
            event_type = event["event_type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "uptime_seconds": uptime,
            "total_metrics": len(self.metrics),
            "total_events": len(self.events),
            "metric_counts": metric_counts,
            "event_counts": event_counts
        }
