"""Conditional measurement design for a standard Cattaneo thermal comparator.

This is not an admitted UET or He-II two-fluid response operator. In
particular, its wave speed must not be identified with second sound.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

import numpy as np


def poles(*, heat_capacity: float, conductivity: float, relaxation: float, wave_number: float) -> np.ndarray:
    """Roots of tau*s**2 + s + (kappa/c)*q**2 = 0 in SI units."""
    if min(heat_capacity, conductivity, relaxation, wave_number) <= 0:
        raise ValueError("positive c, kappa, tau and q required")
    diffusivity = conductivity / heat_capacity
    return np.roots([relaxation, 1.0, diffusivity * wave_number**2])


def inverted_coefficients(*, omega: float, gamma: float, wave_number: float, heat_capacity: float) -> dict[str, float]:
    """Invert an underdamped pole pair s=-gamma +/- i*omega."""
    if min(omega, gamma, wave_number, heat_capacity) <= 0:
        raise ValueError("positive omega, gamma, q and independently measured c required")
    relaxation = 1.0 / (2.0 * gamma)
    diffusivity = relaxation * (omega**2 + gamma**2) / wave_number**2
    return {
        "relaxation_s": relaxation,
        "diffusivity_m2_per_s": diffusivity,
        "conductivity_W_per_m_K": heat_capacity * diffusivity,
    }


def conductivity_relative_uncertainty(
    *, omega: float, gamma: float, wave_number: float, heat_capacity: float,
    sigma_omega: float, sigma_gamma: float, sigma_wave_number: float, sigma_heat_capacity: float,
) -> float:
    """First-order relative uncertainty for independent inputs only."""
    if min(omega, gamma, wave_number, heat_capacity) <= 0:
        raise ValueError("positive central values required")
    if min(sigma_omega, sigma_gamma, sigma_wave_number, sigma_heat_capacity) < 0:
        raise ValueError("nonnegative standard uncertainties required")
    pole_sum = omega**2 + gamma**2
    terms = (
        (2.0 * omega / pole_sum * sigma_omega) ** 2,
        ((2.0 * gamma / pole_sum - 1.0 / gamma) * sigma_gamma) ** 2,
        (2.0 * sigma_wave_number / wave_number) ** 2,
        (sigma_heat_capacity / heat_capacity) ** 2,
    )
    return float(np.sqrt(sum(terms)))


def mode_quadratic_balance(*, amplitude_temperature: float, amplitude_flux: float,
                           heat_capacity: float, conductivity: float,
                           relaxation: float, wave_number: float) -> dict[str, float]:
    """Period-average stability functional for T=A cos(qx), j=B sin(qx).

    The functional density has units J*K/m^3, not physical energy density.
    """
    if min(heat_capacity, conductivity, relaxation, wave_number) <= 0:
        raise ValueError("positive c, kappa, tau and q required")
    a_rate = -wave_number * amplitude_flux / heat_capacity
    b_rate = (conductivity * wave_number * amplitude_temperature - amplitude_flux) / relaxation
    functional = (heat_capacity * amplitude_temperature**2
                  + relaxation * amplitude_flux**2 / conductivity) / 4.0
    rate = (heat_capacity * amplitude_temperature * a_rate
            + relaxation * amplitude_flux * b_rate / conductivity) / 2.0
    dissipation = amplitude_flux**2 / (2.0 * conductivity)
    return {"quadratic_functional": functional, "rate": rate, "dissipation": dissipation,
            "ledger_residual": rate + dissipation}


def audit() -> dict:
    # All numbers below are synthetic protocol illustrations, not helium data.
    omega, wave_number, heat_capacity = 100.0, 1000.0, 1000.0
    witnesses = []
    for relaxation in (0.01, 0.04):
        gamma = 1.0 / (2.0 * relaxation)
        result = inverted_coefficients(omega=omega, gamma=gamma,
                                        wave_number=wave_number, heat_capacity=heat_capacity)
        roots = poles(heat_capacity=heat_capacity,
                      conductivity=result["conductivity_W_per_m_K"],
                      relaxation=relaxation, wave_number=wave_number)
        ledger = mode_quadratic_balance(amplitude_temperature=0.1, amplitude_flux=0.2,
                                        heat_capacity=heat_capacity,
                                        conductivity=result["conductivity_W_per_m_K"],
                                        relaxation=relaxation, wave_number=wave_number)
        witnesses.append({**result, "gamma_per_s": gamma,
                          "omega_per_s": float(max(abs(root.imag) for root in roots)),
                          "pole_real_parts_per_s": [float(root.real) for root in roots],
                          "quadratic_balance_residual": ledger["ledger_residual"]})
    uncertainty = conductivity_relative_uncertainty(
        omega=omega, gamma=witnesses[0]["gamma_per_s"], wave_number=wave_number,
        heat_capacity=heat_capacity, sigma_omega=5.0, sigma_gamma=2.5,
        sigma_wave_number=10.0, sigma_heat_capacity=50.0,
    )
    checks = {
        "same_oscillation_frequency": abs(witnesses[0]["omega_per_s"] - witnesses[1]["omega_per_s"]) < 1e-10,
        "distinct_positive_transport_pairs": all(w["conductivity_W_per_m_K"] > 0 for w in witnesses)
        and witnesses[0]["relaxation_s"] != witnesses[1]["relaxation_s"]
        and witnesses[0]["conductivity_W_per_m_K"] != witnesses[1]["conductivity_W_per_m_K"],
        "underdamped_stable_poles": all(all(real < 0 for real in w["pole_real_parts_per_s"]) for w in witnesses),
        "mode_quadratic_balance": all(abs(w["quadratic_balance_residual"]) < 1e-12 for w in witnesses),
    }
    docs = Path(__file__).resolve().parents[4]
    sources = (
        Path(__file__).resolve(),
        Path(__file__).with_name("test_t13_thermal_pole_measurement_design.py").resolve(),
        docs / "core" / "03_lanes" / "thermal" / "uet_dynamic_thermoelastic_response.py",
    )
    return {
        "schema_version": "t13-thermal-pole-measurement-design-v1",
        "major_result_id": "T13_CATTANEO_POLE_MEASUREMENT_DESIGN_CONTROL",
        "topic": "0.13", "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
        "what_is_closed": "Conditional identifiability and measurement design for a standard linear Cattaneo comparator",
        "equation_or_mapping": {
            "balance": "c*d_t(theta)+d_x(j)=0; tau*d_t(j)+j=-kappa*d_x(theta)",
            "dispersion": "tau*s^2+s+(kappa/c)*q^2=0; s=-gamma+/-i*omega",
            "inversion": "tau=1/(2*gamma); D=tau*(omega^2+gamma^2)/q^2; kappa=c*D",
            "same_frequency_family": "for any tau>0 at fixed omega,q,c: gamma=1/(2*tau), kappa=c*tau*(omega^2+gamma^2)/q^2",
            "quadratic_balance": "V=integral[c*theta^2/2+tau*j^2/(2*kappa)]dx; dV/dt=-integral[j^2/kappa]dx for periodic/no-flux boundaries; V is not physical SI energy",
        },
        "units": {"theta": "K", "j": "W/m^2", "c": "J/(m^3 K)",
                  "kappa": "W/(m K)", "tau": "s", "q": "1/m", "omega_gamma": "1/s",
                  "quadratic_functional_density": "J*K/m^3 (not SI energy density)"},
        "derivation_class": "analytic conditional comparator proof with synthetic numerical witnesses",
        "observable": "mode oscillation frequency plus exponential decay rate at known wave number and independently measured volumetric heat capacity",
        "data_role": "SYNTHETIC_COMPARATOR_NO_HELIUM_VALIDATION",
        "witnesses": witnesses,
        "synthetic_input_uncertainties": {"sigma_omega_per_s": 5.0, "sigma_gamma_per_s": 2.5,
                                          "sigma_q_per_m": 10.0, "sigma_c_J_per_m3_K": 50.0,
                                          "assumed_independent": True},
        "synthetic_relative_sigma_conductivity": uncertainty,
        "measurement_requirements": [
            "same-state mode frequency and decay rate from the same identified pole pair",
            "independently measured wave number/mode geometry and volumetric heat capacity",
            "source and detector transfer functions separated from intrinsic pole estimates",
            "row-level covariance for frequency, decay rate, geometry and heat capacity",
            "a physically admitted two-fluid operator before applying this design to He-II",
        ],
        "evidence_artifacts": [
            {"path": path.relative_to(docs).as_posix(),
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sources
        ],
        "checks": checks,
        "verification_status": "ANALYTIC_AND_SYNTHETIC_CONTROL_PASS" if all(checks.values()) else "FAIL",
        "open_blockers": ["admitted_UET_HeII_two_fluid_response_operator",
                          "state_matched_independent_heat_capacity_and_mode_protocol",
                          "physical_dissipative_coefficients_and_covariance"],
        "controlling_blocker": "admitted_UET_HeII_two_fluid_response_operator",
        "dependency_unlocked": [], "full_core_unlock": False,
        "claim_boundary": "This proves nonidentifiability from frequency alone and local identifiability from frequency, decay and independent c only in the declared standard comparator. The quadratic stability functional is not physical SI energy. It is not UET second-sound prediction, experimental calibration, TTG validation or Full Topic 13 closure.",
    }


if __name__ == "__main__":
    output = Path(__file__).resolve().parents[2] / "Result" / "artifacts" / "t13_thermal_pole_measurement_design_control.json"
    output.write_bytes((json.dumps(audit(), indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(output)
