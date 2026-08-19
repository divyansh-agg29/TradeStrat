"""
Tests for PositionSizingConfig.
"""

import pytest

from position_sizing import PositionSizingConfig


def test_config_accepts_type_and_parameters():
    """
    PositionSizingConfig should store a valid type and parameters.
    """

    config = PositionSizingConfig(
        sizing_type="fixed_percentage",
        sizing_parameters={"percent": 0.25},
    )

    assert config.sizing_type == "fixed_percentage"
    assert config.sizing_parameters == {"percent": 0.25}


def test_config_defaults_to_none():
    """
    Default PositionSizingConfig should have no sizing configured.
    """

    config = PositionSizingConfig()

    assert config.sizing_type is None
    assert config.sizing_parameters is None


def test_config_rejects_type_without_parameters():
    """
    Setting a type that requires parameters without providing them
    should fail clearly.
    """

    with pytest.raises(
        ValueError,
        match="sizing_parameters are required",
    ):
        PositionSizingConfig(sizing_type="fixed_percentage")


def test_config_rejects_type_with_empty_parameters():
    """
    Setting a type with an empty parameters dict should fail.
    """

    with pytest.raises(
        ValueError,
        match="sizing_parameters are required",
    ):
        PositionSizingConfig(
            sizing_type="fixed_amount",
            sizing_parameters={},
        )


def test_config_allows_all_in_without_parameters():
    """
    'all_in' sizing type should work without parameters.
    """

    config = PositionSizingConfig(sizing_type="all_in")

    assert config.sizing_type == "all_in"


def test_config_is_frozen():
    """
    PositionSizingConfig should be immutable (frozen dataclass).
    """

    config = PositionSizingConfig(
        sizing_type="fixed_percentage",
        sizing_parameters={"percent": 0.25},
    )

    with pytest.raises(AttributeError):
        config.sizing_type = "fixed_amount"


@pytest.mark.parametrize("sizing_type", [
    "fixed_percentage",
    "fixed_amount",
    "fixed_shares",
    "risk_based",
])
def test_config_rejects_all_param_requiring_types_without_params(sizing_type):
    """
    Every type that requires parameters should fail without them.
    """

    with pytest.raises(
        ValueError,
        match="sizing_parameters are required",
    ):
        PositionSizingConfig(sizing_type=sizing_type)
