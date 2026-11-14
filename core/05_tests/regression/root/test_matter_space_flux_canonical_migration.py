"""Regression checks for the canonical matter-space flux family migration."""

from __future__ import annotations

import importlib

import pytest


CASES = {
    "uet_matter_space_flux_telegraph": (
        "FLUX_TELEGRAPH_OPERATOR_MODE",
        "FluxTelegraphConfig",
        "flux_telegraph_step",
    ),
    "uet_matter_space_flux_phi": (
        "FLUX_PHI_COUPLED_OPERATOR_MODE",
        "FluxPhiCoupledConfig",
        "flux_phi_coupled_step",
    ),
}


@pytest.mark.parametrize("module_name, public_names", CASES.items())
def test_flux_root_module_forwards_to_canonical_family(
    module_name: str, public_names: tuple[str, ...]
) -> None:
    legacy = importlib.import_module(f"docs.core.{module_name}")
    canonical_name = f"docs.core.02_equations.matter_space.{module_name}"
    canonical = importlib.import_module(canonical_name)

    assert legacy.__canonical_module__ == canonical_name
    assert all(getattr(legacy, name) is getattr(canonical, name) for name in public_names)


def test_flux_family_paths_are_classified_as_equation_sources() -> None:
    from docs.core.core_paths import canonical_path_for

    for module_name in CASES:
        assert canonical_path_for(f"docs/core/{module_name}.py") == (
            f"docs/core/02_equations/matter_space/{module_name}.py"
        )
