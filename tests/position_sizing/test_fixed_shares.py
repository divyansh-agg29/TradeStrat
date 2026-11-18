"""
Tests for FixedSharesPositionSizing rule.
"""

import pytest

from position_sizing import FixedSharesPositionSizing


class TestFixedSharesPositionSizing:

    def test_basic_calculation(self):
        """
        Should buy the configured number of shares.
        """

        rule = FixedSharesPositionSizing(shares=100)

        result = rule.calculate_shares(
            portfolio_value=100000,
            cash=100000,
            current_price=50,
        )

        assert result == 100

    def test_limited_by_cash(self):
        """
        When cash is insufficient for the full amount, buy fewer shares.
        """

        rule = FixedSharesPositionSizing(shares=100)

        result = rule.calculate_shares(
            portfolio_value=5000,
            cash=2000,  # Can only afford 40 shares at $50
            current_price=50,
        )

        assert result == 40

    def test_zero_cash(self):
        """
        Should return 0 when cash is zero.
        """

        rule = FixedSharesPositionSizing(shares=100)

        result = rule.calculate_shares(
            portfolio_value=100000,
            cash=0,
            current_price=50,
        )

        assert result == 0

    def test_zero_price(self):
        """
        Should return 0 when price is zero.
        """

        rule = FixedSharesPositionSizing(shares=100)

        result = rule.calculate_shares(
            portfolio_value=100000,
            cash=100000,
            current_price=0,
        )

        assert result == 0

    @pytest.mark.parametrize("shares", [0, -10])
    def test_rejects_non_positive_shares(self, shares):
        """
        Shares must be positive.
        """

        with pytest.raises(
            ValueError,
            match="shares must be greater than zero",
        ):
            FixedSharesPositionSizing(shares=shares)

    def test_exact_cash_match(self):
        """
        When cash exactly affords the requested shares, buy them all.
        """

        rule = FixedSharesPositionSizing(shares=100)

        result = rule.calculate_shares(
            portfolio_value=5000,
            cash=5000,
            current_price=50,
        )

        assert result == 100

    def test_ignores_portfolio_value(self):
        """
        Fixed shares count should not depend on portfolio value.
        """

        rule = FixedSharesPositionSizing(shares=50)

        shares_small = rule.calculate_shares(
            portfolio_value=10000,
            cash=10000,
            current_price=100,
        )

        shares_large = rule.calculate_shares(
            portfolio_value=1000000,
            cash=1000000,
            current_price=100,
        )

        assert shares_small == shares_large == 50
