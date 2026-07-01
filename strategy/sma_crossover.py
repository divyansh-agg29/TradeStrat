"""
SMA Crossover Strategy

This module implements the Simple Moving Average (SMA) crossover trading strategy.

The strategy generates BUY, SELL and HOLD signals based on crossover events
between a short-term and long-term SMA.

Responsibilities
----------------
- Validate strategy-specific inputs.
- Ensure required SMA indicators are available.
- Generate crossover signals.
- Return an enriched copy of the input DataFrame.

The strategy intentionally does NOT:
- Download market data.
- Calculate indicators directly.
- Execute trades.
- Track portfolio state.
- Compute performance metrics.
"""

import pandas as pd

from indicators.moving_average import calculate_sma
from utils.logger import get_logger

logger = get_logger(__name__)


def generate_sma_crossover_signals(
    df: pd.DataFrame,
    short_period: int = 20,
    long_period: int = 50,
    price_column: str = "Close",
) -> pd.DataFrame:
    """
    Generate trading signals using the SMA crossover strategy.

    BUY Signal
        Generated when the short SMA crosses ABOVE the long SMA.

    SELL Signal
        Generated when the short SMA crosses BELOW the long SMA.

    HOLD Signal
        Generated on all other rows.

    Parameters
    ----------
    df : pandas.DataFrame
        Market data DataFrame.

    short_period : int, default=20
        Short-term SMA period.

    long_period : int, default=50
        Long-term SMA period.

    price_column : str, default="Close"
        Column used for SMA calculations if indicators
        need to be generated.

    Returns
    -------
    pandas.DataFrame
        Copy of the supplied DataFrame containing:

        - original columns
        - required SMA columns
        - Signal column

    Raises
    ------
    ValueError
        If:

        - DataFrame is empty.
        - short_period >= long_period.
    """

    logger.info(
        "Generating SMA crossover signals "
        "(short=%s, long=%s).",
        short_period,
        long_period,
    )

    # ------------------------------------------------------------------
    # Strategy validation
    # ------------------------------------------------------------------

    if df.empty:
        logger.error("Input DataFrame is empty.")
        raise ValueError("Input DataFrame cannot be empty.")

    if short_period >= long_period:
        logger.error(
            "Invalid SMA configuration: "
            "short_period=%s long_period=%s",
            short_period,
            long_period,
        )
        raise ValueError(
            "short_period must be smaller than long_period."
        )

    result_df = df.copy()

    short_column = f"SMA{short_period}"
    long_column = f"SMA{long_period}"

    # ------------------------------------------------------------------
    # Ensure indicators exist
    # ------------------------------------------------------------------

    if short_column not in result_df.columns:
        logger.debug("%s not found. Calculating.", short_column)
        result_df = calculate_sma(
            result_df,
            period=short_period,
            price_column=price_column,
        )

    if long_column not in result_df.columns:
        logger.debug("%s not found. Calculating.", long_column)
        result_df = calculate_sma(
            result_df,
            period=long_period,
            price_column=price_column,
        )

    # ------------------------------------------------------------------
    # Generate signals
    # ------------------------------------------------------------------

    result_df["Signal"] = "HOLD"

    previous_short = result_df[short_column].shift(1)
    previous_long = result_df[long_column].shift(1)

    current_short = result_df[short_column]
    current_long = result_df[long_column]

    buy_mask = (
        (previous_short <= previous_long)
        & (current_short > current_long)
    )

    sell_mask = (
        (previous_short >= previous_long)
        & (current_short < current_long)
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