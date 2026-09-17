"""Synthetic thermal observable bridge for the relational C path.

This module does not declare that C is temperature or heat flux.  It tests the
missing correspondence explicitly by applying a declared gain

    T_norm = T0 + alpha_T * C

and then evaluating standard Fourier/Cattaneo controls.  ``alpha_T`` is an open
mapping coefficient, not a fitted UET constant.  The bridge is therefore an
identifiability and thermodynamic-sign diagnostic until a dimensional observable
map is supplied.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, pi, sin
from typing import List, Tuple


THERMAL_BRIDGE_STATUS = "SIMULATION_ONLY"
THERMAL_MAPPING_STATUS = "BLOCKED_OPEN_C_TO_T_GAIN"


@dataclass(frozen=True)
class ThermalObservableBridgeConfig:
    """Normalized 1D periodic thermal-map configuration."""

    spatial_points: int = 64
    spatial_length: float = 2.0 * pi
    mode_number: int = 1
    duration: float = 8.0
    time_steps: int = 8000
    C_amplitude: float = 0.1
    temperature_background: float = 1.0
    C_to_temperature_gain: float = 0.2
    conductivity: float = 1.0
    tau_q: float = 0.2
    drive_omega: float = 0.75
    path_cost_coefficient: float = 0.1
    unit_lane: str = "normalized"

    def __post_init__(self) -> None:
        if self.spatial_points < 8:
            raise ValueError("spatial_points must be at least 8")
        if self.mode_number < 1:
            raise ValueError("mode_number must be positive")
        if self.time_steps < 10:
            raise ValueError("time_steps must be at least 10")
        values = {
            "spatial_length": self.spatial_length,
            "duration": self.duration,
            "C_amplitude": self.C_amplitude,
            "temperature_background": self.temperature_background,
            "C_to_temperature_gain": self.C_to_temperature_gain,
            "conductivity": self.conductivity,
            "tau_q": self.tau_q,
            "drive_omega": self.drive_omega,
            "path_cost_coefficient": self.path_cost_coefficient,
        }
        if not all(isfinite(float(value)) for value in values.values()):
            raise ValueError("thermal bridge parameters must be finite")
        for name in (
            "spatial_length",
            "duration",
            "conductivity",
            "tau_q",
            "drive_omega",
            "path_cost_coefficient",
        ):
            if float(getattr(self, name)) <= 0.0:
                raise ValueError(f"{name} must be positive")
        if self.temperature_background <= abs(
            self.C_to_temperature_gain * self.C_amplitude
        ):
            raise ValueError("temperature must remain positive in the declared map")
        if self.unit_lane != "normalized":
            raise NotImplementedError(
                "thermal observable bridge supports only unit_lane='normalized'"
            )

    @property
    def dt(self) -> float:
        return self.duration / self.time_steps

    @property
    def dx(self) -> float:
        return self.spatial_length / self.spatial_points

    @property
    def spatial_wave_number(self) -> float:
        return 2.0 * pi * self.mode_number / self.spatial_length


@dataclass(frozen=True)
class ThermalObservableBridgeResult:
    """Aggregated outputs from one declared normalized map."""

    mapping_gain: float
    C_path_work: float
    fourier_entropy_proxy: float
    cattaneo_entropy_proxy: float
    cattaneo_reference_residual: float
    minimum_temperature: float
    minimum_fourier_entropy_source: float
    minimum_cattaneo_entropy_source: float
    status: str = THERMAL_BRIDGE_STATUS
    mapping_status: str = THERMAL_MAPPING_STATUS


def _trapezoid(values: List[float], step: float) -> float:
    return step * (
        0.5 * values[0] + sum(values[1:-1]) + 0.5 * values[-1]
    )


def _cattaneo_reference(
    forcing_amplitude: float, omega: float, tau_q: float, time: float
) -> float:
    lag = omega * tau_q
    return forcing_amplitude * (
        sin(omega * time) - lag * cos(omega * time)
    ) / (1.0 + lag * lag)


def run_thermal_observable_bridge(
    config: ThermalObservableBridgeConfig | None = None,
) -> ThermalObservableBridgeResult:
    """Evaluate the candidate C-to-temperature bridge and standard controls.

    The map is intentionally explicit and reversible at the bookkeeping level,
    but ``C_to_temperature_gain`` is not inferred.  Changing that gain while
    holding C fixed is the diagnostic that blocks a direct universal C-to-T claim.
    """

    config = config or ThermalObservableBridgeConfig()
    n = config.spatial_points
    dx = config.dx
    dt = config.dt
    kx = config.spatial_wave_number
    x_values = [index * dx for index in range(n)]
    sin_x = [sin(kx * x) for x in x_values]
    cos_x = [cos(kx * x) for x in x_values]

    cattaneo_q = [0.0] * n
    forcing_amplitudes = [
        -config.conductivity
        * config.C_to_temperature_gain
        * config.C_amplitude
        * kx
        * value
        for value in cos_x
    ]
    for index, amplitude in enumerate(forcing_amplitudes):
        cattaneo_q[index] = _cattaneo_reference(
            amplitude, config.drive_omega, config.tau_q, 0.0
        )

    path_power: List[float] = []
    fourier_entropy: List[float] = []
    cattaneo_entropy: List[float] = []
    minimum_temperature = float("inf")
    minimum_fourier_source = float("inf")
    minimum_cattaneo_source = float("inf")
    maximum_reference_residual = 0.0

    for step_index in range(config.time_steps + 1):
        time = step_index * dt
        sin_t = sin(config.drive_omega * time)
        cos_t = cos(config.drive_omega * time)
        C = [config.C_amplitude * value * sin_t for value in sin_x]
        dC_dt = [config.C_amplitude * value * config.drive_omega * cos_t for value in sin_x]
        temperature = [
            config.temperature_background + config.C_to_temperature_gain * value
            for value in C
        ]
        gradient_temperature = [
            config.C_to_temperature_gain
            * config.C_amplitude
            * kx
            * value
            * sin_t
            for value in cos_x
        ]
        fourier_q = [
            -config.conductivity * value for value in gradient_temperature
        ]
        fourier_source = [
            q * q / (config.conductivity * temp * temp)
            for q, temp in zip(fourier_q, temperature)
        ]
        cattaneo_source = [
            q * q / (config.conductivity * temp * temp)
            for q, temp in zip(cattaneo_q, temperature)
        ]
        path_power.append(
            config.path_cost_coefficient
            * dx
            * sum(value * value for value in dC_dt)
        )
        fourier_entropy.append(dx * sum(fourier_source))
        cattaneo_entropy.append(dx * sum(cattaneo_source))
        minimum_temperature = min(minimum_temperature, min(temperature))
        minimum_fourier_source = min(minimum_fourier_source, min(fourier_source))
        minimum_cattaneo_source = min(minimum_cattaneo_source, min(cattaneo_source))

        if step_index == config.time_steps:
            break
        forcing_now = [
            amplitude * sin_t for amplitude in forcing_amplitudes
        ]
        forcing_next = [
            amplitude * sin(config.drive_omega * (time + dt))
            for amplitude in forcing_amplitudes
        ]
        k1 = [
            (-q + source) / config.tau_q
            for q, source in zip(cattaneo_q, forcing_now)
        ]
        predictor = [q + dt * rate for q, rate in zip(cattaneo_q, k1)]
        k2 = [
            (-q + source) / config.tau_q
            for q, source in zip(predictor, forcing_next)
        ]
        cattaneo_q = [
            q + 0.5 * dt * (rate_1 + rate_2)
            for q, rate_1, rate_2 in zip(cattaneo_q, k1, k2)
        ]
        reference_next = [
            _cattaneo_reference(
                amplitude, config.drive_omega, config.tau_q, time + dt
            )
            for amplitude in forcing_amplitudes
        ]
        maximum_reference_residual = max(
            maximum_reference_residual,
            max(
                abs(value - reference)
                for value, reference in zip(cattaneo_q, reference_next)
            ),
        )

    total_path_work = _trapezoid(path_power, dt)
    total_fourier_entropy = _trapezoid(fourier_entropy, dt)
    total_cattaneo_entropy = _trapezoid(cattaneo_entropy, dt)
    return ThermalObservableBridgeResult(
        mapping_gain=config.C_to_temperature_gain,
        C_path_work=total_path_work,
        fourier_entropy_proxy=total_fourier_entropy,
        cattaneo_entropy_proxy=total_cattaneo_entropy,
        cattaneo_reference_residual=maximum_reference_residual,
        minimum_temperature=minimum_temperature,
        minimum_fourier_entropy_source=minimum_fourier_source,
        minimum_cattaneo_entropy_source=minimum_cattaneo_source,
    )


__all__ = [
    "THERMAL_BRIDGE_STATUS",
    "THERMAL_MAPPING_STATUS",
    "ThermalObservableBridgeConfig",
    "ThermalObservableBridgeResult",
    "run_thermal_observable_bridge",
]
