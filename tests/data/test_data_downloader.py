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


@patch("data.downloader.yf.Ticker")
def test_download_stock_data_connection_error(mock_ticker):
    """
    Verify that download failures raise ConnectionError.
    """
    mock_ticker.side_effect = Exception("Yahoo Finance unavailable")

    with pytest.raises(
        ConnectionError,
        match="Failed to download market data",
    ):
        download_stock_data(
            "RELIANCE.NS",
            "2024-01-01",
            "2024-12-31",
        )