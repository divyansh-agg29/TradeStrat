"""
Tests for FixedAmountPositionSizing rule.
"""

import pytest

from position_sizing import FixedAmountPositionSizing


def test_fixed_amount_basic_calculation():
    """
    $10,000 allocation at $100/share = 100 shares.
    """

    rule = FixedAmountPositionSizing(amount=10000)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 100


def test_fixed_amount_limited_by_cash():
    """
    When cash is less than the amount, should use available cash.
    """

    rule = FixedAmountPositionSizing(amount=10000)

    shares = rule.calculate_shares(
        portfolio_value=50000,
        cash=5000,  # Only $5k available
        current_price=100,
    )

    assert shares == 50  # $5k / $100 = 50 shares


def test_fixed_amount_zero_cash():
    """
    Should return 0 when cash is zero.
    """

    rule = FixedAmountPositionSizing(amount=10000)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=0,
        current_price=100,
    )

    assert shares == 0


def test_fixed_amount_zero_price():
    """
    Should return 0 when price is zero.
    """

    rule = FixedAmountPositionSizing(amount=10000)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=0,
    )

    assert shares == 0


@pytest.mark.parametrize("amount", [0, -1000])
def test_fixed_amount_rejects_non_positive_amount(amount):
    """
    Amount must be positive.
    """

    with pytest.raises(
        ValueError,
        match="amount must be greater than zero",
    ):
        FixedAmountPositionSizing(amount=amount)


def test_fixed_amount_truncates_to_whole_shares():
    """
    Should only buy whole shares.
    """

    rule = FixedAmountPositionSizing(amount=10000)

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=33,
    )

    assert shares == 303  # 10000 // 33 = 303


def test_fixed_amount_ignores_portfolio_value():
    """
    Fixed amount should not depend on portfolio value.
    Same shares regardless of portfolio size.
    """

    rule = FixedAmountPositionSizing(amount=10000)

    shares_small = rule.calculate_shares(
        portfolio_value=20000,
        cash=20000,
        current_price=100,
    )

    shares_large = rule.calculate_shares(
        portfolio_value=1000000,
        cash=1000000,
        current_price=100,
    )

    assert shares_small == shares_large == 100


def test_fixed_amount_exact_cash_match():
    """
    When cash equals the amount exactly, buy the full allocation.
    """

    rule = FixedAmountPositionSizing(amount=5000)

    shares = rule.calculate_shares(
        portfolio_value=5000,
        cash=5000,
        current_price=50,
    )

    assert shares == 100
