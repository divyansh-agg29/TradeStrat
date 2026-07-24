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

import pandas as pd

from data.market_data_store import initialize_db
from data.retriever import retrieve_market_data
from data.validator import validate_request
from utils.logger import get_logger

logger = get_logger(__name__)

_DB_CONN = None


def get_stock_data(
    ticker: str,
    start_date: str,
    end_date: str,
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
        "ticker=%s, start_date=%s, end_date=%s",
        ticker,
        start_date,
        end_date,
    )

    # Step 1: Validate the request.
    validate_request(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
    )

    logger.debug("Request validation completed successfully.")

    # Step 2: Ensure database connection is available.
    global _DB_CONN
    if _DB_CONN is None:
        _DB_CONN = initialize_db()

    # Step 3: Retrieve data (cache-first, download on miss).
    cleaned_data = retrieve_market_data(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        conn=_DB_CONN,
    )

    logger.info("Market data request completed successfully.")

    return cleaned_data