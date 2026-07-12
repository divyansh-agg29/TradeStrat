"""
Unit tests for indicators.momentum.

These tests verify the behaviour of the calculate_macd() function,
including successful calculations, input validation, duplicate
indicator prevention and copy semantics.
"""

import pandas as pd
import pytest

from indicators.momentum import calculate_macd


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


def test_calculate_macd_success(sample_dataframe):
    """Test successful MACD calculation."""

    result = calculate_macd(sample_dataframe)

    assert "MACD_12_26_9" in result.columns
    assert "MACD_Signal_12_26_9" in result.columns
    assert "MACD_Histogram_12_26_9" in result.columns

    assert result["MACD_12_26_9"].notna().sum() > 0
    assert result["MACD_Signal_12_26_9"].notna().sum() > 0
    assert result["MACD_Histogram_12_26_9"].notna().sum() > 0


def test_original_dataframe_not_modified(sample_dataframe):
    """Ensure the original DataFrame is not modified."""

    original = sample_dataframe.copy()

    result = calculate_macd(sample_dataframe)

    assert "MACD_12_26_9" not in sample_dataframe.columns
    assert "MACD_Signal_12_26_9" not in sample_dataframe.columns
    assert "MACD_Histogram_12_26_9" not in sample_dataframe.columns

    pd.testing.assert_frame_equal(sample_dataframe, original)

    assert "MACD_12_26_9" in result.columns


def test_existing_columns_are_preserved(sample_dataframe):
    """Verify original columns remain unchanged."""

    result = calculate_macd(sample_dataframe)

    expected_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "MACD_12_26_9",
        "MACD_Signal_12_26_9",
        "MACD_Histogram_12_26_9",
    ]

    assert list(result.columns) == expected_columns


def test_custom_price_column(sample_dataframe):
    """Verify MACD can be calculated on a custom column."""

    result = calculate_macd(
        sample_dataframe,
        price_column="Open",
    )

    assert "MACD_12_26_9" in result.columns
    assert "MACD_Signal_12_26_9" in result.columns
    assert "MACD_Histogram_12_26_9" in result.columns


def test_duplicate_indicator_raises_exception(sample_dataframe):
    """Verify duplicate MACD configuration is rejected."""

    result = calculate_macd(sample_dataframe)

    with pytest.raises(
        ValueError,
        match="Indicator column 'MACD_12_26_9' already exists.",
    ):
        calculate_macd(result)


@pytest.mark.parametrize(
    "fast_period, slow_period, signal_period",
    [
        (0, 26, 9),
        (12, 0, 9),
        (12, 26, 0),
        (-1, 26, 9),
        (12, -1, 9),
        (12, 26, -1),
    ],
)
def test_invalid_period_values(
    sample_dataframe,
    fast_period,
    slow_period,
    signal_period,
):
    """Verify non-positive periods raise ValueError."""

    with pytest.raises(
        ValueError,
        match="must be greater than zero.",
    ):
        calculate_macd(
            sample_dataframe,
            fast_period=fast_period,
            slow_period=slow_period,
            signal_period=signal_period,
        )


@pytest.mark.parametrize(
    "fast_period, slow_period, signal_period",
    [
        (12.5, 26, 9),
        ("12", 26, 9),
        (12, "26", 9),
        (12, 26, "9"),
        (None, 26, 9),
    ],
)
def test_invalid_period_types(
    sample_dataframe,
    fast_period,
    slow_period,
    signal_period,
):
    """Verify invalid period types raise TypeError."""

    with pytest.raises(
        TypeError,
        match="must be an integer.",
    ):
        calculate_macd(
            sample_dataframe,
            fast_period=fast_period,
            slow_period=slow_period,
            signal_period=signal_period,
        )


def test_fast_period_must_be_less_than_slow_period(
    sample_dataframe,
):
    """Verify fast_period must be less than slow_period."""

    with pytest.raises(
        ValueError,
        match="fast_period must be less than slow_period.",
    ):
        calculate_macd(
            sample_dataframe,
            fast_period=26,
            slow_period=12,
        )


def test_missing_price_column(sample_dataframe):
    """Verify missing price column raises ValueError."""

    with pytest.raises(
        ValueError,
        match="Price column 'Adj Close' not found.",
    ):
        calculate_macd(
            sample_dataframe,
            price_column="Adj Close",
        )


def test_invalid_dataframe_type():
    """Verify non-DataFrame input raises TypeError."""

    with pytest.raises(
        TypeError,
        match="Input must be a pandas DataFrame.",
    ):
        calculate_macd([])


def test_empty_dataframe():
    """Verify empty DataFrame is handled correctly."""

    empty_df = pd.DataFrame(
        columns=["Open", "High", "Low", "Close", "Volume"]
    )

    result = calculate_macd(empty_df)

    assert "MACD_12_26_9" in result.columns
    assert "MACD_Signal_12_26_9" in result.columns
    assert "MACD_Histogram_12_26_9" in result.columns

    assert result.empty


def test_multiple_macd_indicators_can_be_added(sample_dataframe):
    """Verify multiple MACD configurations can coexist."""

    result = calculate_macd(
        sample_dataframe,
        fast_period=12,
        slow_period=26,
        signal_period=9,
    )

    result = calculate_macd(
        result,
        fast_period=5,
        slow_period=35,
        signal_period=5,
    )

    assert "MACD_12_26_9" in result.columns
    assert "MACD_Signal_12_26_9" in result.columns
    assert "MACD_Histogram_12_26_9" in result.columns

    assert "MACD_5_35_5" in result.columns
    assert "MACD_Signal_5_35_5" in result.columns
    assert "MACD_Histogram_5_35_5" in result.columns

    assert len(result.columns) == 11