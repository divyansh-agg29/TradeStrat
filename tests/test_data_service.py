"""
Unit tests for the Market Data service.
"""

from unittest.mock import patch

import pandas as pd
import pytest

from data.service import get_stock_data


@patch("data.service.download_stock_data")
@patch("data.service.validate_request")
def test_get_stock_data_success(
    mock_validate_request,
    mock_download_stock_data,
):
    """
    Verify that the service validates the request,
    downloads the data, and returns the downloaded DataFrame.
    """
    expected_df = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [105.0],
            "Low": [99.0],
            "Close": [104.0],
            "Volume": [1000],
        }
    )

    mock_download_stock_data.return_value = expected_df

    result = get_stock_data(
        "RELIANCE.NS",
        "2024-01-01",
        "2024-12-31",
    )

    mock_validate_request.assert_called_once_with(
        ticker="RELIANCE.NS",
        start_date="2024-01-01",
        end_date="2024-12-31",
    )

    mock_download_stock_data.assert_called_once_with(
        ticker="RELIANCE.NS",
        start_date="2024-01-01",
        end_date="2024-12-31",
    )

    pd.testing.assert_frame_equal(result, expected_df)


@patch("data.service.download_stock_data")
@patch("data.service.validate_request")
def test_get_stock_data_validation_failure(
    mock_validate_request,
    mock_download_stock_data,
):
    """
    Verify that validation errors are propagated and
    downloading is not attempted.
    """
    mock_validate_request.side_effect = ValueError("Invalid ticker.")

    with pytest.raises(ValueError, match="Invalid ticker."):
        get_stock_data(
            "INVALID",
            "2024-01-01",
            "2024-12-31",
        )

    mock_download_stock_data.assert_not_called()


@patch("data.service.download_stock_data")
@patch("data.service.validate_request")
def test_get_stock_data_download_failure(
    mock_validate_request,
    mock_download_stock_data,
):
    """
    Verify that download errors are propagated after
    successful validation.
    """
    mock_download_stock_data.side_effect = ConnectionError(
        "Download failed."
    )

    with pytest.raises(
        ConnectionError,
        match="Download failed.",
    ):
        get_stock_data(
            "RELIANCE.NS",
            "2024-01-01",
            "2024-12-31",
        )

    mock_validate_request.assert_called_once()