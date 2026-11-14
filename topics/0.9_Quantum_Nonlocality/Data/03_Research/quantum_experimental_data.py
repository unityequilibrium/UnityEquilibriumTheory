"""
Quantum Mechanics Experimental Data
===================================
Real data from published experiments.

References:
- Bell: Hensen et al. 2015, Nature 526, 682
- Double-slit: Arndt et al. 1999, Nature 401, 680
"""

import numpy as np

# =============================================================================
# BELL INEQUALITY (CHSH)
# =============================================================================

# Classical bound: |S| ≤ 2
# Quantum max: |S| ≤ 2√2 ≈ 2.828
CLASSICAL_BOUND = 2.0
QUANTUM_MAX = 2 * np.sqrt(2)  # Tsirelson bound

# Hensen 2015 loophole-free test
HENSEN_2015 = {
    "S_measured": 2.42,
    "S_error": 0.20,
    "p_value": 0.039,
    "distance_km": 1.3,
}


def bell_violation_sigma(S: float, S_error: float) -> float:
    """Calculate significance of Bell violation in sigma."""
    return (S - CLASSICAL_BOUND) / S_error


# =============================================================================
# DOUBLE-SLIT INTERFERENCE
# =============================================================================

def de_broglie_wavelength(mass_kg: float, velocity_m_s: float) -> float:
    """Calculate de Broglie wavelength."""
    from scipy.constants import h
    return h / (mass_kg * velocity_m_s)


# C60 experiment (Arndt 1999)
C60_MASS_KG = 720 * 1.66054e-27  # 720 amu
C60_VELOCITY = 200  # m/s
C60_WAVELENGTH = de_broglie_wavelength(C60_MASS_KG, C60_VELOCITY)
# ≈ 2.5 pm


if __name__ == "__main__":
    print("Quantum Experimental Data")
    print("=" * 50)
    
    print("\nBell Inequality (Hensen 2015):")
    S = HENSEN_2015["S_measured"]
    sig = bell_violation_sigma(S, HENSEN_2015["S_error"])
    print(f"  S = {S:.2f} ± {HENSEN_2015['S_error']:.2f}")
    print(f"  Classical bound = {CLASSICAL_BOUND}")
    print(f"  Violation = {sig:.1f} sigma")
    
    print("\nDouble-Slit (C60, Arndt 1999):")
    print(f"  λ_dB = {C60_WAVELENGTH*1e12:.2f} pm")
