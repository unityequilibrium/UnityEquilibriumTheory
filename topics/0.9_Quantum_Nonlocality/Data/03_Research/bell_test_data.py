"""
Bell Inequality Test Data
=========================
Historical and Modern Bell Test Experiments

References:
- Aspect et al. 1982, Phys. Rev. Lett.
- Hensen et al. 2015, Nature (Loophole-free)
- 2022 Nobel Prize in Physics

Updated for UET V3.0
"""

import sys
from pathlib import Path

# --- ROBUST UET BOOTSTRAP ---
def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None

ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)



# Import from UET V3.0 Master Equation
import sys
from pathlib import Path
_root = Path(__file__).parent
while _root.name != "docs" and _root.parent != _root:
    _root = _root.parent
sys.path.insert(0, str(_root.parent))
try:
    from docs.core.uet_master_equation import (
        UETParameters, SIGMA_CRIT, strategic_boost, potential_V, KAPPA_BEKENSTEIN
    )
except ImportError:
    pass  # Use local definitions if not available

import numpy as np

# ================================================================
# CHSH-BELL INEQUALITY
# ================================================================

BELL_INEQUALITY = {
    "CHSH_bound": {
        "classical_limit": 2.0,
        "quantum_maximum": 2 * np.sqrt(2),  # ≈ 2.828 (Tsirelson bound)
        "formula": "|S| ≤ 2 for local hidden variables",
        "quantum_formula": "S_max = 2√2 for quantum entanglement",
    },
}

# ================================================================
# ASPECT EXPERIMENTS (1981-1982)
# ================================================================

ASPECT_EXPERIMENTS = {
    "1981_first": {
        "authors": "Aspect, Grangier, Roger",
        "title": "Experimental Tests of Realistic Local Theories via Bell's Theorem",
        "journal": "Phys. Rev. Lett. 47, 460",
        "year": 1981,
        "S_value": None,  # First test, different metric
        "result": "First violation observed",
    },
    "1982_switching": {
        "authors": "Aspect, Dalibard, Roger",
        "title": "Experimental Realization of EPR Gedankenexperiment",
        "journal": "Phys. Rev. Lett. 49, 1804",
        "year": 1982,
        "S_value": 2.697,
        "S_uncertainty": 0.015,
        "QM_prediction": 2.70,
        "QM_uncertainty": 0.05,
        "sigma_violation": 46,  # Standard deviations above 2
        "innovation": "Fast-switching polarizers (closed locality loophole)",
        "loopholes": {
            "locality": "Closed (fast switching)",
            "detection": "Open (low efficiency)",
        },
    },
}

# ================================================================
# LOOPHOLE-FREE TESTS (2015)
# ================================================================

LOOPHOLE_FREE_TESTS = {
    "delft_2015": {
        "authors": "Hensen et al. (TU Delft)",
        "title": "Loophole-free Bell inequality violation",
        "journal": "Nature 526, 682",
        "year": 2015,
        "S_value": 2.42,
        "S_uncertainty": 0.20,
        "p_value": 0.039,
        "sigma_violation": 2.1,
        "method": "Entangled electron spins",
        "distance_km": 1.3,
        "loopholes": {
            "locality": "Closed (1.3 km separation)",
            "detection": "Closed (heralded scheme)",
            "freedom_of_choice": "Closed (random number generators)",
        },
        "note": "First fully loophole-free test",
    },
    "vienna_2015": {
        "authors": "Giustina et al. (Vienna)",
        "title": "Significant-loophole-free test of Bell's theorem",
        "journal": "Phys. Rev. Lett. 115, 250401",
        "year": 2015,
        "S_value": 2.35,
        "S_uncertainty": 0.09,
        "method": "Entangled photons",
        "loopholes": {
            "locality": "Closed",
            "detection": "Closed (high-efficiency detectors)",
        },
    },
    "nist_2015": {
        "authors": "Shalm et al. (NIST)",
        "title": "Strong loophole-free test of local realism",
        "journal": "Phys. Rev. Lett. 115, 250402",
        "year": 2015,
        "S_value": 2.373,
        "uncertainty": 0.014,
        "method": "Entangled photons",
        "p_value": 2.3e-7,
    },
}

# ================================================================
# RECENT EXPERIMENTS
# ================================================================

RECENT_EXPERIMENTS = {
    "big_bell_test_2018": {
        "title": "Challenging local realism with human choices",
        "journal": "Nature 557, 212",
        "year": 2018,
        "method": "100,000+ human random choices",
        "result": "Violations confirmed",
        "note": "Addressed freedom-of-choice loophole",
    },
    "cosmic_bell_2017": {
        "title": "Cosmic Bell Test with Random Measurement Settings",
        "journal": "Phys. Rev. Lett. 118, 060401",
        "year": 2017,
        "method": "Settings from distant quasars",
        "result": "8σ violation of local realism",
    },
}

# ================================================================
# 2022 NOBEL PRIZE
# ================================================================

NOBEL_PRIZE_2022 = {
    "laureates": ["Alain Aspect", "John Clauser", "Anton Zeilinger"],
    "reason": "For experiments with entangled photons, establishing the violation of Bell inequalities and pioneering quantum information science",
    "significance": "Confirmed quantum mechanics over local hidden variables",
}

# ================================================================
# SUMMARY TABLE
# ================================================================

SUMMARY = {
    "experiments": [
        {"name": "Aspect 1982", "S": 2.697, "err": 0.015, "sigma": 46, "loophole_free": False},
        {"name": "Delft 2015", "S": 2.42, "err": 0.20, "sigma": 2.1, "loophole_free": True},
        {"name": "Vienna 2015", "S": 2.35, "err": 0.09, "sigma": 3.9, "loophole_free": True},
        {"name": "NIST 2015", "S": 2.373, "err": 0.014, "sigma": 27, "loophole_free": True},
    ],
    "classical_limit": 2.0,
    "quantum_maximum": 2.828,
}

# ================================================================
# UET INTERPRETATION
# ================================================================

UET_INTERPRETATION = {
    "concept": "Entanglement as Information field correlation",
    "mechanism": """
        In UET framework:
        - Entangled particles share Information state
        - Bell violation = non-local I-field correlation
        - S > 2 because I-field is faster than light
        
        The I-field connects entangled particles instantaneously,
        but no information can be transmitted (no signaling).
        
        Quantum non-locality = I-field topology
    """,
    "prediction": """
        S_max = 2√2 reflects maximum I-field correlation.
        The Tsirelson bound is the I-field coherence limit.
        
        Decoherence = I-field thermalization with βCI
    """,
}


# ================================================================
# HELPER FUNCTIONS
# ================================================================


def bell_violation_sigma(S_measured, S_uncertainty, classical_limit=2.0):
    """Calculate significance of Bell violation."""
    return (S_measured - classical_limit) / S_uncertainty


def get_experiment(name="aspect_1982"):
    """Get experiment data."""
    if "aspect" in name.lower():
        return ASPECT_EXPERIMENTS["1982_switching"]
    elif "delft" in name.lower():
        return LOOPHOLE_FREE_TESTS["delft_2015"]
    else:
        return SUMMARY["experiments"]


if __name__ == "__main__":
    print("=" * 60)
    print("Bell Inequality Test Summary")
    print("=" * 60)

    print(f"\nClassical limit: S ≤ {BELL_INEQUALITY['CHSH_bound']['classical_limit']}")
    print(f"Quantum maximum: S ≤ {BELL_INEQUALITY['CHSH_bound']['quantum_maximum']:.3f}")

    print("\nKey Experiments:")
    for exp in SUMMARY["experiments"]:
        status = "✅ Loophole-free" if exp["loophole_free"] else "⚠️ Has loopholes"
        print(
            f"  {exp['name']}: S = {exp['S']:.3f} ± {exp['err']:.3f} ({exp['sigma']:.1f}σ) {status}"
        )

    print("\n🏆 Nobel Prize 2022:")
    for name in NOBEL_PRIZE_2022["laureates"]:
        print(f"  - {name}")
