"""Audit the source-locked legacy-NEP2 PBTE reproduction lane for Topic 13."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
TOPIC = "docs/topics/0.13_Thermodynamic_Bridge"
DATA = f"{TOPIC}/Data/03_Research"
ARCHIVE = f"{DATA}/reproduction/t13_calorine_legacy_nep2_cx"
PACKAGE_REL = f"{DATA}/calorine_legacy_nep2_pbte_reproduction_source_package.json"
AUDIT_REL = "docs/core/artifacts/t13_calorine_legacy_nep2_pbte_reproduction_audit.json"
WRAPPER_REL = "docs/scripts/audit/run_topic13_calorine_legacy_pbte_reproduction.py"
RECEIPT_REL = f"{DATA}/raw/calorine_legacy_nep2_backend_probe_receipt.txt"
STRUCTURE_REL = f"{DATA}/raw/calorine_zenodo_7811021_nep_C_CX/graphite-prim.xyz"
POTENTIAL_REL = f"{DATA}/raw/calorine_zenodo_7811021_nep_C_CX/nep-C.txt"
MODEL_SHA256 = "cf75256947a8953b8041ccc26a34ac307724f69bf2edbcc97b46d87bc5e72408"
STRUCTURE_SHA256 = "87fdd172bd5b77e1aa5bd9b4d85c3f21eb5df6521089cc4b769e12d481a1aed0"
LEGACY_COMMIT = "eedb2ac9f49cb60a64512e987b98993d3a44e186"
LEGACY_TAG = "1.0"
LEGACY_NEP_CPP_SHA256 = "433a919d15b320d8d301f8b7c345762cbf4a2bd99133521a94470f8df8a2ddb3"
LEGACY_NEP_H_SHA256 = "44a9eb6adb871b5f0e7af89b0d5ac79481f1c0c0032813f90177153983c6ddf7"
LEGACY_NEPY_CPP_SHA256 = "352eb19fd4a521395ecd25087b346293f14fcd99edc27e3b89f70ab7605e3e51"
EXPECTED_MODEL_HEADER = "nep 1 C"
CONVERGENCE_TOLERANCE = 0.01


def path(relative: str) -> Path:
    return ROOT / relative


def load(relative: str) -> dict[str, Any]:
    value = json.loads(path(relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def digest(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def record(relative: str, locator: str | None = None) -> dict[str, Any]:
    file_path = path(relative)
    return {
        "path": file_path.relative_to(ROOT).as_posix(),
        "size_bytes": file_path.stat().st_size,
        "sha256": digest(file_path),
        "locator": locator,
    }


def relative_change(previous: float, current: float) -> float:
    denominator = abs(current)
    if denominator == 0.0:
        return 0.0 if previous == 0.0 else float("inf")
    return abs(current - previous) / denominator


def poscar_geometry(file_path: Path) -> tuple[int, float]:
    """Read the atom count and cell volume without treating formatting as state."""

    lines = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines()]
    if len(lines) < 8:
        raise SystemExit(f"invalid POSCAR: {file_path}")
    scale = float(lines[1])
    cell = [[float(value) * scale for value in lines[index].split()[:3]] for index in range(2, 5)]
    counts_index = 5
    try:
        counts = [int(value) for value in lines[counts_index].split()]
    except ValueError:
        counts_index = 6
        counts = [int(value) for value in lines[counts_index].split()]
    ax, ay, az = cell
    volume = abs(
        ax[0] * (ay[1] * az[2] - ay[2] * az[1])
        - ax[1] * (ay[0] * az[2] - ay[2] * az[0])
        + ax[2] * (ay[0] * az[1] - ay[1] * az[0])
    )
    return sum(counts), volume


def find_row(rows: list[dict[str, Any]], temperature: float) -> dict[str, Any]:
    for row in rows:
        if float(row.get("temperature_K")) == temperature:
            return row
    raise KeyError(f"missing C_src row at {temperature} K")


def run_record(label: str, summary_rel: str, kappa_rel: str, expected_mesh: list[int]) -> dict[str, Any]:
    summary = load(summary_rel)
    run = summary.get("run", {})
    geometry = summary.get("geometry", {})
    force = summary.get("force_constant_summary", {})
    rows = summary.get("c_src_rows", [])
    if summary.get("schema_version") != "t13-calorine-pbte-csrc-run-v1":
        raise SystemExit(f"unexpected summary schema: {summary_rel}")
    if run.get("dim") != [4, 4, 2] or run.get("mesh") != expected_mesh:
        raise SystemExit(f"unexpected state/grid in {summary_rel}")
    if run.get("temperatures_K") != [200.0, 300.0]:
        raise SystemExit(f"unexpected temperature grid in {summary_rel}")
    if run.get("transport_solver") != "RTA":
        raise SystemExit(f"unexpected transport solver in {summary_rel}")
    if not rows or any(
        not math.isfinite(float(row["C_src_J_m^-3_K^-1"]))
        or float(row["C_src_J_m^-3_K^-1"]) <= 0.0
        for row in rows
    ):
        raise SystemExit(f"missing or invalid C_src rows: {summary_rel}")
    if not path(kappa_rel).is_file() or path(kappa_rel).stat().st_size <= 0:
        raise SystemExit(f"missing kappa payload: {kappa_rel}")
    force_hashes = {
        name: force.get(name, {}).get("sha256")
        for name in ("poscar", "fc2", "fc3")
    }
    return {
        "label": label,
        "summary": record(summary_rel),
        "mesh": run["mesh"],
        "temperatures_K": run["temperatures_K"],
        "q_point_count": geometry.get("q_point_count"),
        "q_weight_sum": geometry.get("q_weight_sum"),
        "primitive_volume_A3": geometry.get("primitive_volume_A3"),
        "mode_count": geometry.get("mode_count"),
        "frequency_range_THz": geometry.get("frequency_range_THz"),
        "c_src_rows": rows,
        "kappa": record(kappa_rel),
        "force_constant_hashes": force_hashes,
        "fit_performed": bool(run.get("fit_performed")),
        "target_curve_used": bool(run.get("target_curve_used")),
        "alpha_Phi_K_fit_performed": bool(run.get("alpha_Phi_K_fit_performed")),
        "holdout_accessed": bool(run.get("holdout_accessed")),
    }


def build_convergence(runs: list[dict[str, Any]]) -> dict[str, Any]:
    previous, current = runs
    if previous["temperatures_K"] != current["temperatures_K"]:
        raise SystemExit("temperature grids differ across mesh runs")
    rows = []
    for previous_row, current_row in zip(previous["c_src_rows"], current["c_src_rows"], strict=True):
        if previous_row["temperature_K"] != current_row["temperature_K"]:
            raise SystemExit("temperature row identity changed across mesh runs")
        previous_value = float(previous_row["C_src_J_m^-3_K^-1"])
        current_value = float(current_row["C_src_J_m^-3_K^-1"])
        rows.append(
            {
                "temperature_K": current_row["temperature_K"],
                "previous_C_src_J_m^-3_K^-1": previous_value,
                "current_C_src_J_m^-3_K^-1": current_value,
                "relative_change": relative_change(previous_value, current_value),
            }
        )
    max_change = max(float(row["relative_change"]) for row in rows)
    return {
        "criterion": "latest adjacent mesh relative change <= 0.01 for every reported temperature; candidate numerical preflight only",
        "declared_tolerance": CONVERGENCE_TOLERANCE,
        "from_mesh": previous["mesh"],
        "to_mesh": current["mesh"],
        "rows": rows,
        "max_relative_change": max_change,
        "latest_pair_pass": max_change <= CONVERGENCE_TOLERANCE,
        "scope": "q-mesh convergence at fixed 4x4x2 force-constant state and fixed RTA solver; not Ding source acceptance",
    }


def main() -> int:
    structure = path(STRUCTURE_REL)
    potential = path(POTENTIAL_REL)
    receipt = path(RECEIPT_REL)
    wrapper = path(WRAPPER_REL)
    state_summary_rel = f"{ARCHIVE}/state_4x4x2/run_summary.json"
    state_poscar_rel = f"{ARCHIVE}/state_4x4x2/POSCAR"
    state_fc2_rel = f"{ARCHIVE}/state_4x4x2/fc2.hdf5"
    state_fc3_rel = f"{ARCHIVE}/state_4x4x2/fc3.hdf5"
    runs = [
        run_record(
            "8x8x4",
            f"{ARCHIVE}/mesh_8x8x4/csrc_summary.json",
            f"{ARCHIVE}/mesh_8x8x4/kappa-m884.hdf5",
            [8, 8, 4],
        ),
        run_record(
            "10x10x5",
            f"{ARCHIVE}/mesh_10x10x5/csrc_summary.json",
            f"{ARCHIVE}/mesh_10x10x5/kappa-m10105.hdf5",
            [10, 10, 5],
        ),
    ]
    state_summary = load(state_summary_rel)
    force = state_summary.get("force_constant_summary", {})
    convergence = build_convergence(runs)
    force_records = {
        "poscar": record(state_poscar_rel),
        "fc2": record(state_fc2_rel),
        "fc3": record(state_fc3_rel),
    }
    all_no_fit = all(
        not run["fit_performed"]
        and not run["target_curve_used"]
        and not run["alpha_Phi_K_fit_performed"]
        and not run["holdout_accessed"]
        for run in runs
    )
    expected_force_hashes = {
        name: item["sha256"] for name, item in force_records.items()
    }
    poscar_atom_count, poscar_volume = poscar_geometry(path(state_poscar_rel))
    expected_volume = float(
        state_summary.get("geometry", {}).get(
            "primitive_volume_A3", runs[0]["primitive_volume_A3"]
        )
    )
    poscar_state_contract_valid = (
        poscar_atom_count == 4
        and expected_volume > 0.0
        and math.isclose(poscar_volume, expected_volume, rel_tol=0.0, abs_tol=1e-9)
    )
    source_hashes_match = digest(structure) == STRUCTURE_SHA256 and digest(potential) == MODEL_SHA256
    header_matches = potential.read_text(encoding="utf-8").splitlines()[0].strip() == EXPECTED_MODEL_HEADER
    receipt_contract = receipt.read_text(encoding="utf-8").lower()
    legacy_backend_receipt = (
        f"source_commit: {LEGACY_COMMIT}" in receipt.read_text(encoding="utf-8")
        and "returncode: 0" in receipt_contract
        and "use the nep2 potential" in receipt_contract
    )
    same_force_state = poscar_state_contract_valid and all(
        run["force_constant_hashes"].get(name) == expected_force_hashes[name]
        for run in runs
        for name in ("fc2", "fc3")
    )
    checks = {
        "structure_source_hash_matches": source_hashes_match and digest(structure) == STRUCTURE_SHA256,
        "potential_source_hash_matches": source_hashes_match and digest(potential) == MODEL_SHA256,
        "legacy_model_header_preserved": header_matches,
        "legacy_backend_receipt_present": receipt.is_file() and legacy_backend_receipt,
        "legacy_backend_source_hashes_declared": all(
            len(value) == 64
            for value in (LEGACY_NEP_CPP_SHA256, LEGACY_NEP_H_SHA256, LEGACY_NEPY_CPP_SHA256)
        ),
        "wrapper_hash_recorded": wrapper.is_file() and len(digest(wrapper)) == 64,
        "state_summary_schema_valid": state_summary.get("schema_version") == "t13-calorine-pbte-csrc-run-v1",
        "state_dim_valid": state_summary.get("run", {}).get("dim") == [4, 4, 2],
        "displacement_contract_valid": force.get("displacement_count") == 1220
        and force.get("supercell_atoms") == 128
        and force.get("force_array_shape") == [1220, 128, 3],
        "force_constant_payloads_present": all(item["size_bytes"] > 0 for item in force_records.values()),
        "poscar_state_contract_valid": poscar_state_contract_valid,
        "same_force_constant_state_across_meshes": same_force_state,
        "mesh_pair_preflight_pass": convergence["latest_pair_pass"],
        "all_c_src_rows_finite_positive": all(
            math.isfinite(float(row["current_C_src_J_m^-3_K^-1"]))
            and float(row["current_C_src_J_m^-3_K^-1"]) > 0.0
            for row in convergence["rows"]
        ),
        "no_fit_target_or_holdout": all_no_fit,
    }
    required = [key for key in checks if key != "no_fit_target_or_holdout"]
    status = (
        "PASS_SCOPED_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION"
        if all(checks[key] for key in required) and checks["no_fit_target_or_holdout"]
        else "FAIL_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION"
    )
    major_result = {
        "major_result_id": "T13_CALORINE_LEGACY_NEP2_PBTE_REPRODUCTION",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
        "what_is_closed": [
            "the hash-locked legacy NEP1 model is evaluated through the pinned Calorine 1.0 NEP2-compatible backend",
            "a fixed 4x4x2 state produces archived fc2/fc3 payloads from 1220 force-displacement calculations",
            "the same force-constant state is rerun at 8x8x4 and 10x10x5 q-meshes",
            "candidate volumetric C_src rows are emitted in J m^-3 K^-1 and the latest mesh pair passes the declared 1% numerical preflight",
            "fit, target-curve tuning, alpha_Phi_K fitting, and Xie 2026 holdout access are absent",
        ],
        "ontology": {
            "C": "collective system-behaviour coordinate; not a heat capacity or mass",
            "Phi": "effective response variable; no Phi mapping is inferred by this lane",
            "R_gen": "derived history trace; no independent dynamics or backreaction is used",
            "R_obs": "observer record kept separate; no observer record is consumed",
        },
        "equation_or_mapping": {
            "mode_to_volumetric": "C_src(T) = [sum_q w_q sum_mu c_qmu(T)] / [sum_q w_q V_primitive]",
            "input_units": "c_qmu(T) in eV K^-1 per mode per primitive cell",
            "si_conversion": "1 eV = 1.602176634e-19 J; 1 A^3 = 1e-30 m^3",
            "future_thermal_bridge": "Delta_Tq = alpha_Phi_K * Delta_Phi remains uninstantiated",
        },
        "units": {
            "C_src": "J m^-3 K^-1",
            "temperature": "K",
            "primitive_volume": "A^3 converted to m^3",
            "transport_output": "W m^-1 K^-1; RTA comparator output only",
        },
        "derivation_class": "EXTERNAL_CANDIDATE_PBTE_REPRODUCTION_NO_UET_DERIVATION",
        "observable": "candidate graphite volumetric phonon heat-capacity response",
        "data_role": "EXTERNAL_CANDIDATE_REPRODUCTION_NOT_CALIBRATION",
        "evidence_artifacts": [],
        "verification_status": status,
        "open_blockers": [
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            "calorine_legacy_pbte_source_grade_uncertainty_missing",
            "calorine_route_material_regime_mapping_to_ding_missing",
            "alpha_Phi_K_independent_calibration_missing",
        ],
        "dependency_unlocked": "candidate C_src reproduction and q-mesh preflight lane only; no Ding acceptance, alpha, bridge, transport, Core, Gravity, or Galaxy unlock",
        "claim_boundary": "This closes only a source-locked legacy-NEP2 harmonic/RTA PBTE candidate reproduction lane. It is not Ding-regime equivalence, not source-grade uncertainty closure, not an alpha_Phi_K calibration, not a UET Phi map, not a TTG prediction, and not Full Topic 13 closure.",
    }
    evidence = [
        record(STRUCTURE_REL, "https://zenodo.org/api/records/7811021/files/graphite-prim.xyz/content"),
        record(POTENTIAL_REL, "https://zenodo.org/api/records/7811021/files/nep_C_CX.txt/content"),
        record(RECEIPT_REL),
        record(WRAPPER_REL),
        record(state_summary_rel),
        *force_records.values(),
        *[run["summary"] for run in runs],
        *[run["kappa"] for run in runs],
    ]
    major_result["evidence_artifacts"] = evidence
    source = {
        "inputs": [
            record(STRUCTURE_REL, "https://zenodo.org/api/records/7811021/files/graphite-prim.xyz/content"),
            record(POTENTIAL_REL, "https://zenodo.org/api/records/7811021/files/nep_C_CX.txt/content"),
        ],
        "model_header": EXPECTED_MODEL_HEADER,
        "backend": {
            "package": "Calorine",
            "tag": LEGACY_TAG,
            "commit": LEGACY_COMMIT,
            "source_locator": "https://gitlab.com/materials-modeling/calorine/-/tree/1.0",
            "nep_cpp_sha256": LEGACY_NEP_CPP_SHA256,
            "nep_h_sha256": LEGACY_NEP_H_SHA256,
            "nepy_cpp_sha256": LEGACY_NEPY_CPP_SHA256,
            "compile_contract": "g++ -O3 -shared -std=c++14 -fPIC with Python 3.12 headers and pybind11 3.1.0 headers",
            "runtime": {
                "python": "3.12.3",
                "numpy": "2.2.6",
                "ase": "3.29.0",
                "calorine": "1.0",
                "phonopy": "4.4.0",
                "phono3py": "4.4.0",
                "h5py": "3.16.0",
            },
            "legacy_probe_receipt": record(RECEIPT_REL),
        },
        "state": {
            "material": "public C-CX graphite primitive C4 state",
            "primitive_atoms": 4,
            "supercell_dim": [4, 4, 2],
            "supercell_atoms": force.get("supercell_atoms"),
            "displacement_count": force.get("displacement_count"),
            "force_array_shape": force.get("force_array_shape"),
            "relaxed": force.get("relaxed"),
            "material_state_equivalent_to_ding": False,
        },
    }
    reproduction = {
        "software": source["backend"]["runtime"],
        "force_constants": force_records,
        "mesh_runs": runs,
        "c_src_rows_latest_mesh": runs[-1]["c_src_rows"],
        "convergence": convergence,
    }
    uncertainty = {
        "numerical_mesh_envelope_latest_pair": convergence["max_relative_change"],
        "numerical_envelope_is_source_uncertainty": False,
        "source_grade_statistical_or_systematic_uncertainty_present": False,
        "model_form_uncertainty": "OPEN",
        "material_state_uncertainty": "OPEN",
        "density_uncertainty": "OPEN",
        "c_v_source_uncertainty": "OPEN",
        "status": "OPEN_SOURCE_GRADE_UNCERTAINTY",
    }
    package = {
        "schema_version": "t13-calorine-legacy-nep2-pbte-reproduction-source-package-v1",
        "artifact": "t13_calorine_legacy_nep2_pbte_reproduction_source_package",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "source": source,
        "reproduction": reproduction,
        "uncertainty": uncertainty,
        "checks": checks,
        "acceptance_for_full_topic13": False,
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "calibration_path_may_read_holdout": False,
        },
        "controlling_blocker": "calorine_legacy_pbte_source_grade_uncertainty_and_ding_mapping_missing",
        "next_controller": "Source-lock Ding numeric C_src or establish accepted same-regime mapping and source-grade uncertainty; keep this output outside alpha_Phi_K calibration and Xie 2026 holdout paths.",
        "claim_boundary": major_result["claim_boundary"],
    }
    package_path = path(PACKAGE_REL)
    package_path.parent.mkdir(parents=True, exist_ok=True)
    package_path.write_text(json.dumps(package, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    audit = {
        "schema_version": "t13-calorine-legacy-nep2-pbte-reproduction-audit-v1",
        "artifact": "t13_calorine_legacy_nep2_pbte_reproduction_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "source_package": {
            "path": PACKAGE_REL,
            "sha256": digest(package_path),
            "role": "source, backend, force-constant, and candidate C_src manifest",
        },
        "source": source,
        "reproduction": reproduction,
        "uncertainty": uncertainty,
        "checks": checks,
        "evidence_artifacts": evidence,
        "acceptance_for_full_topic13": False,
        "claim_promotion": False,
        "holdout_policy": package["holdout_policy"],
        "controlling_blocker": package["controlling_blocker"],
        "next_controller": package["next_controller"],
        "claim_boundary": package["claim_boundary"],
    }
    audit_path = path(AUDIT_REL)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "package": PACKAGE_REL,
                "audit": AUDIT_REL,
                "latest_pair_max_relative_change": convergence["max_relative_change"],
                "c_src_rows_latest_mesh": runs[-1]["c_src_rows"],
                "source_grade_uncertainty": uncertainty["status"],
                "full_topic13_acceptance": False,
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
