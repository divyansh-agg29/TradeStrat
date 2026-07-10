"""
Tests for the REST API.
"""

from unittest.mock import patch

import pytest

from app import app


@pytest.fixture
def client():
    """
    Create a Flask test client.
    """

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def _create_request_payload():
    """
    Create a valid backtest request payload.
    """

    return {
        "ticker": "RELIANCE.NS",
        "start_date": "2022-01-01",
        "end_date": "2023-01-01",
        "initial_capital": 100000,
        "risk_free_rate": 0.06,
        "strategy": {
            "type": "sma_crossover",
            "parameters": {
                "short_period": 20,
                "long_period": 50,
            },
        },
    }

def test_health_check(client):
    """
    The health endpoint should return HTTP 200.
    """

    response = client.get("/")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "running"

    assert "message" in data

@patch("api.routes.serialize_backtest_result")
@patch("api.routes.run_backtest")
def test_backtest_success(
    mock_run_backtest,
    mock_serializer,
    client,
):
    """
    A successful backtest request should return HTTP 200.
    """

    mock_run_backtest.return_value = object()

    mock_serializer.return_value = {
        "portfolio_metrics": {},
        "risk_metrics": {},
        "trade_metrics": {},
        "portfolio_history": [],
        "analytics_history": [],
        "trade_history": [],
    }

    response = client.post(
        "/backtest",
        json=_create_request_payload(),
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True

    assert "data" in data

    mock_run_backtest.assert_called_once()

    mock_serializer.assert_called_once()

def test_backtest_missing_strategy(client):
    """
    Missing strategy should return HTTP 400.
    """

    payload = _create_request_payload()

    payload.pop("strategy")

    response = client.post(
        "/backtest",
        json=payload,
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False

    assert "error" in data

def test_backtest_invalid_json(client):
    """
    Invalid JSON should return HTTP 400.
    """

    response = client.post(
        "/backtest",
        data="this is not valid json",
        content_type="application/json",
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False

    assert data["error"]["type"] == "ValueError"

    assert (
        data["error"]["message"]
        == "Request body must contain valid JSON."
    )

@patch("api.routes.run_backtest")
def test_backtest_service_validation_error(
    mock_run_backtest,
    client,
):
    """
    ValueError raised by the Backtest Service should
    return HTTP 400.
    """

    mock_run_backtest.side_effect = ValueError(
        "Invalid ticker."
    )

    response = client.post(
        "/backtest",
        json=_create_request_payload(),
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False

    assert data["error"]["type"] == "ValueError"

    assert data["error"]["message"] == "Invalid ticker."

@patch("api.routes.run_backtest")
def test_backtest_internal_server_error(
    mock_run_backtest,
    client,
):
    """
    Unexpected exceptions should return HTTP 500.
    """

    mock_run_backtest.side_effect = RuntimeError(
        "Unexpected failure."
    )

    response = client.post(
        "/backtest",
        json=_create_request_payload(),
    )

    assert response.status_code == 500

    data = response.get_json()

    assert data["success"] is False

    assert data["error"]["type"] == "RuntimeError"

    assert (
        data["error"]["message"]
        == "An unexpected internal error occurred."
    )