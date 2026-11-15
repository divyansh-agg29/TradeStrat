"""
Public service interface for the Market Data module.

This module provides the public API that other parts of the application
should use to interact with the Data module.

Current workflow (Version 2A):

    Validate Request
          ↓
    Check Local Cache (Market Data Store)
          ↓
    Cache Hit → Retrieve & Clean
    Cache Miss → Download → Store → Clean
          ↓
    Return Standardized DataFrame
"""


import atexit
import sqlite3

import pandas as pd

from data.market_data_store import initialize_db
from data.retriever import retrieve_market_data
from data.validator import validate_request
from utils.logger import get_logger

logger = get_logger(__name__)

_DB_CONN = None
_DB_PATH = None


def _get_connection(db_path: str) -> sqlite3.Connection:
    """
    Return a valid database connection, re-creating it when the
    requested path differs from the cached one or when the existing
    connection is no longer usable.
    """
    global _DB_CONN, _DB_PATH

    if _DB_CONN is not None and _DB_PATH == db_path:
        try:
            _DB_CONN.execute("SELECT 1")
            return _DB_CONN
        except sqlite3.Error:
            logger.warning("Stale database connection detected. Reconnecting.")
            _DB_CONN = None

    if _DB_CONN is not None:
        _DB_CONN.close()
        logger.info("Closed previous database connection to '%s'.", _DB_PATH)

    _DB_CONN = initialize_db(db_path)
    _DB_PATH = db_path
    return _DB_CONN


def close_db():
    """Close the cached database connection and reset state."""
    global _DB_CONN, _DB_PATH
    if _DB_CONN is not None:
        _DB_CONN.close()
        _DB_CONN = None
        _DB_PATH = None


atexit.register(close_db)


def get_stock_data(
    ticker: str,
    start_date: str,
    end_date: str,
    db_path: str,
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Retrieve historical market data for a stock.

    This function is the public entry point to the Data module.

    Workflow:
        1. Validate request parameters.
        2. Download raw market data.
        3. Clean and standardize the data.
        4. Return the cleaned DataFrame.

    Args:
        ticker: NSE stock ticker (e.g. "RELIANCE.NS").
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        db_path: Path to the SQLite database file.
        interval: Data interval (e.g., '1m', '5m', '1h', '1d'). Default: '1d'.

    Returns:
        A standardized pandas DataFrame that satisfies the project's
        data contract.

    Raises:
        TypeError:
            If input argument types are invalid.

        ValueError:
            If validation fails or downloaded data violates the
            expected data contract.

        ConnectionError:
            If market data cannot be downloaded.
    """
    logger.info(
        "Received market data request: "
        "ticker=%s, start_date=%s, end_date=%s, interval=%s",
        ticker,
        start_date,
        end_date,
        interval,
    )

    # Step 1: Validate the request.
    validate_request(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        interval=interval,
    )

    logger.debug("Request validation completed successfully.")

    # Step 2: Ensure database connection is available.
    conn = _get_connection(db_path)

    # Step 3: Retrieve data (cache-first, download on miss).
    cleaned_data = retrieve_market_data(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        conn=conn,
        interval=interval,
    )

    logger.info("Market data request completed successfully.")

    return cleaned_data