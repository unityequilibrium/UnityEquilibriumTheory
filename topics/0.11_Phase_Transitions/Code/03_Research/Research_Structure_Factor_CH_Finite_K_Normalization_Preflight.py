"""
Wave 47 Cahn-Hilliard finite-k normalization preflight.

Wave 46 identified the Cahn-Hilliard finite-k structure-factor source lane as
the strongest estimator-policy candidate. This verifier writes a normalization
preflight manifest for that lane and keeps estimator acceptance blocked until
field normalization, source coefficient mapping, xi extraction, and finite-size
admissibility are explicit enough to support a rerun.
"""

from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any


def _bootstrap() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("UET docs root not found")


ROOT = _bootstrap()
TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
DATA_DIR = TOPIC_DIR / "Data" / "03_Research"
ARTIFACT_DIR = TOPIC_DIR / "Result" / "artifacts"

WAVE46_ARTIFACT_PATH = (
    ARTIFACT_DIR / "0_11_structure_factor_estimator_normalization_map_gate.json"
)
WAVE46_MANIFEST_PATH = DATA_DIR / "structure_factor_estimator_normalization_map.json"
PREFLIGHT_MANIFEST_PATH = DATA_DIR / "structure_factor_ch_finite_k_normalization_preflight.json"
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_ch_finite_k_normalization_preflight_gate.json"

CH_SOURCE_ID = "longo_2021_cahn_hilliard_structure_factor"
REQUIRED_PREFLIGHT_SECTIONS = {
    "field_normalization",
    "fourier_convention",
    "source_coefficient_mapping",
    "xi_extraction_rule",
    "finite_size_admissibility",
    "implementation_acceptance_requirements",
}


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_record(path: Path, role: str) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": relpath(path),
        "role": role,
        "exists": exists,
        "sha256": hash_file(path) if exists else None,
    }


def artifact_record(path: Path, role: str) -> dict[str, Any]:
    exists = path.exists()
    data = load_json(path) if exists else {}
    return {
        "path": relpath(path),
        "role": role,
        "exists": exists,
        "sha256": hash_file(path) if exists else None,
        "status": data.get("status"),
        "blocker_label": data.get("blocker_label"),
        "claim_class": data.get("claim_class"),
    }


def gate_status(artifact: dict[str, Any], gate_name: str) -> str | None:
    gate = artifact.get("gates", {}).get(gate_name, {})
    return gate.get("status") if isinstance(gate, dict) else None


def ch_mapping_row(mapping_manifest: dict[str, Any]) -> dict[str, Any]:
    for row in mapping_manifest.get("policy_mapping_rows", []):
        if row.get("source_id") == CH_SOURCE_ID:
            return row
    return {}


def write_preflight_manifest(mapping_manifest: dict[str, Any]) -> dict[str, Any]:
    ch_row = ch_mapping_row(mapping_manifest)
    manifest = {
        "schema_version": "1.0",
        "manifest_id": "structure_factor_ch_finite_k_normalization_preflight_wave47",
        "topic": "0.11_Phase_Transitions",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_mapping_manifest": relpath(WAVE46_MANIFEST_PATH),
        "source_mapping_manifest_sha256": hash_file(WAVE46_MANIFEST_PATH),
        "candidate_source_id": CH_SOURCE_ID,
        "candidate_policy_lane": ch_row.get("candidate_policy_lane"),
        "supporting_fragment_ids": ch_row.get("supporting_fragment_ids", []),
        "preflight_sections": {
            "field_normalization": {
                "status": "WARN",
                "source_symbol": "delta c or normalized concentration fluctuation in S(q,t)",
                "uet_symbol": "C_centered = C - mean(C)",
                "proposed_mapping": "Use centered dimensionless UET order parameter as a diagnostic concentration-fluctuation field.",
                "unit_status": "dimensionless_proxy_open",
                "missing_for_acceptance": [
                    "source normalization of c_A must be matched to UET C range and centering policy",
                    "ensemble or time-averaging convention must be declared before S(q,t) is accepted",
                ],
            },
            "fourier_convention": {
                "status": "PASS",
                "source_symbol": "q",
                "uet_symbol": "q = 2*pi*fftfreq(L, d=dx)",
                "proposed_mapping": "Use NumPy FFT lattice wave numbers with dx declared by the simulation grid.",
                "unit_status": "closed_in_lattice_units",
                "normalization_note": "This closes the q-grid convention only; it does not accept an estimator.",
            },
            "source_coefficient_mapping": {
                "status": "BLOCKED",
                "source_symbols": ["M", "kappa", "L", "K", "Delta T", "chi_q0_inverse"],
                "uet_symbols": [
                    "mobility or dt coefficient",
                    "kappa",
                    "interconversion/source-sink coefficient",
                    "linear damping coefficient",
                    "temperature offset",
                    "susceptibility or curvature proxy",
                ],
                "unit_status": "open",
                "missing_for_acceptance": [
                    "no source-locked mapping from Longo coefficients to UETParameters",
                    "no policy for setting interconversion terms when the current conserved-order lane omits them",
                    "no chi(q=0) curvature/susceptibility estimate accepted for conserved-mean fields",
                ],
            },
            "xi_extraction_rule": {
                "status": "BLOCKED",
                "source_basis": "finite-k S(q,t) and characteristic wave-number behavior",
                "rejected_proxy": "current all-nonzero-mode RMS inverse-k proxy remains diagnostic-only",
                "candidate_rule_status": "not_implemented",
                "unit_status": "open",
                "missing_for_acceptance": [
                    "derive a source-backed finite-k characteristic length from S(q,t)",
                    "avoid empirical calibration factors unless source-backed",
                    "demonstrate nondeclining absolute length across accepted grid sizes",
                ],
            },
            "finite_size_admissibility": {
                "status": "BLOCKED",
                "draft_rule": [
                    "exclude q=0 for conserved-mean fields",
                    "exclude domain-scale saturated modes before exponent fitting",
                    "require at least three accepted grid sizes",
                    "require stable or increasing absolute length under accepted estimator",
                ],
                "unit_status": "open_policy",
                "missing_for_acceptance": [
                    "numeric q-band bounds are not yet derived from source or accepted simulations",
                    "domain-scale threshold is not source-backed",
                    "accepted-grid rule has not been rerun with a source-backed estimator",
                ],
            },
            "implementation_acceptance_requirements": {
                "status": "BLOCKED",
                "required_before_rerun": [
                    "implement candidate estimator in a verifier separate from the rejected RMS inverse-k proxy",
                    "emit per-grid q-window diagnostics and exclusion reasons",
                    "compare against baseline and prior estimator lanes without promoting either by default",
                    "rerun finite-size/exponent gates only after normalization and admissibility gates pass",
                ],
            },
        },
        "preflight_decision": {
            "decision": "ch_finite_k_normalization_preflight_written_acceptance_blocked",
            "next_controller": "implement_source_backed_ch_finite_k_estimator_candidate",
            "reason": (
                "The q-grid convention can be stated in lattice units, but field normalization, "
                "source coefficient mapping, xi extraction, and finite-size admissibility remain "
                "open before estimator acceptance."
            ),
        },
        "claim_boundary": (
            "This manifest is a normalization preflight only. It accepts no estimator policy, "
            "finite-size exponent rerun, material validation, RG closure, universality shift, "
            "or Tier A upgrade."
        ),
    }
    PREFLIGHT_MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return manifest


def section_ready(section: dict[str, Any]) -> bool:
    return bool(section) and section.get("status") in {"PASS", "WARN", "BLOCKED"}


def run_ch_finite_k_normalization_preflight() -> dict[str, Any]:
    wave46 = load_json(WAVE46_ARTIFACT_PATH) if WAVE46_ARTIFACT_PATH.exists() else {}
    mapping_manifest = load_json(WAVE46_MANIFEST_PATH) if WAVE46_MANIFEST_PATH.exists() else {}
    ch_row = ch_mapping_row(mapping_manifest)
    preflight = write_preflight_manifest(mapping_manifest)
    sections = preflight.get("preflight_sections", {})
    ready_sections = {
        key: value for key, value in sections.items() if section_ready(value)
    }

    wave46_chain_gate = {
        "status": (
            "PASS"
            if wave46.get("blocker_label")
            == "source_formulas_mapped_normalization_and_admissibility_open"
            and gate_status(wave46, "policy_mapping_manifest_gate") == "PASS"
            else "BLOCKED"
        ),
        "required_condition": "Wave 47 must start from Wave 46 formula-to-policy mapping.",
        "wave46_status": wave46.get("status"),
        "wave46_blocker_label": wave46.get("blocker_label"),
        "policy_mapping_manifest_gate": gate_status(wave46, "policy_mapping_manifest_gate"),
    }
    ch_candidate_chain_gate = {
        "status": (
            "PASS"
            if ch_row.get("support_status") == "candidate_formula_family_present"
            and ch_row.get("candidate_policy_lane")
            == "cahn_hilliard_finite_k_structure_factor_candidate"
            else "BLOCKED"
        ),
        "required_condition": "The Cahn-Hilliard finite-k source lane must remain the mapped candidate family.",
        "candidate_source_id": ch_row.get("source_id"),
        "candidate_policy_lane": ch_row.get("candidate_policy_lane"),
        "support_status": ch_row.get("support_status"),
    }
    preflight_manifest_gate = {
        "status": (
            "PASS"
            if PREFLIGHT_MANIFEST_PATH.exists()
            and REQUIRED_PREFLIGHT_SECTIONS.issubset(set(sections))
            and len(ready_sections) == len(sections)
            else "BLOCKED"
        ),
        "required_condition": "A preflight manifest must declare all normalization and admissibility sections.",
        "preflight_manifest_path": relpath(PREFLIGHT_MANIFEST_PATH),
        "preflight_manifest_sha256": hash_file(PREFLIGHT_MANIFEST_PATH)
        if PREFLIGHT_MANIFEST_PATH.exists()
        else None,
        "section_count": len(sections),
        "ready_section_count": len(ready_sections),
        "missing_sections": sorted(REQUIRED_PREFLIGHT_SECTIONS - set(sections)),
    }
    field_normalization_gate = {
        "status": sections.get("field_normalization", {}).get("status", "BLOCKED"),
        "required_condition": "UET C must be mapped to the source concentration fluctuation before S(q,t) is accepted.",
        "details": sections.get("field_normalization", {}),
    }
    fourier_convention_gate = {
        "status": sections.get("fourier_convention", {}).get("status", "BLOCKED"),
        "required_condition": "q-grid convention must be explicit in lattice units.",
        "details": sections.get("fourier_convention", {}),
    }
    coefficient_mapping_gate = {
        "status": sections.get("source_coefficient_mapping", {}).get("status", "BLOCKED"),
        "required_condition": "Source coefficients must be mapped or intentionally excluded before using source dynamics formulas.",
        "details": sections.get("source_coefficient_mapping", {}),
    }
    xi_extraction_rule_gate = {
        "status": sections.get("xi_extraction_rule", {}).get("status", "BLOCKED"),
        "required_condition": "An accepted finite-k xi extraction rule must exist before exponent gates rerun.",
        "details": sections.get("xi_extraction_rule", {}),
    }
    finite_size_admissibility_gate = {
        "status": sections.get("finite_size_admissibility", {}).get("status", "BLOCKED"),
        "required_condition": "Finite-size q-window and domain-scale exclusion rules must be accepted before exponent fitting.",
        "details": sections.get("finite_size_admissibility", {}),
    }
    implementation_acceptance_gate = {
        "status": sections.get("implementation_acceptance_requirements", {}).get(
            "status", "BLOCKED"
        ),
        "required_condition": "A source-backed estimator implementation must pass before any scaling claim can rerun.",
        "details": sections.get("implementation_acceptance_requirements", {}),
    }
    estimator_acceptance_preflight_gate = {
        "status": (
            "PASS"
            if all(
                gate["status"] == "PASS"
                for gate in [
                    field_normalization_gate,
                    fourier_convention_gate,
                    coefficient_mapping_gate,
                    xi_extraction_rule_gate,
                    finite_size_admissibility_gate,
                    implementation_acceptance_gate,
                ]
            )
            else "BLOCKED"
        ),
        "required_condition": "All normalization, admissibility, and implementation gates must pass before accepting the estimator.",
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates from this preflight alone.",
        "next_controller": "implement_source_backed_ch_finite_k_estimator_candidate",
        "next_artifacts_required": [
            "candidate estimator verifier using declared q-grid and centered C field",
            "per-grid q-window exclusion report",
            "source coefficient inclusion/exclusion policy",
            "finite-size trend artifact using the candidate estimator",
        ],
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "A preflight table narrows the blocker but does not upgrade claims.",
        "claim_boundary": (
            "Wave 47 makes normalization/admissibility gaps explicit. It accepts no "
            "estimator, exponent, universality, material, RG, or Tier A claim."
        ),
    }

    if wave46_chain_gate["status"] != "PASS":
        blocker_label = "ch_finite_k_preflight_chain_missing_wave46_mapping"
    elif estimator_acceptance_preflight_gate["status"] == "BLOCKED":
        blocker_label = "ch_finite_k_normalization_preflight_written_estimator_implementation_open"
    else:
        blocker_label = "ch_finite_k_preflight_ready_for_scaling_rerun"

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 47 Cahn-Hilliard finite-k normalization preflight",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Normalization_Preflight.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "normalization_preflight_only",
        "inputs": [
            artifact_record(WAVE46_ARTIFACT_PATH, "Wave 46 normalization-map gate"),
            source_record(WAVE46_MANIFEST_PATH, "Wave 46 normalization-map manifest"),
            source_record(PREFLIGHT_MANIFEST_PATH, "Wave 47 CH finite-k preflight manifest"),
        ],
        "metrics": {
            "preflight_section_count": len(sections),
            "ready_section_count": len(ready_sections),
            "pass_section_count": sum(
                1 for section in sections.values() if section.get("status") == "PASS"
            ),
            "warn_section_count": sum(
                1 for section in sections.values() if section.get("status") == "WARN"
            ),
            "blocked_section_count": sum(
                1 for section in sections.values() if section.get("status") == "BLOCKED"
            ),
        },
        "gates": {
            "wave46_chain_gate": wave46_chain_gate,
            "ch_candidate_chain_gate": ch_candidate_chain_gate,
            "preflight_manifest_gate": preflight_manifest_gate,
            "field_normalization_gate": field_normalization_gate,
            "fourier_convention_gate": fourier_convention_gate,
            "coefficient_mapping_gate": coefficient_mapping_gate,
            "xi_extraction_rule_gate": xi_extraction_rule_gate,
            "finite_size_admissibility_gate": finite_size_admissibility_gate,
            "implementation_acceptance_gate": implementation_acceptance_gate,
            "estimator_acceptance_preflight_gate": estimator_acceptance_preflight_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "The q-grid convention is explicit in lattice units, but this alone does not accept an estimator.",
            "Centered UET C is still a proxy for the source concentration fluctuation.",
            "Source coefficients and chi(q=0) are not mapped to UETParameters.",
            "No source-backed finite-k xi extraction implementation has been rerun.",
            "No finite-size/exponent, universality, material, RG, or Tier A claim may be upgraded.",
        ],
        "claim_boundary": (
            "Wave 47 is a normalization and admissibility preflight only. It narrows the "
            "next controller to implementing a source-backed CH finite-k estimator candidate."
        ),
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_ch_finite_k_normalization_preflight()
    print(
        json.dumps(
            {
                "status": result["status"],
                "blocker_label": result["blocker_label"],
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
                "artifact": relpath(ARTIFACT_PATH),
                "manifest": relpath(PREFLIGHT_MANIFEST_PATH),
            },
            indent=2,
            sort_keys=True,
        )
    )
