"""Locate a conditional flat partial-action Phi root without physical fitting."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

from scipy.optimize import brentq


ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config  # noqa: E402
from docs.core.uet_o2_finite_density_eos import condensate_control  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    finite_temperature_o2_state,
    quasiparticle_pressure,
)
from docs.core.uet_covariant_response import (  # noqa: E402
    response_potential_derivative,
    response_potential_hessian,
)


DOCS = ROOT / "docs"
CHARGE_AUDIT = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_conditional_charge_map_circularity.json"
RESPONSE_AUDIT = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_relaxed_phi_response_boundary.json"
OUTPUT = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_flat_partial_stationary_root.json"
PHI_BRACKET = (0.5, 1.0)
MU_BRACKET = (1.85, 1.855)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pressure(t: float, mu: float, phi: float, config) -> float:
    return quasiparticle_pressure(t, mu, phi, config)


def _phi_residual(t: float, mu: float, phi: float, h: float, config) -> float:
    response = config.eos.response
    p_phi = (_pressure(t, mu, phi + h, config) - _pressure(t, mu, phi - h, config)) / (2 * h)
    return response.epsilon_nc * response_potential_derivative(phi, response) - p_phi


def _stationary_phi(t: float, mu: float, h: float, config) -> float:
    left, right = PHI_BRACKET
    if _phi_residual(t, mu, left, h, config) * _phi_residual(t, mu, right, h, config) >= 0:
        raise ValueError("declared Phi bracket has no sign change")
    return float(brentq(lambda phi: _phi_residual(t, mu, phi, h, config), left, right, xtol=1e-12))


def _root(t: float, target_n: float, old_mu: float, h: float, config) -> dict:
    fixed_mu_phi = _stationary_phi(t, old_mu, h, config)
    fixed_mu_state = finite_temperature_o2_state(t, old_mu, fixed_mu_phi, config)

    def density_residual(mu: float) -> float:
        phi = _stationary_phi(t, mu, h, config)
        return finite_temperature_o2_state(t, mu, phi, config).charge_density - target_n

    mu_left, mu_right = MU_BRACKET
    if density_residual(mu_left) * density_residual(mu_right) >= 0:
        raise ValueError("declared chemical-potential bracket has no sign change")
    mu = float(brentq(density_residual, mu_left, mu_right, xtol=1e-12))
    phi = _stationary_phi(t, mu, h, config)
    state = finite_temperature_o2_state(t, mu, phi, config)
    p0 = _pressure(t, mu, phi, config)
    p_phiphi = (_pressure(t, mu, phi + h, config) - 2 * p0 + _pressure(t, mu, phi - h, config)) / h**2
    p_mumu = (_pressure(t, mu + h, phi, config) - 2 * p0 + _pressure(t, mu - h, phi, config)) / h**2
    p_muphi = (
        _pressure(t, mu + h, phi + h, config) - _pressure(t, mu + h, phi - h, config)
        - _pressure(t, mu - h, phi + h, config) + _pressure(t, mu - h, phi - h, config)
    ) / (4 * h**2)
    k = config.eos.response.epsilon_nc * response_potential_hessian(phi, config.eos.response) - p_phiphi
    return {
        "derivative_step": h,
        "quadrature_order": config.quadrature_order,
        "old_mu_fixed_stationary_phi": fixed_mu_phi,
        "old_mu_fixed_stationary_branch": fixed_mu_state.branch,
        "old_mu_fixed_stationary_density": fixed_mu_state.charge_density,
        "joint_mu": mu,
        "joint_phi": phi,
        "joint_branch": state.branch,
        "joint_condensate_control": condensate_control(mu, phi, config.eos),
        "joint_density": state.charge_density,
        "joint_density_residual": state.charge_density - target_n,
        "joint_stationarity_residual": _phi_residual(t, mu, phi, h, config),
        "effective_Phi_curvature": k,
        "chi_clamped_natural": p_mumu,
        "p_muphi_natural": p_muphi,
        "chi_relaxed_natural": p_mumu + p_muphi**2 / k if k > 0 else None,
        "dPhi_dmu": p_muphi / k if k > 0 else None,
    }


def audit() -> dict:
    charge = json.loads(CHARGE_AUDIT.read_text(encoding="utf-8"))
    response = json.loads(RESPONSE_AUDIT.read_text(encoding="utf-8"))
    t = float(charge["inputs"]["temperature_natural"])
    target_n = float(charge["inputs"]["derived_natural_charge_target"])
    old_mu = float(charge["conditional_internal_root"]["mu_natural"])
    old_phi = float(charge["conditional_internal_root"]["phi_natural"])
    config = natural_bridge_config()
    runs = [
        _root(t, target_n, old_mu, 1e-3, config),
        _root(t, target_n, old_mu, 5e-4, config),
        _root(t, target_n, old_mu, 5e-4, replace(config, quadrature_order=192)),
    ]
    fine, refined = runs[1], runs[2]
    checks = {
        "prior_root_was_conditional_and_nonstationary": (
            not charge["conditional_internal_root"]["physical_HeII_match_admitted"]
            and response["declared_flat_partial_action_probe"]["status"] == "NONSTATIONARY_AT_CONDITIONAL_ROOT_FOR_DECLARED_FLAT_PARTIAL_POTENTIAL"
        ),
        "fixed_mu_stationarity_changes_density": abs(fine["old_mu_fixed_stationary_density"] - target_n) > 1e-3,
        "joint_roots_are_condensed_and_locally_Phi_stable": all(
            row["joint_branch"] == "condensed"
            and row["joint_condensate_control"] > 0
            and row["effective_Phi_curvature"] > 0 for row in runs
        ),
        "stationarity_and_density_residuals_resolved": all(
            abs(row["joint_stationarity_residual"]) < 1e-7
            and abs(row["joint_density_residual"]) < 1e-7 for row in runs
        ),
        "step_and_quadrature_refinement_agree": (
            max(abs(row["joint_mu"] - fine["joint_mu"]) for row in (runs[0], refined)) < 1e-4
            and max(abs(row["joint_phi"] - fine["joint_phi"]) for row in (runs[0], refined)) < 1e-4
            and max(abs(row["chi_relaxed_natural"] - fine["chi_relaxed_natural"]) for row in (runs[0], refined)) < 1e-3
        ),
        "no_independent_response_row_or_holdout_used": True,
    }
    sources = (
        CHARGE_AUDIT, RESPONSE_AUDIT,
        DOCS / "core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
        DOCS / "core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py",
        DOCS / "core/02_equations/covariant/uet_covariant_response.py",
        Path(__file__).resolve(),
        Path(__file__).with_name("test_t13_he4_flat_partial_stationary_root.py").resolve(),
    )
    return {
        "schema_version": "t13-he4-flat-partial-stationary-root-v1",
        "major_result_id": "T13_HE4_FLAT_PARTIAL_STATIONARY_ROOT_CONDITIONAL",
        "topic": "0.13",
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "what_is_closed": "A condensed local stationary root exists in the declared flat partial-action approximation after reselecting mu and Phi under the same recycled density condition",
        "equation_or_mapping": {
            "flat_partial_stationarity": "0=epsilon_nc*U'(Phi)-partial_Phi p_qp(T,mu,Phi)",
            "recycled_density_constraint": "n_nat=partial_mu p_qp=1/T_nat only under the unadmitted e0,E_mu,atom-number map",
            "local_curvature": "K_eff=epsilon_nc*U''(Phi)-partial_Phi^2 p_qp>0",
            "conditional_relaxed_susceptibility": "chi_relaxed=partial_mu^2 p_qp+(partial_muPhi p_qp)^2/K_eff",
        },
        "units": {"lane": "natural", "mu_T_Phi": "natural energy", "K_eff": "natural mass dimension 2", "SI_response": "not emitted"},
        "derivation_class": "conditional flat partial-action stationary solve and local implicit-function response",
        "observable": "synthetic natural-unit condensed background; no admitted physical He-II measurement operator",
        "data_role": "SYNTHETIC_CIRCULAR_DENSITY_ANCHOR_NOT_VALIDATION",
        "assumption_boundary": "Flat homogeneous partial action omits curved terms, vacuum counterterms and microscopic finite-T completion; density target reuses the same physical density used to define e0",
        "prior_anchor": {"T_natural": t, "mu_natural": old_mu, "Phi_natural": old_phi, "target_natural_charge": target_n},
        "solver_brackets": {"Phi": list(PHI_BRACKET), "mu": list(MU_BRACKET), "role": "exploratory internal brackets selected before external response comparison"},
        "runs": runs,
        "checks": checks,
        "verification_status": "PASS_CONDITIONAL_FLAT_PARTIAL_STATIONARY_ROOT" if all(checks.values()) else "REVIEW_REQUIRED",
        "evidence_artifacts": [{"path": path.relative_to(ROOT).as_posix(), "sha256": _sha(path)} for path in sources],
        "open_blockers": ["full_finite_temperature_action_and_material_map_not_admitted", "density_constraint_recycled_from_e0", "independent_response_source_and_uncertainty_missing", "dynamic_two_fluid_operator_missing"],
        "controlling_blocker": "full_finite_temperature_action_and_material_map_not_admitted",
        "dependency_unlocked": [],
        "full_core_unlock": False,
        "claim_boundary": "This is a synthetic local root of a flat partial action and a recycled density condition, not an independent He-II fit or prediction. It neither closes full finite-temperature UET stationarity nor selects an SI Phi map, physical Kubo coefficient, TTG response, Xie 2026 comparison, or Full Topic 13.",
    }


if __name__ == "__main__":
    OUTPUT.write_bytes((json.dumps(audit(), indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(OUTPUT)
