"""Conditional non-recycled He-4 response design for an unadmitted charge map.

This uses the preceding density-circularity audit as input. It does not admit
the O(2) Noether charge as helium atom number or consume experimental response.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    finite_temperature_o2_state,
)


DOCS = ROOT / "docs"
CHARGE_AUDIT = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_conditional_charge_map_circularity.json"
SI_SOURCE = DOCS / "topics/0.13_Thermodynamic_Bridge/Data/03_Research/he4_o2_si_beta_mapping_source_package.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _response_jacobian(temperature: float, mu: float, phi: float, step: float, config) -> tuple[float, float]:
    """Determinant of clamped-Phi (n_nat, chi_nat/n_nat) versus (mu, Phi)."""
    def outputs(candidate_mu: float, candidate_phi: float) -> tuple[float, float]:
        state = finite_temperature_o2_state(temperature, candidate_mu, candidate_phi, config)
        return state.charge_density, state.susceptibility / state.charge_density

    mu_plus = outputs(mu + step, phi)
    mu_minus = outputs(mu - step, phi)
    phi_plus = outputs(mu, phi + step)
    phi_minus = outputs(mu, phi - step)
    d_n_mu = (mu_plus[0] - mu_minus[0]) / (2 * step)
    d_ratio_mu = (mu_plus[1] - mu_minus[1]) / (2 * step)
    d_n_phi = (phi_plus[0] - phi_minus[0]) / (2 * step)
    d_ratio_phi = (phi_plus[1] - phi_minus[1]) / (2 * step)
    return d_n_mu * d_ratio_phi - d_n_phi * d_ratio_mu, d_n_mu


def audit() -> dict:
    charge = json.loads(CHARGE_AUDIT.read_text(encoding="utf-8"))
    inputs = charge["inputs"]
    root = charge["conditional_internal_root"]
    temperature = float(inputs["temperature_natural"])
    mu = float(root["mu_natural"])
    phi = float(root["phi_natural"])
    n_physical = float(inputs["physical_number_density_m3"])
    e_mu = float(inputs["hypothetical_E_mu_J"])
    e0 = float(inputs["e0_J_per_m3"])
    config = natural_bridge_config()
    state = finite_temperature_o2_state(temperature, mu, phi, config)

    # Under all three unadmitted map hypotheses: n=e0*n_nat/E_mu and
    # chi_SI=e0*chi_nat/E_mu**2 at clamped Phi, so kappa_T=chi_SI/n**2.
    chi_si = e0 * state.susceptibility / e_mu**2
    kappa_si = chi_si / n_physical**2
    dimensionless_response = n_physical * e_mu * kappa_si
    natural_response = state.susceptibility / state.charge_density
    det_coarse, d_n_mu = _response_jacobian(temperature, mu, phi, 1e-3, config)
    det_fine, _ = _response_jacobian(temperature, mu, phi, 5e-4, config)
    determinant_change = abs(det_coarse - det_fine)

    rescalings = []
    for factor in (0.5, 1.0, 2.0):
        scaled_n = factor * n_physical
        scaled_e0 = factor * e0
        scaled_kappa = (scaled_e0 * state.susceptibility / e_mu**2) / scaled_n**2
        rescalings.append({
            "synthetic_density_and_e0_factor": factor,
            "conditional_kappa_T_per_Pa": scaled_kappa,
            "dimensionless_n_E_mu_kappa": scaled_n * e_mu * scaled_kappa,
        })

    checks = {
        "input_charge_audit_is_conditional_only": (
            charge["verification_status"] == "PASS_SCOPED_DENSITY_CIRCULARITY_BOUNDARY"
            and not root["physical_HeII_match_admitted"]
        ),
        "same_condensed_root_and_positive_susceptibility": (
            state.branch == "condensed"
            and abs(state.charge_density - float(root["total_charge_natural"])) < 1e-8
            and state.susceptibility > 0
        ),
        "chain_rule_compressibility_identity": abs(dimensionless_response / natural_response - 1) < 1e-10,
        "density_rescaling_does_not_create_response_validation": all(
            abs(row["dimensionless_n_E_mu_kappa"] / natural_response - 1) < 1e-10
            for row in rescalings
        ),
        "fixed_phi_density_locally_selects_mu": d_n_mu > 0,
        "free_phi_density_and_kappa_locally_select_two_parameters": (
            abs(det_fine) > 10 * determinant_change and abs(det_fine) > 1e-5
        ),
        "no_physical_compressibility_row_used": True,
    }
    paths = (
        CHARGE_AUDIT, SI_SOURCE,
        DOCS / "core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
        Path(__file__).resolve(),
        Path(__file__).with_name("test_t13_he4_conditional_compressibility_design.py").resolve(),
    )
    return {
        "schema_version": "t13-he4-conditional-compressibility-design-v1",
        "major_result_id": "T13_HE4_CONDITIONAL_COMPRESSIBILITY_INDEPENDENCE_DESIGN",
        "topic": "0.13",
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "what_is_closed": "A clamped-Phi conditional response observable and minimum independent-measurement count under the unadmitted O(2)-to-He-4 charge map",
        "equation_or_mapping": {
            "hypothesized_number": "n_SI=e0*n_nat/E_mu",
            "hypothesized_susceptibility": "chi_SI=e0*chi_nat/E_mu^2 at fixed T and Phi",
            "clamped_isothermal_compressibility": "kappa_T|Phi=chi_SI|Phi/n_SI^2; n_SI*E_mu*kappa_T|Phi=chi_nat|Phi/n_nat",
            "relaxed_phi_correction": "chi_nat,total=d_mu n_nat|Phi+(d_Phi n_nat)*(d_mu Phi)|T; the latter term is not supplied by the frozen-Phi EOS",
            "frozen_density_anchor": "n_nat=1/T_nat because e0=n_SI*k_B*T0 and E_mu=k_B*theta_T",
            "independence_boundary": "If Phi is physically clamped and independently fixed, density selects mu and matched clamped-Phi kappa_T is a distinct test. If Phi is free, its state and dPhi/dmu require an admitted response law; density and one response can select parameters rather than validate them",
        },
        "units": {"chi_SI": "m^-3/J", "kappa_T": "Pa^-1", "E_mu": "J per hypothesized atom", "n_E_mu_kappa": "dimensionless"},
        "derivation_class": "conditional chain-rule and local numerical Jacobian; no admitted physical charge correspondence",
        "observable": "independent same-state clamped-Phi isothermal compressibility or an admitted relaxed-Phi correction to ordinary compressibility",
        "data_role": "SYNTHETIC_CONDITIONAL_DESIGN_NO_PHYSICAL_RESPONSE_ROW",
        "assumptions_not_admitted": charge["additional_assumptions_not_admitted"],
        "conditional_state": {"temperature_natural": temperature, "mu_natural": mu, "phi_natural": phi,
                              "charge_natural": state.charge_density, "susceptibility_natural": state.susceptibility},
        "conditional_response": {"chi_SI_clamped_Phi_m3_inverse_per_J": chi_si, "kappa_T_clamped_Phi_per_Pa": kappa_si,
                                  "n_E_mu_kappa": dimensionless_response, "chi_nat_over_n_nat": natural_response},
        "local_rank_witness": {"jacobian_variables": ["mu_natural", "Phi_natural"],
                               "jacobian_outputs": ["n_natural", "chi_natural/n_natural"],
                               "determinant_step_1e_minus_3": det_coarse,
                               "determinant_step_5e_minus_4": det_fine,
                               "determinant_refinement_difference": determinant_change,
                               "scope": "local numerical witness at the conditional root, not global identifiability or physical inference"},
        "synthetic_rescalings": rescalings,
        "minimum_measurement_policy": {
            "already_used_for_scale_or_state": ["physical temperature", "physical density"],
            "fixed_phi": "Independently determine and physically clamp Phi and E_mu, then reserve matched clamped-Phi kappa_T as a test; do not fit it",
            "free_phi": "An admitted Phi response law is required to convert clamped to relaxed susceptibility. Density plus one response may select mu and Phi; reserve at least one further independent observable for falsification",
            "source_requirements": ["same material and thermodynamic state", "clamped-Phi protocol or source-backed relaxed-Phi response correction", "isothermal rather than adiabatic compressibility or justified conversion", "independent instrument/provenance and covariance", "declared chemical-potential energy scale", "no parameter retuning after test"],
        },
        "checks": checks,
        "verification_status": "PASS_SCOPED_CONDITIONAL_COMPRESSIBILITY_DESIGN" if all(checks.values()) else "REVIEW_REQUIRED",
        "evidence_artifacts": [{"path": path.relative_to(ROOT).as_posix(), "sha256": _sha(path)} for path in paths],
        "open_blockers": ["Noether_charge_to_helium_atom_identity_not_admitted", "physical_mu_and_pressure_map_not_derived", "Phi_state_independent_selection_missing", "Phi_clamp_or_relaxed_response_law_missing", "same_state_independent_isothermal_compressibility_not_source_locked", "physical_two_fluid_response_operator_missing"],
        "controlling_blocker": "Noether_charge_to_helium_atom_identity_not_admitted",
        "dependency_unlocked": [],
        "full_core_unlock": False,
        "claim_boundary": "The numerical clamped-Phi compressibility is a conditional model output, not a He-II prediction or comparison. Ordinary measured compressibility cannot be substituted without a physical Phi-clamp or a derived relaxed-Phi correction. The map is still hypothetical; no external response row, TTG holdout, second sound, Core unlock, or Full Topic 13 closure is asserted.",
    }


if __name__ == "__main__":
    output = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_conditional_compressibility_design.json"
    output.write_bytes((json.dumps(audit(), indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(output)
