from dataclasses import dataclass


@dataclass(frozen=True)
class RiskConfig:
    """
    Configuration for risk-management rules.

    Uses a type + parameters pattern so that new stop-loss and
    take-profit types can be added without changing this class.

    Attributes
    ----------
    stop_loss_type : str | None
        Key identifying the stop-loss rule (e.g. "fixed_percentage",
        "fixed_price_offset").  None means no stop-loss is applied.

    stop_loss_parameters : dict | None
        Parameters forwarded to the selected stop-loss rule.

    take_profit_type : str | None
        Key identifying the take-profit rule (e.g. "fixed_percentage").
        None means no take-profit is applied.

    take_profit_parameters : dict | None
        Parameters forwarded to the selected take-profit rule.
    """

    stop_loss_type: str | None = None
    stop_loss_parameters: dict | None = None
    take_profit_type: str | None = None
    take_profit_parameters: dict | None = None

    def __post_init__(self) -> None:
        if self.stop_loss_type is not None and not self.stop_loss_parameters:
            raise ValueError(
                "stop_loss_parameters are required when stop_loss_type is set"
            )
        if self.take_profit_type is not None and not self.take_profit_parameters:
            raise ValueError(
                "take_profit_parameters are required when take_profit_type is set"
            )
