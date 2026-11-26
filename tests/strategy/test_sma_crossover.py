import pandas as pd
import pytest

from strategy import SmaStrategy
from tests.strategy.helpers import create_market_data


class TestSMACrossoverSignalGeneration:

    def test_generate_signals_adds_signal_column(self):
        """Signal column should be added to the returned DataFrame."""

        df = create_market_data(range(1, 101))

        result = SmaStrategy().run(df).df

        assert "Signal" in result.columns

    def test_signal_column_contains_only_valid_values(self):
        """Signal column should contain only BUY, SELL or HOLD."""

        df = create_market_data(range(1, 101))

        result = SmaStrategy().run(df).df

        assert set(result["Signal"].unique()).issubset(
            {"BUY", "SELL", "HOLD"}
        )

    def test_buy_signal_generated(self):
        """Strategy should generate at least one BUY signal."""

        prices = (
            [100] * 60
            + [105, 110, 115, 120, 125, 130, 135, 140]
        )

        df = create_market_data(prices)

        result = SmaStrategy().run(df).df

        assert "BUY" in result["Signal"].values

    def test_sell_signal_generated(self):
        """Strategy should generate at least one SELL signal."""

        prices = (
            [140] * 60
            + [130, 120, 110, 100, 90, 80, 70]
        )

        df = create_market_data(prices)

        result = SmaStrategy().run(df).df

        assert "SELL" in result["Signal"].values

    def test_no_crossover_generates_hold_only(self):
        """Constant prices should generate only HOLD signals."""

        df = create_market_data([100] * 100)

        result = SmaStrategy().run(df).df

        assert set(result["Signal"].unique()) == {"HOLD"}


class TestSMACrossoverIndicatorIntegration:

    def test_existing_sma_columns_are_reused(self):
        """Existing SMA columns should not be recalculated."""

        df = create_market_data(range(1, 101))

        df["SMA20"] = 999
        df["SMA50"] = 888

        result = SmaStrategy().run(df).df

        assert (result["SMA20"] == 999).all()
        assert (result["SMA50"] == 888).all()

    def test_missing_sma_columns_are_created(self):
        """Missing SMA columns should be generated automatically."""

        df = create_market_data(range(1, 101))

        result = SmaStrategy().run(df).df

        assert "SMA20" in result.columns
        assert "SMA50" in result.columns

    def test_custom_periods_create_correct_columns(self):
        """Custom SMA periods should generate corresponding columns."""

        df = create_market_data(range(1, 101))

        result = SmaStrategy().run(
            df,
            short_period=10,
            long_period=30,
        ).df

        assert "SMA10" in result.columns
        assert "SMA30" in result.columns


class TestSMACrossoverValidation:

    def test_empty_dataframe_raises_value_error(self):
        """Empty DataFrame should raise ValueError."""

        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Input DataFrame cannot be empty"):
            SmaStrategy().run(df)

    def test_invalid_period_order_raises_value_error(self):
        """short_period must be smaller than long_period."""

        df = create_market_data(range(1, 101))

        with pytest.raises(ValueError, match="short_period must be smaller than long_period"):
            SmaStrategy().run(
                df,
                short_period=50,
                long_period=20,
            )

    def test_equal_periods_raise_value_error(self):
        """Equal SMA periods are not allowed."""

        df = create_market_data(range(1, 101))

        with pytest.raises(ValueError, match="short_period must be smaller than long_period"):
            SmaStrategy().run(
                df,
                short_period=20,
                long_period=20,
            )

    def test_invalid_price_column_is_propagated(self):
        """Indicator validation errors should propagate."""

        df = create_market_data(range(1, 101))

        with pytest.raises(ValueError, match="Price column.*not found"):
            SmaStrategy().run(
                df,
                price_column="AdjustedClose",
            )


class TestSMACrossoverDataFrameContract:

    def test_original_dataframe_not_modified(self):
        """Original DataFrame should remain unchanged."""

        df = create_market_data(range(1, 101))
        original = df.copy(deep=True)

        SmaStrategy().run(df)

        pd.testing.assert_frame_equal(df, original)

    def test_returns_new_dataframe(self):
        """Returned DataFrame should be a copy."""

        df = create_market_data(range(1, 101))

        result = SmaStrategy().run(df).df

        assert result is not df

    def test_original_columns_are_preserved(self):
        """Original columns should still exist."""

        df = create_market_data(range(1, 101))

        result = SmaStrategy().run(df).df

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

        result = SmaStrategy().run(df).df

        pd.testing.assert_index_equal(df.index, result.index)


class TestSMACrossoverEdgeCases:

    def test_small_dataset_returns_hold_only(self):
        """Dataset shorter than long SMA period should not generate trades."""

        df = create_market_data(range(10))

        result = SmaStrategy().run(df).df

        assert set(result["Signal"].unique()) == {"HOLD"}

    def test_first_row_is_hold(self):
        """First row cannot generate a crossover."""

        df = create_market_data(range(1, 101))

        result = SmaStrategy().run(df).df

        assert result.iloc[0]["Signal"] == "HOLD"

    def test_signal_column_contains_no_missing_values(self):
        """Signal column should never contain NaN."""

        df = create_market_data(range(1, 101))

        result = SmaStrategy().run(df).df

        assert result["Signal"].isna().sum() == 0
