"""
Standard Model Particle Masses - PDG 2024
==========================================
Complete data for all fundamental particles.

Source: Particle Data Group, Review of Particle Physics (2024)
https://pdg.lbl.gov
"""

# All masses in GeV unless otherwise noted

# ============================================
# QUARKS (running masses at MS-bar 2 GeV for light, pole for heavy)
# ============================================
QUARK_MASSES = {
    # Light quarks (MS-bar at 2 GeV)
    "up": {"mass_MeV": 2.16, "error": 0.07, "charge": 2 / 3},
    "down": {"mass_MeV": 4.70, "error": 0.07, "charge": -1 / 3},
    "strange": {"mass_MeV": 93.5, "error": 0.8, "charge": -1 / 3},
    # Heavy quarks (MS-bar at own scale)
    "charm": {"mass_GeV": 1.273, "error": 0.005, "charge": 2 / 3},
    "bottom": {"mass_GeV": 4.183, "error": 0.007, "charge": -1 / 3},
    "top": {"mass_GeV": 172.57, "error": 0.29, "charge": 2 / 3},
}

# ============================================
# LEPTONS
# ============================================
LEPTON_MASSES = {
    "electron": {"mass_MeV": 0.51099895, "error": 0.00000015, "charge": -1},
    "muon": {"mass_MeV": 105.6583755, "error": 0.0000023, "charge": -1},
    "tau": {"mass_MeV": 1776.96, "error": 0.09, "charge": -1},
    # Neutrinos - only upper limits from cosmology
    "nu_e": {"mass_upper_eV": 0.8, "charge": 0},  # From KATRIN
    "nu_mu": {"mass_upper_eV": 0.8, "charge": 0},
    "nu_tau": {"mass_upper_eV": 0.8, "charge": 0},
}

# ============================================
# GAUGE BOSONS
# ============================================
GAUGE_BOSON_MASSES = {
    "photon": {"mass_GeV": 0, "upper_limit_eV": 1e-18, "spin": 1},
    "gluon": {"mass_GeV": 0, "spin": 1},
    "W_pm": {"mass_GeV": 80.3602, "error": 0.0099, "spin": 1},
    "Z_0": {"mass_GeV": 91.1876, "error": 0.0021, "spin": 1},
}

# ============================================
# HIGGS BOSON (LHC 2024)
# ============================================
HIGGS_BOSON = {
    "mass_GeV": 125.20,
    "error": 0.11,
    "width_GeV": 0.0032,  # Theoretical SM prediction
    "spin": 0,
    "source": "LHC ATLAS/CMS combined 2024",
}

# ============================================
# COUPLING CONSTANTS
# ============================================
COUPLING_CONSTANTS = {
    # Electromagnetic
    "alpha_EM": {
        "value": 1 / 137.035999084,
        "inverse": 137.035999084,
        "error": 0.000000021,
        "scale": "Thomson limit (Q=0)",
        "at_MZ": 1 / 127.955,
    },
    # Strong
    "alpha_s": {
        "value": 0.1179,
        "error": 0.0009,
        "scale_GeV": 91.1876,  # at M_Z
        "source": "PDG 2024 world average",
    },
    # Weak (Fermi constant)
    "G_F": {"value_GeV_inv2": 1.1663787e-5, "error": 0.0000006e-5, "source": "CODATA 2022"},
    # Weinberg angle
    "sin2_theta_W": {
        "value": 0.23147,  # Effective leptonic
        "error": 0.00044,
        "source": "LHCb 2024",
    },
}

# ============================================
# SUMMARY TABLE
# ============================================
ALL_PARTICLE_MASSES_GEV = {
    # Quarks
    "u": 2.16e-3,
    "d": 4.70e-3,
    "s": 93.5e-3,
    "c": 1.273,
    "b": 4.183,
    "t": 172.57,
    # Leptons
    "e": 0.511e-3,
    "mu": 0.106,
    "tau": 1.777,
    # Bosons
    "gamma": 0,
    "g": 0,
    "W": 80.36,
    "Z": 91.19,
    "H": 125.20,
}


if __name__ == "__main__":
    print("=" * 60)
    print("Standard Model Particle Masses - PDG 2024")
    print("=" * 60)

    print("\nQuarks:")
    for name, data in QUARK_MASSES.items():
        if "mass_MeV" in data:
            print(f"  {name:8s}: {data['mass_MeV']:>10.2f} MeV")
        else:
            print(f"  {name:8s}: {data['mass_GeV']:>10.3f} GeV")

    print("\nLeptons:")
    for name, data in LEPTON_MASSES.items():
        if "nu" not in name:
            print(f"  {name:8s}: {data['mass_MeV']:>10.6f} MeV")

    print("\nGauge Bosons:")
    for name, data in GAUGE_BOSON_MASSES.items():
        print(f"  {name:8s}: {data['mass_GeV']:>10.4f} GeV")

    print(f"\nHiggs: {HIGGS_BOSON['mass_GeV']:.2f} +/- {HIGGS_BOSON['error']} GeV")
