"""Layer 2 -> 3, wave D7 (model A): a lone body in space that has only Lambda.

Question (author, 2026-11-22: space exists before the free fall of all masses; "alone, nobody
divides entropy"; the disorder of a body spreads toward the order of space, law 3): put one body,
falling freely, into a universe with no other matter, only Lambda (de Sitter, the AI mapping of the
author's "space of the first kind"). Is it really alone? Where does its entropy go, how fast, and
does it reach absolute zero?

Standard inputs. A geodesic (freely falling) observer in de Sitter space sees thermal radiation at
the Gibbons-Hawking temperature T_dS = hbar H/(2 pi k) (Gibbons and Hawking 1977); H = H_L of wave D6.
The body has constant heat capacity C, area A and black surface, and exchanges radiation with the
bath: C dT/dt = -sigma A (T^4 - Tb^4).

[AI derivation]
D7a Cooling law. With kappa = sigma A / C, the time to cool from T0 to T1 (both above Tb) is
        t = [ ln((T+Tb)/(T-Tb)) + 2 atan(T/Tb) ]_{T1}^{T0} / (4 kappa Tb^3).
    As Tb -> 0 it tends to (T1^-3 - T0^-3)/(3 kappa), with corrections of order (Tb/T)^4.
D7b Never zero, equilibrium only approached. T > Tb at every finite time; near the bath
    T - Tb ~ exp(-4 kappa Tb^3 t), so the last relaxation time is C/(4 sigma A Tb^3).
    Law 3: the body cannot reach 0 K because the bath of space-only is not at 0 K. Law 0: it
    reaches equilibrium only as a limit.
D7c Entropy bookkeeping. The body loses C ln(T0/T1); the bath gains C (T0 - T1)/Tb; the sum is
    >= 0, zero only when T0 = Tb (to second order C eps^2/2 with T0 = Tb(1 + eps)). Because Tb is
    tiny, almost all of the entropy ends in space: the lone body is not alone, the horizon of
    Lambda-only space divides its entropy.
D7d Wavelength mismatch. The bath's thermal wavelength is an exact multiple of the horizon:
        lambda_T = h c / (k T_dS) = 4 pi^2 c / H     (Wien peak: 4 pi^2/4.965 = 7.95 c/H).
    No body inside the horizon is as large as the radiation it would have to exchange, so the
    blackbody contact of D7a cannot hold near Tb: real coupling is weaker, and the relaxation time
    of D7b is a lower bound. Illustrative AI choice (a rock of radius 1 m, density 3000 kg/m^3,
    c_p 800 J/(kg K), blackbody): kappa = 7.1e-14 K^-3 s^-1; 300 K -> 3 K in about 5.5e3 yr; last
    relaxation time >= 1.0e94 yr. The blackbody law fails already below about hc/(k R) = 0.014 K.

Consequence [AI interpretation]: in the author's cycle the step "disorder spreads into space" is
real for space of the first kind (it has a temperature), but for any ordinary body it is
infinitely slow. In practice entropy is divided by other matter and radiation (the second kind:
CMB, stars, gas), which is model B. This sharpens SYNTHESIS_AUDIT C2: space as a heat bath exists
only through its horizon, and its wavelength is horizon-sized.

Nearest known theory: Newton/Stefan cooling, Gibbons-Hawking de Sitter temperature. Not
UET-distinct. Left out: low-temperature heat capacity (Debye C ~ T^3), emissivity below
hc/(kR), the CMB (absent by construction), portal drag (would be the only friction with space).
"""

from __future__ import annotations

import importlib
from math import atan, atanh, log, pi

from scipy.integrate import quad

cd = importlib.import_module("docs.core.03_lanes.persistence.uet_cosmic_divider")

K_B, HBAR, C_LIGHT = cd.K_B, cd.HBAR, cd.C_LIGHT
H_PLANCK = 2.0 * pi * HBAR
SIGMA_SB = pi ** 2 * K_B ** 4 / (60.0 * HBAR ** 3 * C_LIGHT ** 2)
YEAR = cd.YEAR


def bath_temperature(H: float = cd.H_L) -> float:
    return cd.de_sitter_temperature(H)


def _h(x: float) -> float:
    """(atanh x - atan x) / x^3 = sum_n 2 x^(4n) / (4n + 3); the primitive of D7a is
    pi + 2 (atanh x - atan x) with x = Tb/T. The series avoids cancellation for small x."""

    if x >= 0.1:
        return (atanh(x) - atan(x)) / x ** 3
    return sum(2.0 * x ** (4 * n) / (4 * n + 3) for n in range(12))


def cooling_time_closed_form(T0: float, T1: float, Tb: float, kappa: float) -> float:
    """D7a in the cancellation-free form t = [h(Tb/T1)/T1^3 - h(Tb/T0)/T0^3] / (2 kappa)."""

    return (_h(Tb / T1) / T1 ** 3 - _h(Tb / T0) / T0 ** 3) / (2.0 * kappa)


def cooling_time_numeric(T0: float, T1: float, Tb: float, kappa: float) -> float:
    """General path: t = int_{T1}^{T0} dT / (kappa (T^4 - Tb^4)), integrated in ln T."""

    from math import exp
    value, _ = quad(lambda u: exp(u) / (kappa * (exp(4 * u) - Tb ** 4)), log(T1), log(T0),
                    epsabs=0.0, epsrel=1e-13, limit=400)
    return value


def entropy_changes(T0: float, T1: float, Tb: float, C: float) -> tuple[float, float]:
    """(body, bath) entropy changes when the body cools from T0 to T1 against a bath at Tb."""

    return -C * log(T0 / T1), C * (T0 - T1) / Tb


def thermal_wavelength(T: float) -> float:
    return H_PLANCK * C_LIGHT / (K_B * T)


def rock(radius: float = 1.0, density: float = 3000.0, c_p: float = 800.0) -> tuple[float, float]:
    """Illustrative body (AI choice): heat capacity and kappa = sigma A / C."""

    C = 4.0 / 3.0 * pi * radius ** 3 * density * c_p
    A = 4.0 * pi * radius ** 2
    return C, SIGMA_SB * A / C
