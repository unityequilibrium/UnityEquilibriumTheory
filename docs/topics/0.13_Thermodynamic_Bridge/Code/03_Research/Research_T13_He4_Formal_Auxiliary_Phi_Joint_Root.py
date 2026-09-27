"""Test Phi stationarity on Core's fixed-prescription formal auxiliary lane."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from scipy.optimize import brentq


ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.uet_covariant_response import (  # noqa: E402
    response_potential,
    response_potential_derivative,
    response_potential_hessian,
)
from docs.core.uet_o2_action_thermal_observable_bridge import natural_bridge_config  # noqa: E402
from docs.core.uet_o2_auxiliary_field_condensed import auxiliary_field_condensed_state  # noqa: E402
from docs.core.uet_o2_finite_density_eos import effective_mass_sq  # noqa: E402
from docs.scripts.audit.audit_topic13_uet_o2_auxiliary_field_condensed import (  # noqa: E402
    CHEMICAL_POTENTIAL,
    PHI_RESPONSE,
    REFERENCE_CUTOFF_FACTOR,
    REFERENCE_ORDER,
    TEMPERATURE,
    config as formal_auxiliary_config,
)


DOCS = ROOT / "docs"
AUXILIARY_AUDIT = DOCS / "core/07_artifacts/topic13/t13_uet_o2_auxiliary_field_condensed_audit.json"
GAUSSIAN_BOUNDARY = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_phi_amplitude_compatibility.json"
OUTPUT = DOCS / "topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_he4_formal_auxiliary_phi_joint_root.json"
PHI_BRACKET = (0.0, 0.5)
TEMPERATURES = (0.20, TEMPERATURE, 0.28)
ORDERS = (128, REFERENCE_ORDER)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _phi_residual(phi: float, mu: float, config) -> float:
    response = config.response
    matter = config.matter
    mass_sq = effective_mass_sq(phi, config)
    dressed_mass_sq = matter.matter_kinetic * mu * mu
    source = matter.response_coupling * (dressed_mass_sq - mass_sq) / (2.0 * matter.matter_quartic)
    return response.epsilon_nc * (response_potential_derivative(phi, response) - source)


def _phi_curvature(phi: float, config) -> float:
    response = config.response
    matter = config.matter
    return response.epsilon_nc * response_potential_hessian(phi, response) - (
        response.epsilon_nc * matter.response_coupling
    ) ** 2 / (2.0 * matter.matter_quartic)


def _profile_total_potential(phi: float, t: float, mu: float, config, order: int, cutoff: float) -> float:
    state = auxiliary_field_condensed_state(
        t, mu, phi, config, quadrature_order=order, momentum_cutoff=cutoff
    )
    return -state.pressure + config.response.epsilon_nc * response_potential(phi, config.response)


def audit() -> dict:
    auxiliary = json.loads(AUXILIARY_AUDIT.read_text(encoding="utf-8"))
    gaussian = json.loads(GAUSSIAN_BOUNDARY.read_text(encoding="utf-8"))
    config = formal_auxiliary_config()
    normalized_config = natural_bridge_config().eos
    mu = CHEMICAL_POTENTIAL
    left, right = PHI_BRACKET
    left_residual = _phi_residual(left, mu, config)
    right_residual = _phi_residual(right, mu, config)
    if left_residual * right_residual >= 0.0:
        raise ValueError("declared Phi bracket does not straddle an analytic root")
    phi = float(brentq(lambda point: _phi_residual(point, mu, config), left, right, xtol=1e-13))
    reference = auxiliary_field_condensed_state(
        TEMPERATURE, mu, PHI_RESPONSE, config,
        quadrature_order=REFERENCE_ORDER, cutoff_factor=REFERENCE_CUTOFF_FACTOR,
    )
    cutoff = reference.momentum_cutoff
    try:
        auxiliary_field_condensed_state(
            TEMPERATURE, mu, phi, normalized_config,
            quadrature_order=64, momentum_cutoff=cutoff,
        )
    except ValueError as error:
        normalized_domain_rejection = str(error)
    else:
        normalized_domain_rejection = None
    h = 1e-4
    records = []
    off_root_witnesses = []
    for t in TEMPERATURES:
        for order in ORDERS:
            state = auxiliary_field_condensed_state(
                t, mu, phi, config, quadrature_order=order, momentum_cutoff=cutoff
            )
            base = _profile_total_potential(phi, t, mu, config, order, cutoff)
            upper = _profile_total_potential(phi + h, t, mu, config, order, cutoff)
            lower = _profile_total_potential(phi - h, t, mu, config, order, cutoff)
            records.append({
                "temperature": t,
                "quadrature_order": order,
                "Phi": phi,
                "condensate_amplitude_sq": state.condensate_amplitude_sq,
                "auxiliary_gap_residual": state.auxiliary_gap_residual,
                "amplitude_stationarity_residual": state.condensed_stationarity_residual,
                "ward_phase_gap_sq": state.ward_phase_gap_sq,
                "charge_density_natural": state.charge_density,
                "entropy_density_natural": state.entropy_density,
                "analytic_Phi_residual": _phi_residual(phi, mu, config),
                "profiled_Phi_derivative_fd": (upper - lower) / (2.0 * h),
                "analytic_Phi_curvature": _phi_curvature(phi, config),
                "profiled_Phi_curvature_fd": (upper - 2.0 * base + lower) / (h * h),
            })
            off_root_upper = _profile_total_potential(PHI_RESPONSE + h, t, mu, config, order, cutoff)
            off_root_lower = _profile_total_potential(PHI_RESPONSE - h, t, mu, config, order, cutoff)
            off_root_witnesses.append({
                "temperature": t,
                "quadrature_order": order,
                "Phi": PHI_RESPONSE,
                "analytic_Phi_residual": _phi_residual(PHI_RESPONSE, mu, config),
                "profiled_Phi_derivative_fd": (off_root_upper - off_root_lower) / (2.0 * h),
            })
    check_fields = ("condensate_amplitude_sq", "charge_density_natural", "entropy_density_natural")
    order_differences = {
        str(t): {
            field: abs(records[2 * i][field] - records[2 * i + 1][field])
            for field in check_fields
        }
        for i, t in enumerate(TEMPERATURES)
    }
    checks = {
        "core_auxiliary_artifact_is_formal_only": (
            auxiliary["status"] == "PASS_FORMAL_WARD_PRESERVING_AUXILIARY_FIELD_CONDENSED_LANE"
            and auxiliary["major_result"]["closure_level"] == "CLOSED_FOR_LANE"
            and not auxiliary["contract"]["approximation"]["microscopic_2pi_or_controlled_1N_match"]
        ),
        "gaussian_root_remains_a_separate_blocked_branch": (
            gaussian["closure_level"] == "CLOSED_AS_NO_GO" and not gaussian["full_core_unlock"]
        ),
        "original_normalized_action_is_outside_auxiliary_domain": (
            normalized_config.matter.matter_kinetic == 1.0
            and config.matter.matter_kinetic > 1.0
            and normalized_domain_rejection == "auxiliary-field condensed lane requires Z > 1"
        ),
        "Phi_bracket_and_analytic_root": (
            left_residual < 0 < right_residual and abs(_phi_residual(phi, mu, config)) < 1e-12
        ),
        "joint_auxiliary_amplitude_Ward_and_Phi_stationarity": all(
            row["condensate_amplitude_sq"] > 0
            and abs(row["auxiliary_gap_residual"]) < 1e-9
            and abs(row["amplitude_stationarity_residual"]) < 1e-12
            and abs(row["ward_phase_gap_sq"]) < 1e-12
            and abs(row["profiled_Phi_derivative_fd"]) < 1e-7
            for row in records
        ),
        "local_Phi_curvature_positive_and_fd_agrees": all(
            row["analytic_Phi_curvature"] > 0
            and abs(row["analytic_Phi_curvature"] - row["profiled_Phi_curvature_fd"]) < 1e-5
            for row in records
        ),
        "off_root_envelope_derivative_agrees": all(
            abs(row["analytic_Phi_residual"] - row["profiled_Phi_derivative_fd"]) < 1e-7
            for row in off_root_witnesses
        ),
        "quadrature_refinement_agrees": all(
            difference < 1e-4
            for differences in order_differences.values() for difference in differences.values()
        ),
        "no_response_target_or_holdout_input": True,
    }
    sources = (
        AUXILIARY_AUDIT, GAUSSIAN_BOUNDARY,
        DOCS / "core/02_equations/o2/uet_o2_auxiliary_field_condensed.py",
        DOCS / "core/02_equations/o2/uet_o2_finite_density_eos.py",
        DOCS / "core/02_equations/covariant/uet_covariant_response.py",
        DOCS / "scripts/audit/audit_topic13_uet_o2_auxiliary_field_condensed.py",
        Path(__file__).resolve(),
        Path(__file__).with_name("test_t13_he4_formal_auxiliary_phi_joint_root.py").resolve(),
    )
    return {
        "schema_version": "t13-he4-formal-auxiliary-phi-joint-root-v1",
        "major_result_id": "T13_FORMAL_AUXILIARY_PHI_CONDENSATE_JOINT_STATIONARITY",
        "topic": "0.13",
        "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "what_is_closed": "At Core's fixed formal auxiliary-field configuration in a flat homogeneous partial-action composition, a positive-condensate root jointly satisfies the auxiliary, amplitude, Ward-gap and Phi stationarity equations at fixed chemical potential",
        "equation_or_mapping": {
            "auxiliary_solution": "M^2=Z*mu^2; rho=(M^2-m_eff^2(Phi)-2*lambda*I_R)/lambda",
            "Phi_stationarity": "0=epsilon_nc*[U'(Phi)-h*(Z*mu^2-m_eff^2(Phi))/(2*lambda)]",
            "Phi_curvature": "epsilon_nc*U''(Phi)-epsilon_nc^2*h^2/(2*lambda)>0",
            "thermal_boundary": "At fixed mu and fixed subtraction, this formal Phi equation has no explicit T; rho and thermodynamic observables still vary with T",
        },
        "units": {"lane": "natural", "Phi_and_mu": "natural energy", "rho": "natural amplitude squared", "SI_thermal_map": "not emitted"},
        "derivation_class": "conditional flat homogeneous composition of the declared response potential and existing formal auxiliary functional; stationary-envelope derivative with numerical finite-difference cross-check",
        "observable": "internal joint formal stationarity; not an admitted He-II or TTG operator",
        "data_role": "SYNTHETIC_FORMAL_ACTION_CONTROL_NO_RESPONSE_SOURCE",
        "reference_config": {
            "T_natural": TEMPERATURE, "mu_natural": mu, "Phi_seed": PHI_RESPONSE,
            "Z_auxiliary": config.matter.matter_kinetic,
            "Z_prior_normalized": normalized_config.matter.matter_kinetic,
            "fixed_momentum_cutoff": cutoff,
            "Phi_bracket": list(PHI_BRACKET),
            "Phi_root": phi,
            "normalized_domain_rejection": normalized_domain_rejection,
        },
        "temperature_and_resolution_records": records,
        "off_root_envelope_witnesses": off_root_witnesses,
        "quadrature_differences": order_differences,
        "checks": checks,
        "verification_status": "PASS_FORMAL_AUXILIARY_PHI_JOINT_ROOT" if all(checks.values()) else "REVIEW_REQUIRED",
        "evidence_artifacts": [{"path": path.relative_to(ROOT).as_posix(), "sha256": _sha(path)} for path in sources],
        "open_blockers": ["microscopic_2pi_or_controlled_1N_matching_missing", "physical_finite_temperature_renormalization_scheme_missing", "Z_1_normalized_branch_outside_auxiliary_domain", "material_map_and_independent_response_data_missing"],
        "controlling_blocker": "microscopic_2pi_or_controlled_1N_matching_missing",
        "dependency_unlocked": [],
        "full_core_unlock": False,
        "claim_boundary": "This is only a flat homogeneous formal joint stationary point for Core's declared Z>1 auxiliary-field configuration. It is not a full Hessian or curved/action-level stability result, cannot be transplanted to the previous Z=1 root, does not resolve microscopic matching or scheme identifiability, and does not predict He-II, alpha_Phi_K, TTG or Full Topic 13. No Xie 2026 holdout was used.",
    }


if __name__ == "__main__":
    OUTPUT.write_bytes((json.dumps(audit(), indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(OUTPUT)
