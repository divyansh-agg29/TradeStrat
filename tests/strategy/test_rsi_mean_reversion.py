import pandas as pd
import pytest

from strategy import RsiStrategy
from tests.strategy.helpers import create_market_data


class TestRSIMeanReversionSignalGeneration:

    def test_generate_signals_adds_signal_column(self):
        """Signal column should be added to the returned DataFrame."""

        df = create_market_data(range(1, 101))

        result = RsiStrategy().run(df).df

        assert "Signal" in result.columns

    def test_signal_column_contains_only_valid_values(self):
        """Signal column should contain only BUY, SELL or HOLD."""

        df = create_market_data(range(1, 101))

        result = RsiStrategy().run(df).df

        assert set(result["Signal"].unique()).issubset(
            {"BUY", "SELL", "HOLD"}
        )

    def test_no_threshold_crossing_generates_hold_only(self):
        """Flat prices should generate only HOLD signals."""

        df = create_market_data([100] * 100)

        result = RsiStrategy().run(df).df

        assert set(result["Signal"].unique()) == {"HOLD"}


class TestRSIMeanReversionIndicatorIntegration:

    def test_existing_rsi_column_is_reused(self):
        """Existing RSI column should not be recalculated."""

        df = create_market_data(range(1, 101))

        df["RSI14"] = 50

        result = RsiStrategy().run(df).df

        assert (result["RSI14"] == 50).all()

    def test_missing_rsi_column_is_created(self):
        """Missing RSI column should be generated automatically."""

        df = create_market_data(range(1, 101))

        result = RsiStrategy().run(df).df

        assert "RSI14" in result.columns

    def test_custom_period_creates_correct_column(self):
        """Custom RSI period should generate the corresponding column."""

        df = create_market_data(range(1, 101))

        result = RsiStrategy().run(
            df,
            rsi_period=10,
        ).df

        assert "RSI10" in result.columns


class TestRSIMeanReversionValidation:

    def test_empty_dataframe_raises_value_error(self):
        """Empty DataFrame should raise ValueError."""

        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Input DataFrame cannot be empty"):
            RsiStrategy().run(df)

    def test_invalid_rsi_period_raises_value_error(self):
        """RSI period must be positive."""

        df = create_market_data(range(1, 101))

        with pytest.raises(ValueError, match="rsi_period must be greater than zero"):
            RsiStrategy().run(
                df,
                rsi_period=0,
            )

    def test_invalid_thresholds_raise_value_error(self):
        """Overbought must be greater than oversold."""

        df = create_market_data(range(1, 101))

        with pytest.raises(ValueError, match="overbought must be greater than oversold"):
            RsiStrategy().run(
                df,
                overbought=30,
                oversold=70,
            )

    def test_equal_thresholds_raise_value_error(self):
        """Equal thresholds are not allowed."""

        df = create_market_data(range(1, 101))

        with pytest.raises(ValueError, match="overbought must be greater than oversold"):
            RsiStrategy().run(
                df,
                overbought=50,
                oversold=50,
            )

    def test_invalid_price_column_is_propagated(self):
        """Indicator validation errors should propagate."""

        df = create_market_data(range(1, 101))

        with pytest.raises(ValueError, match="Price column.*not found"):
            RsiStrategy().run(
                df,
                price_column="AdjustedClose",
            )


class TestRSIMeanReversionDataFrameContract:

    def test_original_dataframe_not_modified(self):
        """Original DataFrame should remain unchanged."""

        df = create_market_data(range(1, 101))
        original = df.copy(deep=True)

        RsiStrategy().run(df)

        pd.testing.assert_frame_equal(df, original)

    def test_returns_new_dataframe(self):
        """Returned DataFrame should be a copy."""

        df = create_market_data(range(1, 101))

        result = RsiStrategy().run(df).df

        assert result is not df

    def test_original_columns_are_preserved(self):
        """Original columns should still exist."""

        df = create_market_data(range(1, 101))

        result = RsiStrategy().run(df).df

        for column in df.columns:
            assert column in result.columns

    def test_dataframe_index_is_preserved(self):
        """Index should remain unchanged."""

        df = create_market_data(range(1, 101))
        df.index = pd.date_range(
            "2024-01-01",
            periods=100,
            freq="D",
        )

        result = RsiStrategy().run(df).df

        pd.testing.assert_index_equal(df.index, result.index)


class TestRSIMeanReversionEdgeCases:

    def test_first_row_is_hold(self):
        """First row cannot generate a threshold crossing."""

        df = create_market_data(range(1, 101))

        result = RsiStrategy().run(df).df

        assert result.iloc[0]["Signal"] == "HOLD"

    def test_signal_column_contains_no_missing_values(self):
        """Signal column should never contain NaN."""

        df = create_market_data(range(1, 101))

        result = RsiStrategy().run(df).df

        assert result["Signal"].isna().sum() == 0
