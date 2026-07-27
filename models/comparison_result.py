from dataclasses import dataclass
from typing import Optional
from models.strategy_config import StrategyConfig
from models.backtest_result import BacktestResult
from models.comparison_request import ComparisonRequest


@dataclass
class StrategyResult:
    """
    Result for a single strategy within a comparison.

    On success, backtest_result contains the full BacktestResult.
    On failure, backtest_result is None and error describes what went wrong.
    """
    strategy: StrategyConfig
    success: bool
    error: Optional[str] = None
    backtest_result: Optional[BacktestResult] = None


@dataclass(frozen=True)
class ComparisonResult:
    """
    Aggregated result for a full comparison run.

    Contains the original request (for echoing common parameters)
    and an ordered list of per-strategy results.
    """
    request: ComparisonRequest
    strategy_results: list[StrategyResult]
