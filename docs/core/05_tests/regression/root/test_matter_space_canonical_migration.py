"""Regression checks for the matter-space canonical package migration."""

from __future__ import annotations

import importlib

import pytest


CASES = {
    "uet_trace": ("TraceKernelConfig", "UETStepResult", "compute_spacetime_trace"),
    "uet_spatial": ("integral_1d", "laplacian_1d", "validate_field_1d"),
    "uet_matter_space": ("MatterSpaceConfig", "MatterSpaceState", "matter_space_step"),
    "uet_master_equation": ("UETMasterEquation", "UETParameters", "dynamics_step_complete"),
}


@pytest.mark.parametrize("module_name, public_names", CASES.items())
def test_root_module_forwards_to_one_canonical_implementation(
    module_name: str, public_names: tuple[str, ...]
) -> None:
    legacy = importlib.import_module(f"docs.core.{module_name}")
    canonical_name = f"docs.core.02_equations.matter_space.{module_name}"
    canonical = importlib.import_module(canonical_name)

    assert legacy.__canonical_module__ == canonical_name
    for name in public_names:
        assert getattr(legacy, name) is getattr(canonical, name)


def test_matter_space_family_package_is_importable_without_root_aliases() -> None:
    package = importlib.import_module("docs.core.02_equations.matter_space")
    assert package.__all__ == []
