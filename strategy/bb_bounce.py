"""
Bollinger Bands Bounce Strategy

This module implements a mean reversion trading strategy based on
Bollinger Bands.

The strategy generates BUY, SELL and HOLD signals based on price
crossing the upper and lower Bollinger Bands.

Responsibilities
----------------
- Validate strategy-specific inputs.
- Ensure the required BB indicators are available.
- Generate band-crossing signals.
- Return an enriched copy of the input DataFrame.
"""

import pandas as pd

from indicators.moving_average import calculate_bollinger_bands
from strategy.base import Strategy
from strategy.result import IndicatorConfig, StrategyOutput
from utils.logger import get_logger

logger = get_logger(__name__)


class BbBounceStrategy(Strategy):
    """Bollinger Bands bounce strategy implementation."""

    name = "BB bounce"

    def validate_params(self, period=20, std_multiplier=2.0, **_):
        if period <= 0:
            logger.error("Invalid BB period: %s", period)
            raise ValueError(
                "period must be greater than zero."
            )

        if std_multiplier <= 0:
            logger.error("Invalid std_multiplier: %s", std_multiplier)
            raise ValueError(
                "std_multiplier must be greater than zero."
            )

    def compute_indicators(self, df, price_column="Close", period=20, std_multiplier=2.0, **_):
        middle_column = f"BB_Middle{period}_{std_multiplier}"
        upper_column = f"BB_Upper{period}_{std_multiplier}"
        lower_column = f"BB_Lower{period}_{std_multiplier}"

        if middle_column not in df.columns:
            logger.debug("BB indicators not found. Calculating.")
            df = calculate_bollinger_bands(
                df,
                period=period,
                std_multiplier=std_multiplier,
                price_column=price_column,
            )

        columns = {
            "middle": middle_column,
            "upper": upper_column,
            "lower": lower_column,
        }
        return df, columns

    def generate_signals(self, df, columns, price_column="Close", **_):
        upper_col = columns["upper"]
        lower_col = columns["lower"]

        df["Signal"] = "HOLD"

        previous_price = df[price_column].shift(1)
        current_price = df[price_column]

        previous_lower = df[lower_col].shift(1)
        previous_upper = df[upper_col].shift(1)

        current_lower = df[lower_col]
        current_upper = df[upper_col]

        # BUY when price crosses below lower band
        buy_mask = (
            (previous_price >= previous_lower)
            & (current_price < current_lower)
        )

        # SELL when price crosses above upper band
        sell_mask = (
            (previous_price <= previous_upper)
            & (current_price > current_upper)
        )

        df.loc[buy_mask, "Signal"] = "BUY"
        df.loc[sell_mask, "Signal"] = "SELL"

        return df

    def build_indicator_metadata(self, columns, period=20, std_multiplier=2.0, **_):
        return [
            IndicatorConfig(
                column=columns["middle"],
                name=f"BB Middle ({period}, {std_multiplier}\u03c3)",
                display="overlay",
            ),
            IndicatorConfig(
                column=columns["upper"],
                name=f"BB Upper ({period}, {std_multiplier}\u03c3)",
                display="overlay",
            ),
            IndicatorConfig(
                column=columns["lower"],
                name=f"BB Lower ({period}, {std_multiplier}\u03c3)",
                display="overlay",
            ),
        ]


def generate_bb_bounce_signals(
    df: pd.DataFrame,
    period: int = 20,
    std_multiplier: float = 2.0,
    price_column: str = "Close",
) -> StrategyOutput:
    """
    Generate trading signals using the Bollinger Bands bounce strategy.

    BUY Signal
        Generated when the price crosses BELOW the lower band.

    SELL Signal
        Generated when the price crosses ABOVE the upper band.

    HOLD Signal
        Generated on all other rows.

    Parameters
    ----------
    df : pandas.DataFrame
        Market data DataFrame.

    period : int, default=20
        Period used for the Bollinger Bands calculation.

    std_multiplier : float, default=2.0
        Number of standard deviations for band width.

    price_column : str, default="Close"
        Column used for BB calculation if the indicator
        needs to be generated.

    Returns
    -------
    StrategyOutput
        Contains the enriched DataFrame and indicator metadata.

    Raises
    ------
    ValueError
        If:

        - DataFrame is empty.
        - period is not positive.
        - std_multiplier is not positive.
    """

    return BbBounceStrategy().run(
        df,
        price_column=price_column,
        period=period,
        std_multiplier=std_multiplier,
    )
