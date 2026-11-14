"""Wave 51 policy gate for CH finite-k field/coefficient boundaries.

This verifier does not rerun simulations. It separates the measurement-only
finite-k diagnostic lane from source-dynamics claims so the remaining blocker
is explicit before any estimator acceptance or exponent rerun.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _bootstrap() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("UET repository root not found")


ROOT = _bootstrap()
TOPIC = "0.11_Phase_Transitions"
TOPIC_DIR = ROOT / "docs" / "topics" / TOPIC
DATA_DIR = TOPIC_DIR / "Data" / "03_Research"
RESULT_DIR = TOPIC_DIR / "Result"
ARTIFACT_DIR = RESULT_DIR / "artifacts"

WAVE50_ARTIFACT = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_extended_grid_coverage_probe.json"
WAVE49_MANIFEST = DATA_DIR / "structure_factor_ch_finite_k_acceptance_policy.json"
WAVE47_MANIFEST = DATA_DIR / "structure_factor_ch_finite_k_normalization_preflight.json"

MANIFEST_PATH = DATA_DIR / "structure_factor_ch_finite_k_field_coefficient_policy.json"
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_field_coefficient_policy_gate.json"


def relpath(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def hash_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def gate(status: str, required_condition: str, **details: Any) -> dict[str, Any]:
    return {"status": status, "required_condition": required_condition, **details}


POLICY = {
    "field_policy": {
        "measurement_centering": {
            "status": "PASS",
            "relation": "C_centered = C - mean(C)",
            "role": "remove the conserved zero mode before finite-k S(q) measurement",
            "unit_closure": "normalized_proxy",
            "claim_boundary": "allowed only as a diagnostic field-preparation step",
        },
        "source_equivalent_normalization": {
            "status": "BLOCKED",
            "missing": [
                "amplitude normalization between UET C and source concentration fluctuation",
                "material concentration units or nondimensionalization map",
                "source-backed rule for using centered C as exponent-bearing critical fluctuation",
            ],
            "claim_boundary": "not accepted as source-equivalent concentration fluctuation for exponent use",
        },
    },
    "coefficient_policy": {
        "measurement_only_exclusion": {
            "status": "PASS",
            "rule": "finite-k q_peak measurement reads S(q) from existing fields and does not use source dynamics coefficients",
            "claim_boundary": "may support diagnostic row filtering only, not source-dynamics or material claims",
        },
        "source_dynamics_mapping": {
            "status": "BLOCKED",
            "missing": [
                "mobility M mapping",
                "kappa/interface-energy normalization mapping",
                "free-energy curvature or susceptibility mapping",
                "temperature-offset mapping",
                "interconversion/source coefficient mapping",
            ],
            "claim_boundary": "required before source CH dynamics, material, or mechanism-equivalence claims",
        },
    },
    "acceptance_policy": {
        "diagnostic_measurement_lane_allowed": True,
        "accepted_estimator_replacement_allowed": False,
        "exponent_rerun_allowed": False,
        "claim_boundary": "Wave 51 narrows policy only; it does not accept the estimator or rerun scaling.",
    },
}


def build_manifest(wave50: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "topic": TOPIC,
        "wave": "Wave 51 CH finite-k field/coefficient policy gate",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "claim_class": "field_coefficient_policy_preflight_only",
        "policy": POLICY,
        "inputs": [
            {
                "path": relpath(WAVE50_ARTIFACT),
                "role": "Wave 50 accepted-row coverage probe",
                "status": wave50.get("status"),
                "blocker_label": wave50.get("blocker_label"),
                "sha256": hash_file(WAVE50_ARTIFACT),
                "exists": WAVE50_ARTIFACT.exists(),
            },
            {
                "path": relpath(WAVE49_MANIFEST),
                "role": "Wave 49 strict row/coefficient policy",
                "sha256": hash_file(WAVE49_MANIFEST),
                "exists": WAVE49_MANIFEST.exists(),
            },
            {
                "path": relpath(WAVE47_MANIFEST),
                "role": "Wave 47 field/q/coefficient normalization preflight",
                "sha256": hash_file(WAVE47_MANIFEST),
                "exists": WAVE47_MANIFEST.exists(),
            },
        ],
        "claim_boundary": (
            "Wave 51 separates a measurement-only finite-k diagnostic lane from source-dynamics "
            "coefficient claims. It does not accept centered C as source-equivalent or allow exponent reruns."
        ),
    }


def build_artifact(manifest: dict[str, Any], wave50: dict[str, Any]) -> dict[str, Any]:
    wave50_gates = wave50.get("gates", {})
    accepted_coverage = wave50_gates.get("accepted_multi_grid_coverage_gate", {})
    wave50_chain_pass = (
        wave50.get("blocker_label") == "ch_finite_k_extended_grid_coverage_repaired_normalization_and_coefficients_open"
        and accepted_coverage.get("status") == "PASS"
    )

    gates = {
        "wave50_chain_gate": gate(
            "PASS" if wave50_chain_pass else "BLOCKED",
            "Wave 51 must start from the Wave 50 coverage probe with accepted multi-grid coverage passing.",
            wave50_status=wave50.get("status"),
            wave50_blocker_label=wave50.get("blocker_label"),
            accepted_grid_counts=accepted_coverage.get("accepted_grid_counts"),
        ),
        "measurement_field_centering_gate": gate(
            "PASS",
            "Finite-k S(q) measurement may remove the conserved zero mode by centering C.",
            policy=POLICY["field_policy"]["measurement_centering"],
        ),
        "source_equivalent_field_normalization_gate": gate(
            "BLOCKED",
            "Centered UET C still lacks source-equivalent concentration-fluctuation normalization.",
            policy=POLICY["field_policy"]["source_equivalent_normalization"],
        ),
        "measurement_only_coefficient_exclusion_gate": gate(
            "PASS",
            "Measurement-only finite-k q_peak extraction does not require source dynamics coefficients.",
            policy=POLICY["coefficient_policy"]["measurement_only_exclusion"],
        ),
        "source_dynamics_coefficient_mapping_gate": gate(
            "BLOCKED",
            "Source CH dynamics coefficients remain unmapped and cannot support source-dynamics or material claims.",
            policy=POLICY["coefficient_policy"]["source_dynamics_mapping"],
        ),
        "diagnostic_measurement_lane_gate": gate(
            "PASS" if wave50_chain_pass else "BLOCKED",
            "A diagnostic finite-k measurement lane is allowed after Wave 50 coverage, with claim boundaries.",
            allowed_claim="diagnostic row filtering and measurement-only S(q) inspection",
        ),
        "accepted_estimator_replacement_gate": gate(
            "BLOCKED",
            "Estimator replacement requires source-equivalent field normalization plus accepted source-claim policy.",
            blocking_gates=[
                "source_equivalent_field_normalization_gate=BLOCKED",
                "source_dynamics_coefficient_mapping_gate=BLOCKED for source-dynamics claims",
            ],
        ),
        "exponent_rerun_gate": gate(
            "BLOCKED",
            "Do not rerun or interpret finite-size/exponent gates until estimator replacement is accepted.",
            next_required_artifact="field-normalization derivation or replacement estimator policy",
        ),
        "next_path_gate": gate(
            "BLOCKED",
            "The next controller is field normalization for centered C; source coefficients are excluded only from the measurement lane.",
            next_controller="ch_finite_k_field_normalization_open_measurement_coefficient_policy_separated",
        ),
    }

    return {
        "schema_version": "1.0",
        "topic": TOPIC,
        "wave": "Wave 51 CH finite-k field/coefficient policy gate",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Field_Coefficient_Policy_Gate.py",
        "status": "WARN",
        "blocker_label": "ch_finite_k_field_normalization_open_measurement_coefficient_policy_separated",
        "claim_class": "field_coefficient_policy_preflight_only",
        "claim_boundary": (
            "Wave 51 allows the CH finite-k q_peak path only as a diagnostic measurement lane. "
            "Source coefficients are not required for that measurement lane, but source-equivalent "
            "field normalization remains blocked before estimator replacement, exponent, universality, "
            "material, RG, or Tier A claims."
        ),
        "inputs": manifest["inputs"],
        "policy": POLICY,
        "gates": gates,
        "limitations": [
            "No simulation or exponent verifier is rerun by this policy gate.",
            "Centered UET C is still a normalized proxy and not source-equivalent concentration fluctuation.",
            "Source dynamics coefficients remain unmapped for dynamics/material claims.",
            "The Wave 50 coverage repair remains a diagnostic measurement lane, not an accepted estimator replacement.",
            "No exponent, universality, material, RG, or Tier A claim may be upgraded.",
        ],
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
    }


def main() -> dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    wave50 = load_json(WAVE50_ARTIFACT)
    manifest = build_manifest(wave50)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    artifact = build_artifact(manifest, wave50)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = main()
    print(
        json.dumps(
            {
                "status": result["status"],
                "blocker_label": result["blocker_label"],
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
            },
            indent=2,
            sort_keys=True,
        )
    )
