"""
Validation utilities for the Market Data module.

This module is responsible for validating user inputs before any attempt is
made to download market data. It performs only syntactic validation and does
not verify whether a ticker actually exists on Yahoo Finance.

Public Functions:
    - validate_ticker()
    - validate_dates()
    - validate_request()
"""

from datetime import datetime, date

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


def validate_request(
    ticker: str,
    start_date: str,
    end_date: str,
) -> None:
    """
    Validate the complete market data request.

    This function acts as the public entry point for validation and delegates
    validation to specialized helper functions.

    Args:
        ticker: Stock ticker symbol.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Raises:
        TypeError: If any argument has an invalid type.
        ValueError: If any validation rule fails.
    """
    logger.info("Validating market data request.")

    validate_ticker(ticker)
    validate_dates(start_date, end_date)

    logger.info("Market data request validation completed successfully.")