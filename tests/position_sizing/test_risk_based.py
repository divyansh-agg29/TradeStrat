"""
Tests for RiskBasedPositionSizing rule.
"""

import pytest

from position_sizing import RiskBasedPositionSizing


def test_risk_based_basic_calculation():
    """
    Risk 2% of $100k = $2k risk budget.
    Entry $100, stop $95 -> risk/share $5.
    Shares = $2k / $5 = 400.
    """

    rule = RiskBasedPositionSizing(risk_percent=0.02)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
        stop_loss_price=95,
    )

    assert shares == 400


def test_risk_based_limited_by_cash():
    """
    When cash is insufficient for the risk-calculated size, limit to
    what cash can afford.
    """

    rule = RiskBasedPositionSizing(risk_percent=0.02)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=10000,  # Only $10k -> max 100 shares at $100
        current_price=100,
        stop_loss_price=95,
    )

    assert shares == 100  # min(400, 100) = 100


def test_risk_based_fallback_without_stop_loss():
    """
    When no stop-loss price is provided, should fall back to all-in.
    """

    rule = RiskBasedPositionSizing(risk_percent=0.02)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=50000,
        current_price=100,
        stop_loss_price=None,
    )

    assert shares == 500  # All-in: $50k / $100 = 500


def test_risk_based_fallback_when_stop_above_entry():
    """
    When stop-loss is at or above entry, fall back to all-in.
    """

    rule = RiskBasedPositionSizing(risk_percent=0.02)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=50000,
        current_price=100,
        stop_loss_price=105,
    )

    assert shares == 500


def test_risk_based_fallback_when_stop_equals_entry():
    """
    When stop-loss equals entry price, fall back to all-in.
    """

    rule = RiskBasedPositionSizing(risk_percent=0.02)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=50000,
        current_price=100,
        stop_loss_price=100,
    )

    assert shares == 500


def test_risk_based_zero_cash():
    """
    Should return 0 when cash is zero.
    """

    rule = RiskBasedPositionSizing(risk_percent=0.02)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=0,
        current_price=100,
        stop_loss_price=95,
    )

    assert shares == 0


def test_risk_based_zero_price():
    """
    Should return 0 when price is zero.
    """

    rule = RiskBasedPositionSizing(risk_percent=0.02)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=0,
        stop_loss_price=0,
    )

    assert shares == 0


def test_risk_based_zero_portfolio_value():
    """
    Should return 0 when portfolio value is zero.
    """

    rule = RiskBasedPositionSizing(risk_percent=0.02)

    shares = rule.calculate_shares(
        portfolio_value=0,
        cash=50000,
        current_price=100,
        stop_loss_price=95,
    )

    assert shares == 0


@pytest.mark.parametrize("risk_percent", [0, -0.01])
def test_risk_based_rejects_non_positive_risk_percent(risk_percent):
    """
    risk_percent must be positive.
    """

    with pytest.raises(
        ValueError,
        match="risk_percent must be greater than zero",
    ):
        RiskBasedPositionSizing(risk_percent=risk_percent)


def test_risk_based_rejects_risk_percent_over_one():
    """
    risk_percent must not exceed 1.0.
    """

    with pytest.raises(
        ValueError,
        match="risk_percent must not exceed 1.0",
    ):
        RiskBasedPositionSizing(risk_percent=1.5)


def test_risk_based_tight_stop_gives_large_position():
    """
    A tight stop-loss means low risk per share, allowing more shares.
    Risk 2% of $100k = $2k. Entry $100, stop $99 -> $1/share risk.
    Risk-based = $2k / $1 = 2000, but cash-limited to $100k / $100 = 1000.
    """

    rule = RiskBasedPositionSizing(risk_percent=0.02)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
        stop_loss_price=99,
    )

    assert shares == 1000


def test_risk_based_wide_stop_gives_small_position():
    """
    A wide stop-loss means high risk per share, allowing fewer shares.
    Risk 2% of $100k = $2k. Entry $100, stop $50 -> $50/share risk.
    Shares = $2k / $50 = 40.
    """

    rule = RiskBasedPositionSizing(risk_percent=0.02)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
        stop_loss_price=50,
    )

    assert shares == 40
