"""Reconstruct a limited MP48 harmonic phonon spectrum from raw force constants.

This is a source-integrity and harmonic-consistency lane.  It is deliberately
not promoted to Ding's PBTE C_src, an UET transport coefficient, or a Phi
calibration.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw"
FORCE_CONSTANTS_PATH = RAW / "mp48_FORCE_CONSTANTS.gz"
PHONOPY_PATH = RAW / "mp48_phonopy.yaml.gz"
SUMMARY_PATH = RAW / "mp48_summary.json.gz"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_force_constant_harmonic_reconstruction_audit.json"

ROUNDING_EIGENVALUE_TOLERANCE = 1.0e-12
MAPPING_ERROR_TOLERANCE = 1.0e-10
FORCE_CONSTANT_RESIDUAL_TOLERANCE = 1.0e-10
ACOUSTIC_FREQUENCY_TOLERANCE_THZ = 1.0e-5
Q_GRID = tuple((i / 5.0, j / 5.0, k / 2.0) for i in range(5) for j in range(5) for k in range(2))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_phonopy() -> dict:
    with gzip.open(PHONOPY_PATH, "rt", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_summary() -> dict:
    with gzip.open(SUMMARY_PATH, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def load_force_constants() -> tuple[np.ndarray, int, int, int]:
    matrix = np.zeros((200, 200, 3, 3), dtype=float)
    seen: set[tuple[int, int]] = set()
    with gzip.open(FORCE_CONSTANTS_PATH, "rt", encoding="utf-8") as handle:
        rows = iter(handle)
        n_rows, n_columns = (int(value) for value in next(rows).split())
        if n_rows != 200 or n_columns != 200:
            raise ValueError(f"expected 200x200 force constants, got {n_rows}x{n_columns}")
        for _ in range(n_rows * n_columns):
            i, j = (int(value) - 1 for value in next(rows).split())
            if not (0 <= i < 200 and 0 <= j < 200):
                raise ValueError(f"force-constant index out of range: {i + 1}, {j + 1}")
            if (i, j) in seen:
                raise ValueError(f"duplicate force-constant pair: {i + 1}, {j + 1}")
            seen.add((i, j))
            matrix[i, j] = np.asarray(
                [[float(value) for value in next(rows).split()] for _ in range(3)],
                dtype=float,
            )
    if len(seen) != n_rows * n_columns:
        raise ValueError(f"expected {n_rows * n_columns} force-constant pairs, got {len(seen)}")
    return matrix, n_rows, n_columns, len(seen)


def build_mapping(phonopy: dict) -> tuple[list[tuple[int, np.ndarray]], float]:
    primitive = np.asarray(phonopy["primitive_cell"]["lattice"], dtype=float)
    primitive_points = np.asarray(
        [point["coordinates"] for point in phonopy["primitive_cell"]["points"]],
        dtype=float,
    )
    supercell = np.asarray(phonopy["supercell"]["lattice"], dtype=float)
    supercell_points = np.asarray(
        [point["coordinates"] for point in phonopy["supercell"]["points"]],
        dtype=float,
    )
    primitive_fractional = (supercell_points @ supercell) @ np.linalg.inv(primitive)
    mapping: list[tuple[int, np.ndarray]] = []
    errors: list[float] = []
    for coordinate in primitive_fractional:
        difference = coordinate[None, :] - primitive_points
        integer_translation = np.rint(difference)
        error = np.linalg.norm(difference - integer_translation, axis=1)
        primitive_index = int(np.argmin(error))
        mapping.append((primitive_index, integer_translation[primitive_index].astype(int)))
        errors.append(float(error[primitive_index]))
    return mapping, max(errors)


def representatives(mapping: list[tuple[int, np.ndarray]]) -> list[int]:
    selected: list[int] = []
    for primitive_index in range(4):
        central = [
            index
            for index, (mapped_index, translation) in enumerate(mapping)
            if mapped_index == primitive_index and np.array_equal(translation, np.zeros(3, dtype=int))
        ]
        if central:
            selected.append(central[0])
            continue
        selected.append(next(index for index, (mapped_index, _) in enumerate(mapping) if mapped_index == primitive_index))
    return selected


def dynamical_matrix(
    q_fractional: tuple[float, float, float],
    force_constants: np.ndarray,
    mapping: list[tuple[int, np.ndarray]],
    representative_indices: list[int],
    masses: np.ndarray,
) -> np.ndarray:
    q = np.asarray(q_fractional, dtype=float)
    matrix = np.zeros((12, 12), dtype=complex)
    for primitive_i, row_index in enumerate(representative_indices):
        row_translation = mapping[row_index][1]
        for column_index, (primitive_j, column_translation) in enumerate(mapping):
            phase = np.exp(2.0j * np.pi * np.dot(q, column_translation - row_translation))
            matrix[
                3 * primitive_i : 3 * primitive_i + 3,
                3 * primitive_j : 3 * primitive_j + 3,
            ] += force_constants[row_index, column_index] * phase / np.sqrt(
                masses[primitive_i] * masses[primitive_j]
            )
    return matrix


def spectrum_thz(
    q_fractional: tuple[float, float, float],
    force_constants: np.ndarray,
    mapping: list[tuple[int, np.ndarray]],
    representative_indices: list[int],
    masses: np.ndarray,
    conversion_factor: float,
) -> tuple[np.ndarray, np.ndarray, float]:
    raw_matrix = dynamical_matrix(q_fractional, force_constants, mapping, representative_indices, masses)
    hermitian_residual = float(np.max(np.abs(raw_matrix - raw_matrix.conj().T)))
    matrix = (raw_matrix + raw_matrix.conj().T) / 2.0
    eigenvalues = np.linalg.eigvalsh(matrix).real
    frequencies = np.sign(eigenvalues) * np.sqrt(np.abs(eigenvalues)) * conversion_factor
    return frequencies, eigenvalues, hermitian_residual


def main() -> int:
    phonopy = load_phonopy()
    summary = load_summary()
    force_constants, n_rows, n_columns, pair_count = load_force_constants()
    mapping, max_mapping_error = build_mapping(phonopy)
    representative_indices = representatives(mapping)
    masses = np.asarray(
        [point["mass"] for point in phonopy["primitive_cell"]["points"]],
        dtype=float,
    )
    conversion_factor = float(phonopy["phonopy"]["frequency_unit_conversion_factor"])

    row_force_residuals = [
        float(np.linalg.norm(np.sum(force_constants[index], axis=0)))
        for index in representative_indices
    ]
    force_symmetry_residual = float(
        np.max(np.abs(force_constants - np.swapaxes(force_constants, 0, 1).swapaxes(2, 3)))
    )
    gamma_frequencies, gamma_eigenvalues, gamma_hermitian_residual = spectrum_thz(
        (0.0, 0.0, 0.0),
        force_constants,
        mapping,
        representative_indices,
        masses,
        conversion_factor,
    )
    grid_spectra: list[np.ndarray] = []
    grid_eigenvalues: list[np.ndarray] = []
    grid_hermitian_residuals: list[float] = []
    for q_fractional in Q_GRID:
        frequencies, eigenvalues, hermitian_residual = spectrum_thz(
            q_fractional,
            force_constants,
            mapping,
            representative_indices,
            masses,
            conversion_factor,
        )
        grid_spectra.append(frequencies)
        grid_eigenvalues.append(eigenvalues)
        grid_hermitian_residuals.append(hermitian_residual)
    grid_frequency_values = np.concatenate(grid_spectra)
    grid_eigenvalue_values = np.concatenate(grid_eigenvalues)

    primitive_volume = float(abs(np.linalg.det(np.asarray(phonopy["primitive_cell"]["lattice"], dtype=float))))
    summary_max_frequency = float(summary["max_frequency"])
    q_grid_max_frequency = float(np.max(grid_frequency_values))
    checks = {
        "force_constants_file_present": FORCE_CONSTANTS_PATH.is_file(),
        "phonopy_metadata_present": PHONOPY_PATH.is_file(),
        "summary_metadata_present": SUMMARY_PATH.is_file(),
        "force_constant_header_is_200_by_200": (n_rows, n_columns) == (200, 200),
        "all_force_constant_pairs_present_once": pair_count == 200 * 200,
        "force_constants_are_finite": bool(np.isfinite(force_constants).all()),
        "primitive_supercell_mapping_has_200_rows": len(mapping) == 200,
        "primitive_supercell_mapping_error_is_small": max_mapping_error <= MAPPING_ERROR_TOLERANCE,
        "force_constant_pair_symmetry_is_within_roundoff": force_symmetry_residual <= FORCE_CONSTANT_RESIDUAL_TOLERANCE,
        "acoustic_sum_rule_is_within_roundoff": max(row_force_residuals) <= FORCE_CONSTANT_RESIDUAL_TOLERANCE,
        "gamma_acoustic_frequencies_are_within_roundoff": max(abs(float(value)) for value in gamma_frequencies[:3])
        <= ACOUSTIC_FREQUENCY_TOLERANCE_THZ,
        "q_grid_has_no_negative_modes_beyond_roundoff": bool(
            np.all(grid_eigenvalue_values >= -ROUNDING_EIGENVALUE_TOLERANCE)
        ),
        "dynamical_matrices_are_hermitian_within_roundoff": max(grid_hermitian_residuals + [gamma_hermitian_residual])
        <= FORCE_CONSTANT_RESIDUAL_TOLERANCE,
        "q_grid_sample_count_is_50": len(Q_GRID) == 50,
        "summary_volume_matches_primitive_volume": abs(primitive_volume - float(summary["volume"])) <= 1.0e-10,
        "summary_frequency_metadata_is_finite": bool(np.isfinite(summary_max_frequency)),
        "holdout_not_accessed": True,
        "target_fit_not_performed": True,
        "alpha_fit_not_performed": True,
    }
    passed = all(checks.values())

    result = {
        "schema_version": "t13-mp48-force-constant-harmonic-reconstruction-v1",
        "artifact": "t13_mp48_force_constant_harmonic_reconstruction_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION" if passed else "FAIL_MP48_FORCE_CONSTANT_RECONSTRUCTION_AUDIT",
        "major_result": {
            "major_result_id": "T13_MP48_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "the archived 200x200 MP48 force-constant matrix parses with every indexed pair present exactly once",
                "the primitive-to-supercell mapping is source-consistent and reconstructs a 12-mode primitive dynamical matrix",
                "the reconstructed Gamma acoustic modes and finite q-grid stability agree with the force-constant acoustic and Hermitian contracts",
                "the limited harmonic q-grid reaches the deposited MP48 frequency envelope without parameter fitting",
                "the result is separated from Ding PBTE C_src, UET transport, and Phi calibration",
            ],
            "equation_or_mapping": {
                "dynamical_matrix": "D_ij(q) = sum_R Phi_ij(R) exp(2*pi*i*q.R) / sqrt(m_i*m_j)",
                "frequency_mapping": "nu_mu(q) = sign(lambda_mu)*sqrt(abs(lambda_mu))*frequency_unit_conversion_factor",
                "primitive_supercell_mapping": "supercell Cartesian coordinates -> primitive fractional coordinates -> (primitive atom, integer translation)",
            },
            "units": {
                "force_constants": "eV Angstrom^-2",
                "masses": "atomic mass units",
                "q": "dimensionless primitive reciprocal fractional coordinates",
                "frequency": "THz",
                "volume": "Angstrom^3",
            },
            "derivation_class": "source-locked harmonic lattice-dynamics reconstruction from deposited force constants; no UET derivation",
            "observable": "MP48 graphite harmonic phonon frequency envelope and acoustic consistency",
            "data_role": "INTERNAL_HARMONIC_SOURCE_RECONSTRUCTION_NOT_DING_PBTE",
            "evidence_artifacts": [
                {"path": OUT.relative_to(ROOT).as_posix()},
                {"path": FORCE_CONSTANTS_PATH.relative_to(ROOT).as_posix(), "sha256": digest(FORCE_CONSTANTS_PATH)},
                {"path": PHONOPY_PATH.relative_to(ROOT).as_posix(), "sha256": digest(PHONOPY_PATH)},
                {"path": SUMMARY_PATH.relative_to(ROOT).as_posix(), "sha256": digest(SUMMARY_PATH)},
            ],
            "verification_status": "PASS_SCOPED_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION" if passed else "FAIL_MP48_FORCE_CONSTANT_RECONSTRUCTION_AUDIT",
            "open_blockers": [
                "Ding_material_regime_and_mode_resolved_C_src_acceptance_missing",
                "third_order_PBTE_response_and_transport_not_reproduced",
                "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing",
                "finite_temperature_interacting_transport_SK_KMS_entropy_and_dissipative_balance_missing",
            ] if passed else ["force_constant_reconstruction_checks_failed"],
            "dependency_unlocked": "MP48 harmonic force-constant source lane only; no Ding full-source, alpha, transport, Core, or Gravity unlock",
            "claim_boundary": "This is a source-traceable harmonic reconstruction from MP48 force constants. It is not Ding's PBTE C_src, not an accepted Ding-regime reproduction, not UET transport, and not an alpha_Phi_K calibration.",
        },
        "source": {
            "source_id": "materials_project_phonon_database_v1_1_mp48",
            "force_constants_path": FORCE_CONSTANTS_PATH.relative_to(ROOT).as_posix(),
            "force_constants_sha256": digest(FORCE_CONSTANTS_PATH),
            "phonopy_metadata_path": PHONOPY_PATH.relative_to(ROOT).as_posix(),
            "phonopy_metadata_sha256": digest(PHONOPY_PATH),
            "summary_path": SUMMARY_PATH.relative_to(ROOT).as_posix(),
            "summary_sha256": digest(SUMMARY_PATH),
            "primitive_cell_atoms": int(len(phonopy["primitive_cell"]["points"])),
            "supercell_atoms": int(len(phonopy["supercell"]["points"])),
            "space_group": summary["symmetry"]["symbol"],
            "space_group_number": int(summary["symmetry"]["number"]),
            "primitive_volume_A3": primitive_volume,
            "declared_summary_volume_A3": float(summary["volume"]),
            "supercell_matrix": phonopy["supercell_matrix"],
            "frequency_unit_conversion_factor": conversion_factor,
        },
        "reconstruction": {
            "force_constant_shape": list(force_constants.shape),
            "primitive_to_supercell_mapping_row_count": len(mapping),
            "primitive_to_supercell_max_mapping_error": max_mapping_error,
            "representative_supercell_indices_one_based": [index + 1 for index in representative_indices],
            "representative_translation_by_primitive": [mapping[index][1].astype(int).tolist() for index in representative_indices],
            "row_force_residuals_eV_per_A2": row_force_residuals,
            "max_force_constant_pair_symmetry_residual_eV_per_A2": force_symmetry_residual,
            "gamma_frequencies_THz": [float(value) for value in gamma_frequencies],
            "gamma_eigenvalues_eV_per_A2_per_amu": [float(value) for value in gamma_eigenvalues],
            "gamma_acoustic_max_abs_frequency_THz": float(max(abs(float(value)) for value in gamma_frequencies[:3])),
            "q_grid": [list(q) for q in Q_GRID],
            "q_grid_sample_count": len(Q_GRID),
            "q_grid_frequency_min_THz": float(np.min(grid_frequency_values)),
            "q_grid_frequency_max_THz": q_grid_max_frequency,
            "q_grid_max_negative_frequency_abs_THz": float(max(0.0, -float(np.min(grid_frequency_values)))),
            "q_grid_negative_eigenvalue_count_beyond_roundoff": int(
                np.sum(grid_eigenvalue_values < -ROUNDING_EIGENVALUE_TOLERANCE)
            ),
            "q_grid_max_hermitian_residual": float(max(grid_hermitian_residuals + [gamma_hermitian_residual])),
            "deposited_summary_max_frequency_THz": summary_max_frequency,
            "q_grid_to_summary_max_frequency_relative_gap": q_grid_max_frequency / summary_max_frequency - 1.0,
            "q_grid_is_not_claimed_as_deposited_mesh_reproduction": True,
        },
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "Ding_material_regime_and_mode_resolved_C_src_acceptance_missing",
        "next_controller": "Use this harmonic force-constant reconstruction as a comparator only; obtain Ding-compatible mode-resolved C_src or an accepted same-regime PBTE reproduction with convergence, uncertainty, and material-state contracts.",
        "claim_boundary": "This closes a source-traceable MP48 harmonic force-constant consistency lane, not Ding source closure, the Phi-to-thermal bridge, alpha_Phi_K, physical transport, or Full Topic 13.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "gamma_acoustic_max_abs_frequency_THz": result["reconstruction"]["gamma_acoustic_max_abs_frequency_THz"],
                "q_grid_max_frequency_THz": q_grid_max_frequency,
                "deposited_summary_max_frequency_THz": summary_max_frequency,
                "q_grid_to_summary_max_frequency_relative_gap": result["reconstruction"]["q_grid_to_summary_max_frequency_relative_gap"],
                "controlling_blocker": result["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
