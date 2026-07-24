"""
Unit tests for the Market Data Retriever module.
"""

import os
import tempfile
from unittest.mock import patch

import pandas as pd
import pytest

from data.market_data_store import initialize_db, store_data
from data.retriever import retrieve_market_data


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #


def _make_raw_df(dates):
    """Build a raw yfinance-style DataFrame."""
    n = len(dates)
    return pd.DataFrame(
        {
            "Open": [100.0 + i for i in range(n)],
            "High": [105.0 + i for i in range(n)],
            "Low": [99.0 + i for i in range(n)],
            "Close": [104.0 + i for i in range(n)],
            "Volume": [1000 + i for i in range(n)],
            "Dividends": [0.0] * n,
            "Stock Splits": [0.0] * n,
            "Capital Gains": [0.0] * n,
        },
        index=pd.DatetimeIndex(dates, name="Date"),
    )


def _make_cleaned_df(dates):
    """Build a cleaned DataFrame (only OHLCV columns)."""
    n = len(dates)
    return pd.DataFrame(
        {
            "Open": [100.0 + i for i in range(n)],
            "High": [105.0 + i for i in range(n)],
            "Low": [99.0 + i for i in range(n)],
            "Close": [104.0 + i for i in range(n)],
            "Volume": [1000 + i for i in range(n)],
        },
        index=pd.DatetimeIndex(dates, name="Date"),
    )


@pytest.fixture()
def db_conn():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = initialize_db(path)
    yield conn
    conn.close()
    if os.path.exists(path):
        os.remove(path)


# ------------------------------------------------------------------ #
# Tests
# ------------------------------------------------------------------ #


class TestRetrieveMarketData:

    @patch("data.retriever.clean_market_data")
    @patch("data.retriever.download_stock_data")
    def test_cache_hit_returns_cached_data(
        self,
        mock_download,
        mock_clean,
        db_conn,
    ):
        """When data is cached, downloader should NOT be called."""
        dates = ["2024-01-02", "2024-01-03", "2024-01-04"]
        raw_df = _make_raw_df(dates)
        cleaned_df = _make_cleaned_df(dates)

        store_data(db_conn, "RELIANCE.NS", raw_df, "2024-01-02", "2024-01-04")

        mock_clean.return_value = cleaned_df

        result = retrieve_market_data(
            "RELIANCE.NS", "2024-01-02", "2024-01-04", db_conn,
        )

        mock_download.assert_not_called()
        mock_clean.assert_called_once()
        pd.testing.assert_frame_equal(result, cleaned_df)

    @patch("data.retriever.clean_market_data")
    @patch("data.retriever.download_stock_data")
    def test_cache_miss_downloads_and_stores(
        self,
        mock_download,
        mock_clean,
        db_conn,
    ):
        """When data is NOT cached, downloader should be called."""
        dates = ["2024-01-02", "2024-01-03", "2024-01-04"]
        raw_df = _make_raw_df(dates)
        cleaned_df = _make_cleaned_df(dates)

        mock_download.return_value = raw_df
        mock_clean.return_value = cleaned_df

        result = retrieve_market_data(
            "RELIANCE.NS", "2024-01-02", "2024-01-04", db_conn,
        )

        mock_download.assert_called_once_with(
            ticker="RELIANCE.NS",
            start_date="2024-01-02",
            end_date="2024-01-04",
        )
        mock_clean.assert_called_once()
        pd.testing.assert_frame_equal(result, cleaned_df)

    @patch("data.retriever.clean_market_data")
    @patch("data.retriever.download_stock_data")
    def test_corrupted_cache_falls_through_to_download(
        self,
        mock_download,
        mock_clean,
        db_conn,
    ):
        """
        When cached data fails cleaning, the retriever should fall
        through to download fresh data.
        """
        dates = ["2024-01-02", "2024-01-03"]
        raw_df = _make_raw_df(dates)
        cleaned_df = _make_cleaned_df(dates)

        store_data(db_conn, "RELIANCE.NS", raw_df, "2024-01-02", "2024-01-03")

        # First clean call (on cached data) fails, second (on downloaded) succeeds.
        mock_clean.side_effect = [
            ValueError("Bad cached data"),
            cleaned_df,
        ]
        mock_download.return_value = raw_df

        result = retrieve_market_data(
            "RELIANCE.NS", "2024-01-02", "2024-01-03", db_conn,
        )

        mock_download.assert_called_once()
        assert mock_clean.call_count == 2
        pd.testing.assert_frame_equal(result, cleaned_df)

    @patch("data.retriever.clean_market_data")
    @patch("data.retriever.download_stock_data")
    def test_download_failure_propagates(
        self,
        mock_download,
        mock_clean,
        db_conn,
    ):
        """ConnectionError from downloader should propagate up."""
        mock_download.side_effect = ConnectionError("Network error")

        with pytest.raises(ConnectionError, match="Network error"):
            retrieve_market_data(
                "RELIANCE.NS", "2024-01-02", "2024-01-04", db_conn,
            )

        mock_clean.assert_not_called()
