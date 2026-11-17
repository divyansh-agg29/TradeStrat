"""
Strategy Configuration

Defines the StrategyConfig dataclass that specifies which trading
strategy to execute and its associated parameters.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StrategyConfig:
    """
    Configuration for a trading strategy.

    Attributes
    ----------
    type : str
        Identifier of the trading strategy.

    parameters : dict[str, Any]
        Strategy-specific parameters.
    """

    type: str
    parameters: dict[str, Any] = field(default_factory=dict)