"""
Public service interface for the Market Data module.

This module provides the public API that other parts of the application
should use to interact with the Data module.

Current workflow (Phase 2C):

    Validate Request
          ↓
    Download Raw Data
          ↓
    Clean & Standardize Data
          ↓
    Return Standardized DataFrame
"""

import pandas as pd

from data.cleaner import clean_market_data
from data.downloader import download_stock_data
from data.validator import validate_request
from utils.logger import get_logger

logger = get_logger(__name__)


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

    # Step 2: Download raw market data.
    raw_data = download_stock_data(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
    )

    logger.debug("Market data downloaded successfully.")

    # Step 3: Clean and standardize the data.
    cleaned_data = clean_market_data(raw_data)

    logger.info("Market data request completed successfully.")

    return cleaned_data