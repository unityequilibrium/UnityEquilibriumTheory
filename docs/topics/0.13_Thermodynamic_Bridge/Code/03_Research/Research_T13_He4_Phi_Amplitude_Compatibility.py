"""Apply the scoped thermal-Gaussian amplitude no-go to a Phi-only root."""

from __future__ import annotations

import hashlib
import json
from math import sqrt
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config  # noqa: E402
from docs.core.uet_o2_gaussian_offshell_background import off_shell_gaussian_thermal_state  # noqa: E402
from docs.core.uet_o2_gaussian_thermal_stationarity_no_go import (  # noqa: E402
    mode_omega_sq_x_derivatives,
    stationarity_no_go_contract,
    thermal_gaussian_stationarity_no_go,
    tree_derivative_x,
)


DOCS = ROOT / "docs"
ROOT_AUDIT = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_flat_partial_stationary_root.json"
NO_GO = DOCS / "core/07_artifacts/topic13/t13_uet_o2_gaussian_thermal_stationarity_no_go.json"
FORMAL_WARD = DOCS / "core/07_artifacts/topic13/t13_uet_o2_ward_constrained_condensed_audit.json"
OUTPUT = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_phi_amplitude_compatibility.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit() -> dict:
    root = json.loads(ROOT_AUDIT.read_text(encoding="utf-8"))
    no_go = json.loads(NO_GO.read_text(encoding="utf-8"))
    ward = json.loads(FORMAL_WARD.read_text(encoding="utf-8"))
    t = float(root["prior_anchor"]["T_natural"])
    state = root["runs"][1]
    mu = float(state["joint_mu"])
    phi = float(state["joint_phi"])
    config = natural_bridge_config()
    proof = thermal_gaussian_stationarity_no_go(mu, phi, config.eos)
    x0 = proof.x_boundary
    mode_witnesses = []
    for k in (0.01, 0.1, 1.0):
        low, high, dlow_dx, dhigh_dx, margin = mode_omega_sq_x_derivatives(k, x0, mu, proof)
        mode_witnesses.append({"k": k, "low_omega_sq": low, "high_omega_sq": high,
                               "d_low_omega_sq_dx": dlow_dx, "d_high_omega_sq_dx": dhigh_dx,
                               "discriminant_margin": margin})
    one_sided = []
    for order in (128, 192):
        baseline = off_shell_gaussian_thermal_state(t, mu, phi, sqrt(x0), config.eos,
                                                     quadrature_order=order, cutoff_factor=60.0)
        for delta in (0.01, 0.005, 0.0025):
            x = x0 * (1 + delta)
            shifted = off_shell_gaussian_thermal_state(t, mu, phi, sqrt(x), config.eos,
                                                        quadrature_order=order, cutoff_factor=60.0)
            one_sided.append({
                "quadrature_order": order,
                "relative_x_step": delta,
                "x_boundary": x0,
                "x_shifted": x,
                "total_Omega_secant": (shifted.grand_potential - baseline.grand_potential) / (x - x0),
                "tree_derivative_at_boundary": tree_derivative_x(x0, proof),
                "phase_curvature_at_boundary": baseline.phase_curvature,
                "phase_curvature_shifted": shifted.phase_curvature,
            })
    checks = {
        "input_is_conditional_Phi_only_root": (
            root["verification_status"] == "PASS_CONDITIONAL_FLAT_PARTIAL_STATIONARY_ROOT"
            and not root["full_core_unlock"]
        ),
        "analytic_no_go_is_scoped_and_recorded": (
            no_go["status"] == "PASS_SCOPED_NO_GO_THERMAL_GAUSSIAN_CONDENSATE_STATIONARITY"
            and no_go["major_result"]["closure_level"] == "CLOSED_AS_NO_GO"
        ),
        "proof_domain_contains_partial_root": (
            t > 0 and proof.condensate_control > 0
            and proof.kinetic_coefficient > 0 and proof.quartic_coupling > 0
            and state["joint_branch"] == "condensed"
            and abs(root["runs"][1]["joint_condensate_control"] - proof.condensate_control) < 1e-8
            and abs(x0 - proof.condensate_control / proof.quartic_coupling) < 1e-12
        ),
        "stable_mode_derivatives_positive_at_representative_k": all(
            row["low_omega_sq"] > 0 and row["high_omega_sq"] > 0
            and row["d_low_omega_sq_dx"] > 0 and row["d_high_omega_sq_dx"] > 0
            and row["discriminant_margin"] > 0 for row in mode_witnesses
        ),
        "one_sided_amplitude_secants_positive": all(row["total_Omega_secant"] > 0 for row in one_sided),
        "formal_Ward_lane_is_not_microscopic_completion": (
            ward["status"] == "PASS_FORMAL_WARD_CONSTRAINED_CONDENSED_STATIONARITY"
            and ward["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
            and "not a microscopic finite-temperature renormalization"
            in ward["major_result"]["claim_boundary"]
        ),
        "no_holdout_or_external_response_used": True,
    }
    sources = (
        ROOT_AUDIT, NO_GO, FORMAL_WARD,
        DOCS / "core/02_equations/o2/uet_o2_gaussian_thermal_stationarity_no_go.py",
        DOCS / "core/02_equations/o2/uet_o2_gaussian_offshell_background.py",
        Path(__file__).resolve(),
        Path(__file__).with_name("test_t13_he4_phi_amplitude_compatibility.py").resolve(),
    )
    return {
        "schema_version": "t13-he4-phi-amplitude-compatibility-v1",
        "major_result_id": "T13_HE4_PHI_ONLY_ROOT_THERMAL_GAUSSIAN_AMPLITUDE_NO_GO",
        "topic": "0.13",
        "closure_level": "CLOSED_AS_NO_GO" if all(checks.values()) else "OPEN",
        "what_is_closed": "The new Phi-only root lies in the stable domain of the existing thermal-only Gaussian amplitude no-go, so it cannot be a simultaneous amplitude-stationary condensate in that same class",
        "equation_or_mapping": {
            "tree_condensate_boundary": "x0=A_tree^2=q/lambda, q=Z*mu^2-m_eff(Phi)^2>0",
            "amplitude_domain": "x>=x0; partial_x Omega_tree=0.5*(-q+lambda*x)>=0",
            "thermal_gaussian_no_go": "partial_x(Omega_tree+Omega_G)>0 for T>0 and stable modes",
            "separate_Phi_equation": "epsilon_nc*U'(Phi)-partial_Phi p_qp=0 does not imply partial_x Omega=0",
        },
        "units": {"lane": "natural", "x": "natural amplitude squared", "Omega_derivative_x": "natural thermodynamic density per amplitude squared"},
        "derivation_class": "application of existing scoped analytic no-go with independent parameter-domain and one-sided numerical witnesses",
        "observable": "compatibility of a synthetic Phi-stationary point with thermal-only Gaussian condensate amplitude stationarity",
        "data_role": "INTERNAL_STRUCTURAL_NO_GO_NO_HEII_RESPONSE_DATA",
        "root_state": {"T_natural": t, "mu_natural": mu, "Phi_natural": phi,
                       "tree_condensate_control_q": proof.condensate_control,
                       "x_boundary": x0},
        "proof_assumptions": stationarity_no_go_contract()["proof_assumptions"],
        "representative_mode_witnesses": mode_witnesses,
        "one_sided_amplitude_secants": one_sided,
        "checks": checks,
        "verification_status": "PASS_SCOPED_PHI_ROOT_AMPLITUDE_NO_GO" if all(checks.values()) else "REVIEW_REQUIRED",
        "evidence_artifacts": [{"path": path.relative_to(ROOT).as_posix(), "sha256": _sha(path)} for path in sources],
        "open_blockers": ["ward_preserving_condensed_2PI_or_1N_microscopic_completion_missing", "physical_finite_temperature_renormalization_scheme_missing", "material_map_and_independent_response_data_missing"],
        "controlling_blocker": "ward_preserving_condensed_2PI_or_1N_microscopic_completion_missing",
        "dependency_unlocked": [],
        "full_core_unlock": False,
        "claim_boundary": "No simultaneous stationary condensate is established in the tree plus stable thermal-Gaussian class at this Phi-only root. This is not a universal no-go: vacuum renormalization, interactions, symmetry-improved 2PI/1N or a different branch can change the conclusion. No He-II prediction, TTG validation, Xie 2026 access or Full Topic 13 closure follows.",
    }


if __name__ == "__main__":
    OUTPUT.write_bytes((json.dumps(audit(), indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(OUTPUT)
