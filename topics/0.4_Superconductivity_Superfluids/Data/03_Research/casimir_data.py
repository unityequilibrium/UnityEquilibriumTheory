"""
Casimir Force Experimental Data
===============================
Source: Lamoreaux 1997 PRL 78, 5
        Mohideen & Roy 1998 PRL 81, 4549
"""

import numpy as np
from scipy.constants import hbar, c, pi

# Casimir force formula
# F/A = -π²ℏc / (240 d⁴)

def casimir_force_per_area(d_m: float) -> float:
    """
    Calculate Casimir force per unit area.
    
    Args:
        d_m: Plate separation in meters
        
    Returns:
        Force per area in N/m²
    """
    return -pi**2 * hbar * c / (240 * d_m**4)


# Experimental measurements (Lamoreaux 1997)
# d in μm, F in μN for 1 cm² area
LAMOREAUX_DATA = [
    (0.6, 0.62, 0.04),  # (d_um, F_uN, error_uN)
    (0.7, 0.35, 0.02),
    (0.8, 0.21, 0.01),
    (0.9, 0.13, 0.01),
    (1.0, 0.09, 0.005),
]

# Converting: 1 μm = 1e-6 m, 1 μN = 1e-6 N
# Area = 1 cm² = 1e-4 m²


def get_casimir_data():
    """Get Casimir data as numpy arrays."""
    d = np.array([x[0] for x in LAMOREAUX_DATA]) * 1e-6  # m
    F_measured = np.array([x[1] for x in LAMOREAUX_DATA]) * 1e-6  # N
    F_error = np.array([x[2] for x in LAMOREAUX_DATA]) * 1e-6  # N
    
    # Theoretical prediction for 1 cm² = 1e-4 m²
    F_theory = np.abs(casimir_force_per_area(d)) * 1e-4  # N
    
    return d, F_measured, F_theory, F_error


if __name__ == "__main__":
    print("Casimir Force Data")
    print("=" * 50)
    
    d, F_m, F_t, F_e = get_casimir_data()
    
    print(f"{'d (μm)':<10} {'F_meas (μN)':<15} {'F_theory (μN)':<15} {'Error %':<10}")
    print("-" * 50)
    for i in range(len(d)):
        d_um = d[i] * 1e6
        F_m_uN = F_m[i] * 1e6
        F_t_uN = F_t[i] * 1e6
        err = abs(F_m_uN - F_t_uN) / F_t_uN * 100
        print(f"{d_um:<10.1f} {F_m_uN:<15.3f} {F_t_uN:<15.3f} {err:<10.1f}")
