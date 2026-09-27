"""Focused checks for the hypothetical charge-map circularity boundary."""

import hashlib
import importlib.util
from pathlib import Path

import numpy as np


SOURCE = Path(__file__).with_name("Research_T13_He4_Conditional_Charge_Map_Circularity.py")
SPEC = importlib.util.spec_from_file_location("he4_conditional_charge_map", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
AUDIT = MODULE.audit()


def test_conditional_density_root_is_not_a_physical_admission():
    assert AUDIT["verification_status"] == "PASS_SCOPED_DENSITY_CIRCULARITY_BOUNDARY"
    assert all(AUDIT["checks"].values())
    root = AUDIT["conditional_internal_root"]
    assert root["branch"] == "condensed"
    assert not root["physical_HeII_match_admitted"]
    assert np.isclose(root["total_charge_natural"], AUDIT["inputs"]["derived_natural_charge_target"])
    assert AUDIT["full_core_unlock"] is False
    assert AUDIT["dependency_unlocked"] == []


def test_reusing_density_in_e0_makes_the_match_an_identity():
    target = AUDIT["inputs"]["derived_natural_charge_target"]
    assert np.isclose(target, 1.0 / AUDIT["inputs"]["temperature_natural"])
    for witness in AUDIT["synthetic_density_rescalings"]:
        assert np.isclose(witness["implied_natural_charge_target"], target)
        assert np.isclose(witness["reconstructed_density_m3"], witness["input_density_m3"])


def test_evidence_hashes_match_current_inputs():
    for entry in AUDIT["evidence_artifacts"]:
        path = MODULE.ROOT / entry["path"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
