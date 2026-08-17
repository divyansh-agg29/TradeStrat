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
from strategy.result import IndicatorConfig, StrategyOutput
from utils.logger import get_logger

logger = get_logger(__name__)


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

    logger.info(
        "Generating BB bounce signals "
        "(period=%s, std_multiplier=%s).",
        period,
        std_multiplier,
    )

    # ------------------------------------------------------------------
    # Strategy validation
    # ------------------------------------------------------------------

    if df.empty:
        logger.error("Input DataFrame is empty.")
        raise ValueError("Input DataFrame cannot be empty.")

    if period <= 0:
        logger.error(
            "Invalid BB period: %s",
            period,
        )
        raise ValueError(
            "period must be greater than zero."
        )

    if std_multiplier <= 0:
        logger.error(
            "Invalid std_multiplier: %s",
            std_multiplier,
        )
        raise ValueError(
            "std_multiplier must be greater than zero."
        )

    result_df = df.copy()

    middle_column = f"BB_Middle{period}_{std_multiplier}"
    upper_column = f"BB_Upper{period}_{std_multiplier}"
    lower_column = f"BB_Lower{period}_{std_multiplier}"

    # ------------------------------------------------------------------
    # Ensure indicator exists
    # ------------------------------------------------------------------

    if middle_column not in result_df.columns:
        logger.debug("BB indicators not found. Calculating.")
        result_df = calculate_bollinger_bands(
            result_df,
            period=period,
            std_multiplier=std_multiplier,
            price_column=price_column,
        )

    # ------------------------------------------------------------------
    # Generate signals
    # ------------------------------------------------------------------

    result_df["Signal"] = "HOLD"

    previous_price = result_df[price_column].shift(1)
    current_price = result_df[price_column]

    previous_lower = result_df[lower_column].shift(1)
    previous_upper = result_df[upper_column].shift(1)

    current_lower = result_df[lower_column]
    current_upper = result_df[upper_column]

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

    result_df.loc[buy_mask, "Signal"] = "BUY"
    result_df.loc[sell_mask, "Signal"] = "SELL"

    logger.info(
        "Signal generation complete. "
        "BUY=%d SELL=%d",
        int(buy_mask.sum()),
        int(sell_mask.sum()),
    )

    indicators = [
        IndicatorConfig(
            column=middle_column,
            name=f"BB Middle ({period}, {std_multiplier}σ)",
            display="overlay",
        ),
        IndicatorConfig(
            column=upper_column,
            name=f"BB Upper ({period}, {std_multiplier}σ)",
            display="overlay",
        ),
        IndicatorConfig(
            column=lower_column,
            name=f"BB Lower ({period}, {std_multiplier}σ)",
            display="overlay",
        ),
    ]

    return StrategyOutput(df=result_df, indicators=indicators)
