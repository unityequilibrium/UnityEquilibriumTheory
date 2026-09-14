from __future__ import annotations

import importlib

from docs.core import uet_o2_finite_density_eos as legacy_eos
from docs.core import standard_o2_finite_temperature_comparator as legacy_comparator


def test_o2_implementations_have_one_canonical_module() -> None:
    canonical_eos = importlib.import_module(
        "docs.core.02_equations.o2.uet_o2_finite_density_eos"
    )
    canonical_comparator = importlib.import_module(
        "docs.core.02_equations.o2.standard_o2_finite_temperature_comparator"
    )

    assert legacy_eos.__canonical_module__ == canonical_eos.__name__
    assert legacy_comparator.__canonical_module__ == canonical_comparator.__name__
    assert legacy_eos.O2FiniteDensityEOSConfig is canonical_eos.O2FiniteDensityEOSConfig
    assert (
        legacy_comparator.StandardO2ThermalNormalState
        is canonical_comparator.StandardO2ThermalNormalState
    )


def test_o2_canonical_package_exports_both_declared_roles() -> None:
    package = importlib.import_module("docs.core.02_equations.o2")

    assert "O2FiniteDensityEOSConfig" in package.__all__
    assert "StandardO2ThermalNormalState" in package.__all__
