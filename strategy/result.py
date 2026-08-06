"""
Strategy Result

Defines the structured output returned by all strategy functions.
"""

from dataclasses import dataclass, field
from typing import List, Optional

import pandas as pd


@dataclass
class IndicatorConfig:
    """
    Configuration for a single indicator trace.

    Attributes
    ----------
    column : str
        Column name in the DataFrame.

    name : str
        Display name for the chart legend.

    display : str
        Where to display: "overlay" on price chart or "subplot" below.

    subplot_id : str, optional
        Groups multiple indicators into the same subplot.
        If None, uses the column name as subplot_id.

    y_range : tuple, optional
        Fixed y-axis range for subplot (e.g., (0, 100) for RSI).
    """

    column: str
    name: str
    display: str = "overlay"
    subplot_id: Optional[str] = None
    y_range: Optional[tuple] = None


@dataclass
class StrategyOutput:
    """
    Structured output from a strategy function.

    Attributes
    ----------
    df : pd.DataFrame
        DataFrame with OHLCV data, indicator columns, and Signal column.

    indicators : List[IndicatorConfig]
        Metadata describing each indicator column for chart rendering.
    """

    df: pd.DataFrame
    indicators: List[IndicatorConfig] = field(default_factory=list)
