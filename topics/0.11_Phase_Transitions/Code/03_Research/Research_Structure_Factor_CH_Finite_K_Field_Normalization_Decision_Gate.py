"""Wave 52 decision gate for CH finite-k field normalization.

This verifier does not rerun simulations. It audits whether centered UET C can
be accepted as the source-equivalent concentration fluctuation used by the
Cahn-Hilliard finite-k structure-factor source lane.
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

WAVE51_ARTIFACT = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_field_coefficient_policy_gate.json"
WAVE51_MANIFEST = DATA_DIR / "structure_factor_ch_finite_k_field_coefficient_policy.json"
WAVE47_MANIFEST = DATA_DIR / "structure_factor_ch_finite_k_normalization_preflight.json"
FRAGMENT_MANIFEST = DATA_DIR / "structure_factor_tex_formula_fragments.json"

MANIFEST_PATH = DATA_DIR / "structure_factor_ch_finite_k_field_normalization_decision.json"
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_field_normalization_decision_gate.json"

LONGO_SOURCE_ID = "longo_2021_cahn_hilliard_structure_factor"
REQUIRED_FRAGMENT_LABELS = {
    "Eqn_Gen_OrdParam_Evo",
    "Eqn_Gen_Chem_Pot",
    "S(q,t) = \\int",
}


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


def collect_longo_fragments(fragment_manifest: dict[str, Any]) -> dict[str, Any]:
    for source in fragment_manifest.get("source_formula_fragments", []):
        if source.get("source_id") == LONGO_SOURCE_ID:
            fragments = source.get("fragments", [])
            labels = {fragment.get("formula_label") for fragment in fragments}
            tex_by_label = {fragment.get("formula_label"): fragment.get("tex") for fragment in fragments}
            return {
                "source_id": LONGO_SOURCE_ID,
                "policy_role": source.get("policy_role"),
                "source_url": source.get("source_url"),
                "accepted_for_estimator_policy_now": source.get("accepted_for_estimator_policy_now"),
                "labels": sorted(label for label in labels if label),
                "required_labels_present": sorted(REQUIRED_FRAGMENT_LABELS & labels),
                "required_labels_missing": sorted(REQUIRED_FRAGMENT_LABELS - labels),
                "tex_by_required_label": {
                    label: tex_by_label.get(label) for label in sorted(REQUIRED_FRAGMENT_LABELS & labels)
                },
            }
    return {
        "source_id": LONGO_SOURCE_ID,
        "required_labels_present": [],
        "required_labels_missing": sorted(REQUIRED_FRAGMENT_LABELS),
        "tex_by_required_label": {},
    }


def build_manifest(wave51: dict[str, Any], wave47: dict[str, Any], fragments: dict[str, Any]) -> dict[str, Any]:
    field_preflight = wave47.get("preflight_sections", {}).get("field_normalization", {})
    return {
        "schema_version": "1.0",
        "topic": TOPIC,
        "wave": "Wave 52 CH finite-k field-normalization decision gate",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "claim_class": "field_normalization_decision_preflight_only",
        "inputs": [
            {
                "path": relpath(WAVE51_ARTIFACT),
                "role": "Wave 51 field/coefficient policy gate",
                "status": wave51.get("status"),
                "blocker_label": wave51.get("blocker_label"),
                "sha256": hash_file(WAVE51_ARTIFACT),
                "exists": WAVE51_ARTIFACT.exists(),
            },
            {
                "path": relpath(WAVE51_MANIFEST),
                "role": "Wave 51 field/coefficient policy manifest",
                "sha256": hash_file(WAVE51_MANIFEST),
                "exists": WAVE51_MANIFEST.exists(),
            },
            {
                "path": relpath(WAVE47_MANIFEST),
                "role": "Wave 47 field-normalization preflight",
                "sha256": hash_file(WAVE47_MANIFEST),
                "exists": WAVE47_MANIFEST.exists(),
            },
            {
                "path": relpath(FRAGMENT_MANIFEST),
                "role": "Wave 43 TeX formula fragments",
                "sha256": hash_file(FRAGMENT_MANIFEST),
                "exists": FRAGMENT_MANIFEST.exists(),
            },
        ],
        "source_field_evidence": fragments,
        "uet_field_mapping_under_review": {
            "source_symbol": field_preflight.get("source_symbol", "delta c or normalized concentration fluctuation"),
            "uet_symbol": field_preflight.get("uet_symbol", "C_centered = C - mean(C)"),
            "proposed_mapping": field_preflight.get(
                "proposed_mapping",
                "Use centered dimensionless UET order parameter as a diagnostic concentration-fluctuation field.",
            ),
            "preflight_status": field_preflight.get("status"),
            "preflight_unit_status": field_preflight.get("unit_status"),
        },
        "decision_policy": {
            "diagnostic_field_use": {
                "status": "PASS",
                "reason": "Source formulas expose normalized concentration/order-parameter fluctuation language, and UET C can be centered to remove the conserved zero mode for finite-k S(q) diagnostics.",
            },
            "accepted_estimator_field_use": {
                "status": "BLOCKED",
                "reason": "The current package lacks a source-backed amplitude/variance normalization, ensemble-or-time averaging convention, and S(q) normalization mapping for exponent-bearing use.",
            },
            "claim_boundary": "Wave 52 decides field-normalization readiness only; no estimator replacement, exponent rerun, universality, material, RG, or Tier A claim is accepted.",
        },
    }


def build_artifact(manifest: dict[str, Any], wave51: dict[str, Any]) -> dict[str, Any]:
    wave51_gates = wave51.get("gates", {})
    wave51_chain_pass = (
        wave51.get("blocker_label") == "ch_finite_k_field_normalization_open_measurement_coefficient_policy_separated"
        and wave51_gates.get("diagnostic_measurement_lane_gate", {}).get("status") == "PASS"
        and wave51_gates.get("source_equivalent_field_normalization_gate", {}).get("status") == "BLOCKED"
    )
    fragments = manifest["source_field_evidence"]
    source_fragments_present = not fragments.get("required_labels_missing")

    gates = {
        "wave51_chain_gate": gate(
            "PASS" if wave51_chain_pass else "BLOCKED",
            "Wave 52 must start from Wave 51 with diagnostic lane pass and source-equivalent field normalization blocked.",
            wave51_status=wave51.get("status"),
            wave51_blocker_label=wave51.get("blocker_label"),
        ),
        "source_field_symbol_gate": gate(
            "PASS" if source_fragments_present else "BLOCKED",
            "Source fragments must expose normalized concentration/order-parameter fluctuation symbols relevant to S(q,t).",
            required_labels_present=fragments.get("required_labels_present"),
            required_labels_missing=fragments.get("required_labels_missing"),
            tex_by_required_label=fragments.get("tex_by_required_label"),
        ),
        "uet_centered_field_proxy_gate": gate(
            "PASS",
            "Centered UET C is acceptable as a diagnostic normalized fluctuation proxy after zero-mode removal.",
            relation="C_centered = C - mean(C)",
            unit_status="dimensionless_proxy",
        ),
        "amplitude_normalization_gate": gate(
            "BLOCKED",
            "No source-backed amplitude or variance normalization maps UET C to the source fluctuation scale.",
            missing=[
                "scale factor between UET C and source c_hat/delta c_hat",
                "variance normalization or S(q) amplitude convention",
                "material or nondimensional concentration basis beyond normalized proxy",
            ],
        ),
        "averaging_convention_gate": gate(
            "BLOCKED",
            "No accepted ensemble or time-averaging convention maps current snapshot fields to source S(q,t) use.",
            missing=[
                "single-snapshot versus ensemble S(q,t) policy",
                "time-averaging window for claim-bearing S(q)",
                "seed aggregation rule for accepted estimator rows",
            ],
        ),
        "source_equivalent_field_acceptance_gate": gate(
            "BLOCKED",
            "Accepted estimator replacement requires amplitude normalization and averaging convention gates to pass.",
            blocking_gates=[
                "amplitude_normalization_gate=BLOCKED",
                "averaging_convention_gate=BLOCKED",
            ],
        ),
        "diagnostic_measurement_lane_gate": gate(
            "PASS" if wave51_chain_pass and source_fragments_present else "BLOCKED",
            "Diagnostic finite-k S(q) inspection may continue with centered C as a proxy field.",
            allowed_claim="diagnostic finite-k structure-factor measurement only",
        ),
        "accepted_estimator_replacement_gate": gate(
            "BLOCKED",
            "Do not accept the CH finite-k estimator for exponent use until source-equivalent field normalization passes.",
            next_required_artifact="field amplitude/averaging normalization acceptance gate",
        ),
        "exponent_rerun_gate": gate(
            "BLOCKED",
            "Do not rerun exponent gates until accepted estimator replacement passes.",
        ),
        "next_path_gate": gate(
            "BLOCKED",
            "The next controller is amplitude/averaging normalization or explicit replacement observable policy.",
            next_controller="ch_finite_k_field_amplitude_and_averaging_normalization_open",
        ),
    }

    return {
        "schema_version": "1.0",
        "topic": TOPIC,
        "wave": "Wave 52 CH finite-k field-normalization decision gate",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Field_Normalization_Decision_Gate.py",
        "status": "WARN",
        "blocker_label": "ch_finite_k_field_amplitude_and_averaging_normalization_open",
        "claim_class": "field_normalization_decision_preflight_only",
        "claim_boundary": (
            "Wave 52 accepts centered UET C only as a diagnostic finite-k proxy field. "
            "It does not accept source-equivalent field normalization because amplitude/variance "
            "normalization and ensemble/time-averaging convention remain blocked."
        ),
        "inputs": manifest["inputs"],
        "source_field_evidence": manifest["source_field_evidence"],
        "uet_field_mapping_under_review": manifest["uet_field_mapping_under_review"],
        "decision_policy": manifest["decision_policy"],
        "gates": gates,
        "limitations": [
            "No simulation or exponent verifier is rerun by this decision gate.",
            "Centered UET C remains diagnostic-only for finite-k measurement.",
            "Amplitude/variance normalization and ensemble/time-averaging convention are not source-accepted.",
            "No estimator replacement, exponent, universality, material, RG, or Tier A claim may be upgraded.",
        ],
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
    }


def main() -> dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    wave51 = load_json(WAVE51_ARTIFACT)
    wave47 = load_json(WAVE47_MANIFEST)
    fragment_manifest = load_json(FRAGMENT_MANIFEST)
    fragments = collect_longo_fragments(fragment_manifest)
    manifest = build_manifest(wave51, wave47, fragments)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    artifact = build_artifact(manifest, wave51)
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
