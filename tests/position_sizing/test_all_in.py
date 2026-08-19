"""
Tests for AllInPositionSizing rule.
"""

from position_sizing import AllInPositionSizing


def test_all_in_uses_all_cash():
    """
    AllIn should buy the maximum whole shares with available cash.
    """

    rule = AllInPositionSizing()

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=50,
    )

    assert shares == 2000


def test_all_in_returns_zero_for_zero_cash():
    """
    AllIn should return 0 when no cash is available.
    """

    rule = AllInPositionSizing()

    shares = rule.calculate_shares(
        portfolio_value=50000,
        cash=0,
        current_price=50,
    )

    assert shares == 0


def test_all_in_returns_zero_for_zero_price():
    """
    AllIn should return 0 when price is zero.
    """

    rule = AllInPositionSizing()

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=0,
    )

    assert shares == 0


def test_all_in_truncates_to_whole_shares():
    """
    AllIn should only buy whole shares.
    """

    rule = AllInPositionSizing()

    shares = rule.calculate_shares(
        portfolio_value=100,
        cash=100,
        current_price=33,
    )

    assert shares == 3  # 100 // 33 = 3


def test_all_in_returns_zero_for_negative_price():
    """
    AllIn should return 0 when price is negative.
    """

    rule = AllInPositionSizing()

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=-10,
    )

    assert shares == 0


def test_all_in_returns_zero_for_negative_cash():
    """
    AllIn should return 0 when cash is negative.
    """

    rule = AllInPositionSizing()

    shares = rule.calculate_shares(
        portfolio_value=100000,
        cash=-5000,
        current_price=50,
    )

    assert shares == 0


def test_all_in_ignores_stop_loss_price():
    """
    AllIn should produce the same result regardless of stop_loss_price.
    """

    rule = AllInPositionSizing()

    shares_without = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=50,
        stop_loss_price=None,
    )

    shares_with = rule.calculate_shares(
        portfolio_value=100000,
        cash=100000,
        current_price=50,
        stop_loss_price=45,
    )

    assert shares_without == shares_with == 2000
