"""
Strategy Base Class

Defines the abstract contract and template-method skeleton shared by
all trading strategies.

Subclasses override the abstract hooks without reimplementing the
common workflow: validate → compute indicators → generate signals →
build indicator metadata → return StrategyOutput.
"""

from abc import ABC, abstractmethod

import pandas as pd

from strategy.result import IndicatorConfig, StrategyOutput
from utils.logger import get_logger

logger = get_logger(__name__)


class Strategy(ABC):
    """
    Abstract base class for all trading strategies.

    The public ``run`` method implements the shared workflow.
    Subclasses must implement the four abstract hooks.
    """

    # Human-readable name used in log messages.
    name: str = "Strategy"

    # ------------------------------------------------------------------
    # Template method
    # ------------------------------------------------------------------

    def run(
        self,
        df: pd.DataFrame,
        price_column: str = "Close",
        **params,
    ) -> StrategyOutput:
        """
        Execute the strategy pipeline.

        Parameters
        ----------
        df : pandas.DataFrame
            Market data DataFrame.
        price_column : str
            Column used for indicator calculations.
        **params
            Strategy-specific parameters forwarded to the hooks.

        Returns
        -------
        StrategyOutput
        """

        logger.info("Generating %s signals.", self.name)

        if df.empty:
            logger.error("Input DataFrame is empty.")
            raise ValueError("Input DataFrame cannot be empty.")

        self.validate_params(**params)

        result_df = df.copy()

        result_df, columns = self.compute_indicators(
            result_df, price_column=price_column, **params
        )

        result_df = self.generate_signals(
            result_df, columns, price_column=price_column, **params
        )

        indicators = self.build_indicator_metadata(columns, **params)

        buy_count = int((result_df["Signal"] == "BUY").sum())
        sell_count = int((result_df["Signal"] == "SELL").sum())
        logger.info(
            "Signal generation complete. BUY=%d SELL=%d",
            buy_count,
            sell_count,
        )

        return StrategyOutput(df=result_df, indicators=indicators)

    # ------------------------------------------------------------------
    # Abstract hooks
    # ------------------------------------------------------------------

    @abstractmethod
    def validate_params(self, **params) -> None:
        """
        Validate strategy-specific parameters.

        Raise ``ValueError`` on invalid configuration.
        """

    @abstractmethod
    def compute_indicators(
        self,
        df: pd.DataFrame,
        price_column: str = "Close",
        **params,
    ) -> tuple[pd.DataFrame, dict[str, str]]:
        """
        Ensure required indicator columns exist on *df*.

        Returns
        -------
        tuple[pd.DataFrame, dict[str, str]]
            The (possibly enriched) DataFrame and a dict mapping
            logical role names to column names
            (e.g. ``{"short": "SMA20", "long": "SMA50"}``).
        """

    @abstractmethod
    def generate_signals(
        self,
        df: pd.DataFrame,
        columns: dict[str, str],
        price_column: str = "Close",
        **params,
    ) -> pd.DataFrame:
        """
        Populate the ``Signal`` column on *df*.

        Must set values to ``"BUY"``, ``"SELL"``, or ``"HOLD"``.
        """

    @abstractmethod
    def build_indicator_metadata(
        self,
        columns: dict[str, str],
        **params,
    ) -> list[IndicatorConfig]:
        """
        Return indicator metadata for chart rendering.
        """

    @classmethod
    @abstractmethod
    def ui_metadata(cls) -> dict:
        """
        Return parameter schema for frontend form generation.

        Returns
        -------
        dict
            ``{"label": str, "parameters": [{"key", "label", "type",
            "default", "min"?, "max"?, "step"?, "display_scale"?}, ...]}``
        """
