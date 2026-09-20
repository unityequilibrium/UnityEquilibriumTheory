from __future__ import annotations

import importlib

from docs.core import he4_normal_viscosity_kubo as legacy_viscosity
from docs.core import he4_o2_response_calibration as legacy_calibration
from docs.core import he4_o2_si_beta_mapping as legacy_beta
from docs.core import he4_svp_reference as legacy_reference


def test_he4_thermal_root_modules_forward_to_one_canonical_package() -> None:
    canonical_names = {
        "viscosity": "docs.core.03_lanes.thermal.he4_normal_viscosity_kubo",
        "calibration": "docs.core.03_lanes.thermal.he4_o2_response_calibration",
        "beta": "docs.core.03_lanes.thermal.he4_o2_si_beta_mapping",
        "reference": "docs.core.03_lanes.thermal.he4_svp_reference",
    }
    canonical = {key: importlib.import_module(name) for key, name in canonical_names.items()}

    assert legacy_viscosity.__canonical_module__ == canonical_names["viscosity"]
    assert legacy_calibration.__canonical_module__ == canonical_names["calibration"]
    assert legacy_beta.__canonical_module__ == canonical_names["beta"]
    assert legacy_reference.__canonical_module__ == canonical_names["reference"]
    assert legacy_viscosity.physical_transport_record is canonical["viscosity"].physical_transport_record
    assert legacy_calibration.calibration_record is canonical["calibration"].calibration_record
    assert legacy_beta.si_beta_record is canonical["beta"].si_beta_record
    assert legacy_reference.calibration_grid is canonical["reference"].calibration_grid


def test_he4_thermal_package_exports_the_declared_lane_surface() -> None:
    package = importlib.import_module("docs.core.03_lanes.thermal")

    assert "physical_transport_record" in package.__all__
    assert "calibration_record" in package.__all__
    assert "si_beta_record" in package.__all__
    assert "calibration_grid" in package.__all__
