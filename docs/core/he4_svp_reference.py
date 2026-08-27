"""Source-locked He-4 saturated-vapour-pressure reference functions.

The coefficients below directly transcribe the public interactive
implementation accompanying Donnelly and Barenghi (1998). They stay separate
from UET equations: this module evaluates reference properties only.
"""

from __future__ import annotations

import math


T_LAMBDA_K = 2.1768
SOURCE_URL = "https://www.mas.ncl.ac.uk/helium/"
SOURCE_DOI = "10.1063/1.556028"
SOURCE_SNAPSHOT_SHA256 = (
    "12665f1450f4a1370206e23a11eff4b13606041e870ccbf59805f842e423a25a"
)
SOURCE_SNAPSHOT_BYTES = 98_593


def _cubic_spline(control: list[float], knots: list[float], x: float) -> float:
    """Evaluate the source's cubic de Boor interpolation implementation."""

    n = len(control) - 5
    if x < knots[4] or x > knots[n + 5]:
        raise ValueError("temperature outside source interpolation range")

    lower = 0
    upper = n + 1
    while upper - lower > 1:
        midpoint = (lower + upper) // 2
        if x >= knots[midpoint + 4]:
            lower = midpoint
        else:
            upper = midpoint

    j = upper
    values = {index: control[index] for index in range(j, j + 4)}
    for order in range(1, 4):
        for index in range(j, j + 4 - order):
            numerator = (
                (x - knots[index + order]) * values[index + 1]
                + (knots[index + 4] - x) * values[index]
            )
            denominator = knots[index + 4] - knots[index + order]
            values[index] = numerator / denominator
    return values[j]


def total_density_kg_m3(temperature_k: float) -> float:
    """Return total He-4 density at saturated vapour pressure."""

    if not 0.0 <= temperature_k <= 4.9:
        raise ValueError("temperature must be in [0, 4.9] K")
    rho_0 = 0.1451397
    rho_lambda = 0.1461087
    if temperature_k < 1.344:
        coefficients = (
            0.0,
            -1.26935e-5,
            7.12413e-5,
            -16.7461e-5,
            8.75342e-5,
        )
        rho = rho_0 + sum(
            coefficients[index] * temperature_k ** (index + 1)
            for index in range(1, 5)
        )
        return rho * 1000.0

    reduced = temperature_k - T_LAMBDA_K
    if temperature_k <= T_LAMBDA_K:
        logarithmic = (0.0, -7.57537e-3, 6.87483e-3)
        polynomial = (
            0.0,
            3.79937e-3,
            1.86557e-3,
            4.88345e-3,
            0.0,
            0.0,
            0.0,
            0.0,
        )
    else:
        logarithmic = (0.0, -7.94605e-3, 5.07051e-3)
        polynomial = (
            0.0,
            -30.3511e-3,
            -10.2326e-3,
            -3.00636e-3,
            0.240720e-3,
            -2.45749e-3,
            1.53454e-3,
            -0.308182e-3,
        )
    delta_rho = sum(
        logarithmic[index]
        * reduced**index
        * (math.log(abs(reduced)) if reduced != 0.0 else 0.0)
        for index in range(1, 3)
    )
    delta_rho += sum(
        polynomial[index] * reduced**index for index in range(1, 8)
    )
    return rho_lambda * (1.0 + delta_rho) * 1000.0


_SUPERFLUID_KNOTS = [
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.443,
    0.9012,
    1.5419,
    1.7540,
    1.918,
    2.111,
    2.156991,
    2.173218,
    2.175647,
    2.176358,
    2.176568,
    2.176692,
    2.176766,
    2.176791,
    2.176798,
    2.176799,
    2.17679999,
    2.1768,
    2.1768,
    2.1768,
    2.1768,
]
_SUPERFLUID_CONTROL = [
    0.0,
    0.1451275432822459,
    0.1451334563362309,
    0.1449759191497576,
    0.1455008000684433,
    0.14075,
    0.1095,
    0.0815,
    0.0530,
    0.021,
    0.008904576,
    0.003053214,
    0.001494043,
    0.0008342826,
    0.000510686,
    0.00028379,
    0.0001287426,
    0.00005202569,
    0.00002153580,
    0.000008564206,
    0.000003567958,
    0.0,
]


def superfluid_density_kg_m3(temperature_k: float) -> float:
    """Return the source-recommended He-4 superfluid density."""

    if not 0.0 <= temperature_k <= T_LAMBDA_K:
        raise ValueError(f"temperature must be in [0, {T_LAMBDA_K}] K")
    return (
        _cubic_spline(_SUPERFLUID_CONTROL, _SUPERFLUID_KNOTS, temperature_k)
        * 1000.0
    )


def reference_row(temperature_k: float) -> dict[str, float | str]:
    """Return one dimensional, source-derived equilibrium row."""

    rho = total_density_kg_m3(temperature_k)
    rho_s = superfluid_density_kg_m3(temperature_k)
    return {
        "row_id": f"he4-svp-{temperature_k:.3f}K",
        "temperature_K": temperature_k,
        "total_density_kg_m3": rho,
        "superfluid_density_kg_m3": rho_s,
        "normal_density_kg_m3": rho - rho_s,
        "superfluid_fraction": rho_s / rho,
    }


def calibration_grid() -> list[dict[str, float | str]]:
    """Return the preregistered source grid, away from the critical endpoint."""

    return [
        reference_row(temperature)
        for temperature in (1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0)
    ]
