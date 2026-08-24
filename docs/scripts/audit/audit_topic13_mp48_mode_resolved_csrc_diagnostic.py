"""Build a mode-resolved MP48 harmonic C_src diagnostic package.

The package is derived from the locally hash-locked MP48 force constants.  It
is useful for row-level reproducibility, but it is not Ding PBTE acceptance:
third-order transport, material-state equivalence, and source-grade
uncertainty remain explicit blockers.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw"
PACKAGE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/mp48_independent_graphite_cv_source_package.json"
FORCE_CONSTANTS = RAW / "mp48_FORCE_CONSTANTS.gz"
PHONOPY_METADATA = RAW / "mp48_phonopy.yaml.gz"
THERMAL_PROPERTIES = RAW / "mp48_thermal_properties.yaml.gz"
NPZ_OUT = ROOT / "docs/core/artifacts/t13_mp48_mode_resolved_csrc_diagnostic.npz"
JSON_OUT = ROOT / "docs/core/artifacts/t13_mp48_mode_resolved_csrc_diagnostic.json"

AVOGADRO = 6.02214076e23
PLANCK = 6.62607015e-34
BOLTZMANN = 1.380649e-23
MESH = (35, 35, 14)
TEMPERATURES = (100.0, 200.0, 250.0, 300.0)
AGGREGATE_RELATIVE_TOLERANCE = 1.0e-5


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def load_thermal_rows(path: Path) -> dict[float, float]:
    import re

    text = gzip.open(path, "rt", encoding="utf-8").read()
    rows = re.findall(
        r"- temperature:\s*([0-9.]+)\s*\n"
        r"\s+free_energy:\s*[^\n]+\n"
        r"\s+entropy:\s*[^\n]+\n"
        r"\s+heat_capacity:\s*([0-9.eE+-]+)",
        text,
    )
    return {float(temperature): float(capacity) for temperature, capacity in rows}


def mode_capacity(frequency_thz: np.ndarray, temperature_K: float) -> np.ndarray:
    x = PLANCK * np.abs(frequency_thz) * 1.0e12 / (BOLTZMANN * temperature_K)
    output = np.empty_like(x, dtype=float)
    small = np.abs(x) < 1.0e-7
    output[small] = BOLTZMANN
    regular = ~small
    exponent = np.exp(np.clip(x[regular], -700.0, 700.0))
    output[regular] = (
        BOLTZMANN
        * x[regular] ** 2
        * exponent
        / (exponent - 1.0) ** 2
    )
    return output


def load_phonopy():
    try:
        from phonopy import load
    except ImportError as exc:  # pragma: no cover - environment diagnosis
        raise SystemExit("phonopy is required for the MP48 mode diagnostic") from exc

    with tempfile.TemporaryDirectory(prefix="t13_mp48_mode_") as directory:
        work = Path(directory)
        metadata = work / "phonopy.yaml"
        force_constants = work / "FORCE_CONSTANTS"
        metadata.write_bytes(gzip.open(PHONOPY_METADATA, "rb").read())
        force_constants.write_bytes(gzip.open(FORCE_CONSTANTS, "rb").read())
        return load(str(metadata), force_constants_filename=str(force_constants))


def main() -> int:
    package = load_json(PACKAGE)
    phonopy = load_phonopy()
    mesh = phonopy.run_mesh(
        MESH,
        is_mesh_symmetry=False,
        is_time_reversal=False,
        with_eigenvectors=False,
    )
    qpoints = np.asarray(mesh.qpoints, dtype=float)
    weights = np.asarray(mesh.weights, dtype=np.int64)
    frequencies = np.asarray(mesh.frequencies, dtype=float)
    if frequencies.ndim != 2:
        raise ValueError(f"expected q-point by mode frequencies, got {frequencies.shape}")

    volume = float(
        package["experimental_volume_anchor"]["molar_primitive_cell_volume_m3_per_mol"]
    )
    if not np.isfinite(volume) or volume <= 0.0:
        raise ValueError("MP48 volume anchor must be finite and positive")

    mode_capacity_rows: dict[str, np.ndarray] = {}
    aggregate_rows: list[dict[str, float]] = []
    deposited = load_thermal_rows(THERMAL_PROPERTIES)
    total_weight = int(np.sum(weights))
    for temperature in TEMPERATURES:
        per_mode_molar = mode_capacity(frequencies, temperature) * AVOGADRO
        per_mode_volumetric = per_mode_molar / volume
        mode_capacity_rows[str(int(temperature))] = per_mode_volumetric
        aggregate_molar = float(
            np.sum(weights[:, None] * per_mode_molar) / total_weight
        )
        aggregate_volumetric = aggregate_molar / volume
        deposited_value = deposited.get(temperature)
        relative_difference = (
            abs(aggregate_molar - deposited_value) / abs(deposited_value)
            if deposited_value is not None and deposited_value != 0.0
            else None
        )
        aggregate_rows.append(
            {
                "temperature_K": temperature,
                "C_src_harmonic_J_per_mol_cell_K": aggregate_molar,
                "C_src_harmonic_J_per_m3_K": aggregate_volumetric,
                "deposited_C_v_J_per_mol_cell_K": deposited_value,
                "relative_difference_to_deposited": relative_difference,
            }
        )

    np.savez_compressed(
        NPZ_OUT,
        qpoints=qpoints,
        weights=weights,
        frequencies_THz=frequencies,
        **{f"c_mu_J_per_m3_K_{temperature}": values for temperature, values in mode_capacity_rows.items()},
    )

    checks = {
        "source_force_constants_hash_matches_package": digest(FORCE_CONSTANTS)
        == next(
            item["sha256"]
            for item in package["archive_members"]
            if item["member"] == "mp-48/FORCE_CONSTANTS.gz"
        ),
        "source_phonopy_hash_matches_package": digest(PHONOPY_METADATA)
        == next(
            item["sha256"]
            for item in package["archive_members"]
            if item["member"] == "mp-48/phonopy.yaml.gz"
        ),
        "mesh_shape_is_declared": tuple(qpoints.shape) == (np.prod(MESH), 3),
        "mode_count_is_12": frequencies.shape[1] == 12,
        "weights_are_positive": bool(np.all(weights > 0)),
        "frequencies_are_finite": bool(np.isfinite(frequencies).all()),
        "no_negative_modes_beyond_roundoff": float(np.min(frequencies)) >= -1.0e-7,
        "mode_rows_are_finite": all(
            bool(np.isfinite(values).all()) for values in mode_capacity_rows.values()
        ),
        "aggregate_rows_are_finite": all(
            np.isfinite(row["C_src_harmonic_J_per_m3_K"])
            for row in aggregate_rows
        ),
        "deposited_comparison_is_within_declared_diagnostic_tolerance": all(
            row["relative_difference_to_deposited"] is not None
            and row["relative_difference_to_deposited"]
            <= AGGREGATE_RELATIVE_TOLERANCE
            for row in aggregate_rows
        ),
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False,
        "target_fit_not_performed": package["holdout_policy"]["target_curve_used"] is False,
        "alpha_fit_not_performed": package["holdout_policy"]["alpha_fit_used"] is False,
    }
    status = (
        "PASS_MP48_MODE_RESOLVED_DERIVED_COMPARISON"
        if all(checks.values())
        else "BLOCKED_MP48_MODE_RESOLVED_DERIVED_COMPARISON"
    )
    report = {
        "schema_version": "t13-mp48-mode-resolved-csrc-diagnostic-v1",
        "artifact": "t13_mp48_mode_resolved_csrc_diagnostic",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_MP48_MODE_RESOLVED_CSRC_DERIVED_COMPARISON",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "a row-addressable mode-resolved harmonic c_mu(T) array is derived from the local MP48 force constants",
                "the mode sum is converted to volumetric C_src units using the locked graphite volume anchor",
                "the aggregate rows reproduce the deposited MP48 harmonic heat-capacity rows within the declared diagnostic tolerance",
            ],
            "equation_or_mapping": {
                "mode_capacity": "c_mu(T) = k_B*x_mu^2*exp(x_mu)/(exp(x_mu)-1)^2",
                "mode_sum": "C_src^vol(T) = N_A/(N_q V_mol) * sum_(q,mu) c_mu(q,T)",
                "row_identity": "mesh35x35x14:q_index:mode_index:temperature_K",
            },
            "units": {
                "frequency": "THz",
                "mode_capacity": "J m^-3 K^-1",
                "aggregate_capacity": "J m^-3 K^-1",
                "temperature": "K",
            },
            "derivation_class": "derived harmonic lattice-dynamics comparator from source-locked force constants; no UET derivation",
            "observable": "mode-resolved and aggregate harmonic graphite C_src comparator",
            "data_role": "DERIVED_COMPARISON",
            "evidence_artifacts": [
                {"path": "docs/core/artifacts/t13_mp48_mode_resolved_csrc_diagnostic.npz", "sha256": digest(NPZ_OUT)},
                {"path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/mp48_independent_graphite_cv_source_package.json", "sha256": digest(PACKAGE)},
                {"path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/mp48_FORCE_CONSTANTS.gz", "sha256": digest(FORCE_CONSTANTS)},
                {"path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/mp48_phonopy.yaml.gz", "sha256": digest(PHONOPY_METADATA)},
            ],
            "verification_status": status,
            "open_blockers": [
                "third_order_PBTE_transport_and_Ding_material_state_equivalence_missing",
                "source_grade_uncertainty_missing",
                "base_Phi_to_energy_anchor_and_independent_alpha_Phi_K_missing",
            ],
            "dependency_unlocked": "Only a row-level harmonic comparator route; no Ding source, alpha, Full Topic 13, or downstream unlock.",
            "claim_boundary": "This derived diagnostic is not Ding PBTE C_src acceptance, not a source-grade uncertainty package, not a Phi calibration, and not a TTG prediction.",
        },
        "source": {
            "source_id": package["source"]["source_id"],
            "force_constants_path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/mp48_FORCE_CONSTANTS.gz",
            "force_constants_sha256": digest(FORCE_CONSTANTS),
            "phonopy_metadata_path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/mp48_phonopy.yaml.gz",
            "phonopy_metadata_sha256": digest(PHONOPY_METADATA),
            "source_package_sha256": digest(PACKAGE),
            "mesh": list(MESH),
            "q_point_count": int(qpoints.shape[0]),
            "mode_count": int(frequencies.shape[1]),
        },
        "derived_payload": {
            "path": "docs/core/artifacts/t13_mp48_mode_resolved_csrc_diagnostic.npz",
            "sha256": digest(NPZ_OUT),
            "format": "NumPy compressed archive",
            "arrays": [
                "qpoints[n_q,3]",
                "weights[n_q]",
                "frequencies_THz[n_q,12]",
                "c_mu_J_per_m3_K_{100,200,250,300}[n_q,12]",
            ],
            "row_identity": "mesh35x35x14:q_index:mode_index:temperature_K",
            "uncertainty_status": "NOT_SOURCE_GRADE",
            "material_mapping_status": "OPEN",
        },
        "aggregate_rows": aggregate_rows,
        "checks": checks,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
        "controlling_blocker": "third_order_PBTE_transport_and_Ding_material_state_equivalence_missing",
        "next_controller": "Use this row-level diagnostic to support an independently accepted same-regime PBTE package only if third-order transport, material state, convergence, permission, and source-grade uncertainty are separately supplied.",
        "claim_boundary": "Derived harmonic comparison only; it does not promote MP48 to Ding C_src or close Topic 13.",
    }
    JSON_OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": "docs/core/artifacts/t13_mp48_mode_resolved_csrc_diagnostic.json",
                "payload": "docs/core/artifacts/t13_mp48_mode_resolved_csrc_diagnostic.npz",
                "q_point_count": int(qpoints.shape[0]),
                "mode_count": int(frequencies.shape[1]),
                "failed_checks": [key for key, value in checks.items() if not value],
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
