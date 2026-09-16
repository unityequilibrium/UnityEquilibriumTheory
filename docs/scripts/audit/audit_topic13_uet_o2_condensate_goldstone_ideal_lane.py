"""Audit the tree-level O(2) condensate and Goldstone ideal lane.

This audit joins the existing finite-density EOS, covariant phase
constitutive relation, and Noether-current implementation.  It is limited to
the natural-unit, T=0, tree-level condensed branch.  Synthetic Kubo records
are used only to exercise the existing mode-spectrum control; they are never
reported as physical transport coefficients.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np

if str(Path(__file__).resolve().parents[3]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from docs.core.uet_covariant_matter import (
    CovariantMatterConfig,
    coupled_response_scalar_equation_residual,
    matter_action_contract,
    matter_current_divergence,
    matter_current_divergence_from_eom,
    matter_eom_residual,
    matter_noether_current,
    matter_on_shell_box,
)
from docs.core.uet_covariant_response import CovariantResponseConfig
from docs.core.uet_covariant_superfluid_transport import (
    KuboCoefficientRecord,
    SuperfluidHydroState,
    SuperfluidTransportConfig,
    covariant_superfluid_transport_contract,
    ideal_superfluid_current,
    ideal_superfluid_stress_tensor,
    josephson_residual,
    linear_mode_spectrum,
    superfluid_invariants,
)
from docs.core.uet_o2_finite_density_eos import (
    O2FiniteDensityEOSConfig,
    effective_mass_sq,
    o2_eos_derivatives,
    o2_equilibrium_state,
    o2_finite_density_eos_contract,
    o2_helmholtz_state,
)


ROOT = Path(__file__).resolve().parents[3]
EOS_REL = "docs/core/02_equations/o2/uet_o2_finite_density_eos.py"
MATTER_REL = "docs/core/02_equations/covariant/uet_covariant_matter.py"
TRANSPORT_REL = "docs/core/02_equations/covariant/uet_covariant_superfluid_transport.py"
RESPONSE_REL = "docs/core/02_equations/covariant/uet_covariant_response.py"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_uet_o2_condensate_goldstone_ideal_lane_audit.json"

METRIC = np.diag([-1.0, 1.0, 1.0, 1.0])
MU = 1.3
PHI = 0.2
WAVENUMBER = 0.23


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def config() -> O2FiniteDensityEOSConfig:
    return O2FiniteDensityEOSConfig(
        matter=CovariantMatterConfig(
            matter_kinetic=1.2,
            matter_mass_sq=0.5,
            matter_quartic=0.8,
            response_coupling=0.3,
        ),
        response=CovariantResponseConfig(epsilon_nc=0.1),
    )


def relative_error(actual: float, expected: float) -> float:
    return abs(float(actual) - float(expected)) / max(abs(float(expected)), 1.0e-30)


def synthetic_record(name: str, value: float, state: SuperfluidHydroState) -> KuboCoefficientRecord:
    return KuboCoefficientRecord(
        coefficient_name=name,
        value=value,
        units="natural",
        hydrodynamic_frame="Landau",
        temperature=state.temperature,
        chemical_potential=state.chemical_potential,
        space_response=state.space_response,
        correlator_formula_id=f"synthetic_control_{name}_v1",
        source_path_or_url="internal://synthetic-kubo-control",
        source_hash="0" * 64,
        evidence_status="SYNTHETIC_CONTROL",
    )


def main() -> int:
    eos_config = config()
    eos_state = o2_equilibrium_state(MU, PHI, eos_config)
    mass_sq = float(effective_mass_sq(PHI, eos_config))
    q = float(eos_config.matter.matter_kinetic * MU**2 - mass_sq)
    amplitude_sq = float(q / eos_config.matter.matter_quartic)
    amplitude = float(np.sqrt(amplitude_sq))
    derivatives = o2_eos_derivatives(MU, PHI, eos_config)
    helmholtz = o2_helmholtz_state(0.8, PHI, eos_config)

    h_mu = 1.0e-6
    h_phi = 1.0e-6
    fd_dp_dmu = (
        o2_equilibrium_state(MU + h_mu, PHI, eos_config).pressure
        - o2_equilibrium_state(MU - h_mu, PHI, eos_config).pressure
    ) / (2.0 * h_mu)
    fd_dchi_dmu = (
        o2_equilibrium_state(MU + h_mu, PHI, eos_config).charge_density
        - o2_equilibrium_state(MU - h_mu, PHI, eos_config).charge_density
    ) / (2.0 * h_mu)
    fd_dp_dphi = (
        o2_equilibrium_state(MU, PHI + h_phi, eos_config).pressure
        - o2_equilibrium_state(MU, PHI - h_phi, eos_config).pressure
    ) / (2.0 * h_phi)

    fields = np.array([amplitude, 0.0])
    on_shell_box = matter_on_shell_box(fields, PHI, eos_config.response, eos_config.matter)
    matter_residual = matter_eom_residual(
        on_shell_box,
        fields,
        PHI,
        eos_config.response,
        eos_config.matter,
    )
    gradients = np.vstack([np.zeros(4), amplitude * np.array([-MU, 0.0, 0.0, 0.0])])
    action_current = matter_noether_current(
        METRIC,
        fields,
        gradients,
        eos_config.matter,
    )
    current_divergence = matter_current_divergence(on_shell_box, fields, eos_config.matter)
    current_divergence_from_eom = matter_current_divergence_from_eom(matter_residual, fields)

    hydro_state = SuperfluidHydroState(
        temperature=0.0,
        chemical_potential=MU,
        four_velocity=np.array([1.0, 0.0, 0.0, 0.0]),
        phase_gradient=np.array([-MU, 0.0, 0.0, 0.0]),
        space_response=PHI,
    )
    transport_config = SuperfluidTransportConfig(eos=eos_config)
    invariants = superfluid_invariants(hydro_state, METRIC, transport_config)
    ideal_current = ideal_superfluid_current(hydro_state, METRIC, transport_config)
    ideal_stress = ideal_superfluid_stress_tensor(hydro_state, METRIC, transport_config)
    synthetic_transport_config = SuperfluidTransportConfig(
        eos=eos_config,
        coefficient_records=(
            synthetic_record("regular_conductivity", 0.12, hydro_state),
            synthetic_record("phase_relaxation", 0.20, hydro_state),
            synthetic_record("charge_phase_cross", 0.03, hydro_state),
            synthetic_record("relaxation_time", 0.8, hydro_state),
        ),
        allow_synthetic_controls=True,
    )
    modes = linear_mode_spectrum(
        WAVENUMBER,
        hydro_state,
        METRIC,
        synthetic_transport_config,
    )
    expected_goldstone = np.sqrt(float(eos_state.sound_speed_sq)) * WAVENUMBER

    response_contract = matter_action_contract()
    eos_contract = o2_finite_density_eos_contract()
    transport_contract = covariant_superfluid_transport_contract()
    finite_temperature_rejected = False
    try:
        ideal_superfluid_current(
            SuperfluidHydroState(
                temperature=0.2,
                chemical_potential=MU,
                four_velocity=np.array([1.0, 0.0, 0.0, 0.0]),
                phase_gradient=np.array([-MU, 0.0, 0.0, 0.0]),
                space_response=PHI,
            ),
            METRIC,
            transport_config,
        )
    except NotImplementedError:
        finite_temperature_rejected = True

    checks = {
        "condensed_branch_selected": eos_state.branch == "condensed",
        "condensate_control_positive": q > 0.0,
        "stationarity_closes": abs(
            (mass_sq - eos_config.matter.matter_kinetic * MU**2) * amplitude
            + eos_config.matter.matter_quartic * amplitude**3
        ) <= 1.0e-12,
        "amplitude_formula_closes": relative_error(eos_state.amplitude**2, amplitude_sq) <= 1.0e-12,
        "pressure_formula_closes": relative_error(
            eos_state.pressure,
            q**2 / (4.0 * eos_config.matter.matter_quartic),
        ) <= 1.0e-12,
        "charge_is_pressure_derivative": relative_error(fd_dp_dmu, eos_state.charge_density) <= 1.0e-8,
        "susceptibility_is_charge_derivative": relative_error(fd_dchi_dmu, eos_state.susceptibility) <= 1.0e-8,
        "response_reciprocity_is_preserved": relative_error(fd_dp_dphi, eos_state.response_source) <= 1.0e-8,
        "sound_speed_is_stable_and_subluminal": 0.0 <= float(eos_state.sound_speed_sq) <= 1.0 + 1.0e-12,
        "canonical_legendre_state_closes": relative_error(
            helmholtz.energy_density,
            helmholtz.chemical_potential * helmholtz.charge_density - helmholtz.pressure,
        ) <= 1.0e-12,
        "josephson_relation_closes": abs(josephson_residual(hydro_state, METRIC)) <= 1.0e-12,
        "phase_invariant_matches_mu_squared": relative_error(invariants["invariant_X"], MU**2) <= 1.0e-12,
        "covariant_current_matches_action_noether_current": np.allclose(
            ideal_current,
            action_current,
            rtol=0.0,
            atol=1.0e-12,
        ),
        "current_matches_eos_density": relative_error(ideal_current[0], eos_state.charge_density) <= 1.0e-12,
        "covariant_stress_matches_rest_frame_eos": np.allclose(
            ideal_stress,
            np.diag([
                eos_state.energy_density,
                eos_state.pressure,
                eos_state.pressure,
                eos_state.pressure,
            ]),
            rtol=0.0,
            atol=1.0e-12,
        ),
        "matter_eom_is_on_shell": np.max(np.abs(matter_residual)) <= 1.0e-12,
        "noether_current_is_conserved_on_shell": abs(current_divergence) <= 1.0e-12,
        "noether_identity_matches_eom": abs(current_divergence - current_divergence_from_eom) <= 1.0e-12,
        "goldstone_frequency_matches_tree_level_sound_speed": np.allclose(
            modes["goldstone_angular_frequencies"],
            np.array([-expected_goldstone, expected_goldstone]),
            rtol=0.0,
            atol=1.0e-12,
        ),
        "finite_temperature_normal_component_is_rejected": finite_temperature_rejected,
        "C_is_not_matter_amplitude_or_charge": response_contract["matter_amplitude_role"] == "lorentz_scalar_amplitude_not_yet_density_C" and eos_contract["conserved_coordinate"] == "signed_global_O2_Noether_charge_density",
        "Phi_is_response_input": response_contract["normalized_matter_space_map"] == "PARTIAL_RESPONSE_ONLY" and "Phi" not in eos_contract["conserved_coordinate"],
        "trace_is_absent_and_has_no_backreaction": response_contract["derived_trace_imported"] is False and response_contract["derived_trace_backreaction"] is False and transport_contract["trace_input"] is False and transport_contract["trace_backreaction"] is False,
        "normal_component_is_explicitly_open": transport_contract["normal_component"] == "OPEN_NOT_DERIVED",
        "physical_kubo_values_are_required_not_defaulted": transport_contract["transport_values"] == "REQUIRED_EXTERNAL_OR_MICROSCOPIC_MATCH_NO_DEFAULTS",
        "no_trace_parameter_in_matter_eom": "trace" not in inspect.signature(matter_eom_residual).parameters,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    status = "PASS_T0_CONDENSATE_GOLDSTONE_IDEAL_LANE" if all(checks.values()) else "FAIL_T0_CONDENSATE_GOLDSTONE_IDEAL_LANE"
    evidence = [
        {"path": EOS_REL, "sha256": digest(EOS_REL)},
        {"path": MATTER_REL, "sha256": digest(MATTER_REL)},
        {"path": TRANSPORT_REL, "sha256": digest(TRANSPORT_REL)},
        {"path": RESPONSE_REL, "sha256": digest(RESPONSE_REL)},
    ]
    report = {
        "schema_version": "t13-uet-o2-condensate-goldstone-ideal-v1",
        "artifact": "t13_uet_o2_condensate_goldstone_ideal_lane_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_UET_O2_CONDENSATE_GOLDSTONE_IDEAL_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "tree-level finite-density O(2) condensed branch stationarity, pressure, charge, susceptibility, and sound-speed contract",
                "canonical Legendre relation and response derivative at fixed charge/response lane",
                "T=0 covariant P(X,Phi) ideal current and stress mapping to the O(2) action Noether current",
                "on-shell global O(2) Noether conservation and Josephson phase relation",
                "tree-level Goldstone frequency relation omega_G^2=c_s^2*k^2",
                "explicit boundary separating the T=0 ideal lane from normal finite-temperature and dissipative transport physics",
            ] if status.startswith("PASS") else [],
            "equation_or_mapping": {
                "condensate_control": "q=Z*mu^2-m_eff(Phi)^2 > 0",
                "stationarity": "(m_eff^2-Z*mu^2)A+lambda*A^3=0",
                "amplitude": "A^2=q/lambda",
                "pressure": "p=q^2/(4*lambda)",
                "charge": "n=Z*mu*q/lambda",
                "sound_speed": "c_s^2=q/(3*Z*mu^2-m_eff^2)",
                "goldstone": "omega_G=+-c_s*k",
                "phase_invariant": "X=-xi_mu*xi^mu=mu^2",
                "ideal_current": "N^mu=(Z*q/lambda)*xi^mu",
                "ideal_stress": "T^mu nu=f_s*xi^mu*xi^nu+p*g^mu nu",
                "josephson": "u^mu*xi_mu+mu=0",
            },
            "units": {
                "unit_lane": "natural",
                "mu_mass_xi": "natural energy",
                "pressure_energy": "natural energy density",
                "charge": "signed global O(2) Noether charge density in natural units",
                "sound_and_frequency": "natural units",
                "Phi": "action response input; no SI Kelvin map emitted",
            },
            "derivation_class": "tree-level stationary O(2) action reduction plus covariant constitutive and Noether identity verification; synthetic mode controls only",
            "observable": "T=0 ideal condensate pressure, O(2) Noether current, stress tensor, and Goldstone sound mode",
            "data_role": "ACTION_DERIVED_T0_IDEAL_LANE_WITH_SYNTHETIC_MODE_CONTROL_NOT_PHYSICAL_TRANSPORT",
            "evidence_artifacts": evidence,
            "verification_status": status,
            "open_blockers": [
                "vacuum_counterterm_and_renormalized_one_loop_response_not_closed",
                "finite_temperature_normal_component_not_derived",
                "interacting_finite_temperature_self_energy_not_derived",
                "physical_Kubo_coefficient_record_missing",
                "SK_KMS_physical_matching_missing",
                "SI_Phi_to_thermal_observable_map_missing",
                "alpha_Phi_K_missing",
                "curved_3p1_solver_not_implemented",
            ],
            "dependency_unlocked": "T=0 tree-level condensate/Goldstone ideal lane only; no finite-temperature normal, physical transport, SI, Full Topic 13, Core, or Gravity unlock",
            "claim_boundary": "This closes only the natural-unit tree-level condensed O(2) ideal lane and its covariant Noether/Goldstone mapping. It does not derive a finite-temperature two-fluid theory, physical Kubo coefficients, a renormalized one-loop action, an SI Phi map, external validation, or global UET closure.",
        },
        "reference": {
            "chemical_potential": MU,
            "space_response": PHI,
            "wavenumber": WAVENUMBER,
            "effective_mass_sq": mass_sq,
            "condensate_control": q,
            "amplitude_sq": amplitude_sq,
            "amplitude": amplitude,
            "pressure": float(eos_state.pressure),
            "charge_density": float(eos_state.charge_density),
            "energy_density": float(eos_state.energy_density),
            "susceptibility": float(eos_state.susceptibility),
            "sound_speed_sq": float(eos_state.sound_speed_sq),
            "response_source": float(eos_state.response_source),
            "canonical_charge_density": float(helmholtz.charge_density),
            "canonical_mu": float(helmholtz.chemical_potential),
            "phase_invariant_X": float(invariants["invariant_X"]),
            "ideal_current": [float(value) for value in ideal_current],
            "action_noether_current": [float(value) for value in action_current],
            "goldstone_angular_frequencies": [float(value) for value in modes["goldstone_angular_frequencies"]],
        },
        "finite_difference_checks": {
            "dp_dmu": float(fd_dp_dmu),
            "dp_dphi": float(fd_dp_dphi),
            "dcharge_dmu": float(fd_dchi_dmu),
            "analytic_charge": float(eos_state.charge_density),
            "analytic_response_source": float(eos_state.response_source),
        },
        "noether_checks": {
            "matter_eom_residual": [float(value) for value in matter_residual],
            "current_divergence": float(current_divergence),
            "current_divergence_from_eom": float(current_divergence_from_eom),
            "josephson_residual": float(josephson_residual(hydro_state, METRIC)),
        },
        "synthetic_mode_control": {
            "used": True,
            "role": "exercise existing linear_mode_spectrum path only",
            "physical_transport_claim": False,
            "coefficient_records": [
                "regular_conductivity",
                "phase_relaxation",
                "charge_phase_cross",
                "relaxation_time",
            ],
        },
        "boundary": {
            "temperature_scope": transport_contract["temperature_scope"],
            "normal_component": transport_contract["normal_component"],
            "transport_values": transport_contract["transport_values"],
            "si_lane": transport_contract["si_lane"],
            "curved_3p1_solver": transport_contract["curved_3p1_solver"],
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
        "checks": checks,
        "source_hashes": {item["path"]: item["sha256"] for item in evidence},
        "controlling_blocker": "finite_temperature_normal_component_and_physical_Kubo_coefficient_missing",
        "next_controller": "Keep this T=0 ideal result separate while deriving/source-locking the finite-temperature normal component and physical Kubo records; independently close the SI Phi anchor and vacuum-renormalization boundary.",
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
        },
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "failed_checks": [key for key, value in checks.items() if not value],
        "branch": eos_state.branch,
        "condensate_control": q,
        "sound_speed_sq": eos_state.sound_speed_sq,
        "goldstone_frequencies": report["reference"]["goldstone_angular_frequencies"],
    }, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
