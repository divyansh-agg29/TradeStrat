"""
Unit tests for indicators.momentum.

These tests verify the RSI-specific values produced by calculate_rsi().
Behaviour shared with the other single-period indicators (validation,
duplicate prevention, copy semantics) lives in
test_indicator_contract.py.
"""

import pandas as pd
import pytest

from indicators.momentum import calculate_rsi


@pytest.fixture
def sample_dataframe():
    """Return a sample market data DataFrame."""

    return pd.DataFrame(
        {
            "Open": [10, 20, 30, 40, 50, 60, 70, 80],
            "High": [12, 22, 32, 42, 52, 62, 72, 82],
            "Low": [8, 18, 28, 38, 48, 58, 68, 78],
            "Close": [10, 20, 30, 40, 50, 60, 70, 80],
            "Volume": [100, 200, 300, 400, 500, 600, 700, 800],
        }
    )


class TestRSICalculation:

    def test_success(self, sample_dataframe):
        """Test successful RSI calculation."""

        result = calculate_rsi(sample_dataframe, period=3)

        assert "RSI3" in result.columns

        # RSI values should exist after the warm-up period.
        assert result["RSI3"].notna().sum() > 0

        # Every computed RSI must lie between 0 and 100.
        valid = result["RSI3"].dropna()

        assert ((valid >= 0) & (valid <= 100)).all()

    def test_custom_price_column(self, sample_dataframe):
        """Verify RSI can be calculated on a custom column."""

        result = calculate_rsi(
            sample_dataframe,
            period=3,
            price_column="Open",
        )

        assert "RSI3" in result.columns

        valid = result["RSI3"].dropna()

        assert ((valid >= 0) & (valid <= 100)).all()
