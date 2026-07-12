"""
Unit tests for indicators.momentum.

These tests verify the behaviour of the calculate_rsi() function,
including successful calculations, input validation, duplicate
indicator prevention and copy semantics.
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


def test_calculate_rsi_success(sample_dataframe):
    """Test successful RSI calculation."""

    result = calculate_rsi(sample_dataframe, period=3)

    assert "RSI3" in result.columns

    # RSI values should exist after the warm-up period.
    assert result["RSI3"].notna().sum() > 0

    # Every computed RSI must lie between 0 and 100.
    valid = result["RSI3"].dropna()

    assert ((valid >= 0) & (valid <= 100)).all()


def test_original_dataframe_not_modified(sample_dataframe):
    """Ensure the original DataFrame is not modified."""

    original = sample_dataframe.copy()

    result = calculate_rsi(sample_dataframe, period=3)

    assert "RSI3" not in sample_dataframe.columns
    assert "RSI3" in result.columns

    pd.testing.assert_frame_equal(sample_dataframe, original)


def test_existing_columns_are_preserved(sample_dataframe):
    """Verify original columns remain unchanged."""

    result = calculate_rsi(sample_dataframe, period=3)

    expected_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "RSI3",
    ]

    assert list(result.columns) == expected_columns


def test_custom_price_column(sample_dataframe):
    """Verify RSI can be calculated on a custom column."""

    result = calculate_rsi(
        sample_dataframe,
        period=3,
        price_column="Open",
    )

    assert "RSI3" in result.columns

    valid = result["RSI3"].dropna()

    assert ((valid >= 0) & (valid <= 100)).all()


def test_duplicate_indicator_raises_exception(sample_dataframe):
    """Verify duplicate indicator columns are rejected."""

    result = calculate_rsi(sample_dataframe, period=3)

    with pytest.raises(
        ValueError,
        match="Indicator column 'RSI3' already exists.",
    ):
        calculate_rsi(result, period=3)


@pytest.mark.parametrize(
    "period",
    [0, -1, -20],
)
def test_invalid_period_value(sample_dataframe, period):
    """Verify non-positive periods raise ValueError."""

    with pytest.raises(
        ValueError,
        match="Period must be greater than zero.",
    ):
        calculate_rsi(sample_dataframe, period)


@pytest.mark.parametrize(
    "period",
    [2.5, "20", None],
)
def test_invalid_period_type(sample_dataframe, period):
    """Verify invalid period types raise TypeError."""

    with pytest.raises(
        TypeError,
        match="Period must be an integer.",
    ):
        calculate_rsi(sample_dataframe, period)


def test_missing_price_column(sample_dataframe):
    """Verify missing price column raises ValueError."""

    with pytest.raises(
        ValueError,
        match="Price column 'Adj Close' not found.",
    ):
        calculate_rsi(
            sample_dataframe,
            period=3,
            price_column="Adj Close",
        )


def test_invalid_dataframe_type():
    """Verify non-DataFrame input raises TypeError."""

    with pytest.raises(
        TypeError,
        match="Input must be a pandas DataFrame.",
    ):
        calculate_rsi([], period=3)


def test_empty_dataframe():
    """Verify empty DataFrame is handled correctly."""

    empty_df = pd.DataFrame(
        columns=["Open", "High", "Low", "Close", "Volume"]
    )

    result = calculate_rsi(empty_df, period=3)

    assert "RSI3" in result.columns
    assert result.empty


def test_multiple_indicators_can_be_added(sample_dataframe):
    """Verify multiple RSI indicators can coexist."""

    result = calculate_rsi(sample_dataframe, period=2)
    result = calculate_rsi(result, period=3)

    assert "RSI2" in result.columns
    assert "RSI3" in result.columns

    assert len(result.columns) == 7