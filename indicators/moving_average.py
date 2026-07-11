"""
Moving Average Indicator Module.

This module provides reusable functions for calculating moving average indicators
on standardized market data.

Currently implemented indicators:
- Simple Moving Average (SMA)

The functions in this module are intentionally independent of trading strategy,
portfolio simulation, and analytics. Their sole responsibility is to compute
technical indicators and append them to a copy of the supplied DataFrame.
"""

import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)


def calculate_sma(df: pd.DataFrame, period: int, price_column: str = "Close") -> pd.DataFrame:
    """
    Calculate a Simple Moving Average (SMA) and append it to a copy of the
    supplied DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Standardized market data DataFrame.

    period : int
        Number of periods used for the moving average.
        Must be a positive integer.

    price_column : str, default="Close"
        Column on which the moving average will be calculated.

    Returns
    -------
    pandas.DataFrame
        A copy of the original DataFrame with an additional SMA column.

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
        If the SMA column already exists.
    """

    logger.info("Starting SMA calculation (period=%s).", period)

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

    indicator_column = f"SMA{period}"

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

    result_df[indicator_column] = (
        result_df[price_column]
        .rolling(window=period)
        .mean()
    )

    logger.info(
        "Successfully added indicator column '%s'.",
        indicator_column,
    )

    return result_df


def calculate_ema(df: pd.DataFrame, period: int, price_column: str = "Close") -> pd.DataFrame:
    """
    Calculate a Exponential Moving Average (EMA) and append it to a copy of the
    supplied DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Standardized market data DataFrame.

    period : int
        Number of periods used for the moving average.
        Must be a positive integer.

    price_column : str, default="Close"
        Column on which the moving average will be calculated.

    Returns
    -------
    pandas.DataFrame
        A copy of the original DataFrame with an additional EMA column.

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
        If the EMA column already exists.
    """

    logger.info("Starting EMA calculation (period=%s).", period)

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

    indicator_column = f"EMA{period}"

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

    result_df[indicator_column] = (
        result_df[price_column]
        .ewm(span=period, adjust=False)
        .mean()
    )

    logger.info(
        "Successfully added indicator column '%s'.",
        indicator_column,
    )

    return result_df