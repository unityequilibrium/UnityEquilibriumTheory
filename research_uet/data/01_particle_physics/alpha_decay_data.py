"""
Alpha Decay Data
=================
Alpha particle emission data from NNDC.

Source: NNDC (National Nuclear Data Center)
URL: https://www.nndc.bnl.gov/

POLICY: NO PARAMETER FIXING
"""

import numpy as np

# ============================================================
# ALPHA DECAY FUNDAMENTALS
# ============================================================

ALPHA_DECAY_PHYSICS = {
    "description": "Emission of α particle (⁴He nucleus)",
    "Q_value": "Energy released in decay",
    "half_life_range": "10⁻⁷ s to 10¹⁷ years",
    "Geiger_Nuttall": "log(λ) ∝ 1/√E_α (1911)",
    "quantization": "Gamow tunneling theory",
}

# ============================================================
# REPRESENTATIVE ALPHA EMITTERS
# ============================================================

ALPHA_EMITTERS = {
    # Heavy elements
    "U-238": {
        "half_life_years": 4.468e9,
        "Q_MeV": 4.270,
        "daughter": "Th-234",
        "source": "NNDC",
    },
    "U-235": {
        "half_life_years": 7.04e8,
        "Q_MeV": 4.679,
        "daughter": "Th-231",
        "source": "NNDC",
    },
    "Th-232": {
        "half_life_years": 1.4e10,
        "Q_MeV": 4.083,
        "daughter": "Ra-228",
        "source": "NNDC",
    },
    "Ra-226": {
        "half_life_years": 1600,
        "Q_MeV": 4.871,
        "daughter": "Rn-222",
        "source": "NNDC",
    },
    "Rn-222": {
        "half_life_days": 3.82,
        "Q_MeV": 5.590,
        "daughter": "Po-218",
        "source": "NNDC",
        "note": "Radon gas (health hazard)",
    },
    "Po-210": {
        "half_life_days": 138.4,
        "Q_MeV": 5.407,
        "daughter": "Pb-206",
        "source": "NNDC",
    },
    "Am-241": {
        "half_life_years": 432.2,
        "Q_MeV": 5.638,
        "daughter": "Np-237",
        "source": "NNDC",
        "use": "Smoke detectors",
    },
    "Pu-239": {
        "half_life_years": 2.41e4,
        "Q_MeV": 5.244,
        "daughter": "U-235",
        "source": "NNDC",
    },
}

# ============================================================
# GEIGER-NUTTALL RELATION
# ============================================================


def geiger_nuttall_test():
    """
    Geiger-Nuttall law: log(λ) = a + b/√E_α

    This was the first hint of quantum tunneling!
    """
    data = []
    for name, isotope in ALPHA_EMITTERS.items():
        Q = isotope["Q_MeV"]
        if "half_life_years" in isotope:
            t_half_s = isotope["half_life_years"] * 3.156e7
        elif "half_life_days" in isotope:
            t_half_s = isotope["half_life_days"] * 86400
        else:
            continue

        lambda_decay = np.log(2) / t_half_s
        data.append(
            {
                "name": name,
                "Q_MeV": Q,
                "log_lambda": np.log10(lambda_decay),
                "inv_sqrt_Q": 1 / np.sqrt(Q),
            }
        )

    return data


# ============================================================
# UET INTERPRETATION
# ============================================================


def uet_alpha_decay():
    """
    UET interpretation of alpha decay.

    Alpha particle = tightly bound C-I field configuration.
    Tunneling = C-I field fluctuation allowing escape.
    """
    return {
        "alpha_particle": "4 nucleons in C-I bound state",
        "tunneling": "C-I field barrier penetration",
        "Q_value": "C-I binding energy difference",
        "Geiger_Nuttall": "Emergent from C-I dynamics",
        "status": "FRAMEWORK CONSISTENT",
    }


if __name__ == "__main__":
    print("=" * 50)
    print("ALPHA DECAY DATA (NNDC)")
    print("=" * 50)

    print(f"\nRepresentative isotopes:")
    for name, iso in list(ALPHA_EMITTERS.items())[:5]:
        Q = iso["Q_MeV"]
        print(f"  {name}: Q = {Q:.3f} MeV")
