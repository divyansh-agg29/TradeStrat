"""
Unit tests for the KPI Interpreter module.
"""

import math

import pytest

from analytics import (
    AnalyticsResult,
    BenchmarkMetrics,
    PortfolioMetrics,
    RiskMetrics,
    TradeMetrics,
)
from interpretation.kpi_interpreter import (
    build_kpi_cards,
    _evaluate_interpretation,
    KPI_DEFINITIONS,
)


# ============================================================================
# Helper Functions
# ============================================================================

def make_analytics_result(**overrides):
    """
    Create an AnalyticsResult with sensible defaults.
    Individual metric fields can be overridden via keyword arguments
    prefixed with the source name (e.g. portfolio_cagr=15.0).
    """

    portfolio_overrides = {}
    risk_overrides = {}
    trade_overrides = {}
    benchmark_overrides = {}

    for key, value in overrides.items():
        if key.startswith("portfolio_"):
            portfolio_overrides[key[len("portfolio_"):]] = value
        elif key.startswith("risk_"):
            risk_overrides[key[len("risk_"):]] = value
        elif key.startswith("trade_"):
            trade_overrides[key[len("trade_"):]] = value
        elif key.startswith("benchmark_"):
            benchmark_overrides[key[len("benchmark_"):]] = value

    portfolio_defaults = dict(
        initial_capital=100000.0,
        final_portfolio_value=110000.0,
        profit_loss=10000.0,
        total_return=10.0,
        cagr=10.0,
    )
    portfolio_defaults.update(portfolio_overrides)

    risk_defaults = dict(
        annualized_volatility=15.0,
        maximum_drawdown=10.0,
        sharpe_ratio=1.2,
        sortino_ratio=1.0,
        calmar_ratio=0.9,
    )
    risk_defaults.update(risk_overrides)

    trade_defaults = dict(
        total_trades=5,
        winning_trades=3,
        losing_trades=2,
        win_rate=60.0,
        average_winning_trade=5000.0,
        average_losing_trade=-2500.0,
        largest_winner=8000.0,
        largest_loser=-4000.0,
        profit_factor=2.0,
        average_holding_period=30.0,
    )
    trade_defaults.update(trade_overrides)

    benchmark_defaults = dict(
        benchmark_final_value=105000.0,
        benchmark_return=5.0,
        alpha=5.0,
    )
    benchmark_defaults.update(benchmark_overrides)

    return AnalyticsResult(
        portfolio_metrics=PortfolioMetrics(**portfolio_defaults),
        risk_metrics=RiskMetrics(**risk_defaults),
        trade_metrics=TradeMetrics(**trade_defaults),
        benchmark_metrics=BenchmarkMetrics(**benchmark_defaults),
    )


# ============================================================================
# Structure Tests
# ============================================================================

class TestBuildKpiCardsStructure:

    def test_returns_all_ten_keys(self):
        result = make_analytics_result()
        kpi_cards = build_kpi_cards(result)
        expected_keys = {d.key for d in KPI_DEFINITIONS}
        assert set(kpi_cards.keys()) == expected_keys

    def test_returns_exactly_ten_entries(self):
        result = make_analytics_result()
        kpi_cards = build_kpi_cards(result)
        assert len(kpi_cards) == 10

    def test_each_entry_has_value_and_format_type(self):
        result = make_analytics_result()
        kpi_cards = build_kpi_cards(result)
        for key, entry in kpi_cards.items():
            assert "value" in entry, f"{key} missing 'value'"
            assert "format_type" in entry, f"{key} missing 'format_type'"

    def test_interpreted_kpis_have_interpretation(self):
        result = make_analytics_result()
        kpi_cards = build_kpi_cards(result)
        interpreted_keys = {
            d.key for d in KPI_DEFINITIONS
            if d.thresholds is not None
        }
        for key in interpreted_keys:
            assert "interpretation" in kpi_cards[key], (
                f"{key} should have interpretation"
            )

    def test_non_interpreted_kpis_omit_interpretation(self):
        result = make_analytics_result()
        kpi_cards = build_kpi_cards(result)
        non_interpreted_keys = {
            d.key for d in KPI_DEFINITIONS
            if d.thresholds is None
        }
        for key in non_interpreted_keys:
            assert "interpretation" not in kpi_cards[key], (
                f"{key} should not have interpretation"
            )


# ============================================================================
# Value Extraction Tests
# ============================================================================

class TestValueExtraction:

    def test_portfolio_value_extracted(self):
        result = make_analytics_result(
            portfolio_final_portfolio_value=120000.0,
        )
        kpi_cards = build_kpi_cards(result)
        assert kpi_cards["final_portfolio_value"]["value"] == 120000.0

    def test_risk_value_extracted(self):
        result = make_analytics_result(risk_sharpe_ratio=1.8)
        kpi_cards = build_kpi_cards(result)
        assert kpi_cards["sharpe_ratio"]["value"] == 1.8

    def test_trade_value_extracted(self):
        result = make_analytics_result(trade_total_trades=10)
        kpi_cards = build_kpi_cards(result)
        assert kpi_cards["total_trades"]["value"] == 10

    def test_benchmark_value_extracted(self):
        result = make_analytics_result(benchmark_alpha=7.5)
        kpi_cards = build_kpi_cards(result)
        assert kpi_cards["alpha"]["value"] == 7.5


# ============================================================================
# Format Type Tests
# ============================================================================

class TestFormatTypes:

    def test_currency_format(self):
        result = make_analytics_result()
        kpi_cards = build_kpi_cards(result)
        assert kpi_cards["final_portfolio_value"]["format_type"] == "currency"

    def test_percentage_format(self):
        result = make_analytics_result()
        kpi_cards = build_kpi_cards(result)
        assert kpi_cards["total_return"]["format_type"] == "percentage"
        assert kpi_cards["cagr"]["format_type"] == "percentage"

    def test_number_format(self):
        result = make_analytics_result()
        kpi_cards = build_kpi_cards(result)
        assert kpi_cards["sharpe_ratio"]["format_type"] == "number"
        assert kpi_cards["profit_factor"]["format_type"] == "number"

    def test_integer_format(self):
        result = make_analytics_result()
        kpi_cards = build_kpi_cards(result)
        assert kpi_cards["total_trades"]["format_type"] == "integer"


# ============================================================================
# Interpretation Logic Tests
# ============================================================================

class TestEvaluateInterpretation:

    def test_below_first_threshold_returns_first_level(self):
        thresholds = [(5, "poor"), (10, "average"), (20, "good")]
        assert _evaluate_interpretation(3, thresholds, False) == "poor"

    def test_at_boundary_moves_to_next_level(self):
        thresholds = [(5, "poor"), (10, "average"), (20, "good")]
        assert _evaluate_interpretation(5, thresholds, False) == "average"

    def test_above_all_thresholds_returns_excellent(self):
        thresholds = [(5, "poor"), (10, "average"), (20, "good")]
        assert _evaluate_interpretation(25, thresholds, False) == "excellent"

    def test_inverted_above_all_returns_poor(self):
        thresholds = [(5, "excellent"), (15, "good"), (25, "average")]
        assert _evaluate_interpretation(30, thresholds, True) == "poor"

    def test_inverted_below_first_returns_excellent(self):
        thresholds = [(5, "excellent"), (15, "good"), (25, "average")]
        assert _evaluate_interpretation(3, thresholds, True) == "excellent"

    def test_none_value_returns_none(self):
        thresholds = [(5, "poor"), (10, "average")]
        assert _evaluate_interpretation(None, thresholds, False) is None

    def test_inf_value_returns_none(self):
        thresholds = [(5, "poor"), (10, "average")]
        assert _evaluate_interpretation(float("inf"), thresholds, False) is None

    def test_nan_value_returns_none(self):
        thresholds = [(5, "poor"), (10, "average")]
        assert _evaluate_interpretation(float("nan"), thresholds, False) is None


# ============================================================================
# Interpretation Threshold Tests (per metric)
# ============================================================================

class TestCagrInterpretation:

    def test_poor(self):
        result = make_analytics_result(portfolio_cagr=3.0)
        assert build_kpi_cards(result)["cagr"]["interpretation"] == "poor"

    def test_average(self):
        result = make_analytics_result(portfolio_cagr=10.0)
        assert build_kpi_cards(result)["cagr"]["interpretation"] == "average"

    def test_good(self):
        result = make_analytics_result(portfolio_cagr=15.0)
        assert build_kpi_cards(result)["cagr"]["interpretation"] == "good"

    def test_excellent(self):
        result = make_analytics_result(portfolio_cagr=25.0)
        assert build_kpi_cards(result)["cagr"]["interpretation"] == "excellent"


class TestProfitFactorInterpretation:

    def test_poor(self):
        result = make_analytics_result(trade_profit_factor=0.8)
        assert build_kpi_cards(result)["profit_factor"]["interpretation"] == "poor"

    def test_average(self):
        result = make_analytics_result(trade_profit_factor=1.2)
        assert build_kpi_cards(result)["profit_factor"]["interpretation"] == "average"

    def test_good(self):
        result = make_analytics_result(trade_profit_factor=1.7)
        assert build_kpi_cards(result)["profit_factor"]["interpretation"] == "good"

    def test_excellent(self):
        result = make_analytics_result(trade_profit_factor=2.5)
        assert build_kpi_cards(result)["profit_factor"]["interpretation"] == "excellent"


class TestSharpeInterpretation:

    def test_poor(self):
        result = make_analytics_result(risk_sharpe_ratio=0.3)
        assert build_kpi_cards(result)["sharpe_ratio"]["interpretation"] == "poor"

    def test_average(self):
        result = make_analytics_result(risk_sharpe_ratio=1.2)
        assert build_kpi_cards(result)["sharpe_ratio"]["interpretation"] == "average"

    def test_good(self):
        result = make_analytics_result(risk_sharpe_ratio=1.7)
        assert build_kpi_cards(result)["sharpe_ratio"]["interpretation"] == "good"

    def test_excellent(self):
        result = make_analytics_result(risk_sharpe_ratio=2.0)
        assert build_kpi_cards(result)["sharpe_ratio"]["interpretation"] == "excellent"


class TestSortinoInterpretation:

    def test_poor(self):
        result = make_analytics_result(risk_sortino_ratio=0.3)
        assert build_kpi_cards(result)["sortino_ratio"]["interpretation"] == "poor"

    def test_excellent(self):
        result = make_analytics_result(risk_sortino_ratio=3.5)
        assert build_kpi_cards(result)["sortino_ratio"]["interpretation"] == "excellent"


class TestMaxDrawdownInterpretation:

    def test_excellent(self):
        result = make_analytics_result(risk_maximum_drawdown=3.0)
        assert build_kpi_cards(result)["maximum_drawdown"]["interpretation"] == "excellent"

    def test_good(self):
        result = make_analytics_result(risk_maximum_drawdown=10.0)
        assert build_kpi_cards(result)["maximum_drawdown"]["interpretation"] == "good"

    def test_average(self):
        result = make_analytics_result(risk_maximum_drawdown=20.0)
        assert build_kpi_cards(result)["maximum_drawdown"]["interpretation"] == "average"

    def test_poor(self):
        result = make_analytics_result(risk_maximum_drawdown=40.0)
        assert build_kpi_cards(result)["maximum_drawdown"]["interpretation"] == "poor"


class TestAlphaInterpretation:

    def test_poor(self):
        result = make_analytics_result(benchmark_alpha=-15.0)
        assert build_kpi_cards(result)["alpha"]["interpretation"] == "poor"

    def test_average(self):
        result = make_analytics_result(benchmark_alpha=-2.0)
        assert build_kpi_cards(result)["alpha"]["interpretation"] == "average"

    def test_good(self):
        result = make_analytics_result(benchmark_alpha=5.0)
        assert build_kpi_cards(result)["alpha"]["interpretation"] == "good"

    def test_excellent(self):
        result = make_analytics_result(benchmark_alpha=15.0)
        assert build_kpi_cards(result)["alpha"]["interpretation"] == "excellent"


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:

    def test_inf_value_sanitized_to_none(self):
        result = make_analytics_result(risk_sharpe_ratio=float("inf"))
        kpi_cards = build_kpi_cards(result)
        assert kpi_cards["sharpe_ratio"]["value"] is None

    def test_nan_value_sanitized_to_none(self):
        result = make_analytics_result(risk_sharpe_ratio=float("nan"))
        kpi_cards = build_kpi_cards(result)
        assert kpi_cards["sharpe_ratio"]["value"] is None

    def test_inf_value_has_no_interpretation(self):
        result = make_analytics_result(risk_sharpe_ratio=float("inf"))
        kpi_cards = build_kpi_cards(result)
        assert "interpretation" not in kpi_cards["sharpe_ratio"]

    def test_zero_values_handled(self):
        result = make_analytics_result(
            portfolio_cagr=0.0,
            risk_sharpe_ratio=0.0,
            trade_profit_factor=0.0,
        )
        kpi_cards = build_kpi_cards(result)
        assert kpi_cards["cagr"]["interpretation"] == "poor"
        assert kpi_cards["sharpe_ratio"]["interpretation"] == "poor"
        assert kpi_cards["profit_factor"]["interpretation"] == "poor"

    def test_negative_values_handled(self):
        result = make_analytics_result(
            portfolio_cagr=-5.0,
            risk_sharpe_ratio=-0.5,
        )
        kpi_cards = build_kpi_cards(result)
        assert kpi_cards["cagr"]["interpretation"] == "poor"
        assert kpi_cards["sharpe_ratio"]["interpretation"] == "poor"
