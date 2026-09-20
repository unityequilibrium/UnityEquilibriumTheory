"""Tests for the linearized open-system/KMS constitutive bridge."""

from __future__ import annotations

import numpy as np
import pytest

from docs.core.uet_covariant_open_system import (
    KMSCoefficientRecord, MemoryKernelRecord, OpenSystemConfig,
    derive_noise_kernel, derive_retarded_kernel, entropy_current_divergence,
    open_system_contract, open_system_evolution,
)


def _coefficient(matrix: np.ndarray | None = None) -> KMSCoefficientRecord:
    return KMSCoefficientRecord(
        coefficient_name="locked_longitudinal_onsager_control",
        value=np.diag([0.5, 0.25]) if matrix is None else matrix,
        units="natural_control_units", temperature=2.0,
        hydrodynamic_frame="Landau",
        source_path_or_url="internal://preregistered-wave4-control",
        source_hash="sha256:wave4-control-not-external",
        evidence_status="SIMULATION_ONLY",
    )


def _config() -> OpenSystemConfig:
    return OpenSystemConfig(
        memory=MemoryKernelRecord(np.array([0.2, 0.4]), _coefficient()),
        unit_lane="natural", state_metric=np.eye(2),
    )


def test_onsager_symmetry_psd_and_provenance_are_required() -> None:
    with pytest.raises(ValueError, match="symmetric"):
        _coefficient(np.array([[1.0, 0.4], [0.0, 1.0]]))
    with pytest.raises(ValueError, match="positive-semidefinite"):
        _coefficient(np.diag([1.0, -0.1]))
    with pytest.raises(ValueError, match="provenance"):
        KMSCoefficientRecord("L", np.eye(2), "u", 1.0, "Landau", "", "", "OPEN")


def test_retarded_kernel_has_no_negative_time_support() -> None:
    kernel = derive_retarded_kernel(np.array([-1.0, -1e-6, 0.0, 0.2]), _config().memory)
    assert np.max(np.abs(kernel[:2])) == 0.0
    assert np.min(np.diag(kernel[2])) > 0.0


def test_classical_kms_noise_is_symmetric_psd() -> None:
    record = derive_noise_kernel(np.linspace(-1.0, 1.0, 21), _config().memory)
    assert record.kms_residual <= 1e-12
    assert record.minimum_eigenvalue >= -1e-12
    assert np.max(np.abs(record.covariance - np.swapaxes(record.covariance, 1, 2))) <= 1e-12


def test_entropy_rate_is_nonnegative_for_instantaneous_psd_control() -> None:
    ledger = entropy_current_divergence(np.array([0.8, -0.3]), _coefficient())
    assert ledger.instantaneous_rate >= 0.0
    assert ledger.total_rate >= 0.0


def test_memory_changes_physical_state_but_trace_is_output_only() -> None:
    config = _config()
    history = np.repeat(np.array([[0.5, -0.2]]), 20, axis=0)
    a = open_system_evolution(np.array([1.0, 2.0]), history, 0.02, config)
    b = open_system_evolution(np.array([1.0, 2.0]), history, 0.02, config)
    assert np.array_equal(a.physical_state, b.physical_state)
    assert np.linalg.norm(a.physical_rate) > 0.0
    assert a.generated_trace_increment >= 0.0
    assert a.diagnostics["trace_used_as_input"] is False


def test_exponential_kernel_integrates_to_onsager_matrix() -> None:
    config = _config()
    times = np.linspace(0.0, 8.0, 20001)
    kernel = derive_retarded_kernel(times, config.memory)
    integral = np.trapezoid(kernel, times, axis=0)
    assert np.max(np.abs(integral - config.memory.coefficient.value)) <= 2e-6


def test_contract_does_not_overclaim_full_sk_derivation() -> None:
    contract = open_system_contract()
    assert contract["doubled_sk_action"] == "NOT_IMPLEMENTED"
    assert contract["coefficient_defaults"] is False
    assert "no_feedback" in contract["generated_trace"]
