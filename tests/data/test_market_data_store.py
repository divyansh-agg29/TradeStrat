"""
Unit tests for the Market Data Store module.
"""

import os
import sqlite3
import tempfile

import pandas as pd
import pytest

from data.market_data_store import (
    initialize_db,
    is_range_cached,
    retrieve_data,
    store_data,
)


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #


def _make_sample_df(dates, ticker_suffix=""):
    """
    Build a minimal yfinance-style DataFrame for the given dates.
    """
    n = len(dates)
    return pd.DataFrame(
        {
            "Open": [100.0 + i for i in range(n)],
            "High": [105.0 + i for i in range(n)],
            "Low": [99.0 + i for i in range(n)],
            "Close": [104.0 + i for i in range(n)],
            "Volume": [1000 + i for i in range(n)],
            "Dividends": [0.0] * n,
            "Stock Splits": [0.0] * n,
            "Capital Gains": [0.0] * n,
        },
        index=pd.DatetimeIndex(dates, name="Date"),
    )


@pytest.fixture()
def db_conn():
    """Yield a fresh in-memory-ish SQLite connection via a temp file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = initialize_db(path)
    yield conn
    conn.close()
    if os.path.exists(path):
        os.remove(path)


# ------------------------------------------------------------------ #
# initialize_db
# ------------------------------------------------------------------ #


class TestInitializeDb:

    def test_creates_tables(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        conn = initialize_db(path)

        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {t[0] for t in tables}

        assert "market_data" in table_names
        assert "market_data_ranges" in table_names

        conn.close()
        os.remove(path)

    def test_handles_corrupted_db(self, tmp_path):
        db_path = str(tmp_path / "corrupt.db")

        with open(db_path, "wb") as f:
            f.write(b"this is not a valid sqlite file")

        conn = initialize_db(db_path)

        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = {t[0] for t in tables}
        assert "market_data" in table_names

        conn.close()


# ------------------------------------------------------------------ #
# store_data + retrieve_data
# ------------------------------------------------------------------ #


class TestStoreAndRetrieve:

    def test_store_and_retrieve_round_trip(self, db_conn):
        dates = ["2024-01-02", "2024-01-03", "2024-01-04"]
        df = _make_sample_df(dates)

        store_data(db_conn, "RELIANCE.NS", df, "2024-01-02", "2024-01-04")

        result = retrieve_data(
            db_conn, "RELIANCE.NS", "2024-01-02", "2024-01-04",
        )

        assert result is not None
        assert len(result) == 3
        assert list(result.columns) == [
            "Open", "High", "Low", "Close",
            "Volume", "Dividends", "Stock Splits", "Capital Gains",
        ]

    def test_retrieve_returns_none_when_not_cached(self, db_conn):
        result = retrieve_data(
            db_conn, "RELIANCE.NS", "2024-01-02", "2024-01-04",
        )
        assert result is None

    def test_upsert_replaces_existing_data(self, db_conn):
        dates = ["2024-01-02", "2024-01-03"]
        df1 = _make_sample_df(dates)

        store_data(db_conn, "RELIANCE.NS", df1, "2024-01-02", "2024-01-03")

        # Create updated data with different prices.
        df2 = pd.DataFrame(
            {
                "Open": [200.0, 201.0],
                "High": [210.0, 211.0],
                "Low": [190.0, 191.0],
                "Close": [205.0, 206.0],
                "Volume": [2000, 2001],
                "Dividends": [0.0, 0.0],
                "Stock Splits": [0.0, 0.0],
                "Capital Gains": [0.0, 0.0],
            },
            index=pd.DatetimeIndex(dates, name="Date"),
        )

        store_data(db_conn, "RELIANCE.NS", df2, "2024-01-02", "2024-01-03")

        result = retrieve_data(
            db_conn, "RELIANCE.NS", "2024-01-02", "2024-01-03",
        )

        assert result is not None
        assert result.iloc[0]["Open"] == 200.0
        assert result.iloc[1]["Open"] == 201.0

    def test_stores_all_yfinance_fields(self, db_conn):
        dates = ["2024-01-02"]
        df = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [105.0],
                "Low": [99.0],
                "Close": [104.0],
                "Volume": [1000],
                "Dividends": [1.5],
                "Stock Splits": [2.0],
                "Capital Gains": [0.75],
            },
            index=pd.DatetimeIndex(dates, name="Date"),
        )

        store_data(db_conn, "RELIANCE.NS", df, "2024-01-02", "2024-01-02")

        result = retrieve_data(
            db_conn, "RELIANCE.NS", "2024-01-02", "2024-01-02",
        )

        assert result is not None
        assert result.iloc[0]["Dividends"] == 1.5
        assert result.iloc[0]["Stock Splits"] == 2.0
        assert result.iloc[0]["Capital Gains"] == 0.75


# ------------------------------------------------------------------ #
# is_range_cached
# ------------------------------------------------------------------ #


class TestIsRangeCached:

    def test_returns_true_for_exact_match(self, db_conn):
        dates = ["2024-01-02", "2024-01-03", "2024-01-04"]
        df = _make_sample_df(dates)
        store_data(db_conn, "RELIANCE.NS", df, "2024-01-02", "2024-01-04")

        assert is_range_cached(
            db_conn, "RELIANCE.NS", "2024-01-02", "2024-01-04",
        )

    def test_returns_true_for_subset_of_cached_range(self, db_conn):
        dates = ["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
        df = _make_sample_df(dates)
        store_data(db_conn, "RELIANCE.NS", df, "2024-01-02", "2024-01-05")

        assert is_range_cached(
            db_conn, "RELIANCE.NS", "2024-01-03", "2024-01-04",
        )

    def test_returns_false_when_no_data(self, db_conn):
        assert not is_range_cached(
            db_conn, "RELIANCE.NS", "2024-01-02", "2024-01-04",
        )

    def test_returns_false_when_range_extends_beyond_cached(self, db_conn):
        dates = ["2024-01-02", "2024-01-03"]
        df = _make_sample_df(dates)
        store_data(db_conn, "RELIANCE.NS", df, "2024-01-02", "2024-01-03")

        assert not is_range_cached(
            db_conn, "RELIANCE.NS", "2024-01-01", "2024-01-04",
        )

    def test_returns_false_for_disjoint_ranges(self, db_conn):
        """
        Two disjoint cached blocks: [Jan 2-3] and [Jan 8-9].
        A request spanning [Jan 2-9] must be a cache miss since no
        single range covers it.
        """
        df1 = _make_sample_df(["2024-01-02", "2024-01-03"])
        store_data(db_conn, "RELIANCE.NS", df1, "2024-01-02", "2024-01-03")

        df2 = _make_sample_df(["2024-01-08", "2024-01-09"])
        store_data(db_conn, "RELIANCE.NS", df2, "2024-01-08", "2024-01-09")

        assert not is_range_cached(
            db_conn, "RELIANCE.NS", "2024-01-02", "2024-01-09",
        )

    def test_ticker_case_insensitive(self, db_conn):
        dates = ["2024-01-02"]
        df = _make_sample_df(dates)
        store_data(db_conn, "reliance.ns", df, "2024-01-02", "2024-01-02")

        assert is_range_cached(
            db_conn, "RELIANCE.NS", "2024-01-02", "2024-01-02",
        )


# ------------------------------------------------------------------ #
# Range merging
# ------------------------------------------------------------------ #


class TestRangeMerging:

    def test_adjacent_ranges_are_merged(self, db_conn):
        df1 = _make_sample_df(["2024-01-02", "2024-01-03"])
        store_data(db_conn, "RELIANCE.NS", df1, "2024-01-02", "2024-01-03")

        df2 = _make_sample_df(["2024-01-04", "2024-01-05"])
        store_data(db_conn, "RELIANCE.NS", df2, "2024-01-04", "2024-01-05")

        rows = db_conn.execute(
            "SELECT start_date, end_date FROM market_data_ranges "
            "WHERE ticker = 'RELIANCE.NS'"
        ).fetchall()

        assert len(rows) == 1
        assert rows[0] == ("2024-01-02", "2024-01-05")

    def test_overlapping_ranges_are_merged(self, db_conn):
        df1 = _make_sample_df(["2024-01-02", "2024-01-03", "2024-01-04"])
        store_data(db_conn, "RELIANCE.NS", df1, "2024-01-02", "2024-01-04")

        df2 = _make_sample_df(["2024-01-03", "2024-01-04", "2024-01-05"])
        store_data(db_conn, "RELIANCE.NS", df2, "2024-01-03", "2024-01-05")

        rows = db_conn.execute(
            "SELECT start_date, end_date FROM market_data_ranges "
            "WHERE ticker = 'RELIANCE.NS'"
        ).fetchall()

        assert len(rows) == 1
        assert rows[0] == ("2024-01-02", "2024-01-05")

    def test_disjoint_ranges_stay_separate(self, db_conn):
        df1 = _make_sample_df(["2024-01-02", "2024-01-03"])
        store_data(db_conn, "RELIANCE.NS", df1, "2024-01-02", "2024-01-03")

        df2 = _make_sample_df(["2024-01-08", "2024-01-09"])
        store_data(db_conn, "RELIANCE.NS", df2, "2024-01-08", "2024-01-09")

        rows = db_conn.execute(
            "SELECT start_date, end_date FROM market_data_ranges "
            "WHERE ticker = 'RELIANCE.NS' ORDER BY start_date"
        ).fetchall()

        assert len(rows) == 2

    def test_bridging_download_merges_disjoint_ranges(self, db_conn):
        """
        Store [Jan 2-3] and [Jan 8-9], then store [Jan 4-7].
        All three should merge into a single [Jan 2-9].
        """
        df1 = _make_sample_df(["2024-01-02", "2024-01-03"])
        store_data(db_conn, "RELIANCE.NS", df1, "2024-01-02", "2024-01-03")

        df2 = _make_sample_df(["2024-01-08", "2024-01-09"])
        store_data(db_conn, "RELIANCE.NS", df2, "2024-01-08", "2024-01-09")

        df3 = _make_sample_df(
            ["2024-01-04", "2024-01-05", "2024-01-06", "2024-01-07"],
        )
        store_data(db_conn, "RELIANCE.NS", df3, "2024-01-04", "2024-01-07")

        rows = db_conn.execute(
            "SELECT start_date, end_date FROM market_data_ranges "
            "WHERE ticker = 'RELIANCE.NS'"
        ).fetchall()

        assert len(rows) == 1
        assert rows[0] == ("2024-01-02", "2024-01-09")
