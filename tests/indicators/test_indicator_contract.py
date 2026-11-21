"""
Shared contract tests for single-period indicators.

SMA, EMA and RSI expose the same interface
(``calculate_x(df, period, price_column)``) and add a single
``<PREFIX><period>`` column.  The behaviour common to all of them is
verified here once; indicator-specific value tests live in the
individual ``test_<INDICATOR>.py`` files.
"""

import pandas as pd
import pytest

from indicators.momentum import calculate_rsi
from indicators.moving_average import calculate_ema, calculate_sma


SINGLE_PERIOD_INDICATORS = pytest.mark.parametrize(
    "calculate_fn, prefix",
    [
        pytest.param(calculate_sma, "SMA", id="SMA"),
        pytest.param(calculate_ema, "EMA", id="EMA"),
        pytest.param(calculate_rsi, "RSI", id="RSI"),
    ],
)


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


@SINGLE_PERIOD_INDICATORS
class TestIndicatorCalculationContract:

    def test_original_dataframe_not_modified(
        self, sample_dataframe, calculate_fn, prefix
    ):
        """Ensure the original DataFrame is not modified."""

        original = sample_dataframe.copy()

        result = calculate_fn(sample_dataframe, period=3)

        assert f"{prefix}3" not in sample_dataframe.columns
        assert f"{prefix}3" in result.columns

        pd.testing.assert_frame_equal(sample_dataframe, original)

    def test_existing_columns_are_preserved(
        self, sample_dataframe, calculate_fn, prefix
    ):
        """Verify original columns remain unchanged."""

        result = calculate_fn(sample_dataframe, period=3)

        expected_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            f"{prefix}3",
        ]

        assert list(result.columns) == expected_columns

    def test_duplicate_indicator_raises_exception(
        self, sample_dataframe, calculate_fn, prefix
    ):
        """Verify duplicate indicator columns are rejected."""

        result = calculate_fn(sample_dataframe, period=3)

        with pytest.raises(
            ValueError,
            match=f"Indicator column '{prefix}3' already exists.",
        ):
            calculate_fn(result, period=3)

    def test_multiple_indicators_can_be_added(
        self, sample_dataframe, calculate_fn, prefix
    ):
        """Verify multiple indicators of the same type can coexist."""

        result = calculate_fn(sample_dataframe, period=2)
        result = calculate_fn(result, period=3)

        assert f"{prefix}2" in result.columns
        assert f"{prefix}3" in result.columns

        assert len(result.columns) == len(sample_dataframe.columns) + 2


@SINGLE_PERIOD_INDICATORS
class TestIndicatorValidationContract:

    @pytest.mark.parametrize(
        "period",
        [0, -1, -20],
    )
    def test_invalid_period_value(
        self, sample_dataframe, calculate_fn, prefix, period
    ):
        """Verify non-positive periods raise ValueError."""

        with pytest.raises(
            ValueError,
            match="Period must be greater than zero.",
        ):
            calculate_fn(sample_dataframe, period)

    @pytest.mark.parametrize(
        "period",
        [2.5, "20", None],
    )
    def test_invalid_period_type(
        self, sample_dataframe, calculate_fn, prefix, period
    ):
        """Verify invalid period types raise TypeError."""

        with pytest.raises(
            TypeError,
            match="Period must be an integer.",
        ):
            calculate_fn(sample_dataframe, period)

    def test_missing_price_column(
        self, sample_dataframe, calculate_fn, prefix
    ):
        """Verify missing price column raises ValueError."""

        with pytest.raises(
            ValueError,
            match="Price column 'Adj Close' not found.",
        ):
            calculate_fn(
                sample_dataframe,
                period=3,
                price_column="Adj Close",
            )

    def test_invalid_dataframe_type(self, calculate_fn, prefix):
        """Verify non-DataFrame input raises TypeError."""

        with pytest.raises(
            TypeError,
            match="Input must be a pandas DataFrame.",
        ):
            calculate_fn([], period=3)

    def test_empty_dataframe(self, calculate_fn, prefix):
        """Verify empty DataFrame is handled correctly."""

        empty_df = pd.DataFrame(
            columns=["Open", "High", "Low", "Close", "Volume"]
        )

        result = calculate_fn(empty_df, period=3)

        assert f"{prefix}3" in result.columns
        assert result.empty
