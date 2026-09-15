from docs.core.core_paths import repo_root
import json
from pathlib import Path


ROOT = repo_root()
ARTIFACT = ROOT / "docs/core/artifacts/matter_space_causal_discretization_diagnostic.json"


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8-sig"))


def test_causal_diagnostic_keeps_original_gate_blocked():
    artifact = load_artifact()
    assert artifact["audit_status"] == "PASS"
    assert artifact["causal_gate_status"] == "FAIL"
    assert artifact["interpretation_status"] == "BLOCKED_NUMERICAL_SUPPORT"
    assert artifact["continuum_formula_status"] == "NOT_TESTED_BY_THIS_GATE"


def test_discrete_domain_speed_is_explicitly_larger_than_declared_speed():
    artifact = load_artifact()
    metrics = artifact["metrics"]
    assert metrics["numerical_domain_speed_upper_bound"] > metrics["declared_physical_speed"]
    assert metrics["numerical_to_declared_speed_ratio"] > 10.0
    assert metrics["leakage_gate_failed"] is True


def test_required_repair_does_not_allow_padding_or_clipping():
    artifact = load_artifact()
    text = artifact["required_repair"]
    assert "without cone padding or clipping" in text
