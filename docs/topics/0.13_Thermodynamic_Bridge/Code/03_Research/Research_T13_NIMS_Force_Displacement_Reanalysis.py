"""Reproduce a bounded harmonic C_v candidate from the public NIMS force sets.

This reanalysis does not digitize the NIMS figure, infer alpha_Phi_K, or claim
Ding/TTG equivalence. Imaginary modes are retained in diagnostics and are not
made real; the zero cutoff only excludes them from the reported C_v sum.
"""

from __future__ import annotations

import hashlib
import json
import lzma
import re
import tempfile
import zipfile
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import phonopy


ROOT = Path(__file__).resolve().parents[5]
SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_REL = SCRIPT_PATH.relative_to(ROOT).as_posix()
SOURCE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "nims_mdr_mp990448_graphite_phonon_dataset.zip"
)
OUTPUT_REL = "docs/core/07_artifacts/topic13/t13_nims_mp990448_force_displacement_reanalysis.json"
SOURCE_URL = "https://mdr.nims.go.jp/datasets/5383108b-180d-4eb0-a34f-b28ff9e430d7"
PHONOPY_DOCS_URL = "https://phonopy.github.io/phonopy/phonopy-module.html"
BIPM_REPORT_URL = (
    "https://www.bipm.org/documents/20126/27085544/"
    "bipm%20publication-ID-1661.pdf/"
    "ecac54bb-1086-ac6c-46a3-6f986951a033?download=true&t=1598613830576&version=1.4"
)
EXPECTED_ARCHIVE_SHA256 = "eea6ca7569c9442754ce5492ddb2f545186f97ad8b82b209d95f1a80b0158767"
EXPECTED_MEMBER_SHA256 = "92bfbcaa4cec51cbdf85c0d5d167bb8a57718e4d5074ac100378250257007a70"
PRIOR_AUDIT_REL = "docs/core/07_artifacts/topic13/t13_nims_mp990448_phonon_source_boundary_audit.json"
TEMPERATURES_K = (200.0, 295.15, 300.0)
Q_MESHES = ((8, 8, 4), (10, 10, 5), (12, 12, 6))
AVOGADRO = 6.02214076e23


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def assess_scoped_result(
    checks: dict[str, bool], scope_controls: dict[str, bool]
) -> tuple[bool, str]:
    expected_scope_controls = {
        "accepted_for_full_topic13": False,
        "claim_promotion": False,
    }
    passed = all(checks.values()) and scope_controls == expected_scope_controls
    if passed:
        return True, "WARN_SCOPED_NIMS_HARMONIC_CV_REANALYSIS_UNSTABLE_MODES_AND_UNCERTAINTY_OPEN"
    return False, "FAIL_NIMS_FORCE_DISPLACEMENT_REANALYSIS"


def run_solver(yaml_path: Path, solver_label: str, fc_calculator: str | None) -> dict[str, Any]:
    if fc_calculator is None:
        phonon = phonopy.load(str(yaml_path))
    else:
        phonon = phonopy.load(str(yaml_path), fc_calculator=fc_calculator)

    dataset = phonon.dataset
    records = dataset["first_atoms"]
    force_shapes = [list(np.asarray(item["forces"]).shape) for item in records]
    displacement_records = [
        {
            "record_index_zero_based": index,
            "displaced_atom_index_zero_based": int(item["number"]),
            "displacement_angstrom": [float(value) for value in item["displacement"]],
            "force_array_shape": list(np.asarray(item["forces"]).shape),
            "normalized_float64_force_array_sha256": sha256_bytes(
                np.asarray(item["forces"], dtype="<f8").tobytes(order="C")
            ),
        }
        for index, item in enumerate(records)
    ]
    force_constants = np.asarray(phonon.force_constants, dtype=float)
    primitive_volume_a3 = abs(float(np.linalg.det(phonon.primitive.cell)))
    primitive_molar_mass_kg_mol = float(np.sum(phonon.primitive.masses)) * 1e-3
    molar_volume_m3_mol = primitive_volume_a3 * 1e-30 * AVOGADRO
    mesh_results: list[dict[str, Any]] = []

    for mesh_shape in Q_MESHES:
        mesh = phonon.run_mesh(
            mesh_shape,
            is_gamma_center=True,
            is_mesh_symmetry=True,
            with_eigenvectors=False,
        )
        thermal = phonon.run_thermal_properties(
            temperatures=TEMPERATURES_K,
            cutoff_frequency=0.0,
            pretend_real=False,
        )
        cv_molar = np.asarray(thermal.heat_capacity, dtype=float)
        cv_mass = cv_molar / primitive_molar_mass_kg_mol
        c_src = cv_molar / molar_volume_m3_mol
        min_flat = int(np.argmin(mesh.frequencies))
        min_q_index, min_band_index = np.unravel_index(min_flat, mesh.frequencies.shape)
        negative_weight = int(np.sum(mesh.weights[:, None] * (mesh.frequencies < 0.0)))
        total_mode_weight = int(np.sum(mesh.weights) * mesh.frequencies.shape[1])

        mesh_results.append(
            {
                "mesh": list(mesh_shape),
                "gamma_centered": True,
                "qpoint_weight_sum": int(np.sum(mesh.weights)),
                "frequency_min_THz": float(mesh.frequencies[min_q_index, min_band_index]),
                "frequency_min_qpoint": [float(value) for value in mesh.qpoints[min_q_index]],
                "frequency_min_band_index": int(min_band_index),
                "negative_mode_weight": negative_weight,
                "total_mode_weight": total_mode_weight,
                "negative_mode_weight_fraction": negative_weight / total_mode_weight,
                "rows": [
                    {
                        "temperature_K": float(temperature),
                        "Cv_J_mol_primitive_cell_K": float(cv_molar[index]),
                        "Cv_J_kg_K": float(cv_mass[index]),
                        "C_src_J_m3_K": float(c_src[index]),
                    }
                    for index, temperature in enumerate(TEMPERATURES_K)
                ],
            }
        )

    for previous, current in zip(mesh_results, mesh_results[1:]):
        previous_rows = {row["temperature_K"]: row for row in previous["rows"]}
        current["relative_change_from_previous_mesh"] = {
            str(row["temperature_K"]): abs(
                row["C_src_J_m3_K"] - previous_rows[row["temperature_K"]]["C_src_J_m3_K"]
            )
            / abs(previous_rows[row["temperature_K"]]["C_src_J_m3_K"])
            for row in current["rows"]
        }

    return {
        "solver": solver_label,
        "fc_calculator": fc_calculator or "Phonopy default",
        "force_constants_shape": list(force_constants.shape),
        "force_constants_finite": bool(np.isfinite(force_constants).all()),
        "displacement_record_count": len(records),
        "displacement_records": displacement_records,
        "force_shapes": force_shapes,
        "primitive_volume_A3": primitive_volume_a3,
        "primitive_molar_mass_kg_mol": primitive_molar_mass_kg_mol,
        "molar_volume_m3_mol": molar_volume_m3_mol,
        "cutoff_frequency_THz": 0.0,
        "pretend_real": False,
        "imaginary_frequency_treatment": "negative frequencies below zero cutoff are omitted from C_v; not replaced by real frequencies",
        "mesh_results": mesh_results,
    }


def build_artifact(archive_path: Path | None = None) -> dict[str, Any]:
    source_path = archive_path or (ROOT / SOURCE_REL)
    archive_payload = source_path.read_bytes() if source_path.is_file() else b""
    archive_hash = sha256_bytes(archive_payload) if archive_payload else None
    member_payload = b""
    if archive_payload:
        with zipfile.ZipFile(source_path) as archive:
            member_payload = archive.read("phonopy_params.yaml.xz")

    member_hash = sha256_bytes(member_payload) if member_payload else None
    yaml_bytes = lzma.decompress(member_payload) if member_payload else b""
    yaml_text = yaml_bytes.decode("utf-8") if yaml_bytes else ""
    version_match = re.search(r"^  version:\s*([^\s]+)", yaml_text, re.MULTILINE)
    source_phonopy_version = version_match.group(1) if version_match else None

    solver_results: list[dict[str, Any]] = []
    if yaml_bytes:
        with tempfile.TemporaryDirectory(prefix="uet_t13_nims_") as temp_dir:
            yaml_path = Path(temp_dir) / "phonopy_params.yaml"
            yaml_path.write_bytes(yaml_bytes)
            solver_results = [
                run_solver(yaml_path, "symfc_default", None),
                run_solver(yaml_path, "traditional", "traditional"),
            ]

    expected_archive = archive_hash == EXPECTED_ARCHIVE_SHA256
    expected_member = member_hash == EXPECTED_MEMBER_SHA256
    complete_forces = bool(solver_results) and all(
        result["displacement_record_count"] == 2
        and result["force_shapes"] == [[144, 3], [144, 3]]
        and result["force_constants_finite"]
        for result in solver_results
    )
    finite_rows = bool(solver_results) and all(
        np.isfinite(row[field]) and row[field] > 0.0
        for result in solver_results
        for mesh_result in result["mesh_results"]
        for row in mesh_result["rows"]
        for field in ("Cv_J_mol_primitive_cell_K", "Cv_J_kg_K", "C_src_J_m3_K")
    )
    imaginary_modes = any(
        mesh_result["frequency_min_THz"] < 0.0
        for result in solver_results
        for mesh_result in result["mesh_results"]
    )

    finest_rows = {
        result["solver"]: {
            row["temperature_K"]: row
            for row in result["mesh_results"][-1]["rows"]
        }
        for result in solver_results
    }
    cv_295_default = finest_rows.get("symfc_default", {}).get(295.15, {}).get("Cv_J_kg_K")
    cv_295_traditional = finest_rows.get("traditional", {}).get(295.15, {}).get("Cv_J_kg_K")
    bipm_cp_295 = 710.6
    bipm_comparison = {
        "source_locator": BIPM_REPORT_URL,
        "temperature_K": 295.15,
        "reference_quantity": "c_p of a BIPM ultra-pure graphite sample",
        "reference_value_J_kg_K": bipm_cp_295,
        "combined_standard_uncertainty_J_kg_K": 0.7,
        "source_temperature_range_C": [19.0, 25.0],
        "equation": "c_p,g(T)=710.6+3.0*(T_C-22) J kg^-1 K^-1",
        "nims_symfc_default_Cv_J_kg_K": cv_295_default,
        "nims_traditional_Cv_J_kg_K": cv_295_traditional,
        "relative_difference_symfc_vs_BIPM_cp": (
            cv_295_default / bipm_cp_295 - 1.0 if cv_295_default is not None else None
        ),
        "relative_difference_traditional_vs_BIPM_cp": (
            cv_295_traditional / bipm_cp_295 - 1.0 if cv_295_traditional is not None else None
        ),
        "comparability": "NOT_EQUIVALENT: c_v versus c_p and different material states; numerical proximity is not validation or calibration",
    }

    checks = {
        "source_archive_hash_matches": expected_archive,
        "phonopy_member_hash_matches": expected_member,
        "source_deposits_complete_displacement_force_records": complete_forces,
        "force_constants_reconstructed_with_two_methods": len(solver_results) == 2 and complete_forces,
        "candidate_cv_rows_are_finite_positive": finite_rows,
        "imaginary_modes_are_detected_and_reported": imaginary_modes,
        "imaginary_modes_are_not_pretended_real": all(
            result["pretend_real"] is False for result in solver_results
        ),
        "no_figure_digitization_or_target_fit": True,
        "no_alpha_phi_k_emitted": True,
        "xie_2026_not_accessed": True,
    }
    scope_controls = {
        "accepted_for_full_topic13": False,
        "claim_promotion": False,
    }
    passed, status = assess_scoped_result(checks, scope_controls)
    prior_audit_path = ROOT / PRIOR_AUDIT_REL
    prior_audit_hash = sha256_path(prior_audit_path) if prior_audit_path.is_file() else None

    return {
        "schema_version": "t13-nims-force-displacement-reanalysis-v1",
        "artifact": "t13_nims_mp990448_force_displacement_reanalysis",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_NIMS_MP990448_FORCE_DISPLACEMENT_REANALYSIS",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "The hash-locked NIMS archive contains two displacement-force records with 144 force vectors each.",
                "Phonopy reconstructs finite harmonic force constants from the deposited force-displacement data using both default and traditional calculators.",
                "A reproducible, explicitly conditional harmonic C_v/C_src candidate is emitted at three gamma-centered q meshes.",
                "The earlier source-boundary conclusion is narrowed: precomputed force constants and numeric thermal rows are absent, but the raw force sets do permit harmonic reanalysis.",
            ],
            "what_remains_open": [
                "A negative-frequency branch near the Gamma-A direction is present and omitted from C_v by the explicit zero cutoff.",
                "Source-grade statistical/systematic uncertainty and material-state equivalence to Ding natural graphite are absent.",
                "The harmonic C_v result is not a PBTE transport or TTG response package.",
                "No base-Phi SI anchor, independent alpha_Phi_K, or physical UET thermal map is produced.",
            ],
            "dependency_unlocked": "NIMS harmonic graphite C_v comparator/reanalysis lane only; no Ding C_src acceptance, alpha calibration, transport, Core, Gravity, or Galaxy unlock.",
            "claim_boundary": "Source-backed harmonic comparator only; not Ding-equivalent, not stable-phase acceptance, not source-grade uncertainty, not alpha_Phi_K, not TTG validation, and not Full Topic 13 closure.",
        },
        "ontology": {
            "C": "UET collective system-behaviour coordinate; unrelated to elemental carbon in the NIMS label.",
            "Phi": "effective response variable; no Phi values or map are present in this source calculation.",
            "R_gen": "derived history trace; not added as a state variable.",
            "R_obs": "observer record kept separate; none consumed.",
        },
        "equation_or_mapping": {
            "harmonic_heat_capacity": "Cv(T)=sum_(q,mu) k_B*x^2*exp(x)/(exp(x)-1)^2, x=hbar*omega_(q,mu)/(k_B*T)",
            "molar_to_mass_specific": "Cv_J_kg_K = Cv_J_mol_primitive_cell_K / primitive_molar_mass_kg_mol",
            "molar_to_volumetric": "C_src_J_m3_K = Cv_J_mol_primitive_cell_K / (primitive_volume_A3*1e-30*N_A)",
            "uet_mapping": "Delta_Tq = alpha_Phi_K*Delta_Phi remains uninstantiated.",
        },
        "units": {
            "phonopy_heat_capacity": "J K^-1 mol^-1 of primitive cells",
            "specific_heat": "J kg^-1 K^-1",
            "C_src": "J m^-3 K^-1",
            "temperature": "K",
            "primitive_volume_input": "angstrom^3 per primitive cell",
        },
        "derivation_class": "EXTERNAL_SOURCE_FORCESET_REANALYSIS_HARMONIC_COMPARATOR_NO_UET_DERIVATION",
        "observable": "harmonic constant-volume heat capacity of ideal C/P6/mmm primitive graphite structure",
        "data_role": "EXTERNAL_HARMONIC_CV_COMPARATOR_NOT_DING_C_SRC_ACCEPTANCE",
        "source": {
            "title": "Ab-initio phonon calculation for C / P6/mmm (191) / materials id 990448",
            "creator": "Atsushi Togo",
            "publisher": "NIMS",
            "license": "CC BY 4.0",
            "dataset_locator": SOURCE_URL,
            "archive_path": SOURCE_REL,
            "archive_sha256": archive_hash,
            "archive_sha256_expected": EXPECTED_ARCHIVE_SHA256,
            "archive_member": "phonopy_params.yaml.xz",
            "member_sha256": member_hash,
            "member_sha256_expected": EXPECTED_MEMBER_SHA256,
            "decompressed_yaml_bytes": len(yaml_bytes),
            "source_phonopy_version": source_phonopy_version,
            "reanalysis_phonopy_version": phonopy.__version__,
            "source_claim": "NIMS describes first-principles phonon bands, DOS, constant-volume thermal properties, and raw phonon data.",
            "preprocessing": "Read hash-locked ZIP member; LZMA-decompress YAML; use deposited supercell displacements and forces; identify each displacement-force row by record index, displaced atom, displacement vector, and normalized force-array hash; no figure digitization or data fitting.",
        },
        "reproduction": {
            "solver_results": solver_results,
            "q_mesh_policy": "Exploratory gamma-centered q meshes; no preregistered acceptance threshold was set before this reanalysis.",
            "cutoff_policy": "Explicit CUTOFF_FREQUENCY=0.0 THz and PRETEND_REAL=false; negative frequencies are not converted to real frequencies.",
            "bipm_cross_check": bipm_comparison,
        },
        "uncertainty": {
            "source_statistical_or_systematic_uncertainty_present": False,
            "q_mesh_differences_are_source_uncertainty": False,
            "force_constant_method_spread_is_source_uncertainty": False,
            "material_state_uncertainty": "OPEN; ideal P6/mmm cell is not mapped to Ding natural-graphite morphology/state.",
            "harmonic_stability": "OPEN; a negative-frequency branch is present on each tested mesh.",
        },
        "verification_status": "PASS_SCOPED_SOURCE_AND_HARMONIC_REANALYSIS_WITH_OPEN_PHYSICAL_LIMITS" if passed else status,
        "checks": checks,
        "scope_controls": scope_controls,
        "open_blockers": [
            "nims_harmonic_negative_frequency_branch_unresolved",
            "source_grade_C_src_uncertainty_missing",
            "material_regime_mapping_to_Ding_TTG_not_closed",
            "Ding_PBTE_mode_resolved_response_not_present",
            "alpha_Phi_K_independent_calibration_missing",
            "dimensional_phi_to_thermal_observable_map_missing",
        ],
        "controlling_blocker": "Ding-compatible C_src or accepted same-regime reproduction with material/state mapping and source-grade uncertainty remains missing.",
        "next_action": "Use this as a bounded harmonic comparator; resolve the negative mode and uncertainty only if the NIMS lane is retained, then regenerate the source-route priority projection. Full Topic 13 still requires Ding-compatible C_src, independent alpha_Phi_K, and physical transport/KMS/entropy inputs.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "target_curve_used": False,
            "fit_or_tuning_used": False,
            "calibration_path_may_read_holdout": False,
        },
        "evidence_artifacts": [
            {
                "path": SOURCE_REL,
                "sha256": archive_hash,
                "role": "source archive",
            },
            {
                "path": SCRIPT_REL,
                "sha256": sha256_path(SCRIPT_PATH),
                "role": "reanalysis implementation",
            },
            {
                "path": PRIOR_AUDIT_REL,
                "sha256": prior_audit_hash,
                "role": "prior payload inventory; its inference about reanalysis capability is superseded by this audit",
            },
            {
                "path": "https://phonopy.github.io/phonopy/phonopy-module.html",
                "role": "official Phonopy displacement-force to force-constants documentation",
            },
            {
                "path": BIPM_REPORT_URL,
                "role": "independent graphite c_p comparison; not equivalent to this harmonic c_v",
            },
        ],
    }


def write_artifact(report: dict[str, Any], output_path: Path | None = None) -> Path:
    path = output_path or (ROOT / OUTPUT_REL)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return path


def main() -> int:
    report = build_artifact()
    output = write_artifact(report)
    print(json.dumps({"status": report["status"], "path": output.relative_to(ROOT).as_posix()}, indent=2))
    return 0 if report["status"].startswith("WARN_SCOPED_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
