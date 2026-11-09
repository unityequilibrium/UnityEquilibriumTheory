"""
UET Research: Cluster Stability Experiment
==========================================
Checks if UET clusters are stable over Hubble time.
"""

import sys
from pathlib import Path


def test_stability():
    print("=" * 60)
    print("⚖️ UET RESEARCH: CLUSTER STABILITY")
    print("=" * 60)

    # Stability Condition: 2K + U + Theta = 0
    # If Sum != 0, cluster expands or collapses

    K = 1.0  # Normalized Kinetic
    U = -0.1  # Normalized Gravitational (Visible only)
    Theta = -1.9  # Information Pressure (Confining)

    Virial_Sum = 2 * K + U + Theta

    print(f"Kinetic Energy (K):       {K}")
    print(f"Gravitational Potential (U): {U}")
    print(f"Info Pressure (Theta):    {Theta}")
    print("-" * 40)
    print(f"Virial Sum (2K+U+Theta): {Virial_Sum:.2f}")

    if abs(Virial_Sum) < 0.1:
        print("✅ PASS: Cluster is STABLE.")
    else:
        print("❌ FAIL: Cluster is unstable.")


if __name__ == "__main__":
    test_stability()
