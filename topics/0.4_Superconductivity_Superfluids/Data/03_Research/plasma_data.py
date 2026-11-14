"""
Plasma Physics Data
===================
Real measurements from Tokamak fusion (JET, ITER) and Space Plasma (Parker Solar Probe).

Sources:
- JET Joint European Torus (2024 results)
- Parker Solar Probe (NASA 2024/2025)
"""

# Hardcoded Data (Embedded for Robustness)
_data = {
    "fusion": {
        "jet_2024": {
            "energy_output_MJ": 69.2,
            "duration_sec": 5.0,
            "plasma_temp_C": 150000000,
            "Q_value": 0.33,
        },
        "iter_design": {"target_Q": 10, "first_plasma": 2025},
    },
    "space": {
        "parker_solar_probe": {
            "origin": "Coronal Holes",
            "phenomena": "Switchbacks (Magnetic Zig-Zags)",
        }
    },
}

# ============================================
# TOKAMAK FUSION (Magnetic Confinement)
# ============================================

JET_RECORD_2024 = _data["fusion"]["jet_2024"]
ITER_DESIGN = _data["fusion"]["iter_design"]

# ============================================
# SPACE PLASMA (Solar Wind)
# ============================================

PARKER_SOLAR_PROBE = _data["space"]["parker_solar_probe"]


# ============================================
# PLASMA PARAMETERS FUSION
# ============================================


def lawson_criterion(n_density_m3, T_keV, tau_s):
    """
    Lawson Triple Product: n * T * tau
    Ignition condition: n*T*tau > 3e21 keV s m^-3
    """
    return n_density_m3 * T_keV * tau_s


if __name__ == "__main__":
    print("=" * 60)
    print("PLASMA PHYSICS DATA")
    print("=" * 60)

    print("\nJET 2024 Record:")
    print(f"  Energy: {JET_RECORD_2024['energy_output_MJ']} MJ")
    print(f"  Duration: {JET_RECORD_2024['duration_sec']} s")
    print(f"  Temp: {JET_RECORD_2024['plasma_temp_C']/1e6:.1f} M C")

    print("\nITER Goals:")
    print(f"  Target Q: {ITER_DESIGN['target_Q']}")
    print(f"  First Plasma: {ITER_DESIGN['first_plasma']}")

    print("\nParker Solar Probe:")
    print(f"  Origin: {PARKER_SOLAR_PROBE['origin']}")
    print(f"  Discovery: {PARKER_SOLAR_PROBE['phenomena']}")
