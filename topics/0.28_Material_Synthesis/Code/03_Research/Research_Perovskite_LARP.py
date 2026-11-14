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


from docs.core.uet_parameters import get_params, K_B
from docs.core.uet_glass_box import UETPathManager, UETMetricLogger


class PerovskiteLARPSimulator:
    """
    Simulates the Ligand-Assisted Reprecipitation (LARP) synthesis of Perovskite Nanocrystals.
    Applies UET Resonant Guidance to reduce defect density.
    """

    def __init__(self):
        self.params = get_params("0.28")
        self.k_b = K_B
        self.room_temp = 300  # Kelvin
        # Energy barrier for crystal nucleation (approx.)
        self.nucleation_barrier_eV = 0.5
        # Target: MAPbBr3 (Green emitter, common in Thai labs like Mahidol)
        self.target_material = "MAPbBr3"

    def simulate_synthesis(self, use_resonance=True, temp_kelvin=300):
        """
        Simulates defect rate based on thermal noise vs. resonance guidance.
        """
        thermal_energy = self.k_b * temp_kelvin
        # Convert eV to Joules for comparison
        barrier_joules = self.nucleation_barrier_eV * 1.602e-19

        # Base defect rate (Boltzmann probability of "wrong" position)
        # Higher thermal energy = higher chance of defects
        base_defect_rate = np.exp(-barrier_joules / thermal_energy)

        if use_resonance:
            # UET Resonance Guidance reduces effective thermal noise
            # Signal/Noise improvement factor (from Topic 0.28 Graphene research)
            snr_boost = 3.0  # Equivalent to lowering "effective temp" by 3x
            effective_temp = temp_kelvin / snr_boost
            effective_thermal = self.k_b * effective_temp
            resonance_defect_rate = np.exp(-barrier_joules / effective_thermal)
            method = "Resonant LARP (UET)"
        else:
            resonance_defect_rate = base_defect_rate
            method = "Standard LARP"

        # Purity = 1 - Defect Rate
        purity = (1 - resonance_defect_rate) * 100

        return {
            "method": method,
            "material": self.target_material,
            "temperature_K": temp_kelvin,
            "base_defect_rate_pct": base_defect_rate * 100,
            "final_defect_rate_pct": resonance_defect_rate * 100,
            "purity_pct": purity,
            "conclusion": (
                "Resonance Guidance reduces defects significantly."
                if use_resonance
                else "Standard process, higher defects."
            ),
        }

    def run_comparison(self):
        print("\n🔬 RESEARCH: Perovskite LARP Synthesis Comparison")
        print("=================================================")
        print(f"Target Material: {self.target_material}")
        print(f"Room Temperature: {self.room_temp} K")
        print("-" * 50)

        # 1. Standard LARP
        std = self.simulate_synthesis(use_resonance=False)
        print(f"1. [METHOD]: {std['method']}")
        print(f"   [DEFECT RATE]: {std['final_defect_rate_pct']:.6f}%")
        print(f"   [PURITY]: {std['purity_pct']:.4f}%")
        print("-" * 30)

        # 2. Resonant LARP (UET)
        res = self.simulate_synthesis(use_resonance=True)
        print(f"2. [METHOD]: {res['method']}")
        print(f"   [DEFECT RATE]: {res['final_defect_rate_pct']:.10f}%")
        print(f"   [PURITY]: {res['purity_pct']:.6f}%")
        print(f"   [CONCLUSION]: {res['conclusion']}")

        # Improvement Factor
        improvement = std["final_defect_rate_pct"] / res["final_defect_rate_pct"]
        print(f"\n✅ UET Resonance Improvement: Defects reduced by {improvement:.0f}x")

        return [std, res]


if __name__ == "__main__":
    sim = PerovskiteLARPSimulator()
    results = sim.run_comparison()

    # Save to Results
    import json

    logger = UETMetricLogger("Perovskite_LARP", topic_id="0.28", category="log")
    res_dir = logger.run_dir
    with open(res_dir / "synthesis_log.json", "w") as f:
        json.dump(results, f, indent=4)
    print(f"\n💾 RESULTS SAVED: {res_dir}/synthesis_log.json")
