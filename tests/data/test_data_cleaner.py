"""
Unit tests for the Market Data cleaner.
"""

import pandas as pd
import pytest

from data.cleaner import clean_market_data


def create_sample_dataframe() -> pd.DataFrame:
    """
    Create a valid sample DataFrame for testing.
    """
    dates = pd.to_datetime(
        [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
        ]
    )

    return pd.DataFrame(
        {
            "Open": [100, 101, 102],
            "High": [105, 106, 107],
            "Low": [99, 100, 101],
            "Close": [104, 105, 106],
            "Volume": [1000, 1200, 1300],
            "Dividends": [0, 0, 0],
            "Stock Splits": [0, 0, 0],
        },
        index=dates,
    )


# ---------------------------------------------------------------------
# Successful Cleaning
# ---------------------------------------------------------------------


def test_clean_market_data_success():
    """
    Verify that valid market data is cleaned successfully.
    """
    df = create_sample_dataframe()

    cleaned_df = clean_market_data(df)

    expected_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    assert list(cleaned_df.columns) == expected_columns
    assert isinstance(cleaned_df.index, pd.DatetimeIndex)
    assert cleaned_df.index.name == "Date"
    assert cleaned_df.index.is_monotonic_increasing
    assert not cleaned_df.index.has_duplicates
    assert not cleaned_df.isnull().values.any()


# ---------------------------------------------------------------------
# Required Columns
# ---------------------------------------------------------------------


def test_missing_required_column():
    """
    Missing required columns should raise ValueError.
    """
    df = create_sample_dataframe().drop(columns=["Close"])

    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        clean_market_data(df)


# ---------------------------------------------------------------------
# Remove Unwanted Columns
# ---------------------------------------------------------------------


def test_remove_unwanted_columns():
    """
    Verify unwanted columns are removed.
    """
    df = create_sample_dataframe()

    cleaned_df = clean_market_data(df)

    assert "Dividends" not in cleaned_df.columns
    assert "Stock Splits" not in cleaned_df.columns


# ---------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------


def test_sort_by_date():
    """
    Data should be sorted chronologically.
    """
    df = create_sample_dataframe()

    df = df.sample(frac=1)

    cleaned_df = clean_market_data(df)

    assert cleaned_df.index.is_monotonic_increasing


# ---------------------------------------------------------------------
# Duplicate Dates
# ---------------------------------------------------------------------


def test_remove_duplicate_dates():
    """
    Duplicate timestamps should be removed.
    """
    df = create_sample_dataframe()

    duplicate_row = df.iloc[[0]]

    df = pd.concat([df, duplicate_row])

    cleaned_df = clean_market_data(df)

    assert not cleaned_df.index.has_duplicates
    assert len(cleaned_df) == 3


# ---------------------------------------------------------------------
# Missing Values
# ---------------------------------------------------------------------


def test_missing_values():
    """
    Missing values should raise ValueError.
    """
    df = create_sample_dataframe()

    df.loc[df.index[1], "Close"] = None

    with pytest.raises(
        ValueError,
        match="Downloaded market data contains missing values",
    ):
        clean_market_data(df)


# ---------------------------------------------------------------------
# Numeric Types
# ---------------------------------------------------------------------


def test_numeric_types():
    """
    Numeric columns should be standardized.
    """
    df = create_sample_dataframe()

    cleaned_df = clean_market_data(df)

    assert pd.api.types.is_float_dtype(cleaned_df["Open"])
    assert pd.api.types.is_float_dtype(cleaned_df["High"])
    assert pd.api.types.is_float_dtype(cleaned_df["Low"])
    assert pd.api.types.is_float_dtype(cleaned_df["Close"])

    assert pd.api.types.is_integer_dtype(cleaned_df["Volume"])