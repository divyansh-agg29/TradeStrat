"""
Momentum Indicator Module.

This module provides reusable functions for calculating momentum indicators
on standardized market data.

Currently implemented indicators:
- Relative Strength Index (RSI)

The functions in this module are intentionally independent of trading strategy,
portfolio simulation, and analytics. Their sole responsibility is to compute
technical indicators and append them to a copy of the supplied DataFrame.
"""

import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)


def calculate_rsi(df: pd.DataFrame, period: int = 14, price_column: str = "Close") -> pd.DataFrame:
    """
    Calculate the Relative Strength Index (RSI) and append it to a copy of the
    supplied DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Standardized market data DataFrame.

    period : int, default=14
        Number of periods used for the RSI calculation.
        Must be a positive integer.

    price_column : str, default="Close"
        Column on which the RSI will be calculated.

    Returns
    -------
    pandas.DataFrame
        A copy of the original DataFrame with an additional RSI column.

    Raises
    ------
    TypeError
        If df is not a pandas DataFrame.

    TypeError
        If period is not an integer.

    ValueError
        If period is less than or equal to zero.

    ValueError
        If price_column does not exist.

    ValueError
        If the RSI column already exists.
    """

    logger.info("Starting RSI calculation (period=%s).", period)

    # Validate DataFrame
    if not isinstance(df, pd.DataFrame):
        logger.error("Input must be a pandas DataFrame.")
        raise TypeError("Input must be a pandas DataFrame.")

    # Validate period
    if not isinstance(period, int):
        logger.error("Period must be an integer.")
        raise TypeError("Period must be an integer.")

    if period <= 0:
        logger.error("Period must be greater than zero.")
        raise ValueError("Period must be greater than zero.")

    # Validate price column
    if price_column not in df.columns:
        logger.error("Price column '%s' not found.", price_column)
        raise ValueError(f"Price column '{price_column}' not found.")

    indicator_column = f"RSI{period}"

    # Prevent duplicate indicators
    if indicator_column in df.columns:
        logger.error("Indicator column '%s' already exists.", indicator_column)
        raise ValueError(
            f"Indicator column '{indicator_column}' already exists."
        )

    logger.debug(
        "Calculating %s using '%s' prices.",
        indicator_column,
        price_column,
    )

    result_df = df.copy()

    # Price changes
    delta = result_df[price_column].diff()

    # Separate gains and losses
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder's exponential moving averages
    average_gain = gain.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()

    average_loss = loss.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period,
    ).mean()

    # Relative Strength
    rs = average_gain / average_loss

    # Relative Strength Index
    result_df[indicator_column] = 100 - (100 / (1 + rs))

    logger.info(
        "Successfully added indicator column '%s'.",
        indicator_column,
    )

    return result_df

def calculate_macd(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9, price_column: str = "Close",) -> pd.DataFrame:
    """
    Calculate the Moving Average Convergence Divergence (MACD) indicator
    and append it to a copy of the supplied DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Standardized market data DataFrame.

    fast_period : int, default=12
        Period for the fast EMA.

    slow_period : int, default=26
        Period for the slow EMA.

    signal_period : int, default=9
        Period for the signal EMA.

    price_column : str, default="Close"
        Column on which the MACD will be calculated.

    Returns
    -------
    pandas.DataFrame
        Copy of the original DataFrame with additional MACD columns.

    Raises
    ------
    TypeError
        If df is not a pandas DataFrame.

    TypeError
        If any period is not an integer.

    ValueError
        If any period is less than or equal to zero.

    ValueError
        If fast_period >= slow_period.

    ValueError
        If price_column does not exist.

    ValueError
        If any MACD output column already exists.
    """

    logger.info(
        "Starting MACD calculation (fast=%s, slow=%s, signal=%s).",
        fast_period,
        slow_period,
        signal_period,
    )

    # Validate DataFrame
    if not isinstance(df, pd.DataFrame):
        logger.error("Input must be a pandas DataFrame.")
        raise TypeError("Input must be a pandas DataFrame.")

    # Validate periods
    for name, value in {
        "fast_period": fast_period,
        "slow_period": slow_period,
        "signal_period": signal_period,
    }.items():

        if not isinstance(value, int):
            logger.error("%s must be an integer.", name)
            raise TypeError(f"{name} must be an integer.")

        if value <= 0:
            logger.error("%s must be greater than zero.", name)
            raise ValueError(f"{name} must be greater than zero.")

    if fast_period >= slow_period:
        logger.error("fast_period must be less than slow_period.")
        raise ValueError("fast_period must be less than slow_period.")

    # Validate price column
    if price_column not in df.columns:
        logger.error("Price column '%s' not found.", price_column)
        raise ValueError(f"Price column '{price_column}' not found.")

    macd_column = (
        f"MACD_{fast_period}_{slow_period}"
    )
    signal_column = (
        f"MACD_Signal_{signal_period}"
    )
    histogram_column = "MACD_Histogram"

    for column in (
        macd_column,
        signal_column,
        histogram_column,
    ):
        if column in df.columns:
            logger.error(
                "Indicator column '%s' already exists.",
                column,
            )
            raise ValueError(
                f"Indicator column '{column}' already exists."
            )

    logger.debug(
        "Calculating MACD using '%s' prices.",
        price_column,
    )

    result_df = df.copy()

    fast_ema = (
        result_df[price_column]
        .ewm(span=fast_period, adjust=False)
        .mean()
    )

    slow_ema = (
        result_df[price_column]
        .ewm(span=slow_period, adjust=False)
        .mean()
    )

    result_df[macd_column] = fast_ema - slow_ema

    result_df[signal_column] = (
        result_df[macd_column]
        .ewm(span=signal_period, adjust=False)
        .mean()
    )

    result_df[histogram_column] = (
        result_df[macd_column]
        - result_df[signal_column]
    )

    logger.info(
        "Successfully added MACD indicator columns."
    )

    return result_df