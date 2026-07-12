"""
MACD Crossover Strategy

This module implements the Moving Average Convergence Divergence (MACD) crossover trading strategy.

The strategy generates BUY, SELL and HOLD signals based on crossover events
between a MACD line and MACD Signal line.

Responsibilities
----------------
- Validate strategy-specific inputs.
- Ensure required MACD indicators are available.
- Generate crossover signals.
- Return an enriched copy of the input DataFrame.
"""

import pandas as pd

from indicators.momentum import calculate_macd
from utils.logger import get_logger

logger = get_logger(__name__)


def generate_macd_crossover_signals(
    df: pd.DataFrame,
    short_period: int = 12,
    long_period: int = 26,
    signal_period=9,
    price_column: str = "Close",
) -> pd.DataFrame:
    """
    Generate trading signals using the MACD crossover strategy.

    BUY Signal
        Generated when the MACD crosses ABOVE the Signal.

    SELL Signal
        Generated when the MACD crosses BELOW the Signal.

    HOLD Signal
        Generated on all other rows.

    Parameters
    ----------
    df : pandas.DataFrame
        Market data DataFrame.

    short_period : int, default=12
        Short-term EMA period.

    long_period : int, default=26
        Long-term EMA period.

    signal_period : int, default=9
        Signal line EMA period.

    price_column : str, default="Close"
        Column used for EMA calculations if indicators
        need to be generated.

    Returns
    -------
    pandas.DataFrame
        Copy of the supplied DataFrame containing:

        - original columns
        - required MACD columns
        - Signal column

    Raises
    ------
    ValueError
        If:

        - DataFrame is empty.
        - short_period >= long_period.
    """

    logger.info(
        "Generating MACD crossover signals "
        "(short=%s, long=%s, signal=%s).",
        short_period,
        long_period,
        signal_period,
    )

    # ------------------------------------------------------------------
    # Strategy validation
    # ------------------------------------------------------------------

    if df.empty:
        logger.error("Input DataFrame is empty.")
        raise ValueError("Input DataFrame cannot be empty.")

    if short_period >= long_period:
        logger.error(
            "Invalid MACD configuration: "
            "short_period=%s long_period=%s",
            short_period,
            long_period,
        )
        raise ValueError(
            "short_period must be smaller than long_period."
        )

    result_df = df.copy()

    macd_column = f"MACD_{short_period}_{long_period}_{signal_period}"
    signal_column = f"MACD_Signal_{short_period}_{long_period}_{signal_period}"
    histogram_column = f"MACD_Histogram_{short_period}_{long_period}_{signal_period}"

    # ------------------------------------------------------------------
    # Ensure indicators exist
    # ------------------------------------------------------------------

    if any([macd_column,signal_column,histogram_column]) not in result_df.columns:
        logger.debug("MACD not found. Calculating.")
        result_df = calculate_macd(
            result_df,
            fast_period=short_period,
            slow_period=long_period,
            signal_period=signal_period,
            price_column=price_column,
        )

    # ------------------------------------------------------------------
    # Generate signals
    # ------------------------------------------------------------------

    result_df["Signal"] = "HOLD"

    previous_macd = result_df[macd_column].shift(1)
    previous_signal = result_df[signal_column].shift(1)

    current_macd = result_df[macd_column]
    current_signal = result_df[signal_column]

    buy_mask = (
        (previous_macd <= previous_signal)
        & (current_macd > current_signal)
    )

    sell_mask = (
        (previous_macd >= previous_signal)
        & (current_macd < current_signal)
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