"""
Tests for the Backtest Service.
"""

import pandas as pd
import pytest
from unittest.mock import patch

from analytics import AnalyticsResult
from models import (
    BacktestRequest,
    BacktestResult,
    RiskConfig,
    StrategyConfig,
)
from portfolio import SimulationResult
from services import run_backtest
from strategy import StrategyOutput


def _create_request(
    strategy_type: str = "sma_crossover",
    risk: RiskConfig | None = None,
) -> BacktestRequest:
    """
    Create a valid BacktestRequest for testing.
    """

    return BacktestRequest(
        ticker="RELIANCE.NS",
        start_date="2022-01-01",
        end_date="2023-01-01",
        initial_capital=100000,
        risk_free_rate=0.06,
        strategy=StrategyConfig(
            type=strategy_type,
            parameters={
                "short_period": 20,
                "long_period": 50,
            },
        ),
        risk=risk,
    )

@patch("services.backtest_service.analyze_performance")
@patch("services.backtest_service.simulate_portfolio")
@patch("services.backtest_service.get_stock_data")
def test_run_backtest_success(
    mock_get_stock_data,
    mock_simulate_portfolio,
    mock_analyze_performance,
):
    """
    Backtest Service should orchestrate the complete workflow
    and return a BacktestResult.
    """

    market_data = pd.DataFrame(
        {
            "Close": [100.0, 101.0],
        }
    )

    strategy_output = StrategyOutput(
        df=pd.DataFrame(
            {
                "Close": [100.0, 101.0],
                "Signal": ["HOLD", "BUY"],
            }
        ),
        indicators=[],
    )

    simulation_result = SimulationResult(
        portfolio_history=pd.DataFrame(),
        trade_history=pd.DataFrame(),
        summary={},
    )

    analytics_result = AnalyticsResult()

    mock_get_stock_data.return_value = market_data

    mock_simulate_portfolio.return_value = (
        simulation_result
    )

    mock_analyze_performance.return_value = (
        analytics_result
    )

    with patch(
        "services.backtest_service._get_strategy_function"
    ) as mock_strategy:

        mock_strategy.return_value = (
            lambda df, **kwargs: strategy_output
        )

        result = run_backtest(
            _create_request()
        )

    assert isinstance(
        result,
        BacktestResult,
    )

    assert (
        result.simulation_result
        is simulation_result
    )

    assert (
        result.analytics_result
        is analytics_result
    )

    mock_get_stock_data.assert_called_once()

    mock_simulate_portfolio.assert_called_once()

    mock_analyze_performance.assert_called_once()


@patch("services.backtest_service.analyze_performance")
@patch("services.backtest_service.simulate_portfolio")
@patch("services.backtest_service.get_stock_data")
def test_run_backtest_passes_risk_config_to_simulator(
    mock_get_stock_data,
    mock_simulate_portfolio,
    mock_analyze_performance,
):
    """
    Backtest Service should forward request risk settings to the simulator.
    """

    strategy_df = pd.DataFrame(
        {
            "Close": [100.0, 95.0],
            "Signal": ["BUY", "HOLD"],
        },
        index=pd.date_range(
            start="2022-01-01",
            periods=2,
            freq="D",
        ),
    )
    strategy_output = StrategyOutput(df=strategy_df, indicators=[])

    simulation_result = SimulationResult(
        portfolio_history=pd.DataFrame(),
        trade_history=pd.DataFrame(),
        summary={},
    )
    analytics_result = AnalyticsResult()
    risk_config = RiskConfig(
        stop_loss_type="fixed_percentage",
        stop_loss_parameters={"percent": 0.05},
    )

    mock_get_stock_data.return_value = strategy_df
    mock_simulate_portfolio.return_value = simulation_result
    mock_analyze_performance.return_value = analytics_result

    with patch(
        "services.backtest_service._get_strategy_function"
    ) as mock_strategy:

        mock_strategy.return_value = (
            lambda df, **kwargs: strategy_output
        )

        run_backtest(
            _create_request(risk=risk_config)
        )

    _, kwargs = mock_simulate_portfolio.call_args

    assert kwargs["risk_config"] is risk_config


def test_run_backtest_invalid_request_type():
    """
    A TypeError should be raised when the supplied object
    is not a BacktestRequest.
    """

    with pytest.raises(
        TypeError,
        match="request must be a BacktestRequest.",
    ):
        run_backtest(None)

def test_run_backtest_missing_strategy():
    """
    A ValueError should be raised when no strategy
    configuration is supplied.
    """

    request = BacktestRequest(
        ticker="RELIANCE.NS",
        start_date="2022-01-01",
        end_date="2023-01-01",
        strategy=None,
    )

    with pytest.raises(
        ValueError,
        match="A strategy configuration must be provided.",
    ):
        run_backtest(request)

def test_run_backtest_unsupported_strategy():
    """
    A ValueError should be raised when the requested
    strategy is not registered.
    """

    request = _create_request(
        strategy_type="unknown_strategy"
    )

    with pytest.raises(
        ValueError,
        match="Unsupported strategy",
    ):
        run_backtest(request)

@patch("services.backtest_service.get_stock_data")
def test_run_backtest_propagates_data_errors(
    mock_get_stock_data,
):
    """
    Exceptions raised by the Data module should
    propagate unchanged.
    """

    mock_get_stock_data.side_effect = ValueError(
        "Invalid ticker."
    )

    with pytest.raises(
        ValueError,
        match="Invalid ticker.",
    ):
        run_backtest(
            _create_request()
        )

@patch("services.backtest_service.analyze_performance")
@patch("services.backtest_service.simulate_portfolio")
@patch("services.backtest_service.get_stock_data")
def test_run_backtest_propagates_analytics_errors(
    mock_get_stock_data,
    mock_simulate_portfolio,
    mock_analyze_performance,
):
    """
    Exceptions raised by the Analytics Engine
    should propagate unchanged.
    """

    market_data = pd.DataFrame()

    simulation_result = SimulationResult(
        portfolio_history=pd.DataFrame(),
        trade_history=pd.DataFrame(),
        summary={},
    )

    mock_get_stock_data.return_value = market_data

    mock_simulate_portfolio.return_value = (
        simulation_result
    )

    mock_analyze_performance.side_effect = ValueError(
        "Analytics failed."
    )

    with patch(
        "services.backtest_service._get_strategy_function"
    ) as mock_strategy:

        mock_strategy.return_value = (
            lambda df, **kwargs: StrategyOutput(df=df, indicators=[])
        )

        with pytest.raises(
            ValueError,
            match="Analytics failed.",
        ):
            run_backtest(
                _create_request()
            )
