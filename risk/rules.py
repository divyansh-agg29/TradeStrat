from dataclasses import dataclass


@dataclass(frozen=True)
class FixedStopLossRule:
    """
    Fixed percentage stop-loss rule.

    For a long position, the stop is triggered when the current price
    falls to entry_price * (1 - stop_loss_percent).
    """

    stop_loss_percent: float

    def should_stop(self, entry_price: float, current_price: float) -> bool:
        """
        Determine whether the current price has hit the stop-loss threshold.
        """

        if entry_price <= 0:
            return False

        stop_price = entry_price * (1 - self.stop_loss_percent)
        return current_price <= stop_price
