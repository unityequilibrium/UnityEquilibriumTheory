"""
Wave 46 estimator-policy normalization-map gate.

Wave 45 restored repo-local arXiv source archives and refreshed TeX formula
fragments. This verifier does not accept a new estimator. It maps those source
formula fragments to candidate policy lanes and records the exact normalization
and finite-size admissibility gaps that still block exponent reruns.
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
ARTIFACT_DIR = TOPIC_DIR / "Result" / "artifacts"
DATA_DIR = TOPIC_DIR / "Data" / "03_Research"

ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_estimator_normalization_map_gate.json"
NORMALIZATION_MAP_PATH = DATA_DIR / "structure_factor_estimator_normalization_map.json"
FRAGMENT_MANIFEST_PATH = DATA_DIR / "structure_factor_tex_formula_fragments.json"
WAVE43_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_tex_formula_fragment_gate.json"
WAVE44_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_source_archive_policy_gate.json"

EXPECTED_SOURCE_IDS = {
    "blote_heringa_tsypin_1999_fixed_magnetization_ising",
    "deng_blote_2005_canonical_fss",
    "longo_2021_cahn_hilliard_structure_factor",
}

REQUIRED_MAPPING_FIELDS = {
    "source_id",
    "candidate_policy_lane",
    "support_status",
    "supporting_fragment_ids",
    "accepted_for_estimator_policy_now",
    "normalization_requirements",
    "missing_for_acceptance",
    "claim_boundary",
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


def fragment_ids(source_row: dict[str, Any]) -> list[str]:
    return sorted(str(fragment.get("fragment_id")) for fragment in source_row.get("fragments", []))


def formula_labels(source_row: dict[str, Any]) -> list[str]:
    return sorted(str(fragment.get("formula_label")) for fragment in source_row.get("fragments", []))


def build_mapping_rows(fragment_manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows_by_source = {
        str(row.get("source_id")): row
        for row in fragment_manifest.get("source_formula_fragments", [])
    }

    fixed = rows_by_source.get("blote_heringa_tsypin_1999_fixed_magnetization_ising", {})
    canonical = rows_by_source.get("deng_blote_2005_canonical_fss", {})
    ch = rows_by_source.get("longo_2021_cahn_hilliard_structure_factor", {})

    return [
        {
            "source_id": "blote_heringa_tsypin_1999_fixed_magnetization_ising",
            "candidate_policy_lane": "fixed_magnetization_effective_potential_boundary",
            "support_status": "boundary_evidence_only",
            "formula_labels": formula_labels(fixed),
            "supporting_fragment_ids": fragment_ids(fixed),
            "accepted_for_estimator_policy_now": False,
            "normalization_requirements": [
                "map M and effective-potential derivatives to the conserved UET order parameter C",
                "derive connected susceptibility or accepted replacement for conserved-mean fields",
                "define finite-size scaling units for N, L, and lattice spacing",
            ],
            "missing_for_acceptance": [
                "no accepted source-equivalent S(0) lane for the conserved-order snapshots",
                "no finite-k correlation-length estimator relation in this source lane",
                "no UET lattice normalization or admissibility rule",
            ],
            "claim_boundary": "Useful as fixed-magnetization/canonical boundary evidence; not an accepted UET estimator policy.",
        },
        {
            "source_id": "deng_blote_2005_canonical_fss",
            "candidate_policy_lane": "canonical_finite_size_susceptibility_boundary",
            "support_status": "boundary_evidence_only",
            "formula_labels": formula_labels(canonical),
            "supporting_fragment_ids": fragment_ids(canonical),
            "accepted_for_estimator_policy_now": False,
            "normalization_requirements": [
                "map canonical susceptibility scaling to the conserved UET lattice ensemble",
                "declare how rho, rho_c, d, y_t, y_rho, and L correspond to UET simulation variables",
                "define when canonical susceptibility can replace or calibrate finite-k structure factors",
            ],
            "missing_for_acceptance": [
                "canonical susceptibility equality is not yet a usable finite-k estimator",
                "finite-size correction terms are not mapped to the current L16/L20 diagnostics",
                "no accepted UET normalization table for density/order-parameter variables",
            ],
            "claim_boundary": "Useful for canonical finite-size policy constraints; not an accepted replacement estimator.",
        },
        {
            "source_id": "longo_2021_cahn_hilliard_structure_factor",
            "candidate_policy_lane": "cahn_hilliard_finite_k_structure_factor_candidate",
            "support_status": "candidate_formula_family_present",
            "formula_labels": formula_labels(ch),
            "supporting_fragment_ids": fragment_ids(ch),
            "accepted_for_estimator_policy_now": False,
            "normalization_requirements": [
                "map UET lattice C to the source normalized concentration fluctuation delta c",
                "define Fourier convention, q grid, k_min, and lattice spacing used by S(q,t)",
                "map source parameters M, kappa, L, K, Delta T, and chi(q=0) to UET normalized coefficients",
                "define admissible finite-k window and exclude domain-scale saturated modes",
                "specify how xi or characteristic length is extracted from S(q,t) without using an empirical calibration factor",
            ],
            "missing_for_acceptance": [
                "no accepted q-window/admissibility rule for finite-size scaling",
                "no source-backed conversion from S(q,t) fragments to the current RMS inverse-k proxy",
                "no nondeclining absolute-length trend demonstrated under the accepted estimator",
                "no rerun of finite-size/exponent gates using an accepted policy",
            ],
            "claim_boundary": "Strongest candidate lane after Wave 45, but still diagnostic until normalization and admissibility pass.",
        },
    ]


def mapping_row_ready(row: dict[str, Any]) -> bool:
    return all(row.get(field) not in (None, "", []) for field in REQUIRED_MAPPING_FIELDS)


def write_normalization_map(fragment_manifest: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    accepted_rows = [row for row in rows if row["accepted_for_estimator_policy_now"]]
    candidate_rows = [
        row for row in rows if row["support_status"] == "candidate_formula_family_present"
    ]
    manifest = {
        "schema_version": "1.0",
        "manifest_id": "structure_factor_estimator_normalization_map_wave46",
        "topic": "0.11_Phase_Transitions",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_fragment_manifest": relpath(FRAGMENT_MANIFEST_PATH),
        "source_fragment_manifest_sha256": hash_file(FRAGMENT_MANIFEST_PATH),
        "source_fragment_decision": fragment_manifest.get("formula_fragment_decision", {}),
        "mapping_decision": {
            "decision": "source_formulas_mapped_normalization_and_admissibility_open",
            "accepted_policy_count": len(accepted_rows),
            "candidate_formula_family_count": len(candidate_rows),
            "next_controller": "derive_uet_lattice_normalization_for_ch_finite_k_structure_factor",
            "reason": (
                "The restored source formulas identify a plausible Cahn-Hilliard finite-k "
                "structure-factor family, but no UET lattice normalization, q-window "
                "admissibility rule, or accepted estimator rerun exists yet."
            ),
        },
        "policy_mapping_rows": rows,
        "claim_boundary": (
            "This manifest maps extracted source formulas to candidate estimator-policy lanes. "
            "It accepts no estimator policy, UET normalization mapping, exponent result, RG "
            "closure, material validation, universality shift, or Tier A upgrade."
        ),
    }
    NORMALIZATION_MAP_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return manifest


def run_estimator_normalization_map_gate() -> dict[str, Any]:
    wave43 = load_json(WAVE43_ARTIFACT_PATH) if WAVE43_ARTIFACT_PATH.exists() else {}
    wave44 = load_json(WAVE44_ARTIFACT_PATH) if WAVE44_ARTIFACT_PATH.exists() else {}
    fragment_manifest = load_json(FRAGMENT_MANIFEST_PATH) if FRAGMENT_MANIFEST_PATH.exists() else {}
    rows = build_mapping_rows(fragment_manifest)
    normalization_map = write_normalization_map(fragment_manifest, rows)

    observed_source_ids = {
        str(row.get("source_id"))
        for row in fragment_manifest.get("source_formula_fragments", [])
        if row.get("source_id")
    }
    extracted_fragment_count = sum(
        int(row.get("extracted_fragment_count", 0))
        for row in fragment_manifest.get("source_formula_fragments", [])
    )
    ready_rows = [row for row in rows if mapping_row_ready(row)]
    accepted_rows = [row for row in rows if row["accepted_for_estimator_policy_now"]]
    ch_candidate_rows = [
        row
        for row in rows
        if row["candidate_policy_lane"] == "cahn_hilliard_finite_k_structure_factor_candidate"
        and row["support_status"] == "candidate_formula_family_present"
    ]

    wave43_chain_gate = {
        "status": (
            "PASS"
            if gate_status(wave43, "source_archive_availability_gate") == "PASS"
            and gate_status(wave43, "source_formula_fragment_gate") == "PASS"
            else "BLOCKED"
        ),
        "required_condition": "Wave 46 requires Wave 43 fresh formula extraction from repo archives.",
        "wave43_status": wave43.get("status"),
        "wave43_blocker_label": wave43.get("blocker_label"),
        "source_archive_availability_gate": gate_status(wave43, "source_archive_availability_gate"),
        "source_formula_fragment_gate": gate_status(wave43, "source_formula_fragment_gate"),
    }
    wave44_archive_gate = {
        "status": "PASS" if gate_status(wave44, "repo_archive_availability_gate") == "PASS" else "BLOCKED",
        "required_condition": "Repo source archives must remain available before source-formula mapping is reproducible.",
        "wave44_status": wave44.get("status"),
        "wave44_blocker_label": wave44.get("blocker_label"),
        "repo_archive_availability_gate": gate_status(wave44, "repo_archive_availability_gate"),
    }
    fragment_coverage_gate = {
        "status": (
            "PASS"
            if EXPECTED_SOURCE_IDS.issubset(observed_source_ids)
            and extracted_fragment_count >= 19
            else "BLOCKED"
        ),
        "required_condition": "All three source lanes and the expected 19 extracted fragments must be present.",
        "observed_source_ids": sorted(observed_source_ids),
        "missing_expected_source_ids": sorted(EXPECTED_SOURCE_IDS - observed_source_ids),
        "extracted_fragment_count": extracted_fragment_count,
    }
    policy_mapping_manifest_gate = {
        "status": (
            "PASS"
            if NORMALIZATION_MAP_PATH.exists()
            and len(ready_rows) == len(rows)
            and len(rows) == len(EXPECTED_SOURCE_IDS)
            else "BLOCKED"
        ),
        "required_condition": "A normalization-map manifest must map each source lane to a policy lane and explicit missing requirements.",
        "normalization_map_path": relpath(NORMALIZATION_MAP_PATH),
        "normalization_map_sha256": hash_file(NORMALIZATION_MAP_PATH)
        if NORMALIZATION_MAP_PATH.exists()
        else None,
        "mapping_row_count": len(rows),
        "ready_mapping_row_count": len(ready_rows),
    }
    finite_k_policy_candidate_gate = {
        "status": "WARN" if ch_candidate_rows else "BLOCKED",
        "required_condition": "The Cahn-Hilliard source lane may be treated as a candidate finite-k formula family, not an accepted estimator.",
        "candidate_rows": [row["source_id"] for row in ch_candidate_rows],
        "claim_boundary": "WARN is intentional: candidate source formulas exist, but acceptance gates remain blocked.",
    }
    conserved_susceptibility_policy_gate = {
        "status": "BLOCKED",
        "required_condition": "A conserved-order connected S(0) or canonical susceptibility policy must be accepted before source-family S(0) estimators can be used.",
        "reason": "Fixed-magnetization and canonical fragments constrain the policy boundary but do not resolve the conserved-mean S(0) blocker.",
    }
    uet_normalization_mapping_gate = {
        "status": "BLOCKED",
        "required_condition": "An accepted source formula must be mapped into UET lattice units before scaling or exponent gates may rerun.",
        "missing_mapping": [
            "C or delta-c field normalization",
            "Fourier/S(q,t) convention and q grid",
            "M, kappa, L, K, Delta T, and chi(q=0) coefficient mapping",
            "xi or characteristic-length extraction rule",
        ],
    }
    finite_size_admissibility_gate = {
        "status": "BLOCKED",
        "required_condition": "Accepted finite-k estimator use requires a finite-size q-window and domain-scale saturation guard.",
        "missing_rules": [
            "allowed q modes or q band for L16/L20 and future grids",
            "domain-scale saturation exclusion rule",
            "nondeclining absolute-length trend requirement under the accepted estimator",
        ],
    }
    estimator_policy_acceptance_gate = {
        "status": "PASS" if accepted_rows else "BLOCKED",
        "required_condition": "At least one source-mapped policy row must set accepted_for_estimator_policy_now true before exponent gates rerun.",
        "accepted_policy_count": len(accepted_rows),
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent, universality, material, or Tier A gates until normalization and admissibility pass.",
        "next_controller": "derive_uet_lattice_normalization_for_ch_finite_k_structure_factor",
        "next_artifacts_required": [
            "UET lattice normalization table for C, delta-c, q, S(q,t), and xi",
            "finite-k admissibility rule with domain-scale guard",
            "accepted estimator implementation that is not the rejected RMS inverse-k proxy",
            "finite-size/exponent rerun using the accepted estimator",
        ],
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Formula mapping narrows the blocker but does not upgrade the topic claim.",
        "claim_boundary": (
            "Wave 46 maps source formulas to policy lanes and identifies the CH finite-k "
            "candidate as the next plausible path; it accepts no estimator or Tier A claim."
        ),
    }

    if wave43_chain_gate["status"] != "PASS" or wave44_archive_gate["status"] != "PASS":
        blocker_label = "normalization_map_chain_missing_source_formula_or_archive_gate"
    elif estimator_policy_acceptance_gate["status"] == "BLOCKED":
        blocker_label = "source_formulas_mapped_normalization_and_admissibility_open"
    else:
        blocker_label = "estimator_policy_mapping_ready_for_scaling_rerun"

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 46 estimator policy normalization-map gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Estimator_Normalization_Map_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "estimator_policy_normalization_mapping_triage_only",
        "inputs": [
            artifact_record(WAVE43_ARTIFACT_PATH, "Wave 43 TeX formula-fragment gate"),
            artifact_record(WAVE44_ARTIFACT_PATH, "Wave 44 source-archive policy gate"),
            source_record(FRAGMENT_MANIFEST_PATH, "Wave 43 formula-fragment manifest"),
            source_record(NORMALIZATION_MAP_PATH, "Wave 46 normalization-map manifest"),
        ],
        "metrics": {
            "source_lane_count": len(observed_source_ids),
            "extracted_fragment_count": extracted_fragment_count,
            "mapping_row_count": len(rows),
            "accepted_policy_count": len(accepted_rows),
            "candidate_formula_family_count": len(ch_candidate_rows),
            "next_candidate_lane": "cahn_hilliard_finite_k_structure_factor_candidate",
        },
        "gates": {
            "wave43_chain_gate": wave43_chain_gate,
            "wave44_archive_gate": wave44_archive_gate,
            "fragment_coverage_gate": fragment_coverage_gate,
            "policy_mapping_manifest_gate": policy_mapping_manifest_gate,
            "finite_k_policy_candidate_gate": finite_k_policy_candidate_gate,
            "conserved_susceptibility_policy_gate": conserved_susceptibility_policy_gate,
            "uet_normalization_mapping_gate": uet_normalization_mapping_gate,
            "finite_size_admissibility_gate": finite_size_admissibility_gate,
            "estimator_policy_acceptance_gate": estimator_policy_acceptance_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "The restored TeX fragments are mapped to policy lanes, but no estimator is accepted.",
            "The Cahn-Hilliard S(q,t) lane is the strongest candidate path, but it lacks UET lattice normalization and q-window admissibility.",
            "Fixed-magnetization and canonical susceptibility fragments constrain policy boundaries but do not resolve the conserved-mean S(0) blocker.",
            "No finite-size/exponent, material, RG, universality, or Tier A claim may be upgraded from this mapping gate.",
        ],
        "claim_boundary": (
            "Wave 46 narrows the next controller to UET lattice normalization plus finite-k "
            "admissibility for the Cahn-Hilliard structure-factor candidate. It does not "
            "accept estimator replacement or rerun scaling claims."
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
    result = run_estimator_normalization_map_gate()
    print(
        json.dumps(
            {
                "status": result["status"],
                "blocker_label": result["blocker_label"],
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
                "artifact": relpath(ARTIFACT_PATH),
                "manifest": relpath(NORMALIZATION_MAP_PATH),
            },
            indent=2,
            sort_keys=True,
        )
    )
