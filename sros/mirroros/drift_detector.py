"""
Drift Detector

Detects anomalies and performance drift in SROS operations.
"""
from typing import Dict, Any, List
import time
import logging

logger = logging.getLogger(__name__)


class DriftDetector:
    """
    Detects drift and anomalies in system behavior.
    
    Features:
    - Performance drift detection
    - Error rate monitoring
    - Anomaly detection
    - Trend analysis
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metrics: List[Dict[str, Any]] = []
        self.baselines: Dict[str, float] = {}
        
        # Thresholds
        self.performance_threshold = self.config.get("performance_threshold", 0.20)  # 20% degradation
        self.error_rate_threshold = self.config.get("error_rate_threshold", 0.05)  # 5% error rate
    
    def record_metric(
        self,
        component: str,
        metric_name: str,
        value: float,
        metadata: Dict[str, Any] = None
    ):
        """
        Record a metric value.
        
        Args:
            component: Component name
            metric_name: Metric name
            value: Metric value
            metadata: Additional metadata
        """
        entry = {
            "timestamp": time.time(),
            "component": component,
            "metric": metric_name,
            "value": value,
            "metadata": metadata or {}
        }
        
        self.metrics.append(entry)
        
        # Check for drift
        self._check_drift(component, metric_name, value)
    
    def set_baseline(self, component: str, metric_name: str, value: float):
        """Set baseline value for a metric."""
        key = f"{component}.{metric_name}"
        self.baselines[key] = value
        logger.info(f"Baseline set: {key} = {value}")
    
    def _check_drift(self, component: str, metric_name: str, value: float):
        """Check if metric has drifted from baseline."""
        key = f"{component}.{metric_name}"
        
        if key not in self.baselines:
            # Set first value as baseline
            self.baselines[key] = value
            return
        
        baseline = self.baselines[key]
        
        # Calculate drift percentage
        if baseline > 0:
            drift = (value - baseline) / baseline
            
            if abs(drift) > self.performance_threshold:
                logger.warning(
                    f"Drift detected: {key} = {value} "
                    f"(baseline: {baseline}, drift: {drift:.1%})"
                )
    
    def detect_anomalies(self, component: str = None) -> List[Dict[str, Any]]:
        """
        Detect anomalies in metrics.
        
        Args:
            component: Optional component filter
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Group metrics by component and name
        metric_groups = {}
        for entry in self.metrics:
            if component and entry["component"] != component:
                continue
            
            key = f"{entry['component']}.{entry['metric']}"
            if key not in metric_groups:
                metric_groups[key] = []
            metric_groups[key].append(entry["value"])
        
        # Simple anomaly detection: values outside 2 std deviations
        for key, values in metric_groups.items():
            if len(values) < 10:
                continue
            
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            
            for i, value in enumerate(values[-10:]):  # Check last 10 values
                if abs(value - mean) > 2 * std_dev:
                    anomalies.append({
                        "metric": key,
                        "value": value,
                        "mean": mean,
                        "std_dev": std_dev,
                        "severity": "high" if abs(value - mean) > 3 * std_dev else "medium"
                    })
        
        return anomalies
    
    def get_drift_report(self) -> Dict[str, Any]:
        """Generate drift report."""
        report = {
            "total_metrics": len(self.metrics),
            "baselines": len(self.baselines),
            "anomalies": len(self.detect_anomalies())
        }
        
        return report
