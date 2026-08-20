"""
Tests for the position sizing registry.
"""

from position_sizing import (
    POSITION_SIZING_REGISTRY,
    AllInPositionSizing,
    FixedPercentagePositionSizing,
    FixedAmountPositionSizing,
    FixedSharesPositionSizing,
    RiskBasedPositionSizing,
    KellyCriterionPositionSizing,
)


def test_registry_contains_expected_types():
    """
    POSITION_SIZING_REGISTRY should contain all implemented types.
    """

    assert "all_in" in POSITION_SIZING_REGISTRY
    assert "fixed_percentage" in POSITION_SIZING_REGISTRY
    assert "fixed_amount" in POSITION_SIZING_REGISTRY
    assert "fixed_shares" in POSITION_SIZING_REGISTRY
    assert "risk_based" in POSITION_SIZING_REGISTRY
    assert "kelly_criterion" in POSITION_SIZING_REGISTRY


def test_registry_maps_to_correct_classes():
    """
    Each registry key should map to the correct class.
    """

    assert POSITION_SIZING_REGISTRY["all_in"] is AllInPositionSizing
    assert POSITION_SIZING_REGISTRY["fixed_percentage"] is FixedPercentagePositionSizing
    assert POSITION_SIZING_REGISTRY["fixed_amount"] is FixedAmountPositionSizing
    assert POSITION_SIZING_REGISTRY["fixed_shares"] is FixedSharesPositionSizing
    assert POSITION_SIZING_REGISTRY["risk_based"] is RiskBasedPositionSizing
    assert POSITION_SIZING_REGISTRY["kelly_criterion"] is KellyCriterionPositionSizing


def test_registry_has_exactly_six_entries():
    """
    Registry should have exactly 6 entries (no unexpected extras).
    """

    assert len(POSITION_SIZING_REGISTRY) == 6
