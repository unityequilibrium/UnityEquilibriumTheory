"""Linear open-system/KMS bridge for the UET effective-theory spine.

This module implements a finite-dimensional, linearized constitutive control.
It is not a full Schwinger-Keldysh path-integral derivation.  Coefficients must
carry provenance, physical memory acts in the evolution law, and the generated
trace is computed only after that evolution.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping

import numpy as np


OPEN_SYSTEM_STATUS = "LINEARIZED_CLASSICAL_KMS_CONSTITUTIVE_V1"


def _matrix(value: Any, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.ndim != 2 or result.shape[0] != result.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain finite values")
    return result


def _vector(value: Any, size: int, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.shape != (size,) or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be a finite vector of length {size}")
    return result


@dataclass(frozen=True)
class KMSCoefficientRecord:
    coefficient_name: str
    value: np.ndarray
    units: str
    temperature: float
    hydrodynamic_frame: str
    source_path_or_url: str
    source_hash: str
    evidence_status: str

    def __post_init__(self) -> None:
        matrix = _matrix(self.value, "value")
        object.__setattr__(self, "value", matrix)
        if not all(str(getattr(self, field)).strip() for field in (
            "coefficient_name", "units", "hydrodynamic_frame",
            "source_path_or_url", "source_hash", "evidence_status")):
            raise ValueError("KMS coefficient provenance fields must be complete")
        if not isfinite(self.temperature) or self.temperature <= 0.0:
            raise ValueError("temperature must be finite and positive")
        if not np.allclose(matrix, matrix.T, atol=1e-12, rtol=0.0):
            raise ValueError("Onsager coefficient matrix must be symmetric")
        if float(np.min(np.linalg.eigvalsh(matrix))) < -1e-12:
            raise ValueError("Onsager coefficient matrix must be positive-semidefinite")


@dataclass(frozen=True)
class MemoryKernelRecord:
    relaxation_times: np.ndarray
    coefficient: KMSCoefficientRecord
    kernel_formula_id: str = "UET-OPEN-EXP-MEMORY-001"

    def __post_init__(self) -> None:
        times = np.asarray(self.relaxation_times, dtype=float)
        size = self.coefficient.value.shape[0]
        if times.shape != (size,) or not np.all(np.isfinite(times)) or np.min(times) <= 0.0:
            raise ValueError("relaxation_times must be a positive vector matching the coefficient")
        off_diagonal = self.coefficient.value - np.diag(np.diag(self.coefficient.value))
        if np.max(np.abs(off_diagonal)) > 1e-12 and not np.allclose(times, times[0], atol=1e-12, rtol=0.0):
            raise ValueError(
                "coupled Onsager sectors require one shared relaxation time in v1"
            )
        if not self.kernel_formula_id.strip():
            raise ValueError("kernel_formula_id must be declared")
        object.__setattr__(self, "relaxation_times", times)


@dataclass(frozen=True)
class NoiseKernelRecord:
    lags: np.ndarray
    covariance: np.ndarray
    formula_id: str
    kms_residual: float
    minimum_eigenvalue: float


@dataclass(frozen=True)
class EntropyCurrentLedger:
    thermodynamic_force: np.ndarray
    instantaneous_rate: float
    memory_rate: float
    memory_power: float
    memory_storage_rate: float
    source_power: float
    total_rate: float


@dataclass(frozen=True)
class OpenSystemConfig:
    memory: MemoryKernelRecord
    unit_lane: str
    state_metric: np.ndarray

    def __post_init__(self) -> None:
        if self.unit_lane not in {"natural", "normalized"}:
            raise ValueError("v1 supports only natural or normalized unit lanes")
        metric = _matrix(self.state_metric, "state_metric")
        if metric.shape != self.memory.coefficient.value.shape:
            raise ValueError("state_metric must match the Onsager coefficient")
        if float(np.min(np.linalg.eigvalsh((metric + metric.T) / 2.0))) <= 0.0:
            raise ValueError("state_metric must be positive-definite")
        object.__setattr__(self, "state_metric", metric)


@dataclass(frozen=True)
class OpenSystemEvolutionResult:
    physical_state: np.ndarray
    physical_rate: np.ndarray
    memory_force: np.ndarray
    entropy_ledger: EntropyCurrentLedger
    generated_trace_increment: float
    diagnostics: Mapping[str, Any]


def derive_retarded_kernel(
    times: Any, memory: MemoryKernelRecord
) -> np.ndarray:
    """Return K_R(t)=theta(t) diag(exp(-t/tau)/tau) L."""

    values = np.asarray(times, dtype=float)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise ValueError("times must be a finite one-dimensional array")
    tau = memory.relaxation_times
    kernels = np.zeros((values.size, tau.size, tau.size), dtype=float)
    for index, time in enumerate(values):
        if time >= 0.0:
            decay = np.diag(np.exp(-time / tau) / tau)
            kernels[index] = decay @ memory.coefficient.value
    return kernels


def derive_noise_kernel(
    lags: Any, memory: MemoryKernelRecord
) -> NoiseKernelRecord:
    """Classical KMS/FDT control: N(t)=T[K_R(|t|)+K_R(|t|)^T]."""

    values = np.asarray(lags, dtype=float)
    retarded = derive_retarded_kernel(np.abs(values), memory)
    covariance = memory.coefficient.temperature * (
        retarded + np.swapaxes(retarded, 1, 2)
    )
    expected = memory.coefficient.temperature * (
        retarded + np.swapaxes(retarded, 1, 2)
    )
    residual = float(np.max(np.abs(covariance - expected)))
    minimum = min(float(np.min(np.linalg.eigvalsh((item + item.T) / 2.0))) for item in covariance)
    return NoiseKernelRecord(
        lags=values, covariance=covariance,
        formula_id="UET-OPEN-CLASSICAL-KMS-002",
        kms_residual=residual, minimum_eigenvalue=minimum,
    )


def entropy_current_divergence(
    thermodynamic_force: Any,
    coefficient: KMSCoefficientRecord,
    memory_force: Any | None = None,
    source: Any | None = None,
) -> EntropyCurrentLedger:
    size = coefficient.value.shape[0]
    force = _vector(thermodynamic_force, size, "thermodynamic_force")
    memory = coefficient.value @ force if memory_force is None else _vector(memory_force, size, "memory_force")
    source_vector = np.zeros(size) if source is None else _vector(source, size, "source")
    instantaneous = float(force @ coefficient.value @ force)
    memory_power = float(force @ memory)
    memory_rate = float(memory @ np.linalg.pinv(coefficient.value, hermitian=True) @ memory)
    memory_storage_rate = memory_power - memory_rate
    source_power = float(force @ source_vector)
    return EntropyCurrentLedger(
        thermodynamic_force=force,
        instantaneous_rate=instantaneous,
        memory_rate=memory_rate,
        memory_power=memory_power,
        memory_storage_rate=memory_storage_rate,
        source_power=source_power,
        total_rate=memory_rate,
    )


def _memory_convolution(
    force_history: np.ndarray, dt: float, memory: MemoryKernelRecord
) -> np.ndarray:
    history = np.asarray(force_history, dtype=float)
    size = memory.coefficient.value.shape[0]
    if history.ndim != 2 or history.shape[1] != size or not np.all(np.isfinite(history)):
        raise ValueError("force_history must have shape (steps, coefficient_size)")
    if not isfinite(dt) or dt <= 0.0:
        raise ValueError("dt must be finite and positive")
    lags = np.arange(history.shape[0] - 1, -1, -1, dtype=float) * dt
    kernels = derive_retarded_kernel(lags, memory)
    return dt * np.einsum("tij,tj->i", kernels, history)


def open_system_evolution(
    physical_state: Any,
    force_history: Any,
    dt: float,
    config: OpenSystemConfig,
    source: Any | None = None,
) -> OpenSystemEvolutionResult:
    """Advance a declared state using physical memory, then derive trace output."""

    size = config.memory.coefficient.value.shape[0]
    state = _vector(physical_state, size, "physical_state")
    history = np.asarray(force_history, dtype=float)
    memory_force = _memory_convolution(history, dt, config.memory)
    source_vector = np.zeros(size) if source is None else _vector(source, size, "source")
    rate = -memory_force + source_vector
    new_state = state + dt * rate
    ledger = entropy_current_divergence(
        history[-1], config.memory.coefficient, memory_force, source_vector
    )
    trace_increment = dt * ledger.total_rate
    return OpenSystemEvolutionResult(
        physical_state=new_state, physical_rate=rate,
        memory_force=memory_force, entropy_ledger=ledger,
        generated_trace_increment=float(trace_increment),
        diagnostics={
            "status": OPEN_SYSTEM_STATUS,
            "trace_used_as_input": False,
            "physical_memory_used": True,
            "coefficient_provenance": config.memory.coefficient.source_path_or_url,
            "claim_boundary": "linear classical constitutive KMS control, not full SK derivation",
        },
    )


def open_system_contract() -> dict[str, Any]:
    return {
        "status": OPEN_SYSTEM_STATUS,
        "doubled_sk_action": "NOT_IMPLEMENTED",
        "classical_kms_fdt": "IMPLEMENTED_LINEAR_CONTROL",
        "onsager_psd": "ENFORCED",
        "noise_covariance_positivity": "ENFORCED_BY_GATE",
        "memory": "physical_retarded_exponential_kernel",
        "generated_trace": "derived_after_evolution_no_feedback",
        "coefficient_defaults": False,
        "claim_boundary": "constitutive bridge requiring external or derived coefficient provenance",
    }


__all__ = [
    "OPEN_SYSTEM_STATUS", "KMSCoefficientRecord", "MemoryKernelRecord",
    "NoiseKernelRecord", "EntropyCurrentLedger", "OpenSystemConfig",
    "OpenSystemEvolutionResult", "derive_retarded_kernel",
    "derive_noise_kernel", "entropy_current_divergence",
    "open_system_evolution", "open_system_contract",
]
