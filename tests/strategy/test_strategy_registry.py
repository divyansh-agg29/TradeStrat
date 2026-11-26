"""
Tests for the strategy registry.
"""

import pytest

from strategy import (
    STRATEGY_CLASS_REGISTRY,
    BbBounceStrategy,
    EmaStrategy,
    MacdStrategy,
    RsiStrategy,
    SmaStrategy,
    Strategy,
)


EXPECTED_STRATEGIES = {
    "sma_crossover": SmaStrategy,
    "ema_crossover": EmaStrategy,
    "macd_crossover": MacdStrategy,
    "rsi_mean_reversion": RsiStrategy,
    "bb_bounce": BbBounceStrategy,
}


class TestStrategyRegistry:

    def test_contains_exactly_expected_strategies(self):
        """
        The registry should contain all known strategies and nothing extra.
        """

        assert set(STRATEGY_CLASS_REGISTRY.keys()) == set(EXPECTED_STRATEGIES.keys())

    @pytest.mark.parametrize(
        "name, expected_class",
        EXPECTED_STRATEGIES.items(),
    )
    def test_strategy_maps_to_correct_class(self, name, expected_class):
        """
        Each strategy key should map to its implementation class.
        """

        assert STRATEGY_CLASS_REGISTRY[name] is expected_class

    def test_all_registered_strategies_subclass_strategy(self):
        """
        Every registered strategy should inherit from the Strategy ABC.
        """

        for strategy_class in STRATEGY_CLASS_REGISTRY.values():

            assert issubclass(strategy_class, Strategy)
