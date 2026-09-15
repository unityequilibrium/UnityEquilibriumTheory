from __future__ import annotations
from docs.core.core_paths import repo_root

import json
from pathlib import Path


ROOT = repo_root()
REGISTER = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_topic13_source_lanes_are_reported_as_major_results_without_unlock() -> None:
    register = load(REGISTER)
    dependency = load(DEPENDENCY)
    expected = {
        "T13_GRAPHITE_ELASTIC_BULK_MODULUS_SOURCE",
        "T13_GRAPHITE_ISOTHERMAL_KT_SOURCE",
        "T13_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE",
        "T13_HUANG_2023_SUPPLEMENTARY_PAYLOAD_BOUNDARY",
        "T13_NIST_AXM5Q1_DENSITY_SOURCE_BOUNDARY",
        "T13_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR",
        "T13_NATURAL_GRAPHITE_NELSON_RILEY_ALPHA_V_COMPARATOR",
    }
    entries = {
        item["major_result_id"]: item
        for item in register["entries"]
        if item.get("major_result_id") in expected
    }
    assert set(entries) == expected
    assert all(item["closure_level"] == "CLOSED_FOR_LANE" for item in entries.values())
    assert all(item["dependency_unlocked"].endswith("unlock") or "unlock" in item["dependency_unlocked"] for item in entries.values())
    assert register["claim_promotion"] is False
    assert dependency["topic13_partial_evidence"]["full_core_unlock"] is False
    assert all(
        lane["full_core_unlock"] is False
        for lane in dependency["topic13_partial_evidence"]["source_lanes"].values()
    )
