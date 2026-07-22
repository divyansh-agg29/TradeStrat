"""
KPI Interpreter

Responsible for building a dedicated KPI response from
the AnalyticsResult.

Each KPI entry contains:
- value:          The raw metric value.
- format_type:    How the frontend should format it.
- interpretation: Optional quality level based on predefined thresholds.

The interpreter owns all interpretation logic.
The frontend only maps interpretation levels to colors.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from analytics import AnalyticsResult
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# KPI Definition
# ============================================================================

@dataclass(frozen=True)
class KPIDefinition:
    """
    Defines a single KPI card.
    """

    key: str
    source: str
    field: str
    format_type: str
    thresholds: Optional[list] = None
    invert: bool = False


# ============================================================================
# KPI Definitions Registry
# ============================================================================

KPI_DEFINITIONS = [

    KPIDefinition(
        key="final_portfolio_value",
        source="portfolio",
        field="final_portfolio_value",
        format_type="currency",
    ),

    KPIDefinition(
        key="total_return",
        source="portfolio",
        field="total_return",
        format_type="percentage",
    ),

    KPIDefinition(
        key="cagr",
        source="portfolio",
        field="cagr",
        format_type="percentage",
        thresholds=[
            (5, "poor"),
            (10, "average"),
            (20, "good"),
        ],
    ),

    KPIDefinition(
        key="win_rate",
        source="trade",
        field="win_rate",
        format_type="percentage",
    ),

    KPIDefinition(
        key="profit_factor",
        source="trade",
        field="profit_factor",
        format_type="number",
        thresholds=[
            (1.0, "poor"),
            (1.5, "average"),
            (2.0, "good"),
        ],
    ),

    KPIDefinition(
        key="sharpe_ratio",
        source="risk",
        field="sharpe_ratio",
        format_type="number",
        thresholds=[
            (0.5, "poor"),
            (1.0, "average"),
            (1.5, "good"),
        ],
    ),

    KPIDefinition(
        key="sortino_ratio",
        source="risk",
        field="sortino_ratio",
        format_type="number",
        thresholds=[
            (0.5, "poor"),
            (1.0, "average"),
            (1.5, "good"),
        ],
    ),

    KPIDefinition(
        key="maximum_drawdown",
        source="risk",
        field="maximum_drawdown",
        format_type="percentage",
        thresholds=[
            (5, "excellent"),
            (15, "good"),
            (25, "average"),
        ],
        invert=True,
    ),

    KPIDefinition(
        key="total_trades",
        source="trade",
        field="total_trades",
        format_type="integer",
    ),

    KPIDefinition(
        key="alpha",
        source="benchmark",
        field="alpha",
        format_type="percentage",
        thresholds=[
            (-5, "poor"),
            (0, "average"),
            (10, "good"),
        ],
    ),

]


# ============================================================================
# Source Mapping
# ============================================================================

_SOURCE_MAP = {
    "portfolio": "portfolio_metrics",
    "risk": "risk_metrics",
    "trade": "trade_metrics",
    "benchmark": "benchmark_metrics",
}


# ============================================================================
# Public API
# ============================================================================

def build_kpi_cards(
    analytics_result: AnalyticsResult,
) -> dict:
    """
    Build a KPI cards dictionary from the analytics result.

    Parameters
    ----------
    analytics_result : AnalyticsResult
        Complete analytics output from a backtest.

    Returns
    -------
    dict
        Dictionary keyed by KPI key, each value containing
        value, format_type, and optional interpretation.
    """

    logger.info("Building KPI cards.")

    kpi_cards = {}

    for definition in KPI_DEFINITIONS:

        value = _extract_value(
            analytics_result,
            definition,
        )

        entry = {
            "value": _sanitize_value(value),
            "format_type": definition.format_type,
        }

        if definition.thresholds is not None:

            interpretation = _evaluate_interpretation(
                value,
                definition.thresholds,
                definition.invert,
            )

            if interpretation is not None:
                entry["interpretation"] = interpretation

        kpi_cards[definition.key] = entry

    return kpi_cards


# ============================================================================
# Helper Functions
# ============================================================================

def _extract_value(
    analytics_result: AnalyticsResult,
    definition: KPIDefinition,
) -> object:
    """
    Extract the raw value for a KPI from the analytics result.
    """

    attr_name = _SOURCE_MAP[definition.source]

    metrics_obj = getattr(analytics_result, attr_name)

    return getattr(metrics_obj, definition.field)


def _sanitize_value(value):
    """
    Replace non-JSON-safe floats with None.
    """

    if isinstance(value, float) and (
        math.isinf(value) or math.isnan(value)
    ):
        return None

    return value


def _evaluate_interpretation(
    value,
    thresholds: list,
    invert: bool,
) -> Optional[str]:
    """
    Evaluate a KPI value against its interpretation thresholds.

    Parameters
    ----------
    value : numeric
        The raw KPI value.

    thresholds : list
        Ordered list of (upper_bound, level) tuples.
        The value is compared against each bound in order.
        If it falls below the bound, that level is assigned.
        If it exceeds all bounds, "excellent" is assigned
        (or "poor" if inverted).

    invert : bool
        If True, lower values are better (e.g. Max Drawdown).
        The thresholds are already ordered for inverted logic.

    Returns
    -------
    str or None
        Interpretation level or None if value is invalid.
    """

    if value is None:
        return None

    if isinstance(value, float) and (
        math.isinf(value) or math.isnan(value)
    ):
        return None

    for bound, level in thresholds:
        if value < bound:
            return level

    if invert:
        return "poor"

    return "excellent"
