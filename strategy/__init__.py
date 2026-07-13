from .registry import STRATEGY_REGISTRY
from .sma_crossover import generate_sma_crossover_signals
from .ema_crossover import generate_ema_crossover_signals
from .macd_crossover import generate_macd_crossover_signals
from .rsi_mean_reversion import generate_rsi_mean_reversion_signals

__all__ = [
    "generate_sma_crossover_signals",
    "generate_ema_crossover_signals",
    "generate_macd_crossover_signals",
    "generate_rsi_mean_reversion_signals",
    "STRATEGY_REGISTRY",
]