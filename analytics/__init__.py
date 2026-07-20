"""
Analytics package.

Provides functionality for evaluating the performance of completed
portfolio simulations.
"""

from .metrics import (
    AnalyticsResult,
    BenchmarkMetrics,
    PortfolioMetrics,
    RiskMetrics,
    TradeMetrics,
    analyze_performance,
)

__all__ = [
    "AnalyticsResult",
    "BenchmarkMetrics",
    "PortfolioMetrics",
    "RiskMetrics",
    "TradeMetrics",
    "analyze_performance",
]