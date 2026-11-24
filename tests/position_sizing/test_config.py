"""
Tests for PositionSizingConfig.
"""

import pytest

from models import PositionSizingConfig


class TestPositionSizingConfig:

    def test_accepts_type_and_parameters(self):
        """
        PositionSizingConfig should store a valid type and parameters.
        """

        config = PositionSizingConfig(
            sizing_type="fixed_percentage",
            sizing_parameters={"percent": 0.25},
        )

        assert config.sizing_type == "fixed_percentage"
        assert config.sizing_parameters == {"percent": 0.25}

    def test_defaults_to_none(self):
        """
        Default PositionSizingConfig should have no sizing configured.
        """

        config = PositionSizingConfig()

        assert config.sizing_type is None
        assert config.sizing_parameters is None

    def test_rejects_type_without_parameters(self):
        """
        Setting a type that requires parameters without providing them
        should fail clearly.
        """

        with pytest.raises(
            ValueError,
            match="sizing_parameters are required",
        ):
            PositionSizingConfig(sizing_type="fixed_percentage")

    def test_accepts_type_with_empty_parameters(self):
        """
        Setting a type with an empty parameters dict should be accepted.
        An empty dict means 'provided but empty', distinct from None.
        """

        config = PositionSizingConfig(
            sizing_type="fixed_amount",
            sizing_parameters={},
        )

        assert config.sizing_parameters == {}

    def test_allows_all_in_without_parameters(self):
        """
        'all_in' sizing type should work without parameters.
        """

        config = PositionSizingConfig(sizing_type="all_in")

        assert config.sizing_type == "all_in"

    def test_is_frozen(self):
        """
        PositionSizingConfig should be immutable (frozen dataclass).
        """

        config = PositionSizingConfig(
            sizing_type="fixed_percentage",
            sizing_parameters={"percent": 0.25},
        )

        with pytest.raises(AttributeError, match="cannot assign to field"):
            config.sizing_type = "fixed_amount"

    @pytest.mark.parametrize("sizing_type", [
        "fixed_percentage",
        "fixed_amount",
        "fixed_shares",
        "risk_based",
        "kelly_criterion",
    ])
    def test_rejects_all_param_requiring_types_without_params(self, sizing_type):
        """
        Every type that requires parameters should fail without them.
        """

        with pytest.raises(
            ValueError,
            match="sizing_parameters are required",
        ):
            PositionSizingConfig(sizing_type=sizing_type)
