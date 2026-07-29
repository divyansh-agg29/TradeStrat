from typing import Any

from risk.config import RiskConfig
from risk.rules import FixedStopLossRule


class RiskManager:
    """
    Apply configured risk rules to the current trade state.

    The first implementation supports a single fixed stop-loss rule.
    The interface is intentionally simple so that future rules such as
    take-profit, trailing stops, and sizing can be introduced later.
    """

    def __init__(self, risk_config: RiskConfig | None = None):
        self.risk_config = risk_config
        self._rule = None

        if risk_config is not None and risk_config.stop_loss_enabled:
            self._rule = FixedStopLossRule(
                stop_loss_percent=risk_config.stop_loss_percent
            )

    def should_stop(self, entry_price: float, current_price: float) -> bool:
        """
        Return True when the active risk rule requests an exit.
        """

        if self._rule is None:
            return False

        return self._rule.should_stop(entry_price, current_price)

    def get_stop_loss_price(self, entry_price: float) -> float | None:
        """
        Return the stop-loss price for the configured fixed stop-loss rule.
        """

        if self._rule is None:
            return None

        return entry_price * (1 - self._rule.stop_loss_percent)
