"""Same-kernel tagged elastic loss, gain, and retarded width for Topic 13.

The width is derived from the same charge-resolved contact-plus-Phi amplitude
and exact center-of-mass event kernel as the invariant Galerkin collision
operator. Detailed balance separates the tagged out-scattering rate from the
retarded pole width. This remains a tree elastic normal-state result, not a
dressed or resonant self-consistent self-energy.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

import numpy as np

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_invariant_galerkin_collision_operator import (
    _center_of_mass_frame,
    _outgoing_center_of_mass_event,
)
from docs.core.uet_o2_invariant_rate_collision_operator import _action_amplitude
from docs.core.uet_o2_kinetic_collision_kubo import _bose, _normal_state_inputs


SAME_KERNEL_TAGGED_WIDTH_STATUS = (
    "PASS_SCOPED_SAME_KERNEL_TREE_LOSS_GAIN_RETARDED_WIDTH"
)


@dataclass(frozen=True)
class SameKernelTaggedWidthState:
    temperature: float
    chemical_potential: float
    effective_mass: float
    momentum_cutoff: float
    tagged_momenta: tuple[float, ...]
    tagged_energies: tuple[float, ...]
    species_signs: tuple[int, int]
    widths_by_tag_momentum_target: tuple[
        tuple[tuple[float, float], ...],
        tuple[tuple[float, float], ...],
    ]
    total_widths_by_tag_momentum: tuple[
        tuple[float, ...],
        tuple[float, ...],
    ]
    gain_widths_by_tag_momentum_target: tuple[
        tuple[tuple[float, float], ...],
        tuple[tuple[float, float], ...],
    ]
    total_gain_widths_by_tag_momentum: tuple[
        tuple[float, ...],
        tuple[float, ...],
    ]
    retarded_spectral_widths_by_tag_momentum: tuple[
        tuple[float, ...],
        tuple[float, ...],
    ]
    retarded_self_energy_imaginary_by_tag_momentum: tuple[
        tuple[float, ...],
        tuple[float, ...],
    ]
    radial_order: int
    incoming_angular_order: int
    outgoing_angular_order: int
    outgoing_azimuth_order: int
    event_count: int
    maximum_event_energy_residual: float
    maximum_event_momentum_residual: float
    maximum_detailed_balance_residual: float
    maximum_kms_gain_loss_residual: float
    minimum_width: float
    maximum_width: float
    minimum_tagged_loss_width: float
    maximum_tagged_loss_width: float
    width_energy_dimension: int = 1
    same_kernel_amplitude_used: bool = True
    same_center_of_mass_event_kernel_used: bool = True
    dressed_self_consistent_width_completed: bool = False
    resonant_resummation_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    xie_2026_accessed: bool = False
    parameter_fitting_performed: bool = False


def same_kernel_tagged_width_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    tagged_momenta: tuple[float, ...] = (0.5, 1.0, 2.0),
    radial_order: int = 16,
    incoming_angular_order: int = 8,
    outgoing_angular_order: int = 8,
    outgoing_azimuth_order: int = 12,
    cutoff_factor: float = 12.0,
) -> SameKernelTaggedWidthState:
    """Evaluate charge-resolved tagged elastic widths on a momentum grid."""

    controls = {
        "radial_order": (radial_order, 4),
        "incoming_angular_order": (incoming_angular_order, 4),
        "outgoing_angular_order": (outgoing_angular_order, 4),
        "outgoing_azimuth_order": (outgoing_azimuth_order, 4),
    }
    for name, (value, minimum) in controls.items():
        if isinstance(value, bool) or int(value) != value or int(value) < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    if not tagged_momenta:
        raise ValueError("tagged_momenta must not be empty")
    momenta = tuple(float(value) for value in tagged_momenta)
    if any(not np.isfinite(value) or value <= 0.0 for value in momenta):
        raise ValueError("tagged momenta must be positive and finite")
    if tuple(sorted(momenta)) != momenta or len(set(momenta)) != len(momenta):
        raise ValueError("tagged_momenta must be strictly increasing")
    if not np.isfinite(cutoff_factor) or cutoff_factor <= 0.0:
        raise ValueError("cutoff_factor must be positive and finite")
    config = config or FiniteTemperatureO2QuasiparticleConfig()
    response = config.eos.response
    if abs(space_response - response.phi_equilibrium) > config.phase_tolerance:
        raise NotImplementedError(
            "the same-kernel width v1 requires the declared normal response background"
        )
    t, mu, mass, mu_eff, _quartic = _normal_state_inputs(
        temperature, chemical_potential, space_response, config
    )
    cutoff = cutoff_factor * max(t, mass, abs(mu_eff))
    radial_x, radial_w = np.polynomial.legendre.leggauss(int(radial_order))
    radial_p = 0.5 * cutoff * (radial_x + 1.0)
    radial_dp = 0.5 * cutoff * radial_w
    incoming_cos, incoming_w = np.polynomial.legendre.leggauss(
        int(incoming_angular_order)
    )
    outgoing_cos, outgoing_w = np.polynomial.legendre.leggauss(
        int(outgoing_angular_order)
    )
    azimuths = 2.0 * pi * (
        np.arange(int(outgoing_azimuth_order), dtype=float) + 0.5
    ) / int(outgoing_azimuth_order)
    azimuth_weight = 2.0 * pi / int(outgoing_azimuth_order)
    signs = (-1, 1)
    loss_widths = np.zeros((2, len(momenta), 2), dtype=float)
    gain_widths = np.zeros((2, len(momenta), 2), dtype=float)
    energies_one = tuple(sqrt(momentum * momentum + mass * mass) for momentum in momenta)
    max_energy_residual = 0.0
    max_momentum_residual = 0.0
    max_balance = 0.0
    event_count = 0

    for momentum_index, (p1_mag, e1) in enumerate(zip(momenta, energies_one)):
        p1 = np.array((0.0, 0.0, p1_mag))
        external_normalization = 1.0 / (2.0 * e1)
        for p2_mag, dp2 in zip(radial_p, radial_dp):
            e2 = sqrt(float(p2_mag * p2_mag + mass * mass))
            for cosine_in, weight_in in zip(incoming_cos, incoming_w):
                sine_in = sqrt(1.0 - float(cosine_in) ** 2)
                p2 = np.array(
                    (float(p2_mag) * sine_in, 0.0, float(p2_mag) * float(cosine_in))
                )
                invariant_s, p_star, root_s, boost, ex, ey, ez = (
                    _center_of_mass_frame(e1, p1, e2, p2, mass)
                )
                d_pi_two = (
                    2.0
                    * pi
                    * p2_mag
                    * p2_mag
                    * dp2
                    * weight_in
                    / ((2.0 * pi) ** 3 * 2.0 * e2)
                )
                for cosine_out, weight_out in zip(outgoing_cos, outgoing_w):
                    d_phi_two = (
                        p_star
                        / (16.0 * pi * pi * root_s)
                        * weight_out
                        * azimuth_weight
                    )
                    for azimuth in azimuths:
                        e3, p3, e4, p4 = _outgoing_center_of_mass_event(
                            root_s,
                            p_star,
                            boost,
                            ex,
                            ey,
                            ez,
                            float(cosine_out),
                            float(azimuth),
                        )
                        max_energy_residual = max(
                            max_energy_residual, abs(e1 + e2 - e3 - e4)
                        )
                        max_momentum_residual = max(
                            max_momentum_residual,
                            float(np.linalg.norm(p1 + p2 - p3 - p4)),
                        )
                        for tag_index, q1 in enumerate(signs):
                            f1 = float(_bose(e1 - q1 * mu_eff, t))
                            for target_index, q2 in enumerate(signs):
                                f2 = float(_bose(e2 - q2 * mu_eff, t))
                                f3 = float(_bose(e3 - q1 * mu_eff, t))
                                f4 = float(_bose(e4 - q2 * mu_eff, t))
                                forward = f1 * f2 * (1.0 + f3) * (1.0 + f4)
                                reverse = f3 * f4 * (1.0 + f1) * (1.0 + f2)
                                max_balance = max(
                                    max_balance,
                                    abs(forward - reverse)
                                    / max(forward, reverse, 1.0e-300),
                                )
                                amplitude = _action_amplitude(
                                    invariant_s,
                                    float(cosine_out),
                                    (q1, q2, q1, q2),
                                    config,
                                )
                                final_symmetry = 2.0 if q1 == q2 else 1.0
                                common = (
                                    external_normalization
                                    * d_pi_two
                                    * d_phi_two
                                    * amplitude
                                    * amplitude
                                    / final_symmetry
                                )
                                loss_widths[tag_index, momentum_index, target_index] += (
                                    common * f2 * (1.0 + f3) * (1.0 + f4)
                                )
                                gain_widths[tag_index, momentum_index, target_index] += (
                                    common * (1.0 + f2) * f3 * f4
                                )
                                event_count += 1
    total_loss_widths = np.sum(loss_widths, axis=2)
    total_gain_widths = np.sum(gain_widths, axis=2)
    retarded_widths = total_loss_widths - total_gain_widths
    occupations = np.asarray([
        [float(_bose(energy - sign * mu_eff, t)) for energy in energies_one]
        for sign in signs
    ])
    kms_expected = total_loss_widths / (1.0 + occupations)
    kms_scale = np.maximum(
        np.maximum(np.abs(kms_expected), np.abs(retarded_widths)), 1.0e-300
    )
    kms_residual = float(
        np.max(np.abs(retarded_widths - kms_expected) / kms_scale)
    )
    if (
        np.any(~np.isfinite(total_loss_widths))
        or np.any(~np.isfinite(total_gain_widths))
        or np.any(~np.isfinite(retarded_widths))
        or np.any(total_loss_widths <= 0.0)
        or np.any(total_gain_widths <= 0.0)
        or np.any(retarded_widths <= 0.0)
    ):
        raise FloatingPointError(
            "loss, gain, and retarded widths must be positive and finite"
        )
    self_energy_imaginary = (
        -2.0 * np.asarray(energies_one)[None, :] * retarded_widths
    )
    return SameKernelTaggedWidthState(
        temperature=t,
        chemical_potential=mu,
        effective_mass=mass,
        momentum_cutoff=float(cutoff),
        tagged_momenta=momenta,
        tagged_energies=tuple(float(value) for value in energies_one),
        species_signs=signs,
        widths_by_tag_momentum_target=tuple(
            tuple(
                tuple(float(value) for value in loss_widths[tag, momentum])
                for momentum in range(len(momenta))
            )
            for tag in range(2)
        ),
        total_widths_by_tag_momentum=tuple(
            tuple(float(value) for value in total_loss_widths[tag])
            for tag in range(2)
        ),
        gain_widths_by_tag_momentum_target=tuple(
            tuple(
                tuple(float(value) for value in gain_widths[tag, momentum])
                for momentum in range(len(momenta))
            )
            for tag in range(2)
        ),
        total_gain_widths_by_tag_momentum=tuple(
            tuple(float(value) for value in total_gain_widths[tag])
            for tag in range(2)
        ),
        retarded_spectral_widths_by_tag_momentum=tuple(
            tuple(float(value) for value in retarded_widths[tag])
            for tag in range(2)
        ),
        retarded_self_energy_imaginary_by_tag_momentum=tuple(
            tuple(float(value) for value in self_energy_imaginary[tag])
            for tag in range(2)
        ),
        radial_order=int(radial_order),
        incoming_angular_order=int(incoming_angular_order),
        outgoing_angular_order=int(outgoing_angular_order),
        outgoing_azimuth_order=int(outgoing_azimuth_order),
        event_count=event_count,
        maximum_event_energy_residual=max_energy_residual,
        maximum_event_momentum_residual=max_momentum_residual,
        maximum_detailed_balance_residual=max_balance,
        maximum_kms_gain_loss_residual=kms_residual,
        minimum_width=float(np.min(retarded_widths)),
        maximum_width=float(np.max(retarded_widths)),
        minimum_tagged_loss_width=float(np.min(total_loss_widths)),
        maximum_tagged_loss_width=float(np.max(total_loss_widths)),
    )


def same_kernel_tagged_width_contract() -> dict[str, object]:
    return {
        "status": SAME_KERNEL_TAGGED_WIDTH_STATUS,
        "equations": {
            "tagged_loss_width": "Gamma_out,q(p)=1/(2E_p)*sum_r integral dPi2 dPhi2 |M_qr|^2 f_r(1+f3)(1+f4)/S_final",
            "tagged_gain_width": "Gamma_in,q(p)=1/(2E_p)*sum_r integral dPi2 dPhi2 |M_qr|^2 (1+f_r)f3 f4/S_final",
            "kms_retarded_width": "Gamma_R,q=Gamma_out,q-Gamma_in,q=Gamma_out,q/(1+f_q)",
            "spectral_interface": "-Im Sigma_R,q(E_p,p)=2E_p Gamma_R,q(p)",
            "cross_section_equivalence": "Gamma_out,q=sum_r integral d^3p2/(2pi)^3 f_r v_Moller integral dOmega (dSigma_qr/dOmega)(1+f3)(1+f4)",
        },
        "unit_contract": {
            "dPi2": 2,
            "dPhi2": 0,
            "external_1_over_2E": -1,
            "Gamma": 1,
            "Gamma_out": 1,
            "Gamma_in": 1,
            "Gamma_R": 1,
            "Im_Sigma_R": 2,
        },
        "included": {
            "same_action_amplitude": True,
            "same_center_of_mass_event_kernel": True,
            "charge_resolved_tag_and_target": True,
            "momentum_resolved_width": True,
            "kms_gain_loss_separation": True,
            "independent_cross_section_form_available": True,
        },
        "excluded": {
            "dressed_self_consistency": True,
            "resonant_resummation": True,
            "number_changing_response_channels": True,
            "vector_heat_current_ladder": True,
            "physical_Kubo_or_SI_coefficient": True,
            "external_validation": True,
        },
        "claim_boundary": (
            "Tree elastic same-kernel tagged loss/gain and retarded width only; not a "
            "dressed self-consistent width, full damping rate or transport coefficient."
        ),
    }


__all__ = [
    "SAME_KERNEL_TAGGED_WIDTH_STATUS",
    "SameKernelTaggedWidthState",
    "same_kernel_tagged_width_state",
    "same_kernel_tagged_width_contract",
]
