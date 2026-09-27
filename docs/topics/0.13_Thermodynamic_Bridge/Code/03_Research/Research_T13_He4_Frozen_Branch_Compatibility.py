"""Audit the frozen natural O(2) branch against the He-II response anchor.

The result bounds a proposed second-sound inference, not the existing local
Phi calibration. The tree-level branch surface is not a physical phase map.
"""

from __future__ import annotations

import hashlib
import json
from math import sqrt
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config
from docs.core.uet_o2_finite_density_eos import (
    condensate_control,
    effective_mass_sq,
    o2_equilibrium_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    finite_temperature_o2_state,
)
from docs.core.uet_o2_finite_temperature_two_fluid_response import (
    finite_temperature_two_fluid_static_contract,
)
from docs.core.uet_o2_condensed_relative_flow_collision import (
    condensed_relative_flow_collision_contract,
)


DOCS = ROOT / "docs"
COMPOSITION = DOCS / "core/07_artifacts/topic13/t13_he4_core_thermodynamic_bridge_composition_audit.json"
CALIBRATION = DOCS / "core/07_artifacts/topic13/t13_he4_o2_response_calibration_audit.json"
NATURAL_BRIDGE = DOCS / "core/07_artifacts/topic13/t13_uet_o2_action_thermal_observable_bridge_audit.json"


def _evidence(paths: tuple[Path, ...]) -> list[dict[str, str]]:
    return [
        {"path": path.relative_to(ROOT).as_posix(),
         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        for path in paths
    ]


def audit() -> dict:
    composition = json.loads(COMPOSITION.read_text(encoding="utf-8"))
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    natural_bridge = json.loads(NATURAL_BRIDGE.read_text(encoding="utf-8"))
    frozen = composition["state_interface"]["natural_action_state"]
    physical = composition["state_interface"]["physical_he4_state"]
    t, mu, phi = (float(frozen[key]) for key in
                  ("temperature", "chemical_potential", "space_response"))
    config = natural_bridge_config()
    eos = config.eos
    z = float(eos.matter.matter_kinetic)
    coupling = float(eos.response.epsilon_nc * eos.matter.response_coupling)
    m2 = effective_mass_sq(phi, eos)
    q = condensate_control(mu, phi, eos)
    equilibrium = o2_equilibrium_state(mu, phi, eos)
    thermal = finite_temperature_o2_state(t, mu, phi, config)
    if z <= 0 or m2 <= 0 or coupling <= 0:
        raise ValueError("this audit requires positive kinetic/mass/coupling controls")
    mu_boundary = sqrt(m2 / z)
    phi_boundary = eos.response.phi_equilibrium + (eos.matter.matter_mass_sq - z * mu**2) / coupling
    source_fraction = float(calibration["record"]["superfluid_fraction_reference"])
    static_contract = finite_temperature_two_fluid_static_contract()
    collision_contract = condensed_relative_flow_collision_contract()

    checks = {
        "reference_identity_matches_bridge": all(
            abs(float(natural_bridge["state"][name]) - value) < 1e-12
            for name, value in (("temperature", t), ("chemical_potential", mu),
                                ("space_response", phi))
        ),
        "declared_branch_matches_recalculation": (
            frozen["branch"] == natural_bridge["state"]["branch"]
            == equilibrium.branch == thermal.branch == "normal"
        ),
        "normal_branch_has_negative_condensate_control": q < -eos.branch_tolerance,
        "tree_thresholds_are_outside_frozen_point": mu_boundary > mu and phi_boundary > phi,
        "physical_anchor_is_heii_with_nonzero_superfluid_fraction": (
            physical["phase"] == "He II"
            and 0.0 < source_fraction < 1.0
            and abs(float(physical["superfluid_fraction"]) - source_fraction) < 1e-12
        ),
        "no_target_or_fit_in_calibration": (
            not calibration["record"]["holdout_policy"]["target_curve_used"]
            and not calibration["record"]["holdout_policy"]["fit_or_tuning_used"]
        ),
        "static_and_collision_lanes_exclude_complete_two_fluid_transport": (
            "full dissipative condensed two-fluid tensor" in static_contract["excluded_scope"]
            and "complete two-fluid transport tensor" in collision_contract["claim_boundary"]
        ),
    }
    status = "PASS_SCOPED_FROZEN_STATE_BRANCH_MISMATCH" if all(checks.values()) else "REVIEW_REQUIRED"
    sources = (
        COMPOSITION, CALIBRATION, NATURAL_BRIDGE,
        ROOT / calibration["source_identity"]["source_row_package"],
        DOCS / "core/02_equations/o2/uet_o2_action_thermal_stiffness_beta.py",
        DOCS / "core/02_equations/o2/uet_o2_finite_density_eos.py",
        DOCS / "core/02_equations/o2/uet_o2_finite_temperature_two_fluid_response.py",
        DOCS / "core/02_equations/o2/uet_o2_condensed_relative_flow_collision.py",
        Path(__file__).resolve(),
        Path(__file__).with_name("test_t13_he4_frozen_branch_compatibility.py").resolve(),
    )
    return {
        "schema_version": "t13-he4-frozen-branch-compatibility-v1",
        "major_result_id": "T13_HE4_FROZEN_STATE_BRANCH_COMPATIBILITY_BOUNDARY",
        "topic": "0.13", "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "what_is_closed": "The frozen natural bridge reference is a normal O(2) state and cannot itself be linearized as a condensed He-II two-fluid state",
        "equation_or_mapping": {
            "tree_branch_control": "q=Z*mu^2-[m^2-epsilon_nc*h*(Phi-Phi_*)]",
            "condensed_condition": "q>branch_tolerance*max(1,abs(Z*mu^2),abs(m_eff^2)); normal below negative tolerance",
            "mu_boundary_at_frozen_phi": "sqrt(m_eff(Phi)^2/Z)",
            "phi_boundary_at_frozen_mu": "Phi_*+(m^2-Z*mu^2)/(epsilon_nc*h)",
            "mapping_boundary": "local T_K=theta_T*T_nat and DeltaPhi_norm=Z_Phi*DeltaPhi_nat do not identify a condensed background",
        },
        "units": {"natural_state": "natural action units", "mu_boundary": "natural energy",
                  "phi_boundary": "natural action Phi; not SI temperature",
                  "physical_anchor_temperature": "K", "superfluid_fraction": "dimensionless"},
        "derivation_class": "exact tree-branch algebra plus independent module cross-check at a frozen source-calibrated reference",
        "observable": "branch admissibility of proposed He-II second-sound inference from frozen bridge state",
        "data_role": "STRUCTURAL_BRANCH_COMPATIBILITY_AUDIT_NO_HOLDOUT_NO_FIT",
        "frozen_natural_state": {"temperature": t, "chemical_potential": mu,
                                 "space_response": phi, "branch": thermal.branch,
                                 "condensate_control": q, "effective_mass_sq": m2,
                                 "matter_kinetic": z, "response_mass_coupling": coupling,
                                 "mu_critical_at_frozen_phi": mu_boundary,
                                 "delta_mu_to_tree_boundary": mu_boundary - mu,
                                 "phi_critical_at_frozen_mu": phi_boundary,
                                 "delta_phi_to_tree_boundary": phi_boundary - phi,
                                 "condensate_amplitude": thermal.condensate_amplitude},
        "physical_anchor": {"temperature_K": physical["temperature_K"],
                             "phase": physical["phase"],
                             "superfluid_fraction": source_fraction},
        "existing_partial_lanes": {
            "finite_temperature_two_sector": static_contract["data_role"],
            "condensed_relative_flow_collision": collision_contract["data_role"],
            "interpretation": "static two-sector state and a natural-unit relative-flow kernel exist, but their own contracts exclude complete condensed two-fluid transport",
        },
        "checks": checks, "verification_status": status,
        "evidence_artifacts": _evidence(sources),
        "open_blockers": ["state_matched_condensed_action_background_and_independent_transfer_map",
                          "admitted_condensed_two_fluid_longitudinal_response_operator",
                          "physical_normal_superfluid_inertia_and_transport_provenance"],
        "controlling_blocker": "state_matched_condensed_action_background_and_independent_transfer_map",
        "next_action": "Keep the frozen normal-branch local calibration intact; select a condensed natural background independently, rederive its response and SI mapping, then construct and verify a longitudinal two-fluid operator before any second-sound comparison",
        "dependency_unlocked": [], "full_core_unlock": False,
        "claim_boundary": "The result blocks only an attempted second-sound inference from the frozen normal reference. It does not invalidate the existing local effective-response calibration or Core-bounded composition, establish a physical He-II phase map, or prove that all future UET condensed extensions fail. Tree thresholds are algebraic, not admissible fit targets.",
    }


if __name__ == "__main__":
    output = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_frozen_branch_compatibility.json"
    output.write_bytes((json.dumps(audit(), indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(output)
