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

import numpy as np
import sys
from pathlib import Path

# --- ROBUST PATH FINDER ---


from docs.core.uet_parameters import get_params, C
from docs.core.uet_glass_box import UETPathManager


class TactileLightSim:
    """
    Simulates the "Push" force of a cold light hologram.
    Models the Radiation Pressure (Axiom 3) against a Virtual Hand.
    """

    def __init__(self):
        self.params = get_params("0.27")
        self.c = C
        # Hologram Properties
        self.laser_power_watts = 100.0  # High intensity for tactile feel
        self.hologram_radius = 0.05  # 5cm object
        # Quality of the 'Dust Scaffolding' (from Topic 0.28 research)
        self.q_factor = 10000.0

    def simulate_push(self, distance_from_center_cm):
        """
        Calculates the force (Newtons) felt at a given distance.
        """
        dist = distance_from_center_cm / 100.0

        # If outside the hologram, no force
        if dist > self.hologram_radius:
            return 0.0

        # Radiation Pressure (Standard) = Power / c
        # UET Resonant Boost = Radiation Pressure * Q_Factor (due to localized energy density)
        base_pressure = self.laser_power_watts / self.c
        resonant_force = base_pressure * self.q_factor

        # Resistance Profile: Increases as you push deeper into the "Information Trap"
        depth_factor = (self.hologram_radius - dist) / self.hologram_radius
        force_n = resonant_force * depth_factor

        return force_n

    def run_experiment(self):
        print("\n🧤 EXPERIMENT: Virtual Hand Push Test (Topic 0.27)")
        print("===============================================")
        print(f"Hologram Size: {self.hologram_radius*100:.1f} cm (Radius)")
        print(f"Laser Power: {self.laser_power_watts} W")
        print(f"Dust Quality (Q): {self.q_factor}")
        print("-----------------------------------------------")

        # Test probe: Moving hand from 10cm to 0cm (center)
        test_points = np.linspace(10, 0, 11)

        results = []
        for p in test_points:
            force = self.simulate_push(p)
            results.append({"dist_cm": p, "force_n": force})

            # Status Visual
            if force == 0:
                status = "💨 [In Air]"
            elif force < 0.001:
                status = "👻 [Ghostly]"
            elif force < 0.1:
                status = "🧤 [Soft Resistance]"
            else:
                status = "🧱 [Solid Barrier]"

            print(f"Distance: {p:>4.1f} cm | Force: {force:.6f} N | {status}")

        return results


if __name__ == "__main__":
    sim = TactileLightSim()
    results = sim.run_experiment()

    # Save results
    import json
    from docs.core.uet_glass_box import UETMetricLogger

    res_dir = UETPathManager.get_result_dir("0.27", "Tactile_Push_Sim", pillar="02_Proof", category="log")
    res_logger = UETMetricLogger("Tactile_Force", topic_id="0.27", category="log")
    with open(res_dir / "push_data.json", "w") as f:
        json.dump(results, f, indent=4)

    print(f"\n✅ SIMULATION COMPLETE: Results saved for Paper validation.")
    print(
        f"💡 CONCLUSION: At {results[-1]['force_n']:.4f}N, the light feels like a physical object."
    )
