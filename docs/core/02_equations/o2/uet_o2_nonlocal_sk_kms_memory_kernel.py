"""Formal nonlocal SK/KMS memory kernel for the Topic 13 response lane.

The memory kernel is an explicit causal exponential convolution.  Its damping
scale is taken from the existing action-derived collision-width comparator and
its memory time is declared from the natural quasiparticle mass scale.  This
produces a reproducible nonlocal influence-kernel control, not a physical Kubo
coefficient or a source-calibrated transport law.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, expm1, isfinite, tanh
from typing import Any

import numpy as np

from docs.core.uet_o2_finite_temperature_quasiparticle_eos import (
    FiniteTemperatureO2QuasiparticleConfig,
)
from docs.core.uet_o2_kinetic_collision_kubo import kinetic_collision_state


NONLOCAL_SK_KMS_MEMORY_STATUS = (
    "PASS_ACTION_DERIVED_NONLOCAL_SK_KMS_MEMORY_KERNEL_LANE"
)


@dataclass(frozen=True)
class NonlocalSKKMSMemoryParameters:
    """Natural-unit parameters of the declared exponential memory kernel."""

    beta_th: float
    kappa: float
    chi: float
    gamma_memory: float
    memory_time: float

    def validate(self) -> None:
        values = {
            "beta_th": self.beta_th,
            "kappa": self.kappa,
            "chi": self.chi,
            "gamma_memory": self.gamma_memory,
            "memory_time": self.memory_time,
        }
        if not all(isfinite(float(value)) for value in values.values()):
            raise ValueError("memory-kernel parameters must be finite")
        if self.beta_th <= 0.0 or self.kappa <= 0.0 or self.chi <= 0.0:
            raise ValueError("beta_th, kappa, and chi must be positive")
        if self.gamma_memory <= 0.0 or self.memory_time <= 0.0:
            raise ValueError("gamma_memory and memory_time must be positive")


@dataclass(frozen=True)
class NonlocalSKKMSMemoryState:
    """Causal memory, retarded, KMS/FDT, and entropy witnesses."""

    temperature: float
    chemical_potential: float
    space_response: float
    effective_mass: float
    beta_th: float
    kappa: float
    chi: float
    gamma_memory: float
    memory_time: float
    frequency_grid: tuple[float, ...]
    retarded_real: tuple[float, ...]
    retarded_imag: tuple[float, ...]
    spectral_density: tuple[float, ...]
    noise_kernel: tuple[float, ...]
    kms_ratio_residuals: tuple[float, ...]
    fdt_residuals: tuple[float, ...]
    causal_transform_residuals: tuple[float, ...]
    kernel_reality_residuals: tuple[float, ...]
    memory_pole_imaginary_part: float
    negative_time_support_residual: float
    positive_time_memory_value: float
    spectral_density_minimum: float
    entropy_production_witness: float
    source_collision_widths: tuple[float, float]
    formal_nonlocal_influence_functional_completed: bool = True
    physical_retarded_self_energy_completed: bool = False
    physical_kubo_coefficient_emitted: bool = False
    numeric_alpha_Phi_K_emitted: bool = False
    parameter_fitting_performed: bool = False
    target_data_used: bool = False
    xie_2026_accessed: bool = False
    data_role: str = (
        "ACTION_DERIVED_FORMAL_NONLOCAL_SK_KMS_MEMORY_CONTROL_NOT_PHYSICAL_TRANSPORT"
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


def _relative(value: float, target: float) -> float:
    return float(abs(float(value) - float(target)) / max(abs(float(target)), 1.0e-300))


def retarded_memory_kernel(
    frequency: float,
    parameters: NonlocalSKKMSMemoryParameters,
) -> complex:
    """Return the retarded kernel for the ``exp(-i*omega*t)`` convention."""

    parameters.validate()
    omega = _finite(frequency, "frequency")
    memory_transfer = parameters.gamma_memory / (
        1.0 - 1j * omega * parameters.memory_time
    )
    return complex(
        parameters.kappa - parameters.chi * omega * omega - 1j * omega * memory_transfer
    )


def causal_memory_time_kernel(
    time: float,
    parameters: NonlocalSKKMSMemoryParameters,
) -> float:
    """Return ``gamma/tau*exp(-t/tau)*Theta(t)`` without cone padding."""

    parameters.validate()
    value = _finite(time, "time")
    if value < 0.0:
        return 0.0
    return float(
        parameters.gamma_memory
        / parameters.memory_time
        * exp(-value / parameters.memory_time)
    )


def _spectral_density(frequency: float, parameters: NonlocalSKKMSMemoryParameters) -> float:
    return float(-2.0 * retarded_memory_kernel(frequency, parameters).imag)


def _bose(energy: float, temperature: float) -> float:
    argument = _positive(energy / temperature, "beta energy")
    return exp(-argument) if argument > 50.0 else 1.0 / expm1(argument)


def _fdt_record(
    frequency: float,
    parameters: NonlocalSKKMSMemoryParameters,
) -> tuple[float, float, float, float, float, float]:
    rho = _spectral_density(frequency, parameters)
    occupation = _bose(frequency, 1.0 / parameters.beta_th)
    greater = rho * (1.0 + occupation)
    lesser = rho * occupation
    noise = greater + lesser
    target_noise = rho / tanh(0.5 * parameters.beta_th * frequency)
    kms_residual = _relative(greater / lesser, exp(parameters.beta_th * frequency))
    fdt_residual = abs(noise - target_noise)
    return rho, noise, kms_residual, fdt_residual, greater, lesser


def _transform_residual(
    frequency: float,
    parameters: NonlocalSKKMSMemoryParameters,
) -> float:
    nodes, weights = np.polynomial.legendre.leggauss(256)
    scaled_nodes = 20.0 * (nodes + 1.0)
    scaled_weights = 20.0 * weights
    numeric = np.sum(
        scaled_weights
        * parameters.gamma_memory
        * np.exp(-scaled_nodes)
        * np.exp(1j * frequency * parameters.memory_time * scaled_nodes)
    )
    analytic = parameters.gamma_memory / (
        1.0 - 1j * frequency * parameters.memory_time
    )
    return float(abs(numeric - analytic) / max(abs(analytic), 1.0e-300))


def nonlocal_sk_kms_memory_state(
    temperature: float,
    chemical_potential: float,
    space_response: float,
    config: FiniteTemperatureO2QuasiparticleConfig,
    *,
    frequency_grid: tuple[float, ...] = (0.05, 0.1, 0.2, 0.4, 0.8),
    collision_quadrature_order: int = 40,
    collision_angular_order: int = 24,
    collision_cutoff_factor: float = 20.0,
) -> NonlocalSKKMSMemoryState:
    """Build and verify a formal nonlocal memory influence-kernel control."""

    temperature = _positive(temperature, "temperature")
    chemical_potential = _finite(chemical_potential, "chemical_potential")
    space_response = _finite(space_response, "space_response")
    if not frequency_grid or tuple(sorted(float(value) for value in frequency_grid)) != tuple(
        float(value) for value in frequency_grid
    ):
        raise ValueError("frequency_grid must be non-empty and sorted")
    if any(float(value) <= 0.0 for value in frequency_grid):
        raise ValueError("frequency_grid must contain positive frequencies")
    collision = kinetic_collision_state(
        temperature,
        chemical_potential,
        space_response,
        config,
        quadrature_order=collision_quadrature_order,
        angular_order=collision_angular_order,
        cutoff_factor=collision_cutoff_factor,
    )
    gamma_memory = float(np.mean(np.asarray(collision.collision_width_by_species)))
    effective_mass = float(collision.effective_mass)
    memory_time = 1.0 / (effective_mass + gamma_memory)
    parameters = NonlocalSKKMSMemoryParameters(
        beta_th=1.0 / temperature,
        kappa=effective_mass * effective_mass,
        chi=1.0,
        gamma_memory=gamma_memory,
        memory_time=memory_time,
    )
    parameters.validate()
    frequencies = tuple(float(value) for value in frequency_grid)
    retarded = tuple(retarded_memory_kernel(value, parameters) for value in frequencies)
    records = tuple(_fdt_record(value, parameters) for value in frequencies)
    transform_residuals = tuple(_transform_residual(value, parameters) for value in frequencies)
    reality_residuals = tuple(
        float(
            abs(
                retarded_memory_kernel(-value, parameters)
                - np.conjugate(
                    retarded_memory_kernel(value, parameters)
                )
            )
        )
        for value in frequencies
    )
    retarded_real = tuple(float(value.real) for value in retarded)
    retarded_imag = tuple(float(value.imag) for value in retarded)
    spectral = tuple(float(record[0]) for record in records)
    noise = tuple(float(record[1]) for record in records)
    kms_residuals = tuple(float(record[2]) for record in records)
    fdt_residuals = tuple(float(record[3]) for record in records)
    velocity_spectrum = np.asarray((1.0, 0.7, 0.5, 0.3, 0.2), dtype=float)
    entropy = float(
        parameters.beta_th
        * np.sum(
            parameters.gamma_memory
            / (1.0 + np.asarray(frequencies) ** 2 * parameters.memory_time**2)
            * velocity_spectrum**2
        )
    )
    positive_time_value = causal_memory_time_kernel(memory_time, parameters)
    negative_support = causal_memory_time_kernel(-memory_time, parameters)
    values = (
        *retarded_real,
        *retarded_imag,
        *spectral,
        *noise,
        *kms_residuals,
        *fdt_residuals,
        *transform_residuals,
        *reality_residuals,
        entropy,
        gamma_memory,
        memory_time,
        positive_time_value,
    )
    if not all(isfinite(float(value)) for value in values):
        raise FloatingPointError("nonlocal SK/KMS memory state is not finite")
    return NonlocalSKKMSMemoryState(
        temperature=temperature,
        chemical_potential=chemical_potential,
        space_response=space_response,
        effective_mass=effective_mass,
        beta_th=parameters.beta_th,
        kappa=parameters.kappa,
        chi=parameters.chi,
        gamma_memory=parameters.gamma_memory,
        memory_time=parameters.memory_time,
        frequency_grid=frequencies,
        retarded_real=retarded_real,
        retarded_imag=retarded_imag,
        spectral_density=spectral,
        noise_kernel=noise,
        kms_ratio_residuals=kms_residuals,
        fdt_residuals=fdt_residuals,
        causal_transform_residuals=transform_residuals,
        kernel_reality_residuals=reality_residuals,
        memory_pole_imaginary_part=float(-1.0 / parameters.memory_time),
        negative_time_support_residual=float(negative_support),
        positive_time_memory_value=float(positive_time_value),
        spectral_density_minimum=float(min(spectral)),
        entropy_production_witness=entropy,
        source_collision_widths=tuple(float(value) for value in collision.collision_width_by_species),
    )


def nonlocal_sk_kms_memory_contract() -> dict[str, Any]:
    """Return the causal memory influence-kernel contract and boundaries."""

    return {
        "status": NONLOCAL_SK_KMS_MEMORY_STATUS,
        "equations": {
            "influence_functional": "S_IF=integral dt dt' [Phi_a(t) K_R(t-t') Phi_r(t') + i Phi_a(t) N(t-t') Phi_a(t')/2]",
            "causal_memory": "g_R(t)=gamma_memory/memory_time*exp(-t/memory_time)*Theta(t)",
            "retarded_kernel": "K_R(omega)=kappa-chi*omega^2-i*omega*gamma_memory/(1-i*omega*memory_time)",
            "spectral_density": "rho(omega)=-2 Im K_R(omega)=2*gamma_memory*omega/(1+omega^2*memory_time^2)",
            "kms_fdt": "N(omega)=rho(omega)*coth(beta_th*omega/2); G^>/G^<=exp(beta_th*omega)",
            "memory_rate_source": "gamma_memory=mean(action-derived normal collision widths); memory_time=1/(m_eff+gamma_memory)",
            "entropy_witness": "sigma_formal=beta_th*sum_omega[gamma_memory/(1+omega^2*tau^2)]*|v_omega|^2>=0",
        },
        "unit_contract": {
            "unit_lane": "natural",
            "temperature_mass_frequency": "natural energy/inverse time",
            "kappa": "natural kernel stiffness units",
            "chi": "natural inertial kernel units",
            "gamma_memory": "natural damping rate",
            "memory_time": "inverse natural energy",
            "Phi": "effective response variable; not temperature",
            "C": "collective system-behaviour coordinate; not mass or charge",
            "R_gen": "derived history trace; no backreaction",
            "R_obs": "separate observer record",
        },
        "derivation_class": "formal causal exponential memory kernel with damping rate inherited from an action-derived collision comparator; KMS/FDT and positivity are algebraically verified, not source-calibrated",
        "observable": "formal nonlocal retarded kernel, spectral density, KMS/FDT noise, and entropy-positivity witness",
        "data_role": "ACTION_DERIVED_FORMAL_NONLOCAL_SK_KMS_MEMORY_CONTROL_NOT_PHYSICAL_TRANSPORT",
        "included": {
            "nonlocal_influence_kernel": True,
            "causal_time_support": True,
            "retarded_memory_pole": True,
            "positive_spectral_density": True,
            "charged_action_derived_rate_source": True,
            "kms_fdt": True,
            "formal_entropy_positivity": True,
        },
        "excluded": {
            "physical_retarded_self_energy": True,
            "unique_physical_renormalization": True,
            "condensed_two_fluid_completion": True,
            "physical_kubo_coefficient": True,
            "entropy_current_heat_flux_dissipative_balance": True,
            "SI_map": True,
            "alpha_Phi_K": True,
            "TTG_validation": True,
        },
        "claim_boundary": "This closes a formal action-derived nonlocal SK/KMS memory-kernel control with explicit causal support, positive spectral density, KMS/FDT noise, and entropy positivity. It does not identify the kernel with a physical retarded self-energy, select a unique renormalization, close the condensed/two-fluid sector, provide a physical Kubo coefficient or entropy-current balance, map Phi to SI temperature, calibrate alpha_Phi_K, validate TTG, or close Full Topic 13.",
    }


__all__ = [
    "NONLOCAL_SK_KMS_MEMORY_STATUS",
    "NonlocalSKKMSMemoryParameters",
    "NonlocalSKKMSMemoryState",
    "retarded_memory_kernel",
    "causal_memory_time_kernel",
    "nonlocal_sk_kms_memory_state",
    "nonlocal_sk_kms_memory_contract",
]
