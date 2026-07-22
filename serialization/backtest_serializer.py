"""
Backtest Serializer

Responsible for converting BacktestResult objects into
JSON-serializable dictionaries suitable for API responses.

The serializer intentionally remains independent of:
- Flask
- HTTP
- Business logic
"""

import math

from models import BacktestResult
from utils.logger import get_logger
from analytics import BenchmarkMetrics,PortfolioMetrics,RiskMetrics,TradeMetrics
from interpretation import build_kpi_cards
import pandas as pd

logger = get_logger(__name__)

def serialize_backtest_result(
    result: BacktestResult,
) -> dict:
    """
    Convert a BacktestResult into a JSON-serializable dictionary.

    Parameters
    ----------
    result : BacktestResult
        Completed backtest result.

    Returns
    -------
    dict
        JSON-serializable representation of the backtest.
    """

    logger.info("Serializing backtest result.")

    return {
        "portfolio_metrics": _serialize_portfolio_metrics(
            result.analytics_result.portfolio_metrics
        ),
        "risk_metrics": _serialize_risk_metrics(
            result.analytics_result.risk_metrics
        ),
        "trade_metrics": _serialize_trade_metrics(
            result.analytics_result.trade_metrics
        ),
        "portfolio_history": _serialize_portfolio_history(
            result.simulation_result.portfolio_history
        ),
        "analytics_history": _serialize_analytics_history(
            result.analytics_result.analytics_history
        ),
        "trade_history": _serialize_trade_history(
            result.simulation_result.trade_history
        ),
        "benchmark_metrics": _serialize_benchmark_metrics(
            result.analytics_result.benchmark_metrics
        ),
        "kpi_cards": build_kpi_cards(
            result.analytics_result
        ),
    }


def _sanitize_value(value):
    """Replace non-JSON-safe floats with None."""
    if isinstance(value, float) and (math.isinf(value) or math.isnan(value)):
        return None
    return value


def _serialize_portfolio_metrics(
    metrics: PortfolioMetrics,
) -> dict:
    """
    Serialize portfolio metrics.
    """

    return {k: _sanitize_value(v) for k, v in vars(metrics).items()}

def _serialize_risk_metrics(
    metrics: RiskMetrics,
) -> dict:
    """
    Serialize risk metrics.
    """

    return {k: _sanitize_value(v) for k, v in vars(metrics).items()}

def _serialize_trade_metrics(
    metrics: TradeMetrics,
) -> dict:
    """
    Serialize trade metrics.
    """

    return {k: _sanitize_value(v) for k, v in vars(metrics).items()}

def _serialize_benchmark_metrics(
    metrics: BenchmarkMetrics,
) -> dict:
    """
    Serialize benchmark metrics.
    """

    return {k: _sanitize_value(v) for k, v in vars(metrics).items()}

def _serialize_portfolio_history(
    portfolio_history: pd.DataFrame,
) -> list[dict]:
    """
    Serialize portfolio history.
    """

    portfolio_history = (
        portfolio_history
        .astype(object)
        .where(pd.notnull(portfolio_history), None)
    )

    return (
        portfolio_history
        .reset_index()
        .to_dict(orient="records")
    )

def _serialize_analytics_history(
    analytics_history: pd.DataFrame,
) -> list[dict]:
    """
    Serialize analytics history.
    """

    analytics_history = analytics_history.astype(object).where(
        pd.notnull(analytics_history),
        None
    )

    return (
        analytics_history
        .reset_index()
        .to_dict(orient="records")
    )

def _serialize_trade_history(
    trade_history: pd.DataFrame,
) -> list[dict]:
    """
    Serialize completed trade history.
    """

    trade_history = trade_history.astype(object).where(
        pd.notnull(trade_history),
        None
    )

    return (
        trade_history
        .reset_index(drop=True)
        .to_dict(orient="records")
    )