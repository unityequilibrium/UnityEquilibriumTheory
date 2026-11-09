"""
Download Real Superconductor Critical Temperature Data
=======================================================
Sources:
1. NIMS SuperCon Database (MatNavi)
2. UCI Machine Learning Database (Hamidieh)
3. MIT Experimental Data

References:
- McMillan equation: Tc = (ΘD/1.45) * exp(-1.04(1+λ)/(λ-μ*(1+0.62λ)))
- Allen-Dynes modification for strong coupling
- BCS theory for conventional superconductors

Updated: 2026-01-02
"""

import json
import os
from pathlib import Path

# Real experimental data from literature
# Sources: Kittel (Solid State Physics), Nature reviews, Physical Review Letters

SUPERCONDUCTOR_DATA = {
    "description": "Real experimental superconductor data with references",
    "sources": [
        "NIMS SuperCon Database",
        "MIT Junior Lab",
        "Kittel Solid State Physics 8th Ed",
        "McMillan (1968) Phys. Rev. 167, 331",
    ],
    "superconductors": [
        # ======= TYPE-I (Classical BCS) =======
        {
            "name": "Aluminum (Al)",
            "Tc_K": 1.175,
            "Tc_uncertainty": 0.002,
            "Theta_D_K": 428,
            "type": "Type-I",
            "lambda_ep": 0.43,  # Electron-phonon coupling
            "mu_star": 0.10,  # Coulomb pseudopotential
            "source": "McMillan 1968",
        },
        {
            "name": "Mercury (Hg)",
            "Tc_K": 4.15,
            "Tc_uncertainty": 0.01,
            "Theta_D_K": 72,
            "type": "Type-I",
            "lambda_ep": 1.6,
            "mu_star": 0.10,
            "source": "Onnes 1911 / Kittel",
        },
        {
            "name": "Lead (Pb)",
            "Tc_K": 7.19,
            "Tc_uncertainty": 0.02,
            "Theta_D_K": 105,
            "type": "Type-I",
            "lambda_ep": 1.55,
            "mu_star": 0.12,
            "source": "MIT Junior Lab",
        },
        {
            "name": "Vanadium (V)",
            "Tc_K": 5.36,
            "Tc_uncertainty": 0.13,
            "Theta_D_K": 380,
            "type": "Type-II",
            "lambda_ep": 0.80,
            "mu_star": 0.11,
            "source": "MIT Junior Lab",
        },
        {
            "name": "Niobium (Nb)",
            "Tc_K": 9.25,
            "Tc_uncertainty": 0.02,
            "Theta_D_K": 275,
            "type": "Type-II",
            "lambda_ep": 1.04,
            "mu_star": 0.12,
            "source": "Kittel / MIT",
        },
        {
            "name": "Tin (Sn)",
            "Tc_K": 3.72,
            "Tc_uncertainty": 0.01,
            "Theta_D_K": 200,
            "type": "Type-I",
            "lambda_ep": 0.72,
            "mu_star": 0.10,
            "source": "Kittel",
        },
        {
            "name": "Indium (In)",
            "Tc_K": 3.41,
            "Tc_uncertainty": 0.01,
            "Theta_D_K": 112,
            "type": "Type-I",
            "lambda_ep": 0.81,
            "mu_star": 0.10,
            "source": "Kittel",
        },
        # ======= A15 Compounds =======
        {
            "name": "Nb3Sn",
            "Tc_K": 18.3,
            "Tc_uncertainty": 0.2,
            "Theta_D_K": 280,
            "type": "A15",
            "lambda_ep": 1.8,
            "mu_star": 0.13,
            "source": "Matthias 1954",
        },
        {
            "name": "Nb3Ge",
            "Tc_K": 23.2,
            "Tc_uncertainty": 0.3,
            "Theta_D_K": 300,
            "type": "A15",
            "lambda_ep": 2.1,
            "mu_star": 0.13,
            "source": "Gavaler 1973",
        },
        # ======= MgB2 (Two-Gap) =======
        {
            "name": "MgB2",
            "Tc_K": 39.0,
            "Tc_uncertainty": 0.5,
            "Theta_D_K": 800,
            "type": "Two-Gap",
            "lambda_ep": 0.87,  # Weighted average
            "mu_star": 0.10,
            "source": "Nagamatsu 2001 Nature",
        },
        # ======= HIGH-Tc CUPRATES (Non-BCS) =======
        {
            "name": "YBCO (YBa2Cu3O7)",
            "Tc_K": 92.0,
            "Tc_uncertainty": 2.0,
            "Theta_D_K": 400,
            "type": "High-Tc Cuprate",
            "lambda_ep": None,  # Not applicable - different mechanism
            "mu_star": None,
            "source": "Wu 1987 PRL",
            "note": "Non-BCS mechanism",
        },
        {
            "name": "BSCCO-2223",
            "Tc_K": 110.0,
            "Tc_uncertainty": 2.0,
            "Theta_D_K": 400,
            "type": "High-Tc Cuprate",
            "lambda_ep": None,
            "mu_star": None,
            "source": "Maeda 1988",
            "note": "Non-BCS mechanism",
        },
    ],
    "formulas": {
        "BCS_weak_coupling": "Tc = 1.13 * Theta_D * exp(-1/λ)",
        "McMillan_1968": "Tc = (Theta_D/1.45) * exp(-1.04*(1+λ)/(λ-μ*(1+0.62*λ)))",
        "Allen_Dynes": "Tc = (f1*f2*ω_log/1.2) * exp(-1.04*(1+λ)/(λ-μ*(1+0.62*λ)))",
        "UET_extension": "Pending - need Information field coupling",
    },
}


def save_data(output_dir="docs/data/03_condensed_matter"):
    """Save real superconductor data to JSON."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_path = Path(output_dir) / "real_superconductor_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(SUPERCONDUCTOR_DATA, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved: {output_path}")
    print(f"   {len(SUPERCONDUCTOR_DATA['superconductors'])} superconductors")
    return output_path


def mcmillan_tc(theta_D, lambda_ep, mu_star=0.10):
    """
    McMillan equation for critical temperature.

    Tc = (Theta_D / 1.45) * exp(-1.04(1+λ) / (λ - μ*(1+0.62λ)))

    Valid for: λ < 1.5 (weak to intermediate coupling)
    """
    import numpy as np

    if lambda_ep is None or lambda_ep <= mu_star * (1 + 0.62 * lambda_ep):
        return None  # Not applicable

    exponent = -1.04 * (1 + lambda_ep) / (lambda_ep - mu_star * (1 + 0.62 * lambda_ep))
    return (theta_D / 1.45) * np.exp(exponent)


def test_mcmillan():
    """Test McMillan equation against real data."""
    import numpy as np

    print("=" * 70)
    print("🔬 McMillan Equation Test (Real Data)")
    print("=" * 70)

    results = []
    for sc in SUPERCONDUCTOR_DATA["superconductors"]:
        if sc.get("lambda_ep") is None:
            continue

        tc_pred = mcmillan_tc(sc["Theta_D_K"], sc["lambda_ep"], sc.get("mu_star", 0.10))
        if tc_pred is None:
            continue

        tc_obs = sc["Tc_K"]
        error = abs(tc_pred - tc_obs) / tc_obs * 100
        status = "✅" if error < 20 else "⚠️"

        print(
            f"{sc['name']:20} | Tc_obs={tc_obs:6.2f}K | Tc_McM={tc_pred:6.2f}K | λ={sc['lambda_ep']:.2f} | Err={error:5.1f}% {status}"
        )
        results.append(error)

    avg_err = np.mean(results)
    print("-" * 70)
    print(f"Average Error: {avg_err:.1f}%")
    return avg_err


if __name__ == "__main__":
    # Save data
    save_data()

    # Test McMillan
    print()
    test_mcmillan()
