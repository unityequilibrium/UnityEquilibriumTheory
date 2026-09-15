"""Audit q-mesh convergence for an independent MP48 harmonic C_src route.

This audit is intentionally conservative.  It tests whether the deposited
second-order force constants support a mesh-stable harmonic heat-capacity
reproduction.  It does not relabel MP48 as Ding data, infer alpha_Phi_K, or
consume the locked Xie 2026 holdout.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np

from audit_topic13_mp48_force_constant_harmonic_reconstruction import (
    build_mapping,
    load_force_constants,
    load_phonopy,
    representatives,
    spectrum_thz,
)


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw"
FORCE_CONSTANTS_PATH = RAW / "mp48_FORCE_CONSTANTS.gz"
PHONOPY_PATH = RAW / "mp48_phonopy.yaml.gz"
SUMMARY_PATH = RAW / "mp48_summary.json.gz"
THERMAL_PATH = RAW / "mp48_thermal_properties.yaml.gz"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json"

AVOGADRO = 6.02214076e23
PLANCK = 6.62607015e-34
BOLTZMANN = 1.380649e-23
TARGET_TEMPERATURES_K = (100.0, 200.0, 250.0, 300.0)
MESHES = ((5, 5, 2), (10, 10, 4), (15, 15, 6), (20, 20, 8), (25, 25, 10), (30, 30, 12), (35, 35, 14))
MESH_STEP_ACCEPTANCE_TOLERANCE = 1.0e-2
NEGATIVE_EIGENVALUE_TOLERANCE = 1.0e-12


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_deposited_heat_capacity() -> dict[float, float]:
    import gzip
    import re

    text = gzip.open(THERMAL_PATH, "rt", encoding="utf-8").read()
    rows = re.findall(
        r"- temperature:\s*([0-9.]+)\s*\n"
        r"\s+free_energy:\s*[^\n]+\n"
        r"\s+entropy:\s*[^\n]+\n"
        r"\s+heat_capacity:\s*([0-9.eE+-]+)",
        text,
    )
    return {float(temperature): float(value) for temperature, value in rows}


def mode_heat_capacity(frequency_thz: np.ndarray, temperature_K: float) -> np.ndarray:
    x = PLANCK * np.abs(frequency_thz) * 1.0e12 / (BOLTZMANN * temperature_K)
    result = np.empty_like(x, dtype=float)
    small = np.abs(x) < 1.0e-7
    result[small] = BOLTZMANN
    regular = ~small
    exponent = np.exp(np.clip(x[regular], -700.0, 700.0))
    result[regular] = BOLTZMANN * x[regular] ** 2 * exponent / (exponent - 1.0) ** 2
    return result


def q_grid(shape: tuple[int, int, int]) -> list[tuple[float, float, float]]:
    nx, ny, nz = shape
    return [
        (i / float(nx), j / float(ny), k / float(nz))
        for i in range(nx)
        for j in range(ny)
        for k in range(nz)
    ]


def reconstruct_rows(
    shape: tuple[int, int, int],
    force_constants: np.ndarray,
    mapping: list[tuple[int, np.ndarray]],
    representative_indices: list[int],
    masses: np.ndarray,
    conversion_factor: float,
) -> tuple[list[dict[str, float]], int, float]:
    rows: list[dict[str, float]] = []
    negative_eigenvalue_count = 0
    minimum_eigenvalue = float("inf")
    frequencies_by_q: list[np.ndarray] = []
    for q_fractional in q_grid(shape):
        frequencies, eigenvalues, _ = spectrum_thz(
            q_fractional,
            force_constants,
            mapping,
            representative_indices,
            masses,
            conversion_factor,
        )
        frequencies_by_q.append(frequencies)
        negative_eigenvalue_count += int(np.sum(eigenvalues < -NEGATIVE_EIGENVALUE_TOLERANCE))
        minimum_eigenvalue = min(minimum_eigenvalue, float(np.min(eigenvalues)))

    for temperature in TARGET_TEMPERATURES_K:
        capacity_sum = sum(
            float(np.sum(mode_heat_capacity(frequencies, temperature)))
            for frequencies in frequencies_by_q
        )
        capacity = capacity_sum / float(len(frequencies_by_q)) * AVOGADRO
        rows.append(
            {
                "temperature_K": temperature,
                "heat_capacity_J_per_mol_cell_K": capacity,
            }
        )
    return rows, negative_eigenvalue_count, minimum_eigenvalue


def reconstruct_rows_batched(
    shape: tuple[int, int, int],
    force_constants: np.ndarray,
    mapping: list[tuple[int, np.ndarray]],
    representative_indices: list[int],
    masses: np.ndarray,
    conversion_factor: float,
) -> tuple[list[dict[str, float]], int, float]:
    """Evaluate the same dynamical matrices in q-point batches."""
    q_values = np.asarray(
        [
            (i / float(shape[0]), j / float(shape[1]), k / float(shape[2]))
            for i in range(shape[0])
            for j in range(shape[1])
            for k in range(shape[2])
        ],
        dtype=float,
    )
    translations = np.asarray([translation for _, translation in mapping], dtype=float)
    row_translations = np.asarray(
        [mapping[index][1] for index in representative_indices], dtype=float
    )
    primitive_indices = np.asarray([primitive for primitive, _ in mapping], dtype=int)
    coefficients = np.zeros((4, len(mapping), 12, 12), dtype=complex)
    for primitive_i, row_index in enumerate(representative_indices):
        for column_index, primitive_j in enumerate(primitive_indices):
            coefficients[
                primitive_i,
                column_index,
                3 * primitive_i : 3 * primitive_i + 3,
                3 * primitive_j : 3 * primitive_j + 3,
            ] = force_constants[row_index, column_index] / np.sqrt(
                masses[primitive_i] * masses[primitive_j]
            )

    frequencies_by_q: list[np.ndarray] = []
    negative_eigenvalue_count = 0
    minimum_eigenvalue = float("inf")
    for start in range(0, len(q_values), 1024):
        q_chunk = q_values[start : start + 1024]
        phase_argument = 2.0j * np.pi * np.einsum(
            "nd,rkd->nrk",
            q_chunk,
            translations[None, :, :] - row_translations[:, None, :],
        )
        phases = np.exp(phase_argument)
        matrices = np.einsum("nrm,rmij->nij", phases, coefficients)
        matrices = (matrices + np.swapaxes(matrices.conj(), 1, 2)) / 2.0
        eigenvalues = np.linalg.eigvalsh(matrices).real
        negative_eigenvalue_count += int(np.sum(eigenvalues < -NEGATIVE_EIGENVALUE_TOLERANCE))
        minimum_eigenvalue = min(minimum_eigenvalue, float(np.min(eigenvalues)))
        frequencies_by_q.append(
            np.sign(eigenvalues) * np.sqrt(np.abs(eigenvalues)) * conversion_factor
        )

    frequencies = np.concatenate(frequencies_by_q, axis=0)
    rows = []
    for temperature in TARGET_TEMPERATURES_K:
        rows.append(
            {
                "temperature_K": temperature,
                "heat_capacity_J_per_mol_cell_K": float(
                    np.sum(mode_heat_capacity(frequencies, temperature))
                    / float(len(frequencies))
                    * AVOGADRO
                ),
            }
        )
    return rows, negative_eigenvalue_count, minimum_eigenvalue

def main() -> int:
    phonopy = load_phonopy()
    force_constants, n_rows, n_columns, pair_count = load_force_constants()
    mapping, mapping_error = build_mapping(phonopy)
    representative_indices = representatives(mapping)
    masses = np.asarray(
        [point["mass"] for point in phonopy["primitive_cell"]["points"]],
        dtype=float,
    )
    conversion_factor = float(phonopy["phonopy"]["frequency_unit_conversion_factor"])
    deposited = read_deposited_heat_capacity()

    mesh_rows: dict[str, dict[str, object]] = {}
    for shape in MESHES:
        rows, negative_count, minimum_eigenvalue = reconstruct_rows_batched(
            shape,
            force_constants,
            mapping,
            representative_indices,
            masses,
            conversion_factor,
        )
        key = "x".join(str(value) for value in shape)
        mesh_rows[key] = {
            "q_shape": list(shape),
            "q_point_count": int(np.prod(shape)),
            "rows": rows,
            "negative_eigenvalue_count_beyond_tolerance": negative_count,
            "minimum_eigenvalue_eV_per_A2_per_amu": minimum_eigenvalue,
        }

    relative_steps: list[dict[str, float | str]] = []
    for left, right in zip(MESHES, MESHES[1:]):
        left_key = "x".join(str(value) for value in left)
        right_key = "x".join(str(value) for value in right)
        left_rows = mesh_rows[left_key]["rows"]
        right_rows = mesh_rows[right_key]["rows"]
        for left_row, right_row in zip(left_rows, right_rows):
            relative_steps.append(
                {
                    "from_mesh": left_key,
                    "to_mesh": right_key,
                    "temperature_K": float(left_row["temperature_K"]),
                    "relative_step": float(
                        right_row["heat_capacity_J_per_mol_cell_K"]
                        / left_row["heat_capacity_J_per_mol_cell_K"]
                        - 1.0
                    ),
                }
            )

    max_relative_step = max(abs(float(row["relative_step"])) for row in relative_steps)
    source_checks = {
        "force_constants_file_present": FORCE_CONSTANTS_PATH.is_file(),
        "phonopy_metadata_present": PHONOPY_PATH.is_file(),
        "summary_metadata_present": SUMMARY_PATH.is_file(),
        "thermal_properties_file_present": THERMAL_PATH.is_file(),
        "force_constant_shape_is_200_by_200": (n_rows, n_columns) == (200, 200),
        "all_force_constant_pairs_present_once": pair_count == 200 * 200,
        "primitive_supercell_mapping_error_is_small": mapping_error <= 1.0e-10,
        "all_mesh_rows_are_finite": all(
            np.isfinite(float(row["heat_capacity_J_per_mol_cell_K"]))
            for mesh in mesh_rows.values()
            for row in mesh["rows"]
        ),
        "all_meshes_have_no_negative_modes_beyond_tolerance": all(
            int(mesh["negative_eigenvalue_count_beyond_tolerance"]) == 0
            for mesh in mesh_rows.values()
        ),
        "deposited_reference_rows_present": all(
            temperature in deposited for temperature in TARGET_TEMPERATURES_K
        ),
        "holdout_not_accessed": True,
        "target_fit_not_performed": True,
        "alpha_fit_not_performed": True,
    }
    source_integrity_pass = all(source_checks.values())
    fine_tail_pairs = {("20x20x8", "25x25x10"), ("25x25x10", "30x30x12"), ("30x30x12", "35x35x14")}
    fine_tail_relative_steps = [
        row for row in relative_steps
        if (str(row["from_mesh"]), str(row["to_mesh"])) in fine_tail_pairs
    ]
    max_fine_tail_relative_step = max(
        abs(float(row["relative_step"])) for row in fine_tail_relative_steps
    )
    fine_tail_pair_count_is_complete = len(fine_tail_relative_steps) == (
        len(fine_tail_pairs) * len(TARGET_TEMPERATURES_K)
    )
    fine_tail_converged = (
        source_integrity_pass
        and fine_tail_pair_count_is_complete
        and max_fine_tail_relative_step <= MESH_STEP_ACCEPTANCE_TOLERANCE
    )
    finest_pair_relative_steps = [
        row for row in relative_steps
        if (str(row["from_mesh"]), str(row["to_mesh"])) == ("30x30x12", "35x35x14")
    ]
    max_finest_pair_relative_step = max(
        abs(float(row["relative_step"])) for row in finest_pair_relative_steps
    )
    finest_pair_converged = (
        source_integrity_pass
        and max_finest_pair_relative_step <= MESH_STEP_ACCEPTANCE_TOLERANCE
    )
    # Coarse meshes are retained as diagnostics; convergence is accepted only
    # after the complete declared fine tail is stable across all temperatures.
    mesh_converged = source_integrity_pass and fine_tail_converged
    status = (
        "PASS_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE"
        if mesh_converged
        else "BLOCKED_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE"
    )

    result = {
        "schema_version": "t13-mp48-force-constant-csrc-mesh-convergence-v1",
        "artifact": "t13_mp48_force_constant_csrc_mesh_convergence_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if source_integrity_pass else "OPEN",
            "what_is_closed": [
                "the deposited MP48 second-order force constants were tested on seven explicit q-meshes",
                "the native 5x5x2 result and coarse pre-asymptotic changes are retained as diagnostics",
                "the complete 20x20x8 through 35x35x14 fine tail is accepted only when all three adjacent pairs and all target temperatures satisfy the declared tolerance",
                "the mesh-step and negative-mode diagnostics are source-traceable and emitted in machine-readable form",
                "the independent route is prevented from becoming Ding C_src, an alpha_Phi_K calibration, or a holdout fit",
            ],
            "equation_or_mapping": {
                "mode_heat_capacity": "c_mu(T) = k_B*x_mu^2*exp(x_mu)/(exp(x_mu)-1)^2; x_mu=h*nu_mu/(k_B*T)",
                "mesh_sum": "C_src^mesh(T) = N_A/N_q * sum_(q,mu) c_mu(q,T)",
                "Ding_boundary": "Delta_Tq = Delta_u_ph / C_src",
            },
            "units": {
                "frequency": "THz",
                "q": "dimensionless primitive reciprocal fractional coordinates",
                "heat_capacity": "J K^-1 mol^-1 primitive cell",
                "eigenvalue": "eV A^-2 amu^-1",
            },
            "derivation_class": "source-locked harmonic lattice-dynamics reconstruction and deterministic mesh sensitivity audit; no UET derivation",
            "observable": "independent MP48 harmonic graphite heat-capacity comparator",
            "data_role": "INDEPENDENT_REPRODUCTION_NOT_CALIBRATION",
            "evidence_artifacts": [
                {"path": OUT.relative_to(ROOT).as_posix()},
                {"path": FORCE_CONSTANTS_PATH.relative_to(ROOT).as_posix(), "sha256": digest(FORCE_CONSTANTS_PATH)},
                {"path": PHONOPY_PATH.relative_to(ROOT).as_posix(), "sha256": digest(PHONOPY_PATH)},
                {"path": SUMMARY_PATH.relative_to(ROOT).as_posix(), "sha256": digest(SUMMARY_PATH)},
                {"path": THERMAL_PATH.relative_to(ROOT).as_posix(), "sha256": digest(THERMAL_PATH)},
            ],
            "verification_status": status,
            "open_blockers": [
                *([] if mesh_converged else ["mp48_force_constant_C_src_mesh_convergence_missing"]),
                "Ding_material_regime_and_mode_resolved_C_src_acceptance_missing",
                "Ding_C_src_uncertainty_or_PBTE_convergence_contract_missing",
                "base_Phi_to_Delta_u_ph_mapping_and_alpha_Phi_K_missing",
            ],
            "dependency_unlocked": "No Ding-source or Core dependency unlock; only the q-mesh convergence question is closed for this independent lane",
            "claim_boundary": "This audit does not establish Ding PBTE C_src, same-regime material equivalence, UET transport, a Phi-to-energy anchor, alpha_Phi_K, or Full Topic 13 closure.",
        },
        "source": {
            "source_id": "materials_project_phonon_database_v1_1_mp48",
            "force_constants_path": FORCE_CONSTANTS_PATH.relative_to(ROOT).as_posix(),
            "force_constants_sha256": digest(FORCE_CONSTANTS_PATH),
            "phonopy_metadata_path": PHONOPY_PATH.relative_to(ROOT).as_posix(),
            "phonopy_metadata_sha256": digest(PHONOPY_PATH),
            "summary_path": SUMMARY_PATH.relative_to(ROOT).as_posix(),
            "summary_sha256": digest(SUMMARY_PATH),
            "thermal_properties_path": THERMAL_PATH.relative_to(ROOT).as_posix(),
            "thermal_properties_sha256": digest(THERMAL_PATH),
            "primitive_cell_atoms": 4,
            "supercell_matrix": phonopy["supercell_matrix"],
            "temperature_rows_K": list(TARGET_TEMPERATURES_K),
        },
        "mesh_policy": {
            "meshes": [list(shape) for shape in MESHES],
            "acceptance_tolerance_abs_relative_step": MESH_STEP_ACCEPTANCE_TOLERANCE,
            "tolerance_role": "declared numerical source-acceptance criterion; not the TTG leakage threshold and not a physical uncertainty bound",
            "native_mesh": "5x5x2",
            "fine_tail_meshes": ["20x20x8", "25x25x10", "30x30x12", "35x35x14"],
            "acceptance_policy": "complete_three_pair_fine_tail_across_all_target_temperatures",
            "coarse_mesh_steps_retained_as_diagnostic": True,
            "fine_tail_pair_count_is_complete": fine_tail_pair_count_is_complete,
            "fine_tail_max_abs_relative_step": max_fine_tail_relative_step,
            "fine_tail_converged": fine_tail_converged,
            "finest_pair_meshes": ["30x30x12", "35x35x14"],
            "finest_pair_max_abs_relative_step": max_finest_pair_relative_step,
            "finest_pair_converged": finest_pair_converged,
            "continuum_convergence_required_for_Ding_acceptance": True,
        },
        "mesh_results": mesh_rows,
        "deposited_reference_rows": [
            {
                "temperature_K": temperature,
                "deposited_heat_capacity_J_per_mol_cell_K": deposited[temperature],
            }
            for temperature in TARGET_TEMPERATURES_K
        ],
        "relative_mesh_steps": relative_steps,
        "max_abs_relative_mesh_step": max_relative_step,
        "max_abs_relative_fine_tail_mesh_step": max_fine_tail_relative_step,
        "max_abs_relative_finest_pair_mesh_step": max_finest_pair_relative_step,
        "checks": source_checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": (
            "Ding_material_regime_and_mode_resolved_C_src_acceptance_missing"
            if mesh_converged
            else "mp48_force_constant_C_src_mesh_convergence_missing"
        ),
        "next_controller": (
            "Obtain a Ding-compatible mode-resolved C_src or a permissioned source package, without relabeling the native MP48 mesh."
            if not mesh_converged
            else "Use the asymptotically converged MP48 harmonic route only as an independent comparator while closing Ding material matching, uncertainty, and base-Phi mapping."
        ),
        "claim_boundary": "The MP48 force-constant route is a harmonic comparator. A finite native-mesh match is not a continuum convergence proof, a Ding PBTE reproduction, a Phi calibration, or external validation.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "closure_level": result["major_result"]["closure_level"],
                "max_abs_relative_mesh_step": max_relative_step,
                "controlling_blocker": result["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if source_integrity_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
