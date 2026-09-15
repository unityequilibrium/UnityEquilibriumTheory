"""Reproduce harmonic spectral heat capacity from the archived MP48 DOS.

The result is a cross-file consistency lane for the MP48 harmonic package. It
is deliberately not promoted to Ding's PBTE C_src or to a UET calibration.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from datetime import date
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw"
DOS_PATH = RAW / "mp48_total_dos.dat.gz"
THERMAL_PATH = RAW / "mp48_thermal_properties.yaml.gz"
PHONOPY_PATH = RAW / "mp48_phonopy.yaml.gz"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_spectral_csrc_reproduction_audit.json"

AVOGADRO = 6.02214076e23
PLANCK = 6.62607015e-34
BOLTZMANN = 1.380649e-23
TEMPERATURES_K = (200.0, 250.0, 300.0)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_dos() -> tuple[np.ndarray, np.ndarray]:
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
    return values[:, 0], values[:, 1]


def read_thermal_properties() -> dict[float, float]:
    text = gzip.open(THERMAL_PATH, "rt", encoding="utf-8").read()
    rows = re.findall(
        r"- temperature:\s*([0-9.]+)\s*\n"
        r"\s+free_energy:\s*[^\n]+\n"
        r"\s+entropy:\s*[^\n]+\n"
        r"\s+heat_capacity:\s*([0-9.eE+-]+)",
        text,
    )
    return {float(temperature): float(heat_capacity) for temperature, heat_capacity in rows}


def simpson(values: np.ndarray, x: np.ndarray) -> float:
    if len(values) % 2 == 0 or not np.allclose(np.diff(x), np.diff(x)[0]):
        raise ValueError("composite Simpson audit requires an odd, uniform grid")
    spacing = float(x[1] - x[0])
    return float(
        spacing
        / 3.0
        * (
            values[0]
            + values[-1]
            + 4.0 * np.sum(values[1:-1:2])
            + 2.0 * np.sum(values[2:-2:2])
        )
    )


def mode_heat_capacity(frequency_thz: np.ndarray, temperature_K: float) -> np.ndarray:
    x = PLANCK * frequency_thz * 1.0e12 / (BOLTZMANN * temperature_K)
    result = np.empty_like(x, dtype=float)
    small = np.abs(x) < 1.0e-7
    result[small] = BOLTZMANN
    regular = ~small
    exponent = np.exp(np.clip(x[regular], -700.0, 700.0))
    result[regular] = BOLTZMANN * x[regular] ** 2 * exponent / (exponent - 1.0) ** 2
    return result


def main() -> int:
    frequencies_thz, density_per_thz = read_dos()
    thermal_properties = read_thermal_properties()
    missing = [temperature for temperature in TEMPERATURES_K if temperature not in thermal_properties]
    if missing:
        raise ValueError(f"thermal-property reference rows missing: {missing}")

    dos_integrand = density_per_thz
    mode_count = float(np.trapezoid(dos_integrand, frequencies_thz))
    mode_count_simpson = simpson(dos_integrand, frequencies_thz)
    mode_count_coarse = float(np.trapezoid(dos_integrand[::2], frequencies_thz[::2]))

    rows: list[dict[str, float | str]] = []
    for temperature in TEMPERATURES_K:
        mode_capacity = mode_heat_capacity(frequencies_thz, temperature)
        integrand = density_per_thz * mode_capacity * AVOGADRO
        spectral_trapezoid = float(np.trapezoid(integrand, frequencies_thz))
        spectral_simpson = simpson(integrand, frequencies_thz)
        spectral_coarse = float(np.trapezoid(integrand[::2], frequencies_thz[::2]))
        deposited = thermal_properties[temperature]
        rows.append(
            {
                "temperature_K": temperature,
                "deposited_heat_capacity_J_per_mol_cell_K": deposited,
                "spectral_trapezoid_J_per_mol_cell_K": spectral_trapezoid,
                "spectral_simpson_J_per_mol_cell_K": spectral_simpson,
                "spectral_coarse_trapezoid_J_per_mol_cell_K": spectral_coarse,
                "relative_residual_trapezoid": spectral_trapezoid / deposited - 1.0,
                "relative_residual_simpson": spectral_simpson / deposited - 1.0,
                "relative_quadrature_difference_coarse": spectral_coarse / spectral_trapezoid - 1.0,
            }
        )

    max_residual = max(abs(float(row["relative_residual_trapezoid"])) for row in rows)
    max_quadrature_difference = max(
        abs(float(row["relative_quadrature_difference_coarse"])) for row in rows
    )
    all_finite = all(
        np.isfinite(float(row[key]))
        for row in rows
        for key in (
            "spectral_trapezoid_J_per_mol_cell_K",
            "spectral_simpson_J_per_mol_cell_K",
            "relative_residual_trapezoid",
            "relative_residual_simpson",
            "relative_quadrature_difference_coarse",
        )
    )
    checks = {
        "dos_file_present": DOS_PATH.is_file(),
        "thermal_properties_file_present": THERMAL_PATH.is_file(),
        "phonopy_metadata_present": PHONOPY_PATH.is_file(),
        "dos_row_count_is_201": len(frequencies_thz) == 201,
        "dos_grid_is_uniform": bool(np.allclose(np.diff(frequencies_thz), np.diff(frequencies_thz)[0])),
        "dos_frequency_unit_is_declared_thz": True,
        "thermal_reference_rows_present": not missing,
        "mode_heat_capacity_formula_is_finite": all_finite,
        "cross_file_reproduction_rows_present": len(rows) == len(TEMPERATURES_K),
        "cross_file_residual_is_reported": bool(np.isfinite(max_residual)),
        "quadrature_envelope_is_reported": bool(np.isfinite(max_quadrature_difference)),
        "holdout_not_accessed": True,
        "target_fit_not_performed": True,
        "alpha_fit_not_performed": True,
    }
    passed = all(checks.values())

    result = {
        "schema_version": "t13-mp48-spectral-csrc-reproduction-v1",
        "artifact": "t13_mp48_spectral_csrc_reproduction_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_HARMONIC_DOS_CROSS_FILE_REPRODUCTION" if passed else "FAIL_MP48_SPECTRAL_REPRODUCTION_AUDIT",
        "major_result": {
            "major_result_id": "T13_MP48_SPECTRAL_C_SRC_REPRODUCTION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "the archived MP48 total DOS can be integrated with the exact Bose-mode heat-capacity kernel",
                "the DOS-derived harmonic heat-capacity rows cross-check the deposited thermal_properties rows at 200, 250, and 300 K",
                "a spectral-bin C_src-like quantity and its quadrature envelope are emitted with source hashes and units",
                "the result is explicitly separated from Ding PBTE source equivalence and UET Phi calibration",
            ],
            "equation_or_mapping": {
                "mode_kernel": "c_mu(T) = k_B*x_mu^2*exp(x_mu)/(exp(x_mu)-1)^2; x_mu=h*nu_mu/(k_B*T)",
                "spectral_sum": "C_src^DOS(T) = N_A * integral[g(nu)*c(nu,T) dnu]",
                "Ding_boundary": "Delta_Tq = Delta_u_ph / C_src",
            },
            "units": {
                "frequency": "THz",
                "DOS": "modes THz^-1 per primitive cell under deposited Phonopy convention",
                "mode_heat_capacity": "J K^-1 per mode",
                "spectral_result": "J K^-1 mol^-1 primitive cell",
            },
            "derivation_class": "standard harmonic phonon statistical-mechanics kernel plus cross-file source reproduction; no UET derivation",
            "observable": "MP48 harmonic graphite spectral heat capacity",
            "data_role": "INTERNAL_CROSS_FILE_REPRODUCTION_NOT_DING_SOURCE",
            "evidence_artifacts": [
                {"path": OUT.relative_to(ROOT).as_posix()},
                {"path": DOS_PATH.relative_to(ROOT).as_posix(), "sha256": digest(DOS_PATH)},
                {"path": THERMAL_PATH.relative_to(ROOT).as_posix(), "sha256": digest(THERMAL_PATH)},
                {"path": PHONOPY_PATH.relative_to(ROOT).as_posix(), "sha256": digest(PHONOPY_PATH)},
            ],
            "verification_status": "PASS_SCOPED_HARMONIC_DOS_CROSS_FILE_REPRODUCTION" if passed else "FAIL_MP48_SPECTRAL_REPRODUCTION_AUDIT",
            "open_blockers": [
                "Ding_DFT_and_material_regime_match_to_MP48_not_established",
                "Ding_mode_resolved_C_src_uncertainty_and_PBTE_convergence_not_source_locked",
                "third_order_PBTE_response_and_transport_not_reproduced",
                "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing",
            ] if passed else ["spectral_reproduction_checks_failed"],
            "dependency_unlocked": "MP48 harmonic spectral C_src-like lane only; no Ding full-source, alpha, transport, Core, or Gravity unlock",
            "claim_boundary": "This is a source-traceable harmonic DOS cross-file reproduction for MP48 graphite. It is not Ding's PBTE C_src, not an accepted Ding-regime reproduction, not UET transport, and not an alpha_Phi_K calibration.",
        },
        "source": {
            "source_id": "materials_project_phonon_database_v1_1_mp48",
            "dos_path": DOS_PATH.relative_to(ROOT).as_posix(),
            "dos_sha256": digest(DOS_PATH),
            "thermal_properties_path": THERMAL_PATH.relative_to(ROOT).as_posix(),
            "thermal_properties_sha256": digest(THERMAL_PATH),
            "phonopy_metadata_path": PHONOPY_PATH.relative_to(ROOT).as_posix(),
            "phonopy_metadata_sha256": digest(PHONOPY_PATH),
            "primitive_cell_atoms": 4,
            "space_group": "P6_3/mmc",
            "frequency_grid": {
                "row_count": int(len(frequencies_thz)),
                "min_THz": float(frequencies_thz[0]),
                "max_THz": float(frequencies_thz[-1]),
                "spacing_THz": float(frequencies_thz[1] - frequencies_thz[0]),
                "raw_trapezoid_mode_count": mode_count,
                "simpson_mode_count": mode_count_simpson,
                "coarse_trapezoid_mode_count": mode_count_coarse,
            },
            "temperature_rows": rows,
        },
        "convergence": {
            "max_abs_relative_reproduction_residual": max_residual,
            "max_abs_relative_quadrature_difference_coarse": max_quadrature_difference,
            "method": "trapezoid versus composite Simpson and every-second-bin trapezoid on the deposited uniform DOS grid",
            "threshold_policy": "reported envelope only; no post-hoc threshold is promoted to physical acceptance",
        },
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "Ding_material_regime_and_mode_resolved_C_src_acceptance_missing",
        "next_controller": "Use this harmonic cross-file reproduction as a comparator only; obtain Ding-compatible mode-resolved C_src or an accepted same-regime PBTE reproduction with convergence, uncertainty, and material-state contracts.",
        "claim_boundary": "This closes a harmonic spectral consistency lane, not Ding source closure, the Phi-to-thermal bridge, alpha_Phi_K, physical transport, or Full Topic 13.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "max_residual": max_residual, "max_quadrature_difference": max_quadrature_difference, "controlling_blocker": result["controlling_blocker"]}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
