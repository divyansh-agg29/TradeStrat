"""
Strategy Registry

Maps strategy identifiers to their corresponding strategy classes.

The Backtest Service uses this registry to dynamically select
the requested trading strategy without depending on individual
strategy modules.
"""

from .sma_crossover import SmaStrategy
from .ema_crossover import EmaStrategy
from .macd_crossover import MacdStrategy
from .rsi_mean_reversion import RsiStrategy
from .bb_bounce import BbBounceStrategy
from .base import Strategy


STRATEGY_CLASS_REGISTRY: dict[str, type[Strategy]] = {
    "sma_crossover": SmaStrategy,
    "ema_crossover": EmaStrategy,
    "macd_crossover": MacdStrategy,
    "rsi_mean_reversion": RsiStrategy,
    "bb_bounce": BbBounceStrategy,
}
