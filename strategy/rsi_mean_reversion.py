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
from utils.logger import get_logger

logger = get_logger(__name__)


def generate_rsi_mean_reversion_signals(
    df: pd.DataFrame,
    rsi_period: int = 14,
    overbought: int = 70,
    oversold: int = 30,
    price_column: str = "Close",
) -> pd.DataFrame:
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
    pandas.DataFrame
        Copy of the supplied DataFrame containing:

        - original columns
        - required RSI column
        - Signal column

    Raises
    ------
    ValueError
        If:

        - DataFrame is empty.
        - rsi_period is not positive.
        - overbought <= oversold.
    """

    logger.info(
        "Generating RSI mean reversion signals "
        "(period=%s, overbought=%s, oversold=%s).",
        rsi_period,
        overbought,
        oversold,
    )

    # ------------------------------------------------------------------
    # Strategy validation
    # ------------------------------------------------------------------

    if df.empty:
        logger.error("Input DataFrame is empty.")
        raise ValueError("Input DataFrame cannot be empty.")

    if rsi_period <= 0:
        logger.error(
            "Invalid RSI period: %s",
            rsi_period,
        )
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

    result_df = df.copy()

    rsi_column = f"RSI{rsi_period}"

    # ------------------------------------------------------------------
    # Ensure indicator exists
    # ------------------------------------------------------------------

    if rsi_column not in result_df.columns:
        logger.debug("%s not found. Calculating.", rsi_column)
        result_df = calculate_rsi(
            result_df,
            period=rsi_period,
            price_column=price_column,
        )

    # ------------------------------------------------------------------
    # Generate signals
    # ------------------------------------------------------------------

    result_df["Signal"] = "HOLD"

    previous_rsi = result_df[rsi_column].shift(1)
    current_rsi = result_df[rsi_column]

    buy_mask = (
        (previous_rsi >= oversold)
        & (current_rsi < oversold)
    )

    sell_mask = (
        (previous_rsi <= overbought)
        & (current_rsi > overbought)
    )

    result_df.loc[buy_mask, "Signal"] = "BUY"
    result_df.loc[sell_mask, "Signal"] = "SELL"

    logger.info(
        "Signal generation complete. "
        "BUY=%d SELL=%d",
        int(buy_mask.sum()),
        int(sell_mask.sum()),
    )

    return result_df
