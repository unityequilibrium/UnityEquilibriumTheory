"""Regression checks for canonical matter-space candidate equation modules."""

from __future__ import annotations

import importlib

import pytest


CASES = {
    "uet_matter_space_causal": (
        "CAUSAL_DISCRETE_GRADIENT_OPERATOR_MODE",
        "causal_space_discrete_energy",
        "causal_space_discrete_gradient_step",
    ),
    "uet_matter_space_finite_cone": (
        "FINITE_CONE_C_OPERATOR_MODE",
        "FiniteConeCConfig",
        "finite_cone_c_step",
        "finite_cone_c_contract",
    ),
    "uet_matter_space_characteristic": (
        "CHARACTERISTIC_CONE_OPERATOR_MODE",
        "CharacteristicConeStabilityError",
        "characteristic_cone_step",
        "characteristic_cone_contract",
    ),
    "uet_matter_space_split": (
        "MATTER_SPACE_CAUSAL_SPLIT_OPERATOR_MODE",
        "causal_split_energy",
        "causal_matter_space_split_step",
    ),
}


@pytest.mark.parametrize("module_name, public_names", CASES.items())
def test_candidate_root_module_forwards_to_canonical_family(
    module_name: str, public_names: tuple[str, ...]
) -> None:
    legacy = importlib.import_module(f"docs.core.{module_name}")
    canonical_name = f"docs.core.02_equations.matter_space.{module_name}"
    canonical = importlib.import_module(canonical_name)

    assert legacy.__canonical_module__ == canonical_name
    assert all(getattr(legacy, name) is getattr(canonical, name) for name in public_names)


def test_candidate_modules_are_classified_as_matter_space_equations() -> None:
    from docs.core.core_paths import canonical_path_for

    for module_name in CASES:
        assert canonical_path_for(f"docs/core/{module_name}.py") == (
            f"docs/core/02_equations/matter_space/{module_name}.py"
        )
