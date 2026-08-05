"""
Tests for the Backtest Serializer.
"""

import math

import pandas as pd
import pytest
from unittest.mock import patch

from analytics import (
    AnalyticsResult,
    BenchmarkMetrics,
    PortfolioMetrics,
    RiskMetrics,
    TradeMetrics,
)
from models import BacktestResult
from portfolio import SimulationResult
from serialization.backtest_serializer import (
    serialize_backtest_result,
    _sanitize_value,
)


# ── Helpers ───────────────────────────────────────────────────


def _make_portfolio_history():
    """
    Create a minimal portfolio history DataFrame.
    """

    dates = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"])
    return pd.DataFrame(
        {
            "Portfolio Value": [100000.0, 101000.0, 102000.0],
            "Close": [500.0, 505.0, 510.0],
            "Cash": [50000.0, 50000.0, 50000.0],
        },
        index=dates,
    )


def _make_analytics_history():
    """
    Create a minimal analytics history DataFrame.
    """

    dates = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"])
    return pd.DataFrame(
        {
            "Portfolio Value": [100000.0, 101000.0, 102000.0],
            "Close": [500.0, 505.0, 510.0],
            "Daily Return %": [0.0, 1.0, 0.99],
            "Drawdown %": [0.0, 0.0, 0.0],
            "Buy & Hold Value": [100000.0, 101000.0, 102000.0],
        },
        index=dates,
    )


def _make_trade_history():
    """
    Create a minimal trade history DataFrame.
    """

    return pd.DataFrame(
        {
            "entry_date": ["2020-01-02"],
            "exit_date": ["2020-01-03"],
            "profit_loss": [1000.0],
            "holding_period": [1],
        }
    )


def _make_backtest_result(
    portfolio_metrics=None,
    risk_metrics=None,
    trade_metrics=None,
    benchmark_metrics=None,
    analytics_history=None,
    portfolio_history=None,
    trade_history=None,
):
    """
    Build a BacktestResult with sensible defaults.
    """

    if portfolio_metrics is None:
        portfolio_metrics = PortfolioMetrics(
            initial_capital=100000.0,
            final_portfolio_value=102000.0,
            profit_loss=2000.0,
            total_return=2.0,
            cagr=5.0,
        )

    if risk_metrics is None:
        risk_metrics = RiskMetrics(
            annualized_volatility=15.0,
            maximum_drawdown=5.0,
            sharpe_ratio=1.2,
            sortino_ratio=1.5,
            calmar_ratio=1.0,
        )

    if trade_metrics is None:
        trade_metrics = TradeMetrics(
            total_trades=1,
            winning_trades=1,
            losing_trades=0,
            win_rate=100.0,
            average_winning_trade=1000.0,
            average_losing_trade=0.0,
            largest_winner=1000.0,
            largest_loser=0.0,
            profit_factor=float("inf"),
            average_holding_period=1.0,
        )

    if benchmark_metrics is None:
        benchmark_metrics = BenchmarkMetrics(
            benchmark_final_value=102000.0,
            benchmark_return=2.0,
            alpha=0.0,
        )

    if analytics_history is None:
        analytics_history = _make_analytics_history()

    if portfolio_history is None:
        portfolio_history = _make_portfolio_history()

    if trade_history is None:
        trade_history = _make_trade_history()

    simulation_result = SimulationResult(
        portfolio_history=portfolio_history,
        trade_history=trade_history,
        summary={
            "initial_capital": 100000.0,
            "final_portfolio_value": 102000.0,
        },
    )

    analytics_result = AnalyticsResult(
        portfolio_metrics=portfolio_metrics,
        risk_metrics=risk_metrics,
        trade_metrics=trade_metrics,
        benchmark_metrics=benchmark_metrics,
        analytics_history=analytics_history,
    )

    return BacktestResult(
        simulation_result=simulation_result,
        analytics_result=analytics_result,
    )


# ── Top-Level Keys ────────────────────────────────────────────


@patch("serialization.backtest_serializer.build_kpi_cards", return_value=[])
def test_output_contains_all_expected_keys(mock_kpi):
    """
    The serialized output should contain all expected top-level keys.
    """

    result = _make_backtest_result()
    output = serialize_backtest_result(result)

    expected_keys = {
        "portfolio_metrics",
        "risk_metrics",
        "trade_metrics",
        "portfolio_history",
        "analytics_history",
        "trade_history",
        "benchmark_metrics",
        "kpi_cards",
        "charts",
    }

    assert set(output.keys()) == expected_keys


# ── Portfolio Metrics ─────────────────────────────────────────


@patch("serialization.backtest_serializer.build_kpi_cards", return_value=[])
def test_portfolio_metrics_serialized(mock_kpi):
    """
    Portfolio metrics should be serialized as a flat dict
    with all fields present.
    """

    result = _make_backtest_result()
    output = serialize_backtest_result(result)

    pm = output["portfolio_metrics"]
    assert pm["initial_capital"] == 100000.0
    assert pm["final_portfolio_value"] == 102000.0
    assert pm["profit_loss"] == 2000.0
    assert pm["total_return"] == 2.0
    assert pm["cagr"] == 5.0


# ── Risk Metrics ──────────────────────────────────────────────


@patch("serialization.backtest_serializer.build_kpi_cards", return_value=[])
def test_risk_metrics_serialized(mock_kpi):
    """
    Risk metrics should be serialized as a flat dict.
    """

    result = _make_backtest_result()
    output = serialize_backtest_result(result)

    rm = output["risk_metrics"]
    assert rm["annualized_volatility"] == 15.0
    assert rm["maximum_drawdown"] == 5.0
    assert rm["sharpe_ratio"] == 1.2
    assert rm["sortino_ratio"] == 1.5
    assert rm["calmar_ratio"] == 1.0


# ── Trade Metrics ─────────────────────────────────────────────


@patch("serialization.backtest_serializer.build_kpi_cards", return_value=[])
def test_trade_metrics_serialized(mock_kpi):
    """
    Trade metrics should be serialized as a flat dict.
    """

    result = _make_backtest_result()
    output = serialize_backtest_result(result)

    tm = output["trade_metrics"]
    assert tm["total_trades"] == 1
    assert tm["winning_trades"] == 1
    assert tm["losing_trades"] == 0
    assert tm["win_rate"] == 100.0


# ── Benchmark Metrics ─────────────────────────────────────────


@patch("serialization.backtest_serializer.build_kpi_cards", return_value=[])
def test_benchmark_metrics_serialized(mock_kpi):
    """
    Benchmark metrics should be serialized as a flat dict.
    """

    result = _make_backtest_result()
    output = serialize_backtest_result(result)

    bm = output["benchmark_metrics"]
    assert bm["benchmark_final_value"] == 102000.0
    assert bm["benchmark_return"] == 2.0
    assert bm["alpha"] == 0.0


# ── Portfolio History ─────────────────────────────────────────


@patch("serialization.backtest_serializer.build_kpi_cards", return_value=[])
def test_portfolio_history_serialized_as_list_of_dicts(mock_kpi):
    """
    Portfolio history should be a list of dicts with the index
    reset as a column.
    """

    result = _make_backtest_result()
    output = serialize_backtest_result(result)

    ph = output["portfolio_history"]
    assert isinstance(ph, list)
    assert len(ph) == 3
    assert "Portfolio Value" in ph[0]
    assert "Close" in ph[0]


@patch("serialization.backtest_serializer.build_kpi_cards", return_value=[])
def test_portfolio_history_index_included(mock_kpi):
    """
    The date index should appear as a column after reset_index.
    """

    result = _make_backtest_result()
    output = serialize_backtest_result(result)

    ph = output["portfolio_history"]
    first_record = ph[0]
    assert any(
        "2020" in str(v) for v in first_record.values()
    )


# ── Analytics History ─────────────────────────────────────────


@patch("serialization.backtest_serializer.build_kpi_cards", return_value=[])
def test_analytics_history_serialized(mock_kpi):
    """
    Analytics history should be a list of dicts with derived columns.
    """

    result = _make_backtest_result()
    output = serialize_backtest_result(result)

    ah = output["analytics_history"]
    assert isinstance(ah, list)
    assert len(ah) == 3
    assert "Daily Return %" in ah[0]
    assert "Drawdown %" in ah[0]
    assert "Buy & Hold Value" in ah[0]


# ── Trade History ─────────────────────────────────────────────


@patch("serialization.backtest_serializer.build_kpi_cards", return_value=[])
def test_trade_history_serialized(mock_kpi):
    """
    Trade history should be a list of dicts without an index column.
    """

    result = _make_backtest_result()
    output = serialize_backtest_result(result)

    th = output["trade_history"]
    assert isinstance(th, list)
    assert len(th) == 1
    assert th[0]["entry_date"] == "2020-01-02"
    assert th[0]["profit_loss"] == 1000.0


@patch("serialization.backtest_serializer.build_kpi_cards", return_value=[])
def test_empty_trade_history(mock_kpi):
    """
    An empty trade history should serialize to an empty list.
    """

    result = _make_backtest_result(
        trade_history=pd.DataFrame(columns=["entry_date", "exit_date", "profit_loss", "holding_period"]),
    )
    output = serialize_backtest_result(result)

    assert output["trade_history"] == []


# ── KPI Cards ─────────────────────────────────────────────────


@patch("serialization.backtest_serializer.build_kpi_cards")
def test_kpi_cards_included(mock_kpi):
    """
    kpi_cards should be the return value of build_kpi_cards.
    """

    mock_kpi.return_value = [{"key": "total_return", "value": 2.0}]

    result = _make_backtest_result()
    output = serialize_backtest_result(result)

    assert output["kpi_cards"] == [{"key": "total_return", "value": 2.0}]
    mock_kpi.assert_called_once_with(result.analytics_result)


# ── Sanitize Value ────────────────────────────────────────────


def test_sanitize_value_normal_float():
    """Normal floats should pass through unchanged."""

    assert _sanitize_value(42.0) == 42.0


def test_sanitize_value_inf():
    """Infinity should be replaced with None."""

    assert _sanitize_value(float("inf")) is None
    assert _sanitize_value(float("-inf")) is None


def test_sanitize_value_nan():
    """NaN should be replaced with None."""

    assert _sanitize_value(float("nan")) is None


def test_sanitize_value_non_float():
    """Non-float values should pass through unchanged."""

    assert _sanitize_value(42) == 42
    assert _sanitize_value("hello") == "hello"
    assert _sanitize_value(None) is None


# ── Inf/NaN in Metrics ────────────────────────────────────────


@patch("serialization.backtest_serializer.build_kpi_cards", return_value=[])
def test_inf_in_metrics_replaced_with_none(mock_kpi):
    """
    Infinity values in metrics should be serialized as None
    for JSON safety.
    """

    result = _make_backtest_result(
        trade_metrics=TradeMetrics(
            profit_factor=float("inf"),
        ),
    )
    output = serialize_backtest_result(result)

    assert output["trade_metrics"]["profit_factor"] is None


@patch("serialization.backtest_serializer.build_kpi_cards", return_value=[])
def test_nan_in_metrics_replaced_with_none(mock_kpi):
    """
    NaN values in metrics should be serialized as None
    for JSON safety.
    """

    result = _make_backtest_result(
        risk_metrics=RiskMetrics(
            sharpe_ratio=float("nan"),
        ),
    )
    output = serialize_backtest_result(result)

    assert output["risk_metrics"]["sharpe_ratio"] is None


# ── NaN in DataFrames ─────────────────────────────────────────


@patch("serialization.backtest_serializer.build_kpi_cards", return_value=[])
def test_nan_in_dataframe_replaced_with_none(mock_kpi):
    """
    NaN values in DataFrame histories should be serialized as None.
    """

    dates = pd.to_datetime(["2020-01-02"])
    analytics = pd.DataFrame(
        {
            "Portfolio Value": [100000.0],
            "Close": [500.0],
            "Daily Return %": [float("nan")],
            "Drawdown %": [0.0],
            "Buy & Hold Value": [100000.0],
        },
        index=dates,
    )

    result = _make_backtest_result(analytics_history=analytics)
    output = serialize_backtest_result(result)

    assert output["analytics_history"][0]["Daily Return %"] is None
