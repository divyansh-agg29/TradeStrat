"""
Strategy Registry

Maps strategy identifiers to their corresponding implementation
functions.

The Backtest Service uses this registry to dynamically select
the requested trading strategy without depending on individual
strategy modules.
"""

from . import generate_sma_crossover_signals, generate_ema_crossover_signals


STRATEGY_REGISTRY = {
    "sma_crossover": generate_sma_crossover_signals,
    "ema_crossover": generate_ema_crossover_signals,
}