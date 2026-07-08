from dataclasses import dataclass

from models.strategy_config import StrategyConfig


@dataclass(frozen=True)
class BacktestRequest:
    """
    Represents a complete backtest request.

    This object is passed into the Backtest Service and contains
    every configuration required to execute a backtest.
    """

    ticker: str
    start_date: str
    end_date: str
    initial_capital: float = 100000.0
    risk_free_rate: float = 0.0
    strategy: StrategyConfig = None