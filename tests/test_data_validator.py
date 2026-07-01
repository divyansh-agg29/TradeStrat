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


# ----------------------------------------------------------------------
# validate_ticker()
# ----------------------------------------------------------------------

@pytest.mark.parametrize(
    "ticker",
    [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "SBIN.NS",
    ],
)
def test_validate_ticker_valid(ticker):
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
def test_validate_ticker_invalid(ticker):
    """Invalid ticker formats should raise ValueError."""
    with pytest.raises(ValueError):
        validate_ticker(ticker)


def test_validate_ticker_non_string():
    """Ticker must be a string."""
    with pytest.raises(TypeError):
        validate_ticker(123)


# ----------------------------------------------------------------------
# validate_dates()
# ----------------------------------------------------------------------

def test_validate_dates_valid():
    """A valid date range should pass validation."""
    validate_dates(
        "2024-01-01",
        "2024-12-31",
    )


def test_validate_dates_start_after_end():
    """Start date cannot be after end date."""
    with pytest.raises(ValueError):
        validate_dates(
            "2024-12-31",
            "2024-01-01",
        )


def test_validate_dates_invalid_start_format():
    """Invalid start date format should raise ValueError."""
    with pytest.raises(ValueError):
        validate_dates(
            "01-01-2024",
            "2024-12-31",
        )


def test_validate_dates_invalid_end_format():
    """Invalid end date format should raise ValueError."""
    with pytest.raises(ValueError):
        validate_dates(
            "2024-01-01",
            "31-12-2024",
        )


def test_validate_dates_future_start():
    """Future start dates should fail validation."""
    future = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    with pytest.raises(ValueError):
        validate_dates(
            future,
            future,
        )


def test_validate_dates_future_end():
    """Future end dates should fail validation."""
    future = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    with pytest.raises(ValueError):
        validate_dates(
            "2024-01-01",
            future,
        )


def test_validate_dates_non_string():
    """Dates must be strings."""
    with pytest.raises(TypeError):
        validate_dates(
            date.today(),
            "2024-12-31",
        )


# ----------------------------------------------------------------------
# validate_request()
# ----------------------------------------------------------------------

def test_validate_request_valid():
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
def test_validate_request_invalid(ticker, start, end):
    """Invalid requests should raise an exception."""
    with pytest.raises((TypeError, ValueError)):
        validate_request(
            ticker,
            start,
            end,
        )