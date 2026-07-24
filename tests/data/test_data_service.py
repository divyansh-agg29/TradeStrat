"""
Unit tests for the Market Data service.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from data.service import get_stock_data


@patch("data.service.retrieve_market_data")
@patch("data.service.initialize_db")
@patch("data.service.validate_request")
def test_get_stock_data_success(
    mock_validate_request,
    mock_initialize_db,
    mock_retrieve,
):
    """
    Verify that the service validates the request, initialises the
    database, and delegates to retrieve_market_data.
    """
    import data.service as svc
    svc._DB_CONN = None

    cleaned_df = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [105.0],
            "Low": [99.0],
            "Close": [104.0],
            "Volume": [1000],
        }
    )

    mock_conn = MagicMock()
    mock_initialize_db.return_value = mock_conn
    mock_retrieve.return_value = cleaned_df

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

    mock_initialize_db.assert_called_once()

    mock_retrieve.assert_called_once_with(
        ticker="RELIANCE.NS",
        start_date="2024-01-01",
        end_date="2024-12-31",
        conn=mock_conn,
    )

    pd.testing.assert_frame_equal(result, cleaned_df)


@patch("data.service.retrieve_market_data")
@patch("data.service.initialize_db")
@patch("data.service.validate_request")
def test_get_stock_data_validation_failure(
    mock_validate_request,
    mock_initialize_db,
    mock_retrieve,
):
    """
    Verify that validation errors are propagated and no
    further processing occurs.
    """
    import data.service as svc
    svc._DB_CONN = None

    mock_validate_request.side_effect = ValueError("Invalid request.")

    with pytest.raises(ValueError, match="Invalid request."):
        get_stock_data(
            "INVALID",
            "2024-01-01",
            "2024-12-31",
        )

    mock_initialize_db.assert_not_called()
    mock_retrieve.assert_not_called()


@patch("data.service.retrieve_market_data")
@patch("data.service.initialize_db")
@patch("data.service.validate_request")
def test_get_stock_data_retrieval_failure(
    mock_validate_request,
    mock_initialize_db,
    mock_retrieve,
):
    """
    Verify that errors from retrieve_market_data are propagated.
    """
    import data.service as svc
    svc._DB_CONN = None

    mock_conn = MagicMock()
    mock_initialize_db.return_value = mock_conn
    mock_retrieve.side_effect = ConnectionError("Download failed.")

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
    mock_initialize_db.assert_called_once()
    mock_retrieve.assert_called_once()


@patch("data.service.retrieve_market_data")
@patch("data.service.initialize_db")
@patch("data.service.validate_request")
def test_get_stock_data_cleaning_failure(
    mock_validate_request,
    mock_initialize_db,
    mock_retrieve,
):
    """
    Verify that cleaning errors (raised inside retrieve_market_data)
    are propagated.
    """
    import data.service as svc
    svc._DB_CONN = None

    mock_conn = MagicMock()
    mock_initialize_db.return_value = mock_conn
    mock_retrieve.side_effect = ValueError("Invalid market data.")

    with pytest.raises(
        ValueError,
        match="Invalid market data.",
    ):
        get_stock_data(
            "RELIANCE.NS",
            "2024-01-01",
            "2024-12-31",
        )

    mock_validate_request.assert_called_once()
    mock_initialize_db.assert_called_once()
    mock_retrieve.assert_called_once()


@patch("data.service.retrieve_market_data")
@patch("data.service.initialize_db")
@patch("data.service.validate_request")
def test_db_connection_reused_across_calls(
    mock_validate_request,
    mock_initialize_db,
    mock_retrieve,
):
    """
    Verify that initialize_db is called only once even when
    get_stock_data is called multiple times.
    """
    import data.service as svc
    svc._DB_CONN = None

    mock_conn = MagicMock()
    mock_initialize_db.return_value = mock_conn
    mock_retrieve.return_value = pd.DataFrame()

    get_stock_data("RELIANCE.NS", "2024-01-01", "2024-06-30")
    get_stock_data("TCS.NS", "2024-01-01", "2024-06-30")

    mock_initialize_db.assert_called_once()
    assert mock_retrieve.call_count == 2