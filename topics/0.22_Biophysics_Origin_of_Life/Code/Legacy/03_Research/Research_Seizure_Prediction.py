"""
Engine: UET Neural Dynamics
============================
Topic: 0.22_Neural_Dynamics
Folder: 01_Engine

Core UET neural simulation using information-energy framework.
Uses core UET framework - NO PARAMETER FITTING.

Core Concept: Brain as C-I field system
  C = Excitatory activity (EEG signal)
  I = Inhibitory state (hidden)
  Ω = Neural disequilibrium (brain state)
  𝒱 = -ΔΩ = Value (learning/adaptation)

Real Data Reference: CHB-MIT Scalp EEG Database
DOI: 10.13026/C2K01R
"""

import sys
import numpy as np
from pathlib import Path
from docs import ROOT_PATH

root_path = ROOT_PATH


# --- ROBUST PATH FINDER ---


# Setup local imports for Topic 0.22
topic_path = root_path / "docs" / "topics" / "0.22_Biophysics_Origin_of_Life"
engine_path = topic_path / "Code" / "01_Engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

try:
    from Engine_Biophysics import UETBiophysicsEngine
except ImportError as e:
    print(f"CRITICAL SETUP ERROR: {e}")
    sys.exit(1)


# Standardized UET Root Path


def run_research():
    """
    Test UET neural dynamics simulation (Pure Problem).
    """
    print("=" * 70)
    print("🧪 RESEARCH: UET Neural Dynamics (Seizure Prediction)")
    print("    Delegating to Engine_Biophysics (Zero Shadow Math)")
    print("=" * 70)

    # 1. Instantiate the Engine (The Solver)
    engine = UETBiophysicsEngine()

    print("\n[1] BRAIN STATE → Ω MAPPING")
    print("-" * 50)

    states = ["normal", "seizure", "sleep"]
    results = {}

    for state in states:
        # Engine handles simulation and Omega calculation
        signal = engine.simulate_eeg_signal(1.0, 256, state)
        omega = engine.compute_neural_omega(signal)
        results[state] = omega

    print(f"| {'State':<12} | {'Ω (UET)':<12} | Interpretation |")
    print("-" * 50)

    for state, omega in results.items():
        interp = (
            "Desynchronized"
            if state == "normal"
            else "Hypersynchronous" if state == "seizure" else "Slow Wave"
        )
        print(f"| {state:<12} | {omega:>10.4f} | {interp} |")

    print("-" * 50)

    omega_normal = results["normal"]
    omega_seizure = results["seizure"]

    if omega_seizure < omega_normal:
        print("\n✅ INTEGRITY VERIFIED: Seizure has LOWER Ω (Hypersynchrony detected)")
    else:
        print("\n❌ INTEGRITY FAIL: Engine logic inconsistent")

    print("=" * 70)
    return omega_seizure < omega_normal


if __name__ == "__main__":
    success = run_research()
    sys.exit(0 if success else 1)
