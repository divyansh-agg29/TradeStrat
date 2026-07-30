from dataclasses import dataclass


@dataclass(frozen=True)
class RiskConfig:
    """
    Configuration for risk-management rules.

    Uses a type + parameters pattern so that new stop-loss types
    can be added without changing this class.

    Attributes
    ----------
    stop_loss_type : str | None
        Key identifying the stop-loss rule (e.g. "fixed_percentage",
        "absolute_price").  None means no stop-loss is applied.

    stop_loss_parameters : dict | None
        Parameters forwarded to the selected stop-loss rule.
    """

    stop_loss_type: str | None = None
    stop_loss_parameters: dict | None = None

    def __post_init__(self) -> None:
        if self.stop_loss_type is not None and not self.stop_loss_parameters:
            raise ValueError(
                "stop_loss_parameters are required when stop_loss_type is set"
            )
