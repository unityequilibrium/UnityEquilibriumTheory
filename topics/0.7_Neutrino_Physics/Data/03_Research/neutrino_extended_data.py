"""
Extended Neutrino Data
======================
Recent experimental results from KATRIN (mass) and Borexino (solar flux).

Sources:
- KATRIN Collaboration 2024/2025 (Nature Physics)
- Borexino Collaboration 2020/2023 (Nature, Phys. Rev. Lett.)
"""

# ============================================
# NEUTRINO MASS (Direct - Model Independent)
# ============================================

KATRIN_RESULTS = {
    "experiment": "KATRIN (Karlsruhe Tritium Neutrino)",
    "mass_limit_eV": 0.45,  # Upper limit (90% CL)
    "previous_limit_eV": 0.8,  # 2022
    "year": 2025,
    "method": "Tritium beta decay endpoint",
    "status": "New world record (factor of 2 improvement)",
    "goal_sensitivity_eV": 0.2,
    "source": "KATRIN 2025 Nature Physics release",
}

# ============================================
# SOLAR NEUTRINO FLUX (Borexino)
# ============================================

SOLAR_NEUTRINOS_BOREXINO = {
    "CNO_cycle": {
        "flux_cm2_s": 6.7e8,
        "error_plus": 1.2e8,
        "error_minus": 0.8e8,
        "significance_sigma": 5.0,  # Discovery level
        "year": 2023,
        "notes": "First direct evidence of CNO cycle in Sun (1% of energy)",
    },
    "pp_chain": {
        "pp_flux": 5.98e10,  # cm^-2 s^-1
        "Be7_flux": 4.99e9,
        "pep_flux": 1.27e8,
        "B8_flux": 5.46e6,
        "status": "Precision confirmation of SSM",
        "year": 2020,
    },
}

# ============================================
# COSMIC NEUTRINO BACKGROUND (Theoretical)
# ============================================

CNB_DATA = {
    "temperature_K": 1.95,
    "density_per_cm3": 336,  # Total (all species)
    "status": "Not yet directly detected (PTOLEMY proposed)",
}


if __name__ == "__main__":
    print("=" * 60)
    print("EXTENDED NEUTRINO DATA (2024-2025)")
    print("=" * 60)

    print(f"\nKATRIN Mass Limit: < {KATRIN_RESULTS['mass_limit_eV']} eV (90% CL)")
    print(f"Status: {KATRIN_RESULTS['status']}")

    print("\nBorexino Solar Flux:")
    print(f"  CNO Flux: {SOLAR_NEUTRINOS_BOREXINO['CNO_cycle']['flux_cm2_s']:.1e} cm^-2 s^-1")
    print(
        f"  Significance: {SOLAR_NEUTRINOS_BOREXINO['CNO_cycle']['significance_sigma']} sigma (Discovery!)"
    )

    print(f"\npp-Chain Flux (Borexino):")
    for reactions, flux in SOLAR_NEUTRINOS_BOREXINO["pp_chain"].items():
        if isinstance(flux, float):
            print(f"  {reactions}: {flux:.2e}")
