"""
Public service interface for the Market Data module.

This module provides the public API that other parts of the application
should use to interact with the Data module.

Current workflow (Phase 2B):

    Validate Request
          ↓
    Download Data
          ↓
    Return Raw DataFrame

Future phases will extend this workflow to clean and standardize the
downloaded data before returning it.
"""

import pandas as pd

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

    This function acts as the public entry point for the Data module.

    Workflow:
        1. Validate request parameters.
        2. Download historical market data.
        3. Return the raw DataFrame.

    Args:
        ticker: NSE stock ticker (e.g. "RELIANCE.NS").
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        Raw historical market data as a pandas DataFrame.

    Raises:
        TypeError:
            If input argument types are invalid.

        ValueError:
            If validation fails or no market data is available.

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

    # Validate user inputs.
    validate_request(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
    )

    logger.debug("Validation completed successfully.")

    # Download historical market data.
    data = download_stock_data(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
    )

    logger.info("Market data request completed successfully.")

    return data