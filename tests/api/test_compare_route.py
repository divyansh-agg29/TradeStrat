"""
Tests for the POST /compare API route.
"""

from unittest.mock import patch, MagicMock

import pytest

from app import app
from models import BacktestResult


@pytest.fixture
def client():
    """
    Create a Flask test client.
    """

    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def _create_compare_payload(num_strategies=2):
    """
    Create a valid comparison request payload.
    """

    strategy_configs = [
        {"type": "sma_crossover", "parameters": {"short_period": 20, "long_period": 50}},
        {"type": "ema_crossover", "parameters": {"short_period": 12, "long_period": 26}},
        {"type": "macd_crossover", "parameters": {}},
        {"type": "rsi_mean_reversion", "parameters": {"rsi_period": 14, "oversold": 30, "overbought": 70}},
        {"type": "sma_crossover", "parameters": {"short_period": 10, "long_period": 30}},
        {"type": "ema_crossover", "parameters": {"short_period": 9, "long_period": 21}},
        {"type": "sma_crossover", "parameters": {"short_period": 5, "long_period": 15}},
    ]

    return {
        "ticker": "RELIANCE.NS",
        "start_date": "2022-01-01",
        "end_date": "2023-01-01",
        "initial_capital": 100000,
        "risk_free_rate": 0.06,
        "strategies": strategy_configs[:num_strategies],
    }


# ── Success ───────────────────────────────────────────────────


@patch("api.routes.serialize_comparison_result")
@patch("api.routes.run_comparison")
def test_compare_endpoint_success(
    mock_run_comparison,
    mock_serializer,
    client,
):
    """
    A valid comparison request should return HTTP 200.
    """

    mock_run_comparison.return_value = MagicMock()

    mock_serializer.return_value = {
        "common": {
            "ticker": "RELIANCE.NS",
            "start_date": "2022-01-01",
            "end_date": "2023-01-01",
            "initial_capital": 100000,
            "risk_free_rate": 0.06,
        },
        "benchmark": None,
        "results": [
            {"strategy": {"type": "sma_crossover"}, "success": True},
            {"strategy": {"type": "ema_crossover"}, "success": True},
        ],
    }

    response = client.post(
        "/compare",
        json=_create_compare_payload(2),
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert "data" in data
    assert len(data["data"]["results"]) == 2

    mock_run_comparison.assert_called_once()
    mock_serializer.assert_called_once()


# ── Validation Errors ─────────────────────────────────────────


def test_compare_endpoint_invalid_json(client):
    """
    Invalid JSON should return HTTP 400.
    """

    response = client.post(
        "/compare",
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


@patch("api.routes.run_comparison")
def test_compare_endpoint_too_few_strategies(
    mock_run_comparison,
    client,
):
    """
    A payload with fewer than 2 strategies should return HTTP 400.
    """

    mock_run_comparison.side_effect = ValueError(
        "A comparison requires between 2 and 6 strategies."
    )

    response = client.post(
        "/compare",
        json=_create_compare_payload(1),
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False
    assert "2 and 6" in data["error"]["message"]


@patch("api.routes.run_comparison")
def test_compare_endpoint_too_many_strategies(
    mock_run_comparison,
    client,
):
    """
    A payload with more than 6 strategies should return HTTP 400.
    """

    mock_run_comparison.side_effect = ValueError(
        "A comparison requires between 2 and 6 strategies."
    )

    response = client.post(
        "/compare",
        json=_create_compare_payload(7),
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False
    assert "2 and 6" in data["error"]["message"]


@patch("api.routes.run_comparison")
def test_compare_endpoint_missing_ticker(
    mock_run_comparison,
    client,
):
    """
    A missing/empty ticker should return HTTP 400 when the
    service raises a ValueError.
    """

    mock_run_comparison.side_effect = ValueError(
        "Invalid ticker."
    )

    payload = _create_compare_payload(2)
    payload["ticker"] = ""

    response = client.post(
        "/compare",
        json=payload,
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["success"] is False


# ── Partial Failure ───────────────────────────────────────────


@patch("api.routes.serialize_comparison_result")
@patch("api.routes.run_comparison")
def test_compare_endpoint_partial_failure(
    mock_run_comparison,
    mock_serializer,
    client,
):
    """
    When some strategies fail individually, the endpoint should
    still return HTTP 200 with mixed success/failure results.
    """

    mock_run_comparison.return_value = MagicMock()

    mock_serializer.return_value = {
        "common": {},
        "benchmark": None,
        "results": [
            {"strategy": {"type": "sma_crossover"}, "success": True, "error": None},
            {"strategy": {"type": "ema_crossover"}, "success": False, "error": "No trades"},
            {"strategy": {"type": "macd_crossover"}, "success": True, "error": None},
        ],
    }

    response = client.post(
        "/compare",
        json=_create_compare_payload(3),
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True

    results = data["data"]["results"]
    assert results[0]["success"] is True
    assert results[1]["success"] is False
    assert results[1]["error"] == "No trades"
    assert results[2]["success"] is True


# ── Internal Server Error ─────────────────────────────────────


@patch("api.routes.run_comparison")
def test_compare_endpoint_internal_server_error(
    mock_run_comparison,
    client,
):
    """
    Unexpected exceptions should return HTTP 500.
    """

    mock_run_comparison.side_effect = RuntimeError(
        "Unexpected failure."
    )

    response = client.post(
        "/compare",
        json=_create_compare_payload(2),
    )

    assert response.status_code == 500

    data = response.get_json()

    assert data["success"] is False
    assert data["error"]["type"] == "RuntimeError"
    assert (
        data["error"]["message"]
        == "An unexpected internal error occurred."
    )
