import pandas as pd
import pytest

from strategy import generate_rsi_mean_reversion_signals


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

    df = create_market_data(range(1, 101))

    result = generate_rsi_mean_reversion_signals(df)

    assert "Signal" in result.columns


def test_signal_column_contains_only_valid_values():
    """Signal column should contain only BUY, SELL or HOLD."""

    df = create_market_data(range(1, 101))

    result = generate_rsi_mean_reversion_signals(df)

    assert set(result["Signal"].unique()).issubset(
        {"BUY", "SELL", "HOLD"}
    )


def test_no_threshold_crossing_generates_hold_only():
    """Flat prices should generate only HOLD signals."""

    df = create_market_data([100] * 100)

    result = generate_rsi_mean_reversion_signals(df)

    assert set(result["Signal"].unique()) == {"HOLD"}


# ---------------------------------------------------------------------
# Indicator Integration
# ---------------------------------------------------------------------

def test_existing_rsi_column_is_reused():
    """Existing RSI column should not be recalculated."""

    df = create_market_data(range(1, 101))

    df["RSI14"] = 50

    result = generate_rsi_mean_reversion_signals(df)

    assert (result["RSI14"] == 50).all()


def test_missing_rsi_column_is_created():
    """Missing RSI column should be generated automatically."""

    df = create_market_data(range(1, 101))

    result = generate_rsi_mean_reversion_signals(df)

    assert "RSI14" in result.columns


def test_custom_period_creates_correct_column():
    """Custom RSI period should generate the corresponding column."""

    df = create_market_data(range(1, 101))

    result = generate_rsi_mean_reversion_signals(
        df,
        rsi_period=10,
    )

    assert "RSI10" in result.columns


# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------

def test_empty_dataframe_raises_value_error():
    """Empty DataFrame should raise ValueError."""

    df = pd.DataFrame()

    with pytest.raises(ValueError):
        generate_rsi_mean_reversion_signals(df)


def test_invalid_rsi_period_raises_value_error():
    """RSI period must be positive."""

    df = create_market_data(range(1, 101))

    with pytest.raises(ValueError):
        generate_rsi_mean_reversion_signals(
            df,
            rsi_period=0,
        )


def test_invalid_thresholds_raise_value_error():
    """Overbought must be greater than oversold."""

    df = create_market_data(range(1, 101))

    with pytest.raises(ValueError):
        generate_rsi_mean_reversion_signals(
            df,
            overbought=30,
            oversold=70,
        )


def test_equal_thresholds_raise_value_error():
    """Equal thresholds are not allowed."""

    df = create_market_data(range(1, 101))

    with pytest.raises(ValueError):
        generate_rsi_mean_reversion_signals(
            df,
            overbought=50,
            oversold=50,
        )


def test_invalid_price_column_is_propagated():
    """Indicator validation errors should propagate."""

    df = create_market_data(range(1, 101))

    with pytest.raises(ValueError):
        generate_rsi_mean_reversion_signals(
            df,
            price_column="AdjustedClose",
        )


# ---------------------------------------------------------------------
# DataFrame Contract
# ---------------------------------------------------------------------

def test_original_dataframe_not_modified():
    """Original DataFrame should remain unchanged."""

    df = create_market_data(range(1, 101))
    original = df.copy(deep=True)

    generate_rsi_mean_reversion_signals(df)

    pd.testing.assert_frame_equal(df, original)


def test_returns_new_dataframe():
    """Returned DataFrame should be a copy."""

    df = create_market_data(range(1, 101))

    result = generate_rsi_mean_reversion_signals(df)

    assert result is not df


def test_original_columns_are_preserved():
    """Original columns should still exist."""

    df = create_market_data(range(1, 101))

    result = generate_rsi_mean_reversion_signals(df)

    for column in df.columns:
        assert column in result.columns


def test_dataframe_index_is_preserved():
    """Index should remain unchanged."""

    df = create_market_data(range(1, 101))
    df.index = pd.date_range(
        "2024-01-01",
        periods=100,
        freq="D",
    )

    result = generate_rsi_mean_reversion_signals(df)

    pd.testing.assert_index_equal(df.index, result.index)


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------

def test_first_row_is_hold():
    """First row cannot generate a threshold crossing."""

    df = create_market_data(range(1, 101))

    result = generate_rsi_mean_reversion_signals(df)

    assert result.iloc[0]["Signal"] == "HOLD"


def test_signal_column_contains_no_missing_values():
    """Signal column should never contain NaN."""

    df = create_market_data(range(1, 101))

    result = generate_rsi_mean_reversion_signals(df)

    assert result["Signal"].isna().sum() == 0