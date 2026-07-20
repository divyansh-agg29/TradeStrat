"""
Unit tests for the Analytics Engine.
"""

import math

import pandas as pd
import pytest

from analytics import analyze_performance
from portfolio.simulator import SimulationResult


# ============================================================================
# Helper Functions
# ============================================================================

def create_simulation_result(
    portfolio_values,
    trade_history=None,
    close_prices=None,
):
    """
    Create a minimal SimulationResult for testing.
    """

    if close_prices is None:
        close_prices = [v / 100 for v in portfolio_values]

    portfolio_history = pd.DataFrame(
        {
            "Portfolio Value": portfolio_values,
            "Close": close_prices,
        },
        index=pd.date_range(
            start="2025-01-01",
            periods=len(portfolio_values),
            freq="B",
        ),
    )

    if trade_history is None:
        trade_history = pd.DataFrame()

    summary = {
        "initial_capital": portfolio_values[0],
        "final_portfolio_value": portfolio_values[-1],
    }

    return SimulationResult(
        portfolio_history=portfolio_history,
        trade_history=trade_history,
        summary=summary,
    )

# ============================================================================
# Validation Tests
# ============================================================================

def test_analyze_performance_rejects_non_simulation_result():
    """
    Analytics should only accept a SimulationResult.
    """

    with pytest.raises(
        TypeError,
        match="Input must be a SimulationResult.",
    ):
        analyze_performance("invalid")


def test_analyze_performance_rejects_empty_portfolio_history():
    """
    Portfolio history cannot be empty.
    """

    simulation_result = SimulationResult(
        portfolio_history=pd.DataFrame(),
        trade_history=pd.DataFrame(),
        summary={
            "initial_capital": 100000,
            "final_portfolio_value": 100000,
        },
    )

    with pytest.raises(
        ValueError,
        match="Portfolio history cannot be empty.",
    ):
        analyze_performance(simulation_result)


def test_analyze_performance_rejects_missing_portfolio_value_column():
    """
    Portfolio history must contain the Portfolio Value column.
    """

    portfolio_history = pd.DataFrame(
        {
            "Close": [100, 101, 102],
        }
    )

    simulation_result = SimulationResult(
        portfolio_history=portfolio_history,
        trade_history=pd.DataFrame(),
        summary={
            "initial_capital": 100000,
            "final_portfolio_value": 102000,
        },
    )

    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        analyze_performance(simulation_result)


def test_analyze_performance_rejects_missing_summary_fields():
    """
    Required summary fields must be present.
    """

    simulation_result = SimulationResult(
        portfolio_history=pd.DataFrame(
            {
                "Portfolio Value": [100000, 101000],
                "Close": [1000, 1010],
            }
        ),
        trade_history=pd.DataFrame(),
        summary={},
    )

    with pytest.raises(
        ValueError,
        match="Simulation summary is missing required fields",
    ):
        analyze_performance(simulation_result)


# ============================================================================
# Portfolio Metrics Tests
# ============================================================================

def test_portfolio_metrics_positive_return():
    """
    Portfolio metrics should be calculated correctly for a profitable
    portfolio.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            105000,
            110000,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    metrics = analytics_result.portfolio_metrics

    assert metrics.initial_capital == 100000
    assert metrics.final_portfolio_value == 110000
    assert metrics.profit_loss == 10000
    assert metrics.total_return == pytest.approx(10.0)

    assert metrics.cagr > 0


def test_portfolio_metrics_negative_return():
    """
    Portfolio metrics should be calculated correctly for a losing
    portfolio.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            98000,
            95000,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    metrics = analytics_result.portfolio_metrics

    assert metrics.initial_capital == 100000
    assert metrics.final_portfolio_value == 95000
    assert metrics.profit_loss == -5000
    assert metrics.total_return == pytest.approx(-5.0)

    assert metrics.cagr < 0


def test_portfolio_metrics_zero_return():
    """
    Portfolio metrics should correctly handle a flat portfolio.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            100000,
            100000,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    metrics = analytics_result.portfolio_metrics

    assert metrics.initial_capital == 100000
    assert metrics.final_portfolio_value == 100000
    assert metrics.profit_loss == 0
    assert metrics.total_return == pytest.approx(0.0)
    assert metrics.cagr == pytest.approx(0.0)


def test_portfolio_metrics_single_trading_day():
    """
    CAGR should be zero when only one trading day is present.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    assert (
        analytics_result.portfolio_metrics.cagr
        == pytest.approx(0.0)
    )


# ============================================================================
# Analytics History Tests
# ============================================================================

def test_analytics_history_contains_expected_columns():
    """
    Analytics history should contain all derived columns.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            102000,
            101000,
            104000,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    analytics_history = analytics_result.analytics_history

    expected_columns = {
        "Portfolio Value",
        "Daily Return %",
        "Running Peak",
        "Drawdown",
        "Drawdown %",
    }

    assert expected_columns.issubset(
        analytics_history.columns
    )


def test_daily_return_calculation():
    """
    Daily returns should be calculated correctly.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100,
            110,
            121,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    daily_returns = (
        analytics_result.analytics_history[
            "Daily Return %"
        ]
    )

    assert daily_returns.iloc[0] == pytest.approx(0.0)
    assert daily_returns.iloc[1] == pytest.approx(10.0)
    assert daily_returns.iloc[2] == pytest.approx(10.0)


def test_running_peak_calculation():
    """
    Running peak should never decrease.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100,
            120,
            110,
            140,
            130,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    running_peak = (
        analytics_result.analytics_history[
            "Running Peak"
        ]
    )

    expected = [
        100,
        120,
        120,
        140,
        140,
    ]

    assert list(running_peak) == expected


def test_drawdown_calculation():
    """
    Drawdown should be calculated correctly.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100,
            120,
            110,
            90,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    drawdown = (
        analytics_result.analytics_history[
            "Drawdown"
        ]
    )

    expected = [
        0,
        0,
        10,
        30,
    ]

    assert list(drawdown) == expected


def test_drawdown_percentage_calculation():
    """
    Drawdown percentage should be calculated correctly.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100,
            120,
            110,
            90,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    drawdown_pct = (
        analytics_result.analytics_history[
            "Drawdown %"
        ]
    )

    assert drawdown_pct.iloc[0] == pytest.approx(0.0)
    assert drawdown_pct.iloc[1] == pytest.approx(0.0)
    assert drawdown_pct.iloc[2] == pytest.approx(8.3333333333)
    assert drawdown_pct.iloc[3] == pytest.approx(25.0)


# ============================================================================
# Risk Metrics Tests
# ============================================================================

def test_annualized_volatility_zero_for_constant_portfolio():
    """
    Volatility should be zero for a portfolio whose value never changes.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            100000,
            100000,
            100000,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    assert (
        analytics_result.risk_metrics.annualized_volatility
        == pytest.approx(0.0)
    )


def test_annualized_volatility_positive_for_changing_portfolio():
    """
    Volatility should be positive when portfolio value changes.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            102000,
            101000,
            104000,
            103000,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    assert (
        analytics_result.risk_metrics.annualized_volatility
        > 0
    )


def test_maximum_drawdown_calculation():
    """
    Maximum drawdown should equal the largest drawdown percentage.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100,
            120,
            110,
            90,
            130,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    assert (
        analytics_result.risk_metrics.maximum_drawdown
        == pytest.approx(25.0)
    )


def test_sharpe_ratio_is_zero_for_flat_portfolio():
    """
    Sharpe Ratio should be zero when both the average excess return
    and volatility are zero.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            100000,
            100000,
            100000,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    assert (
        analytics_result.risk_metrics.sharpe_ratio
        == pytest.approx(0.0)
    )


def test_sharpe_ratio_returns_finite_value():
    """
    Sharpe Ratio should be finite for a portfolio with changing returns.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            102000,
            101000,
            104000,
            103000,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    assert math.isfinite(
        analytics_result.risk_metrics.sharpe_ratio
    )


# ============================================================================
# Trade Metrics Tests
# ============================================================================

def test_trade_metrics_empty_trade_history():
    """
    Trade metrics should return default values when no completed trades
    are present.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            101000,
            102000,
        ]
    )

    analytics_result = analyze_performance(simulation_result)

    metrics = analytics_result.trade_metrics

    assert metrics.total_trades == 0
    assert metrics.winning_trades == 0
    assert metrics.losing_trades == 0
    assert metrics.win_rate == 0.0
    assert metrics.average_winning_trade == 0.0
    assert metrics.average_losing_trade == 0.0
    assert metrics.largest_winner == 0.0
    assert metrics.largest_loser == 0.0
    assert metrics.average_holding_period == 0.0


def test_trade_metrics_calculated_correctly():
    """
    Trade statistics should be calculated correctly.
    """

    trade_history = pd.DataFrame(
        {
            "profit_loss": [1000, -500, 2000],
            "holding_period": [10, 5, 15],
        }
    )

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            102000,
            101000,
            103000,
        ],
        trade_history=trade_history,
    )

    analytics_result = analyze_performance(simulation_result)

    metrics = analytics_result.trade_metrics

    assert metrics.total_trades == 3
    assert metrics.winning_trades == 2
    assert metrics.losing_trades == 1

    assert metrics.win_rate == pytest.approx(66.6666666667)

    assert metrics.average_winning_trade == pytest.approx(1500.0)
    assert metrics.average_losing_trade == pytest.approx(-500.0)

    assert metrics.largest_winner == 2000
    assert metrics.largest_loser == -500

    assert metrics.profit_factor == pytest.approx(6.0)

    assert metrics.average_holding_period == pytest.approx(10.0)


def test_profit_factor_is_infinite_when_no_losses():
    """
    Profit Factor should be infinite when gross loss is zero.
    """

    trade_history = pd.DataFrame(
        {
            "profit_loss": [1000, 500, 200],
            "holding_period": [5, 8, 4],
        }
    )

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            101000,
            103000,
        ],
        trade_history=trade_history,
    )

    analytics_result = analyze_performance(simulation_result)

    assert math.isinf(
        analytics_result.trade_metrics.profit_factor
    )


def test_trade_metrics_all_losing_trades():
    """
    Trade statistics should handle all losing trades correctly.
    """

    trade_history = pd.DataFrame(
        {
            "profit_loss": [-500, -1000, -200],
            "holding_period": [4, 8, 3],
        }
    )

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            98000,
            96000,
        ],
        trade_history=trade_history,
    )

    analytics_result = analyze_performance(simulation_result)

    metrics = analytics_result.trade_metrics

    assert metrics.total_trades == 3
    assert metrics.winning_trades == 0
    assert metrics.losing_trades == 3

    assert metrics.win_rate == 0.0

    assert metrics.average_winning_trade == 0.0
    assert metrics.average_losing_trade == pytest.approx(-566.6666666667)

    assert metrics.largest_winner == 0.0
    assert metrics.largest_loser == -1000

    assert metrics.profit_factor == pytest.approx(0.0)

# ============================================================================
# End-to-End Tests
# ============================================================================

def test_analyze_performance_returns_complete_analytics_result():
    """
    Analytics Engine should return a fully populated AnalyticsResult.
    """

    trade_history = pd.DataFrame(
        {
            "profit_loss": [1000, -500, 2000],
            "holding_period": [5, 10, 15],
        }
    )

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            102000,
            101000,
            104000,
            106000,
        ],
        trade_history=trade_history,
    )

    analytics_result = analyze_performance(
        simulation_result
    )

    assert analytics_result.portfolio_metrics is not None
    assert analytics_result.risk_metrics is not None
    assert analytics_result.trade_metrics is not None
    assert not analytics_result.analytics_history.empty


def test_analytics_history_preserves_row_count():
    """
    Analytics history should contain one row for every row in the
    original portfolio history.
    """

    portfolio_values = [
        100000,
        101000,
        102000,
        101500,
        103000,
        104500,
    ]

    simulation_result = create_simulation_result(
        portfolio_values=portfolio_values
    )

    analytics_result = analyze_performance(
        simulation_result
    )

    assert len(
        analytics_result.analytics_history
    ) == len(
        simulation_result.portfolio_history
    )



def test_original_portfolio_history_is_not_modified():
    """
    Analytics Engine should not modify the original portfolio history.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            101000,
            102000,
        ]
    )

    original_columns = list(
        simulation_result.portfolio_history.columns
    )

    analyze_performance(simulation_result)

    assert (
        list(simulation_result.portfolio_history.columns)
        == original_columns
    )


# ============================================================================
# Benchmark Metrics Tests
# ============================================================================

def test_benchmark_metrics_calculated_correctly():
    """
    Buy & Hold metrics should match manual computation.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            105000,
            110000,
        ],
        close_prices=[
            100,
            110,
            120,
        ],
    )

    analytics_result = analyze_performance(simulation_result)

    metrics = analytics_result.benchmark_metrics

    # Buy & Hold: 100000 / 100 = 1000 shares, final = 1000 * 120 = 120000
    assert metrics.benchmark_final_value == pytest.approx(120000.0)
    assert metrics.benchmark_return == pytest.approx(20.0)


def test_benchmark_return_matches_stock_return():
    """
    Buy & Hold return should equal the stock's percentage change.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            100000,
            100000,
        ],
        close_prices=[
            200,
            250,
            300,
        ],
    )

    analytics_result = analyze_performance(simulation_result)

    # Stock went from 200 to 300 = 50%
    assert (
        analytics_result.benchmark_metrics.benchmark_return
        == pytest.approx(50.0)
    )


def test_alpha_positive_when_strategy_outperforms():
    """
    Alpha should be positive when strategy return exceeds benchmark.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            120000,
            150000,
        ],
        close_prices=[
            100,
            105,
            110,
        ],
    )

    analytics_result = analyze_performance(simulation_result)

    # Strategy return = 50%, Benchmark return = 10%
    assert analytics_result.benchmark_metrics.alpha > 0
    assert analytics_result.benchmark_metrics.alpha == pytest.approx(40.0)


def test_alpha_negative_when_strategy_underperforms():
    """
    Alpha should be negative when strategy return is below benchmark.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            99000,
            98000,
        ],
        close_prices=[
            100,
            110,
            120,
        ],
    )

    analytics_result = analyze_performance(simulation_result)

    # Strategy return = -2%, Benchmark return = 20%
    assert analytics_result.benchmark_metrics.alpha < 0


def test_alpha_zero_when_equal():
    """
    Alpha should be approximately zero when strategy matches benchmark.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            110000,
            120000,
        ],
        close_prices=[
            100,
            110,
            120,
        ],
    )

    analytics_result = analyze_performance(simulation_result)

    # Strategy return = 20%, Benchmark return = 20%
    assert (
        analytics_result.benchmark_metrics.alpha
        == pytest.approx(0.0)
    )


def test_analytics_history_contains_buy_hold_column():
    """
    Analytics history should contain the Buy & Hold Value column.
    """

    simulation_result = create_simulation_result(
        portfolio_values=[
            100000,
            102000,
            104000,
        ],
        close_prices=[
            100,
            102,
            104,
        ],
    )

    analytics_result = analyze_performance(simulation_result)

    assert (
        "Buy & Hold Value"
        in analytics_result.analytics_history.columns
    )