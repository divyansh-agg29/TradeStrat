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
from interval_config.intervals import get_interval_config
from data.service import get_stock_data
from models import BacktestRequest, BacktestResult
from portfolio import SimulationResult, simulate_portfolio
from models import StrategyConfig
from strategy import STRATEGY_REGISTRY, StrategyOutput
from utils.logger import get_logger

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

logger = get_logger(__name__)


def run_backtest(
    request: BacktestRequest,
    db_path: str,
) -> BacktestResult:
    """
    Execute a complete trading strategy backtest.

    Parameters
    ----------
    request : BacktestRequest
        Configuration describing the requested backtest.
    db_path : str
        Path to the SQLite database file for market data storage.

    Returns
    -------
    BacktestResult
        Complete simulation and analytics output.
    """

    _validate_request(request)

    logger.info("Starting backtest (interval=%s).", request.interval)

    strategy_function = _get_strategy_function(
        request.strategy.type
    )

    market_data = _get_market_data(request, db_path, request.interval)

    strategy_result = _execute_strategy(
        market_data,
        strategy_function,
        request.strategy,
    )

    strategy_df = _trim_to_requested_period(
        strategy_result.df,
        request.start_date,
        request.end_date,
    )

    simulation_result = _run_simulation(
        strategy_df,
        request.initial_capital,
        request.risk,
        request.position_sizing,
    )

    analytics_result = _run_analytics(
        simulation_result,
        request.risk_free_rate,
        request.interval,
    )

    logger.info("Backtest completed.")

    return BacktestResult(
        simulation_result=simulation_result,
        analytics_result=analytics_result,
        indicator_metadata=strategy_result.indicators,
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
    db_path: str,
    interval: str,
):
    """
    Download market data including a warm-up period.

    The warmup period is calculated based on the interval to allow
    recursive indicators (EMA, RSI, MACD, etc.) to stabilize before
    the backtest begins.

    Parameters
    ----------
    request : BacktestRequest
        The backtest request containing ticker and date information.
    db_path : str
        Path to the SQLite database file for market data storage.
    interval : str
        Data interval (e.g., '1m', '5m', '1h', '1d').
    """

    warmup_start_date = _calculate_warmup_start(
        request.start_date,
        interval,
    )

    logger.info(
        "Retrieving market data for %s "
        "(warm-up start=%s, requested start=%s, interval=%s).",
        request.ticker,
        warmup_start_date,
        request.start_date,
        interval,
    )

    return get_stock_data(
        ticker=request.ticker,
        start_date=warmup_start_date,
        end_date=request.end_date,
        db_path=db_path,
        interval=interval,
    )

def _calculate_warmup_start(
    start_date: str,
    interval: str,
) -> str:
    """
    Calculate the extended start date used for indicator warm-up.

    The warmup period is determined by the interval configuration,
    providing enough historical data for indicators to stabilize.
    Also ensures warmup doesn't exceed yfinance data availability limits.

    Parameters
    ----------
    start_date : str
        User-requested start date (YYYY-MM-DD).
    interval : str
        Data interval (e.g., '1m', '5m', '1h', '1d').

    Returns
    -------
    str
        Warmup start date (YYYY-MM-DD).
    """
    config = get_interval_config(interval)
    requested_start = datetime.strptime(start_date, "%Y-%m-%d")
    
    # Calculate warmup start based on interval configuration
    warmup_delta = config.warmup_period
    warmup_start = requested_start - warmup_delta
    
    # Ensure warmup doesn't exceed yfinance data availability
    if config.max_lookback_days is not None:
        today = datetime.now()
        earliest_available = today - timedelta(days=config.max_lookback_days)
        
        if warmup_start < earliest_available:
            logger.warning(
                "Warmup period for %s would exceed data availability. "
                "Adjusting warmup start from %s to %s",
                interval,
                warmup_start.date(),
                earliest_available.date(),
            )
            warmup_start = earliest_available
    
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
    risk_config,
    position_sizing_config=None,
) -> SimulationResult:
    """
    Execute the Portfolio Simulator.
    """

    logger.info("Running portfolio simulation.")

    return simulate_portfolio(
        strategy_output,
        initial_capital=initial_capital,
        risk_config=risk_config,
        position_sizing_config=position_sizing_config,
    )

def _run_analytics(
    simulation_result: SimulationResult,
    risk_free_rate: float,
    interval: str,
) -> AnalyticsResult:
    """
    Execute the Analytics Engine.
    
    Parameters
    ----------
    simulation_result : SimulationResult
        Completed portfolio simulation.
    risk_free_rate : float
        Annual risk-free rate.
    interval : str
        Data interval used in the backtest.
    """

    logger.info("Running performance analytics.")

    return analyze_performance(
        simulation_result,
        risk_free_rate=risk_free_rate,
        interval=interval,
    )