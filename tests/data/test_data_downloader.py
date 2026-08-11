"""
Unit tests for the Market Data downloader.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from data.downloader import download_stock_data


@patch("data.downloader.yf.Ticker")
def test_download_stock_data_success(mock_ticker):
    """
    Verify that market data is downloaded successfully.
    """
    mock_history = pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [105.0, 106.0],
            "Low": [99.0, 100.0],
            "Close": [104.0, 105.0],
            "Volume": [1000, 1200],
        }
    )

    mock_stock = MagicMock()
    mock_stock.history.return_value = mock_history
    mock_ticker.return_value = mock_stock

    data = download_stock_data(
        "RELIANCE.NS",
        "2024-01-01",
        "2024-12-31",
    )

    mock_ticker.assert_called_once_with("RELIANCE.NS")

    mock_stock.history.assert_called_once_with(
        start="2024-01-01",
        end="2024-12-31",
    )

    pd.testing.assert_frame_equal(data, mock_history)


@patch("data.downloader.yf.Ticker")
def test_download_stock_data_empty_dataframe(mock_ticker):
    """
    Verify that an empty DataFrame raises ValueError.
    """
    mock_stock = MagicMock()
    mock_stock.history.return_value = pd.DataFrame()
    mock_ticker.return_value = mock_stock

    with pytest.raises(
        ValueError,
        match="No historical market data found",
    ):
        download_stock_data(
            "RELIANCE.NS",
            "2024-01-01",
            "2024-12-31",
        )


@patch("data.downloader.time.sleep")
@patch("data.downloader.yf.Ticker")
def test_download_stock_data_connection_error(mock_ticker, mock_sleep):
    """
    Verify that download failures raise ConnectionError after retries.
    """
    mock_ticker.side_effect = Exception("Yahoo Finance unavailable")

    with pytest.raises(
        ConnectionError,
        match="Failed to download market data.*after 3 attempts",
    ):
        download_stock_data(
            "RELIANCE.NS",
            "2024-01-01",
            "2024-12-31",
        )

    assert mock_ticker.call_count == 3
    assert mock_sleep.call_count == 2


@patch("data.downloader.time.sleep")
@patch("data.downloader.yf.Ticker")
def test_download_stock_data_retry_success(mock_ticker, mock_sleep):
    """
    Verify that download succeeds on retry after initial failure.
    """
    mock_history = pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [105.0, 106.0],
            "Low": [99.0, 100.0],
            "Close": [104.0, 105.0],
            "Volume": [1000, 1200],
        }
    )

    mock_stock_success = MagicMock()
    mock_stock_success.history.return_value = mock_history

    mock_ticker.side_effect = [
        Exception("Temporary failure"),
        mock_stock_success,
    ]

    data = download_stock_data(
        "RELIANCE.NS",
        "2024-01-01",
        "2024-12-31",
    )

    assert mock_ticker.call_count == 2
    assert mock_sleep.call_count == 1
    mock_sleep.assert_called_once_with(1.0)
    pd.testing.assert_frame_equal(data, mock_history)