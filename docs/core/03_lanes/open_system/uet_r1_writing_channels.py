"""R1: how strongly does energy use "write onto space"? (author points 7 and 8)

Two channels exist in established physics, with no free parameter:

1. Gravity. Energy that leaves a body as light or wind lowers its mass-energy, and the
   field equation G = kappa T writes that change into the curvature around it:
       d(GM)/dt / GM = Gdot/G + Mdot/M,   Mdot_rad = -L/c^2
   Orbits respond adiabatically: a ~ 1/(GM), so the orbits of the planets expand and the
   trace is readable later from the ephemerides (Noerdlinger 2008).
2. Radiation entropy. Light emitted at temperature T carries entropy 4E/(3T), i.e.
       bits/s = (4/3) L / (k_B T ln 2)
   at the emitting surface; re-thermalisation at lower temperature only adds bits.

The UET field psi would add a third channel; T005 bounds it. R1 asks whether the
author's "writing" is already fully accounted for by channels 1 and 2.

SI units.
"""

from __future__ import annotations

from math import log

C = 299_792_458.0                 # m/s (exact)
K_B = 1.380649e-23                # J/K (exact)
YEAR = 365.25 * 86400.0           # Julian year, s
L_SUN = 3.828e26                  # W, IAU 2015 Resolution B3 nominal
GM_SUN = 1.3271244e20             # m^3 s^-2, IAU 2015 nominal
G_NEWTON = 6.67430e-11            # m^3 kg^-1 s^-2, CODATA 2018
T_EFF_SUN = 5772.0                # K, IAU 2015 nominal
M_SUN = GM_SUN / G_NEWTON         # kg


def radiative_mass_loss_fraction_per_year(luminosity: float = L_SUN, mass: float = M_SUN) -> float:
    """-Mdot/M per year from luminosity alone (positive number)."""

    return luminosity / (C * C * mass) * YEAR


def predicted_gm_rate_per_year(wind_fraction_per_year: float, gdot_over_g: float = 0.0,
                               luminosity: float = L_SUN, mass: float = M_SUN) -> float:
    """d(GM)/dt / GM per year (negative for mass loss)."""

    return gdot_over_g - radiative_mass_loss_fraction_per_year(luminosity, mass) - wind_fraction_per_year


def radiation_bits_per_second(luminosity: float, temperature: float) -> float:
    """Entropy carried by blackbody light, in bits per second."""

    return 4.0 / 3.0 * luminosity / (K_B * temperature * log(2.0))
