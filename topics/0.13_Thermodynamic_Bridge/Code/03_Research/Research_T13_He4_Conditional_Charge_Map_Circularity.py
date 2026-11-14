"""Test the tempting but unadmitted SI O(2)-charge-to-He-atom shortcut.

The pressure, chemical-potential, and charge identifications below are
explicit *hypotheses*. The existing e0 convention uses the same measured
number density, so a density match after choosing mu is not validation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scipy.optimize import brentq  # noqa: E402
from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config  # noqa: E402
from docs.core.uet_o2_finite_density_eos import o2_equilibrium_state  # noqa: E402
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (  # noqa: E402
    finite_temperature_o2_state,
)


DOCS = ROOT / "docs"
SI_AUDIT = DOCS / "core/07_artifacts/topic13/t13_he4_o2_si_beta_mapping_audit.json"
SI_SOURCE = DOCS / "topics/0.13_Thermodynamic_Bridge/Data/03_Research/he4_o2_si_beta_mapping_source_package.json"
CALIBRATION = DOCS / "core/07_artifacts/topic13/t13_he4_o2_response_calibration_audit.json"
BRANCH_AUDIT = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_frozen_branch_compatibility.json"
SELECTION_AUDIT = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_condensed_state_identifiability.json"


def _evidence(paths: tuple[Path, ...]) -> list[dict[str, str]]:
    return [
        {"path": path.relative_to(ROOT).as_posix(),
         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in paths
    ]


def audit() -> dict:
    si = json.loads(SI_AUDIT.read_text(encoding="utf-8"))["record"]
    source = json.loads(SI_SOURCE.read_text(encoding="utf-8"))
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))["record"]
    branch = json.loads(BRANCH_AUDIT.read_text(encoding="utf-8"))
    selection = json.loads(SELECTION_AUDIT.read_text(encoding="utf-8"))
    n_physical = float(si["number_density_m3"])
    e0 = float(si["energy_density_scale_J_m3"])
    k_b = float(source["sources"]["boltzmann_constant"]["value_J_K"])
    t_kelvin = float(si["temperature_K"])
    theta_t = float(calibration["theta_T_K_per_natural_temperature"])
    t_natural = float(branch["frozen_natural_state"]["temperature"])
    phi = float(branch["frozen_natural_state"]["space_response"])
    e_mu_hypothetical = k_b * theta_t
    n_natural_target = n_physical * e_mu_hypothetical / e0
    config = natural_bridge_config()
    root = brentq(
        lambda mu: finite_temperature_o2_state(t_natural, mu, phi, config).charge_density
        - n_natural_target,
        1.05, 3.0, xtol=1e-11,
    )
    finite_t = finite_temperature_o2_state(t_natural, root, phi, config)
    tree = o2_equilibrium_state(root, phi, config.eos)
    synthetic_rescalings = []
    for factor in (0.5, 1.0, 2.0):
        n_rescaled = factor * n_physical
        e0_rescaled = factor * e0
        natural_target = n_rescaled * e_mu_hypothetical / e0_rescaled
        reconstructed = e0_rescaled * finite_t.charge_density / e_mu_hypothetical
        synthetic_rescalings.append({
            "synthetic_density_factor": factor,
            "implied_natural_charge_target": natural_target,
            "reconstructed_density_m3": reconstructed,
            "input_density_m3": n_rescaled,
            "relative_match_residual": abs(reconstructed - n_rescaled) / n_rescaled,
        })
    checks = {
        "energy_scale_reuses_same_density": (
            abs(e0 / (n_physical * k_b * t_kelvin) - 1.0) < 1e-12
        ),
        "temperature_scale_matches_frozen_natural_state": (
            abs(theta_t * t_natural / t_kelvin - 1.0) < 1e-12
        ),
        "target_density_cancels_algebraically": (
            abs(n_natural_target - 1.0 / t_natural) < 1e-12
        ),
        "conditional_root_is_internal_condensed": (
            finite_t.branch == tree.branch == "condensed"
            and tree.stability == "STABLE_CONDENSED"
            and finite_t.entropy_density > 0
            and finite_t.susceptibility > 0
        ),
        "density_rescalings_leave_natural_target_unchanged": all(
            abs(row["implied_natural_charge_target"] - n_natural_target) < 1e-12
            and row["relative_match_residual"] < 1e-10
            for row in synthetic_rescalings
        ),
        "charge_identity_is_not_admitted_by_current_selection_audit": (
            "independent_absolute_O2_charge_or_phase_stiffness_to_HeII_density_map"
            in selection["open_blockers"]
        ),
        "source_scale_is_declared_convention": (
            source["mapping_contract"]["derivation_class"]
            == "EXTERNAL_STATE_MATCHED_SCALE_CONVENTION_PLUS_ACTION_DERIVED_BETA"
            and "a first-principles prediction of the absolute free-energy density"
            in source["claim_boundary"]
        ),
    }
    paths = (
        SI_AUDIT, SI_SOURCE, CALIBRATION, BRANCH_AUDIT, SELECTION_AUDIT,
        DOCS / "core/01_contracts/O2_SUPERFLUID_EOS_TRANSPORT_SPEC.md",
        DOCS / "core/02_equations/lorentz_noether/uet_noether_phase_field_map.py",
        DOCS / "core/02_equations/o2/uet_o2_finite_temperature_quasiparticle_eos.py",
        Path(__file__).resolve(),
        Path(__file__).with_name("test_t13_he4_conditional_charge_map_circularity.py").resolve(),
    )
    return {
        "schema_version": "t13-he4-conditional-charge-map-circularity-v1",
        "major_result_id": "T13_HE4_CONDITIONAL_CHARGE_MAP_DENSITY_CIRCULARITY",
        "topic": "0.13", "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "what_is_closed": "A hypothetical full pressure/chemical-potential/charge identity selects an internal condensed mu, but its density match is algebraically circular because e0 was built from that same physical density",
        "equation_or_mapping": {
            "hypothesized_pressure": "p_SI=e0*p_nat as a full grand-canonical material pressure, beyond the admitted scale convention",
            "hypothesized_mu": "mu_SI=mu_offset+k_B*theta_T*mu_nat",
            "hypothesized_charge_identity": "n_He4=partial_(mu_SI) p_SI=(e0/(k_B*theta_T))*n_O2",
            "density_cancellation": "e0=n_He4*k_B*T0 and T0=theta_T*T_nat imply n_O2_required=1/T_nat independently of n_He4",
            "finite_temperature_inversion": "n_O2(T_nat,mu,Phi)=1/T_nat solved only under all three extra hypotheses",
        },
        "units": {"e0": "J/m^3", "mu_SI": "J per hypothesized atom",
                  "E_mu": "J per natural chemical-potential unit",
                  "n_He4": "m^-3", "n_O2": "natural-unit Noether charge density"},
        "derivation_class": "conditional chain-rule derivation, exact density cancellation, and internal finite-temperature root; not a physical map derivation",
        "observable": "whether the He-4 density anchor independently validates or only normalizes a proposed O(2) charge map",
        "data_role": "CONDITIONAL_SYNTHETIC_CIRCULARITY_WITNESS_NO_TARGET_FIT",
        "additional_assumptions_not_admitted": [
            "the scale convention is an absolute physical grand-canonical pressure map",
            "O(2) Noether charge is helium atom number",
            "the physical chemical-potential energy scale is k_B*theta_T with compatible ensemble and reference",
            "Phi=0.15 is independently fixed at the physical He-II state",
            "the approximate finite-temperature EOS is valid for liquid He-II at that state",
        ],
        "inputs": {"physical_number_density_m3": n_physical,
                   "reference_temperature_K": t_kelvin,
                   "theta_T_K_per_natural_T": theta_t,
                   "temperature_natural": t_natural,
                   "e0_J_per_m3": e0,
                   "hypothetical_E_mu_J": e_mu_hypothetical,
                   "derived_natural_charge_target": n_natural_target},
        "conditional_internal_root": {
            "mu_natural": root, "phi_natural": phi,
            "branch": finite_t.branch,
            "total_charge_natural": finite_t.charge_density,
            "tree_goldstone_speed_sq_not_second_sound": tree.sound_speed_sq,
            "physical_HeII_match_admitted": False,
        },
        "synthetic_density_rescalings": synthetic_rescalings,
        "checks": checks,
        "verification_status": "PASS_SCOPED_DENSITY_CIRCULARITY_BOUNDARY" if all(checks.values()) else "REVIEW_REQUIRED",
        "evidence_artifacts": _evidence(paths),
        "open_blockers": ["absolute_material_pressure_and_chemical_potential_correspondence_not_derived",
                          "Noether_charge_to_helium_atom_identity_not_admitted",
                          "independent_phase_stiffness_or_pressure_observable_not_source_locked",
                          "condensed_response_and_two_fluid_operator_not_admitted"],
        "controlling_blocker": "Noether_charge_to_helium_atom_identity_not_admitted",
        "dependency_unlocked": [], "full_core_unlock": False,
        "claim_boundary": "The conditional mu root is not an admitted He-II state. Matching the same density used to define e0 is not validation or a prediction, even if the extra identifications were adopted. No physical pressure comparison, second sound, holdout access, or Full Topic 13 closure follows.",
    }


if __name__ == "__main__":
    output = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_conditional_charge_map_circularity.json"
    output.write_bytes((json.dumps(audit(), indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(output)
