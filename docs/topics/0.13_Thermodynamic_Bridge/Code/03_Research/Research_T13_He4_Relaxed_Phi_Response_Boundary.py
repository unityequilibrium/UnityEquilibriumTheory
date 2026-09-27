"""Conditional local response-completion witness, not an admitted He-II model."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import quasiparticle_pressure  # noqa: E402
from docs.core.uet_covariant_response import (  # noqa: E402
    response_potential_derivative,
    response_potential_hessian,
)


DOCS = ROOT / "docs"
CHARGE_AUDIT = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_conditional_charge_map_circularity.json"
CLAMPED_AUDIT = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_conditional_compressibility_design.json"
OUTPUT = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_relaxed_phi_response_boundary.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _derivatives(t: float, mu: float, phi: float, h: float, config) -> dict[str, float]:
    def pressure(m: float, f: float) -> float:
        return quasiparticle_pressure(t, m, f, config)

    p0 = pressure(mu, phi)
    p_mu_plus, p_mu_minus = pressure(mu + h, phi), pressure(mu - h, phi)
    p_phi_plus, p_phi_minus = pressure(mu, phi + h), pressure(mu, phi - h)
    return {
        "pressure": p0,
        "p_mu": (p_mu_plus - p_mu_minus) / (2 * h),
        "p_phi": (p_phi_plus - p_phi_minus) / (2 * h),
        "p_mumu": (p_mu_plus - 2 * p0 + p_mu_minus) / h**2,
        "p_phiphi": (p_phi_plus - 2 * p0 + p_phi_minus) / h**2,
        "p_muphi": (
            pressure(mu + h, phi + h) - pressure(mu + h, phi - h)
            - pressure(mu - h, phi + h) + pressure(mu - h, phi - h)
        ) / (4 * h**2),
    }


def _completion(derivatives: dict[str, float], k: float, quartic: float) -> dict:
    if k <= 0 or quartic <= 0:
        raise ValueError("local curvature and bounding quartic must be positive")
    cross = derivatives["p_muphi"]
    return {
        "K_natural": k,
        "quartic_natural": quartic,
        "U_at_anchor": 0.0,
        "U_prime_at_anchor": derivatives["p_phi"],
        "U_second_at_anchor": derivatives["p_phiphi"] + k,
        "Omega_Phi_at_anchor": 0.0,
        "Omega_PhiPhi_at_anchor": k,
        "dPhi_dmu_at_anchor": cross / k,
        "chi_clamped_natural": derivatives["p_mumu"],
        "chi_relaxed_natural": derivatives["p_mumu"] + cross**2 / k,
    }


def audit() -> dict:
    charge = json.loads(CHARGE_AUDIT.read_text(encoding="utf-8"))
    clamped = json.loads(CLAMPED_AUDIT.read_text(encoding="utf-8"))
    inputs = charge["inputs"]
    root = charge["conditional_internal_root"]
    t = float(inputs["temperature_natural"])
    mu = float(root["mu_natural"])
    phi = float(root["phi_natural"])
    config = natural_bridge_config()
    coarse = _derivatives(t, mu, phi, 1e-3, config)
    fine = _derivatives(t, mu, phi, 5e-4, config)
    completions = [_completion(fine, k, 1.0) for k in (1.0, 2.0)]
    cross_spread = abs(coarse["p_muphi"] - fine["p_muphi"])
    curvature_spread = abs(coarse["p_phiphi"] - fine["p_phiphi"])
    chi_spread = abs(coarse["p_mumu"] - fine["p_mumu"])
    phi_slope_spread = abs(coarse["p_phi"] - fine["p_phi"])
    response = config.eos.response
    weighted_potential_slope = response.epsilon_nc * response_potential_derivative(phi, response)
    weighted_potential_curvature = response.epsilon_nc * response_potential_hessian(phi, response)
    flat_probe = {
        "scope": "flat homogeneous partial action Omega=-p_qp+epsilon_nc*U(Phi); no curvature, vacuum counterterms, or microscopic thermal completion",
        "epsilon_nc": response.epsilon_nc,
        "Phi_equilibrium_config": response.phi_equilibrium,
        "weighted_U_prime": weighted_potential_slope,
        "p_qp_Phi_at_anchor": fine["p_phi"],
        "Omega_Phi_at_anchor": weighted_potential_slope - fine["p_phi"],
        "weighted_U_second": weighted_potential_curvature,
        "Omega_PhiPhi_at_anchor": weighted_potential_curvature - fine["p_phiphi"],
        "status": "NONSTATIONARY_AT_CONDITIONAL_ROOT_FOR_DECLARED_FLAT_PARTIAL_POTENTIAL",
    }
    checks = {
        "input_map_remains_unadmitted": (
            not root["physical_HeII_match_admitted"]
            and not clamped["full_core_unlock"]
        ),
        "same_condensed_anchor": clamped["conditional_state"]["temperature_natural"] == t
        and abs(clamped["conditional_state"]["mu_natural"] - mu) < 1e-10
        and abs(clamped["conditional_state"]["phi_natural"] - phi) < 1e-10,
        "pressure_derivatives_resolved": (
            abs(fine["p_muphi"]) > 10 * cross_spread
            and abs(fine["p_phiphi"]) > 10 * curvature_spread
            and fine["p_mumu"] > 10 * chi_spread
        ),
        "clamped_derivatives_match_prior_eos_state": (
            abs(fine["p_mu"] / clamped["conditional_state"]["charge_natural"] - 1) < 1e-5
            and abs(fine["p_mumu"] / clamped["conditional_state"]["susceptibility_natural"] - 1) < 1e-5
        ),
        "both_local_completions_stable": all(row["Omega_PhiPhi_at_anchor"] > 0 for row in completions),
        "same_clamped_eos_different_relaxed_response": (
            completions[0]["chi_clamped_natural"] == completions[1]["chi_clamped_natural"]
            and completions[0]["chi_relaxed_natural"] != completions[1]["chi_relaxed_natural"]
        ),
        "stable_local_relaxation_raises_susceptibility": all(
            row["chi_relaxed_natural"] > row["chi_clamped_natural"] for row in completions
        ),
        "declared_flat_partial_potential_nonstationarity_resolved": (
            abs(flat_probe["Omega_Phi_at_anchor"]) > 10 * max(phi_slope_spread, 1e-10)
        ),
        "no_external_row_or_holdout_used": True,
    }
    sources = (
        CHARGE_AUDIT, CLAMPED_AUDIT,
        DOCS / "core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
        DOCS / "core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py",
        DOCS / "core/02_equations/covariant/uet_covariant_response.py",
        Path(__file__).resolve(),
        Path(__file__).with_name("test_t13_he4_relaxed_phi_response_boundary.py").resolve(),
    )
    return {
        "schema_version": "t13-he4-relaxed-phi-response-boundary-v1",
        "major_result_id": "T13_HE4_RELAXED_PHI_RESPONSE_NONIDENTIFIABILITY_BOUNDARY",
        "topic": "0.13",
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "what_is_closed": "The fixed-Phi EOS does not uniquely determine a relaxed-Phi susceptibility within a declared local stable response-completion family",
        "equation_or_mapping": {
            "local_completion": "Omega_K=-p_qp(T,mu,Phi)+U_K(Phi); delta=Phi-Phi0; U_K=p_Phi|0*delta+(p_PhiPhi|0+K)*delta^2/2+lambda*delta^4/4, K>0, lambda>0",
            "stationarity_and_stability": "Omega_Phi|0=0; Omega_PhiPhi|0=K>0",
            "relaxed_slope": "dPhi/dmu|T=p_muPhi/K",
            "relaxed_charge_susceptibility": "chi_relaxed=p_mumu+p_muPhi^2/K",
            "clamped_charge_susceptibility": "chi_clamped=p_mumu",
        },
        "units": {"lane": "natural", "Phi": "mass dimension 1", "K": "mass dimension 2", "quartic": "dimensionless", "chi": "natural charge susceptibility", "SI_compressibility": "not emitted"},
        "derivation_class": "local implicit-function/Schur-complement identity plus two synthetic positive-curvature completions",
        "observable": "conditional relaxed versus clamped isothermal response at one natural O(2) condensed anchor",
        "data_role": "SYNTHETIC_STRUCTURAL_WITNESS_NOT_HEII_DATA",
        "assumption_boundary": "U_K is a hypothetical local conservative completion, not an admitted UET action or calibrated helium response law; the result is local, not a global continuum no-go",
        "anchor": {"T_natural": t, "mu_natural": mu, "Phi_natural": phi, "phase_from_prior_audit": "condensed"},
        "derivatives_step_1e_minus_3": coarse,
        "derivatives_step_5e_minus_4": fine,
        "derivative_refinement_spread": {"p_muphi": cross_spread, "p_phiphi": curvature_spread, "p_mumu": chi_spread},
        "synthetic_local_completions": completions,
        "declared_flat_partial_action_probe": flat_probe,
        "checks": checks,
        "verification_status": "PASS_SCOPED_RELAXED_RESPONSE_NONIDENTIFIABILITY" if all(checks.values()) else "REVIEW_REQUIRED",
        "evidence_artifacts": [{"path": path.relative_to(ROOT).as_posix(), "sha256": _sha(path)} for path in sources],
        "open_blockers": ["declared_flat_partial_action_not_stationary_at_conditional_root", "physical_Phi_response_curvature_and_mixed_susceptibility_not_admitted", "Noether_charge_to_helium_atom_identity_not_admitted", "same_state_independent_isothermal_source_missing"],
        "controlling_blocker": "declared_flat_partial_action_not_stationary_at_conditional_root",
        "dependency_unlocked": [],
        "full_core_unlock": False,
        "claim_boundary": "This is a local conditional class witness plus a flat partial-action stationarity probe. The latter does not test the full curved, renormalized or microscopic UET action. No two physical UET completions, He-II compressibility, fitted K, TTG prediction, Xie 2026 access or Full Topic 13 closure follows.",
    }


if __name__ == "__main__":
    OUTPUT.write_bytes((json.dumps(audit(), indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(OUTPUT)
