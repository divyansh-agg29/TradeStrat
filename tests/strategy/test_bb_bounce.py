import pandas as pd
import pytest

from strategy import generate_bb_bounce_signals


# ---------------------------------------------------------------------
# Test Helpers
# ---------------------------------------------------------------------

def create_market_data(close_prices):
    """Create a standard market DataFrame for testing."""

    return pd.DataFrame(
        {
            "Open": close_prices,
            "High": close_prices,
            "Low": close_prices,
            "Close": close_prices,
            "Volume": [1000] * len(close_prices),
        }
    )


# ---------------------------------------------------------------------
# Successful Signal Generation
# ---------------------------------------------------------------------

def test_generate_signals_adds_signal_column():
    """Signal column should be added to the returned DataFrame."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(df).df

    assert "Signal" in result.columns


def test_signal_column_contains_only_valid_values():
    """Signal column should contain only BUY, SELL or HOLD."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(df).df

    assert set(result["Signal"].unique()).issubset(
        {"BUY", "SELL", "HOLD"}
    )


def test_flat_prices_generate_hold_only():
    """Flat prices should generate only HOLD signals."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(df).df

    assert set(result["Signal"].unique()) == {"HOLD"}


def test_buy_signal_when_price_crosses_below_lower_band():
    """BUY signal should be generated when price crosses below lower band."""

    # Create a scenario where price drops below lower band
    prices = [100] * 20 + [95, 90, 85, 80, 75] + [100] * 25

    df = create_market_data(prices)

    result = generate_bb_bounce_signals(
        df,
        period=5,
        std_multiplier=1.0,
    ).df

    # Check that at least one BUY signal was generated
    assert (result["Signal"] == "BUY").any()


def test_sell_signal_when_price_crosses_above_upper_band():
    """SELL signal should be generated when price crosses above upper band."""

    # Create a scenario where price spikes above upper band
    prices = [100] * 20 + [105, 110, 115, 120, 125] + [100] * 25

    df = create_market_data(prices)

    result = generate_bb_bounce_signals(
        df,
        period=5,
        std_multiplier=1.0,
    ).df

    # Check that at least one SELL signal was generated
    assert (result["Signal"] == "SELL").any()


def test_no_signal_when_price_stays_within_bands():
    """HOLD signal should be maintained when price stays within bands."""

    # Create prices that oscillate gently within bands
    prices = [100 + i % 3 for i in range(50)]

    df = create_market_data(prices)

    result = generate_bb_bounce_signals(
        df,
        period=10,
        std_multiplier=3.0,
    ).df

    # Most signals should be HOLD
    hold_count = (result["Signal"] == "HOLD").sum()
    assert hold_count > 40


# ---------------------------------------------------------------------
# Indicator Integration
# ---------------------------------------------------------------------

def test_existing_bb_columns_are_reused():
    """Existing BB columns should not be recalculated."""

    df = create_market_data([100] * 50)

    df["BB_Middle20_2.0"] = 105
    df["BB_Upper20_2.0"] = 110
    df["BB_Lower20_2.0"] = 100

    result = generate_bb_bounce_signals(df).df

    assert (result["BB_Middle20_2.0"] == 105).all()
    assert (result["BB_Upper20_2.0"] == 110).all()
    assert (result["BB_Lower20_2.0"] == 100).all()


def test_missing_bb_columns_are_created():
    """Missing BB columns should be generated automatically."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(df).df

    assert "BB_Middle20_2.0" in result.columns
    assert "BB_Upper20_2.0" in result.columns
    assert "BB_Lower20_2.0" in result.columns


def test_custom_period_creates_correct_columns():
    """Custom BB period should generate the corresponding columns."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(
        df,
        period=10,
    ).df

    assert "BB_Middle10_2.0" in result.columns
    assert "BB_Upper10_2.0" in result.columns
    assert "BB_Lower10_2.0" in result.columns


def test_custom_std_multiplier_creates_correct_columns():
    """Custom std_multiplier should generate the corresponding columns."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(
        df,
        std_multiplier=1.5,
    ).df

    assert "BB_Middle20_1.5" in result.columns
    assert "BB_Upper20_1.5" in result.columns
    assert "BB_Lower20_1.5" in result.columns


def test_custom_price_column_is_used():
    """Custom price column should be used for BB calculation."""

    df = create_market_data([100] * 50)
    df["CustomPrice"] = [110] * 50

    result = generate_bb_bounce_signals(
        df,
        price_column="CustomPrice",
    ).df

    # BB middle should be based on CustomPrice (110), not Close (100)
    assert result["BB_Middle20_2.0"].iloc[-1] == pytest.approx(110, abs=0.1)


# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------

def test_empty_dataframe_raises_value_error():
    """Empty DataFrame should raise ValueError."""

    df = pd.DataFrame()

    with pytest.raises(ValueError, match="cannot be empty"):
        generate_bb_bounce_signals(df)


def test_invalid_period_raises_value_error():
    """Period must be positive."""

    df = create_market_data([100] * 50)

    with pytest.raises(ValueError, match="greater than zero"):
        generate_bb_bounce_signals(
            df,
            period=0,
        )


def test_negative_period_raises_value_error():
    """Negative period should raise ValueError."""

    df = create_market_data([100] * 50)

    with pytest.raises(ValueError, match="greater than zero"):
        generate_bb_bounce_signals(
            df,
            period=-5,
        )


def test_invalid_std_multiplier_raises_value_error():
    """std_multiplier must be positive."""

    df = create_market_data([100] * 50)

    with pytest.raises(ValueError, match="greater than zero"):
        generate_bb_bounce_signals(
            df,
            std_multiplier=0,
        )


def test_negative_std_multiplier_raises_value_error():
    """Negative std_multiplier should raise ValueError."""

    df = create_market_data([100] * 50)

    with pytest.raises(ValueError, match="greater than zero"):
        generate_bb_bounce_signals(
            df,
            std_multiplier=-1.0,
        )


def test_invalid_price_column_is_propagated():
    """Indicator validation errors should propagate."""

    df = create_market_data([100] * 50)

    with pytest.raises(ValueError, match="not found"):
        generate_bb_bounce_signals(
            df,
            price_column="NonExistentColumn",
        )


# ---------------------------------------------------------------------
# DataFrame Contract
# ---------------------------------------------------------------------

def test_original_dataframe_not_modified():
    """Original DataFrame should remain unchanged."""

    df = create_market_data([100] * 50)
    original = df.copy(deep=True)

    generate_bb_bounce_signals(df)

    pd.testing.assert_frame_equal(df, original)


def test_returns_new_dataframe():
    """Returned DataFrame should be a copy."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(df).df

    assert result is not df


def test_original_columns_are_preserved():
    """Original columns should still exist."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(df).df

    for column in df.columns:
        assert column in result.columns


def test_dataframe_index_is_preserved():
    """Index should remain unchanged."""

    df = create_market_data([100] * 50)
    df.index = pd.date_range(
        "2024-01-01",
        periods=50,
        freq="D",
    )

    result = generate_bb_bounce_signals(df).df

    pd.testing.assert_index_equal(df.index, result.index)


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------

def test_first_row_is_hold():
    """First row cannot generate a band crossing."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(df).df

    assert result.iloc[0]["Signal"] == "HOLD"


def test_signal_column_contains_no_missing_values():
    """Signal column should never contain NaN."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(df).df

    assert result["Signal"].isna().sum() == 0


def test_minimum_data_length():
    """Strategy should work with minimum required data points."""

    df = create_market_data([100] * 25)

    result = generate_bb_bounce_signals(
        df,
        period=20,
    ).df

    assert "Signal" in result.columns
    assert len(result) == 25


# ---------------------------------------------------------------------
# StrategyOutput Validation
# ---------------------------------------------------------------------

def test_returns_strategy_output_object():
    """Function should return a StrategyOutput object."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(df)

    assert hasattr(result, "df")
    assert hasattr(result, "indicators")


def test_indicator_metadata_contains_all_bands():
    """Indicator metadata should include all three BB bands."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(df)

    assert len(result.indicators) == 3

    indicator_names = [ind.name for ind in result.indicators]

    assert any("Middle" in name for name in indicator_names)
    assert any("Upper" in name for name in indicator_names)
    assert any("Lower" in name for name in indicator_names)


def test_all_indicators_are_overlay_type():
    """All BB indicators should be displayed as overlays."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(df)

    for indicator in result.indicators:
        assert indicator.display == "overlay"


def test_indicator_columns_match_dataframe():
    """Indicator metadata columns should exist in the DataFrame."""

    df = create_market_data([100] * 50)

    result = generate_bb_bounce_signals(df)

    for indicator in result.indicators:
        assert indicator.column in result.df.columns
