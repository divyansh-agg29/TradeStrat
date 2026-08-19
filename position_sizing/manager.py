from position_sizing.config import PositionSizingConfig
from position_sizing.rules import (
    AllInPositionSizing,
    POSITION_SIZING_REGISTRY,
)


class PositionSizingManager:
    """
    Apply configured position sizing rules to calculate trade sizes.

    The manager resolves the active position sizing rule from the
    registry using the type key stored in PositionSizingConfig.
    When no config is provided, defaults to all-in sizing (current
    system behavior).
    """

    def __init__(
        self,
        config: PositionSizingConfig | None = None,
    ):
        self.config = config
        self._rule = None

        if config is None or config.sizing_type is None:
            self._rule = AllInPositionSizing()
        else:
            rule_class = POSITION_SIZING_REGISTRY.get(config.sizing_type)

            if rule_class is None:
                raise ValueError(
                    f"Unknown sizing_type: '{config.sizing_type}'"
                )

            params = config.sizing_parameters or {}
            self._rule = rule_class(**params)

    def calculate_shares_to_buy(
        self,
        portfolio_value: float,
        cash: float,
        current_price: float,
        stop_loss_price: float | None = None,
    ) -> int:
        """
        Calculate the number of shares to buy for the current trade.

        Parameters
        ----------
        portfolio_value : float
            Current total portfolio value (cash + holdings).

        cash : float
            Available cash balance.

        current_price : float
            Current price of the asset.

        stop_loss_price : float | None
            Stop-loss price for risk-based sizing.  Ignored by other
            sizing strategies.

        Returns
        -------
        int
            Number of whole shares to buy.
        """

        return self._rule.calculate_shares(
            portfolio_value=portfolio_value,
            cash=cash,
            current_price=current_price,
            stop_loss_price=stop_loss_price,
        )
