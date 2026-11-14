"""Independent harmonic modes with declared source derivatives, not Phi calibration."""

import numpy as np
from scipy.constants import Boltzmann as KB


def equilibrium(gaps, temperature):
    e = np.asarray(gaps, dtype=float)
    if e.ndim != 1 or not e.size or not np.isfinite(e).all() or np.any(e <= 0):
        raise ValueError('positive finite one-dimensional energy gaps required')
    if not np.isfinite(temperature) or temperature <= 0:
        raise ValueError('positive finite temperature required')
    y = e/(KB*temperature)
    if not np.isfinite(y).all():
        raise ValueError('energy/temperature ratio overflow')
    denominator = -np.expm1(-y)
    n = np.exp(-y)/denominator
    capacity = KB*y*y*n*(n+1)
    return dict(occupation=n, capacity=capacity, energy=e*(n+.5),
                entropy=KB*(y*n-np.log(denominator)))


def protocol_response(gaps, temperature, gap_derivative, weights):
    e = np.asarray(gaps, dtype=float)
    state = equilibrium(e, temperature)
    de, weights = np.asarray(gap_derivative, dtype=float), np.asarray(weights, dtype=float)
    if de.shape != e.shape or weights.shape != e.shape:
        raise ValueError('one derivative and weight per mode required')
    if not np.isfinite(de).all() or not np.isfinite(weights).all() or np.any(weights <= 0):
        raise ValueError('finite derivatives and positive weights required')
    capacity = np.dot(weights, state['capacity'])
    if capacity <= 0 or not np.isfinite(capacity):
        raise ValueError('resolved positive total heat capacity required for temperature gain')
    work = np.dot(weights, (state['occupation']+.5)*de)
    heat = -temperature*np.dot(weights, state['capacity']*de/e)
    return dict(capacity=float(capacity), isothermal_work_derivative=float(work),
                isothermal_heat_derivative=float(heat),
                isothermal_energy_derivative=float(work+heat),
                isothermal_entropy_derivative=float(heat/temperature),
                equilibrium_isentropic_temperature_derivative=float(-heat/capacity),
                frozen_occupation_energy_derivative=float(work),
                frozen_occupation_heat_derivative=0.)
