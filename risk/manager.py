from risk.config import RiskConfig
from risk.rules import STOP_LOSS_REGISTRY, TAKE_PROFIT_REGISTRY


class RiskManager:
    """
    Apply configured risk rules to the current trade state.

    The manager resolves the active stop-loss and take-profit rules
    from their respective registries using the type keys stored in
    RiskConfig.
    """

    def __init__(self, risk_config: RiskConfig | None = None):
        self.risk_config = risk_config
        self._rule = None
        self._take_profit_rule = None

        if risk_config is not None and risk_config.stop_loss_type is not None:
            rule_class = STOP_LOSS_REGISTRY.get(risk_config.stop_loss_type)

            if rule_class is None:
                raise ValueError(
                    f"Unknown stop_loss_type: '{risk_config.stop_loss_type}'"
                )

            self._rule = rule_class(**risk_config.stop_loss_parameters)

        if risk_config is not None and risk_config.take_profit_type is not None:
            tp_class = TAKE_PROFIT_REGISTRY.get(risk_config.take_profit_type)

            if tp_class is None:
                raise ValueError(
                    f"Unknown take_profit_type: '{risk_config.take_profit_type}'"
                )

            self._take_profit_rule = tp_class(**risk_config.take_profit_parameters)

    def should_stop(
        self,
        entry_price: float,
        current_price: float,
        peak_price: float | None = None,
    ) -> bool:
        """
        Return True when the active risk rule requests an exit.
        """

        if self._rule is None:
            return False

        return self._rule.should_stop(entry_price, current_price, peak_price)

    def get_stop_loss_price(
        self,
        entry_price: float,
        peak_price: float | None = None,
    ) -> float | None:
        """
        Return the stop-loss price for the active rule.
        """

        if self._rule is None:
            return None

        return self._rule.get_stop_price(entry_price, peak_price)

    def should_take_profit(
        self,
        entry_price: float,
        current_price: float,
    ) -> bool:
        """
        Return True when the active take-profit rule requests an exit.
        """

        if self._take_profit_rule is None:
            return False

        return self._take_profit_rule.should_take_profit(entry_price, current_price)

    def get_take_profit_price(
        self,
        entry_price: float,
    ) -> float | None:
        """
        Return the take-profit price for the active rule.
        """

        if self._take_profit_rule is None:
            return None

        return self._take_profit_rule.get_take_profit_price(entry_price)
