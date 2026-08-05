"""
Chart Serializer

Builds backend-driven chart specifications from simulation and
analytics results.  Each chart is a dictionary of semantic traces
that the frontend maps to Plotly styles.

Trace types
-----------
line              Primary data line (e.g. Close price)
indicator_line    Technical indicator overlay (SMA, EMA, …)
benchmark_line    Buy & Hold reference line
area              Filled area chart (drawdown)
execution_marker  Trade entry / exit marker (buy, sell_signal,
                  stop_loss, take_profit)
"""

import pandas as pd

from utils.logger import get_logger

logger = get_logger(__name__)

_NON_INDICATOR_COLUMNS = frozenset([
    "Date", "Open", "High", "Low", "Close", "Volume",
    "Signal", "Cash", "Shares", "Holdings Value",
    "Portfolio Value", "Position",
])

_INDICATOR_PREFIXES = (
    "SMA",
    "EMA",
    "RSI",
    "MACD",
    "BB",
)


def build_charts(
    portfolio_history: pd.DataFrame,
    trade_history: pd.DataFrame,
    analytics_history: pd.DataFrame,
) -> dict:
    """
    Build chart specifications for the backtest dashboard.

    Returns a dict with keys ``price_chart``, ``equity_chart``,
    and ``drawdown_chart``, each containing a list of traces.
    """

    return {
        "price_chart": _build_price_chart(portfolio_history, trade_history),
        "equity_chart": _build_equity_chart(analytics_history),
        "drawdown_chart": _build_drawdown_chart(analytics_history),
    }


# ── Price Chart ──────────────────────────────────────────────


def _build_price_chart(
    portfolio_history: pd.DataFrame,
    trade_history: pd.DataFrame,
) -> dict:
    """
    Build the price chart specification.

    Includes close price, indicator overlays, and execution markers.
    """

    history = portfolio_history.reset_index()
    date_column = _resolve_date_column(history)
    dates = _dates_to_strings(history[date_column])
    close_prices = history["Close"].tolist()

    traces = []

    traces.append({
        "id": "close",
        "type": "line",
        "name": "Close",
        "x": dates,
        "y": close_prices,
    })

    for column in history.columns:
        if _is_indicator_column(column):
            values = history[column].where(
                pd.notnull(history[column]), None
            ).tolist()
            traces.append({
                "id": column.lower().replace(" ", "_"),
                "type": "indicator_line",
                "name": column,
                "x": dates,
                "y": values,
            })

    traces.extend(
        _build_signal_markers(history, date_column)
    )

    traces.extend(
        _build_execution_markers(trade_history, history)
    )

    return {"traces": traces}


def _is_indicator_column(column: str) -> bool:
    """Return True if the column is a technical indicator."""

    if column in _NON_INDICATOR_COLUMNS:
        return False

    return any(column.startswith(prefix) for prefix in _INDICATOR_PREFIXES)


def _build_signal_markers(
    portfolio_history: pd.DataFrame,
    date_column: str,
) -> list[dict]:
    """
    Build signal marker traces from the portfolio history.

    These show every BUY / SELL signal the strategy generated,
    regardless of whether the signal was actually executed.
    """

    if "Signal" not in portfolio_history.columns:
        return []

    markers = []

    buy_rows = portfolio_history[portfolio_history["Signal"] == "BUY"]
    if not buy_rows.empty:
        markers.append({
            "id": "buy_signal",
            "type": "signal_marker",
            "category": "buy",
            "group": "signals",
            "name": "BUY Signal",
            "x": _dates_to_strings(buy_rows[date_column]),
            "y": buy_rows["Close"].tolist(),
        })

    sell_rows = portfolio_history[portfolio_history["Signal"] == "SELL"]
    if not sell_rows.empty:
        markers.append({
            "id": "sell_signal",
            "type": "signal_marker",
            "category": "sell",
            "group": "signals",
            "name": "SELL Signal",
            "x": _dates_to_strings(sell_rows[date_column]),
            "y": sell_rows["Close"].tolist(),
        })

    return markers


def _build_execution_markers(
    trade_history: pd.DataFrame,
    portfolio_history: pd.DataFrame,
) -> list[dict]:
    """
    Build execution marker traces from the completed trade history.

    Returns up to four marker traces: buy executions, sell-signal
    exits, stop-loss exits, and take-profit exits.
    """

    required_columns = {"entry_date", "entry_price", "exit_date", "exit_price", "exit_reason"}

    if trade_history.empty or not required_columns.issubset(trade_history.columns):
        return []

    markers = []

    entry_dates = _dates_to_strings(trade_history["entry_date"])
    entry_prices = trade_history["entry_price"].tolist()

    if entry_dates:
        markers.append({
            "id": "buy_executed",
            "type": "execution_marker",
            "category": "buy",
            "group": "executions",
            "name": "BUY Executed",
            "x": entry_dates,
            "y": entry_prices,
        })

    exit_categories = {
        "signal": ("sell_signal_exit", "sell_signal", "SELL (Signal)"),
        "stop_loss": ("stop_loss_exit", "stop_loss", "Stop Loss"),
        "take_profit": ("take_profit_exit", "take_profit", "Take Profit"),
    }

    for reason, (trace_id, category, label) in exit_categories.items():
        subset = trade_history[trade_history["exit_reason"] == reason]

        if subset.empty:
            continue

        markers.append({
            "id": trace_id,
            "type": "execution_marker",
            "category": category,
            "group": "executions",
            "name": label,
            "x": _dates_to_strings(subset["exit_date"]),
            "y": subset["exit_price"].tolist(),
        })

    return markers


# ── Equity Chart ─────────────────────────────────────────────


def _build_equity_chart(
    analytics_history: pd.DataFrame,
) -> dict:
    """
    Build the equity chart specification.

    Includes strategy equity curve and buy-and-hold benchmark.
    """

    history = analytics_history.reset_index()
    date_column = _resolve_date_column(history)
    dates = _dates_to_strings(history[date_column])

    traces = [
        {
            "id": "strategy",
            "type": "line",
            "name": "Strategy",
            "x": dates,
            "y": history["Portfolio Value"].tolist(),
        },
        {
            "id": "benchmark",
            "type": "benchmark_line",
            "name": "Buy & Hold",
            "x": dates,
            "y": history["Buy & Hold Value"].tolist(),
        },
    ]

    return {"traces": traces}


# ── Drawdown Chart ───────────────────────────────────────────


def _build_drawdown_chart(
    analytics_history: pd.DataFrame,
) -> dict:
    """
    Build the drawdown chart specification.
    """

    history = analytics_history.reset_index()
    date_column = _resolve_date_column(history)
    dates = _dates_to_strings(history[date_column])

    drawdown_column = _resolve_drawdown_column(history)
    drawdown_values = history[drawdown_column].tolist() if drawdown_column else []

    traces = [
        {
            "id": "drawdown",
            "type": "area",
            "name": "Drawdown",
            "x": dates,
            "y": drawdown_values,
        },
    ]

    return {"traces": traces}


# ── Helpers ──────────────────────────────────────────────────


def _resolve_date_column(df: pd.DataFrame) -> str:
    """
    Find the date column name after a reset_index.

    The production DataFrames use an index named "Date".
    Fallback to the first column for test fixtures that
    have an unnamed index (reset_index creates "index").
    """

    if "Date" in df.columns:
        return "Date"

    return df.columns[0]


def _resolve_drawdown_column(df: pd.DataFrame) -> str | None:
    """
    Find the drawdown column after a reset_index.

    Production analytics DataFrames have both "Drawdown" (absolute)
    and "Drawdown %" columns.  Return "Drawdown" when available,
    fall back to "Drawdown %", or None.
    """

    if "Drawdown" in df.columns:
        return "Drawdown"

    if "Drawdown %" in df.columns:
        return "Drawdown %"

    return None


def _dates_to_strings(series: pd.Series) -> list[str]:
    """Convert a datetime series to ISO-format strings."""

    return [
        d.isoformat() if hasattr(d, "isoformat") else str(d)
        for d in series
    ]
