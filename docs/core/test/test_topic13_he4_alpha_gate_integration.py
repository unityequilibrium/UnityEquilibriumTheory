from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)


def test_core_track_accepts_local_alpha_si_beta_and_physical_transport() -> None:
    gate = json.loads(GATE.read_text(encoding="utf-8-sig"))
    core = gate["closure_tracks"]["o2_he4_core_ready"]
    requirements = core["requirements"]
    assert requirements["he4_property_uncertainty_bound"] == "PASS"
    assert requirements["independent_alpha_and_field_normalization"] == "PASS"
    assert requirements["non_circular_natural_bridge"] == "PASS"
    assert requirements["formal_eos_and_entropy_interface"] == "PASS"
    assert requirements["absolute_temperature_scale_uncertainty"] == "PASS"
    assert requirements["normalized_beta_and_SI_energy_scale"] == "PASS"
    assert requirements["dimensional_observable_map"] == "PASS"
    assert requirements["physical_transport_coefficient"] == "PASS"
    assert requirements["landauer_constraint_source_disposition"] == "PASS"
    assert requirements["state_interface_and_core_composition"] == "PASS"
    assert core["status"] == "CLOSED_FOR_CORE"
    assert gate["claim_promotion"] is False
