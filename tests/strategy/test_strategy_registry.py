"""
Tests for the strategy registry.
"""

import pytest

from strategy import STRATEGY_REGISTRY
from strategy.sma_crossover import generate_sma_crossover_signals
from strategy.ema_crossover import generate_ema_crossover_signals
from strategy.macd_crossover import generate_macd_crossover_signals
from strategy.rsi_mean_reversion import generate_rsi_mean_reversion_signals
from strategy.bb_bounce import generate_bb_bounce_signals


EXPECTED_STRATEGIES = {
    "sma_crossover": generate_sma_crossover_signals,
    "ema_crossover": generate_ema_crossover_signals,
    "macd_crossover": generate_macd_crossover_signals,
    "rsi_mean_reversion": generate_rsi_mean_reversion_signals,
    "bb_bounce": generate_bb_bounce_signals,
}


class TestStrategyRegistry:

    def test_contains_exactly_expected_strategies(self):
        """
        The registry should contain all known strategies and nothing extra.
        """

        assert set(STRATEGY_REGISTRY.keys()) == set(EXPECTED_STRATEGIES.keys())

    @pytest.mark.parametrize(
        "name, expected_fn",
        EXPECTED_STRATEGIES.items(),
    )
    def test_strategy_maps_to_correct_function(self, name, expected_fn):
        """
        Each strategy key should map to its implementation function.
        """

        assert STRATEGY_REGISTRY[name] is expected_fn

    def test_all_registered_strategies_are_callable(self):
        """
        Every registered strategy implementation should be callable.
        """

        for strategy_function in STRATEGY_REGISTRY.values():

            assert callable(strategy_function)
