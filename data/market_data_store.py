"""
Market Data Store — SQLite persistence layer for cached market data.

This module manages a local SQLite database that stores historical market
data downloaded from Yahoo Finance.  It provides functions to initialise
the database, store data with upsert behaviour, check whether a requested
date range is fully cached, and retrieve cached data.

Database tables
---------------
market_data        — one row per (ticker, date) with all yfinance fields.
market_data_ranges — metadata rows recording which contiguous date ranges
                     have been downloaded for each ticker.
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)

# ------------------------------------------------------------------ #
# Schema helpers
# ------------------------------------------------------------------ #

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS market_data (
    ticker        TEXT    NOT NULL,
    date          TEXT    NOT NULL,
    open          REAL,
    high          REAL,
    low           REAL,
    close         REAL,
    volume        INTEGER,
    dividends     REAL,
    stock_splits  REAL,
    capital_gains REAL,
    PRIMARY KEY (ticker, date)
);

CREATE INDEX IF NOT EXISTS idx_market_data_ticker
    ON market_data (ticker);

CREATE INDEX IF NOT EXISTS idx_market_data_date
    ON market_data (date);

CREATE TABLE IF NOT EXISTS market_data_ranges (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker     TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ranges_ticker
    ON market_data_ranges (ticker);
"""

# Mapping from yfinance DataFrame column names → SQLite column names
_COLUMN_MAP = {
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Volume": "volume",
    "Dividends": "dividends",
    "Stock Splits": "stock_splits",
    "Capital Gains": "capital_gains",
}

# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #


def _normalize_ticker(ticker: str) -> str:
    """Upper-case the ticker for consistent storage."""
    return ticker.strip().upper()


def _parse_date(date_str: str) -> datetime:
    """Parse a YYYY-MM-DD string to a datetime object."""
    return datetime.strptime(date_str, "%Y-%m-%d")


def _safe_float(value) -> Optional[float]:
    """Convert a value to float, returning None on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value) -> Optional[int]:
    """Convert a value to int, returning None on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------ #
# Public API
# ------------------------------------------------------------------ #


def initialize_db(
    db_path: str = "data/market_data.db",
) -> sqlite3.Connection:
    """
    Open (or create) the SQLite database and ensure the schema exists.

    If the database file is corrupted, it is deleted and recreated so
    that subsequent queries simply behave as cache misses.

    Args:
        db_path: Path to the SQLite file.

    Returns:
        An open ``sqlite3.Connection``.
    """
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.executescript(_SCHEMA_SQL)
        conn.commit()
        logger.info("Market data database initialised at '%s'.", db_path)
        return conn

    except sqlite3.DatabaseError:
        logger.warning(
            "Database at '%s' appears corrupted. Recreating.", db_path,
        )
        conn.close()

        if os.path.exists(db_path):
            os.remove(db_path)

        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.executescript(_SCHEMA_SQL)
        conn.commit()
        return conn


def store_data(
    conn: sqlite3.Connection,
    ticker: str,
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
) -> None:
    """
    Store a DataFrame of market data with upsert behaviour.

    Existing rows for the same ``(ticker, date)`` are replaced.
    After inserting the rows, the requested ``(start_date, end_date)``
    is recorded in ``market_data_ranges`` and overlapping / adjacent
    ranges are merged.

    Args:
        conn:       Active database connection.
        ticker:     Stock symbol.
        df:         DataFrame with a DatetimeIndex and yfinance columns.
        start_date: Requested range start (YYYY-MM-DD).
        end_date:   Requested range end   (YYYY-MM-DD).
    """
    norm_ticker = _normalize_ticker(ticker)

    df_copy = df.copy()

    # Strip timezone info so we get clean YYYY-MM-DD strings.
    if getattr(df_copy.index, "tz", None) is not None:
        df_copy.index = df_copy.index.tz_localize(None)

    cursor = conn.cursor()

    for idx, row in df_copy.iterrows():
        date_str = idx.strftime("%Y-%m-%d")

        cursor.execute(
            """
            INSERT INTO market_data
                (ticker, date, open, high, low, close,
                 volume, dividends, stock_splits, capital_gains)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, date) DO UPDATE SET
                open          = excluded.open,
                high          = excluded.high,
                low           = excluded.low,
                close         = excluded.close,
                volume        = excluded.volume,
                dividends     = excluded.dividends,
                stock_splits  = excluded.stock_splits,
                capital_gains = excluded.capital_gains
            """,
            (
                norm_ticker,
                date_str,
                _safe_float(row.get("Open")),
                _safe_float(row.get("High")),
                _safe_float(row.get("Low")),
                _safe_float(row.get("Close")),
                _safe_int(row.get("Volume")),
                _safe_float(row.get("Dividends")),
                _safe_float(row.get("Stock Splits")),
                _safe_float(row.get("Capital Gains")),
            ),
        )

    # Record the downloaded range and merge with existing ranges.
    cursor.execute(
        """
        INSERT INTO market_data_ranges (ticker, start_date, end_date)
        VALUES (?, ?, ?)
        """,
        (norm_ticker, start_date, end_date),
    )

    conn.commit()

    _merge_ranges(conn, norm_ticker)

    logger.info(
        "Stored %d rows for '%s' (%s → %s).",
        len(df_copy),
        norm_ticker,
        start_date,
        end_date,
    )


def is_range_cached(
    conn: sqlite3.Connection,
    ticker: str,
    start_date: str,
    end_date: str,
) -> bool:
    """
    Return ``True`` if a **single** stored range fully contains the
    requested ``[start_date, end_date]`` interval.

    A request that spans multiple disjoint stored ranges is considered
    a cache miss so that only one API call is made.
    """
    norm_ticker = _normalize_ticker(ticker)

    cursor = conn.execute(
        """
        SELECT 1
        FROM   market_data_ranges
        WHERE  ticker     = ?
          AND  start_date <= ?
          AND  end_date   >= ?
        LIMIT 1
        """,
        (norm_ticker, start_date, end_date),
    )

    return cursor.fetchone() is not None


def retrieve_data(
    conn: sqlite3.Connection,
    ticker: str,
    start_date: str,
    end_date: str,
) -> Optional[pd.DataFrame]:
    """
    Retrieve cached market data for ``ticker`` in ``[start_date, end_date]``.

    Returns ``None`` when the range is not fully cached (the caller
    should treat this as a cache miss and download from yfinance).
    """
    if not is_range_cached(conn, ticker, start_date, end_date):
        return None

    norm_ticker = _normalize_ticker(ticker)

    query = """
        SELECT date, open, high, low, close,
               volume, dividends, stock_splits, capital_gains
        FROM   market_data
        WHERE  ticker = ?
          AND  date  >= ?
          AND  date  <= ?
        ORDER BY date
    """

    rows = conn.execute(query, (norm_ticker, start_date, end_date)).fetchall()

    if not rows:
        return None

    columns = [
        "Date", "Open", "High", "Low", "Close",
        "Volume", "Dividends", "Stock Splits", "Capital Gains",
    ]

    df = pd.DataFrame(rows, columns=columns)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")

    return df


# ------------------------------------------------------------------ #
# Internal helpers
# ------------------------------------------------------------------ #


def _merge_ranges(
    conn: sqlite3.Connection,
    ticker: str,
) -> None:
    """
    Merge overlapping or adjacent date ranges for *ticker* in the
    ``market_data_ranges`` table so that ``is_range_cached`` only
    needs to find a single covering row.
    """
    cursor = conn.execute(
        """
        SELECT start_date, end_date
        FROM   market_data_ranges
        WHERE  ticker = ?
        ORDER BY start_date
        """,
        (ticker,),
    )
    ranges = cursor.fetchall()

    if len(ranges) <= 1:
        return

    merged: list[tuple[datetime, datetime]] = []

    current_start = _parse_date(ranges[0][0])
    current_end = _parse_date(ranges[0][1])

    for start_str, end_str in ranges[1:]:
        start_dt = _parse_date(start_str)
        end_dt = _parse_date(end_str)

        # Merge if overlapping or adjacent (next day).
        if start_dt <= current_end + timedelta(days=1):
            current_end = max(current_end, end_dt)
        else:
            merged.append((current_start, current_end))
            current_start = start_dt
            current_end = end_dt

    merged.append((current_start, current_end))

    # Replace old rows with the merged set.
    conn.execute(
        "DELETE FROM market_data_ranges WHERE ticker = ?",
        (ticker,),
    )

    conn.executemany(
        """
        INSERT INTO market_data_ranges (ticker, start_date, end_date)
        VALUES (?, ?, ?)
        """,
        [
            (ticker, s.strftime("%Y-%m-%d"), e.strftime("%Y-%m-%d"))
            for s, e in merged
        ],
    )

    conn.commit()
