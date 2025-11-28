"""
Cost Tracker

Tracks and enforces cost budgets for model adapter calls.
"""
from typing import Dict, Any, List
import time
import logging

logger = logging.getLogger(__name__)


class CostTracker:
    """
    Tracks costs and enforces budgets.
    
    Features:
    - Per-tenant cost tracking
    - Daily/monthly budgets
    - Cost alerts
    - Usage reporting
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.costs: List[Dict[str, Any]] = []
        self.budgets: Dict[str, float] = {}
        
        # Default budgets
        self.daily_budget = self.config.get("daily_budget", 100.0)  # USD
        self.monthly_budget = self.config.get("monthly_budget", 1000.0)
    
    def record_cost(
        self,
        adapter_name: str,
        cost: float,
        tokens: Dict[str, int],
        tenant: str = "default",
        metadata: Dict[str, Any] = None
    ):
        """
        Record a cost entry.
        
        Args:
            adapter_name: Name of adapter
            cost: Cost in USD
            tokens: Token usage
            tenant: Tenant ID
            metadata: Additional metadata
        """
        entry = {
            "timestamp": time.time(),
            "adapter": adapter_name,
            "cost": cost,
            "tokens": tokens,
            "tenant": tenant,
            "metadata": metadata or {}
        }
        
        self.costs.append(entry)
        logger.debug(f"Recorded cost: ${cost:.4f} for {adapter_name} (tenant: {tenant})")
    
    def get_daily_cost(self, tenant: str = None) -> float:
        """Get total cost for today."""
        today_start = time.time() - (24 * 3600)
        
        total = 0.0
        for entry in self.costs:
            if entry["timestamp"] >= today_start:
                if tenant is None or entry["tenant"] == tenant:
                    total += entry["cost"]
        
        return total
    
    def get_monthly_cost(self, tenant: str = None) -> float:
        """Get total cost for this month."""
        month_start = time.time() - (30 * 24 * 3600)
        
        total = 0.0
        for entry in self.costs:
            if entry["timestamp"] >= month_start:
                if tenant is None or entry["tenant"] == tenant:
                    total += entry["cost"]
        
        return total
    
    def check_budget(self, tenant: str = "default") -> Dict[str, Any]:
        """
        Check if budget limits are exceeded.
        
        Returns:
            Dict with budget status
        """
        daily_cost = self.get_daily_cost(tenant)
        monthly_cost = self.get_monthly_cost(tenant)
        
        daily_exceeded = daily_cost >= self.daily_budget
        monthly_exceeded = monthly_cost >= self.monthly_budget
        
        if daily_exceeded:
            logger.warning(f"Daily budget exceeded for {tenant}: ${daily_cost:.2f} / ${self.daily_budget:.2f}")
        
        if monthly_exceeded:
            logger.warning(f"Monthly budget exceeded for {tenant}: ${monthly_cost:.2f} / ${self.monthly_budget:.2f}")
        
        return {
            "daily_cost": daily_cost,
            "daily_budget": self.daily_budget,
            "daily_exceeded": daily_exceeded,
            "monthly_cost": monthly_cost,
            "monthly_budget": self.monthly_budget,
            "monthly_exceeded": monthly_exceeded
        }
    
    def get_usage_report(self, tenant: str = None) -> Dict[str, Any]:
        """Generate usage report."""
        daily_cost = self.get_daily_cost(tenant)
        monthly_cost = self.get_monthly_cost(tenant)
        
        # Count calls by adapter
        adapter_counts = {}
        for entry in self.costs:
            if tenant is None or entry["tenant"] == tenant:
                adapter = entry["adapter"]
                adapter_counts[adapter] = adapter_counts.get(adapter, 0) + 1
        
        return {
            "daily_cost": daily_cost,
            "monthly_cost": monthly_cost,
            "total_calls": len(self.costs),
            "adapter_counts": adapter_counts,
            "tenant": tenant or "all"
        }
    
    def set_budget(self, daily: float = None, monthly: float = None):
        """Set budget limits."""
        if daily is not None:
            self.daily_budget = daily
        if monthly is not None:
            self.monthly_budget = monthly
        
        logger.info(f"Budgets updated: daily=${self.daily_budget}, monthly=${self.monthly_budget}")
