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

from datetime import datetime
from dateutil.relativedelta import relativedelta

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

    strategy_output = _trim_to_requested_period(
        strategy_output,
        request.start_date,
        request.end_date,
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
    """
    Download market data including a warm-up period.

    An additional one year of historical data is downloaded prior to
    the requested start date to allow recursive indicators (EMA, RSI,
    MACD, etc.) to stabilize before the backtest begins.
    """

    warmup_start_date = _get_warmup_start_date(
        request.start_date
    )

    logger.info(
        "Downloading market data for %s "
        "(warm-up start=%s, requested start=%s).",
        request.ticker,
        warmup_start_date,
        request.start_date,
    )

    return get_stock_data(
        ticker=request.ticker,
        start_date=warmup_start_date,
        end_date=request.end_date,
    )

def _get_warmup_start_date(
    start_date: str,
) -> str:
    """
    Calculate the extended start date used for indicator warm-up.

    One calendar year of additional historical data is requested
    before the user-specified start date.
    """

    requested_start = datetime.strptime(
        start_date,
        "%Y-%m-%d",
    )

    warmup_start = requested_start - relativedelta(years=1)

    return warmup_start.strftime("%Y-%m-%d")

def _trim_to_requested_period(
    df,
    start_date: str,
    end_date: str,
):
    """
    Trim the strategy output back to the user-requested date range.

    Indicator calculations and signal generation are performed on the
    extended dataset to allow indicators to stabilize during the warm-up
    period. Before portfolio simulation, the warm-up rows are removed so
    that only the requested period is evaluated.
    """

    logger.info(
        "Trimming warm-up period "
        "(start=%s, end=%s).",
        start_date,
        end_date,
    )

    return df.loc[start_date:end_date].copy()

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