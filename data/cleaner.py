"""
Market data cleaning utilities.

This module is responsible for converting raw market data downloaded from
Yahoo Finance into the standardized format expected by the rest of the
application.

Data Contract
-------------
Any DataFrame returned by this module is guaranteed to:

- Use a DatetimeIndex named "Date"
- Be sorted in ascending chronological order
- Contain only the approved columns
- Have no duplicate timestamps
- Contain no missing values
- Use consistent numeric data types
"""

import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)

REQUIRED_COLUMNS = [
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
]

OPTIONAL_COLUMNS = [
    "Dividends",
    "Stock Splits",
    "Capital Gains",
]


def clean_market_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize downloaded market data.

    Args:
        df: Raw DataFrame returned by Yahoo Finance.

    Returns:
        Standardized DataFrame.

    Raises:
        ValueError:
            If the DataFrame violates the expected data contract.
    """
    logger.info("Cleaning downloaded market data.")

    cleaned_df = df.copy()

    _validate_required_columns(cleaned_df)

    cleaned_df = _remove_unwanted_columns(cleaned_df)

    cleaned_df = _standardize_index(cleaned_df)

    cleaned_df = _remove_duplicate_dates(cleaned_df)

    _validate_missing_values(cleaned_df)

    cleaned_df = _standardize_numeric_types(cleaned_df)    

    _validate_output(cleaned_df)

    logger.info("Market data cleaning completed successfully.")

    return cleaned_df


def _validate_required_columns(df: pd.DataFrame) -> None:
    """
    Ensure all required columns are present.
    """
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def _remove_unwanted_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove columns that are not required by Version 1.
    """
    return df.drop(
        columns=OPTIONAL_COLUMNS,
        errors="ignore",
    )


def _standardize_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure the DataFrame uses a DatetimeIndex named 'Date'.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    df.index.name = "Date"

    return df.sort_index()


def _remove_duplicate_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate timestamps while keeping the first occurrence.
    """
    return df.loc[~df.index.duplicated(keep="first")]


def _standardize_numeric_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize numeric column types.
    """
    float_columns = [
        "Open",
        "High",
        "Low",
        "Close",
    ]

    for column in float_columns:
        df[column] = df[column].astype(float)

    df["Volume"] = df["Volume"].astype(int)

    return df


def _validate_missing_values(df: pd.DataFrame) -> None:
    """
    Ensure the DataFrame contains no missing values.
    """
    if df.isnull().values.any():
        raise ValueError(
            "Downloaded market data contains missing values."
        )


def _validate_output(df: pd.DataFrame) -> None:
    """
    Validate that the cleaned DataFrame satisfies the project data contract.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError(
            "Market data index must be a DatetimeIndex."
        )

    if df.index.name != "Date":
        raise ValueError(
            "Market data index must be named 'Date'."
        )

    if not df.index.is_monotonic_increasing:
        raise ValueError(
            "Market data must be sorted chronologically."
        )

    if df.index.has_duplicates:
        raise ValueError(
            "Market data contains duplicate timestamps."
        )

    if list(df.columns) != REQUIRED_COLUMNS:
        raise ValueError(
            "Market data columns do not match the required schema."
        )