from __future__ import annotations

import json
from pathlib import Path

from docs.core.he4_normal_viscosity_kubo import physical_transport_record
from docs.core.topic13_closure_record_contract import validate_physical_transport_record


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "docs/core/artifacts/t13_he4_normal_viscosity_kubo_audit.json"


def test_physical_viscosity_record_passes_fail_closed_contract() -> None:
    record = physical_transport_record()
    validation = validate_physical_transport_record(record)
    assert validation["status"] == "PASS_PHYSICAL_TRANSPORT_RECORD"
    assert all(validation["checks"].values())
    assert record["value"] > record["uncertainty"] > 0.0
    assert record["unit_lane"] == "SI"
    assert record["holdout_policy"]["xie_2026_accessed"] is False


def test_physical_viscosity_audit_closes_only_the_shear_transport_lane() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8-sig"))
    assert audit["status"] == "PASS_HE4_PHYSICAL_SHEAR_KUBO_TRANSPORT"
    assert all(audit["checks"].values())
    assert audit["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
    assert audit["major_result"]["open_blockers"] == []
    assert "not a bulk Fourier heat conductivity" in audit["claim_boundary"]
