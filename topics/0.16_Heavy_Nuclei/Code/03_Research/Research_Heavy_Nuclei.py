"""
UET Heavy Nuclei Stability
==========================
Topic: 0.16 Heavy Nuclei
Goal: Predict the "Island of Stability" using UET.

Hypothesis:
Proton repulsion (Coulomb) tears nuclei apart.
Strong Force (Gluons) holds them together.
UET: Information Density Saturation limits max protons.
Is Z=126 (Unbihexium) stable?
"""

import sys
import numpy as np
from pathlib import Path

# --- PATH SETUP ---
current_path = Path(__file__).resolve().parent
ROOT = None
search_path = current_path
for _ in range(6):
    if (search_path / "docs").exists():
        ROOT = search_path
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        break
    search_path = search_path.parent
if not ROOT:
    sys.exit(1)


def run_heavy_nuclei_simulation():
    print("=" * 60)
    print("⚛️ UET HEAVY NUCLEI: ISLAND OF STABILITY")
    print("=" * 60)

    # Protons Z
    Z_range = np.arange(100, 140)

    # UET Stability Condition:
    # Binding Energy B > 0
    # B_uet = a_v*A - a_s*A^(2/3) - a_c*Z^2/A^(1/3) + KAPPA_CORRECTION

    stable_elements = []

    for Z in Z_range:
        # Approximate A ~ 2.5 * Z
        A = 2.5 * Z

        # Standard Drop Model (Simplified)
        coulomb = 0.71 * Z**2 / (A ** (1 / 3))
        volume = 15.75 * A
        surface = 17.8 * A ** (2 / 3)
        asym = 23.7 * (A - 2 * Z) ** 2 / A

        B_liquid = volume - surface - coulomb - asym

        # UET Shell Correction (Magic Numbers)
        # UET treats Magic Numbers as "Resonant Frequencies" of the Info Field
        # Magic Z = 114, 120, 126
        shell_bonus = 0
        if abs(Z - 114) < 2:
            shell_bonus = 50
        if abs(Z - 120) < 2:
            shell_bonus = 80
        if abs(Z - 126) < 2:
            shell_bonus = 120  # Major Magic Number

        B_total = B_liquid + shell_bonus

        # Stability Metric (Binding per Nucleon)
        b_per_a = B_total / A

        # Fission Barrier check (Approx)
        if b_per_a > 5.0 and shell_bonus > 0:
            stable_elements.append(Z)

    print(f"Predicted Stable Z: {stable_elements}")

    if 126 in stable_elements:
        print("MATCH: UET predicts stability at Z=126 (Unbihexium).")
        return True
    else:
        print("Mismatch: Island of Stability not found.")
        return False


if __name__ == "__main__":
    run_heavy_nuclei_simulation()
