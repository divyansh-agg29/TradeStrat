"""
Tests for the strategy registry.
"""

from strategy import STRATEGY_REGISTRY
from strategy.sma_crossover import (
    generate_sma_crossover_signals,
)


def test_sma_strategy_registered():
    """
    The SMA crossover strategy should exist in the registry.
    """

    assert "sma_crossover" in STRATEGY_REGISTRY


def test_sma_strategy_maps_to_correct_function():
    """
    The registry should map the SMA strategy to its
    implementation function.
    """

    assert (
        STRATEGY_REGISTRY["sma_crossover"]
        is generate_sma_crossover_signals
    )


def test_all_registered_strategies_are_callable():
    """
    Every registered strategy implementation should be callable.
    """

    for strategy_function in STRATEGY_REGISTRY.values():

        assert callable(strategy_function)