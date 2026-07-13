"""
Strategy Registry

Maps strategy identifiers to their corresponding implementation
functions.

The Backtest Service uses this registry to dynamically select
the requested trading strategy without depending on individual
strategy modules.
"""

from .sma_crossover import generate_sma_crossover_signals
from .ema_crossover import generate_ema_crossover_signals
from .macd_crossover import generate_macd_crossover_signals
from .rsi_mean_reversion import generate_rsi_mean_reversion_signals


STRATEGY_REGISTRY = {
    "sma_crossover": generate_sma_crossover_signals,
    "ema_crossover": generate_ema_crossover_signals,
    "macd_crossover": generate_macd_crossover_signals,
    "rsi_mean_reversion": generate_rsi_mean_reversion_signals,
}