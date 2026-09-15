"""Finite-channel two-loop sunset-cut interface for Topic 13.

The local quartic one-loop retarded correction is a real tadpole.  The next
action-derived dissipative candidate is the order-lambda^2 elastic phase-space
cut.  This module evaluates the forward and reverse Bose-weighted channel
rates separately using the existing exact-kinematic transition kernel.

The result is deliberately a finite-channel cut interface.  It is not a full
one-particle-irreducible sunset integral, a continuum-limit renormalized
self-energy, a physical Kubo coefficient, or an SI observable.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

import numpy as np

from docs.core.uet_o2_action_derived_transition_kernel import (
    action_derived_transition_kernel_contract,
    action_derived_transition_kernel_state,
)
from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)


TWO_LOOP_SUNSET_CUT_STATUS = (
    "PASS_ACTION_DERIVED_TWO_LOOP_SUNSET_CUT_LANE"
)


@dataclass(frozen=True)
class TwoLoopSunsetCutState:
    """Finite-channel forward/reverse cut witnesses."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    quartic_coupling: float
    momentum_cutoff: float
    quadrature_order: int
    channel_count: int
    channel_forward_rates: tuple[float, ...]
    channel_reverse_rates: tuple[float, ...]
    channel_cut_rates: tuple[float, ...]
    forward_cut_total: float
    reverse_cut_total: float
    symmetric_cut_total: float
    nonzero_cut_channel_count: int
    detailed_balance_max_residual: float
    positive_semidefinite_min_eigenvalue: float
    collision_conservation_residual: float
    entropy_production_witness: float
    response_kms_max_residual: float
    response_fdt_max_residual: float
    one_loop_retarded_self_energy_remains_no_go: bool = True
    finite_channel_sunset_cut_completed: bool = True
    continuum_sunset_self_energy_completed: bool = False
    physical_retarded_self_energy_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FINITE_CHANNEL_TWO_LOOP_SUNSET_CUT_NOT_FULL_SELF_ENERGY"
    )


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _positive(value: float, name: str) -> float:
    result = _finite(value, name)
    if result <= 0.0:
        raise ValueError(f"{name} must be positive")
    return result


def two_loop_sunset_cut_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig | None = None,
    *,
    quadrature_order: int = 24,
    channel_count: int = 12,
    cutoff_factor: float = 36.0,
) -> TwoLoopSunsetCutState:
    """Evaluate the finite-channel order-lambda^2 phase-space cut."""

    if isinstance(quadrature_order, bool) or int(quadrature_order) != quadrature_order:
        raise ValueError("quadrature_order must be an integer")
    if isinstance(channel_count, bool) or int(channel_count) != channel_count:
        raise ValueError("channel_count must be an integer")
    if int(quadrature_order) < 24:
        raise ValueError("quadrature_order must be >= 24")
    if int(channel_count) < 4:
        raise ValueError("channel_count must be >= 4")
    cutoff_factor = _positive(cutoff_factor, "cutoff_factor")
    config = config or FiniteTemperatureO2QuasiparticleConfig()

    transition = action_derived_transition_kernel_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        quadrature_order=int(quadrature_order),
        channel_count=int(channel_count),
        cutoff_factor=cutoff_factor,
    )
    forward = np.asarray(transition.channel_rates, dtype=float)
    reverse = np.asarray(transition.channel_reverse_rates, dtype=float)
    if forward.shape != reverse.shape or not forward.size:
        raise ValueError("forward and reverse channel rates must have equal nonzero shape")
    if np.any(forward <= 0.0) or np.any(reverse <= 0.0):
        raise FloatingPointError("sunset-cut channel rates must be positive")
    cut = 0.5 * (forward + reverse)
    balance = np.abs(forward - reverse) / np.maximum(np.maximum(forward, reverse), 1.0e-300)
    kms_residual = max(
        abs(value - target) / max(abs(target), 1.0e-300)
        for value, target in zip(transition.kms_ratio, transition.kms_target_ratio)
    )
    fdt_residual = max(
        abs(value - target) / max(abs(target), 1.0e-300)
        for value, target in zip(transition.kms_noise, transition.kms_noise_target)
    )
    values = (
        *forward,
        *reverse,
        *cut,
        float(np.sum(forward)),
        float(np.sum(reverse)),
        float(np.sum(cut)),
        float(np.max(balance)),
        kms_residual,
        fdt_residual,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("sunset-cut state is not finite")
    return TwoLoopSunsetCutState(
        temperature=transition.temperature,
        chemical_potential=transition.chemical_potential,
        space_response=transition.space_response,
        effective_mass=transition.effective_mass,
        quartic_coupling=float(config.eos.matter.matter_quartic),
        momentum_cutoff=transition.momentum_cutoff,
        quadrature_order=transition.quadrature_order,
        channel_count=transition.channel_count,
        channel_forward_rates=tuple(float(value) for value in forward),
        channel_reverse_rates=tuple(float(value) for value in reverse),
        channel_cut_rates=tuple(float(value) for value in cut),
        forward_cut_total=float(np.sum(forward)),
        reverse_cut_total=float(np.sum(reverse)),
        symmetric_cut_total=float(np.sum(cut)),
        nonzero_cut_channel_count=int(np.count_nonzero(cut > 0.0)),
        detailed_balance_max_residual=float(np.max(balance)),
        positive_semidefinite_min_eigenvalue=transition.positive_semidefinite_min_eigenvalue,
        collision_conservation_residual=transition.collision_conservation_residual,
        entropy_production_witness=transition.entropy_production_witness,
        response_kms_max_residual=float(kms_residual),
        response_fdt_max_residual=float(fdt_residual),
    )


def two_loop_sunset_cut_contract() -> dict[str, Any]:
    """Return the equations and the finite-channel claim boundary."""

    transition_contract = action_derived_transition_kernel_contract()
    return {
        "status": TWO_LOOP_SUNSET_CUT_STATUS,
        "equations": {
            "forward_sunset_cut": (
                "W_>^(2)=integral dPi_1...dPi_4 (2*pi)^4 delta^4(p1+p2-p3-p4) "
                "|M_22|^2 f1*f2*(1+f3)*(1+f4)"
            ),
            "reverse_sunset_cut": (
                "W_<^(2)=integral dPi_1...dPi_4 (2*pi)^4 delta^4(p1+p2-p3-p4) "
                "|M_22|^2 f3*f4*(1+f1)*(1+f2)"
            ),
            "action_order": "|M_22|^2 is order lambda^2 in the declared action-derived elastic branch",
            "symmetric_cut": "W_cut^(2)=0.5*(W_>^(2)+W_<^(2)) > 0 for an active channel",
            "equilibrium_detailed_balance": "W_>^(2)/W_<^(2)=1 when charge and four-momentum are conserved",
            "retarded_self_energy_boundary": "Im Sigma_R^(2) is not emitted until the continuum 1PI sunset integral and renormalization are matched",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_chemical_potential_mass_momentum_energy": "energy",
            "cut_rate": "formal natural-unit phase-space rate",
            "self_energy": "not emitted by this lane",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": (
            "action-derived finite-channel elastic phase-space cut with separately evaluated "
            "forward/reverse Bose weights"
        ),
        "observable": "positive finite-channel cut weight, detailed balance, and response KMS/FDT boundary",
        "data_role": "ACTION_DERIVED_INTERNAL_NO_SOURCE_ROWS_NO_HOLDOUT",
        "inheritance": {
            "transition_kernel_equations": transition_contract["equations"],
            "transition_kernel_boundary": "inherited only for exact finite-channel kinematics and algebraic response",
        },
        "excluded": {
            "full_1PI_sunset_self_energy": True,
            "continuum_limit": True,
            "physical_retarded_self_energy": True,
            "physical_kubo_coefficient": True,
            "entropy_current_heat_flux_balance": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": (
            "This closes only the first nonzero action-derived finite-channel two-loop "
            "phase-space cut interface after the one-loop tadpole no-go. It does not close "
            "the continuum 1PI sunset self-energy, renormalization, physical Kubo/transport, "
            "entropy-current balance, SI Phi mapping, alpha_Phi_K, TTG validation, or Full Topic 13."
        ),
    }


__all__ = [
    "TWO_LOOP_SUNSET_CUT_STATUS",
    "TwoLoopSunsetCutState",
    "two_loop_sunset_cut_state",
    "two_loop_sunset_cut_contract",
]
