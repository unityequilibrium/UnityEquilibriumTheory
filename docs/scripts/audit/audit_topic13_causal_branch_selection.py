"""Select the admissible Topic 13 causal branch without erasing the baseline fail."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
NO_GO_REL = "docs/core/07_artifacts/archive/conserved_c_finite_cone_no_go_assessment.json"
FLUX_REL = "docs/core/07_artifacts/verification/matter_space_conserved_flux_telegraph_verification.json"
COUPLED_REL = "docs/core/07_artifacts/verification/matter_space_flux_phi_coupled_verification.json"
THERMAL_GATE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/thermal_wave1_branch_gate.json"
FULL_GATE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_causal_branch_selection_audit.json"


def load(rel: str) -> dict[str, Any]:
    with (ROOT / rel).open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def main() -> int:
    no_go = load(NO_GO_REL)
    flux = load(FLUX_REL)
    coupled = load(COUPLED_REL)
    thermal_gate = load(THERMAL_GATE_REL)
    full_gate = load(FULL_GATE_REL)
    full_causal = full_gate["verification_status"]["causal_full_candidate_or_formal_no_go_branch"]
    coupled_checks = coupled.get("verification", {}).get("checks", {})
    flux_checks = flux.get("verification", {}).get("checks", {})
    threshold = float(full_causal["threshold"])
    baseline_leakage = float(thermal_gate["full_candidate_branch"]["prearrival_leakage_fraction"])
    checks = {
        "baseline_scoped_no_go_recorded": no_go.get("status") == "NO_GO_FOR_DECLARED_CONSERVED_CATTANEO_LOCAL_GRADIENT_CLASS",
        "baseline_no_go_scope_is_declared": "local conserved-C Cattaneo equation" in no_go.get("proof_scope", ""),
        "original_baseline_stays_failed": full_causal.get("full_candidate_pass") is False,
        "original_baseline_leakage_exceeds_locked_threshold": baseline_leakage > threshold,
        "threshold_is_unchanged": threshold == 1.0e-6 and thermal_gate["gates"].get("locked_threshold_unchanged") is True,
        "flux_branch_passes": flux.get("status") == "PASS" and all(flux_checks.values()),
        "coupled_branch_passes": coupled.get("status") == "PASS" and all(coupled_checks.values()),
        "coupled_branch_is_lane_only": coupled.get("major_result", {}).get("closure_level") == "CLOSED_FOR_LANE",
        "coupled_leakage_passes_locked_threshold": float(coupled["domain_of_dependence"]["metrics"]["prearrival_leakage_fraction"]) <= threshold,
        "coupled_arrival_is_nonzero": float(coupled["domain_of_dependence"]["metrics"]["C_arrival_target_abs"]) > 0.0 and float(coupled["domain_of_dependence"]["metrics"]["Phi_arrival_target_abs"]) > 0.0,
        "coupled_energy_ledger_passes": float(coupled["domain_of_dependence"]["metrics"]["max_combined_energy_relative_residual"]) <= 1.0e-6,
        "no_clipping_or_padding_or_fit": coupled_checks.get("no_clipping") is True and coupled_checks.get("no_cone_padding") is True and coupled_checks.get("no_parameter_fitting") is True,
        "holdout_not_accessed": coupled.get("verification", {}).get("xie_2026_accessed") is False,
    }
    status = "PASS_CLOSED_AS_NO_GO_WITH_NAMED_COUPLED_BRANCH" if all(checks.values()) else "FAIL_CAUSAL_BRANCH_SELECTION_AUDIT"
    report = {
        "schema_version": "t13-causal-branch-selection-audit-v1",
        "artifact": "t13_causal_branch_selection_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_CAUSAL_THERMAL_BRANCH_SELECTION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "the original local conserved-C gradient Cattaneo baseline is retained as a scoped high-k finite-cone no-go",
                "the named conserved C flux-telegraph branch passes compact-support, mass, ledger, convergence, and anti-manipulation controls",
                "the named coupled C/Phi flux-telegraph branch passes the same locked finite-cone, arrival, mass, shared-ledger, convergence, no-clipping, no-padding, and no-fit controls",
                "the branch-selection conclusion preserves the original baseline failure instead of relabeling it as passed"
            ],
            "equation_or_mapping": {
                "blocked_baseline": "tau_C C_tt + C_t = M_C Laplacian(a_C C - kappa_C Laplacian(C)) with kappa_C>0",
                "selected_C_branch": "C_t + partial_x J_C = 0; tau_C J_C_t + J_C = -M_C partial_x(mu_C); kappa_C=0",
                "selected_coupled_branch": "tau_Phi Phi_tt + Phi_t + M_Phi mu_Phi = 0 with V_CPhi=-coupling_g C^2 Phi/2",
                "causal_measurement": "prearrival_leakage_fraction <= 1e-6; C and Phi arrival targets nonzero; normalized energy ledger residual <= 1e-6"
            },
            "units": {
                "lane": "normalized internal candidate",
                "C": "collective-coordinate density lane; not universal mass or density",
                "Phi": "effective response variable; not temperature, heat flux, entropy, metric, or particle",
                "R_gen": "derived history trace; absent from branch dynamics"
            },
            "derivation_class": "scoped structural no-go plus named finite-volume flux-telegraph branch verification",
            "observable": "normalized C/Phi response and compact discrete domain-of-dependence diagnostics",
            "data_role": "INTERNAL_NUMERICAL_BRANCH_SELECTION_NO_EXTERNAL_TTG_OR_HOLDOUT",
            "evidence_artifacts": [
                {"path": NO_GO_REL, "sha256": sha256(NO_GO_REL)},
                {"path": FLUX_REL, "sha256": sha256(FLUX_REL)},
                {"path": COUPLED_REL, "sha256": sha256(COUPLED_REL)},
                {"path": THERMAL_GATE_REL, "sha256": sha256(THERMAL_GATE_REL)},
                {"path": "docs/core/07_artifacts/topic13/t13_causal_branch_selection_audit.json"}
            ],
            "verification_status": status,
            "open_blockers": [
                "selected branch remains normalized and has no dimensional Phi-to-temperature map",
                "TTG numeric source and independent alpha_Phi_K remain open",
                "non-circular bridge, beta, EOS, transport, SK/KMS, entropy current, and dissipative balance remain open",
                "original kappa_C>0 conserved-gradient baseline remains blocked and is not replaced"
            ],
            "dependency_unlocked": "normalized causal branch input only; no SI thermal, Core curved 3+1, Gravity, or external-validation dependency unlock",
            "claim_boundary": "This result selects a named normalized causal branch after a scoped no-go. It does not turn the original conserved-gradient baseline into a pass, prove covariant well-posedness, establish a physical temperature mapping, or close Topic 13."
        },
        "baseline_preservation": {
            "full_candidate_pass": full_causal.get("full_candidate_pass"),
            "prearrival_leakage_fraction": baseline_leakage,
            "locked_threshold": threshold,
            "baseline_replaced": False
        },
        "selected_branch": {
            "branch_id": coupled.get("branch_id"),
            "prearrival_leakage_fraction": coupled["domain_of_dependence"]["metrics"]["prearrival_leakage_fraction"],
            "C_arrival_target_abs": coupled["domain_of_dependence"]["metrics"]["C_arrival_target_abs"],
            "Phi_arrival_target_abs": coupled["domain_of_dependence"]["metrics"]["Phi_arrival_target_abs"],
            "max_combined_energy_relative_residual": coupled["domain_of_dependence"]["metrics"]["max_combined_energy_relative_residual"],
            "closure_level": coupled["major_result"]["closure_level"]
        },
        "checks": checks,
        "parameter_fitting_performed": False,
        "source_rows_consumed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "selected_causal_branch_is_normalized_and_dimensional_thermal_bridge_remains_open",
        "next_controller": "Use the selected named causal branch only as a normalized Core input while independently closing the Phi-energy scale, permitted TTG source package, alpha_Phi_K, and thermodynamic bridge; do not rerun or relabel the failed conserved-gradient baseline.",
        "claim_boundary": "No source data, target curve, fit, threshold change, clipping, cone padding, holdout access, external validation, or global UET closure is claimed."
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"), "failed_checks": [key for key, value in checks.items() if not value]}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
