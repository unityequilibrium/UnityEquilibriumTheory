"""
QCD Strong Force Data - PDG 2024
================================
Real experimental data for validating UET strong force predictions.

Sources:
- Particle Data Group (PDG) Review of Particle Physics
- ATLAS/CMS alpha_s running measurements
- Lattice QCD hadron mass spectrum
"""

# PDG 2024 - Strong coupling constant running
# alpha_s at different energy scales Q
ALPHA_S_RUNNING = [
    # (Q in GeV, alpha_s, error)
    (1.5, 0.336, 0.008),  # Tau decays
    (5.0, 0.213, 0.005),  # Bottom quark mass
    (10.0, 0.178, 0.004),  # Upsilon decays
    (34.0, 0.144, 0.003),  # PETRA e+e-
    (91.2, 0.1186, 0.0007),  # Z boson mass (reference scale)
    (133.0, 0.113, 0.004),  # LEP1.5
    (161.0, 0.109, 0.004),  # LEP2
    (172.0, 0.108, 0.004),  # LEP2
    (183.0, 0.106, 0.003),  # LEP2
    (189.0, 0.105, 0.003),  # LEP2
    (200.0, 0.104, 0.003),  # LEP2
    (400.0, 0.094, 0.004),  # LHC jets
    (1000.0, 0.085, 0.005),  # LHC jets 1 TeV
]

# World average at M_Z
ALPHA_S_MZ = {"value": 0.1186, "error": 0.0007, "year": 2024, "source": "PDG Review"}

# PDG 2024 - Hadron masses (MeV)
# For comparison with Lattice QCD and UET predictions
HADRON_MASSES = {
    # Light mesons
    "pion_pm": {"mass": 139.57, "error": 0.00018, "quark": "ud"},
    "pion_0": {"mass": 134.98, "error": 0.0005, "quark": "uu/dd"},
    "kaon_pm": {"mass": 493.68, "error": 0.016, "quark": "us"},
    "kaon_0": {"mass": 497.61, "error": 0.013, "quark": "ds"},
    "eta": {"mass": 547.86, "error": 0.017, "quark": "qq"},
    "eta_prime": {"mass": 957.78, "error": 0.06, "quark": "qq"},
    "rho": {"mass": 775.26, "error": 0.23, "quark": "ud"},
    "omega": {"mass": 782.66, "error": 0.13, "quark": "qq"},
    "phi": {"mass": 1019.46, "error": 0.016, "quark": "ss"},
    # Light baryons
    "proton": {"mass": 938.27, "error": 0.00001, "quark": "uud"},
    "neutron": {"mass": 939.57, "error": 0.00001, "quark": "udd"},
    "lambda": {"mass": 1115.68, "error": 0.006, "quark": "uds"},
    "sigma_p": {"mass": 1189.37, "error": 0.07, "quark": "uus"},
    "sigma_0": {"mass": 1192.64, "error": 0.02, "quark": "uds"},
    "sigma_m": {"mass": 1197.45, "error": 0.03, "quark": "dds"},
    "xi_0": {"mass": 1314.86, "error": 0.20, "quark": "uss"},
    "xi_m": {"mass": 1321.71, "error": 0.07, "quark": "dss"},
    "omega_m": {"mass": 1672.45, "error": 0.29, "quark": "sss"},
    # Heavy mesons
    "D_pm": {"mass": 1869.66, "error": 0.05, "quark": "cd"},
    "D_0": {"mass": 1864.84, "error": 0.05, "quark": "cu"},
    "J_psi": {"mass": 3096.90, "error": 0.006, "quark": "cc"},
    "B_pm": {"mass": 5279.41, "error": 0.07, "quark": "ub"},
    "B_0": {"mass": 5279.72, "error": 0.08, "quark": "db"},
    "upsilon_1S": {"mass": 9460.40, "error": 0.09, "quark": "bb"},
}

# QCD String tension (confinement parameter)
# From Lattice QCD
STRING_TENSION = {
    "value": 0.44,  # GeV/fm (or about 1 GeV/fm in alternative convention)
    "error": 0.02,
    "source": "Lattice QCD review",
}

# Quark masses (PDG current quark masses, MS-bar at 2 GeV)
QUARK_MASSES_MEV = {
    "up": {"value": 2.16, "error_up": 0.49, "error_down": 0.26},
    "down": {"value": 4.67, "error_up": 0.48, "error_down": 0.17},
    "strange": {"value": 93.4, "error_up": 8.6, "error_down": 3.4},
    "charm": {"value": 1270, "error": 20},  # at m_c scale
    "bottom": {"value": 4180, "error_up": 30, "error_down": 20},  # at m_b scale
    "top": {"value": 172500, "error": 700},  # pole mass
}

# Lambda_QCD (scale parameter)
LAMBDA_QCD = {
    "nf5": {"value": 210, "error": 14, "unit": "MeV"},  # 5 flavors
    "nf4": {"value": 292, "error": 16, "unit": "MeV"},  # 4 flavors
    "nf3": {"value": 332, "error": 17, "unit": "MeV"},  # 3 flavors
}


def get_alpha_s_at_scale(Q_GeV: float) -> float:
    """
    Calculate alpha_s at energy scale Q using 1-loop running.

    alpha_s(Q) = alpha_s(MZ) / (1 + (alpha_s(MZ)*b0/2pi)*ln(Q^2/MZ^2))

    b0 = (33 - 2*nf) / 3 for nf active flavors
    """
    import numpy as np

    MZ = 91.2  # GeV
    alpha_MZ = ALPHA_S_MZ["value"]

    # Determine number of active flavors
    if Q_GeV < 1.27:  # below charm
        nf = 3
    elif Q_GeV < 4.18:  # below bottom
        nf = 4
    elif Q_GeV < 172.5:  # below top
        nf = 5
    else:
        nf = 6

    b0 = (33 - 2 * nf) / 3

    # 1-loop running
    log_ratio = np.log(Q_GeV**2 / MZ**2)
    alpha_Q = alpha_MZ / (1 + (alpha_MZ * b0 / (2 * np.pi)) * log_ratio)

    return alpha_Q


if __name__ == "__main__":
    import numpy as np

    print("=" * 60)
    print("QCD Strong Force Data - PDG 2024")
    print("=" * 60)

    print(f"\nWorld Average: alpha_s(M_Z) = {ALPHA_S_MZ['value']} +/- {ALPHA_S_MZ['error']}")

    print("\nalpha_s running:")
    print("-" * 40)
    print(f"{'Q (GeV)':<10} {'alpha_s':<10} {'error':<10}")
    print("-" * 40)
    for Q, alpha, err in ALPHA_S_RUNNING:
        print(f"{Q:<10.1f} {alpha:<10.4f} {err:<10.4f}")

    print(f"\nTotal hadrons: {len(HADRON_MASSES)}")
    print(f"Lambda_QCD (nf=5): {LAMBDA_QCD['nf5']['value']} +/- {LAMBDA_QCD['nf5']['error']} MeV")
