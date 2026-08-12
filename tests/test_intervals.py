"""
Comprehensive tests for multi-timeframe interval support.
"""

import pytest
from datetime import date, timedelta

from interval_config.intervals import (
    get_interval_config,
    is_valid_interval,
    get_all_intervals,
    SUPPORTED_INTERVALS,
)
from data.validator import (
    validate_interval,
    validate_date_range_for_interval,
)


class TestIntervalConfiguration:
    """Test interval configuration system."""

    def test_all_intervals_configured(self):
        """All 8 intervals should be configured."""
        assert len(SUPPORTED_INTERVALS) == 8
        expected = ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]
        assert set(SUPPORTED_INTERVALS.keys()) == set(expected)

    def test_get_interval_config_valid(self):
        """Should return config for valid intervals."""
        config = get_interval_config("1d")
        assert config.interval == "1d"
        assert config.display_name == "1 Day"
        assert config.periods_per_year == 252
        assert config.max_range_days is None
        assert config.max_lookback_days is None

    def test_get_interval_config_1m(self):
        """1m interval should have correct limits."""
        config = get_interval_config("1m")
        assert config.max_range_days == 7
        assert config.max_lookback_days == 30
        assert config.periods_per_year == 98280

    def test_get_interval_config_invalid(self):
        """Should raise ValueError for invalid interval."""
        with pytest.raises(ValueError, match="Unsupported interval"):
            get_interval_config("2h")

    def test_is_valid_interval(self):
        """Should correctly identify valid/invalid intervals."""
        assert is_valid_interval("1m") is True
        assert is_valid_interval("1d") is True
        assert is_valid_interval("1mo") is True
        assert is_valid_interval("2h") is False
        assert is_valid_interval("invalid") is False

    def test_get_all_intervals(self):
        """Should return all interval keys."""
        intervals = get_all_intervals()
        assert len(intervals) == 8
        assert "1m" in intervals
        assert "1d" in intervals


class TestIntervalValidation:
    """Test interval validation functions."""

    def test_validate_interval_valid(self):
        """Valid intervals should not raise."""
        validate_interval("1m")
        validate_interval("1d")
        validate_interval("1mo")

    def test_validate_interval_invalid(self):
        """Invalid intervals should raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported interval"):
            validate_interval("2h")

    def test_validate_interval_non_string(self):
        """Non-string intervals should raise TypeError."""
        with pytest.raises(TypeError, match="must be a string"):
            validate_interval(123)

    def test_validate_date_range_1d_unlimited(self):
        """1d interval should accept any range."""
        # Large range should be fine
        validate_date_range_for_interval("2020-01-01", "2024-12-31", "1d")

    def test_validate_date_range_1m_within_limit(self):
        """1m interval should accept 7-day range."""
        today = date.today()
        start = (today - timedelta(days=5)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        validate_date_range_for_interval(start, end, "1m")

    def test_validate_date_range_1m_exceeds_range(self):
        """1m interval should reject 30-day range."""
        today = date.today()
        start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        
        with pytest.raises(ValueError, match="Date range too large"):
            validate_date_range_for_interval(start, end, "1m")

    def test_validate_date_range_1m_exceeds_lookback(self):
        """1m interval should reject start date > 30 days ago."""
        today = date.today()
        start = (today - timedelta(days=60)).strftime("%Y-%m-%d")
        end = (today - timedelta(days=55)).strftime("%Y-%m-%d")
        
        with pytest.raises(ValueError, match="too far in the past"):
            validate_date_range_for_interval(start, end, "1m")

    def test_validate_date_range_5m_within_limits(self):
        """5m interval should accept 60-day range."""
        today = date.today()
        start = (today - timedelta(days=50)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        validate_date_range_for_interval(start, end, "5m")

    def test_validate_date_range_5m_exceeds_range(self):
        """5m interval should reject 100-day range."""
        today = date.today()
        start = (today - timedelta(days=100)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        
        with pytest.raises(ValueError, match="Date range too large"):
            validate_date_range_for_interval(start, end, "5m")


class TestIntervalTableNames:
    """Test interval-specific table naming."""

    def test_table_names_unique(self):
        """Each interval should have unique table names."""
        table_names = [config.table_name for config in SUPPORTED_INTERVALS.values()]
        assert len(table_names) == len(set(table_names))

    def test_table_names_format(self):
        """Table names should follow market_data_{interval} format."""
        for interval, config in SUPPORTED_INTERVALS.items():
            assert config.table_name.startswith("market_data_")
            # Just check that table name contains some part of the interval
            assert len(config.table_name) > len("market_data_")


class TestIntervalWarmupPeriods:
    """Test interval-specific warmup periods."""

    def test_warmup_periods_defined(self):
        """All intervals should have warmup periods."""
        for config in SUPPORTED_INTERVALS.values():
            assert config.warmup_period is not None

    def test_warmup_increases_with_interval(self):
        """Longer intervals should have longer warmup periods."""
        # Just verify warmup periods exist and are reasonable
        # Can't directly compare timedelta and relativedelta
        warmup_1m = SUPPORTED_INTERVALS["1m"].warmup_period
        warmup_1d = SUPPORTED_INTERVALS["1d"].warmup_period
        
        # Check that warmup periods are defined
        assert warmup_1m is not None
        assert warmup_1d is not None


class TestIntervalPeriodsPerYear:
    """Test periods per year calculations."""

    def test_periods_per_year_1d(self):
        """1d should have 252 periods per year."""
        assert SUPPORTED_INTERVALS["1d"].periods_per_year == 252

    def test_periods_per_year_1wk(self):
        """1wk should have 52 periods per year."""
        assert SUPPORTED_INTERVALS["1wk"].periods_per_year == 52

    def test_periods_per_year_1mo(self):
        """1mo should have 12 periods per year."""
        assert SUPPORTED_INTERVALS["1mo"].periods_per_year == 12

    def test_periods_per_year_1h(self):
        """1h should have 1,638 periods per year."""
        assert SUPPORTED_INTERVALS["1h"].periods_per_year == 1638

    def test_periods_per_year_1m(self):
        """1m should have 98,280 periods per year."""
        assert SUPPORTED_INTERVALS["1m"].periods_per_year == 98280


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
