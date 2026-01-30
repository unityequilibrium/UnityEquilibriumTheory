import numpy as np
import os
import sys
from pathlib import Path

# --- UET CORE SETUP ---
current_path = Path(__file__).resolve()
# Go up 3 levels to pkg_root (Code -> 0.27 -> topics -> research_uet)
# Actually, path is topics/0.27/Code/01_Engine/file
# So parents[0] = 01_Engine
# parents[1] = Code
# parents[2] = 0.27...
# parents[3] = topics
# parents[4] = research_uet
# We generally want 'research_uet' or the root containing it to be in path.
# Let's try adding the project root.

project_root = current_path.parents[5]  # Adjust based on actual depth
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class ColdLightEngine:
    def __init__(self):
        self.c = 3e8  # Speed of light
        self.h_bar = 1.054e-34
        self.lattice_constant = 0.142e-9  # Graphene C-C bond length (nm)

        # UET Resonance Factor (Geometry)
        # Resonance occurs when Wavelength = Lattice_Perimeter / Integer
        # Hexagon Perimeter = 6 * a
        self.resonance_lambda = 6 * self.lattice_constant

    def simulate_photon_interaction(self, input_wavelength_nm, transparency_mode=False):
        """
        Simulates a photon interacting with the Graphene Lattice.
        Returns: Final Velocity, Trapped State (Bool), Entropy Gen
        """
        wavelength = input_wavelength_nm * 1e-9

        # 1. Geometric Mismatch Calculation
        # How far is the photon from the "Locking Key" size at resonance harmonic?
        # We check primarily the first harmonic (n=1)
        mismatch = abs(wavelength - self.resonance_lambda) / self.resonance_lambda

        # 2. Trap Probability (Lorentzian Resonance Profile)
        # The closer the mismatch is to 0, the higher the trap probability.
        # "Q-Factor" of Graphene is extremely high (simulated as 5000)
        q_factor = 5000.0
        trap_prob = 1.0 / (1.0 + (q_factor * mismatch) ** 2)

        # 3. Dynamic State Evolution
        if trap_prob > 0.95 and not transparency_mode:
            # LOCKED STATE (Cold Light)
            velocity = 0.0
            is_trapped = True
            entropy_gen = 0.0  # Ordered rotation (Standing Wave)
            state_desc = "LOCKED (Ring Current)"
        elif trap_prob > 0.1:
            # PARTIAL INTERACTION (Slowing/Refraction)
            velocity = self.c * (1.0 - trap_prob)
            is_trapped = False
            entropy_gen = 0.1 * trap_prob  # Some scattering heat
            state_desc = "SLOWED / SCATTERED"
        else:
            # PASS THROUGH (Transparent)
            velocity = self.c
            is_trapped = False
            entropy_gen = 0.0
            state_desc = "TRANSPARENT"

        return {
            "wavelength_nm": input_wavelength_nm,
            "resonance_target_nm": self.resonance_lambda * 1e9,
            "mismatch_pct": mismatch * 100,
            "trap_probability": trap_prob,
            "final_velocity": velocity,
            "is_trapped": is_trapped,
            "entropy_generated": entropy_gen,
            "state_desc": state_desc,
        }

    def run_sweep(self):
        print("💡 ENGINE: Cold Light Resonance Sweep")
        print("=====================================")
        print(f"Target Lattice: Graphene (a = {self.lattice_constant*1e9:.3f} nm)")
        print(f"Resonance Wavelength (6a): {self.resonance_lambda*1e9:.3f} nm (Target)")
        print("-------------------------------------")

        # Sweep wavelengths around resonance
        center = self.resonance_lambda * 1e9
        test_lambdas = np.linspace(center - 0.5, center + 0.5, 11)

        results = []
        for l in test_lambdas:
            res = self.simulate_photon_interaction(l)
            results.append(res)

            # Visual Bar
            vel_bar = "#" * int(res["final_velocity"] / 3e7)  # Scale for display
            status_icon = "❄️" if res["is_trapped"] else "⚡"

            print(
                f"λ = {l:.3f} nm | {status_icon} {res['state_desc']:<20} | Vel: {res['final_velocity']:.1e} | S: {res['entropy_generated']:.4f}"
            )

        return results


if __name__ == "__main__":
    engine = ColdLightEngine()
    engine.run_sweep()
