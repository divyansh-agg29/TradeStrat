"""
Tests for _calculate_warmup_start() in the Backtest Service.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from services.backtest_service import _calculate_warmup_start


# ============================================================================
# Daily Interval (1-year warmup, no lookback limit)
# ============================================================================

class TestDailyInterval:

    def test_daily_warmup_subtracts_one_year(self):
        """
        The 1d interval has a 1-year relativedelta warmup.
        """
        result = _calculate_warmup_start("2025-06-15", "1d")

        assert result == "2024-06-15"

    def test_daily_no_lookback_clamping(self):
        """
        The 1d interval has max_lookback_days=None, so no clamping
        should occur even for very old start dates.
        """
        result = _calculate_warmup_start("2000-01-01", "1d")

        assert result == "1999-01-01"


# ============================================================================
# Weekly Interval (2-year warmup, no lookback limit)
# ============================================================================

class TestWeeklyInterval:

    def test_weekly_warmup_subtracts_two_years(self):
        """
        The 1wk interval has a 2-year relativedelta warmup.
        """
        result = _calculate_warmup_start("2025-06-15", "1wk")

        assert result == "2023-06-15"


# ============================================================================
# Intraday Intervals (zero warmup, lookback clamping)
# ============================================================================

class TestIntradayInterval:

    def test_5min_zero_warmup(self):
        """
        The 5m interval has warmup_period=timedelta(0), so the warmup
        start should equal the requested start when within lookback.
        """
        # 5m has max_lookback_days=60, so use a date within that window
        recent = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        result = _calculate_warmup_start(recent, "5m")

        assert result == recent

    def test_1h_zero_warmup(self):
        """
        The 1h interval has warmup_period=timedelta(0), so the warmup
        start should equal the requested start when within lookback.
        """
        # 1h has max_lookback_days=730, so use a date within that window
        recent = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        result = _calculate_warmup_start(recent, "1h")

        assert result == recent

    def test_1min_lookback_clamping(self):
        """
        The 1m interval has max_lookback_days=30. If the warmup start
        would fall before (today - 30 days), it gets clamped.

        With warmup_period=timedelta(0), the start_date itself is
        already the warmup start — but if the start_date is very old,
        it still gets clamped.
        """
        # Use a very old start date that is definitely beyond 30 days ago
        old_date = "2020-01-01"
        result = _calculate_warmup_start(old_date, "1m")

        today = datetime.now()
        earliest_available = today - timedelta(days=30)

        # The result should be clamped to earliest_available
        result_date = datetime.strptime(result, "%Y-%m-%d")
        assert result_date >= earliest_available.replace(
            hour=0, minute=0, second=0, microsecond=0,
        )

    def test_5min_lookback_clamping(self):
        """
        The 5m interval has max_lookback_days=60. A start date far
        in the past gets clamped.
        """
        old_date = "2020-01-01"
        result = _calculate_warmup_start(old_date, "5m")

        today = datetime.now()
        earliest_available = today - timedelta(days=60)

        result_date = datetime.strptime(result, "%Y-%m-%d")
        assert result_date >= earliest_available.replace(
            hour=0, minute=0, second=0, microsecond=0,
        )

    def test_recent_start_date_not_clamped(self):
        """
        When the start date is recent (within lookback window),
        no clamping should occur.
        """
        # A start date that is definitely within the 1h lookback of 730 days
        recent_date = datetime.now() - timedelta(days=10)
        start_str = recent_date.strftime("%Y-%m-%d")

        result = _calculate_warmup_start(start_str, "1h")

        assert result == start_str


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:

    def test_invalid_interval_raises_error(self):
        """
        An unsupported interval should raise ValueError.
        """
        with pytest.raises(ValueError, match="Unsupported interval"):
            _calculate_warmup_start("2025-06-15", "3d")

    def test_monthly_warmup_subtracts_five_years(self):
        """
        The 1mo interval has a 5-year relativedelta warmup.
        """
        result = _calculate_warmup_start("2025-06-15", "1mo")

        assert result == "2020-06-15"
