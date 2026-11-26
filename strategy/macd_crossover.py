"""
MACD Crossover Strategy

This module implements the Moving Average Convergence Divergence (MACD) crossover trading strategy.

The strategy generates BUY, SELL and HOLD signals based on crossover events
between a MACD line and MACD Signal line.

Responsibilities
----------------
- Validate strategy-specific inputs.
- Ensure required MACD indicators are available.
- Generate crossover signals.
- Return an enriched copy of the input DataFrame.
"""

from indicators.momentum import calculate_macd
from strategy.crossover import CrossoverStrategy
from strategy.result import IndicatorConfig
from utils.logger import get_logger

logger = get_logger(__name__)


class MacdStrategy(CrossoverStrategy):
    """MACD crossover strategy implementation."""

    name = "MACD crossover"

    def validate_params(self, short_period=12, long_period=26, signal_period=9, **_):
        if short_period >= long_period:
            logger.error(
                "Invalid MACD configuration: "
                "short_period=%s long_period=%s",
                short_period,
                long_period,
            )
            raise ValueError(
                "short_period must be smaller than long_period."
            )

    def compute_indicators(
        self, df, price_column="Close",
        short_period=12, long_period=26, signal_period=9, **_,
    ):
        macd_column = f"MACD_{short_period}_{long_period}_{signal_period}"
        signal_column = f"MACD_Signal_{short_period}_{long_period}_{signal_period}"
        histogram_column = f"MACD_Histogram_{short_period}_{long_period}_{signal_period}"

        if not all(
            col in df.columns
            for col in (macd_column, signal_column, histogram_column)
        ):
            logger.debug("All MACD columns not found. Calculating.")
            df = calculate_macd(
                df,
                fast_period=short_period,
                slow_period=long_period,
                signal_period=signal_period,
                price_column=price_column,
            )

        columns = {
            "short": macd_column,
            "long": signal_column,
            "histogram": histogram_column,
        }
        return df, columns

    def build_indicator_metadata(
        self, columns,
        short_period=12, long_period=26, signal_period=9, **_,
    ):
        return [
            IndicatorConfig(
                column=columns["short"],
                name="MACD",
                display="subplot",
                subplot_id="macd",
            ),
            IndicatorConfig(
                column=columns["long"],
                name="Signal",
                display="subplot",
                subplot_id="macd",
            ),
            IndicatorConfig(
                column=columns["histogram"],
                name="Histogram",
                display="subplot",
                subplot_id="macd",
            ),
        ]

    @classmethod
    def ui_metadata(cls):
        return {
            "label": "MACD Crossover",
            "parameters": [
                {"key": "short_period", "label": "Short EMA", "type": "number", "default": 12, "min": 1},
                {"key": "long_period", "label": "Long EMA", "type": "number", "default": 26, "min": 1},
                {"key": "signal_period", "label": "Signal EMA", "type": "number", "default": 9, "min": 1},
            ],
        }
