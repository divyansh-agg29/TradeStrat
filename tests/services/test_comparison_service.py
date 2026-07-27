"""
Tests for the Comparison Service.
"""

import pytest
from unittest.mock import patch, MagicMock

from models import (
    BacktestRequest,
    BacktestResult,
    StrategyConfig,
    ComparisonRequest,
    ComparisonResult,
    StrategyResult,
)
from services import run_comparison


def _make_comparison_request(num_strategies=2):
    """
    Create a minimal ComparisonRequest for testing.
    """

    strategies = [
        StrategyConfig(
            type="sma_crossover",
            parameters={"short_period": 20, "long_period": 50},
        )
        for _ in range(num_strategies)
    ]
    return ComparisonRequest(
        ticker="TEST.NS",
        start_date="2020-01-01",
        end_date="2024-12-31",
        strategies=strategies,
    )


def _make_dummy_backtest_result():
    """
    Create a minimal mock BacktestResult.
    """

    result = MagicMock(spec=BacktestResult)
    return result


# ── Validation Tests ──────────────────────────────────────────


def test_fewer_than_two_strategies_raises():
    """
    A ValueError should be raised when fewer than 2 strategies
    are provided.
    """

    request = _make_comparison_request(num_strategies=1)

    with pytest.raises(
        ValueError,
        match="A comparison requires between 2 and 6 strategies.",
    ):
        run_comparison(request)


def test_more_than_six_strategies_raises():
    """
    A ValueError should be raised when more than 6 strategies
    are provided.
    """

    request = _make_comparison_request(num_strategies=7)

    with pytest.raises(
        ValueError,
        match="A comparison requires between 2 and 6 strategies.",
    ):
        run_comparison(request)


def test_empty_strategies_raises():
    """
    A ValueError should be raised when an empty strategies list
    is provided.
    """

    request = _make_comparison_request(num_strategies=0)

    with pytest.raises(
        ValueError,
        match="A comparison requires between 2 and 6 strategies.",
    ):
        run_comparison(request)


# ── Success Tests ─────────────────────────────────────────────


@patch("services.comparison_service.run_backtest")
def test_valid_comparison_two_strategies(mock_run_backtest):
    """
    Two valid strategies should produce two successful results.
    """

    mock_run_backtest.return_value = _make_dummy_backtest_result()

    request = _make_comparison_request(num_strategies=2)
    result = run_comparison(request)

    assert isinstance(result, ComparisonResult)
    assert len(result.strategy_results) == 2
    assert all(sr.success for sr in result.strategy_results)
    assert all(
        sr.backtest_result is not None
        for sr in result.strategy_results
    )
    assert mock_run_backtest.call_count == 2


@patch("services.comparison_service.run_backtest")
def test_valid_comparison_six_strategies(mock_run_backtest):
    """
    Six valid strategies should produce six successful results.
    """

    mock_run_backtest.return_value = _make_dummy_backtest_result()

    request = _make_comparison_request(num_strategies=6)
    result = run_comparison(request)

    assert len(result.strategy_results) == 6
    assert all(sr.success for sr in result.strategy_results)
    assert mock_run_backtest.call_count == 6


# ── Failure Handling Tests ────────────────────────────────────


@patch("services.comparison_service.run_backtest")
def test_failed_strategy_included_with_error(mock_run_backtest):
    """
    One failing strategy should not block others.
    The failed entry should have success=False and an error string.
    """

    dummy_result = _make_dummy_backtest_result()

    mock_run_backtest.side_effect = [
        dummy_result,
        Exception("No trades"),
    ]

    request = _make_comparison_request(num_strategies=2)
    result = run_comparison(request)

    assert len(result.strategy_results) == 2

    assert result.strategy_results[0].success is True
    assert result.strategy_results[0].backtest_result is dummy_result
    assert result.strategy_results[0].error is None

    assert result.strategy_results[1].success is False
    assert result.strategy_results[1].error == "No trades"
    assert result.strategy_results[1].backtest_result is None


@patch("services.comparison_service.run_backtest")
def test_all_strategies_fail(mock_run_backtest):
    """
    When all strategies fail, all results should have success=False.
    """

    mock_run_backtest.side_effect = Exception("Failed")

    request = _make_comparison_request(num_strategies=3)
    result = run_comparison(request)

    assert len(result.strategy_results) == 3
    assert all(not sr.success for sr in result.strategy_results)
    assert all(
        sr.error == "Failed" for sr in result.strategy_results
    )
    assert all(
        sr.backtest_result is None
        for sr in result.strategy_results
    )


# ── Ordering and Identity Tests ──────────────────────────────


@patch("services.comparison_service.run_backtest")
def test_result_order_matches_request(mock_run_backtest):
    """
    The order of strategy_results should match the order of
    strategies in the request.
    """

    mock_run_backtest.return_value = _make_dummy_backtest_result()

    strategies = [
        StrategyConfig(type="sma_crossover", parameters={"short_period": 10, "long_period": 30}),
        StrategyConfig(type="ema_crossover", parameters={"short_period": 12, "long_period": 26}),
        StrategyConfig(type="rsi_mean_reversion", parameters={"rsi_period": 14}),
    ]

    request = ComparisonRequest(
        ticker="TEST.NS",
        start_date="2020-01-01",
        end_date="2024-12-31",
        strategies=strategies,
    )

    result = run_comparison(request)

    for i, sr in enumerate(result.strategy_results):
        assert sr.strategy == request.strategies[i]


@patch("services.comparison_service.run_backtest")
def test_request_echoed_in_result(mock_run_backtest):
    """
    The result should contain a reference to the original request.
    """

    mock_run_backtest.return_value = _make_dummy_backtest_result()

    request = _make_comparison_request(num_strategies=2)
    result = run_comparison(request)

    assert result.request is request


# ── BacktestRequest Construction Test ─────────────────────────


@patch("services.comparison_service.run_backtest")
def test_market_data_shared(mock_run_backtest):
    """
    run_backtest should be called once per strategy with correct
    BacktestRequest objects sharing the common parameters.
    """

    mock_run_backtest.return_value = _make_dummy_backtest_result()

    strategies = [
        StrategyConfig(type="sma_crossover", parameters={"short_period": 20, "long_period": 50}),
        StrategyConfig(type="ema_crossover", parameters={"short_period": 12, "long_period": 26}),
        StrategyConfig(type="rsi_mean_reversion", parameters={"rsi_period": 14}),
    ]

    request = ComparisonRequest(
        ticker="TEST.NS",
        start_date="2020-01-01",
        end_date="2024-12-31",
        initial_capital=200000.0,
        risk_free_rate=0.05,
        strategies=strategies,
    )

    run_comparison(request)

    assert mock_run_backtest.call_count == 3

    for i, call in enumerate(mock_run_backtest.call_args_list):
        backtest_req = call[0][0]
        assert isinstance(backtest_req, BacktestRequest)
        assert backtest_req.ticker == "TEST.NS"
        assert backtest_req.start_date == "2020-01-01"
        assert backtest_req.end_date == "2024-12-31"
        assert backtest_req.initial_capital == 200000.0
        assert backtest_req.risk_free_rate == 0.05
        assert backtest_req.strategy == strategies[i]
