"""Conditional condensed-state selection audit for the He-4/O(2) bridge.

Two internally admissible natural states are *not* two physical He-II fits.
Their multiplicity demonstrates what the declared equilibrium maps do not
currently select, and quantifies the hazard of carrying a normal-state gain.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_action_thermal_observable_bridge import (  # noqa: E402
    action_natural_phi_thermal_bridge_state,
    natural_bridge_config,
)
from docs.core.uet_o2_finite_density_eos import o2_equilibrium_state  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    finite_temperature_o2_state,
)


DOCS = ROOT / "docs"
COMPOSITION = DOCS / "core/07_artifacts/topic13/t13_he4_core_thermodynamic_bridge_composition_audit.json"
CALIBRATION = DOCS / "core/07_artifacts/topic13/t13_he4_o2_response_calibration_audit.json"
SI_SCALE = DOCS / "core/07_artifacts/topic13/t13_he4_o2_si_beta_mapping_audit.json"
NATURAL_BRIDGE = DOCS / "core/07_artifacts/topic13/t13_uet_o2_action_thermal_observable_bridge_audit.json"
PHYSICAL_ROWS = DOCS / "topics/0.13_Thermodynamic_Bridge/Data/03_Research/he4_svp_o2_physical_anchor_source_package.json"
BRANCH_AUDIT = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_frozen_branch_compatibility.json"


def _evidence(paths: tuple[Path, ...]) -> list[dict[str, str]]:
    return [
        {"path": path.relative_to(ROOT).as_posix(),
         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in paths
    ]


def audit() -> dict:
    composition = json.loads(COMPOSITION.read_text(encoding="utf-8"))
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    si_scale = json.loads(SI_SCALE.read_text(encoding="utf-8"))
    bridge = json.loads(NATURAL_BRIDGE.read_text(encoding="utf-8"))
    branch = json.loads(BRANCH_AUDIT.read_text(encoding="utf-8"))
    physical_rows = json.loads(PHYSICAL_ROWS.read_text(encoding="utf-8"))
    o2_contract = (DOCS / "core/01_contracts/O2_SUPERFLUID_EOS_TRANSPORT_SPEC.md").read_text(encoding="utf-8")
    frozen = composition["state_interface"]["natural_action_state"]
    t = float(frozen["temperature"])
    phi = float(frozen["space_response"])
    alpha_external = float(calibration["record"]["alpha_Phi_K"])
    theta_t = float(calibration["record"]["theta_T_K_per_natural_temperature"])
    z_phi_normal = float(calibration["record"]["Z_Phi_normalized_per_natural_Phi"])
    config = natural_bridge_config()
    eos = config.eos
    normal_alpha = float(bridge["state"]["alpha_phi_temperature_natural"])

    # These fixed natural points are structural witnesses, not optimized He-II states.
    candidate_mu = (1.05, 1.20)
    witnesses = []
    for mu in candidate_mu:
        tree = o2_equilibrium_state(mu, phi, eos)
        finite_t = finite_temperature_o2_state(t, mu, phi, config)
        response = action_natural_phi_thermal_bridge_state(t, mu, phi, config)
        quadrature_alpha = {128: response.alpha_phi_temperature_natural}
        for order in (96, 192):
            quadrature_alpha[order] = action_natural_phi_thermal_bridge_state(
                t, mu, phi, replace(config, quadrature_order=order)
            ).alpha_phi_temperature_natural
        witnesses.append({
            "mu_natural": mu,
            "phi_natural": phi,
            "temperature_natural": t,
            "tree_branch": tree.branch,
            "finite_temperature_branch": finite_t.branch,
            "tree_stability": tree.stability,
            "tree_charge_density": tree.charge_density,
            "tree_charge_susceptibility": tree.susceptibility,
            "tree_condensate_amplitude": tree.amplitude,
            "tree_goldstone_speed_sq": tree.sound_speed_sq,
            "total_entropy_density": finite_t.entropy_density,
            "total_charge_susceptibility": finite_t.susceptibility,
            "alpha_phi_t_natural": response.alpha_phi_temperature_natural,
            "alpha_phi_t_refined_natural": response.refined_alpha_phi_temperature_natural,
            "response_refinement_relative_change": response.coefficient_refinement_relative_change,
            "quadrature_alpha_phi_t_natural": {
                str(order): quadrature_alpha[order] for order in (96, 128, 192)
            },
            "quadrature_relative_span": (
                max(quadrature_alpha.values()) - min(quadrature_alpha.values())
            ) / abs(quadrature_alpha[128]),
            "counterfactual_normal_Z_carryover_K_per_Phi_norm": (
                theta_t * response.alpha_phi_temperature_natural / z_phi_normal
            ),
            "physical_HeII_state_admitted": False,
        })

    checks = {
        "frozen_reference_is_normal": branch["frozen_natural_state"]["branch"] == "normal",
        "witnesses_are_tree_stable_condensed_with_positive_total_thermo_checks": (
            len(witnesses) == 2 and all(
                w["tree_branch"] == w["finite_temperature_branch"] == "condensed"
                and w["tree_stability"] == "STABLE_CONDENSED"
                and w["total_entropy_density"] > 0
                and w["total_charge_susceptibility"] > 0
                and 0 < w["tree_goldstone_speed_sq"] < 1
                for w in witnesses
            ) and witnesses[0]["tree_goldstone_speed_sq"] != witnesses[1]["tree_goldstone_speed_sq"]
        ),
        "natural_response_changes_across_candidate_states": (
            all(w["response_refinement_relative_change"] < 1e-3 for w in witnesses)
            and all(abs(w["alpha_phi_t_natural"] - normal_alpha) > 1e-2 for w in witnesses)
        ),
        "normal_state_gain_was_matched_locally": (
            abs(theta_t * normal_alpha / z_phi_normal - alpha_external)
            < 1e-10 * max(1.0, abs(alpha_external))
        ),
        "source_fractions_have_no_declared_absolute_O2_order_parameter_map": (
            "Delta(rho_s/rho)" in physical_rows["observable_contract"]["candidate_uet_mapping"]
            and "Phi is not identified with density" in physical_rows["observable_contract"]["ontology_boundary"]
        ),
        "si_scale_is_thermal_cell_scale_not_charge_identity": (
            "rho / m_He4" in si_scale["record"]["energy_scale_mapping"]
            and "Noether" not in si_scale["record"]["energy_scale_mapping"]
            and "signed O(2) Noether charge density" in o2_contract
        ),
        "no_candidate_promoted_to_physical_match": all(
            not w["physical_HeII_state_admitted"] for w in witnesses
        ),
    }
    m2 = branch["frozen_natural_state"]["effective_mass_sq"]
    z = float(eos.matter.matter_kinetic)
    lam = float(eos.matter.matter_quartic)
    sources = (
        COMPOSITION, CALIBRATION, SI_SCALE, NATURAL_BRIDGE, PHYSICAL_ROWS, BRANCH_AUDIT,
        DOCS / "core/01_contracts/O2_SUPERFLUID_EOS_TRANSPORT_SPEC.md",
        DOCS / "core/02_equations/o2/uet_o2_finite_density_eos.py",
        DOCS / "core/02_equations/o2/uet_o2_action_thermal_observable_bridge.py",
        DOCS / "core/02_equations/o2/uet_o2_formal_two_sector_thermodynamics.py",
        Path(__file__).resolve(),
        Path(__file__).with_name("test_t13_he4_condensed_state_identifiability.py").resolve(),
    )
    return {
        "schema_version": "t13-he4-condensed-state-identifiability-v1",
        "major_result_id": "T13_HE4_CONDENSED_STATE_SELECTION_BOUNDARY",
        "topic": "0.13", "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "what_is_closed": "The declared He-4 equilibrium and local differential-response records do not select an absolute condensed O(2) chemical potential; distinct tree-stable states with positive total thermodynamic checks remain and have different internal Goldstone and thermal responses",
        "equation_or_mapping": {
            "condensed_tree_charge": "n_O2=Z*mu*(Z*mu^2-m_eff^2)/lambda",
            "charge_monotonicity_at_fixed_phi": "d(n_O2)/d(mu)=Z*(3*Z*mu^2-m_eff^2)/lambda>0 when q>0, Z>0, lambda>0",
            "local_calibration": "Delta(rho_s/rho)/f0=Z_Phi*DeltaPhi_nat; alpha_K=theta_T*alpha_nat/Z_Phi at the frozen normal reference",
            "missing_absolute_map": "No declared F(A,chi_perp,n_O2)->rho_s/rho or n_He4=N_scale*n_O2 with independently fixed N_scale at a condensed state",
            "conditional_selection": "With Phi fixed and a justified independent Noether-to-atom density scale, one physical density anchor could select mu by monotone inversion; if Phi also free, another independent equation is required",
        },
        "units": {"natural_action_state": "natural", "tree_speed_sq": "dimensionless natural c=1",
                  "alpha_phi_t_natural": "natural energy per natural Phi",
                  "counterfactual_carryover": "K per normalized Phi, inadmissible extrapolation only",
                  "physical_number_density": "m^-3"},
        "derivation_class": "conditional structural identifiability analysis with two tree-stable natural-unit witnesses and existing action-derived response evaluator",
        "observable": "absolute condensed-state selection and future He-II longitudinal response admission",
        "data_role": "INTERNAL_STATE_SELECTION_WITNESSES_NO_TARGET_FIT_NO_EXTERNAL_PREDICTION",
        "fixed_inputs": {"temperature_natural": t, "space_response_natural": phi,
                         "physical_temperature_K": calibration["record"]["temperature_K"],
                         "physical_number_density_m3": si_scale["record"]["number_density_m3"],
                         "physical_superfluid_fraction": calibration["record"]["superfluid_fraction_reference"],
                         "normal_reference_alpha_phi_t_natural": normal_alpha,
                         "normal_reference_Z_Phi": z_phi_normal,
                         "external_alpha_Phi_K": alpha_external,
                         "tree_mass_sq_at_fixed_phi": m2,
                         "tree_kinetic": z, "tree_quartic": lam},
        "witnesses": witnesses,
        "quadrature_policy": "Orders 96/128/192 are an exploratory post-hoc robustness check, not a preregistered physical acceptance gate or uncertainty estimate",
        "checks": checks,
        "verification_status": "PASS_SCOPED_CONDENSED_STATE_SELECTION_BOUNDARY" if all(checks.values()) else "REVIEW_REQUIRED",
        "evidence_artifacts": _evidence(sources),
        "open_blockers": ["independent_absolute_O2_charge_or_phase_stiffness_to_HeII_density_map",
                          "independently_selected_condensed_mu_and_phi_with_uncertainty",
                          "rederived_condensed_alpha_and_Z_Phi_at_same_state",
                          "admitted_longitudinal_two_fluid_operator"],
        "controlling_blocker": "independent_absolute_O2_charge_or_phase_stiffness_to_HeII_density_map",
        "dependency_unlocked": [], "full_core_unlock": False,
        "claim_boundary": "The two internal witnesses are not calibrated He-II candidates; their tree Goldstone speeds are not second sound. The counterfactual reuse of normal Z_Phi is intentionally invalid and only diagnoses cross-branch sensitivity. No physical mapping, holdout fit, TTG validation, or Full Topic 13 closure is claimed.",
    }


if __name__ == "__main__":
    output = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_condensed_state_identifiability.json"
    output.write_bytes((json.dumps(audit(), indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(output)
