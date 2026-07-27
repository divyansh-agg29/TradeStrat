from dataclasses import dataclass, field
from models.strategy_config import StrategyConfig


@dataclass(frozen=True)
class ComparisonRequest:
    """
    Represents a strategy comparison request.

    Common parameters are shared across all strategies.
    Each strategy entry specifies its own type and parameters.
    """
    ticker: str
    start_date: str
    end_date: str
    initial_capital: float = 100000.0
    risk_free_rate: float = 0.0
    strategies: list[StrategyConfig] = field(default_factory=list)
