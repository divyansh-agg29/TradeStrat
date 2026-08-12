"""
Centralized configuration for all supported trading intervals.

This module is the single source of truth for interval-related settings.
Adding a new interval requires updating only this file.
"""

from dataclasses import dataclass
from datetime import timedelta
from typing import Union

from dateutil.relativedelta import relativedelta


@dataclass(frozen=True)
class IntervalConfig:
    """
    Complete configuration for a trading interval.
    
    Attributes:
        interval: yfinance interval string (e.g., "1m", "1d")
        display_name: Human-readable name
        table_name: Database table name
        max_range_days: Maximum date range size (None = unlimited)
        max_lookback_days: How far back data is available (None = unlimited)
        periods_per_year: Trading periods per year (for annualization)
        warmup_period: How much historical data needed for indicator warmup
        use_case: Description of typical use case
    """
    interval: str
    display_name: str
    table_name: str
    max_range_days: int | None
    max_lookback_days: int | None
    periods_per_year: int
    warmup_period: Union[timedelta, relativedelta]
    use_case: str


# ============================================================================
# Constants
# ============================================================================

STOCK_TRADING_HOURS_PER_DAY = 6.5
STOCK_TRADING_DAYS_PER_YEAR = 252


# ============================================================================
# SINGLE SOURCE OF TRUTH - All Supported Intervals
# ============================================================================

SUPPORTED_INTERVALS = {
    "1m": IntervalConfig(
        interval="1m",
        display_name="1 Minute",
        table_name="market_data_1min",
        max_range_days=7,
        max_lookback_days=30,
        periods_per_year=int(STOCK_TRADING_DAYS_PER_YEAR * STOCK_TRADING_HOURS_PER_DAY * 60),
        warmup_period=timedelta(0),
        use_case="Scalping, intraday",
    ),
    
    "5m": IntervalConfig(
        interval="5m",
        display_name="5 Minutes",
        table_name="market_data_5min",
        max_range_days=60,
        max_lookback_days=60,
        periods_per_year=int(STOCK_TRADING_DAYS_PER_YEAR * STOCK_TRADING_HOURS_PER_DAY * 12),
        warmup_period=timedelta(0),
        use_case="Day trading",
    ),
    
    "15m": IntervalConfig(
        interval="15m",
        display_name="15 Minutes",
        table_name="market_data_15min",
        max_range_days=60,
        max_lookback_days=60,
        periods_per_year=int(STOCK_TRADING_DAYS_PER_YEAR * STOCK_TRADING_HOURS_PER_DAY * 4),
        warmup_period=timedelta(0),
        use_case="Swing trading",
    ),
    
    "30m": IntervalConfig(
        interval="30m",
        display_name="30 Minutes",
        table_name="market_data_30min",
        max_range_days=60,
        max_lookback_days=60,
        periods_per_year=int(STOCK_TRADING_DAYS_PER_YEAR * STOCK_TRADING_HOURS_PER_DAY * 2),
        warmup_period=timedelta(0),
        use_case="Swing trading",
    ),
    
    "1h": IntervalConfig(
        interval="1h",
        display_name="1 Hour",
        table_name="market_data_1hour",
        max_range_days=730,
        max_lookback_days=730,
        periods_per_year=int(STOCK_TRADING_DAYS_PER_YEAR * STOCK_TRADING_HOURS_PER_DAY),
        warmup_period=timedelta(0),
        use_case="Position trading",
    ),
    
    "1d": IntervalConfig(
        interval="1d",
        display_name="1 Day",
        table_name="market_data_1day",
        max_range_days=None,
        max_lookback_days=None,
        periods_per_year=STOCK_TRADING_DAYS_PER_YEAR,
        warmup_period=relativedelta(years=1),
        use_case="Long-term strategies",
    ),
    
    "1wk": IntervalConfig(
        interval="1wk",
        display_name="1 Week",
        table_name="market_data_1week",
        max_range_days=None,
        max_lookback_days=None,
        periods_per_year=52,
        warmup_period=relativedelta(years=2),
        use_case="Long-term analysis",
    ),
    
    "1mo": IntervalConfig(
        interval="1mo",
        display_name="1 Month",
        table_name="market_data_1month",
        max_range_days=None,
        max_lookback_days=None,
        periods_per_year=12,
        warmup_period=relativedelta(years=5),
        use_case="Macro analysis",
    ),
}


# ============================================================================
# Utility Functions
# ============================================================================

def get_interval_config(interval: str) -> IntervalConfig:
    """
    Get configuration for an interval.
    
    Args:
        interval: Interval string (e.g., "1m", "1d")
    
    Returns:
        IntervalConfig for the requested interval.
    
    Raises:
        ValueError: If interval is not supported.
    """
    config = SUPPORTED_INTERVALS.get(interval)
    if config is None:
        valid_intervals = ", ".join(SUPPORTED_INTERVALS.keys())
        raise ValueError(
            f"Unsupported interval '{interval}'. "
            f"Valid intervals: {valid_intervals}"
        )
    return config


def is_valid_interval(interval: str) -> bool:
    """
    Check if interval is supported.
    
    Args:
        interval: Interval string to check.
    
    Returns:
        True if interval is supported, False otherwise.
    """
    return interval in SUPPORTED_INTERVALS


def get_all_intervals() -> list[str]:
    """
    Get list of all supported interval strings.
    
    Returns:
        List of interval strings (e.g., ["1m", "5m", "15m", ...])
    """
    return list(SUPPORTED_INTERVALS.keys())


# ============================================================================
# Validation at Module Load Time
# ============================================================================

def _validate_configuration():
    """
    Validate that all intervals have complete configuration.
    Runs automatically when module is imported.
    
    Raises:
        AssertionError: If any configuration is incomplete or invalid.
    """
    for interval, config in SUPPORTED_INTERVALS.items():
        assert config.interval == interval, f"Interval mismatch for {interval}"
        assert config.display_name, f"Missing display_name for {interval}"
        assert config.table_name, f"Missing table_name for {interval}"
        assert config.periods_per_year > 0, f"Invalid periods_per_year for {interval}"
        assert config.warmup_period is not None, f"Missing warmup_period for {interval}"
        assert config.use_case, f"Missing use_case for {interval}"


# Run validation on import
_validate_configuration()
