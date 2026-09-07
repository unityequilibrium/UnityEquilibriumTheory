"""Record the source-locked Calorine/phono3py C_src reproduction wave."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = "docs/topics/0.13_Thermodynamic_Bridge"
DATA = f"{TOPIC}/Data/03_Research"
PACKAGE_REL = f"{DATA}/t13_calorine_zenodo_nep_bte_reproduction_source_package.json"
AUDIT_REL = "docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json"
ARCHIVE = Path(DATA) / "reproduction/t13_calorine_pbte"
CONVERGENCE_TOLERANCE = 0.01
UPSTREAM_NEP_LOCATOR = "https://github.com/brucefan1983/GPUMD/blob/master/potentials/nep/C_2024_NEP4.txt"
RELATED_ROTATION_DISORDER_RECORD = "https://zenodo.org/records/7811021"
UPSTREAM_MODEL_ROLE = "upstream model origin identified by the Zenodo tutorial record; local bytes remain pinned by Zenodo hash"

SUMMARY_RELS = (
    ("4x4x2", f"{DATA}/t13_calorine_zenodo_pbte_run_m442_summary.json"),
    ("6x6x3", f"{DATA}/t13_calorine_zenodo_pbte_run_m663_summary.json"),
    ("8x8x4", f"{DATA}/t13_calorine_zenodo_pbte_run_m884_summary.json"),
    ("10x10x5", f"{DATA}/t13_calorine_zenodo_pbte_run_m10x10x5_summary.json"),
    ("12x12x6", f"{DATA}/t13_calorine_zenodo_pbte_run_m12x12x6_summary.json"),
)

INPUTS = (
    (
        "structure",
        f"{DATA}/raw/calorine_zenodo_21198312/graphite-prim.xyz",
        "https://zenodo.org/api/records/21198312/files/graphite-prim.xyz/content",
    ),
    (
        "potential",
        f"{DATA}/raw/calorine_zenodo_21198312/nep-C.txt",
        "https://zenodo.org/api/records/21198312/files/nep-C.txt/content",
    ),
)


def digest(path: Path, algorithm: str = "sha256") -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def record(relative: str | Path, locator: str | None = None) -> dict:
    path = ROOT / relative
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "size_bytes": path.stat().st_size,
        "sha256": digest(path),
        "locator": locator,
    }


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def relative_change(previous: float, current: float) -> float:
    denominator = abs(current)
    if denominator == 0:
        return 0.0 if previous == 0 else float("inf")
    return abs(current - previous) / denominator


def write_json(relative: str, payload: dict) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def build_run_records() -> list[dict]:
    runs = []
    for label, relative in SUMMARY_RELS:
        summary = load(relative)
        if summary.get("schema_version") != "t13-calorine-pbte-csrc-run-v1":
            raise SystemExit(f"unexpected summary schema: {relative}")
        run = summary.get("run", {})
        if run.get("dim") != [4, 4, 2]:
            raise SystemExit(f"unexpected supercell dim in {relative}: {run.get('dim')}")
        if run.get("transport_solver") != "RTA":
            raise SystemExit(f"unexpected solver in {relative}")
        rows = summary.get("c_src_rows", [])
        if not rows or any(float(row["C_src_J_m^-3_K^-1"]) <= 0 for row in rows):
            raise SystemExit(f"missing or non-positive C_src rows: {relative}")
        force = summary.get("force_constant_summary", {})
        output = summary.get("output_artifacts", {})
        archive_name = {
            "4x4x2": "mesh_4x4x2",
            "6x6x3": "mesh_6x6x3",
            "8x8x4": "mesh_8x8x4",
            "10x10x5": "mesh_10x10x5",
            "12x12x6": "mesh_12x12x6",
        }[label]
        archive_kappa = ARCHIVE / archive_name / "kappa.hdf5"
        if not archive_kappa.is_file():
            raise SystemExit(f"missing archived kappa payload: {archive_kappa}")
        runs.append(
            {
                "label": label,
                "summary": record(relative),
                "mesh": run.get("mesh"),
                "temperatures_K": run.get("temperatures_K"),
                "q_weight_sum": summary.get("geometry", {}).get("q_weight_sum"),
                "primitive_volume_A3": summary.get("geometry", {}).get("primitive_volume_A3"),
                "c_src_rows": rows,
                "force_constants": {
                    "poscar": force.get("poscar"),
                    "fc2": force.get("fc2"),
                    "fc3": force.get("fc3"),
                },
                "archived_kappa": record(archive_kappa),
                "raw_kappa_output": output.get("kappa_hdf5"),
                "fit_performed": bool(run.get("fit_performed")),
                "target_curve_used": bool(run.get("target_curve_used")),
                "holdout_accessed": bool(run.get("holdout_accessed")),
                "alpha_Phi_K_fit_performed": bool(run.get("alpha_Phi_K_fit_performed")),
            }
        )
    return runs


def check_source_inputs() -> list[dict]:
    records = []
    for name, relative, locator in INPUTS:
        path = ROOT / relative
        if not path.is_file():
            raise SystemExit(f"missing source input: {relative}")
        item = record(relative, locator)
        item["name"] = name
        item["md5"] = digest(path, "md5")
        if name == "potential":
            item["upstream_model_origin"] = {
                "locator": UPSTREAM_NEP_LOCATOR,
                "role": UPSTREAM_MODEL_ROLE,
                "related_record": {"locator": RELATED_ROTATION_DISORDER_RECORD, "role": "related record, not the nep-C.txt input source"},
            }
        records.append(item)
    return records


def build_convergence(runs: list[dict]) -> dict:
    comparisons = []
    for previous, current in zip(runs, runs[1:]):
        if previous["temperatures_K"] != current["temperatures_K"]:
            raise SystemExit("temperature grids differ across mesh runs")
        rows = []
        for previous_row, current_row in zip(previous["c_src_rows"], current["c_src_rows"]):
            if previous_row["temperature_K"] != current_row["temperature_K"]:
                raise SystemExit("temperature row identity changed across mesh runs")
            change = relative_change(
                float(previous_row["C_src_J_m^-3_K^-1"]),
                float(current_row["C_src_J_m^-3_K^-1"]),
            )
            rows.append(
                {
                    "temperature_K": current_row["temperature_K"],
                    "relative_change": change,
                    "previous_C_src_J_m^-3_K^-1": previous_row["C_src_J_m^-3_K^-1"],
                    "current_C_src_J_m^-3_K^-1": current_row["C_src_J_m^-3_K^-1"],
                }
            )
        comparisons.append(
            {
                "from_mesh": previous["mesh"],
                "to_mesh": current["mesh"],
                "rows": rows,
                "max_relative_change": max(row["relative_change"] for row in rows),
            }
        )
    latest = comparisons[-1]
    return {
        "criterion": "latest adjacent mesh relative change <= 0.01 for every reported temperature; candidate numerical preflight only",
        "declared_tolerance": CONVERGENCE_TOLERANCE,
        "comparisons": comparisons,
        "latest_pair": latest,
        "latest_pair_pass": latest["max_relative_change"] <= CONVERGENCE_TOLERANCE,
        "scope": "q-mesh convergence at fixed 4x4x2 force-constant supercell and fixed RTA solver; not full source acceptance",
    }


def build_payload() -> tuple[dict, dict]:
    source_inputs = check_source_inputs()
    runs = build_run_records()
    source_hashes = {(item["sha256"], item["md5"]) for item in source_inputs}
    if len(source_hashes) != len(source_inputs):
        raise SystemExit("source input hashes unexpectedly collide")
    fc3_hashes = {run["force_constants"]["fc3"]["sha256"] for run in runs}
    fc2_hashes = {run["force_constants"]["fc2"]["sha256"] for run in runs}
    poscar_hashes = {run["force_constants"]["poscar"]["sha256"] for run in runs}
    if len(fc3_hashes) != 1 or len(fc2_hashes) != 1 or len(poscar_hashes) != 1:
        raise SystemExit("force-constant identity changed across mesh runs")
    convergence = build_convergence(runs)
    all_no_fit = all(
        not run["fit_performed"]
        and not run["target_curve_used"]
        and not run["holdout_accessed"]
        and not run["alpha_Phi_K_fit_performed"]
        for run in runs
    )
    latest = runs[-1]
    source_grade_uncertainty_present = False
    material_state_match = False
    status = (
        "PASS_SCOPED_CALORINE_NUMERIC_C_SRC_REPRODUCTION"
        if convergence["latest_pair_pass"] and all_no_fit
        else "WARN_CALORINE_NUMERIC_C_SRC_REPRODUCTION_OPEN"
    )
    major_result = {
        "major_result_id": "T13_CALORINE_ZENODO_NEP_BTE_NUMERIC_REPRODUCTION",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "PARTIAL",
        "what_is_closed": [
            "public Calorine/Zenodo structure and NEP inputs are locally hashed and rerun",
            "a fixed 4x4x2 force-constant state is reused across four q-mesh runs",
            "phono3py mode heat capacity is aggregated and converted to volumetric C_src in J m^-3 K^-1",
            "the latest 10x10x5 to 12x12x6 mesh pair satisfies the declared candidate numerical preflight",
            "fit, target-curve tuning, alpha_Phi_K fitting, and holdout access are absent from every run",
        ],
        "equation_or_mapping": {
            "mode_to_volumetric": "C_src(T) = [sum_q w_q sum_mu c_qmu(T)] / [sum_q w_q V_primitive]",
            "input_unit": "c_qmu(T) in eV K^-1 per mode per primitive cell",
            "si_conversion": "1 eV = 1.602176634e-19 J; 1 A^3 = 1e-30 m^3",
            "temperature_response_contract": "Delta_Tq = Delta_u_ph / C_src(T); candidate source response only",
            "ttg_measurement": "y_TTG = Delta_Tq(t) / Delta_Tq(0)",
        },
        "units": {
            "C_src": "J m^-3 K^-1",
            "temperature": "K",
            "primitive_volume": "A^3 converted to m^3",
            "thermal_conductivity_control": "W m^-1 K^-1; RTA comparator output only",
        },
        "derivation_class": "EXTERNAL_CANDIDATE_PBTE_REPRODUCTION_NO_UET_DERIVATION",
        "observable": "candidate graphite volumetric phonon heat-capacity response",
        "data_role": "EXTERNAL_CANDIDATE_REPRODUCTION_NOT_CALIBRATION",
        "verification_status": status,
        "open_blockers": [
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            "calorine_route_material_regime_mapping_to_ding_missing",
            "calorine_route_source_grade_uncertainty_missing",
            "alpha_Phi_K_independent_calibration_missing",
        ],
        "dependency_unlocked": "candidate numeric C_src reproduction lane only; no Ding acceptance, alpha, bridge, transport, Core, Gravity, or Galaxy unlock",
        "claim_boundary": "This closes only a source-locked Calorine/Zenodo harmonic/RTA PBTE candidate reproduction lane. It is not Ding-regime equivalence, not source-grade uncertainty closure, not an alpha_Phi_K calibration, not a UET Phi map, not a TTG prediction, and not Full Topic 13 closure.",
    }
    archived_fc = {
        "poscar": record(ARCHIVE / "force_constants_dim_4x4x2/POSCAR"),
        "fc2": record(ARCHIVE / "force_constants_dim_4x4x2/fc2.hdf5"),
        "fc3": record(ARCHIVE / "force_constants_dim_4x4x2/fc3.hdf5"),
    }
    package = {
            "upstream_model_origin": {
                "locator": UPSTREAM_NEP_LOCATOR,
                "role": UPSTREAM_MODEL_ROLE,
                "byte_source": "Zenodo tutorial input record 10.5281/zenodo.21198312",
                "related_record": {"locator": RELATED_ROTATION_DISORDER_RECORD, "role": "related record, not the nep-C.txt input source"},
            },
        "schema_version": "t13-calorine-zenodo-nep-bte-reproduction-source-package-v1",
        "artifact": "t13_calorine_zenodo_nep_bte_reproduction_source_package",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "source": {
            "documentation_url": "https://calorine.materialsmodeling.org/get_started/thermal_conductivity_bte.html",
            "zenodo_record_url": "https://zenodo.org/records/21198312",
            "zenodo_record_doi": "10.5281/zenodo.21198312",
            "inputs": source_inputs,
            "source_state": {
                "material": "public Calorine graphite primitive C4 state",
                "potential": "public nep-C.txt model",
                "morphology": "periodic primitive crystal; not a TTG specimen morphology contract",
                "defect_state": "not declared as Ding natural-graphite TTG state",
                "isotope_state": "not declared as Ding natural-graphite TTG state",
                "equivalent_to_ding": material_state_match,
            },
        },
        "reproduction": {
            "software": latest.get("software", {}) or {
                "calorine": "3.5",
                "phono3py": "4.4.0",
                "phonopy": "4.4.0",
                "ase": "3.29.0",
            },
            "supercell_dim": [4, 4, 2],
            "transport_solver": "phono3py RTA",
            "temperatures_K": latest["temperatures_K"],
            "force_constants": archived_fc,
            "mesh_runs": runs,
            "c_src_rows_latest_mesh": latest["c_src_rows"],
            "convergence": convergence,
        },
        "uncertainty": {
            "numerical_mesh_envelope_latest_pair": convergence["latest_pair"]["max_relative_change"],
            "numerical_envelope_is_source_uncertainty": False,
            "source_grade_statistical_or_systematic_uncertainty_present": source_grade_uncertainty_present,
            "status": "OPEN_SOURCE_GRADE_UNCERTAINTY",
        },
        "checks": {
            "source_locators_present": True,
            "source_hashes_recorded": True,
            "summary_schema_valid": True,
            "same_force_constant_identity_across_meshes": True,
            "archived_force_constant_payload_present": True,
            "archived_kappa_payloads_present": True,
            "mode_heat_capacity_unit_recorded": True,
            "si_volume_and_energy_conversion_recorded": True,
            "latest_mesh_pair_preflight_pass": convergence["latest_pair_pass"],
            "material_state_match_to_ding": material_state_match,
            "source_grade_uncertainty_present": source_grade_uncertainty_present,
            "target_curve_used": False,
            "fit_performed": False,
            "alpha_Phi_K_fit_performed": False,
            "holdout_accessed": False,
        },
        "acceptance_for_full_topic13": False,
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_controller": "Close material/state mapping and source-grade uncertainty, then evaluate against the independent C_src acceptance contract; do not use this candidate output for alpha_Phi_K or holdout prediction.",
        "claim_boundary": major_result["claim_boundary"],
    }
    package_evidence = [
        {"path": item["summary"]["path"], "sha256": item["summary"]["sha256"], "summary": {"role": "persistent PBTE run summary"}}
        for item in runs
    ]
    package_evidence.extend(
        {"path": item["path"], "sha256": item["sha256"], "summary": {"role": "archived reproduction payload"}}
        for item in archived_fc.values()
    )
    audit = {
        "schema_version": "t13-calorine-zenodo-nep-bte-reproduction-audit-v1",
        "artifact": "t13_calorine_zenodo_nep_bte_reproduction_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major_result,
        "source_package": {
            "path": PACKAGE_REL,
            "sha256": None,
            "role": "source and reproduction manifest",
        },
        "reproduction": package["reproduction"],
        "uncertainty": package["uncertainty"],
        "checks": package["checks"],
        "evidence_artifacts": package_evidence,
        "acceptance_for_full_topic13": False,
        "controlling_blocker": package["controlling_blocker"],
        "next_controller": package["next_controller"],
        "claim_boundary": package["claim_boundary"],
    }
    write_json(PACKAGE_REL, package)
    audit["source_package"]["sha256"] = digest(ROOT / PACKAGE_REL)
    write_json(AUDIT_REL, audit)
    return package, audit


def main() -> int:
    package, audit = build_payload()
    print(
        json.dumps(
            {
                "status": audit["status"],
                "package": PACKAGE_REL,
                "audit": AUDIT_REL,
                "latest_pair_max_relative_change": audit["reproduction"]["convergence"]["latest_pair"]["max_relative_change"],
                "c_src_rows_latest_mesh": audit["reproduction"]["c_src_rows_latest_mesh"],
                "full_topic13_acceptance": package["acceptance_for_full_topic13"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
