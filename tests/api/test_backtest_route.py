"""
Tests for the REST API.
"""

from unittest.mock import patch

import pytest

from app import create_app
from config import TestConfig

@pytest.fixture
def client():
    """
    Create a Flask test client.
    """
    app = create_app(TestConfig)


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


@patch("api.routes.serialize_backtest_result")
@patch("api.routes.run_backtest")
def test_backtest_parses_stop_loss_risk_settings(
    mock_run_backtest,
    mock_serializer,
    client,
):
    """
    Backtest route should parse stop-loss settings into RiskConfig.
    """

    payload = _create_request_payload()
    payload["risk"] = {
        "stop_loss_type": "fixed_percentage",
        "parameters": {"percent": 0.05},
    }

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
        json=payload,
    )

    request_arg = mock_run_backtest.call_args.args[0]

    assert response.status_code == 200
    assert request_arg.risk.stop_loss_type == "fixed_percentage"
    assert request_arg.risk.stop_loss_parameters == {"percent": 0.05}


@patch("api.routes.serialize_backtest_result")
@patch("api.routes.run_backtest")
def test_backtest_without_risk_settings_uses_default_mode(
    mock_run_backtest,
    mock_serializer,
    client,
):
    """
    Omitting risk settings should leave the request risk config unset.
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

    request_arg = mock_run_backtest.call_args.args[0]

    assert response.status_code == 200
    assert request_arg.risk is None


@patch("api.routes.serialize_backtest_result")
@patch("api.routes.run_backtest")
def test_backtest_parses_fixed_price_offset_risk_settings(
    mock_run_backtest,
    mock_serializer,
    client,
):
    """
    Backtest route should parse fixed price offset stop-loss settings.
    """

    payload = _create_request_payload()
    payload["risk"] = {
        "stop_loss_type": "fixed_price_offset",
        "parameters": {"offset": 50},
    }

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
        json=payload,
    )

    request_arg = mock_run_backtest.call_args.args[0]

    assert response.status_code == 200
    assert request_arg.risk.stop_loss_type == "fixed_price_offset"
    assert request_arg.risk.stop_loss_parameters == {"offset": 50}


@patch("api.routes.serialize_backtest_result")
@patch("api.routes.run_backtest")
def test_backtest_parses_trailing_stop_risk_settings(
    mock_run_backtest,
    mock_serializer,
    client,
):
    """
    Backtest route should parse trailing stop-loss settings.
    """

    payload = _create_request_payload()
    payload["risk"] = {
        "stop_loss_type": "trailing_stop",
        "parameters": {"percent": 0.05},
    }

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
        json=payload,
    )

    request_arg = mock_run_backtest.call_args.args[0]

    assert response.status_code == 200
    assert request_arg.risk.stop_loss_type == "trailing_stop"
    assert request_arg.risk.stop_loss_parameters == {"percent": 0.05}


@patch("api.routes.serialize_backtest_result")
@patch("api.routes.run_backtest")
def test_backtest_parses_take_profit_risk_settings(
    mock_run_backtest,
    mock_serializer,
    client,
):
    """
    Backtest route should parse take-profit settings.
    """

    payload = _create_request_payload()
    payload["risk"] = {
        "take_profit_type": "fixed_percentage",
        "take_profit_parameters": {"percent": 0.20},
    }

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
        json=payload,
    )

    request_arg = mock_run_backtest.call_args.args[0]

    assert response.status_code == 200
    assert request_arg.risk.take_profit_type == "fixed_percentage"
    assert request_arg.risk.take_profit_parameters == {"percent": 0.20}


@patch("api.routes.serialize_backtest_result")
@patch("api.routes.run_backtest")
def test_backtest_parses_combined_stop_loss_and_take_profit(
    mock_run_backtest,
    mock_serializer,
    client,
):
    """
    Backtest route should parse both stop-loss and take-profit together.
    """

    payload = _create_request_payload()
    payload["risk"] = {
        "stop_loss_type": "fixed_percentage",
        "parameters": {"percent": 0.05},
        "take_profit_type": "fixed_percentage",
        "take_profit_parameters": {"percent": 0.20},
    }

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
        json=payload,
    )

    request_arg = mock_run_backtest.call_args.args[0]

    assert response.status_code == 200
    assert request_arg.risk.stop_loss_type == "fixed_percentage"
    assert request_arg.risk.stop_loss_parameters == {"percent": 0.05}
    assert request_arg.risk.take_profit_type == "fixed_percentage"
    assert request_arg.risk.take_profit_parameters == {"percent": 0.20}


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


@patch("api.routes.serialize_backtest_result")
@patch("api.routes.run_backtest")
def test_backtest_parses_position_sizing_settings(
    mock_run_backtest,
    mock_serializer,
    client,
):
    """
    Backtest route should parse position sizing settings
    into PositionSizingConfig.
    """

    payload = _create_request_payload()
    payload["position_sizing"] = {
        "sizing_type": "fixed_percentage",
        "parameters": {"percent": 0.25},
    }

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
        json=payload,
    )

    request_arg = mock_run_backtest.call_args.args[0]

    assert response.status_code == 200
    assert request_arg.position_sizing.sizing_type == "fixed_percentage"
    assert request_arg.position_sizing.sizing_parameters == {"percent": 0.25}


@patch("api.routes.serialize_backtest_result")
@patch("api.routes.run_backtest")
def test_backtest_parses_fixed_amount_position_sizing(
    mock_run_backtest,
    mock_serializer,
    client,
):
    """
    Backtest route should parse fixed amount position sizing.
    """

    payload = _create_request_payload()
    payload["position_sizing"] = {
        "sizing_type": "fixed_amount",
        "parameters": {"amount": 10000},
    }

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
        json=payload,
    )

    request_arg = mock_run_backtest.call_args.args[0]

    assert response.status_code == 200
    assert request_arg.position_sizing.sizing_type == "fixed_amount"
    assert request_arg.position_sizing.sizing_parameters == {"amount": 10000}


@patch("api.routes.serialize_backtest_result")
@patch("api.routes.run_backtest")
def test_backtest_without_position_sizing_defaults_to_none(
    mock_run_backtest,
    mock_serializer,
    client,
):
    """
    Omitting position sizing should leave the field as None.
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

    request_arg = mock_run_backtest.call_args.args[0]

    assert response.status_code == 200
    assert request_arg.position_sizing is None


@patch("api.routes.serialize_backtest_result")
@patch("api.routes.run_backtest")
def test_backtest_parses_combined_risk_and_position_sizing(
    mock_run_backtest,
    mock_serializer,
    client,
):
    """
    Backtest route should parse both risk and position sizing together.
    """

    payload = _create_request_payload()
    payload["risk"] = {
        "stop_loss_type": "fixed_percentage",
        "parameters": {"percent": 0.05},
    }
    payload["position_sizing"] = {
        "sizing_type": "fixed_shares",
        "parameters": {"shares": 100},
    }

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
        json=payload,
    )

    request_arg = mock_run_backtest.call_args.args[0]

    assert response.status_code == 200
    assert request_arg.risk.stop_loss_type == "fixed_percentage"
    assert request_arg.position_sizing.sizing_type == "fixed_shares"
    assert request_arg.position_sizing.sizing_parameters == {"shares": 100}
