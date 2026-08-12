"""
Validation utilities for the Market Data module.

This module is responsible for validating user inputs before any attempt is
made to download market data. It performs only syntactic validation and does
not verify whether a ticker actually exists on Yahoo Finance.

Public Functions:
    - validate_ticker()
    - validate_dates()
    - validate_interval()
    - validate_date_range_for_interval()
    - validate_request()
"""

from datetime import datetime, date, timedelta

from interval_config.intervals import get_interval_config, is_valid_interval
from utils.logger import get_logger

logger = get_logger(__name__)

DATE_FORMAT = "%Y-%m-%d"


def validate_ticker(ticker: str) -> None:
    """
    Validate the stock ticker symbol.

    Rules:
    - Must be a string.
    - Cannot be empty.
    - Cannot contain whitespace.
    - Must end with '.NS' (Version 1 supports NSE only).

    Args:
        ticker: Stock ticker symbol.

    Raises:
        TypeError: If ticker is not a string.
        ValueError: If ticker format is invalid.
    """
    logger.debug("Validating ticker: %s", ticker)

    if not isinstance(ticker, str):
        raise TypeError("Ticker must be a string.")

    if not ticker:
        raise ValueError("Ticker symbol is required.")

    if " " in ticker:
        raise ValueError("Ticker symbol cannot contain spaces.")

    if not ticker.endswith(".NS"):
        raise ValueError(
            "Only NSE ticker symbols ending with '.NS' are supported."
        )

    logger.debug("Ticker validation successful.")


def validate_dates(start_date: str, end_date: str) -> None:
    """
    Validate the supplied date range.

    Rules:
    - Dates must be strings.
    - Dates must follow YYYY-MM-DD format.
    - Dates cannot be in the future.
    - Start date must not be after end date.

    Args:
        start_date: Start date as YYYY-MM-DD.
        end_date: End date as YYYY-MM-DD.

    Raises:
        TypeError: If either date is not a string.
        ValueError: If dates are invalid.
    """
    logger.debug(
        "Validating date range: start=%s end=%s",
        start_date,
        end_date,
    )

    if not isinstance(start_date, str):
        raise TypeError("Start date must be a string.")

    if not isinstance(end_date, str):
        raise TypeError("End date must be a string.")

    try:
        start = datetime.strptime(start_date, DATE_FORMAT).date()
    except ValueError as exc:
        raise ValueError(
            f"Invalid start date '{start_date}'. "
            f"Expected format: {DATE_FORMAT}"
        ) from exc

    try:
        end = datetime.strptime(end_date, DATE_FORMAT).date()
    except ValueError as exc:
        raise ValueError(
            f"Invalid end date '{end_date}'. "
            f"Expected format: {DATE_FORMAT}"
        ) from exc

    today = date.today()

    if start > today:
        raise ValueError("Start date cannot be in the future.")

    if end > today:
        raise ValueError("End date cannot be in the future.")

    if start > end:
        raise ValueError(
            "Start date cannot be after end date."
        )

    logger.debug("Date validation successful.")


def validate_interval(interval: str) -> None:
    """
    Validate the interval parameter.

    Rules:
    - Must be a string.
    - Must be a supported interval.

    Args:
        interval: Interval string (e.g., '1m', '5m', '1h', '1d').

    Raises:
        TypeError: If interval is not a string.
        ValueError: If interval is not supported.
    """
    logger.debug("Validating interval: %s", interval)

    if not isinstance(interval, str):
        raise TypeError("Interval must be a string.")

    if not is_valid_interval(interval):
        from interval_config.intervals import get_all_intervals
        valid_intervals = ", ".join(get_all_intervals())
        raise ValueError(
            f"Unsupported interval '{interval}'. "
            f"Valid intervals: {valid_intervals}"
        )

    logger.debug("Interval validation successful.")


def validate_date_range_for_interval(
    start_date: str,
    end_date: str,
    interval: str,
) -> None:
    """
    Validate that the date range is compatible with the interval.

    This checks yfinance data availability limits:
    - Range size must not exceed max_range_days for the interval
    - Start date must not be older than max_lookback_days from today

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        interval: Interval string (e.g., '1m', '5m', '1h', '1d').

    Raises:
        ValueError: If date range exceeds limits for the interval.
    """
    logger.debug(
        "Validating date range for interval: start=%s, end=%s, interval=%s",
        start_date,
        end_date,
        interval,
    )

    config = get_interval_config(interval)

    start = datetime.strptime(start_date, DATE_FORMAT).date()
    end = datetime.strptime(end_date, DATE_FORMAT).date()
    today = date.today()

    # Check 1: Range size
    requested_range_days = (end - start).days
    max_range = config.max_range_days

    if max_range is not None and requested_range_days > max_range:
        raise ValueError(
            f"Date range too large for interval '{interval}'. "
            f"Maximum: {max_range} days, Requested: {requested_range_days} days. "
            f"Please reduce your date range or use a larger interval (e.g., '5m' or '1h')."
        )

    # Check 2: Lookback limit (how far in the past)
    max_lookback = config.max_lookback_days

    if max_lookback is not None:
        lookback_days = (today - start).days

        if lookback_days > max_lookback:
            earliest_allowed = (today - timedelta(days=max_lookback)).strftime(DATE_FORMAT)
            raise ValueError(
                f"Start date too far in the past for interval '{interval}'. "
                f"Data only available from {earliest_allowed} onwards. "
                f"Your start date: {start_date}"
            )

    logger.debug("Date range validation for interval successful.")


def validate_request(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
) -> None:
    """
    Validate the complete market data request.

    This function acts as the public entry point for validation and delegates
    validation to specialized helper functions.

    Args:
        ticker: Stock ticker symbol.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        interval: Data interval (e.g., '1m', '5m', '1h', '1d'). Default: '1d'.

    Raises:
        TypeError: If any argument has an invalid type.
        ValueError: If any validation rule fails.
    """
    logger.info("Validating market data request.")

    validate_ticker(ticker)
    validate_dates(start_date, end_date)
    validate_interval(interval)
    validate_date_range_for_interval(start_date, end_date, interval)

    logger.info("Market data request validation completed successfully.")