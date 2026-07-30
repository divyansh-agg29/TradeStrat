from dataclasses import dataclass


@dataclass(frozen=True)
class FixedPercentageStopLoss:
    """
    Fixed percentage stop-loss rule.

    For a long position, the stop is triggered when the current price
    falls to entry_price * (1 - percent).
    """

    percent: float

    def __post_init__(self) -> None:
        if self.percent <= 0:
            raise ValueError("percent must be greater than zero")

    def should_stop(self, entry_price: float, current_price: float) -> bool:
        """
        Determine whether the current price has hit the stop-loss threshold.
        """

        if entry_price <= 0:
            return False

        return current_price <= self.get_stop_price(entry_price)

    def get_stop_price(self, entry_price: float) -> float:
        """
        Return the stop-loss price for the given entry price.
        """

        return entry_price * (1 - self.percent)


@dataclass(frozen=True)
class AbsolutePriceStopLoss:
    """
    Absolute price stop-loss rule.

    The stop is triggered when the current price falls to or below
    a user-specified price level.
    """

    price: float

    def __post_init__(self) -> None:
        if self.price <= 0:
            raise ValueError("price must be greater than zero")

    def should_stop(self, entry_price: float, current_price: float) -> bool:
        """
        Determine whether the current price has hit the stop-loss threshold.
        """

        return current_price <= self.price

    def get_stop_price(self, entry_price: float) -> float:
        """
        Return the configured stop price.
        """

        return self.price


STOP_LOSS_REGISTRY: dict[str, type] = {
    "fixed_percentage": FixedPercentageStopLoss,
    "absolute_price": AbsolutePriceStopLoss,
}
