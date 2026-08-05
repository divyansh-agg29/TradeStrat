"""
Tests for the Chart Serializer.
"""

import pandas as pd
import pytest

from serialization.chart_serializer import build_charts


# ── Helpers ───────────────────────────────────────────────────


def _make_portfolio_history(
    indicator_columns=None,
):
    """
    Create a minimal portfolio history DataFrame with a Date index.
    """

    dates = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"])

    data = {
        "Open": [100.0, 101.0, 102.0],
        "High": [105.0, 106.0, 107.0],
        "Low": [99.0, 100.0, 101.0],
        "Close": [101.0, 103.0, 105.0],
        "Volume": [1000, 1100, 1200],
        "Signal": ["BUY", "HOLD", "SELL"],
        "Cash": [0.0, 0.0, 100000.0],
        "Shares": [990, 990, 0],
        "Holdings Value": [99990.0, 101970.0, 0.0],
        "Portfolio Value": [99990.0, 101970.0, 100000.0],
        "Position": ["LONG", "LONG", "FLAT"],
    }

    if indicator_columns:
        data.update(indicator_columns)

    df = pd.DataFrame(data, index=dates)
    df.index.name = "Date"

    return df


def _make_analytics_history():
    """
    Create a minimal analytics history DataFrame.
    """

    dates = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"])

    df = pd.DataFrame(
        {
            "Portfolio Value": [100000.0, 101000.0, 102000.0],
            "Buy & Hold Value": [100000.0, 100500.0, 101000.0],
            "Drawdown": [0.0, 0.0, 500.0],
        },
        index=dates,
    )
    df.index.name = "Date"

    return df


def _make_trade_history(trades=None):
    """
    Create a trade history DataFrame.

    If trades is None, returns a DataFrame with one signal exit.
    """

    if trades is None:
        trades = [
            {
                "entry_date": pd.Timestamp("2020-01-02"),
                "exit_date": pd.Timestamp("2020-01-06"),
                "entry_price": 101.0,
                "exit_price": 105.0,
                "shares": 990,
                "investment": 99990.0,
                "exit_value": 103950.0,
                "profit_loss": 3960.0,
                "return_pct": 3.96,
                "holding_period": 2,
                "exit_reason": "signal",
                "stop_loss_price": None,
                "take_profit_price": None,
            }
        ]

    return pd.DataFrame(trades)


def _make_empty_trade_history():
    """
    Create an empty trade history DataFrame.
    """

    return pd.DataFrame()


# ── Price Chart ──────────────────────────────────────────────


def test_build_price_chart_includes_close_trace():
    """
    Price chart should always include a Close price line.
    """

    charts = build_charts(
        _make_portfolio_history(),
        _make_trade_history(),
        _make_analytics_history(),
    )

    price_traces = charts["price_chart"]["traces"]
    close_trace = next(t for t in price_traces if t["id"] == "close")

    assert close_trace["type"] == "line"
    assert close_trace["name"] == "Close"
    assert len(close_trace["x"]) == 3
    assert close_trace["y"] == [101.0, 103.0, 105.0]


def test_build_price_chart_includes_indicator_traces():
    """
    Price chart should include indicator overlay traces.
    """

    charts = build_charts(
        _make_portfolio_history(
            indicator_columns={
                "SMA20": [100.0, 101.0, 102.0],
                "EMA50": [99.0, 100.0, 101.0],
            }
        ),
        _make_trade_history(),
        _make_analytics_history(),
    )

    price_traces = charts["price_chart"]["traces"]
    trace_ids = [t["id"] for t in price_traces]

    assert "sma20" in trace_ids
    assert "ema50" in trace_ids

    sma_trace = next(t for t in price_traces if t["id"] == "sma20")
    assert sma_trace["type"] == "indicator_line"
    assert sma_trace["name"] == "SMA20"


def test_build_price_chart_excludes_non_indicator_columns():
    """
    Columns like Signal, Cash, Shares should not appear as traces.
    """

    charts = build_charts(
        _make_portfolio_history(),
        _make_trade_history(),
        _make_analytics_history(),
    )

    price_traces = charts["price_chart"]["traces"]
    trace_ids = [t["id"] for t in price_traces]

    assert "signal" not in trace_ids
    assert "cash" not in trace_ids
    assert "position" not in trace_ids


def test_build_price_chart_includes_execution_markers():
    """
    Price chart should include execution marker traces.
    """

    charts = build_charts(
        _make_portfolio_history(),
        _make_trade_history(),
        _make_analytics_history(),
    )

    price_traces = charts["price_chart"]["traces"]
    trace_ids = [t["id"] for t in price_traces]

    assert "buy_executed" in trace_ids
    assert "sell_signal_exit" in trace_ids


def test_execution_markers_use_correct_category():
    """
    Each execution marker should have the correct category.
    """

    trades = [
        {
            "entry_date": pd.Timestamp("2020-01-02"),
            "exit_date": pd.Timestamp("2020-01-03"),
            "entry_price": 101.0,
            "exit_price": 95.0,
            "shares": 990,
            "investment": 99990.0,
            "exit_value": 94050.0,
            "profit_loss": -5940.0,
            "return_pct": -5.94,
            "holding_period": 1,
            "exit_reason": "stop_loss",
            "stop_loss_price": 95.95,
            "take_profit_price": None,
        },
        {
            "entry_date": pd.Timestamp("2020-01-03"),
            "exit_date": pd.Timestamp("2020-01-06"),
            "entry_price": 103.0,
            "exit_price": 120.0,
            "shares": 990,
            "investment": 101970.0,
            "exit_value": 118800.0,
            "profit_loss": 16830.0,
            "return_pct": 16.50,
            "holding_period": 1,
            "exit_reason": "take_profit",
            "stop_loss_price": None,
            "take_profit_price": 120.0,
        },
    ]

    charts = build_charts(
        _make_portfolio_history(),
        _make_trade_history(trades),
        _make_analytics_history(),
    )

    price_traces = charts["price_chart"]["traces"]

    buy_marker = next(t for t in price_traces if t["id"] == "buy_executed")
    assert buy_marker["category"] == "buy"
    assert len(buy_marker["x"]) == 2

    sl_marker = next(t for t in price_traces if t["id"] == "stop_loss_exit")
    assert sl_marker["category"] == "stop_loss"
    assert len(sl_marker["x"]) == 1

    tp_marker = next(t for t in price_traces if t["id"] == "take_profit_exit")
    assert tp_marker["category"] == "take_profit"
    assert len(tp_marker["x"]) == 1


def test_empty_trade_history_produces_no_markers():
    """
    An empty trade history should produce no execution markers.
    """

    charts = build_charts(
        _make_portfolio_history(),
        _make_empty_trade_history(),
        _make_analytics_history(),
    )

    price_traces = charts["price_chart"]["traces"]
    marker_traces = [t for t in price_traces if t["type"] == "execution_marker"]

    assert len(marker_traces) == 0


# ── Signal Markers ───────────────────────────────────────────


def test_build_price_chart_includes_signal_markers():
    """
    Price chart should include signal marker traces.
    """

    charts = build_charts(
        _make_portfolio_history(),
        _make_trade_history(),
        _make_analytics_history(),
    )

    price_traces = charts["price_chart"]["traces"]
    trace_ids = [t["id"] for t in price_traces]

    assert "buy_signal" in trace_ids
    assert "sell_signal" in trace_ids

    buy_sig = next(t for t in price_traces if t["id"] == "buy_signal")
    assert buy_sig["type"] == "signal_marker"
    assert buy_sig["group"] == "signals"
    assert buy_sig["category"] == "buy"

    sell_sig = next(t for t in price_traces if t["id"] == "sell_signal")
    assert sell_sig["type"] == "signal_marker"
    assert sell_sig["group"] == "signals"
    assert sell_sig["category"] == "sell"


def test_execution_markers_have_executions_group():
    """
    All execution markers should have group='executions'.
    """

    charts = build_charts(
        _make_portfolio_history(),
        _make_trade_history(),
        _make_analytics_history(),
    )

    price_traces = charts["price_chart"]["traces"]
    exec_traces = [t for t in price_traces if t["type"] == "execution_marker"]

    for trace in exec_traces:
        assert trace["group"] == "executions"


# ── Equity Chart ─────────────────────────────────────────────


def test_build_equity_chart_includes_strategy_and_benchmark():
    """
    Equity chart should include strategy and benchmark traces.
    """

    charts = build_charts(
        _make_portfolio_history(),
        _make_trade_history(),
        _make_analytics_history(),
    )

    equity_traces = charts["equity_chart"]["traces"]
    trace_ids = [t["id"] for t in equity_traces]

    assert "strategy" in trace_ids
    assert "benchmark" in trace_ids

    strategy_trace = next(t for t in equity_traces if t["id"] == "strategy")
    assert strategy_trace["type"] == "line"
    assert strategy_trace["y"] == [100000.0, 101000.0, 102000.0]

    benchmark_trace = next(t for t in equity_traces if t["id"] == "benchmark")
    assert benchmark_trace["type"] == "benchmark_line"
    assert benchmark_trace["y"] == [100000.0, 100500.0, 101000.0]


# ── Drawdown Chart ───────────────────────────────────────────


def test_build_drawdown_chart_includes_drawdown_trace():
    """
    Drawdown chart should include a drawdown area trace.
    """

    charts = build_charts(
        _make_portfolio_history(),
        _make_trade_history(),
        _make_analytics_history(),
    )

    dd_traces = charts["drawdown_chart"]["traces"]

    assert len(dd_traces) == 1

    dd_trace = dd_traces[0]
    assert dd_trace["id"] == "drawdown"
    assert dd_trace["type"] == "area"
    assert dd_trace["y"] == [0.0, 0.0, 500.0]


# ── Top-Level Structure ──────────────────────────────────────


def test_build_charts_returns_all_chart_keys():
    """
    build_charts should return price, equity, and drawdown charts.
    """

    charts = build_charts(
        _make_portfolio_history(),
        _make_trade_history(),
        _make_analytics_history(),
    )

    assert set(charts.keys()) == {"price_chart", "equity_chart", "drawdown_chart"}
    assert "traces" in charts["price_chart"]
    assert "traces" in charts["equity_chart"]
    assert "traces" in charts["drawdown_chart"]
