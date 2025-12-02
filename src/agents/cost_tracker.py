"""
Cost Tracker Service

Tracks API usage, tokens, and costs per provider/model for cost management.
"""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class UsageRecord:
    """Record of a single API call usage"""
    timestamp: datetime
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    call_type: str = "text"  # "text" or "vision"
    metadata: Dict = field(default_factory=dict)


class CostTracker:
    """
    Service for tracking API usage, tokens, and costs.
    
    Tracks usage per provider/model and provides cost summaries.
    Supports budgets and cost monitoring.
    """
    
    # Cost per 1K tokens (approximate, update as needed)
    COST_PER_1K_TOKENS = {
        "openai": {
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "gpt-4-vision": {"input": 10.00, "output": 30.00},
        },
        "anthropic": {
            "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
            "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
        },
        "ollama": {
            "*": {"input": 0.0, "output": 0.0},  # Local models are free
        },
    }
    
    def __init__(self, budget: Optional[float] = None):
        """
        Initialize cost tracker.
        
        Args:
            budget: Optional budget limit (in USD)
        """
        self.budget = budget
        self._usage_records: List[UsageRecord] = []
        self._provider_stats: Dict[str, Dict[str, any]] = defaultdict(lambda: {
            "total_calls": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0.0,
            "vision_calls": 0,
        })
    
    def record_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        call_type: str = "text",
        metadata: Optional[Dict] = None,
    ) -> UsageRecord:
        """
        Record API usage.
        
        Args:
            provider: Provider name (openai, anthropic, ollama)
            model: Model name
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            call_type: Type of call (text or vision)
            metadata: Additional metadata
        
        Returns:
            UsageRecord created
        """
        # Calculate cost
        cost = self._calculate_cost(provider, model, input_tokens, output_tokens)
        
        # Create record
        record = UsageRecord(
            timestamp=datetime.utcnow(),
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            call_type=call_type,
            metadata=metadata or {},
        )
        
        # Store record
        self._usage_records.append(record)
        
        # Update stats
        stats = self._provider_stats[provider]
        stats["total_calls"] += 1
        stats["total_input_tokens"] += input_tokens
        stats["total_output_tokens"] += output_tokens
        stats["total_cost"] += cost
        if call_type == "vision":
            stats["vision_calls"] += 1
        
        # Check budget
        if self.budget and self.get_total_cost() > self.budget:
            raise RuntimeError(
                f"Budget exceeded: ${self.get_total_cost():.2f} > ${self.budget:.2f}"
            )
        
        return record
    
    def _calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate cost for a given usage"""
        provider_costs = self.COST_PER_1K_TOKENS.get(provider, {})
        
        # Check for exact model match
        model_costs = provider_costs.get(model)
        if not model_costs:
            # Check for wildcard (e.g., ollama)
            model_costs = provider_costs.get("*")
        
        if not model_costs:
            # Default to 0 if unknown
            return 0.0
        
        input_cost = (input_tokens / 1000.0) * model_costs.get("input", 0.0)
        output_cost = (output_tokens / 1000.0) * model_costs.get("output", 0.0)
        
        return input_cost + output_cost
    
    def get_total_cost(self) -> float:
        """Get total cost across all providers"""
        return sum(record.cost for record in self._usage_records)
    
    def get_provider_cost(self, provider: str) -> float:
        """Get total cost for a specific provider"""
        return self._provider_stats[provider]["total_cost"]
    
    def get_summary(self) -> Dict:
        """
        Get cost summary.
        
        Returns:
            Dictionary with total costs, per-provider breakdown, usage stats
        """
        total_cost = self.get_total_cost()
        total_calls = len(self._usage_records)
        total_input_tokens = sum(r.input_tokens for r in self._usage_records)
        total_output_tokens = sum(r.output_tokens for r in self._usage_records)
        vision_calls = sum(1 for r in self._usage_records if r.call_type == "vision")
        
        provider_breakdown = {}
        for provider, stats in self._provider_stats.items():
            provider_breakdown[provider] = {
                "total_cost": stats["total_cost"],
                "total_calls": stats["total_calls"],
                "total_input_tokens": stats["total_input_tokens"],
                "total_output_tokens": stats["total_output_tokens"],
                "vision_calls": stats["vision_calls"],
            }
        
        return {
            "total_cost": total_cost,
            "total_calls": total_calls,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "vision_calls": vision_calls,
            "provider_breakdown": provider_breakdown,
            "budget": self.budget,
            "budget_remaining": (self.budget - total_cost) if self.budget else None,
            "budget_exceeded": (self.budget and total_cost > self.budget),
        }
    
    def get_recent_usage(self, limit: int = 10) -> List[UsageRecord]:
        """Get recent usage records"""
        return sorted(
            self._usage_records,
            key=lambda r: r.timestamp,
            reverse=True
        )[:limit]
    
    def reset(self):
        """Reset all tracking data"""
        self._usage_records.clear()
        self._provider_stats.clear()


# Global instance
_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker(budget: Optional[float] = None) -> CostTracker:
    """
    Get or create global cost tracker instance.
    
    Args:
        budget: Optional budget limit (only used on first call)
    
    Returns:
        CostTracker instance
    """
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker(budget=budget)
    return _cost_tracker


def reset_cost_tracker():
    """Reset the global cost tracker"""
    global _cost_tracker
    if _cost_tracker:
        _cost_tracker.reset()



