"""
Analytics Engine

This module is responsible for evaluating the performance of a completed
portfolio simulation.

Responsibilities
----------------
- Compute portfolio performance metrics.
- Compute risk metrics.
- Compute trade statistics.
- Generate derived analytical time series.
- Return a structured AnalyticsResult.

The Analytics Engine intentionally remains independent of:
- Market data acquisition
- Indicator calculations
- Strategy generation
- Portfolio simulation
- API layer
- Frontend rendering
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from portfolio.simulator import SimulationResult
from utils.logger import get_logger

logger = get_logger(__name__)

TRADING_DAYS_PER_YEAR = 252


# ============================================================================
# Dataclasses
# ============================================================================

@dataclass
class PortfolioMetrics:
    """
    Summary metrics describing overall portfolio performance.
    """

    initial_capital: float = 0.0
    final_portfolio_value: float = 0.0
    profit_loss: float = 0.0
    total_return: float = 0.0
    cagr: float = 0.0


@dataclass
class RiskMetrics:
    """
    Summary metrics describing portfolio risk.
    """

    annualized_volatility: float = 0.0
    maximum_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0


@dataclass
class TradeMetrics:
    """
    Summary statistics describing completed trades.
    """

    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0

    win_rate: float = 0.0

    average_winning_trade: float = 0.0
    average_losing_trade: float = 0.0

    largest_winner: float = 0.0
    largest_loser: float = 0.0

    profit_factor: float = 0.0

    average_holding_period: float = 0.0


@dataclass
class BenchmarkMetrics:
    """
    Summary metrics comparing strategy performance against
    a passive Buy & Hold benchmark.
    """

    benchmark_final_value: float = 0.0
    benchmark_return: float = 0.0
    alpha: float = 0.0


@dataclass
class AnalyticsResult:
    """
    Container for the complete analytics output.
    """

    portfolio_metrics: PortfolioMetrics = field(
        default_factory=PortfolioMetrics
    )

    risk_metrics: RiskMetrics = field(
        default_factory=RiskMetrics
    )

    trade_metrics: TradeMetrics = field(
        default_factory=TradeMetrics
    )

    benchmark_metrics: BenchmarkMetrics = field(
        default_factory=BenchmarkMetrics
    )

    analytics_history: pd.DataFrame = field(
        default_factory=pd.DataFrame
    )


# ============================================================================
# Public API
# ============================================================================

def analyze_performance(
    simulation_result: SimulationResult,
    risk_free_rate: float = 0.0,
) -> AnalyticsResult:
    """
    Analyze the performance of a completed portfolio simulation.

    Parameters
    ----------
    simulation_result : SimulationResult
        Result produced by the Portfolio Simulator.

    risk_free_rate : float, default=0.0
        Annual risk-free rate expressed as a decimal.
        Example:
            0.06 = 6%

    Returns
    -------
    AnalyticsResult
        Structured analytics containing summary metrics and
        derived analytical time series.
    """

    logger.info("Starting performance analysis.")

    _validate_inputs(simulation_result)

    portfolio_metrics = _calculate_portfolio_metrics(
        simulation_result
    )

    initial_capital = simulation_result.summary["initial_capital"]

    analytics_history = _build_analytics_history(
        simulation_result,
        initial_capital,
    )

    risk_metrics = _calculate_risk_metrics(
        analytics_history,
        risk_free_rate,
    )

    trade_metrics = _calculate_trade_metrics(
        simulation_result
    )

    benchmark_metrics = _calculate_benchmark_metrics(
        simulation_result
    )

    logger.info("Performance analysis completed.")

    return AnalyticsResult(
        portfolio_metrics=portfolio_metrics,
        risk_metrics=risk_metrics,
        trade_metrics=trade_metrics,
        benchmark_metrics=benchmark_metrics,
        analytics_history=analytics_history,
    )


# ============================================================================
# Helper Functions
# ============================================================================

def _validate_inputs(
    simulation_result: SimulationResult,
) -> None:
    """
    Validate the input supplied to the Analytics Engine.

    Parameters
    ----------
    simulation_result : SimulationResult
        Result produced by the Portfolio Simulator.

    Raises
    ------
    TypeError
        If the supplied object is not a SimulationResult.

    ValueError
        If required data is missing or invalid.
    """

    if not isinstance(simulation_result, SimulationResult):
        raise TypeError(
            "Input must be a SimulationResult."
        )

    portfolio_history = simulation_result.portfolio_history
    trade_history = simulation_result.trade_history
    summary = simulation_result.summary

    if not isinstance(portfolio_history, pd.DataFrame):
        raise TypeError(
            "portfolio_history must be a pandas DataFrame."
        )

    if not isinstance(trade_history, pd.DataFrame):
        raise TypeError(
            "trade_history must be a pandas DataFrame."
        )
    
    if not isinstance(summary, dict):
        raise TypeError(
            "summary must be a dictionary."
        )

    if portfolio_history.empty:
        raise ValueError(
            "Portfolio history cannot be empty."
        )

    required_columns = {
        "Portfolio Value",
        "Close",
    }

    missing_columns = (
        required_columns - set(portfolio_history.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    required_summary_fields = {
        "initial_capital",
        "final_portfolio_value",
    }

    missing_summary_fields = (
        required_summary_fields -
        set(simulation_result.summary.keys())
    )

    if missing_summary_fields:
        raise ValueError(
            "Simulation summary is missing required fields: "
            f"{sorted(missing_summary_fields)}"
        )

    
    

def _calculate_portfolio_metrics(
    simulation_result: SimulationResult,
) -> PortfolioMetrics:
    """
    Calculate overall portfolio performance metrics.

    Parameters
    ----------
    simulation_result : SimulationResult
        Completed portfolio simulation.

    Returns
    -------
    PortfolioMetrics
        Summary describing overall portfolio performance.
    """

    logger.debug(
        "Calculating portfolio performance metrics."
    )

    summary = simulation_result.summary
    portfolio_history = simulation_result.portfolio_history

    initial_capital = summary["initial_capital"]
    final_portfolio_value = summary["final_portfolio_value"]

    profit_loss = (
        final_portfolio_value - initial_capital
    )

    total_return = (
        (profit_loss / initial_capital) * 100
    )

    start_date = portfolio_history.index[0]
    end_date = portfolio_history.index[-1]

    trading_days = len(portfolio_history)

    if trading_days <= 1:
        cagr = 0.0

    else:
        years = trading_days / TRADING_DAYS_PER_YEAR

        cagr = (
            (
                final_portfolio_value
                / initial_capital
            )
            ** (1 / years)
            - 1
        ) * 100

    return PortfolioMetrics(
        initial_capital=initial_capital,
        final_portfolio_value=final_portfolio_value,
        profit_loss=profit_loss,
        total_return=total_return,
        cagr=cagr,
    )

def _build_analytics_history(
    simulation_result: SimulationResult,
    initial_capital: float,
) -> pd.DataFrame:
    """
    Build the derived analytics time series.

    Parameters
    ----------
    simulation_result : SimulationResult
        Completed portfolio simulation.

    initial_capital : float
        Starting capital used for Buy & Hold benchmark.

    Returns
    -------
    pd.DataFrame
        Portfolio history enriched with analytical time series.

    Notes
    -----
    The returned DataFrame preserves all existing portfolio history
    columns and appends:

    - Daily Return %
    - Running Peak
    - Drawdown
    - Drawdown %
    - Buy & Hold Value
    """

    logger.debug(
        "Building analytics history."
    )

    analytics_history = (
        simulation_result.portfolio_history.copy()
    )

    portfolio_value = analytics_history["Portfolio Value"]

    # --------------------------------------------------------
    # Daily Return (%)
    # --------------------------------------------------------

    analytics_history["Daily Return %"] = (
        portfolio_value.pct_change() * 100
    )

    analytics_history["Daily Return %"] = (
        analytics_history["Daily Return %"].fillna(0.0)
    )

    # --------------------------------------------------------
    # Running Peak
    # --------------------------------------------------------

    analytics_history["Running Peak"] = (
        portfolio_value.cummax()
    )

    # --------------------------------------------------------
    # Drawdown (Absolute)
    # --------------------------------------------------------

    analytics_history["Drawdown"] = (
        analytics_history["Running Peak"]
        - portfolio_value
    )

    # --------------------------------------------------------
    # Drawdown (%)
    # --------------------------------------------------------

    analytics_history["Drawdown %"] = (
        analytics_history["Drawdown"]
        / analytics_history["Running Peak"]
    ) * 100

    analytics_history["Drawdown %"] = (
        analytics_history["Drawdown %"].fillna(0.0)
    )

    # --------------------------------------------------------
    # Buy & Hold Value
    # --------------------------------------------------------

    close_prices = analytics_history["Close"]
    first_close = close_prices.iloc[0]
    shares_bought = initial_capital / first_close

    analytics_history["Buy & Hold Value"] = (
        shares_bought * close_prices
    )

    return analytics_history


def _calculate_benchmark_metrics(
    simulation_result: SimulationResult,
) -> BenchmarkMetrics:
    """
    Calculate Buy & Hold benchmark metrics.

    Computes the hypothetical portfolio value if the entire initial
    capital was used to buy the stock on the first day and held
    until the last day.

    Parameters
    ----------
    simulation_result : SimulationResult
        Completed portfolio simulation.

    Returns
    -------
    BenchmarkMetrics
        Benchmark performance summary.
    """

    logger.debug(
        "Calculating benchmark metrics."
    )

    portfolio_history = simulation_result.portfolio_history
    summary = simulation_result.summary

    initial_capital = summary["initial_capital"]
    final_portfolio_value = summary["final_portfolio_value"]

    first_close = portfolio_history["Close"].iloc[0]
    last_close = portfolio_history["Close"].iloc[-1]

    shares_bought = initial_capital / first_close
    benchmark_final_value = shares_bought * last_close

    benchmark_return = (
        (benchmark_final_value - initial_capital)
        / initial_capital
    ) * 100

    strategy_return = (
        (final_portfolio_value - initial_capital)
        / initial_capital
    ) * 100

    alpha = strategy_return - benchmark_return

    return BenchmarkMetrics(
        benchmark_final_value=benchmark_final_value,
        benchmark_return=benchmark_return,
        alpha=alpha,
    )


def _calculate_risk_metrics(
    analytics_history: pd.DataFrame,
    risk_free_rate: float,
) -> RiskMetrics:
    """
    Calculate portfolio risk metrics.

    Parameters
    ----------
    analytics_history : pd.DataFrame
        Portfolio history enriched with analytical time series.

    risk_free_rate : float
        Annual risk-free rate expressed as a decimal.
        Example:
            0.06 = 6%

    Returns
    -------
    RiskMetrics
        Summary describing portfolio risk.
    """

    logger.debug(
        "Calculating risk metrics."
    )

    daily_returns = analytics_history["Daily Return %"] / 100

    daily_volatility = daily_returns.std()

    annualized_volatility = (
        daily_volatility
        * (TRADING_DAYS_PER_YEAR ** 0.5)
        * 100
    )

    maximum_drawdown = (
        analytics_history["Drawdown %"].max()
    )

    daily_risk_free_rate = (
        risk_free_rate / TRADING_DAYS_PER_YEAR
    )

    excess_returns = (
        daily_returns - daily_risk_free_rate
    )

    if daily_volatility == 0:

        if excess_returns.mean() > 0:
            sharpe_ratio = float("inf")

        elif excess_returns.mean() < 0:
            sharpe_ratio = float("-inf")

        else:
            sharpe_ratio = 0.0

    else:
        sharpe_ratio = (
            excess_returns.mean()
            / daily_volatility
        ) * (TRADING_DAYS_PER_YEAR ** 0.5)

    # --------------------------------------------------------
    # Sortino Ratio
    # --------------------------------------------------------

    downside_returns = daily_returns[
        daily_returns < daily_risk_free_rate
    ]

    if downside_returns.empty:

        if excess_returns.mean() > 0:
            sortino_ratio = float("inf")

        elif excess_returns.mean() < 0:
            sortino_ratio = float("-inf")

        else:
            sortino_ratio = 0.0

    else:
        downside_deviation = (
            (
                (downside_returns - daily_risk_free_rate)
                ** 2
            ).mean()
            ** 0.5
        )

        if downside_deviation == 0:
            sortino_ratio = 0.0
        else:
            sortino_ratio = (
                excess_returns.mean()
                / downside_deviation
            ) * (TRADING_DAYS_PER_YEAR ** 0.5)

    # --------------------------------------------------------
    # Calmar Ratio
    # --------------------------------------------------------

    if maximum_drawdown == 0:
        calmar_ratio = 0.0

    else:
        portfolio_value = (
            analytics_history["Portfolio Value"]
        )

        total_return_ratio = (
            portfolio_value.iloc[-1]
            / portfolio_value.iloc[0]
        )

        trading_days = len(analytics_history)
        years = trading_days / TRADING_DAYS_PER_YEAR

        if years > 0 and total_return_ratio > 0:
            cagr = (
                total_return_ratio ** (1 / years) - 1
            ) * 100
        else:
            cagr = 0.0

        calmar_ratio = cagr / maximum_drawdown

    return RiskMetrics(
        annualized_volatility=annualized_volatility,
        maximum_drawdown=maximum_drawdown,
        sharpe_ratio=sharpe_ratio,
        sortino_ratio=sortino_ratio,
        calmar_ratio=calmar_ratio,
    )


def _calculate_trade_metrics(
    simulation_result: SimulationResult,
) -> TradeMetrics:
    """
    Calculate statistics for completed trades.

    Parameters
    ----------
    simulation_result : SimulationResult
        Completed portfolio simulation.

    Returns
    -------
    TradeMetrics
        Summary statistics describing completed trades.
    """

    logger.debug(
        "Calculating trade metrics."
    )

    trade_history = simulation_result.trade_history

    if trade_history.empty:
        return TradeMetrics()

    total_trades = len(trade_history)

    winning_trades_df = (
        trade_history[trade_history["profit_loss"] > 0]
    )

    losing_trades_df = (
        trade_history[trade_history["profit_loss"] < 0]
    )

    winning_trades = len(winning_trades_df)
    losing_trades = len(losing_trades_df)

    win_rate = (
        (winning_trades / total_trades) * 100
        if total_trades > 0
        else 0.0
    )

    average_winning_trade = (
        winning_trades_df["profit_loss"].mean()
        if winning_trades > 0
        else 0.0
    )

    average_losing_trade = (
        losing_trades_df["profit_loss"].mean()
        if losing_trades > 0
        else 0.0
    )

    largest_winner = (
        winning_trades_df["profit_loss"].max()
        if winning_trades > 0
        else 0.0
    )

    largest_loser = (
        losing_trades_df["profit_loss"].min()
        if losing_trades > 0
        else 0.0
    )

    gross_profit = (
        winning_trades_df["profit_loss"].sum()
    )

    gross_loss = abs(
        losing_trades_df["profit_loss"].sum()
    )

    if gross_loss == 0:
        profit_factor = float("inf")
    else:
        profit_factor = (
            gross_profit / gross_loss
        )

    average_holding_period = (
        trade_history["holding_period"].mean()
    )

    return TradeMetrics(
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        win_rate=win_rate,
        average_winning_trade=average_winning_trade,
        average_losing_trade=average_losing_trade,
        largest_winner=largest_winner,
        largest_loser=largest_loser,
        profit_factor=profit_factor,
        average_holding_period=average_holding_period,
    )

