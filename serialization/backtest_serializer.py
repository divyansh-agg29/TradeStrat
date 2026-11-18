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
from interpretation import build_kpi_cards
from serialization.chart_serializer import build_charts
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
        "portfolio_metrics": _serialize_dataclass(
            result.analytics_result.portfolio_metrics
        ),
        "risk_metrics": _serialize_dataclass(
            result.analytics_result.risk_metrics
        ),
        "trade_metrics": _serialize_dataclass(
            result.analytics_result.trade_metrics
        ),
        "portfolio_history": _serialize_dataframe(
            result.simulation_result.portfolio_history
        ),
        "analytics_history": _serialize_dataframe(
            result.analytics_result.analytics_history
        ),
        "trade_history": _serialize_dataframe(
            result.simulation_result.trade_history, drop_index=True
        ),
        "benchmark_metrics": _serialize_dataclass(
            result.analytics_result.benchmark_metrics
        ),
        "kpi_cards": build_kpi_cards(
            result.analytics_result
        ),
        "charts": build_charts(
            result.simulation_result.portfolio_history,
            result.simulation_result.trade_history,
            result.analytics_result.analytics_history,
            result.indicator_metadata,
        ),
    }


def _sanitize_value(value):
    """Replace non-JSON-safe floats with None."""
    if isinstance(value, float) and (math.isinf(value) or math.isnan(value)):
        return None
    return value


def _serialize_dataclass(obj) -> dict:
    """Serialize a dataclass instance by sanitizing each field value."""
    return {k: _sanitize_value(v) for k, v in vars(obj).items()}


def _serialize_dataframe(df: pd.DataFrame, drop_index: bool = False) -> list[dict]:
    """Serialize a DataFrame to a list of dicts, replacing NaN/None."""
    df = df.astype(object).where(pd.notnull(df), None)
    return df.reset_index(drop=drop_index).to_dict(orient="records")