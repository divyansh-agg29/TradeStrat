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