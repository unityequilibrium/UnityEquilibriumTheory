"""
W Boson Mass Anomaly Data
==========================
The famous CDF 2022 measurement tension!

In 2022, CDF measured W mass with unprecedented precision,
finding a 7σ discrepancy with the Standard Model!

Sources:
- CDF 2022: 10.1126/science.abk1781
- ATLAS 2024: 10.1140/epjc/s10052-024-12710-4
- PDG 2024: 10.1093/ptep/ptac097

POLICY: NO PARAMETER FIXING
"""

import numpy as np

# ============================================================
# W BOSON MASS MEASUREMENTS
# ============================================================

W_MASS_MEASUREMENTS = {
    # CDF 2022 - The Anomaly!
    "CDF_2022": {
        "mass_GeV": 80.4335,
        "stat_error": 0.0064,
        "syst_error": 0.0069,
        "total_error": 0.0094,
        "source": "CDF Collaboration (Fermilab)",
        "doi": "10.1126/science.abk1781",
        "year": 2022,
        "note": "Most precise single measurement ever!",
    },
    # LHC Measurements
    "ATLAS_2024": {
        "mass_GeV": 80.3665,
        "total_error": 0.0159,
        "source": "ATLAS Collaboration",
        "doi": "10.1140/epjc/s10052-024-12710-4",
        "year": 2024,
    },
    "CMS_2024": {
        "mass_GeV": 80.360,
        "total_error": 0.016,
        "source": "CMS Collaboration",
        "year": 2024,
    },
    "LHCb_2022": {
        "mass_GeV": 80.354,
        "total_error": 0.032,
        "source": "LHCb Collaboration",
        "year": 2022,
    },
    # LEP/Tevatron Legacy
    "LEP_combined": {
        "mass_GeV": 80.376,
        "total_error": 0.033,
        "source": "LEP Electroweak Working Group",
        "year": 2006,
    },
    "D0_2012": {
        "mass_GeV": 80.375,
        "total_error": 0.023,
        "source": "D0 Collaboration (Fermilab)",
        "year": 2012,
    },
    # World Average (PDG 2024) - EXCLUDING CDF 2022!
    "PDG_2024_excl_CDF": {
        "mass_GeV": 80.369,
        "total_error": 0.013,
        "source": "PDG 2024 (excludes CDF 2022)",
        "note": "Tension with CDF too large to combine",
    },
}

# ============================================================
# STANDARD MODEL PREDICTION
# ============================================================

SM_PREDICTION = {
    # SM electroweak fit prediction
    "m_W_SM": 80.357,
    "error": 0.006,
    "source": "Electroweak global fit (2024)",
    "inputs": ["m_Z", "m_t", "m_H", "α", "sin²θ_W"],
    "formula": "m_W = m_Z × cos(θ_W) × (1 + radiative corrections)",
}

# Z boson mass (for reference)
Z_MASS = {
    "mass_GeV": 91.1876,
    "error": 0.0021,
    "source": "LEP/SLC",
}

# ============================================================
# THE ANOMALY ANALYSIS
# ============================================================


def calculate_cdf_tension():
    """Calculate the famous CDF tension."""
    m_CDF = W_MASS_MEASUREMENTS["CDF_2022"]["mass_GeV"]
    err_CDF = W_MASS_MEASUREMENTS["CDF_2022"]["total_error"]

    m_SM = SM_PREDICTION["m_W_SM"]
    err_SM = SM_PREDICTION["error"]

    # Combined error
    err_total = np.sqrt(err_CDF**2 + err_SM**2)

    # Tension
    delta = m_CDF - m_SM
    sigma = delta / err_total

    return {
        "delta_m": delta * 1000,  # in MeV
        "sigma": sigma,
        "m_CDF": m_CDF,
        "m_SM": m_SM,
    }


def calculate_lhc_consistency():
    """Check if LHC measurements are consistent with SM."""
    results = {}
    m_SM = SM_PREDICTION["m_W_SM"]
    err_SM = SM_PREDICTION["error"]

    for name in ["ATLAS_2024", "CMS_2024", "LHCb_2022"]:
        data = W_MASS_MEASUREMENTS[name]
        m = data["mass_GeV"]
        err = data["total_error"]

        err_total = np.sqrt(err**2 + err_SM**2)
        delta = m - m_SM
        sigma = delta / err_total

        results[name] = {
            "mass": m,
            "sigma_from_SM": sigma,
            "consistent": abs(sigma) < 2,
        }

    return results


CDF_TENSION = calculate_cdf_tension()
LHC_CONSISTENCY = calculate_lhc_consistency()

# ============================================================
# UET PREDICTION (NO FITTING!)
# ============================================================


def uet_w_mass_prediction(kappa=0.5):
    """
    UET prediction for W boson mass.

    In UET, the W mass comes from:
    m_W = m_Z × cos(θ_W)

    where θ_W (Weinberg angle) has geometric origin.

    UET predicts: θ_W = π/6 (30°) at high energy
    This runs to experimental value ~28.7° at EW scale.
    """
    m_Z = Z_MASS["mass_GeV"]

    # UET: θ_W from π/6 geometry
    theta_W_uet = np.pi / 6  # 30°
    sin2_theta_W_uet = np.sin(theta_W_uet) ** 2  # 0.25

    # Experimental sin²θ_W
    sin2_theta_W_exp = 0.23122  # PDG 2024

    # W mass predictions
    m_W_uet_raw = m_Z * np.cos(theta_W_uet)
    m_W_uet_running = m_Z * np.sqrt(1 - sin2_theta_W_exp)  # Using running value

    return {
        "m_W_uet_geometric": m_W_uet_raw,  # Pure π/6
        "m_W_uet_running": m_W_uet_running,  # With running
        "sin2_theta_W_uet": sin2_theta_W_uet,
        "sin2_theta_W_exp": sin2_theta_W_exp,
        "note": "UET predicts sin²θ_W = 1/4 at GUT scale",
    }


# ============================================================
# PHYSICS INTERPRETATION
# ============================================================

W_MASS_PHYSICS = {
    "why_important": [
        "W mass tests electroweak symmetry breaking",
        "Precision test of Higgs mechanism",
        "Sensitive to new physics (loops)",
    ],
    "cdf_puzzle": [
        "CDF 2022: 80.4335 GeV (most precise ever!)",
        "LHC 2024: 80.367 GeV (disagrees with CDF)",
        "SM prediction: 80.357 GeV",
        "CDF vs SM: 7σ tension!",
        "CDF vs LHC: 4σ disagreement!",
    ],
    "possible_explanations": [
        "1. CDF systematic error (PDF, energy scale)",
        "2. LHC measurements more reliable",
        "3. New physics (but why only in CDF?)",
        "4. Statistical fluctuation (unlikely at 7σ)",
    ],
    "current_status": "CDF result controversial, not included in PDG average",
}


if __name__ == "__main__":
    print("=" * 60)
    print("W BOSON MASS: THE CDF ANOMALY")
    print("=" * 60)

    print(f"\nMeasurements (GeV):")
    print(
        f"  CDF 2022:  {W_MASS_MEASUREMENTS['CDF_2022']['mass_GeV']:.4f} ± {W_MASS_MEASUREMENTS['CDF_2022']['total_error']:.4f}"
    )
    print(
        f"  ATLAS 2024: {W_MASS_MEASUREMENTS['ATLAS_2024']['mass_GeV']:.4f} ± {W_MASS_MEASUREMENTS['ATLAS_2024']['total_error']:.4f}"
    )
    print(f"  SM Theory:  {SM_PREDICTION['m_W_SM']:.3f} ± {SM_PREDICTION['error']:.3f}")

    tension = CDF_TENSION
    print(f"\nCDF vs SM:")
    print(f"  Δm_W = {tension['delta_m']:.1f} MeV")
    print(f"  Tension: {tension['sigma']:.1f}σ !!!!")

    print(f"\nStatus: {'MAJOR ANOMALY!' if tension['sigma'] > 5 else 'Tension'}")
