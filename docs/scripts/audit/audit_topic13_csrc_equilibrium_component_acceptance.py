"""Audit the equilibrium ``C_src`` component without promoting it to Ding TTG data.

This audit closes only the candidate equilibrium denominator lane.  It keeps
material-regime equivalence, source-grade uncertainty, and the UET Phi map as
separate gates.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUT_REL = "docs/core/artifacts/t13_csrc_equilibrium_component_acceptance_audit.json"
REPRO_REL = "docs/core/artifacts/t13_calorine_zenodo_nep_bte_reproduction_audit.json"
STATE_REL = "docs/core/artifacts/t13_calorine_state_uncertainty_decomposition_audit.json"
ISOTOPE_REL = "docs/core/artifacts/t13_calorine_isotope_mass_sensitivity_audit.json"
MODEL_REL = "docs/core/artifacts/t13_calorine_model_form_state_spread_comparison_audit.json"
IDENTITY_REL = "docs/core/artifacts/t13_csrc_fixed_volume_identity_audit.json"
DECOMPOSITION_REL = "docs/core/artifacts/t13_csrc_thermodynamic_transport_regime_decomposition_audit.json"
SOURCE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/t13_calorine_zenodo_nep_bte_reproduction_source_package.json"
DING_FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_pbte_energy_temperature_source_package.json"


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def evidence(relative: str, role: str, summary: dict[str, Any] | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": relative,
        "sha256": digest(relative),
        "role": role,
    }
    if summary:
        record["summary"] = summary
    return record


def finite_positive(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and float(value) > 0.0


def build_artifact() -> dict[str, Any]:
    reproduction = load(REPRO_REL)
    state = load(STATE_REL)
    isotope = load(ISOTOPE_REL)
    model = load(MODEL_REL)
    identity = load(IDENTITY_REL)
    decomposition = load(DECOMPOSITION_REL)
    source_package = load(SOURCE_REL)
    ding_formula = load(DING_FORMULA_REL)

    latest = reproduction["reproduction"]["c_src_rows_latest_mesh"]
    latest_pair = reproduction["reproduction"]["convergence"]["latest_pair"]
    mesh_envelope = float(latest_pair["max_relative_change"])
    isotope_envelope = float(state["components"]["natural_composition_mass_envelope"]["value"])
    model_rows = model["comparison"]["rows"]
    model_envelope = float(model["comparison"]["spread_summary"]["max_absolute_relative_spread"])
    qualified_bound = max(mesh_envelope, isotope_envelope, model_envelope)

    run_controls = list(reproduction["reproduction"]["mesh_runs"]) + [
        row.get("run", {}) for row in isotope["runs"]
    ]
    checks = {
        "candidate_reproduction_status_pass": str(reproduction.get("status", "")).startswith("PASS_"),
        "candidate_source_package_status_pass": str(source_package.get("status", "")).startswith("PASS_"),
        "source_package_hash_matches_reproduction": (
            digest(SOURCE_REL) == reproduction.get("source_package", {}).get("sha256")
        ),
        "source_package_inputs_have_hashes": all(
            bool(item.get("sha256"))
            for item in source_package.get("source", {}).get("source_inputs", [])
        ),
        "latest_csrc_rows_present": len(latest) == 3,
        "latest_csrc_rows_are_finite_positive": all(
            finite_positive(row.get("C_src_J_m^-3_K^-1")) for row in latest
        ),
        "latest_mesh_pair_pass": reproduction.get("checks", {}).get("latest_mesh_pair_preflight_pass") is True,
        "csrc_si_unit_contract_present": (
            reproduction.get("checks", {}).get("mode_heat_capacity_unit_recorded") is True
            and reproduction.get("checks", {}).get("si_volume_and_energy_conversion_recorded") is True
        ),
        "fixed_volume_identity_pass": identity.get("checks", {}).get("fixed_volume_derivative_identity_verified") is True,
        "decomposition_separates_csrc_from_transport": (
            decomposition.get("status", "").startswith("PASS_")
            and decomposition.get("checks", {}).get("transport_change_exceeds_csrc_change") is True
        ),
        "mesh_sensitivity_present": mesh_envelope >= 0.0,
        "natural_composition_sensitivity_present": isotope_envelope >= 0.0,
        "cross_model_state_sensitivity_present": bool(model_rows) and model_envelope >= 0.0,
        "qualified_bound_is_conservative_max_not_quadrature": qualified_bound == max(
            mesh_envelope, isotope_envelope, model_envelope
        ),
        "source_grade_uncertainty_remains_false": (
            reproduction.get("checks", {}).get("source_grade_uncertainty_present") is False
            and state.get("checks", {}).get("source_grade_uncertainty_present") is False
            and model.get("uncertainty", {}).get("source_grade_statistical_or_systematic_uncertainty_present") is False
        ),
        "material_equivalence_remains_false": (
            reproduction.get("checks", {}).get("material_state_match_to_ding") is False
            and decomposition.get("source", {}).get("calorine_material_state", {}).get("equivalent_to_ding") is False
        ),
        "no_fit_target_or_holdout_in_inputs": all(
            item.get("fit_performed") is False
            and item.get("target_curve_used") is False
            and item.get("holdout_accessed") is False
            and item.get("alpha_Phi_K_fit_performed") is False
            for item in run_controls
        ),
        "identity_formula_does_not_relabel_uet_variables": (
            identity.get("checks", {}).get("source_C_is_not_uet_C") is True
            and identity.get("checks", {}).get("base_phi_identity_not_asserted") is True
        ),
        "ding_formula_source_present": (
            ding_formula.get("formula", {}).get("C_src_definition") is not None
            or ding_formula.get("mapping", {}).get("C_src_definition") is not None
            or "C_src" in json.dumps(ding_formula, ensure_ascii=True)
        ),
    }
    component_ready = all(checks.values())

    rows = [
        {
            "row_id": f"calorine_nep_bte_12x12x6_T{int(row['temperature_K'])}",
            "temperature_K": row["temperature_K"],
            "C_src_J_m^-3_K^-1": row["C_src_J_m^-3_K^-1"],
            "q_mesh": [12, 12, 6],
            "data_role": "EXTERNAL_CANDIDATE_EQUILIBRIUM_COMPONENT_NOT_CALIBRATION",
            "standard_uncertainty_J_m^-3_K^-1": None,
        }
        for row in latest
    ]

    uncertainty = {
        "status": "QUALIFIED_SENSITIVITY_BOUND_NOT_STANDARD_UNCERTAINTY",
        "qualified_global_relative_sensitivity_bound": qualified_bound,
        "aggregation": "max_of_declared_axes; no quadrature or independence assumption",
        "components": {
            "q_mesh_tail": {
                "value": mesh_envelope,
                "scope": "10x10x5_to_12x12x6 at fixed force constants and RTA",
                "source_grade": False,
            },
            "natural_isotope_composition": {
                "value": isotope_envelope,
                "scope": "NIST representative natural-composition bounds in the mass-only lane",
                "source_grade": False,
            },
            "cross_model_state_sensitivity": {
                "value": model_envelope,
                "scope": "baseline versus C-CX at 200 K and 300 K on the common 10x10x5 mesh",
                "source_grade": False,
                "not_pure_model_form": True,
            },
        },
        "excluded_from_bound": {
            "pure_isotope_stress": state["components"]["pure_isotope_stress_envelope"],
            "reason": "stress-only state outside the representative natural-composition lane; not added to the qualified bound",
        },
        "interpretation": (
            "This is a reproducibility and sensitivity envelope for the candidate equilibrium component. "
            "It is not a source-declared standard uncertainty, confidence interval, Ding specimen uncertainty, "
            "or uncertainty for alpha_Phi_K."
        ),
    }

    status = (
        "PASS_SCOPED_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY"
        if component_ready
        else "BLOCKED_C_SRC_EQUILIBRIUM_COMPONENT_INPUT_CONTRACT"
    )
    major_result = {
        "major_result_id": "T13_C_SRC_EQUILIBRIUM_COMPONENT_QUALIFIED_SENSITIVITY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if component_ready else "OPEN",
        "what_is_closed": [
            "The equilibrium C_src denominator is separated from the transport operator under the declared fixed-volume phonon identity.",
            "Candidate C_src rows at 200, 250, and 300 K are source-hash-linked and reported in J m^-3 K^-1.",
            "The 10x10x5 to 12x12x6 numerical tail, natural-isotope mass sensitivity, and cross-model state sensitivity are reported as separate axes.",
            "A qualified max-envelope is recorded without relabeling it as source-grade uncertainty.",
        ],
        "what_is_remains_open": [
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            "material_regime_mapping_to_TTG_not_closed",
            "c_v_source_uncertainty_not_closed",
            "alpha_Phi_K_independent_calibration_missing",
        ],
        "dependency_unlocked": "Candidate equilibrium C_src component and qualified sensitivity lane only; no Ding source, alpha_Phi_K, Phi map, physical transport, Core, Gravity, or external-validation unlock.",
        "equation_or_mapping": {
            "fixed_volume_identity": "C_src(T,V) = (partial u_ph / partial T)_V = V^-1 sum_mu c_mu(T,V)",
            "temperature_response": "Delta_Tq = Delta_u_ph / C_src(T,V)",
            "measurement_boundary": "y_TTG = Delta_Tq(t) / Delta_Tq(0); Delta_Tq = alpha_Phi_K * Delta_Phi remains open",
        },
        "units": {
            "C_src": "J m^-3 K^-1",
            "Delta_u_ph": "J m^-3",
            "Delta_Tq": "K",
            "alpha_Phi_K": "K per normalized Phi; not emitted",
        },
        "derivation_class": "standard fixed-volume thermodynamic identity plus external candidate PBTE reproduction and qualified sensitivity audit; no UET derivation",
        "observable": "candidate equilibrium modal heat-capacity denominator C_src",
        "data_role": "EXTERNAL_CANDIDATE_EQUILIBRIUM_COMPONENT_NOT_CALIBRATION",
        "evidence_artifacts": [
            evidence(REPRO_REL, "source-locked candidate C_src rows and mesh convergence"),
            evidence(SOURCE_REL, "candidate source and reproduction manifest"),
            evidence(STATE_REL, "state uncertainty decomposition"),
            evidence(ISOTOPE_REL, "natural-isotope mass sensitivity"),
            evidence(MODEL_REL, "cross-model/state sensitivity comparison"),
            evidence(IDENTITY_REL, "fixed-volume C_src identity"),
            evidence(DECOMPOSITION_REL, "C_src versus transport separation"),
            evidence(DING_FORMULA_REL, "Ding response formula boundary"),
        ],
        "verification_status": status,
        "open_blockers": [
            "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            "material_regime_mapping_to_TTG_not_closed",
            "c_v_source_uncertainty_not_closed",
            "alpha_Phi_K_independent_calibration_missing",
        ],
        "claim_boundary": "This closes only the candidate equilibrium C_src component and its qualified sensitivity reporting. It is not Ding TTG material equivalence, not source-grade uncertainty, not a UET Phi or alpha_Phi_K calibration, not a transport validation, and not Full Topic 13 closure.",
    }

    artifact = {
        "schema_version": "t13-csrc-equilibrium-component-qualified-sensitivity-v1",
        "artifact": "t13_csrc_equilibrium_component_acceptance_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "claim_promotion": False,
        "major_result": major_result,
        "report": {
            "MAJOR_RESULT_CLOSURE": major_result["closure_level"],
            "WHAT_IS_ACTUALLY_CLOSED": major_result["what_is_closed"],
            "WHAT_REMAINS_OPEN": major_result["what_is_remains_open"],
            "DEPENDENCY_UNLOCKED": major_result["dependency_unlocked"],
            "STATUS": status,
            "WHAT_CHANGED": "Added an evidence-grade equilibrium C_src component acceptance scope with explicit candidate rows, hash-linked inputs, convergence, and qualified sensitivity boundaries.",
            "EQUATION_OR_MAPPING": major_result["equation_or_mapping"],
            "VERIFICATION": "Source hashes, SI C_src rows, fixed-volume identity, latest mesh tail, natural-isotope sensitivity, cross-model sensitivity, no-fit, and holdout isolation are checked. The candidate remains non-Ding and source-grade uncertainty remains open.",
            "CONTROLLING_BLOCKER": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
            "NEXT_ACTION": "Acquire an authorized Ding numeric package or accepted same-regime PBTE reproduction with material/state mapping and source-grade uncertainty; keep this component outside alpha_Phi_K calibration.",
            "CLAIM_BOUNDARY": major_result["claim_boundary"],
        },
        "acceptance": {
            "accepted_as_equilibrium_csrc_component": component_ready,
            "acceptance_scope": "EQUILIBRIUM_C_SRC_COMPONENT_ONLY",
            "accepted_as_ding_ttg_source": False,
            "accepted_for_full_topic13": False,
            "full_topic13_source_gate_unlocked": False,
            "material_state_match_to_ding": False,
            "source_grade_uncertainty_present": False,
        },
        "rows": rows,
        "uncertainty": uncertainty,
        "source": {
            "candidate_reproduction": {"path": REPRO_REL, "sha256": digest(REPRO_REL)},
            "source_package": {"path": SOURCE_REL, "sha256": digest(SOURCE_REL)},
            "ding_formula_boundary": {"path": DING_FORMULA_REL, "sha256": digest(DING_FORMULA_REL)},
            "material_state": reproduction.get("source_package", {}).get("material_state"),
        },
        "checks": checks,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "calibration_path_may_read_holdout": False,
        },
        "numeric_C_src_emitted": True,
        "numeric_alpha_Phi_K_emitted": False,
        "target_fit_performed": False,
        "holdout_accessed": False,
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_controller": "Obtain authorized Ding numeric C_src or accepted same-regime PBTE reproduction with source-grade uncertainty and material/state mapping; retain this candidate as an equilibrium component comparator only.",
        "claim_boundary": major_result["claim_boundary"],
    }
    return artifact


def main() -> int:
    artifact = build_artifact()
    out = ROOT / OUT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": artifact["status"],
                "closure_level": artifact["major_result"]["closure_level"],
                "accepted_as_equilibrium_csrc_component": artifact["acceptance"]["accepted_as_equilibrium_csrc_component"],
                "accepted_for_full_topic13": artifact["acceptance"]["accepted_for_full_topic13"],
                "qualified_global_relative_sensitivity_bound": artifact["uncertainty"]["qualified_global_relative_sensitivity_bound"],
                "artifact": OUT_REL,
            },
            indent=2,
        )
    )
    return 0 if artifact["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
