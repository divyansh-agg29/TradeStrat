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

import time

import pandas as pd
import yfinance as yf

from utils.logger import get_logger

logger = get_logger(__name__)


def download_stock_data(
    ticker: str,
    start_date: str,
    end_date: str,
    max_retries: int = 3,
    initial_delay: float = 1.0,
) -> pd.DataFrame:
    """
    Download historical market data for a stock with retry logic.

    This function implements exponential backoff to handle transient
    failures, particularly the cold-start issues on platforms like Render
    where the first yfinance request often fails after deployment.

    Args:
        ticker: NSE ticker symbol (e.g. 'RELIANCE.NS').
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        max_retries: Maximum number of retry attempts (default: 3).
        initial_delay: Initial delay in seconds before first retry (default: 1.0).

    Returns:
        Raw historical market data as returned by Yahoo Finance.

    Raises:
        ConnectionError:
            If Yahoo Finance cannot be reached or the download fails
            after all retry attempts.

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

    last_exception = None

    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(ticker)

            data = stock.history(
                start=start_date,
                end=end_date,
            )

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

        except ValueError:
            raise

        except Exception as exc:
            last_exception = exc
            
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                logger.warning(
                    "Download attempt %d/%d failed for '%s'. "
                    "Retrying in %.1f seconds... Error: %s",
                    attempt + 1,
                    max_retries,
                    ticker,
                    delay,
                    str(exc),
                )
                time.sleep(delay)
            else:
                logger.exception(
                    "Failed to download market data for '%s' after %d attempts.",
                    ticker,
                    max_retries,
                )

    raise ConnectionError(
        f"Failed to download market data for '{ticker}' after {max_retries} attempts."
    ) from last_exception