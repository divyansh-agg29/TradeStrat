"""
Backtest Service

This module orchestrates the complete backtesting workflow.

Responsibilities
----------------
- Coordinate the Data module.
- Resolve and execute the requested trading strategy.
- Run the Portfolio Simulator.
- Run the Analytics Engine.
- Return a structured BacktestResult.

The Backtest Service intentionally contains no business logic.
Each processing stage is delegated to the appropriate module.
"""

from analytics import AnalyticsResult, analyze_performance
from data.service import get_stock_data
from models import BacktestRequest, BacktestResult
from portfolio import SimulationResult, simulate_portfolio
from models import StrategyConfig
from strategy import STRATEGY_REGISTRY
from utils.logger import get_logger

logger = get_logger(__name__)


def run_backtest(
    request: BacktestRequest,
) -> BacktestResult:
    """
    Execute a complete trading strategy backtest.

    Parameters
    ----------
    request : BacktestRequest
        Configuration describing the requested backtest.

    Returns
    -------
    BacktestResult
        Complete simulation and analytics output.
    """

    logger.info("Starting backtest.")

    _validate_request(request)

    strategy_function = _get_strategy_function(
        request.strategy.type
    )

    market_data = _get_market_data(request)

    strategy_output = _execute_strategy(
        market_data,
        strategy_function,
        request.strategy,
    )

    simulation_result = _run_simulation(
        strategy_output,
        request.initial_capital,
    )

    analytics_result = _run_analytics(
        simulation_result,
        request.risk_free_rate,
    )

    logger.info("Backtest completed.")

    return BacktestResult(
        simulation_result=simulation_result,
        analytics_result=analytics_result,
    )


def _validate_request(
    request: BacktestRequest,
) -> None:
    """
    Perform lightweight validation of a BacktestRequest.
    """

    if not isinstance(request, BacktestRequest):
        raise TypeError(
            "request must be a BacktestRequest."
        )

    if request.strategy is None:
        raise ValueError(
            "A strategy configuration must be provided."
        )

    if not request.strategy.type.strip():
        raise ValueError(
            "Strategy type cannot be empty."
        )

def _get_market_data(
    request: BacktestRequest,
):
    logger.info(
        "Downloading market data for %s",
        request.ticker,
    )

    return get_stock_data(
        ticker=request.ticker,
        start_date=request.start_date,
        end_date=request.end_date,
    )

def _get_strategy_function(
    strategy_type: str,
):
    """
    Retrieve the strategy implementation associated with the
    supplied strategy type.
    """

    try:
        return STRATEGY_REGISTRY[strategy_type]

    except KeyError as exc:
        raise ValueError(
            f"Unsupported strategy: '{strategy_type}'."
        ) from exc

def _execute_strategy(
    market_data,
    strategy_function,
    strategy: StrategyConfig,
):
    """
    Execute the selected trading strategy.
    """

    logger.info(
        "Executing strategy: %s",
        strategy.type,
    )

    return strategy_function(
        market_data,
        **strategy.parameters,
    )

def _run_simulation(
    strategy_output,
    initial_capital: float,
) -> SimulationResult:
    """
    Execute the Portfolio Simulator.
    """

    logger.info("Running portfolio simulation.")

    return simulate_portfolio(
        strategy_output,
        initial_capital=initial_capital,
    )

def _run_analytics(
    simulation_result: SimulationResult,
    risk_free_rate: float,
) -> AnalyticsResult:
    """
    Execute the Analytics Engine.
    """

    logger.info("Running performance analytics.")

    return analyze_performance(
        simulation_result,
        risk_free_rate=risk_free_rate,
    )