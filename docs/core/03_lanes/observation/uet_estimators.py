"""Observation layer, wave O3: Markov versus history-dependent estimates of the present.

An observer holds noisy records y_k = X(t_e - k delta) + eta_k (eta ~ N(0, sigma^2), independent) of a
source and wants X(t_o) = X(t_e + a), where a is the age of the newest record.

    Markov estimator   X_M = y_0                              (treat the record as the present)
    history estimator  X_H = y_0 + (y_0 - y_1)/delta * a      (extrapolate with two records)

Exact moments (no small-parameter expansion):
    bias_M = X(t_e + a) - X(t_e)
    bias_H = X(t_e + a) - [X(t_e) + (X(t_e) - X(t_e - delta))/delta * a]
    Var_M  = sigma^2,    Var_H = sigma^2 [ (1 + a/delta)^2 + (a/delta)^2 ]
    MSE    = bias^2 + Var
Memory removes the bias at one order higher but amplifies the measurement noise, so there is a noise level
sigma* above which the Markov observer is better.
"""

from __future__ import annotations

from math import sqrt
from typing import Callable

import numpy as np

Source = Callable[[float], float]


def bias_markov(x: Source, t_e: float, age: float) -> float:
    return x(t_e + age) - x(t_e)


def bias_history(x: Source, t_e: float, age: float, delta: float) -> float:
    predicted = x(t_e) + (x(t_e) - x(t_e - delta)) / delta * age
    return x(t_e + age) - predicted


def noise_gain_history(age: float, delta: float) -> float:
    r = age / delta
    return (1.0 + r) ** 2 + r * r


def mse_markov(x: Source, t_e: float, age: float, sigma: float) -> float:
    return bias_markov(x, t_e, age) ** 2 + sigma**2


def mse_history(x: Source, t_e: float, age: float, delta: float, sigma: float) -> float:
    return bias_history(x, t_e, age, delta) ** 2 + sigma**2 * noise_gain_history(age, delta)


def crossover_sigma(x: Source, t_e: float, age: float, delta: float) -> float:
    """Noise level at which the two estimators have equal MSE; 0 if the history estimator never wins."""

    numerator = bias_markov(x, t_e, age) ** 2 - bias_history(x, t_e, age, delta) ** 2
    if numerator <= 0.0:
        return 0.0
    return sqrt(numerator / (noise_gain_history(age, delta) - 1.0))


def simulate_errors(x: Source, t_e: float, age: float, delta: float, sigma: float, samples: int,
                    rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Errors X(t_o) - estimate of the Markov and history estimators over noisy record pairs."""

    y0 = x(t_e) + sigma * rng.standard_normal(samples)
    y1 = x(t_e - delta) + sigma * rng.standard_normal(samples)
    truth = x(t_e + age)
    return truth - y0, truth - (y0 + (y0 - y1) / delta * age)
