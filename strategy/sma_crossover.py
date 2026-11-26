"""
SMA Crossover Strategy

This module implements the Simple Moving Average (SMA) crossover trading strategy.

The strategy generates BUY, SELL and HOLD signals based on crossover events
between a short-term and long-term SMA.

Responsibilities
----------------
- Validate strategy-specific inputs.
- Ensure required SMA indicators are available.
- Generate crossover signals.
- Return an enriched copy of the input DataFrame.
"""

from indicators.moving_average import calculate_sma
from strategy.crossover import CrossoverStrategy
from strategy.result import IndicatorConfig
from utils.logger import get_logger

logger = get_logger(__name__)


class SmaStrategy(CrossoverStrategy):
    """SMA crossover strategy implementation."""

    name = "SMA crossover"

    def validate_params(self, short_period=20, long_period=50, **_):
        if short_period >= long_period:
            logger.error(
                "Invalid SMA configuration: "
                "short_period=%s long_period=%s",
                short_period,
                long_period,
            )
            raise ValueError(
                "short_period must be smaller than long_period."
            )

    def compute_indicators(self, df, price_column="Close", short_period=20, long_period=50, **_):
        short_column = f"SMA{short_period}"
        long_column = f"SMA{long_period}"

        if short_column not in df.columns:
            logger.debug("%s not found. Calculating.", short_column)
            df = calculate_sma(df, period=short_period, price_column=price_column)

        if long_column not in df.columns:
            logger.debug("%s not found. Calculating.", long_column)
            df = calculate_sma(df, period=long_period, price_column=price_column)

        columns = {"short": short_column, "long": long_column}
        return df, columns

    def build_indicator_metadata(self, columns, short_period=20, long_period=50, **_):
        return [
            IndicatorConfig(
                column=columns["short"],
                name=f"SMA {short_period}",
                display="overlay",
            ),
            IndicatorConfig(
                column=columns["long"],
                name=f"SMA {long_period}",
                display="overlay",
            ),
        ]

    @classmethod
    def ui_metadata(cls):
        return {
            "label": "SMA Crossover",
            "parameters": [
                {"key": "short_period", "label": "Short SMA", "type": "number", "default": 20, "min": 1},
                {"key": "long_period", "label": "Long SMA", "type": "number", "default": 50, "min": 1},
            ],
        }
