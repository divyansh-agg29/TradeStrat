from dataclasses import dataclass, field
from typing import List

from analytics import AnalyticsResult
from portfolio import SimulationResult


@dataclass(frozen=True)
class BacktestResult:
    """
    Represents the complete output of a backtest.

    This object packages together the outputs produced by the
    Portfolio Simulator and the Analytics Engine.

    It intentionally does not duplicate any information.
    """

    simulation_result: SimulationResult
    analytics_result: AnalyticsResult
    indicator_metadata: List = field(default_factory=list)