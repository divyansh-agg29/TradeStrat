from dataclasses import dataclass


@dataclass(frozen=True)
class PositionSizingConfig:
    """
    Configuration for position sizing rules.

    Uses a type + parameters pattern so that new position sizing
    strategies can be added without changing this class.

    Attributes
    ----------
    sizing_type : str | None
        Key identifying the position sizing rule (e.g. "fixed_percentage",
        "fixed_amount", "fixed_shares", "risk_based", "all_in").
        None means all-in sizing is applied (current default behavior).

    sizing_parameters : dict | None
        Parameters forwarded to the selected position sizing rule.
    """

    sizing_type: str | None = None
    sizing_parameters: dict | None = None

    def __post_init__(self) -> None:
        types_requiring_params = {
            "fixed_percentage",
            "fixed_amount",
            "fixed_shares",
            "risk_based",
        }

        if (
            self.sizing_type is not None
            and self.sizing_type in types_requiring_params
            and not self.sizing_parameters
        ):
            raise ValueError(
                "sizing_parameters are required when sizing_type is set "
                f"to '{self.sizing_type}'"
            )
