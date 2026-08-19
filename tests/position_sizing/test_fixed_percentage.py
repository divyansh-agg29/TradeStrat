"""
Tests for FixedPercentagePositionSizing rule.
"""

import pytest

from position_sizing import FixedPercentagePositionSizing


def test_fixed_percentage_basic_calculation():
    """
    25% of $100k portfolio = $25k allocation -> 250 shares at $100.
    """

    rule = FixedPercentagePositionSizing(percent=0.25)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 250


def test_fixed_percentage_limited_by_cash():
    """
    When cash is less than the allocation, should use available cash.
    """

    rule = FixedPercentagePositionSizing(percent=0.50)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=10000,  # Only $10k cash, but 50% allocation = $50k
        current_price=100,
    )

    assert shares == 100  # Limited to $10k / $100 = 100 shares


def test_fixed_percentage_zero_cash():
    """
    Should return 0 shares when cash is zero.
    """

    rule = FixedPercentagePositionSizing(percent=0.25)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=0,
        current_price=100,
    )

    assert shares == 0


def test_fixed_percentage_zero_portfolio_value():
    """
    Should return 0 shares when portfolio value is zero.
    """

    rule = FixedPercentagePositionSizing(percent=0.25)

    shares = rule.calculate_shares(
        portfolio_value=0,
        cash=10000,
        current_price=100,
    )

    assert shares == 0


def test_fixed_percentage_zero_price():
    """
    Should return 0 shares when price is zero.
    """

    rule = FixedPercentagePositionSizing(percent=0.25)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=0,
    )

    assert shares == 0


@pytest.mark.parametrize("percent", [0, -0.10])
def test_fixed_percentage_rejects_non_positive_percent(percent):
    """
    Percent must be positive.
    """

    with pytest.raises(
        ValueError,
        match="percent must be greater than zero",
    ):
        FixedPercentagePositionSizing(percent=percent)


def test_fixed_percentage_rejects_percent_over_one():
    """
    Percent must not exceed 1.0.
    """

    with pytest.raises(
        ValueError,
        match="percent must not exceed 1.0",
    ):
        FixedPercentagePositionSizing(percent=1.5)


def test_fixed_percentage_hundred_percent():
    """
    100% should behave like all-in.
    """

    rule = FixedPercentagePositionSizing(percent=1.0)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=50,
    )

    assert shares == 2000


def test_fixed_percentage_small_allocation():
    """
    A very small percentage should produce a small number of shares.
    5% of $100k = $5k allocation -> 50 shares at $100.
    """

    rule = FixedPercentagePositionSizing(percent=0.05)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 50


def test_fixed_percentage_truncates_to_whole_shares():
    """
    Fractional shares should be truncated, not rounded.
    25% of $100k = $25k. At $33/share = 757.57... -> 757 shares.
    """

    rule = FixedPercentagePositionSizing(percent=0.25)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=33,
    )

    assert shares == 757
