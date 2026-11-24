"""
Risk Rules

Implements stop-loss and take-profit rule classes and their
registries for dynamic resolution by the Risk Manager.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class StopLossRule(ABC):
    """
    Abstract base class for all stop-loss rules.

    Subclasses must implement ``should_stop`` and ``get_stop_price``.
    """

    @abstractmethod
    def should_stop(
        self,
        entry_price: float,
        current_price: float,
        peak_price: float | None = None,
    ) -> bool:
        """Return True when the stop-loss condition is met."""

    @abstractmethod
    def get_stop_price(
        self,
        entry_price: float,
        peak_price: float | None = None,
    ) -> float:
        """Return the stop-loss trigger price."""

    @classmethod
    @abstractmethod
    def ui_metadata(cls) -> dict:
        """Return parameter schema for frontend form generation."""


class TakeProfitRule(ABC):
    """
    Abstract base class for all take-profit rules.

    Subclasses must implement ``should_take_profit`` and
    ``get_take_profit_price``.
    """

    @abstractmethod
    def should_take_profit(
        self,
        entry_price: float,
        current_price: float,
    ) -> bool:
        """Return True when the take-profit condition is met."""

    @abstractmethod
    def get_take_profit_price(
        self,
        entry_price: float,
    ) -> float:
        """Return the take-profit trigger price."""

    @classmethod
    @abstractmethod
    def ui_metadata(cls) -> dict:
        """Return parameter schema for frontend form generation."""


@dataclass(frozen=True)
class FixedPercentageStopLoss(StopLossRule):
    """
    Fixed percentage stop-loss rule.

    For a long position, the stop is triggered when the current price
    falls to entry_price * (1 - percent).
    """

    percent: float

    def __post_init__(self) -> None:
        if self.percent <= 0:
            raise ValueError("percent must be greater than zero")

    def should_stop(
        self,
        entry_price: float,
        current_price: float,
        peak_price: float | None = None,
    ) -> bool:
        """
        Determine whether the current price has hit the stop-loss threshold.
        """

        if entry_price <= 0:
            return False

        return current_price <= self.get_stop_price(entry_price, peak_price)

    def get_stop_price(
        self,
        entry_price: float,
        peak_price: float | None = None,
    ) -> float:
        """
        Return the stop-loss price for the given entry price.
        """

        return entry_price * (1 - self.percent)

    @classmethod
    def ui_metadata(cls):
        return {
            "label": "Fixed Percentage",
            "parameters": [
                {"key": "percent", "label": "Stop Loss %", "type": "number", "default": 5, "min": 0.1, "step": 0.1, "display_scale": 100},
            ],
        }


@dataclass(frozen=True)
class FixedPriceOffsetStopLoss(StopLossRule):
    """
    Fixed price offset stop-loss from entry price.

    For a long position, the stop is triggered when the current price
    falls to entry_price - offset or below.
    """

    offset: float

    def __post_init__(self) -> None:
        if self.offset <= 0:
            raise ValueError("offset must be greater than zero")

    def should_stop(
        self,
        entry_price: float,
        current_price: float,
        peak_price: float | None = None,
    ) -> bool:
        if entry_price <= 0:
            return False
        return current_price <= self.get_stop_price(entry_price, peak_price)

    def get_stop_price(
        self,
        entry_price: float,
        peak_price: float | None = None,
    ) -> float:
        return entry_price - self.offset

    @classmethod
    def ui_metadata(cls):
        return {
            "label": "Fixed Price Offset",
            "parameters": [
                {"key": "offset", "label": "Price Offset", "type": "number", "default": 100, "min": 0.1, "step": 0.1},
            ],
        }


@dataclass(frozen=True)
class TrailingStopLoss(StopLossRule):
    """
    Trailing stop-loss rule.

    For a long position, the stop is triggered when the current price
    falls to peak_price * (1 - percent) or below, where peak_price is the
    highest close observed since entry.
    """

    percent: float

    def __post_init__(self) -> None:
        if self.percent <= 0:
            raise ValueError("percent must be greater than zero")

    def should_stop(
        self,
        entry_price: float,
        current_price: float,
        peak_price: float | None = None,
    ) -> bool:
        if peak_price is None:
            peak_price = entry_price
        if peak_price <= 0:
            return False
        return current_price <= self.get_stop_price(entry_price, peak_price)

    def get_stop_price(
        self,
        entry_price: float,
        peak_price: float | None = None,
    ) -> float:
        if peak_price is None:
            peak_price = entry_price
        return peak_price * (1 - self.percent)

    @classmethod
    def ui_metadata(cls):
        return {
            "label": "Trailing Stop",
            "parameters": [
                {"key": "percent", "label": "Trail %", "type": "number", "default": 5, "min": 0.1, "step": 0.1, "display_scale": 100},
            ],
        }


STOP_LOSS_REGISTRY: dict[str, type[StopLossRule]] = {
    "fixed_percentage": FixedPercentageStopLoss,
    "fixed_price_offset": FixedPriceOffsetStopLoss,
    "trailing_stop": TrailingStopLoss,
}


@dataclass(frozen=True)
class FixedPercentageTakeProfit(TakeProfitRule):
    """
    Fixed percentage take-profit rule.

    For a long position, the take-profit is triggered when the current price
    rises to entry_price * (1 + percent) or above.
    """

    percent: float

    def __post_init__(self) -> None:
        if self.percent <= 0:
            raise ValueError("percent must be greater than zero")

    def should_take_profit(
        self,
        entry_price: float,
        current_price: float,
    ) -> bool:
        """
        Determine whether the current price has hit the take-profit threshold.
        """

        if entry_price <= 0:
            return False

        return current_price >= self.get_take_profit_price(entry_price)

    def get_take_profit_price(
        self,
        entry_price: float,
    ) -> float:
        """
        Return the take-profit price for the given entry price.
        """

        return entry_price * (1 + self.percent)

    @classmethod
    def ui_metadata(cls):
        return {
            "label": "Fixed Percentage",
            "parameters": [
                {"key": "percent", "label": "Take Profit %", "type": "number", "default": 10, "min": 0.1, "step": 0.1, "display_scale": 100},
            ],
        }


@dataclass(frozen=True)
class FixedAmountTakeProfit(TakeProfitRule):
    """
    Fixed amount take-profit rule.

    For a long position, the take-profit is triggered when the current price
    rises to entry_price + amount or above.
    """

    amount: float

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("amount must be greater than zero")

    def should_take_profit(
        self,
        entry_price: float,
        current_price: float,
    ) -> bool:
        if entry_price <= 0:
            return False
        return current_price >= self.get_take_profit_price(entry_price)

    def get_take_profit_price(
        self,
        entry_price: float,
    ) -> float:
        return entry_price + self.amount

    @classmethod
    def ui_metadata(cls):
        return {
            "label": "Fixed Amount",
            "parameters": [
                {"key": "amount", "label": "Take Profit Amount", "type": "number", "default": 100, "min": 0.1, "step": 0.1},
            ],
        }


TAKE_PROFIT_REGISTRY: dict[str, type[TakeProfitRule]] = {
    "fixed_percentage": FixedPercentageTakeProfit,
    "fixed_amount": FixedAmountTakeProfit,
}