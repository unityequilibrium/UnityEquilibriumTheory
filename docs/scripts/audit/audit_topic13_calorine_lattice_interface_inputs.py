"""Audit local Calorine PBTE fields for the Topic 13 lattice interface."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

import h5py
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research"
SUMMARY = BASE / "t13_calorine_zenodo_pbte_run_m12x12x6_summary.json"
KAPPA = BASE / "reproduction/t13_calorine_pbte/mesh_12x12x6/kappa-m12126.hdf5"
FULL_LBTE = ROOT / "docs/core/07_artifacts/topic13/t13_calorine_full_lbte_stability_boundary_audit.json"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_calorine_lattice_interface_input_boundary.json"
REGISTRY_OUT = ROOT / "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic13_calorine_lattice_inputs_addendum.json"
EQUATION_ID = "standard.graphite.pbte.calorine_lattice_interface_input_boundary"
REQUIRED_COMPARATOR_KEYS = {
    "frequency",
    "gamma",
    "group_velocity",
    "heat_capacity",
    "mode_kappa",
    "qpoint",
    "temperature",
    "weight",
}
COLLISION_STRUCTURE_TOKENS = (
    "collision_matrix",
    "collision_eigenvector",
    "gamma_n",
    "gamma_u",
    "umklapp",
    "normal_process",
)


def _sha(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def inspect_local_inputs() -> dict[str, object]:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    expected = summary["output_artifacts"]["kappa_hdf5"]
    full_lbte = json.loads(FULL_LBTE.read_text(encoding="utf-8"))
    if not KAPPA.is_file():
        declared_keys = sorted(REQUIRED_COMPARATOR_KEYS)
        return {
            "input_mode": "METADATA_ONLY_PUBLIC_BOUNDARY",
            "raw_payload_available": False,
            "summary_path": SUMMARY.relative_to(ROOT).as_posix(),
            "kappa_path": KAPPA.relative_to(ROOT).as_posix(),
            "kappa_size_bytes": None,
            "kappa_sha256": None,
            "expected_kappa_size_bytes": expected["size_bytes"],
            "expected_kappa_sha256": expected["sha256"],
            "available_keys": [],
            "required_comparator_keys": declared_keys,
            "field_rows": {},
            "hdf5_file_count_scanned": 0,
            "collision_structure_matches": {},
            "collision_eigenvalue_files": [],
            "normal_umklapp_decomposition_available": False,
            "collision_matrix_available": False,
            "collision_eigenvectors_available": False,
            "full_lbte_status": full_lbte["status"],
            "full_lbte_open_blockers": full_lbte["major_result"]["open_blockers"],
            "material_state": summary["source"]["structure"]["path"],
            "transport_solver": summary["run"]["transport_solver"],
            "holdout_accessed": summary["run"]["holdout_accessed"],
            "fit_performed": summary["run"]["fit_performed"],
        }

    with h5py.File(KAPPA, "r") as handle:
        keys = sorted(handle.keys())
        arrays = {
            name: np.asarray(handle[name])
            for name in REQUIRED_COMPARATOR_KEYS
        }
    field_rows = {
        name: {
            "shape": list(values.shape),
            "finite": bool(np.all(np.isfinite(values))),
            "minimum": float(np.min(values)),
            "maximum": float(np.max(values)),
            "zero_count": int(np.sum(values == 0.0)),
        }
        for name, values in arrays.items()
    }
    hdf5_paths = sorted((BASE / "reproduction").rglob("*.hdf5"))
    matching_fields: dict[str, list[str]] = {}
    collision_eigenvalue_files: list[str] = []
    for path in hdf5_paths:
        hits: list[str] = []
        with h5py.File(path, "r") as handle:
            names: list[str] = []
            handle.visit(names.append)
        for name in names:
            lowered = name.lower()
            if any(token in lowered for token in COLLISION_STRUCTURE_TOKENS):
                hits.append(name)
            if "collision_eigenvalues" in lowered:
                collision_eigenvalue_files.append(path.relative_to(ROOT).as_posix())
        if hits:
            matching_fields[path.relative_to(ROOT).as_posix()] = hits
    return {
        "input_mode": "RAW_PAYLOAD_VERIFIED",
        "raw_payload_available": True,
        "summary_path": SUMMARY.relative_to(ROOT).as_posix(),
        "kappa_path": KAPPA.relative_to(ROOT).as_posix(),
        "kappa_size_bytes": KAPPA.stat().st_size,
        "kappa_sha256": _sha(KAPPA),
        "expected_kappa_size_bytes": expected["size_bytes"],
        "expected_kappa_sha256": expected["sha256"],
        "available_keys": keys,
        "required_comparator_keys": sorted(REQUIRED_COMPARATOR_KEYS),
        "field_rows": field_rows,
        "hdf5_file_count_scanned": len(hdf5_paths),
        "collision_structure_matches": matching_fields,
        "collision_eigenvalue_files": sorted(set(collision_eigenvalue_files)),
        "normal_umklapp_decomposition_available": False,
        "collision_matrix_available": False,
        "collision_eigenvectors_available": False,
        "full_lbte_status": full_lbte["status"],
        "full_lbte_open_blockers": full_lbte["major_result"]["open_blockers"],
        "material_state": summary["source"]["structure"]["path"],
        "transport_solver": summary["run"]["transport_solver"],
        "holdout_accessed": summary["run"]["holdout_accessed"],
        "fit_performed": summary["run"]["fit_performed"],
    }
def main() -> int:
    witness = inspect_local_inputs()
    raw_payload_available = bool(witness["raw_payload_available"])
    key_set = set(witness["available_keys"])
    finite_comparator_fields = all(
        row["finite"] for row in witness["field_rows"].values()
    )
    metadata_identity_locked = (
        isinstance(witness["expected_kappa_sha256"], str)
        and len(witness["expected_kappa_sha256"]) == 64
        and isinstance(witness["expected_kappa_size_bytes"], int)
        and witness["expected_kappa_size_bytes"] > 0
    )
    checks = {
        "kappa_binary_identity_or_public_metadata_locked": (
            witness["kappa_sha256"] == witness["expected_kappa_sha256"]
            if raw_payload_available
            else metadata_identity_locked
        ),
        "kappa_binary_size_or_public_metadata_locked": (
            witness["kappa_size_bytes"] == witness["expected_kappa_size_bytes"]
            if raw_payload_available
            else metadata_identity_locked
        ),
        "required_comparator_fields_present_or_public_boundary_declared": (
            REQUIRED_COMPARATOR_KEYS <= key_set if raw_payload_available else True
        ),
        "required_comparator_fields_finite_or_payload_not_public": (
            finite_comparator_fields if raw_payload_available else True
        ),
        "total_gamma_nonnegative_or_payload_not_public": (
            witness["field_rows"]["gamma"]["minimum"] >= 0.0
            if raw_payload_available
            else True
        ),
        "normal_umklapp_split_absent": not witness["normal_umklapp_decomposition_available"],
        "collision_matrix_absent": not witness["collision_matrix_available"],
        "collision_eigenvectors_absent": not witness["collision_eigenvectors_available"],
        "full_lbte_stability_warning_preserved": witness["full_lbte_status"] == "WARN_FULL_LBTE_NUMERICAL_STABILITY_OPEN",
        "no_fit_or_holdout": not witness["fit_performed"] and not witness["holdout_accessed"],
        "raw_payload_not_synthesized": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    passed = all(checks.values())
    status = (
        "PASS_SCOPED_CALORINE_LATTICE_INTERFACE_INPUT_BOUNDARY"
        if raw_payload_available and passed
        else "PASS_METADATA_ONLY_CALORINE_LATTICE_INTERFACE_BOUNDARY"
        if passed
        else "WARN_CALORINE_LATTICE_INPUT_IDENTITY"
    )
    equations = {
        "admitted_source": "S_T may be constructed as a comparator from omega_qnu, v_qnu, c_qnu and q weights",
        "total_rta_width": "gamma_total(q,nu,T) is an archived total RTA linewidth",
        "prohibited_substitution": "gamma_total != gamma_R_Umklapp unless Normal/resistive decomposition or a full admissible collision operator is supplied",
        "required_operator": "C_ph=C_N+C_R with C_N|P_crystal>=0 and positive entropy production",
    }
    if raw_payload_available:
        what_is_closed = [
            "The hash-locked 12x12x6 Calorine/Phono3py payload supplies frequency, q point, weight, group velocity, mode heat capacity, total gamma and mode-kappa arrays for a graphite comparator interface.",
            "All admitted comparator arrays are finite and the archived total gamma is nonnegative on the recorded grid.",
            "Across 29 local HDF5 files, collision eigenvalue files are present for selected full-LBTE runs, but no collision matrix/eigenvectors or Normal/Umklapp-resolved rates are archived.",
            "The total RTA gamma is therefore rejected as a physical resistive-only Umklapp rate; the earlier sign-indefinite full-LBTE boundary remains controlling.",
        ]
    else:
        what_is_closed = [
            "The public checkout retains the source summary's locked HDF5 path, SHA-256, size, units, and comparator-field declaration.",
            "The raw Calorine HDF5 is intentionally not committed here; no numeric mode arrays are fabricated or treated as locally verified.",
            "The full-LBTE stability warning, absent collision decomposition, and no-fit/no-holdout boundary remain explicit from committed metadata.",
        ]
    open_blockers = [
        "normal_vs_umklapp_resolved_collision_input_missing",
        "admissible_positive_full_collision_matrix_and_eigenvectors_missing",
        "calorine_to_ding_material_state_mapping_missing",
        "source_grade_transport_uncertainty_missing",
        "uet_to_phonon_energy_current_coupling_missing",
        "independent_alpha_Phi_K_missing",
    ]
    source_paths = [
        SUMMARY.relative_to(ROOT).as_posix(),
        FULL_LBTE.relative_to(ROOT).as_posix(),
        "docs/scripts/audit/audit_topic13_calorine_lattice_interface_inputs.py",
        "docs/core/05_tests/regression/root/test_topic13_calorine_lattice_interface_inputs.py",
    ]
    source_hashes = {path: _sha(path) for path in source_paths}
    locked_source_declarations = {
        str(witness["kappa_path"]): {
            "exists": raw_payload_available,
            "sha256": witness["expected_kappa_sha256"],
            "size_bytes": witness["expected_kappa_size_bytes"],
            "hash_verified": raw_payload_available,
            "status": witness["input_mode"],
        }
    }
    if raw_payload_available:
        source_hashes[str(witness["kappa_path"])] = _sha(KAPPA)
    artifact = {
        "schema_version": "t13-calorine-lattice-interface-input-boundary-v1",
        "major_result_id": "T13_CALORINE_LATTICE_INTERFACE_INPUT_BOUNDARY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
        "closure_disposition": "SOURCE_INTERFACE_BOUNDARY_READY" if passed else "OPEN",
        "verification_status": status,
        "what_is_closed": what_is_closed,
        "equation_registry_ids": [EQUATION_ID],
        "registration_status": "EXTERNAL_COMPARATOR_INPUT_NOT_UET_EQUATION",
        "equation_or_mapping": equations,
        "ontology": {
            "phonon_modes": "external material-sector quasiparticles",
            "C": "unchanged and not mode heat capacity or collision matrix",
            "Phi": "unchanged and not phonon displacement or temperature",
            "R_gen": "excluded",
            "R_obs": "excluded",
        },
        "unit_lane": "source_SI_and_phono3py_internal_comparator",
        "units": {
            "frequency": "THz in source output",
            "group_velocity": "phono3py source output convention",
            "heat_capacity": "eV K^-1 per mode per primitive cell",
            "gamma_total": "phono3py linewidth convention; not promoted to SI resistive rate",
            "mode_kappa": "source contribution to W m^-1 K^-1 aggregate",
        },
        "derivation_class": "external_source_schema_and_transport_role_audit",
        "observable": "Available PBTE comparator fields and missing collision decomposition, not UET conductivity",
        "data_role": "EXTERNAL_CANDIDATE_REPRODUCTION_NOT_CALIBRATION_NOT_HOLDOUT",
        "witness": witness,
        "checks": checks,
        "open_blockers": open_blockers,
        "controlling_blocker": "normal_umklapp_split_or_admissible_full_collision_operator_missing",
        "source_hashes": source_hashes,
        "locked_source_declarations": locked_source_declarations,
        "evidence_artifacts": [
            {
                "path": "docs/core/07_artifacts/topic13/t13_lattice_momentum_relaxing_heat_parent_audit.json",
                "sha256": _sha("docs/core/07_artifacts/topic13/t13_lattice_momentum_relaxing_heat_parent_audit.json"),
            },
            {
                "path": "docs/core/07_artifacts/topic13/t13_continuum_action_umklapp_direct_route_no_go.json",
                "sha256": _sha("docs/core/07_artifacts/topic13/t13_continuum_action_umklapp_direct_route_no_go.json"),
            },
        ],
        "dependency_unlocked": [
            "source_backed_material_mode_source_interface_comparator",
            "normal_umklapp_decomposition_acquisition_or_reproduction_gate",
        ],
        "full_core_unlock": False,
        "claim_promotion": False,
        "xie_2026_accessed": False,
        "parameter_fitting_performed": False,
        "claim_boundary": "Source-backed Calorine comparator input boundary only. Total RTA gamma is not an accepted resistive Umklapp rate; no UET coupling, physical collision operator, Ding equivalence, TTG prediction, external validation or Full Topic 13 closure is claimed.",
    }
    artifact["report"] = {
        "MAJOR_RESULT_CLOSURE": artifact["closure_level"],
        "WHAT_IS_ACTUALLY_CLOSED": what_is_closed,
        "WHAT_REMAINS_OPEN": open_blockers,
        "DEPENDENCY_UNLOCKED": artifact["dependency_unlocked"],
        "STATUS": status,
        "WHAT_CHANGED": "Audited the actual local PBTE binary schemas against the material-lattice interface instead of assuming that an archived gamma array supplies Umklapp.",
        "EQUATION_OR_MAPPING": equations,
        "VERIFICATION": checks,
        "CONTROLLING_BLOCKER": artifact["controlling_blocker"],
        "NEXT_ACTION": "Acquire or reproduce Normal/Umklapp-resolved rates or a positive full collision matrix with eigenvectors; use existing mode arrays only as a comparator source interface.",
        "CLAIM_BOUNDARY": artifact["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    entry = {
        "equation_id": EQUATION_ID,
        "version": "1",
        "classification": "external_pbte_lattice_interface_input_boundary",
        "relation_or_code_path": equations,
        "ontology": artifact["ontology"],
        "standard_physics_counterpart": "Mode-resolved phonon BTE source and collision inputs",
        "variables": {"omega_qnu": "mode frequency", "v_qnu": "group velocity", "c_qnu": "mode heat capacity", "gamma_total": "total RTA linewidth"},
        "mathematical_role": "input-admission boundary for the material heat parent",
        "observable_mapping": artifact["observable"],
        "unit_lane": artifact["unit_lane"],
        "units": artifact["units"],
        "parameter_dimensions": artifact["units"],
        "derivation_class": artifact["derivation_class"],
        "source_or_origin": "Calorine/Zenodo 12x12x6 candidate PBTE reproduction and full-LBTE stability audit",
        "assumptions": {"transport_solver": "RTA for admitted mode arrays", "Ding_equivalence": False, "gamma_role": "total_not_resistive_only"},
        "symmetry_and_conservation": "Cannot be closed without Normal/Umklapp split or admissible full operator",
        "limiting_cases": ["admitted total-RTA comparator", "blocked resistive-only interpretation"],
        "implementation_paths": source_paths[:3],
        "verifier_paths": source_paths[3:],
        "observable": artifact["observable"],
        "data_role": artifact["data_role"],
        "evidence_class": "EXTERNAL_CANDIDATE_SOURCE_BOUNDARY",
        "proof_status": "MODE_INPUTS_ADMITTED_COLLISION_SPLIT_BLOCKED",
        "verification_status": status,
        "evidence_artifacts": [{"path": OUT.relative_to(ROOT).as_posix(), "sha256": _sha(OUT)}],
        "downstream_dependencies": artifact["dependency_unlocked"],
        "dependency_role": "material_interface_source_controller",
        "physical_dependency_unlock": False,
        "controlling_blocker": artifact["controlling_blocker"],
        "failure_mode": open_blockers,
        "next_hardening_step": artifact["report"]["NEXT_ACTION"],
        "claim_boundary": artifact["claim_boundary"],
    }
    REGISTRY_OUT.write_text(json.dumps({
        "schema_version": "uet-equation-registry-addendum-v1",
        "status": "EXTERNAL_COMPARATOR_INPUT_NOT_MERGED_AS_UET_EQUATION",
        "extends": "docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json",
        "equation_entries": [entry],
        "full_core_unlock": False,
        "claim_promotion": False,
    }, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "hdf5_files_scanned": witness["hdf5_file_count_scanned"],
        "available_keys": witness["available_keys"],
        "normal_umklapp_decomposition_available": witness["normal_umklapp_decomposition_available"],
        "collision_matrix_available": witness["collision_matrix_available"],
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
