"""Linearized GH metric-mode to ideal equal-arm interferometer response.

This is a standard-GR observable mapping for a single plane-wave Fourier mode.
It is not a detector calibration model and does not add dynamics to the GH lane.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi, sin
from typing import Any, Final

import numpy as np


SPEED_OF_LIGHT_M_S: Final[float] = 299_792_458.0
RESPONSE_STATUS: Final[str] = "GH_LINEAR_GW_DETECTOR_RESPONSE_READY"


@dataclass(frozen=True)
class InterferometerResponse:
    tt_metric_mode: np.ndarray
    arm_u_transfer: complex
    arm_v_transfer: complex
    detector_tensor: np.ndarray
    strain_response: complex
    equivalent_differential_length_m: complex
    transfer_frequency_hz: float


def _finite_array(value: Any, shape: tuple[int, ...], name: str) -> np.ndarray:
    array = np.asarray(value, dtype=np.complex128)
    if array.shape != shape or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite with shape {shape}")
    return array


def _unit_real_vector(value: Any, name: str) -> np.ndarray:
    raw = np.asarray(value)
    if np.iscomplexobj(raw) and np.any(np.imag(raw) != 0.0):
        raise ValueError(f"{name} must be real")
    vector = np.asarray(np.real(raw), dtype=float)
    if vector.shape != (3,) or not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must be a finite 3-vector")
    norm = float(np.linalg.norm(vector))
    if not isfinite(norm) or abs(norm - 1.0) > 1e-12:
        raise ValueError(f"{name} must already be unit normalized")
    return vector


def spatial_metric_perturbation_from_gh_metric(
    spacetime_metric: Any,
) -> np.ndarray:
    """Extract gamma_ij-delta_ij from one asymptotically Minkowski GH metric."""

    metric = _finite_array(spacetime_metric, (4, 4), "spacetime_metric")
    if np.max(np.abs(metric - metric.T)) > 1e-12:
        raise ValueError("spacetime_metric must be symmetric")
    return metric[1:, 1:] - np.eye(3, dtype=np.complex128)


def project_spatial_metric_mode_to_tt(
    spatial_metric_mode: Any,
    propagation_direction: Any,
) -> np.ndarray:
    """Project a plane-wave spatial metric Fourier mode to its TT sector.

    The projection is intended for a linearized, asymptotically flat wave-zone
    mode. It is not a general curved-space or nonlinear radiation-extraction
    prescription.
    """

    mode = _finite_array(spatial_metric_mode, (3, 3), "spatial_metric_mode")
    if np.max(np.abs(mode - mode.T)) > 1e-12:
        raise ValueError("spatial_metric_mode must be symmetric")
    direction = _unit_real_vector(propagation_direction, "propagation_direction")
    transverse_projector = np.eye(3) - np.outer(direction, direction)
    transverse = transverse_projector @ mode @ transverse_projector
    tt_mode = transverse - 0.5 * transverse_projector * np.trace(transverse)
    return 0.5 * (tt_mode + tt_mode.T)


def _sinc_unscaled(value: float) -> float:
    return 1.0 if value == 0.0 else sin(value) / value


def equal_arm_round_trip_transfer(
    frequency_hz: float,
    arm_length_m: float,
    arm_direction: Any,
    propagation_direction: Any,
) -> complex:
    """Return the exact single-round-trip arm transfer for the declared model.

    Formula: Liang et al. (2019), Eq. (6), with f*=c/(2*pi*L). The detector
    model assumes an equal-arm Michelson without optical cavities.
    """

    frequency = float(frequency_hz)
    length = float(arm_length_m)
    if not isfinite(frequency):
        raise ValueError("frequency_hz must be finite")
    if not isfinite(length) or length <= 0.0:
        raise ValueError("arm_length_m must be finite and positive")
    arm = _unit_real_vector(arm_direction, "arm_direction")
    propagation = _unit_real_vector(propagation_direction, "propagation_direction")
    mu = float(np.dot(arm, propagation))
    q = pi * frequency * length / SPEED_OF_LIGHT_M_S
    first = _sinc_unscaled(q * (1.0 - mu)) * np.exp(-1j * q * (3.0 + mu))
    second = _sinc_unscaled(q * (1.0 + mu)) * np.exp(-1j * q * (1.0 + mu))
    return complex(0.5 * (first + second))


def equal_arm_interferometer_response(
    tt_metric_mode: Any,
    propagation_direction: Any,
    arm_u: Any,
    arm_v: Any,
    frequency_hz: float,
    arm_length_m: float,
) -> InterferometerResponse:
    """Map one TT metric mode to ideal equal-arm detector strain response."""

    mode = _finite_array(tt_metric_mode, (3, 3), "tt_metric_mode")
    if np.max(np.abs(mode - mode.T)) > 1e-12:
        raise ValueError("tt_metric_mode must be symmetric")
    propagation = _unit_real_vector(propagation_direction, "propagation_direction")
    u = _unit_real_vector(arm_u, "arm_u")
    v = _unit_real_vector(arm_v, "arm_v")
    length = float(arm_length_m)
    frequency = float(frequency_hz)
    if not isfinite(length) or length <= 0.0:
        raise ValueError("arm_length_m must be finite and positive")
    if not isfinite(frequency):
        raise ValueError("frequency_hz must be finite")

    transfer_u = equal_arm_round_trip_transfer(frequency, length, u, propagation)
    transfer_v = equal_arm_round_trip_transfer(frequency, length, v, propagation)
    detector = 0.5 * (
        np.outer(u, u) * transfer_u - np.outer(v, v) * transfer_v
    )
    strain = complex(np.einsum("ij,ij->", detector, mode))
    return InterferometerResponse(
        tt_metric_mode=mode.copy(),
        arm_u_transfer=transfer_u,
        arm_v_transfer=transfer_v,
        detector_tensor=detector,
        strain_response=strain,
        equivalent_differential_length_m=complex(length * strain),
        transfer_frequency_hz=SPEED_OF_LIGHT_M_S / (2.0 * pi * length),
    )


def gw_detector_response_contract() -> dict[str, Any]:
    return {
        "equations": {
            "gh_metric_to_spatial_mode": "h_ij = gamma_ij - delta_ij",
            "tt_projection": "h_TT = P h P - 1/2 P tr(P h P), P_ij=delta_ij-n_i n_j",
            "transfer_frequency": "f_star = c/(2*pi*L)",
            "arm_transfer": (
                "T(f,mu)=1/2*[sinc(q*(1-mu))*exp(-i*q*(3+mu)) "
                "+ sinc(q*(1+mu))*exp(-i*q*(1+mu))], q=pi*f*L/c"
            ),
            "detector_tensor": "D_ij(f)=1/2*(u_i*u_j*T_u-v_i*v_j*T_v)",
            "measured_strain_mode": "h_D(f)=D_ij(f)*h_TT_ij(f)",
            "low_frequency_limit": "T_u,T_v -> 1 as f*L/c -> 0",
            "equivalent_length": "DeltaL_equiv(f)=L*h_D(f)",
        },
        "units": {
            "spacetime_metric_and_h_TT": "dimensionless",
            "frequency_hz": "s^-1",
            "arm_length_m": "m",
            "speed_of_light": "m s^-1 (exact SI defining constant)",
            "transfer_frequency_hz": "s^-1",
            "arm_vectors_and_propagation_direction": "dimensionless unit vectors",
            "detector_tensor_and_strain_response": "dimensionless",
            "equivalent_differential_length_m": "m; literal arm displacement only in the low-frequency limit",
        },
        "assumptions": [
            "linearized plane-wave mode in an asymptotically Minkowski wave zone",
            "spatial TT projection relative to the declared propagation direction",
            "equal physical arm lengths and fixed arm directions",
            "ideal Michelson single-round-trip response without optical cavities",
            "frequency-domain mode supplied by caller; no time-series FFT is included",
        ],
        "excluded": [
            "nonlinear or strong-field radiation extraction",
            "finite-control-loop and optical-cavity response",
            "noise, calibration uncertainty, or detector data",
            "self-consistent UET metric generation or Einstein-equation derivation",
            "UET Phi, C, R_gen, and R_obs as inputs or state variables",
        ],
        "constant_origin": {
            "speed_of_light_m_s": "299792458 exactly by the SI definition of the metre",
        },
        "claim_boundary": (
            "standard-GR detector measurement operator for a single TT plane-wave mode; "
            "not external validation or a detector calibration pipeline, and not a UET prediction"
        ),
    }


__all__ = [
    "InterferometerResponse",
    "RESPONSE_STATUS",
    "SPEED_OF_LIGHT_M_S",
    "equal_arm_interferometer_response",
    "equal_arm_round_trip_transfer",
    "gw_detector_response_contract",
    "project_spatial_metric_mode_to_tt",
    "spatial_metric_perturbation_from_gh_metric",
]
