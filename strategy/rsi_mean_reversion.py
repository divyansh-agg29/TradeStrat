"""
RSI Mean Reversion Strategy

This module implements a mean reversion trading strategy based on the
Relative Strength Index (RSI).

The strategy generates BUY, SELL and HOLD signals based on the RSI
crossing classic overbought and oversold thresholds.

Responsibilities
----------------
- Validate strategy-specific inputs.
- Ensure the required RSI indicator is available.
- Generate threshold-crossing signals.
- Return an enriched copy of the input DataFrame.
"""

import pandas as pd

from indicators.momentum import calculate_rsi
from strategy.base import Strategy
from strategy.result import IndicatorConfig, StrategyOutput
from utils.logger import get_logger

logger = get_logger(__name__)


class RsiStrategy(Strategy):
    """RSI mean reversion strategy implementation."""

    name = "RSI mean reversion"

    def validate_params(self, rsi_period=14, overbought=70, oversold=30, **_):
        if rsi_period <= 0:
            logger.error("Invalid RSI period: %s", rsi_period)
            raise ValueError(
                "rsi_period must be greater than zero."
            )

        if overbought <= oversold:
            logger.error(
                "Invalid threshold configuration: "
                "overbought=%s oversold=%s",
                overbought,
                oversold,
            )
            raise ValueError(
                "overbought must be greater than oversold."
            )

    def compute_indicators(self, df, price_column="Close", rsi_period=14, **_):
        rsi_column = f"RSI{rsi_period}"

        if rsi_column not in df.columns:
            logger.debug("%s not found. Calculating.", rsi_column)
            df = calculate_rsi(df, period=rsi_period, price_column=price_column)

        columns = {"rsi": rsi_column}
        return df, columns

    def generate_signals(self, df, columns, overbought=70, oversold=30, **_):
        rsi_column = columns["rsi"]

        df["Signal"] = "HOLD"

        previous_rsi = df[rsi_column].shift(1)
        current_rsi = df[rsi_column]

        buy_mask = (
            (previous_rsi >= oversold)
            & (current_rsi < oversold)
        )

        sell_mask = (
            (previous_rsi <= overbought)
            & (current_rsi > overbought)
        )

        df.loc[buy_mask, "Signal"] = "BUY"
        df.loc[sell_mask, "Signal"] = "SELL"

        return df

    def build_indicator_metadata(self, columns, rsi_period=14, **_):
        return [
            IndicatorConfig(
                column=columns["rsi"],
                name=f"RSI {rsi_period}",
                display="subplot",
                subplot_id="rsi",
                y_range=(0, 100),
            ),
        ]


def generate_rsi_mean_reversion_signals(
    df: pd.DataFrame,
    rsi_period: int = 14,
    overbought: int = 70,
    oversold: int = 30,
    price_column: str = "Close",
) -> StrategyOutput:
    """
    Generate trading signals using the RSI mean reversion strategy.

    BUY Signal
        Generated when the RSI crosses BELOW the oversold threshold.

    SELL Signal
        Generated when the RSI crosses ABOVE the overbought threshold.

    HOLD Signal
        Generated on all other rows.

    Parameters
    ----------
    df : pandas.DataFrame
        Market data DataFrame.

    rsi_period : int, default=14
        Period used for the RSI calculation.

    overbought : int, default=70
        RSI level above which a SELL signal is generated.

    oversold : int, default=30
        RSI level below which a BUY signal is generated.

    price_column : str, default="Close"
        Column used for RSI calculation if the indicator
        needs to be generated.

    Returns
    -------
    StrategyOutput
        Contains the enriched DataFrame and indicator metadata.

    Raises
    ------
    ValueError
        If:

        - DataFrame is empty.
        - rsi_period is not positive.
        - overbought <= oversold.
    """

    return RsiStrategy().run(
        df,
        price_column=price_column,
        rsi_period=rsi_period,
        overbought=overbought,
        oversold=oversold,
    )
