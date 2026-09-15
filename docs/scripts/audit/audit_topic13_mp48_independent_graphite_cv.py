"""Audit the independent mp-48 graphite harmonic heat-capacity route."""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment diagnosis
    raise SystemExit("PyYAML is required for the mp-48 source audit") from exc


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "mp48_independent_graphite_cv_source_package.json"
)
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_independent_graphite_cv_audit.json"
AVOGADRO = 6.02214076e23


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def load_gzip_json(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def load_gzip_yaml(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected YAML object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a: float, b: float, rel: float = 1.0e-11) -> bool:
    return math.isclose(float(a), float(b), rel_tol=rel, abs_tol=1.0e-12)


def relative_difference(a: float, b: float) -> float:
    return abs(float(a) - float(b)) / float(b)


def main() -> int:
    package = load_json(PACKAGE)
    raw_dir = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw"
    summary_path = raw_dir / "mp48_summary.json.gz"
    thermal_path = raw_dir / "mp48_thermal_properties.yaml.gz"
    summary = load_gzip_json(summary_path)
    thermal = load_gzip_yaml(thermal_path)

    member_checks: dict[str, bool] = {}
    member_records: list[dict] = []
    for member in package["archive_members"]:
        path = ROOT / member["local_path"]
        digest = sha256(path) if path.is_file() else None
        actual_size = path.stat().st_size if path.is_file() else None
        magic = path.read_bytes()[:2] == b"\x1f\x8b" if path.is_file() else False
        key = member["member"]
        member_checks[f"{key}_present"] = path.is_file()
        member_checks[f"{key}_bytes_match"] = actual_size == member["size_bytes"]
        member_checks[f"{key}_sha256_match"] = digest == member["sha256"]
        member_checks[f"{key}_gzip_magic"] = magic
        member_records.append(
            {
                "member": key,
                "path": member["local_path"],
                "bytes": actual_size,
                "sha256": digest,
                "expected_sha256": member["sha256"],
                "tar_header_offset": member["tar_header_offset"],
                "data_offset": member["data_offset"],
            }
        )

    temperatures = [float(value) for value in thermal.get("temperatures", [])]
    heat_capacity = [float(value) for value in thermal.get("heat_capacity", [])]
    grid = dict(zip(temperatures, heat_capacity))
    representative = package["representative_rows"]
    volume = package["experimental_volume_anchor"]
    molar_volume = float(volume["volume_per_cell_A3"]) * 1.0e-30 * AVOGADRO

    row_checks: dict[str, bool] = {}
    derived_records: list[dict] = []
    for row in representative:
        temperature = float(row["temperature_K"])
        expected_molar = float(row["heat_capacity_J_per_mol_cell_K"])
        expected_volumetric = float(row["volumetric_cv_J_per_m3_K"])
        if row["row_identity"] == "source_grid":
            actual_molar = grid.get(temperature)
        elif temperature == 125.0:
            actual_molar = (grid[120.0] + grid[130.0]) / 2.0
        elif temperature == 225.0:
            actual_molar = (grid[220.0] + grid[230.0]) / 2.0
        else:
            actual_molar = None
        actual_volumetric = (
            actual_molar / molar_volume if actual_molar is not None else None
        )
        key = str(int(temperature))
        row_checks[f"row_{key}_molar_matches"] = actual_molar is not None and close(actual_molar, expected_molar)
        row_checks[f"row_{key}_volumetric_matches"] = actual_volumetric is not None and close(actual_volumetric, expected_volumetric)
        derived_records.append(
            {
                "temperature_K": temperature,
                "row_identity": row["row_identity"],
                "source_heat_capacity_J_per_mol_cell_K": actual_molar,
                "derived_volumetric_cv_J_per_m3_K": actual_volumetric,
            }
        )

    comparator_checks: dict[str, bool] = {}
    residual_records: list[dict] = []
    for row in package["independent_comparator"]["rows"]:
        temperature = float(row["temperature_K"])
        source_molar = grid[temperature] / 4.0
        residual = relative_difference(source_molar, row["nist_cp_J_per_mol_atom_K"])
        comparator_checks[f"janaf_{int(temperature)}K_matches"] = close(
            source_molar, row["mp48_cv_J_per_mol_atom_K"]
        ) and close(residual, row["relative_difference"], rel=1.0e-9)
        residual_records.append(
            {
                "temperature_K": temperature,
                "mp48_cv_J_per_mol_atom_K": source_molar,
                "nist_cp_J_per_mol_atom_K": row["nist_cp_J_per_mol_atom_K"],
                "relative_difference": residual,
            }
        )
    max_residual = max(item["relative_difference"] for item in residual_records)

    checks = {
        **member_checks,
        **row_checks,
        **comparator_checks,
        "package_status_is_lane_source": package["status"] == "SOURCE_LOCKED_INDEPENDENT_HARMONIC_CV_COMPARATOR",
        "summary_mp_id": summary.get("mp_id") == "mp-48",
        "summary_formula": summary.get("formula_pretty") == "C",
        "summary_primitive_atoms": summary.get("nsites") == 4,
        "summary_supercell_atoms": summary.get("nsites_supercell") == 200,
        "summary_space_group": summary.get("symmetry", {}).get("symbol") == "P6_3/mmc",
        "summary_stable": summary.get("has_imaginary_modes") is False and summary.get("predicted_phonon_stable") is True,
        "summary_grid_is_10K": temperatures == list(range(0, 1001, 10)),
        "thermal_arrays_same_length": len(temperatures) == len(heat_capacity) == 101,
        "thermal_unit_contract_explicit": package["unit_contract"]["thermal_source_units"] == "J K^-1 mol^-1 primitive cell",
        "volume_conversion_matches": close(molar_volume, volume["molar_primitive_cell_volume_m3_per_mol"], rel=1.0e-12),
        "volume_relative_uncertainty_matches": close(
            float(volume["uncertainty_per_cell_A3"]) / float(volume["volume_per_cell_A3"]),
            volume["relative_uncertainty"],
            rel=1.0e-10,
        ),
        "janaf_envelope_matches": close(max_residual, package["independent_comparator"]["maximum_relative_difference"], rel=1.0e-9),
        "uncertainty_not_mislabeled_statistical": package["uncertainty_contract"]["combined_envelope_status"] == "NON_STATISTICAL_DISPLAY_ONLY",
        "source_volume_not_used": "source volume is not used" in package["material"]["source_volume_warning"].lower(),
        "not_cp_to_cv_correction": package["unit_contract"]["no_Cp_to_Cv_correction"] is True,
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False,
        "holdout_not_consumed": package["holdout_policy"]["xie_2026_source_data_consumed"] is False,
        "target_curve_not_used": package["holdout_policy"]["target_curve_used"] is False,
        "alpha_fit_not_used": package["holdout_policy"]["alpha_fit_used"] is False,
    }
    status = (
        "PASS_INDEPENDENT_NUMERIC_CV_WITH_EPISTEMIC_ENVELOPE"
        if all(checks.values())
        else "FAIL_MP48_INDEPENDENT_CV_AUDIT"
    )
    report = {
        "schema_version": "t13-mp48-independent-graphite-cv-audit-v1",
        "artifact": "t13_mp48_independent_graphite_cv_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_MP48_INDEPENDENT_GRAPHITE_CV_REPRODUCTION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": "Independent mp-48 harmonic graphite heat-capacity rows, exact local raw hashes, archive byte locators, experimental-volume conversion, representative volumetric c_v values, and a separate JANAF comparison envelope are reproducibly checked.",
            "equation_or_mapping": "C_v^vol(T) = C_v^mol,cell(T) / V_mol,cell; Delta_Tq = Delta_u / C_v^vol",
            "units": {
                "source": "J K^-1 mol^-1 primitive cell",
                "derived": "J m^-3 K^-1",
                "volume": "m^3 mol^-1 primitive cell",
            },
            "derivation_class": "source extraction and standard unit conversion; no UET derivation",
            "observable": "independent harmonic graphite heat-capacity comparator",
            "data_role": "INDEPENDENT_REPRODUCTION_NOT_CALIBRATION",
            "evidence_artifacts": [
                {"path": str(PACKAGE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(PACKAGE)},
                {"path": "docs/core/07_artifacts/topic13/t13_mp48_independent_graphite_cv_audit.json"},
            ],
            "verification_status": status,
            "open_blockers": package["major_result"]["open_blockers"],
            "dependency_unlocked": package["major_result"]["dependency_unlocked"],
            "claim_boundary": package["claim_boundary"],
        },
        "source_identity": {
            "source_id": package["source"]["source_id"],
            "doi": package["source"]["doi"],
            "archive": package["source"]["archive"],
            "member_records": member_records,
        },
        "summary_identity": {
            "mp_id": summary.get("mp_id"),
            "formula": summary.get("formula_pretty"),
            "primitive_cell_atoms": summary.get("nsites"),
            "supercell_atoms": summary.get("nsites_supercell"),
            "space_group": summary.get("symmetry", {}).get("symbol"),
            "has_imaginary_modes": summary.get("has_imaginary_modes"),
            "debye_temperature_K": summary.get("debye_temperature"),
        },
        "derived_records": derived_records,
        "comparator_records": residual_records,
        "checks": checks,
        "controlling_blocker": "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing",
        "next_controller": "Derive or independently source-lock e0 and the base Phi-to-Delta_u_ph correspondence without reading Xie 2026; then report alpha_Phi_K uncertainty. Keep this mp-48 route as an independent comparator, not as a fitted calibration.",
        "claim_boundary": package["claim_boundary"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"), "failed_checks": [key for key, value in checks.items() if not value]}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
