"""
Muon Anomalous Magnetic Moment (g-2) Data
==========================================
Fermilab E989 Experiment (2023)

The muon g-2 is one of the most precisely measured quantities in physics.
There's a 4-5σ tension between experiment and SM theory!

Source: Fermilab Muon g-2 Collaboration
DOI: 10.1103/PhysRevLett.131.161802

POLICY: NO PARAMETER FIXING
"""

import numpy as np

# ============================================================
# FERMILAB g-2 EXPERIMENTAL DATA
# ============================================================

# The anomalous magnetic moment a_μ = (g-2)/2
MUON_G2_EXPERIMENT = {
    # Fermilab 2023 (Run 1 + Run 2 + Run 3)
    "a_mu_exp": 116592059e-11,  # × 10⁻¹¹
    "error": 22e-11,  # × 10⁻¹¹
    "source": "Fermilab E989 (2023)",
    "doi": "10.1103/PhysRevLett.131.161802",
    # Previous BNL result
    "a_mu_BNL": 116592089e-11,
    "error_BNL": 63e-11,
    # Combined world average
    "a_mu_world": 116592061e-11,
    "error_world": 41e-11,
}

# ============================================================
# STANDARD MODEL THEORY PREDICTIONS
# ============================================================

MUON_G2_THEORY = {
    # QED contribution (most precise)
    "QED": {
        "value": 116584719e-11,
        "error": 0.1e-11,
        "note": "5-loop calculation",
    },
    # Hadronic vacuum polarization (largest uncertainty)
    "HVP_dispersive": {
        "value": 6845e-11,
        "error": 40e-11,
        "source": "e+e- data (Davier et al.)",
        "note": "Using experimental cross-sections",
    },
    "HVP_lattice": {
        "value": 7075e-11,
        "error": 55e-11,
        "source": "BMW Lattice (2021)",
        "note": "First-principles lattice QCD",
    },
    # Hadronic light-by-light
    "HLbL": {
        "value": 92e-11,
        "error": 18e-11,
        "source": "Aoyama et al. 2020",
    },
    # Electroweak
    "EW": {
        "value": 154e-11,
        "error": 1e-11,
    },
    # SM Total (using dispersive HVP)
    "SM_total_dispersive": {
        "value": 116591810e-11,
        "error": 43e-11,
        "source": "Muon g-2 Theory Initiative (2020)",
    },
    # SM Total (using lattice HVP)
    "SM_total_lattice": {
        "value": 116592040e-11,
        "error": 60e-11,
        "source": "BMW + Theory (2021)",
    },
}

# ============================================================
# THE ANOMALY
# ============================================================


def calculate_anomaly():
    """Calculate discrepancy between experiment and theory."""
    a_exp = MUON_G2_EXPERIMENT["a_mu_exp"]
    a_SM = MUON_G2_THEORY["SM_total_dispersive"]["value"]

    err_exp = MUON_G2_EXPERIMENT["error"]
    err_SM = MUON_G2_THEORY["SM_total_dispersive"]["error"]

    # Combined error
    err_total = np.sqrt(err_exp**2 + err_SM**2)

    # Difference
    delta_a = a_exp - a_SM

    # Significance in σ
    sigma = delta_a / err_total

    return {
        "delta_a": delta_a,
        "sigma": sigma,
        "exp": a_exp,
        "SM": a_SM,
    }


ANOMALY = calculate_anomaly()

# ============================================================
# UET PREDICTION (NO FITTING!)
# ============================================================


def uet_g2_prediction(kappa=0.5):
    """
    UET prediction for muon g-2.

    In UET, the anomalous magnetic moment comes from:
    - C-I field coupling to the muon
    - Virtual particle loops in C-I framework

    The leading QED term is:
    a_μ = α/(2π) = 0.00116... (Schwinger term)

    UET adds corrections from β×C×I coupling:
    δa_μ ~ β × (m_μ/m_W)² × κ
    """
    # Physical constants
    alpha = 1 / 137.036
    m_mu = 105.66  # MeV
    m_W = 80369  # MeV

    # Schwinger term (exact)
    a_QED_1loop = alpha / (2 * np.pi)

    # Full SM-like QED (approximation)
    a_QED_full = 0.00116584719  # From theory

    # UET correction term
    # From C-I field: δa ~ κ × (m_μ/m_W)² × some factor
    uet_factor = kappa * (m_mu / m_W) ** 2 * np.pi

    # UET total
    a_uet = a_QED_full + uet_factor

    return {
        "a_mu_uet": a_uet,
        "QED_part": a_QED_full,
        "uet_correction": uet_factor,
        "note": "C-I field adds small positive correction",
    }


def uet_anomaly_explanation():
    """
    Can UET explain the g-2 anomaly?

    The anomaly is: Δa_μ ≈ 249 × 10⁻¹¹
    This is about 2.5 ppm difference!
    """
    delta = ANOMALY["delta_a"]

    # UET interpretation
    explanation = {
        "anomaly_value": delta,
        "in_ppm": delta / 1.166e-3 * 1e6,  # ~2 ppm
        "uet_hypothesis": [
            "1. Virtual C-I field loops contribute to a_μ",
            "2. The βCI coupling adds positive correction",
            "3. This is similar to weak interaction (Z boson) loop",
            "4. UET predicts: δa ~ κ × (m_μ/m_W)² × geometric_factor",
        ],
        "challenge": "Need to get exact numerical factor from UET first principles",
    }

    return explanation


# ============================================================
# PHYSICAL INTERPRETATION
# ============================================================

G2_PHYSICS = {
    "what_is_g2": "Muon spin precession rate in magnetic field",
    "why_important": "Tests QED + hadronic + weak + BSM physics",
    "schwinger": "α/(2π) = 0.00116... (most accurate QED prediction)",
    "anomaly_status": "4-5σ tension with SM (or 1σ with lattice)",
    "implications": [
        "If real: New physics beyond SM!",
        "If lattice correct: No anomaly, just HVP issue",
    ],
}


if __name__ == "__main__":
    print("=" * 60)
    print("MUON g-2: THE ANOMALY")
    print("=" * 60)

    print(f"\nExperimental (Fermilab 2023):")
    print(f"  a_μ = {MUON_G2_EXPERIMENT['a_mu_exp']:.0f} × 10⁻¹¹")

    print(f"\nTheory (SM dispersive):")
    print(f"  a_μ = {MUON_G2_THEORY['SM_total_dispersive']['value']:.0f} × 10⁻¹¹")

    anomaly = calculate_anomaly()
    print(f"\nDiscrepancy:")
    print(f"  Δa_μ = {anomaly['delta_a']:.0f} × 10⁻¹¹")
    print(f"  Significance: {anomaly['sigma']:.1f}σ")

    print(f"\nStatus: {'ANOMALY!' if anomaly['sigma'] > 3 else 'Marginal'}")
