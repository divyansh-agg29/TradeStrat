"""
Tests for PositionSizingManager.
"""

import pytest

from position_sizing import (
    PositionSizingConfig,
    PositionSizingManager,
)


def test_manager_defaults_to_all_in():
    """
    Manager without config should default to all-in behavior.
    """

    manager = PositionSizingManager()

    shares = manager.calculate_shares_to_buy(
        portfolio_value=100000,
        cash=100000,
        current_price=50,
    )

    assert shares == 2000


def test_manager_defaults_to_all_in_with_none_type():
    """
    Manager with config but None sizing_type should default to all-in.
    """

    config = PositionSizingConfig(sizing_type=None)
    manager = PositionSizingManager(config)

    shares = manager.calculate_shares_to_buy(
        portfolio_value=100000,
        cash=100000,
        current_price=50,
    )

    assert shares == 2000


def test_manager_resolves_fixed_percentage():
    """
    Manager should resolve and apply fixed percentage sizing.
    """

    config = PositionSizingConfig(
        sizing_type="fixed_percentage",
        sizing_parameters={"percent": 0.25},
    )
    manager = PositionSizingManager(config)

    shares = manager.calculate_shares_to_buy(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 250


def test_manager_resolves_fixed_amount():
    """
    Manager should resolve and apply fixed amount sizing.
    """

    config = PositionSizingConfig(
        sizing_type="fixed_amount",
        sizing_parameters={"amount": 10000},
    )
    manager = PositionSizingManager(config)

    shares = manager.calculate_shares_to_buy(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 100


def test_manager_resolves_fixed_shares():
    """
    Manager should resolve and apply fixed shares sizing.
    """

    config = PositionSizingConfig(
        sizing_type="fixed_shares",
        sizing_parameters={"shares": 200},
    )
    manager = PositionSizingManager(config)

    shares = manager.calculate_shares_to_buy(
        portfolio_value=100000,
        cash=100000,
        current_price=50,
    )

    assert shares == 200


def test_manager_resolves_risk_based():
    """
    Manager should resolve and apply risk-based sizing.
    """

    config = PositionSizingConfig(
        sizing_type="risk_based",
        sizing_parameters={"risk_percent": 0.02},
    )
    manager = PositionSizingManager(config)

    shares = manager.calculate_shares_to_buy(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
        stop_loss_price=95,
    )

    assert shares == 400


def test_manager_resolves_all_in():
    """
    Manager should resolve and apply all-in sizing explicitly.
    """

    config = PositionSizingConfig(sizing_type="all_in")
    manager = PositionSizingManager(config)

    shares = manager.calculate_shares_to_buy(
        portfolio_value=100000,
        cash=100000,
        current_price=50,
    )

    assert shares == 2000


def test_manager_rejects_unknown_type():
    """
    An unknown sizing_type should raise a ValueError.
    """

    with pytest.raises(
        ValueError,
        match="Unknown sizing_type",
    ):
        PositionSizingManager(
            PositionSizingConfig(
                sizing_type="unknown_rule",
                sizing_parameters={"x": 1},
            )
        )


def test_manager_passes_stop_loss_to_risk_based():
    """
    Manager should forward stop_loss_price to the underlying rule.
    Risk-based sizing depends on it; result should change with it.
    """

    config = PositionSizingConfig(
        sizing_type="risk_based",
        sizing_parameters={"risk_percent": 0.02},
    )
    manager = PositionSizingManager(config)

    shares_tight = manager.calculate_shares_to_buy(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
        stop_loss_price=99,
    )

    shares_wide = manager.calculate_shares_to_buy(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
        stop_loss_price=50,
    )

    assert shares_tight > shares_wide


def test_manager_resolves_kelly_criterion():
    """
    Manager should resolve and apply Kelly Criterion sizing.
    Kelly % = 0.6 - (0.4 / 2.0) = 0.4, half-Kelly = 0.2.
    Allocation = $100k * 0.2 = $20k. Shares = $20k / $100 = 200.
    """

    config = PositionSizingConfig(
        sizing_type="kelly_criterion",
        sizing_parameters={
            "win_rate": 0.6,
            "win_loss_ratio": 2.0,
            "kelly_fraction": 0.5,
        },
    )
    manager = PositionSizingManager(config)

    shares = manager.calculate_shares_to_buy(
        portfolio_value=100000,
        cash=100000,
        current_price=100,
    )

    assert shares == 200
