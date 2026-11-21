"""
Unit tests for indicators.moving_average.

These tests verify the SMA-specific values produced by calculate_sma().
Behaviour shared with the other single-period indicators (validation,
duplicate prevention, copy semantics) lives in
test_indicator_contract.py.
"""

import pandas as pd
import pytest

from indicators.moving_average import calculate_sma


@pytest.fixture
def sample_dataframe():
    """Return a sample market data DataFrame."""

    return pd.DataFrame(
        {
            "Open": [10, 20, 30, 40, 50],
            "High": [12, 22, 32, 42, 52],
            "Low": [8, 18, 28, 38, 48],
            "Close": [10, 20, 30, 40, 50],
            "Volume": [100, 200, 300, 400, 500],
        }
    )


class TestSMACalculation:

    def test_success(self, sample_dataframe):
        """Test successful SMA calculation."""

        result = calculate_sma(sample_dataframe, period=3)

        assert "SMA3" in result.columns

        expected = [None, None, 20.0, 30.0, 40.0]

        for actual, exp in zip(result["SMA3"], expected):
            if exp is None:
                assert pd.isna(actual)
            else:
                assert actual == exp

    def test_custom_price_column(self, sample_dataframe):
        """Verify SMA can be calculated on a custom column."""

        result = calculate_sma(
            sample_dataframe,
            period=2,
            price_column="Open",
        )

        assert "SMA2" in result.columns

        assert pd.isna(result.loc[0, "SMA2"])
        assert result.loc[1, "SMA2"] == 15.0
        assert result.loc[2, "SMA2"] == 25.0
