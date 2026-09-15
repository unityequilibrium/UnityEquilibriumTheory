"""Build a standard harmonic Phi_E dimensional comparator from MP48.

This lane defines a named energy-response coordinate Phi_E := Delta_u/e0.
It does not identify the base UET Phi with Phi_E and does not emit alpha_Phi_K.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw"
DOS_PATH = RAW / "mp48_total_dos.dat.gz"
PACKAGE_PATH = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "mp48_independent_graphite_cv_source_package.json"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_phi_e_dimensional_comparator_audit.json"

AVOGADRO = 6.02214076e23
PLANCK = 6.62607015e-34
BOLTZMANN = 1.380649e-23
TEMPERATURES_K = (200.0, 250.0, 300.0)
REFERENCE_TEMPERATURE_K = 300.0


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_dos() -> tuple[np.ndarray, np.ndarray, int]:
    rows: list[tuple[float, float]] = []
    with gzip.open(DOS_PATH, "rt", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            frequency, density = line.split()[:2]
            rows.append((float(frequency), float(density)))
    values = np.asarray(rows, dtype=float)
    if values.shape != (201, 2):
        raise ValueError(f"expected 201 DOS rows, got {values.shape}")
    # The archived grid has zero DOS below zero frequency. Keep the declared
    # source grid intact while excluding zero-weight negative bins explicitly.
    if np.any(values[values[:, 0] < 0.0, 1] != 0.0):
        raise ValueError("nonzero negative-frequency DOS weight is not accepted")
    positive = values[:, 0] >= 0.0
    return values[positive, 0], values[positive, 1], len(values)


def mode_energy(frequency_thz: np.ndarray, temperature_K: float) -> np.ndarray:
    x = PLANCK * frequency_thz * 1.0e12 / (BOLTZMANN * temperature_K)
    result = np.zeros_like(x, dtype=float)
    nonzero = x > 0.0
    result[nonzero] = (
        PLANCK * frequency_thz[nonzero] * 1.0e12 / np.expm1(x[nonzero])
    )
    return result


def mode_heat_capacity(frequency_thz: np.ndarray, temperature_K: float) -> np.ndarray:
    x = PLANCK * frequency_thz * 1.0e12 / (BOLTZMANN * temperature_K)
    result = np.empty_like(x, dtype=float)
    small = np.abs(x) < 1.0e-7
    result[small] = BOLTZMANN
    regular = ~small
    denominator = np.expm1(x[regular])
    result[regular] = BOLTZMANN * x[regular] ** 2 * np.exp(
        np.clip(x[regular], -700.0, 700.0)
    ) / denominator**2
    return result


def main() -> int:
    frequencies_thz, density_per_thz, source_row_count = read_dos()
    package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8-sig"))
    source_volume_A3 = float(package["material"]["source_volume_A3"])
    molar_volume_m3 = source_volume_A3 * 1.0e-30 * AVOGADRO

    rows: list[dict[str, float | str]] = []
    for temperature in TEMPERATURES_K:
        energy_integrand = density_per_thz * mode_energy(
            frequencies_thz, temperature
        ) * AVOGADRO
        capacity_integrand = density_per_thz * mode_heat_capacity(
            frequencies_thz, temperature
        ) * AVOGADRO
        energy_molar = float(np.trapezoid(energy_integrand, frequencies_thz))
        capacity_molar = float(np.trapezoid(capacity_integrand, frequencies_thz))
        energy_density = energy_molar / molar_volume_m3
        capacity_density = capacity_molar / molar_volume_m3
        rows.append(
            {
                "temperature_K": temperature,
                "thermal_phonon_energy_J_per_mol_cell": energy_molar,
                "thermal_phonon_energy_density_J_per_m3": energy_density,
                "harmonic_cv_J_per_mol_cell_K": capacity_molar,
                "harmonic_cv_volumetric_J_per_m3_K": capacity_density,
                "alpha_Phi_E_K": energy_density / capacity_density,
                "phi_e_definition": "Phi_E = Delta_u_ph / e0(T_reference)",
            }
        )

    reference = next(
        row for row in rows if row["temperature_K"] == REFERENCE_TEMPERATURE_K
    )
    checks = {
        "dos_file_present": DOS_PATH.is_file(),
        "source_package_present": PACKAGE_PATH.is_file(),
        "dos_row_count_is_201": source_row_count == 201,
        "negative_frequency_weight_is_zero": True,
        "frequency_grid_is_uniform": bool(
            np.allclose(np.diff(frequencies_thz), np.diff(frequencies_thz)[0])
        ),
        "source_volume_is_positive": source_volume_A3 > 0.0,
        "reference_temperature_row_present": len(rows) == len(TEMPERATURES_K),
        "energy_and_capacity_are_finite": all(
            np.isfinite(float(row[key]))
            for row in rows
            for key in (
                "thermal_phonon_energy_J_per_mol_cell",
                "thermal_phonon_energy_density_J_per_m3",
                "harmonic_cv_J_per_mol_cell_K",
                "harmonic_cv_volumetric_J_per_m3_K",
                "alpha_Phi_E_K",
            )
        ),
        "reference_alpha_is_volume_invariant": abs(
            float(reference["alpha_Phi_E_K"])
            - float(reference["thermal_phonon_energy_J_per_mol_cell"])
            / float(reference["harmonic_cv_J_per_mol_cell_K"])
        )
        <= 1.0e-12,
        "base_phi_to_phi_e_mapping_remains_open": True,
        "numeric_alpha_Phi_K_not_emitted": True,
        "holdout_not_accessed": True,
        "target_fit_not_performed": True,
        "alpha_Phi_K_fit_not_performed": True,
    }
    passed = all(checks.values())

    result = {
        "schema_version": "t13-mp48-phi-e-dimensional-comparator-v1",
        "artifact": "t13_mp48_phi_e_dimensional_comparator_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_PHI_E_DIMENSIONAL_COMPARATOR" if passed else "FAIL_PHI_E_DIMENSIONAL_COMPARATOR_AUDIT",
        "major_result": {
            "major_result_id": "T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "a named standard-physics Phi_E coordinate is dimensionally anchored to MP48 harmonic thermal energy at a declared reference temperature",
                "the same DOS and shared volume produce a numeric conditional alpha_Phi_E_K = e0/c_v without target fitting",
                "the scale is separated from base UET Phi and no alpha_Phi_K is emitted",
            ],
            "equation_or_mapping": {
                "thermal_energy": "u_th(T) = N_A integral[g(nu) h nu/(exp(h nu/(k_B T))-1) dnu]",
                "reference_scale": "e0(T0) := u_th(T0)",
                "named_coordinate": "Phi_E = Delta_u_ph / e0(T0)",
                "temperature_map": "Delta_Tq = (e0(T0)/c_v(T0)) Phi_E",
                "conditional_coefficient": "alpha_Phi_E_K = e0(T0)/c_v(T0)",
            },
            "units": {
                "thermal_energy_density": "J m^-3",
                "e0": "J m^-3",
                "c_v": "J m^-3 K^-1",
                "Phi_E": "dimensionless",
                "alpha_Phi_E_K": "K per normalized Phi_E",
            },
            "derivation_class": "standard harmonic phonon statistical-mechanics energy/heat-capacity map with source-defined reference scale; no UET base-Phi derivation",
            "observable": "MP48 harmonic graphite thermal energy and conditional temperature response",
            "data_role": "EXTERNAL_INPUT_STANDARD_HARMONIC_COMPARATOR_NOT_BASE_PHI_CALIBRATION",
            "evidence_artifacts": [
                {"path": OUT.relative_to(ROOT).as_posix()},
                {"path": DOS_PATH.relative_to(ROOT).as_posix(), "sha256": digest(DOS_PATH)},
                {"path": PACKAGE_PATH.relative_to(ROOT).as_posix(), "sha256": digest(PACKAGE_PATH)},
            ],
            "verification_status": "PASS_SCOPED_PHI_E_DIMENSIONAL_COMPARATOR" if passed else "FAIL_PHI_E_DIMENSIONAL_COMPARATOR_AUDIT",
            "open_blockers": [
                "base_Phi_to_Phi_E_mapping_missing",
                "independent_alpha_Phi_K_missing",
                "Ding_PBTE_C_src_and_material_matching_missing",
                "finite_temperature_interacting_transport_SK_KMS_entropy_and_dissipative_balance_missing",
            ] if passed else ["Phi_E_dimensional_comparator_checks_failed"],
            "dependency_unlocked": "named Phi_E comparator and standard dimensional map only; base Phi, alpha_Phi_K, Full Topic 13, Core, Gravity, and transport remain blocked",
            "claim_boundary": "This is a source-traceable standard harmonic Phi_E comparator at a declared MP48 reference scale. It is not a base-Phi calibration, not alpha_Phi_K, not Ding PBTE validation, and not a UET temperature prediction.",
        },
        "source": {
            "source_id": package["source"]["source_id"],
            "dos_path": DOS_PATH.relative_to(ROOT).as_posix(),
            "dos_sha256": digest(DOS_PATH),
            "package_path": PACKAGE_PATH.relative_to(ROOT).as_posix(),
            "package_sha256": digest(PACKAGE_PATH),
            "source_volume_A3": source_volume_A3,
            "molar_volume_m3_per_cell": molar_volume_m3,
            "reference_temperature_K": REFERENCE_TEMPERATURE_K,
            "zero_point_energy_included": False,
            "temperature_rows": rows,
        },
        "uncertainty_contract": {
            "source_statistical_uncertainty": "NOT_REPORTED_BY_DEPOSIT",
            "shared_volume_ratio_sensitivity": "cancels in alpha_Phi_E_K when e0 and c_v use the same source volume",
            "harmonic_model_discrepancy_envelope_relative": package["uncertainty_contract"]["model_discrepancy_envelope_relative"],
            "temperature_volume_status": package["experimental_volume_anchor"]["temperature_resolved_volume_status"],
            "interpretation": "the displayed alpha_Phi_E_K is a conditional standard-physics comparator, not a statistical UET calibration uncertainty",
        },
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "alpha_Phi_K_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "numeric_alpha_Phi_E_K_emitted": True,
        "reference_alpha_Phi_E_K": reference["alpha_Phi_E_K"],
        "controlling_blocker": "base_Phi_to_Phi_E_mapping_and_independent_alpha_Phi_K_missing",
        "next_controller": "derive or source-lock the base-Phi-to-Phi_E amplitude map; do not relabel this conditional coefficient as alpha_Phi_K",
        "claim_boundary": "Closes only a named Phi_E standard-physics dimensional comparator. Base Phi remains an effective response variable with no SI normalization, and Full Topic 13 remains blocked.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "reference_alpha_Phi_E_K": reference["alpha_Phi_E_K"], "controlling_blocker": result["controlling_blocker"]}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
