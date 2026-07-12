"""
Unit tests for indicators.moving_average.

These tests verify the behaviour of the calculate_ema() function,
including successful calculations, input validation, duplicate
indicator prevention and copy semantics.
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


def test_calculate_ema_success(sample_dataframe):
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


def test_original_dataframe_not_modified(sample_dataframe):
    """Ensure the original DataFrame is not modified."""

    original = sample_dataframe.copy()

    result = calculate_ema(sample_dataframe, period=3)

    assert "EMA3" not in sample_dataframe.columns
    assert "EMA3" in result.columns

    pd.testing.assert_frame_equal(sample_dataframe, original)


def test_existing_columns_are_preserved(sample_dataframe):
    """Verify original columns remain unchanged."""

    result = calculate_ema(sample_dataframe, period=3)

    expected_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "EMA3",
    ]

    assert list(result.columns) == expected_columns


def test_custom_price_column(sample_dataframe):
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


def test_duplicate_indicator_raises_exception(sample_dataframe):
    """Verify duplicate indicator columns are rejected."""

    result = calculate_ema(sample_dataframe, period=3)

    with pytest.raises(
        ValueError,
        match="Indicator column 'EMA3' already exists.",
    ):
        calculate_ema(result, period=3)


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
        calculate_ema(sample_dataframe, period)


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
        calculate_ema(sample_dataframe, period)


def test_missing_price_column(sample_dataframe):
    """Verify missing price column raises ValueError."""

    with pytest.raises(
        ValueError,
        match="Price column 'Adj Close' not found.",
    ):
        calculate_ema(
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
        calculate_ema([], period=3)


def test_empty_dataframe():
    """Verify empty DataFrame is handled correctly."""

    empty_df = pd.DataFrame(
        columns=["Open", "High", "Low", "Close", "Volume"]
    )

    result = calculate_ema(empty_df, period=3)

    assert "EMA3" in result.columns
    assert result.empty


def test_multiple_indicators_can_be_added(sample_dataframe):
    """Verify multiple EMA indicators can coexist."""

    result = calculate_ema(sample_dataframe, period=2)
    result = calculate_ema(result, period=3)

    assert "EMA2" in result.columns
    assert "EMA3" in result.columns

    assert len(result.columns) == 7