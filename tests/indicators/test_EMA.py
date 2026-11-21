"""
Unit tests for indicators.moving_average.

These tests verify the EMA-specific values produced by calculate_ema().
Behaviour shared with the other single-period indicators (validation,
duplicate prevention, copy semantics) lives in
test_indicator_contract.py.
"""

import pandas as pd
import pytest

from indicators.moving_average import calculate_ema


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


class TestEMACalculation:

    def test_success(self, sample_dataframe):
        """Test successful EMA calculation."""

        result = calculate_ema(sample_dataframe, period=3)

        assert "EMA3" in result.columns

        expected = [
            10.0,
            15.0,
            22.5,
            31.25,
            40.625,
        ]

        for actual, exp in zip(result["EMA3"], expected):
            assert actual == pytest.approx(exp)

    def test_custom_price_column(self, sample_dataframe):
        """Verify EMA can be calculated on a custom column."""

        result = calculate_ema(
            sample_dataframe,
            period=2,
            price_column="Open",
        )

        assert "EMA2" in result.columns

        expected = [
            10.0,
            16.6666666667,
            25.5555555556,
            35.1851851852,
            45.0617283951,
        ]

        for actual, exp in zip(result["EMA2"], expected):
            assert actual == pytest.approx(exp)
