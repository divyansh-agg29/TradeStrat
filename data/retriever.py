"""
Market data retriever — coordinates cache and download.

This module sits between the public service layer and the lower-level
downloader / market-data-store modules.  It implements two-path logic:

    1. **Cache hit** — the requested date range is fully present in the
       local SQLite store → retrieve, clean, and return.
    2. **Cache miss** — any date is missing → download the *full*
       requested range from Yahoo Finance, store with upsert, clean,
       and return.

No partial downloads are ever performed.
"""

import sqlite3

import pandas as pd

from data.cleaner import clean_market_data
from data.downloader import download_stock_data
from data.market_data_store import (
    is_range_cached,
    retrieve_data,
    store_data,
)
from utils.logger import get_logger

logger = get_logger(__name__)


def retrieve_market_data(
    ticker: str,
    start_date: str,
    end_date: str,
    conn: sqlite3.Connection,
) -> pd.DataFrame:
    """
    Retrieve market data, using the local cache when possible.

    Args:
        ticker:     Stock symbol (e.g. ``"RELIANCE.NS"``).
        start_date: Start date in YYYY-MM-DD format.
        end_date:   End date   in YYYY-MM-DD format.
        conn:       Active SQLite connection to the market-data store.

    Returns:
        A cleaned ``pd.DataFrame`` that satisfies the project data contract.

    Raises:
        ValueError:
            If downloaded or cached data fails cleaning validation.
        ConnectionError:
            If Yahoo Finance cannot be reached.
    """

    # ---- Cache hit path ------------------------------------------------- #
    if is_range_cached(conn, ticker, start_date, end_date):
        logger.info(
            "Cache hit for '%s' (%s → %s). Retrieving from store.",
            ticker,
            start_date,
            end_date,
        )

        cached_df = retrieve_data(conn, ticker, start_date, end_date)

        if cached_df is not None:
            try:
                cleaned_df = clean_market_data(cached_df)
                return cleaned_df
            except ValueError:
                logger.warning(
                    "Cached data for '%s' failed cleaning. "
                    "Falling through to download.",
                    ticker,
                )

    # ---- Cache miss path ------------------------------------------------ #
    logger.info(
        "Cache miss for '%s' (%s → %s). Downloading from Yahoo Finance.",
        ticker,
        start_date,
        end_date,
    )

    raw_df = download_stock_data(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
    )

    # Store the raw data *before* cleaning so that all yfinance fields
    # (including Dividends, Stock Splits, Capital Gains) are preserved.
    store_data(
        conn=conn,
        ticker=ticker,
        df=raw_df,
        start_date=start_date,
        end_date=end_date,
    )

    cleaned_df = clean_market_data(raw_df)

    return cleaned_df
