import pytest

from risk import (
    FixedPercentageStopLoss,
    FixedPriceOffsetStopLoss,
    RiskConfig,
    RiskManager,
    STOP_LOSS_REGISTRY,
    TrailingStopLoss,
    FixedPercentageTakeProfit,
    FixedAmountTakeProfit,
    TAKE_PROFIT_REGISTRY,
)


# ── RiskConfig ───────────────────────────────────────────────


def test_risk_config_accepts_stop_loss_type_and_parameters():
    """
    RiskConfig should store a valid type and parameters.
    """

    risk_config = RiskConfig(
        stop_loss_type="fixed_percentage",
        stop_loss_parameters={"percent": 0.05},
    )

    assert risk_config.stop_loss_type == "fixed_percentage"
    assert risk_config.stop_loss_parameters == {"percent": 0.05}


def test_risk_config_defaults_to_no_stop_loss():
    """
    Default RiskConfig should have no stop-loss configured.
    """

    risk_config = RiskConfig()

    assert risk_config.stop_loss_type is None
    assert risk_config.stop_loss_parameters is None


def test_risk_config_rejects_type_without_parameters():
    """
    Setting a type without parameters should fail clearly.
    """

    with pytest.raises(
        ValueError,
        match="stop_loss_parameters are required",
    ):
        RiskConfig(stop_loss_type="fixed_percentage")


def test_risk_config_rejects_type_with_empty_parameters():
    """
    Setting a type with an empty parameters dict should fail.
    """

    with pytest.raises(
        ValueError,
        match="stop_loss_parameters are required",
    ):
        RiskConfig(
            stop_loss_type="fixed_percentage",
            stop_loss_parameters={},
        )


# ── FixedPercentageStopLoss ──────────────────────────────────


def test_fixed_percentage_triggers_at_or_below_threshold():
    """
    A long trade should stop when price falls to the configured threshold.
    """

    rule = FixedPercentageStopLoss(percent=0.05)

    assert rule.should_stop(
        entry_price=100,
        current_price=95,
    ) is True


def test_fixed_percentage_does_not_trigger_above_threshold():
    """
    A long trade should remain open while price is above the threshold.
    """

    rule = FixedPercentageStopLoss(percent=0.05)

    assert rule.should_stop(
        entry_price=100,
        current_price=95.01,
    ) is False


def test_fixed_percentage_get_stop_price():
    """
    get_stop_price should return entry_price * (1 - percent).
    """

    rule = FixedPercentageStopLoss(percent=0.05)

    assert rule.get_stop_price(100) == 95


@pytest.mark.parametrize("percent", [0, -0.01])
def test_fixed_percentage_rejects_non_positive_percent(percent):
    """
    Percent must be positive.
    """

    with pytest.raises(
        ValueError,
        match="percent must be greater than zero",
    ):
        FixedPercentageStopLoss(percent=percent)


# ── FixedPriceOffsetStopLoss ──────────────────────────────


def test_fixed_price_offset_triggers_at_or_below_threshold():
    """
    Stop should fire when current price is at or below entry - offset.
    """

    rule = FixedPriceOffsetStopLoss(offset=50)

    assert rule.should_stop(entry_price=500, current_price=450) is True
    assert rule.should_stop(entry_price=500, current_price=449) is True


def test_fixed_price_offset_does_not_trigger_above_threshold():
    """
    Stop should not fire while price is above entry - offset.
    """

    rule = FixedPriceOffsetStopLoss(offset=50)

    assert rule.should_stop(entry_price=500, current_price=451) is False


def test_fixed_price_offset_get_stop_price():
    """
    get_stop_price should return entry_price - offset.
    """

    rule = FixedPriceOffsetStopLoss(offset=50)

    assert rule.get_stop_price(500) == 450
    assert rule.get_stop_price(1000) == 950


@pytest.mark.parametrize("offset", [0, -10])
def test_fixed_price_offset_rejects_non_positive_offset(offset):
    """
    Offset must be positive.
    """

    with pytest.raises(
        ValueError,
        match="offset must be greater than zero",
    ):
        FixedPriceOffsetStopLoss(offset=offset)


# ── TrailingStopLoss ────────────────────────────────────────


def test_trailing_stop_triggers_at_or_below_peak_threshold():
    """
    Stop should fire when current price is at or below peak * (1 - percent).
    """

    rule = TrailingStopLoss(percent=0.10)

    assert rule.should_stop(entry_price=100, current_price=108, peak_price=120) is True
    assert rule.should_stop(entry_price=100, current_price=107.99, peak_price=120) is True


def test_trailing_stop_does_not_trigger_above_peak_threshold():
    """
    Stop should not fire while price is above peak * (1 - percent).
    """

    rule = TrailingStopLoss(percent=0.10)

    assert rule.should_stop(entry_price=100, current_price=109, peak_price=120) is False


def test_trailing_stop_get_stop_price_uses_peak():
    """
    get_stop_price should return peak_price * (1 - percent).
    """

    rule = TrailingStopLoss(percent=0.10)

    assert rule.get_stop_price(100, peak_price=120) == 108
    assert rule.get_stop_price(100, peak_price=150) == 135


def test_trailing_stop_get_stop_price_defaults_to_entry_when_peak_is_none():
    """
    get_stop_price should use entry_price when no peak is supplied.
    """

    rule = TrailingStopLoss(percent=0.10)

    assert rule.get_stop_price(100) == 90


@pytest.mark.parametrize("percent", [0, -0.10])
def test_trailing_stop_rejects_non_positive_percent(percent):
    """
    Percent must be positive.
    """

    with pytest.raises(
        ValueError,
        match="percent must be greater than zero",
    ):
        TrailingStopLoss(percent=percent)


# ── RiskManager ──────────────────────────────────────────────


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


def test_risk_manager_resolves_fixed_percentage():
    """
    RiskManager should resolve and apply the fixed percentage rule.
    """

    risk_manager = RiskManager(
        RiskConfig(
            stop_loss_type="fixed_percentage",
            stop_loss_parameters={"percent": 0.05},
        )
    )

    assert risk_manager.get_stop_loss_price(100) == 95
    assert risk_manager.should_stop(100, 95) is True
    assert risk_manager.should_stop(100, 96) is False


def test_risk_manager_resolves_fixed_price_offset():
    """
    RiskManager should resolve and apply the fixed price offset rule.
    """

    risk_manager = RiskManager(
        RiskConfig(
            stop_loss_type="fixed_price_offset",
            stop_loss_parameters={"offset": 50},
        )
    )

    assert risk_manager.get_stop_loss_price(500) == 450
    assert risk_manager.should_stop(500, 450) is True
    assert risk_manager.should_stop(500, 451) is False


def test_risk_manager_resolves_trailing_stop():
    """
    RiskManager should resolve and apply the trailing stop rule.
    """

    risk_manager = RiskManager(
        RiskConfig(
            stop_loss_type="trailing_stop",
            stop_loss_parameters={"percent": 0.10},
        )
    )

    assert risk_manager.get_stop_loss_price(100, peak_price=120) == 108
    assert risk_manager.should_stop(100, 108, peak_price=120) is True
    assert risk_manager.should_stop(100, 109, peak_price=120) is False


def test_risk_manager_rejects_unknown_type():
    """
    An unknown stop_loss_type should raise a ValueError.
    """

    with pytest.raises(
        ValueError,
        match="Unknown stop_loss_type",
    ):
        RiskManager(
            RiskConfig(
                stop_loss_type="unknown_rule",
                stop_loss_parameters={"x": 1},
            )
        )


def test_risk_manager_rejects_unknown_take_profit_type():
    """
    An unknown take_profit_type should raise a ValueError.
    """

    with pytest.raises(
        ValueError,
        match="Unknown take_profit_type",
    ):
        RiskManager(
            RiskConfig(
                take_profit_type="unknown_rule",
                take_profit_parameters={"x": 1},
            )
        )


def test_risk_manager_resolves_fixed_percentage_take_profit():
    """
    RiskManager should resolve and apply the fixed percentage take-profit rule.
    """

    risk_manager = RiskManager(
        RiskConfig(
            take_profit_type="fixed_percentage",
            take_profit_parameters={"percent": 0.20},
        )
    )

    assert risk_manager.get_take_profit_price(100) == 120
    assert risk_manager.should_take_profit(100, 120) is True
    assert risk_manager.should_take_profit(100, 119.99) is False


def test_risk_manager_take_profit_disabled_without_config():
    """
    Default risk manager should not request take-profit exits.
    """

    risk_manager = RiskManager()

    assert risk_manager.should_take_profit(
        entry_price=100,
        current_price=200,
    ) is False
    assert risk_manager.get_take_profit_price(100) is None


# ── FixedPercentageTakeProfit ────────────────────────────


def test_fixed_percentage_take_profit_triggers_at_or_above_target():
    """
    Take-profit should fire when current price reaches or exceeds target.
    """

    rule = FixedPercentageTakeProfit(percent=0.20)

    assert rule.should_take_profit(entry_price=100, current_price=120) is True
    assert rule.should_take_profit(entry_price=100, current_price=121) is True


def test_fixed_percentage_take_profit_does_not_trigger_below_target():
    """
    Take-profit should not fire while price is below target.
    """

    rule = FixedPercentageTakeProfit(percent=0.20)

    assert rule.should_take_profit(entry_price=100, current_price=119.99) is False


def test_fixed_percentage_take_profit_get_price():
    """
    get_take_profit_price should return entry_price * (1 + percent).
    """

    rule = FixedPercentageTakeProfit(percent=0.20)

    assert rule.get_take_profit_price(100) == 120
    assert rule.get_take_profit_price(500) == 600


@pytest.mark.parametrize("percent", [0, -0.10])
def test_fixed_percentage_take_profit_rejects_non_positive_percent(percent):
    """
    Percent must be positive.
    """

    with pytest.raises(
        ValueError,
        match="percent must be greater than zero",
    ):
        FixedPercentageTakeProfit(percent=percent)


# ── RiskConfig Take Profit ───────────────────────────────


def test_risk_config_accepts_take_profit_type_and_parameters():
    """
    RiskConfig should store take-profit type and parameters.
    """

    risk_config = RiskConfig(
        take_profit_type="fixed_percentage",
        take_profit_parameters={"percent": 0.20},
    )

    assert risk_config.take_profit_type == "fixed_percentage"
    assert risk_config.take_profit_parameters == {"percent": 0.20}


def test_risk_config_rejects_take_profit_type_without_parameters():
    """
    Setting take_profit_type without parameters should fail.
    """

    with pytest.raises(
        ValueError,
        match="take_profit_parameters are required",
    ):
        RiskConfig(take_profit_type="fixed_percentage")


def test_risk_config_accepts_both_stop_loss_and_take_profit():
    """
    RiskConfig should accept both stop-loss and take-profit simultaneously.
    """

    risk_config = RiskConfig(
        stop_loss_type="fixed_percentage",
        stop_loss_parameters={"percent": 0.05},
        take_profit_type="fixed_percentage",
        take_profit_parameters={"percent": 0.20},
    )

    assert risk_config.stop_loss_type == "fixed_percentage"
    assert risk_config.take_profit_type == "fixed_percentage"


# ── Registry ─────────────────────────────────────────────


def test_stop_loss_registry_contains_expected_types():
    """
    STOP_LOSS_REGISTRY should contain all implemented types.
    """

    assert "fixed_percentage" in STOP_LOSS_REGISTRY
    assert "fixed_price_offset" in STOP_LOSS_REGISTRY
    assert "trailing_stop" in STOP_LOSS_REGISTRY


def test_take_profit_registry_contains_expected_types():
    """
    TAKE_PROFIT_REGISTRY should contain all implemented types.
    """

    assert "fixed_percentage" in TAKE_PROFIT_REGISTRY
    assert "fixed_amount" in TAKE_PROFIT_REGISTRY


# ── FixedAmountTakeProfit ─────────────────────────────────


def test_fixed_amount_take_profit_triggers_at_or_above_target():
    """
    Take-profit should fire when current price reaches or exceeds target.
    """

    rule = FixedAmountTakeProfit(amount=15)

    assert rule.should_take_profit(entry_price=100, current_price=115) is True
    assert rule.should_take_profit(entry_price=100, current_price=116) is True


def test_fixed_amount_take_profit_does_not_trigger_below_target():
    """
    Take-profit should not fire while price is below target.
    """

    rule = FixedAmountTakeProfit(amount=15)

    assert rule.should_take_profit(entry_price=100, current_price=114.99) is False


def test_fixed_amount_take_profit_get_price():
    """
    get_take_profit_price should return entry_price + amount.
    """

    rule = FixedAmountTakeProfit(amount=15)

    assert rule.get_take_profit_price(100) == 115
    assert rule.get_take_profit_price(200) == 215


@pytest.mark.parametrize("amount", [0, -10])
def test_fixed_amount_take_profit_rejects_non_positive_amount(amount):
    """
    Amount must be positive.
    """

    with pytest.raises(
        ValueError,
        match="amount must be greater than zero",
    ):
        FixedAmountTakeProfit(amount=amount)
