"""Separate the thermodynamic C_src input from the transport regime contract."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CALORINE_AUDIT_REL = "docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json"
DING_IDENTITY_REL = "docs/core/artifacts/t13_csrc_fixed_volume_identity_audit.json"
SOURCE_PACKAGE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "t13_calorine_zenodo_nep_bte_reproduction_source_package.json"
)
OUT_REL = "docs/core/artifacts/t13_csrc_thermodynamic_transport_regime_decomposition_audit.json"


def load(relative: str) -> tuple[Path, dict[str, Any]]:
    path = ROOT / relative
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return path, value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite_positive(value: Any) -> bool:
    return isinstance(value, (int, float)) and value > 0.0


def row_by_temperature(rows: list[dict[str, Any]]) -> dict[float, dict[str, Any]]:
    return {float(row["temperature_K"]): row for row in rows}


def relative_change(previous: float, current: float) -> float:
    return abs(current - previous) / abs(previous)


def main() -> int:
    calorine_path, calorine = load(CALORINE_AUDIT_REL)
    ding_path, ding = load(DING_IDENTITY_REL)
    package_path, package = load(SOURCE_PACKAGE_REL)

    mesh_runs = calorine["reproduction"]["mesh_runs"]
    run_summaries: list[dict[str, Any]] = []
    for mesh_run in mesh_runs:
        summary_rel = mesh_run["summary"]["path"]
        summary_path, summary = load(summary_rel)
        run_summaries.append(
            {
                "label": mesh_run["label"],
                "mesh": list(mesh_run["mesh"]),
                "summary_path": summary_rel,
                "summary_sha256": sha256(summary_path),
                "c_src_rows": list(summary["c_src_rows"]),
                "kappa_rows": list(summary["transport_summary"]["kappa_W_m^-1_K^-1"]),
                "temperatures_K": list(summary["run"]["temperatures_K"]),
                "transport_solver": summary["run"]["transport_solver"],
                "holdout_accessed": bool(summary["run"]["holdout_accessed"]),
                "target_curve_used": bool(summary["run"]["target_curve_used"]),
                "fit_performed": bool(summary["run"]["fit_performed"]),
                "alpha_Phi_K_fit_performed": bool(summary["run"]["alpha_Phi_K_fit_performed"]),
            }
        )

    previous_run = run_summaries[-2]
    current_run = run_summaries[-1]
    previous_c_src = row_by_temperature(previous_run["c_src_rows"])
    current_c_src = row_by_temperature(current_run["c_src_rows"])
    temperatures = [float(value) for value in current_run["temperatures_K"]]

    latest_rows: list[dict[str, Any]] = []
    for index, temperature in enumerate(temperatures):
        previous_value = float(previous_c_src[temperature]["C_src_J_m^-3_K^-1"])
        current_value = float(current_c_src[temperature]["C_src_J_m^-3_K^-1"])
        previous_kappa = float(previous_run["kappa_rows"][index][0])
        current_kappa = float(current_run["kappa_rows"][index][0])
        latest_rows.append(
            {
                "temperature_K": temperature,
                "C_src_previous_J_m^-3_K^-1": previous_value,
                "C_src_current_J_m^-3_K^-1": current_value,
                "C_src_relative_change": relative_change(previous_value, current_value),
                "kappa_previous_W_m^-1_K^-1": previous_kappa,
                "kappa_current_W_m^-1_K^-1": current_kappa,
                "kappa_relative_change": relative_change(previous_kappa, current_kappa),
            }
        )

    max_c_src_change = max(row["C_src_relative_change"] for row in latest_rows)
    max_kappa_change = max(row["kappa_relative_change"] for row in latest_rows)
    source_state = package["source"]["source_state"]

    checks = {
        "calorine_audit_present": calorine_path.is_file(),
        "ding_identity_audit_present": ding_path.is_file(),
        "source_package_present": package_path.is_file(),
        "ding_fixed_volume_identity_pass": ding["status"].startswith("PASS_"),
        "calorine_csrc_unit_is_volumetric_si": calorine["checks"]["si_volume_and_energy_conversion_recorded"],
        "calorine_csrc_rows_are_finite_positive": all(
            finite_positive(row["C_src_J_m^-3_K^-1"])
            for run in run_summaries
            for row in run["c_src_rows"]
        ),
        "calorine_transport_rows_are_finite_positive": all(
            finite_positive(row[0])
            for run in run_summaries
            for row in run["kappa_rows"]
        ),
        "temperature_grids_match": all(
            run["temperatures_K"] == current_run["temperatures_K"]
            for run in run_summaries
        ),
        "latest_csrc_change_is_quantified": max_c_src_change >= 0.0,
        "latest_transport_change_is_quantified": max_kappa_change >= 0.0,
        "transport_change_exceeds_csrc_change": max_kappa_change > max_c_src_change,
        "calorine_material_equivalence_is_false": source_state["equivalent_to_ding"] is False,
        "calorine_source_grade_uncertainty_is_open": calorine["uncertainty"]["source_grade_statistical_or_systematic_uncertainty_present"] is False,
        "all_run_transport_solvers_are_rta": all(
            run["transport_solver"] == "RTA" for run in run_summaries
        ),
        "target_curve_not_used": all(not run["target_curve_used"] for run in run_summaries),
        "fit_not_performed": all(not run["fit_performed"] for run in run_summaries),
        "alpha_fit_not_performed": all(
            not run["alpha_Phi_K_fit_performed"] for run in run_summaries
        ),
        "holdout_not_accessed": all(not run["holdout_accessed"] for run in run_summaries),
    }
    passed = all(checks.values())
    status = (
        "PASS_SCOPED_C_SRC_THERMODYNAMIC_TRANSPORT_DECOMPOSITION"
        if passed
        else "FAIL_C_SRC_THERMODYNAMIC_TRANSPORT_DECOMPOSITION"
    )

    evidence_artifacts = [
        {
            "path": CALORINE_AUDIT_REL,
            "sha256": sha256(calorine_path),
            "role": "source-locked candidate C_src and mesh audit",
        },
        {
            "path": DING_IDENTITY_REL,
            "sha256": sha256(ding_path),
            "role": "Ding fixed-volume thermodynamic identity boundary",
        },
        {
            "path": SOURCE_PACKAGE_REL,
            "sha256": sha256(package_path),
            "role": "Calorine material and solver state contract",
        },
    ]
    evidence_artifacts.extend(
        {
            "path": run["summary_path"],
            "sha256": run["summary_sha256"],
            "role": f"archived {run['label']} C_src and RTA transport rows",
        }
        for run in run_summaries
    )

    artifact = {
        "schema_version": "t13-csrc-thermodynamic-transport-regime-decomposition-v1",
        "artifact": "t13_csrc_thermodynamic_transport_regime_decomposition_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "T13_C_SRC_THERMODYNAMIC_TRANSPORT_REGIME_DECOMPOSITION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": [
                "C_src is separated from the transport operator as a thermodynamic mode-capacity denominator under a declared fixed-volume mode basis",
                "the Calorine candidate quantifies C_src in J m^-3 K^-1 across the archived q-mesh runs",
                "the latest q-mesh step shows a smaller C_src change than the RTA in-plane conductivity change, so C_src convergence cannot be used as transport convergence",
                "morphology, isotope/defect state, scattering solver, and grating geometry are retained as transport or Ding-acceptance fields rather than silently folded into C_src uncertainty",
            ],
            "equation_or_mapping": {
                "thermodynamic": "u_ph(T,V) = V^-1 sum_mu [hbar*omega_mu(V)*n_B(omega_mu(V),T)]",
                "fixed_volume_C_src": "C_src(T,V) = (partial u_ph / partial T)_V = V^-1 sum_mu c_mu(T,V)",
                "TTG_response": "Delta_Tq = Delta_u_ph / C_src",
                "transport_operator_boundary": "transport response requires a separate scattering/state/geometry operator; C_src rows do not close that operator",
                "UET_bridge_boundary": "Delta_Tq = alpha_Phi_K * Delta_Phi remains open and is not inferred here",
            },
            "units": {
                "C_src": "J m^-3 K^-1",
                "Delta_u_ph": "J m^-3",
                "Delta_Tq": "K",
                "kappa_RTA": "W m^-1 K^-1",
                "alpha_Phi_K": "K per normalized Phi; not emitted",
            },
            "derivation_class": "standard phonon thermodynamic identity plus source-locked mesh comparison; no UET derivation and no calibration",
            "observable": "thermodynamic C_src denominator versus separate RTA transport response",
            "data_role": "SOURCE_BOUNDARY_AND_MAPPING_NOT_CALIBRATION",
            "evidence_artifacts": evidence_artifacts,
            "verification_status": status,
            "open_blockers": [
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "csrc_mode_spectrum_state_mapping_to_ding_missing",
                "csrc_source_grade_uncertainty_and_convergence_contract_missing",
                "independent_alpha_Phi_K_calibration_missing",
                "ttg_transport_material_regime_mapping_not_closed",
            ],
            "dependency_unlocked": "C_src-versus-transport gate separation only; no Ding source acceptance, alpha_Phi_K, physical transport, Core, Gravity, or Galaxy unlock",
            "claim_boundary": "This is a scoped thermodynamic/transport decomposition for an independent Calorine candidate. It is not Ding C_src acceptance, not a material-equivalence result, not an alpha_Phi_K calibration, not a TTG prediction, and not Full Topic 13 closure.",
        },
        "source": {
            "calorine_audit": {"path": CALORINE_AUDIT_REL, "sha256": sha256(calorine_path)},
            "ding_identity_audit": {"path": DING_IDENTITY_REL, "sha256": sha256(ding_path)},
            "calorine_source_package": {"path": SOURCE_PACKAGE_REL, "sha256": sha256(package_path)},
            "calorine_material_state": source_state,
            "q_meshes": [run["mesh"] for run in run_summaries],
            "temperatures_K": temperatures,
        },
        "requirement_partition": {
            "direct_C_src_requirements": [
                {"field": "mode_frequency_and_heat_capacity_state", "status": "CANDIDATE_ROWS_PRESENT_STATE_MATCH_OPEN"},
                {"field": "volume_and_unit_conversion", "status": "PASS_CANDIDATE_CONTRACT"},
                {"field": "source_grade_uncertainty_and_convergence", "status": "OPEN"},
                {"field": "Ding_material_and_state_mapping", "status": "OPEN"},
            ],
            "transport_or_TTG_additional_requirements": [
                {"field": "scattering_operator_and_solver_contract", "status": "RTA_COMPARATOR_ONLY"},
                {"field": "isotope_defect_and_morphology_state", "status": "OPEN_TO_DING"},
                {"field": "grating_geometry_and_measurement_operator", "status": "OPEN_TO_DING_TTG"},
            ],
            "not_substitutable": [
                "C_src mesh convergence does not establish kappa or TTG transport convergence",
                "a periodic-crystal C_src row does not establish Ding specimen equivalence",
                "a standard-physics C_src row does not determine alpha_Phi_K",
            ],
        },
        "latest_mesh_pair": {
            "from": previous_run["mesh"],
            "to": current_run["mesh"],
            "rows": latest_rows,
            "max_C_src_relative_change": max_c_src_change,
            "max_kappa_relative_change": max_kappa_change,
            "diagnostic_ratio_kappa_to_C_src": max_kappa_change / max_c_src_change,
            "interpretation": "The comparison is a diagnostic separation, not a declared physical acceptance threshold.",
        },
        "checks": checks,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "calibration_path_may_read_holdout": False,
            "target_curve_used": False,
            "fit_performed": False,
            "numeric_alpha_Phi_K_emitted": False,
        },
        "controlling_blocker": "ding_C_src_mode_state_and_source_grade_uncertainty_missing",
        "next_action": "Obtain an authorized Ding-compatible mode-resolved C_src package or same-regime PBTE reproduction with state, convergence, and uncertainty; keep the RTA transport comparator outside the Phi calibration path.",
    }

    out_path = ROOT / OUT_REL
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "artifact": OUT_REL,
                "max_C_src_relative_change": max_c_src_change,
                "max_kappa_relative_change": max_kappa_change,
                "holdout_accessed": False,
                "claim_promotion": False,
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
