"""
Tests for the shared backtest models.
"""

from analytics import AnalyticsResult
from models import (
    BacktestRequest,
    BacktestResult,
    RiskConfig,
    StrategyConfig,
)
from portfolio import SimulationResult


class TestStrategyConfig:

    def test_creation(self):
        """
        StrategyConfig should store the supplied values.
        """

        config = StrategyConfig(
            type="sma_crossover",
            parameters={
                "short_period": 20,
                "long_period": 50,
            },
        )

        assert config.type == "sma_crossover"

        assert config.parameters == {
            "short_period": 20,
            "long_period": 50,
        }

    def test_default_parameters(self):
        """
        StrategyConfig should default to an empty parameter dictionary.
        """

        config = StrategyConfig(
            type="buy_and_hold",
        )

        assert config.parameters == {}


class TestRiskConfig:

    def test_creation(self):
        """
        RiskConfig should store the supplied values.
        """

        risk_config = RiskConfig(
            stop_loss_type="fixed_percentage",
            stop_loss_parameters={"percent": 0.03},
        )

        assert risk_config.stop_loss_type == "fixed_percentage"
        assert risk_config.stop_loss_parameters == {"percent": 0.03}

    def test_defaults(self):
        """
        RiskConfig should default to disabled state.
        """

        risk_config = RiskConfig()

        assert risk_config.stop_loss_type is None
        assert risk_config.stop_loss_parameters is None


class TestBacktestRequest:

    def test_creation(self):
        """
        BacktestRequest should store all supplied values.
        """

        strategy = StrategyConfig(
            type="sma_crossover",
            parameters={
                "short_period": 20,
                "long_period": 50,
            },
        )

        risk_config = RiskConfig(
            stop_loss_type="fixed_percentage",
            stop_loss_parameters={"percent": 0.03},
        )

        request = BacktestRequest(
            ticker="RELIANCE.NS",
            start_date="2022-01-01",
            end_date="2023-01-01",
            initial_capital=100000,
            risk_free_rate=0.06,
            strategy=strategy,
            risk=risk_config,
        )

        assert request.ticker == "RELIANCE.NS"

        assert request.start_date == "2022-01-01"

        assert request.end_date == "2023-01-01"

        assert request.initial_capital == 100000

        assert request.risk_free_rate == 0.06

        assert request.strategy is strategy
        assert request.risk is risk_config

    def test_defaults(self):
        """
        BacktestRequest should use the documented default values.
        """

        strategy = StrategyConfig(
            type="buy_and_hold",
        )

        request = BacktestRequest(
            ticker="RELIANCE.NS",
            start_date="2022-01-01",
            end_date="2023-01-01",
            strategy=strategy,
        )

        assert request.initial_capital == 100000.0

        assert request.risk_free_rate == 0.0


class TestBacktestResult:

    def test_creation(self):
        """
        BacktestResult should store the supplied result objects.
        """

        import pandas as pd

        simulation_result = SimulationResult(
            portfolio_history=pd.DataFrame(),
            trade_history=pd.DataFrame(),
            summary={},
        )

        analytics_result = AnalyticsResult()

        result = BacktestResult(
            simulation_result=simulation_result,
            analytics_result=analytics_result,
        )

        assert result.simulation_result is simulation_result

        assert result.analytics_result is analytics_result
