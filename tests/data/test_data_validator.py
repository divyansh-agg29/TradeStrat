"""
Unit tests for the Market Data validator module.
"""

from datetime import date, timedelta

import pytest

from data.validator import (
    validate_dates,
    validate_request,
    validate_ticker,
)


class TestValidateTicker:

    @pytest.mark.parametrize(
        "ticker",
        [
            "RELIANCE.NS",
            "TCS.NS",
            "INFY.NS",
            "SBIN.NS",
        ],
    )
    def test_valid(self, ticker):
        """Valid NSE ticker symbols should pass validation."""
        validate_ticker(ticker)

    @pytest.mark.parametrize(
        "ticker",
        [
            "",
            "   ",
            "RELIANCE",
            "RELIANCE.BO",
            "RELIANCE NS",
            " RELIANCE.NS ",
        ],
    )
    def test_invalid(self, ticker):
        """Invalid ticker formats should raise ValueError."""
        with pytest.raises(ValueError):
            validate_ticker(ticker)

    def test_non_string(self):
        """Ticker must be a string."""
        with pytest.raises(TypeError, match="Ticker must be a string"):
            validate_ticker(123)


class TestValidateDates:

    def test_valid(self):
        """A valid date range should pass validation."""
        validate_dates(
            "2024-01-01",
            "2024-12-31",
        )

    def test_start_after_end(self):
        """Start date cannot be after end date."""
        with pytest.raises(ValueError, match="Start date cannot be after end date"):
            validate_dates(
                "2024-12-31",
                "2024-01-01",
            )

    def test_invalid_start_format(self):
        """Invalid start date format should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid start date"):
            validate_dates(
                "01-01-2024",
                "2024-12-31",
            )

    def test_invalid_end_format(self):
        """Invalid end date format should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid end date"):
            validate_dates(
                "2024-01-01",
                "31-12-2024",
            )

    def test_future_start(self):
        """Future start dates should fail validation."""
        future = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

        with pytest.raises(ValueError, match="Start date cannot be in the future"):
            validate_dates(
                future,
                future,
            )

    def test_future_end(self):
        """Future end dates should fail validation."""
        future = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

        with pytest.raises(ValueError, match="End date cannot be in the future"):
            validate_dates(
                "2024-01-01",
                future,
            )

    def test_non_string(self):
        """Dates must be strings."""
        with pytest.raises(TypeError, match="date must be a string"):
            validate_dates(
                date.today(),
                "2024-12-31",
            )


class TestValidateRequest:

    def test_valid(self):
        """A completely valid request should pass."""
        validate_request(
            "RELIANCE.NS",
            "2024-01-01",
            "2024-12-31",
        )

    @pytest.mark.parametrize(
        "ticker,start,end",
        [
            ("", "2024-01-01", "2024-12-31"),
            ("RELIANCE", "2024-01-01", "2024-12-31"),
            ("RELIANCE.NS", "2024-12-31", "2024-01-01"),
            ("RELIANCE.NS", "2024/01/01", "2024-12-31"),
        ],
    )
    def test_invalid(self, ticker, start, end):
        """Invalid requests should raise an exception."""
        with pytest.raises((TypeError, ValueError)):
            validate_request(
                ticker,
                start,
                end,
            )
