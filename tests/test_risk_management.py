import pytest

from risk import FixedStopLossRule, RiskConfig, RiskManager


def test_risk_config_accepts_stop_loss_percentage():
    """
    RiskConfig should store a valid fixed stop-loss percentage.
    """

    risk_config = RiskConfig(
        stop_loss_enabled=True,
        stop_loss_percent=0.05,
    )

    assert risk_config.stop_loss_enabled is True
    assert risk_config.stop_loss_percent == 0.05


def test_risk_config_rejects_enabled_stop_loss_without_percentage():
    """
    Enabling stop loss without a percentage should fail clearly.
    """

    with pytest.raises(
        ValueError,
        match="stop_loss_percent is required",
    ):
        RiskConfig(stop_loss_enabled=True)


@pytest.mark.parametrize("stop_loss_percent", [0, -0.01])
def test_risk_config_rejects_non_positive_stop_loss_percentage(
    stop_loss_percent,
):
    """
    Stop-loss percentages must be positive values.
    """

    with pytest.raises(
        ValueError,
        match="stop_loss_percent must be greater than zero",
    ):
        RiskConfig(stop_loss_percent=stop_loss_percent)


def test_fixed_stop_loss_rule_triggers_at_or_below_threshold():
    """
    A long trade should stop when price falls to the configured threshold.
    """

    rule = FixedStopLossRule(stop_loss_percent=0.05)

    assert rule.should_stop(
        entry_price=100,
        current_price=95,
    ) is True


def test_fixed_stop_loss_rule_does_not_trigger_above_threshold():
    """
    A long trade should remain open while price is above the threshold.
    """

    rule = FixedStopLossRule(stop_loss_percent=0.05)

    assert rule.should_stop(
        entry_price=100,
        current_price=95.01,
    ) is False


def test_risk_manager_is_disabled_without_config():
    """
    Default risk manager mode should not request exits.
    """

    risk_manager = RiskManager()

    assert risk_manager.should_stop(
        entry_price=100,
        current_price=1,
    ) is False
    assert risk_manager.get_stop_loss_price(100) is None


def test_risk_manager_returns_configured_stop_loss_price():
    """
    RiskManager should expose the active fixed stop price.
    """

    risk_manager = RiskManager(
        RiskConfig(
            stop_loss_enabled=True,
            stop_loss_percent=0.05,
        )
    )

    assert risk_manager.get_stop_loss_price(100) == 95
