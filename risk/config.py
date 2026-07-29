from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RiskConfig:
    """
    Configuration for risk-management rules.

    The first implementation supports a single fixed stop-loss rule.
    Future versions can add take-profit, trailing stop, sizing, and
    portfolio-level constraints without changing the public shape
    dramatically.
    """

    stop_loss_enabled: bool = False
    stop_loss_percent: float | None = None

    def __post_init__(self) -> None:
        if self.stop_loss_enabled and self.stop_loss_percent is None:
            raise ValueError("stop_loss_percent is required when stop_loss_enabled is True")

        if self.stop_loss_percent is not None and self.stop_loss_percent <= 0:
            raise ValueError("stop_loss_percent must be greater than zero")
