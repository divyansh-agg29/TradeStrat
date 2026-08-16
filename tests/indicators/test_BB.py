"""
Unit tests for indicators.moving_average.

These tests verify the behaviour of the calculate_bollinger_bands() function,
including successful calculations, input validation, duplicate indicator
prevention and copy semantics.
"""

import pandas as pd
import pytest

from indicators.moving_average import calculate_bollinger_bands


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


def test_calculate_bollinger_bands_success(sample_dataframe):
    """Test successful Bollinger Bands calculation."""

    result = calculate_bollinger_bands(
        sample_dataframe,
        period=3,
        std_multiplier=2,
    )

    assert "BB_Middle3_2" in result.columns
    assert "BB_Upper3_2" in result.columns
    assert "BB_Lower3_2" in result.columns

    expected_middle = [
        None,
        None,
        20.0,
        30.0,
        40.0,
    ]

    expected_upper = [
        None,
        None,
        36.3299316186,
        46.3299316186,
        56.3299316186,
    ]

    expected_lower = [
        None,
        None,
        3.6700683814,
        13.6700683814,
        23.6700683814,
    ]

    for actual, exp in zip(
        result["BB_Middle3_2"],
        expected_middle,
    ):
        if exp is None:
            assert pd.isna(actual)
        else:
            assert actual == pytest.approx(exp)

    for actual, exp in zip(
        result["BB_Upper3_2"],
        expected_upper,
    ):
        if exp is None:
            assert pd.isna(actual)
        else:
            assert actual == pytest.approx(exp)

    for actual, exp in zip(
        result["BB_Lower3_2"],
        expected_lower,
    ):
        if exp is None:
            assert pd.isna(actual)
        else:
            assert actual == pytest.approx(exp)


def test_original_dataframe_not_modified(sample_dataframe):
    """Ensure the original DataFrame is not modified."""

    original = sample_dataframe.copy()

    result = calculate_bollinger_bands(
        sample_dataframe,
        period=3,
        std_multiplier=2,
    )

    assert "BB_Middle3_2" not in sample_dataframe.columns
    assert "BB_Upper3_2" not in sample_dataframe.columns
    assert "BB_Lower3_2" not in sample_dataframe.columns

    assert "BB_Middle3_2" in result.columns
    assert "BB_Upper3_2" in result.columns
    assert "BB_Lower3_2" in result.columns

    pd.testing.assert_frame_equal(sample_dataframe, original)


def test_existing_columns_are_preserved(sample_dataframe):
    """Verify original columns remain unchanged."""

    result = calculate_bollinger_bands(
        sample_dataframe,
        period=3,
        std_multiplier=2,
    )

    expected_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "BB_Middle3_2",
        "BB_Upper3_2",
        "BB_Lower3_2",
    ]

    assert list(result.columns) == expected_columns


def test_custom_price_column(sample_dataframe):
    """Verify Bollinger Bands can be calculated on a custom column."""

    result = calculate_bollinger_bands(
        sample_dataframe,
        period=2,
        std_multiplier=2,
        price_column="Open",
    )

    assert "BB_Middle2_2" in result.columns
    assert "BB_Upper2_2" in result.columns
    assert "BB_Lower2_2" in result.columns

    # First row does not have enough data.
    assert pd.isna(result.loc[0, "BB_Middle2_2"])

    # Mean of 10 and 20 = 15
    assert result.loc[1, "BB_Middle2_2"] == pytest.approx(15.0)

    # Population standard deviation of [10, 20]
    # = sqrt(((10 - 15)^2 + (20 - 15)^2) / 2)
    # = 5
    #
    # Upper = 15 + 2 * 5 = 25
    # Lower = 15 - 2 * 5 = 5
    assert result.loc[1, "BB_Upper2_2"] == pytest.approx(25.0)
    assert result.loc[1, "BB_Lower2_2"] == pytest.approx(5.0)


def test_custom_std_multiplier(sample_dataframe):
    """Verify a custom standard deviation multiplier is used."""

    result = calculate_bollinger_bands(
        sample_dataframe,
        period=3,
        std_multiplier=1,
    )

    assert "BB_Middle3_1" in result.columns
    assert "BB_Upper3_1" in result.columns
    assert "BB_Lower3_1" in result.columns

    # For [10, 20, 30]:
    # Mean = 20
    # Population standard deviation = sqrt(200 / 3)
    expected_std = (200 / 3) ** 0.5

    assert result.loc[2, "BB_Middle3_1"] == pytest.approx(20.0)
    assert result.loc[2, "BB_Upper3_1"] == pytest.approx(
        20.0 + expected_std
    )
    assert result.loc[2, "BB_Lower3_1"] == pytest.approx(
        20.0 - expected_std
    )


def test_duplicate_indicator_raises_exception(sample_dataframe):
    """Verify duplicate Bollinger Band columns are rejected."""

    result = calculate_bollinger_bands(
        sample_dataframe,
        period=3,
        std_multiplier=2,
    )

    with pytest.raises(
        ValueError,
        match="Indicator column 'BB_Middle3_2' already exists.",
    ):
        calculate_bollinger_bands(
            result,
            period=3,
            std_multiplier=2,
        )


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
        calculate_bollinger_bands(
            sample_dataframe,
            period,
            std_multiplier=2,
        )


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
        calculate_bollinger_bands(
            sample_dataframe,
            period,
            std_multiplier=2,
        )


@pytest.mark.parametrize(
    "std_multiplier",
    [0, -1, -2.5],
)
def test_invalid_std_multiplier_value(
    sample_dataframe,
    std_multiplier,
):
    """Verify non-positive standard deviation multipliers raise ValueError."""

    with pytest.raises(
        ValueError,
        match="std_multiplier must be greater than zero.",
    ):
        calculate_bollinger_bands(
            sample_dataframe,
            period=3,
            std_multiplier=std_multiplier,
        )


@pytest.mark.parametrize(
    "std_multiplier",
    ["2", None, [2]],
)
def test_invalid_std_multiplier_type(
    sample_dataframe,
    std_multiplier,
):
    """Verify invalid standard deviation multiplier types raise TypeError."""

    with pytest.raises(
        TypeError,
        match="std_multiplier must be a number.",
    ):
        calculate_bollinger_bands(
            sample_dataframe,
            period=3,
            std_multiplier=std_multiplier,
        )


def test_missing_price_column(sample_dataframe):
    """Verify missing price column raises ValueError."""

    with pytest.raises(
        ValueError,
        match="Price column 'Adj Close' not found.",
    ):
        calculate_bollinger_bands(
            sample_dataframe,
            period=3,
            std_multiplier=2,
            price_column="Adj Close",
        )


def test_invalid_dataframe_type():
    """Verify non-DataFrame input raises TypeError."""

    with pytest.raises(
        TypeError,
        match="Input must be a pandas DataFrame.",
    ):
        calculate_bollinger_bands(
            [],
            period=3,
            std_multiplier=2,
        )


def test_empty_dataframe():
    """Verify empty DataFrame is handled correctly."""

    empty_df = pd.DataFrame(
        columns=["Open", "High", "Low", "Close", "Volume"]
    )

    result = calculate_bollinger_bands(
        empty_df,
        period=3,
        std_multiplier=2,
    )

    assert "BB_Middle3_2" in result.columns
    assert "BB_Upper3_2" in result.columns
    assert "BB_Lower3_2" in result.columns
    assert result.empty


def test_multiple_bollinger_bands_can_be_added(sample_dataframe):
    """Verify multiple Bollinger Band configurations can coexist."""

    result = calculate_bollinger_bands(
        sample_dataframe,
        period=2,
        std_multiplier=2,
    )

    result = calculate_bollinger_bands(
        result,
        period=3,
        std_multiplier=2,
    )

    assert "BB_Middle2_2" in result.columns
    assert "BB_Upper2_2" in result.columns
    assert "BB_Lower2_2" in result.columns

    assert "BB_Middle3_2" in result.columns
    assert "BB_Upper3_2" in result.columns
    assert "BB_Lower3_2" in result.columns

    assert len(result.columns) == 11