"""
Market data downloader.

This module is responsible for downloading historical market data from
Yahoo Finance. It acts as a thin wrapper around the yfinance library and
returns the raw DataFrame received from Yahoo Finance.

Responsibilities:
    - Download historical market data
    - Log download progress
    - Handle download-related failures

This module intentionally does NOT:
    - Validate user inputs
    - Clean or transform downloaded data
    - Perform business logic
"""

import pandas as pd
import yfinance as yf

from utils.logger import get_logger

logger = get_logger(__name__)


def download_stock_data(
    ticker: str,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    Download historical market data for a stock.

    Args:
        ticker: NSE ticker symbol (e.g. 'RELIANCE.NS').
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        Raw historical market data as returned by Yahoo Finance.

    Raises:
        ConnectionError:
            If Yahoo Finance cannot be reached or the download fails.

        ValueError:
            If no historical data is available for the requested
            ticker/date range.
    """
    logger.info(
        "Downloading market data: ticker=%s, start=%s, end=%s",
        ticker,
        start_date,
        end_date,
    )

    try:
        stock = yf.Ticker(ticker)

        data = stock.history(
            start=start_date,
            end=end_date,
        )

    except Exception as exc:
        logger.exception(
            "Failed to download market data for '%s'.",
            ticker,
        )
        raise ConnectionError(
            f"Failed to download market data for '{ticker}'."
        ) from exc

    if data.empty:
        logger.warning(
            "No market data returned for '%s'.",
            ticker,
        )
        raise ValueError(
            f"No historical market data found for '{ticker}'."
        )

    logger.info(
        "Download completed successfully. Rows downloaded: %d",
        len(data),
    )

    return data