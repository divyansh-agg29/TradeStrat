"""
Tests for KellyCriterionPositionSizing rule.
"""

import pytest

from position_sizing import KellyCriterionPositionSizing


def test_kelly_basic_calculation():
    """
    Win rate 60%, win/loss ratio 2.0, full Kelly.
    Kelly % = 0.6 - (0.4 / 2.0) = 0.6 - 0.2 = 0.4 (40%).
    Allocation = $100k * 0.4 = $40k.
    Shares = $40k / $100 = 400.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.6,
        win_loss_ratio=2.0,
        kelly_fraction=1.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 400


def test_kelly_half_kelly():
    """
    Win rate 60%, win/loss ratio 2.0, half Kelly (default).
    Kelly % = 0.4, adjusted = 0.4 * 0.5 = 0.2 (20%).
    Allocation = $100k * 0.2 = $20k.
    Shares = $20k / $100 = 200.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.6,
        win_loss_ratio=2.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 200


def test_kelly_quarter_kelly():
    """
    Win rate 60%, win/loss ratio 2.0, quarter Kelly.
    Kelly % = 0.4, adjusted = 0.4 * 0.25 = 0.1 (10%).
    Allocation = $100k * 0.1 = $10k.
    Shares = $10k / $100 = 100.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.6,
        win_loss_ratio=2.0,
        kelly_fraction=0.25,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 100


def test_kelly_limited_by_cash():
    """
    When cash is insufficient, limit to what cash can afford.
    Kelly allocation = $40k but only $5k cash -> 50 shares.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.6,
        win_loss_ratio=2.0,
        kelly_fraction=1.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=5000,
        current_price=100,
    )

    assert shares == 50


def test_kelly_negative_edge_returns_zero():
    """
    When the Kelly formula produces a negative value, return 0.
    Win rate 30%, win/loss ratio 1.0:
    Kelly % = 0.3 - (0.7 / 1.0) = 0.3 - 0.7 = -0.4 -> clamped to 0.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.3,
        win_loss_ratio=1.0,
        kelly_fraction=1.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 0


def test_kelly_breakeven_edge_returns_zero():
    """
    When win rate and loss rate are equal with 1:1 ratio, Kelly is 0.
    Win rate 50%, win/loss ratio 1.0:
    Kelly % = 0.5 - (0.5 / 1.0) = 0.0 -> 0 shares.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.5,
        win_loss_ratio=1.0,
        kelly_fraction=1.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 0


def test_kelly_high_win_rate_low_ratio():
    """
    Win rate 80%, win/loss ratio 0.5, full Kelly.
    Kelly % = 0.8 - (0.2 / 0.5) = 0.8 - 0.4 = 0.4 (40%).
    Allocation = $100k * 0.4 = $40k.
    Shares = $40k / $50 = 800.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.8,
        win_loss_ratio=0.5,
        kelly_fraction=1.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=50,
    )

    assert shares == 800


def test_kelly_low_win_rate_high_ratio():
    """
    Win rate 40%, win/loss ratio 3.0, full Kelly.
    Kelly % = 0.4 - (0.6 / 3.0) = 0.4 - 0.2 = 0.2 (20%).
    Allocation = $100k * 0.2 = $20k.
    Shares = $20k / $100 = 200.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.4,
        win_loss_ratio=3.0,
        kelly_fraction=1.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 200


def test_kelly_zero_cash():
    """
    Should return 0 when cash is zero.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.6,
        win_loss_ratio=2.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=0,
        current_price=100,
    )

    assert shares == 0


def test_kelly_zero_price():
    """
    Should return 0 when price is zero.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.6,
        win_loss_ratio=2.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=0,
    )

    assert shares == 0


def test_kelly_negative_price():
    """
    Should return 0 when price is negative.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.6,
        win_loss_ratio=2.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=-50,
    )

    assert shares == 0


def test_kelly_zero_portfolio_value():
    """
    Should return 0 when portfolio value is zero.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.6,
        win_loss_ratio=2.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=0,
        cash=50000,
        current_price=100,
    )

    assert shares == 0


def test_kelly_negative_cash():
    """
    Should return 0 when cash is negative.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.6,
        win_loss_ratio=2.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=-1000,
        current_price=100,
    )

    assert shares == 0


def test_kelly_stop_loss_ignored():
    """
    Kelly Criterion does not use stop-loss price.
    Result should be the same regardless.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.6,
        win_loss_ratio=2.0,
        kelly_fraction=1.0,
    )

    shares_without = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
        stop_loss_price=None,
    )

    shares_with = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
        stop_loss_price=90,
    )

    assert shares_without == shares_with == 400


def test_kelly_returns_whole_shares():
    """
    Result should always be a whole number of shares (floor).
    Kelly % = 0.4, allocation = $100k * 0.4 = $40k.
    Shares = $40k / $33 = 1212.12... -> 1212.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.6,
        win_loss_ratio=2.0,
        kelly_fraction=1.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=33,
    )

    assert shares == 1212
    assert isinstance(shares, int)


@pytest.mark.parametrize("win_rate", [0, -0.1, 1.0, 1.5])
def test_kelly_rejects_invalid_win_rate(win_rate):
    """
    win_rate must be between 0 and 1 (exclusive).
    """

    with pytest.raises(
        ValueError,
        match="win_rate must be between 0 and 1",
    ):
        KellyCriterionPositionSizing(
            win_rate=win_rate,
            win_loss_ratio=2.0,
        )


@pytest.mark.parametrize("win_loss_ratio", [0, -1.0])
def test_kelly_rejects_non_positive_win_loss_ratio(win_loss_ratio):
    """
    win_loss_ratio must be positive.
    """

    with pytest.raises(
        ValueError,
        match="win_loss_ratio must be greater than zero",
    ):
        KellyCriterionPositionSizing(
            win_rate=0.6,
            win_loss_ratio=win_loss_ratio,
        )


@pytest.mark.parametrize("kelly_fraction", [0, -0.1, 1.5])
def test_kelly_rejects_invalid_kelly_fraction(kelly_fraction):
    """
    kelly_fraction must be between 0 (exclusive) and 1 (inclusive).
    """

    with pytest.raises(
        ValueError,
        match="kelly_fraction must be between 0",
    ):
        KellyCriterionPositionSizing(
            win_rate=0.6,
            win_loss_ratio=2.0,
            kelly_fraction=kelly_fraction,
        )


def test_kelly_accepts_boundary_kelly_fraction():
    """
    kelly_fraction=1.0 is valid (full Kelly).
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.6,
        win_loss_ratio=2.0,
        kelly_fraction=1.0,
    )

    assert rule.kelly_fraction == 1.0


def test_kelly_very_small_edge():
    """
    Win rate 51%, win/loss ratio 1.0, full Kelly.
    Kelly % = 0.51 - (0.49 / 1.0) = 0.02 (2%).
    Allocation = $100k * 0.02 = $2k.
    Shares = $2k / $100 = 20.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.51,
        win_loss_ratio=1.0,
        kelly_fraction=1.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 20


def test_kelly_high_kelly_percent_clamped():
    """
    Extremely favorable odds should clamp Kelly % to 1.0.
    Win rate 99%, win/loss ratio 10.0, full Kelly.
    Kelly % = 0.99 - (0.01 / 10.0) = 0.99 - 0.001 = 0.989.
    Not clamped, allocation = $100k * 0.989 = $98,900.
    Shares = $98,900 / $100 = 989.
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.99,
        win_loss_ratio=10.0,
        kelly_fraction=1.0,
    )

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 989


def test_kelly_default_kelly_fraction_is_half():
    """
    Default kelly_fraction should be 0.5 (half-Kelly).
    """

    rule = KellyCriterionPositionSizing(
        win_rate=0.6,
        win_loss_ratio=2.0,
    )

    assert rule.kelly_fraction == 0.5
