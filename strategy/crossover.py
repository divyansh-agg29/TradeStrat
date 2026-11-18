"""
Crossover Strategy Base

Intermediate base class for strategies that generate signals from
two-line crossover events (short crosses above/below long).

SMA, EMA, and MACD strategies inherit from this class and only
need to specify indicator computation and column names.
"""

import pandas as pd

from strategy.base import Strategy
from strategy.result import IndicatorConfig


class CrossoverStrategy(Strategy):
    """
    Base class for crossover-type strategies.

    Subclasses must implement ``validate_params``,
    ``compute_indicators``, and ``build_indicator_metadata``.

    Signal generation is handled here: BUY when the short line
    crosses above the long line, SELL when it crosses below.
    """

    def generate_signals(
        self,
        df: pd.DataFrame,
        columns: dict[str, str],
        price_column: str = "Close",
        **params,
    ) -> pd.DataFrame:
        """
        Apply crossover mask logic to generate BUY/SELL/HOLD signals.

        Expects *columns* to contain ``"short"`` and ``"long"`` keys
        mapping to the DataFrame column names to compare.
        """

        short_col = columns["short"]
        long_col = columns["long"]

        df["Signal"] = "HOLD"

        previous_short = df[short_col].shift(1)
        previous_long = df[long_col].shift(1)

        current_short = df[short_col]
        current_long = df[long_col]

        buy_mask = (
            (previous_short <= previous_long)
            & (current_short > current_long)
        )

        sell_mask = (
            (previous_short >= previous_long)
            & (current_short < current_long)
        )

        df.loc[buy_mask, "Signal"] = "BUY"
        df.loc[sell_mask, "Signal"] = "SELL"

        return df
