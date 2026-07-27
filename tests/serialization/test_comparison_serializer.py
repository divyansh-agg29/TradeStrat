"""
Tests for the Comparison Serializer.
"""

import pytest
from unittest.mock import patch, MagicMock

from models import (
    BacktestResult,
    StrategyConfig,
    ComparisonRequest,
    ComparisonResult,
    StrategyResult,
)
from serialization.comparison_serializer import serialize_comparison_result


def _make_serialized_backtest():
    """
    Return a canned dict mimicking serialize_backtest_result output.
    """

    return {
        "portfolio_metrics": {
            "initial_capital": 100000.0,
            "final_portfolio_value": 120000.0,
            "profit_loss": 20000.0,
            "total_return": 20.0,
            "cagr": 9.5,
        },
        "risk_metrics": {
            "annualized_volatility": 15.0,
            "maximum_drawdown": 10.0,
            "sharpe_ratio": 1.2,
            "sortino_ratio": 1.5,
            "calmar_ratio": 0.95,
        },
        "trade_metrics": {
            "total_trades": 10,
            "winning_trades": 6,
            "losing_trades": 4,
            "win_rate": 60.0,
            "profit_factor": 1.8,
        },
        "portfolio_history": [
            {"Date": "2020-01-02", "Portfolio Value": 100000.0, "Close": 500.0},
            {"Date": "2020-01-03", "Portfolio Value": 101000.0, "Close": 505.0},
        ],
        "analytics_history": [
            {"Date": "2020-01-02", "Portfolio Value": 100000.0, "Buy & Hold Value": 100000.0, "Drawdown %": 0.0},
            {"Date": "2020-01-03", "Portfolio Value": 101000.0, "Buy & Hold Value": 101000.0, "Drawdown %": 0.0},
        ],
        "trade_history": [
            {"entry_date": "2020-01-02", "exit_date": "2020-01-03", "profit_loss": 1000.0},
        ],
        "benchmark_metrics": {
            "benchmark_final_value": 115000.0,
            "benchmark_return": 15.0,
            "alpha": 5.0,
        },
        "kpi_cards": [
            {"title": "Total Return", "value": "20.0%"},
        ],
    }


def _make_dummy_backtest_result():
    """
    Create a mock BacktestResult.
    """

    return MagicMock(spec=BacktestResult)


def _make_comparison_result(success_flags):
    """
    Build a ComparisonResult with the given success pattern.

    Parameters
    ----------
    success_flags : list[bool]
        True = successful strategy, False = failed strategy.
    """

    strategy_types = [
        "sma_crossover", "ema_crossover", "macd_crossover",
        "rsi_mean_reversion", "sma_crossover", "ema_crossover",
    ]

    strategies = []
    strategy_results = []

    for i, success in enumerate(success_flags):
        config = StrategyConfig(
            type=strategy_types[i % len(strategy_types)],
            parameters={"short_period": 10 + i, "long_period": 50 + i},
        )
        strategies.append(config)

        if success:
            strategy_results.append(
                StrategyResult(
                    strategy=config,
                    success=True,
                    backtest_result=_make_dummy_backtest_result(),
                )
            )
        else:
            strategy_results.append(
                StrategyResult(
                    strategy=config,
                    success=False,
                    error=f"Strategy {i} failed",
                )
            )

    request = ComparisonRequest(
        ticker="TEST.NS",
        start_date="2020-01-01",
        end_date="2024-12-31",
        initial_capital=100000.0,
        risk_free_rate=0.05,
        strategies=strategies,
    )

    return ComparisonResult(
        request=request,
        strategy_results=strategy_results,
    )


# ── Common Params ─────────────────────────────────────────────


@patch(
    "serialization.comparison_serializer.serialize_backtest_result",
    side_effect=lambda _: _make_serialized_backtest(),
)
def test_common_params_echoed(mock_serialize):
    """
    The common dict should echo the request's shared parameters.
    """

    result = _make_comparison_result([True, True])
    output = serialize_comparison_result(result)

    common = output["common"]
    assert common["ticker"] == "TEST.NS"
    assert common["start_date"] == "2020-01-01"
    assert common["end_date"] == "2024-12-31"
    assert common["initial_capital"] == 100000.0
    assert common["risk_free_rate"] == 0.05


# ── Successful Strategy ──────────────────────────────────────


@patch(
    "serialization.comparison_serializer.serialize_backtest_result",
    side_effect=lambda _: _make_serialized_backtest(),
)
def test_successful_strategy_serialized(mock_serialize):
    """
    A successful strategy entry should contain non-null metrics
    and histories.
    """

    result = _make_comparison_result([True])
    output = serialize_comparison_result(result)

    entry = output["results"][0]
    assert entry["success"] is True
    assert entry["error"] is None
    assert entry["portfolio_metrics"] is not None
    assert entry["risk_metrics"] is not None
    assert entry["trade_metrics"] is not None
    assert entry["portfolio_history"] is not None
    assert entry["analytics_history"] is not None
    assert entry["trade_history"] is not None


# ── Stripped Fields ───────────────────────────────────────────


@patch(
    "serialization.comparison_serializer.serialize_backtest_result",
    side_effect=lambda _: _make_serialized_backtest(),
)
def test_kpi_cards_stripped(mock_serialize):
    """
    kpi_cards should be removed from successful strategy entries.
    """

    result = _make_comparison_result([True])
    output = serialize_comparison_result(result)

    assert "kpi_cards" not in output["results"][0]


@patch(
    "serialization.comparison_serializer.serialize_backtest_result",
    side_effect=lambda _: _make_serialized_backtest(),
)
def test_benchmark_metrics_stripped_from_results(mock_serialize):
    """
    benchmark_metrics should be removed from individual strategy
    entries (it is placed at the top level instead).
    """

    result = _make_comparison_result([True])
    output = serialize_comparison_result(result)

    assert "benchmark_metrics" not in output["results"][0]


# ── Benchmark Extraction ─────────────────────────────────────


@patch(
    "serialization.comparison_serializer.serialize_backtest_result",
    side_effect=lambda _: _make_serialized_backtest(),
)
def test_benchmark_extracted_to_top_level(mock_serialize):
    """
    The top-level benchmark object should contain portfolio_history
    and benchmark_metrics extracted from the first successful strategy.
    """

    result = _make_comparison_result([True, True])
    output = serialize_comparison_result(result)

    benchmark = output["benchmark"]
    assert benchmark is not None
    assert "portfolio_history" in benchmark
    assert "benchmark_metrics" in benchmark
    assert benchmark["benchmark_metrics"]["benchmark_final_value"] == 115000.0
    assert len(benchmark["portfolio_history"]) == 2
    assert benchmark["portfolio_history"][0]["Buy & Hold Value"] == 100000.0


@patch(
    "serialization.comparison_serializer.serialize_backtest_result",
)
def test_benchmark_null_when_all_fail(mock_serialize):
    """
    benchmark should be None when all strategies fail.
    """

    result = _make_comparison_result([False, False])
    output = serialize_comparison_result(result)

    assert output["benchmark"] is None
    mock_serialize.assert_not_called()


# ── Failed Strategy ───────────────────────────────────────────


@patch(
    "serialization.comparison_serializer.serialize_backtest_result",
    side_effect=lambda _: _make_serialized_backtest(),
)
def test_failed_strategy_serialized(mock_serialize):
    """
    A failed strategy entry should have success=False, an error
    string, and all metric/history fields set to None.
    """

    result = _make_comparison_result([True, False])
    output = serialize_comparison_result(result)

    failed = output["results"][1]
    assert failed["success"] is False
    assert isinstance(failed["error"], str)
    assert failed["portfolio_metrics"] is None
    assert failed["risk_metrics"] is None
    assert failed["trade_metrics"] is None
    assert failed["portfolio_history"] is None
    assert failed["analytics_history"] is None
    assert failed["trade_history"] is None


# ── Strategy Echo ─────────────────────────────────────────────


@patch(
    "serialization.comparison_serializer.serialize_backtest_result",
    side_effect=lambda _: _make_serialized_backtest(),
)
def test_strategy_config_echoed(mock_serialize):
    """
    Each result entry should echo back the strategy type and
    parameters.
    """

    result = _make_comparison_result([True, False])
    output = serialize_comparison_result(result)

    first_strategy = output["results"][0]["strategy"]
    assert first_strategy["type"] == "sma_crossover"
    assert "short_period" in first_strategy["parameters"]

    second_strategy = output["results"][1]["strategy"]
    assert second_strategy["type"] == "ema_crossover"
    assert "short_period" in second_strategy["parameters"]


# ── Result Ordering ───────────────────────────────────────────


@patch(
    "serialization.comparison_serializer.serialize_backtest_result",
    side_effect=lambda _: _make_serialized_backtest(),
)
def test_results_order_matches_request(mock_serialize):
    """
    The results array order should match the strategies array
    order in the request.
    """

    result = _make_comparison_result([True, True, True])
    output = serialize_comparison_result(result)

    assert len(output["results"]) == 3
    assert output["results"][0]["strategy"]["type"] == "sma_crossover"
    assert output["results"][1]["strategy"]["type"] == "ema_crossover"
    assert output["results"][2]["strategy"]["type"] == "macd_crossover"
