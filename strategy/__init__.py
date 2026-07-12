from .registry import STRATEGY_REGISTRY
from .sma_crossover import generate_sma_crossover_signals
from.ema_crossover import generate_ema_crossover_signals

__all__ = [
    "generate_sma_crossover_signals",
    "generate_ema_crossover_signals",
    "STRATEGY_REGISTRY",
]