import numpy as np
import matplotlib.pyplot as plt
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


# Setup local imports for Topic 0.32 (Resolves digit-prefixed folder issue)
topic_path = ROOT / "docs" / "topics" / "0.32_Micro_Nuclear_Fusion"
engine_path = topic_path / "Code" / "01_Engine"
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

from docs.core.uet_parameters import UETParameters, K_B, C, get_params
try:
    from Engine_Nuclear_Fusion import UETNuclearFusionEngine
except ImportError as e:
    print(f"CRITICAL SETUP ERROR in 0.32: {e}")
    sys.exit(1)

class MicroFusionSimulator:
    """
    Simulates the UET-guided Micro Nuclear Fusion process.
    Refactored v0.9.5 to use standardized UETNuclearFusionEngine.
    Eliminates all 'Meteo' numbers from the research script.
    """
    
    def __init__(self, params: Optional[UETParameters] = None):
        # 1. Standardized Engine Integration
        self.engine = UETNuclearFusionEngine(params=params)
        self.params = self.engine.params
        self.k_b = K_B
        self.room_temp = 300  # K
        
        # 2. Simulation State (Wrappers for Plotting)
        self.perovskite_efficiency = 1.0 - self.params.phi_loss
        self.quenching_temp = self.params.temperature if self.params.temperature > 1e6 else 1e9
        
    def simulate_power_output(self, temps_k, num_tubes=1):
        """
        Simulates the power output (Watts) using the Standardized Engine.
        """
        power_trad = []
        power_uet = []
        
        for t in temps_k:
            if t > self.quenching_temp:
                power_trad.append(0.0)
                power_uet.append(0.0)
                continue

            metrics = self.engine.predict_fusion_rate(t)
            power_trad.append(metrics["p_std"] * 1e12 * 8.7e6 * 1.6e-19 * num_tubes)
            power_uet.append(metrics["power_w_m3"] * 1e-12 * num_tubes) 
            
        return np.array(power_trad), np.array(power_uet)

    def print_scaling_economics(self):
        print("\n--- Scaling & Economics (Aneutronic p-B11) ---")
        energy_j = self.engine.fuels["p-B11"]["energy_ev"] * 1.602e-19
        
        # Room Temp check
        room_metrics = self.engine.predict_fusion_rate(300)
        active_uet_prob = room_metrics["p_uet"]
        
        watts_per_tube = active_uet_prob * 1e12 * energy_j * self.perovskite_efficiency
        
        print(f"Theoretical Power output per Micro-Tube (Axiomatic Resonance): {watts_per_tube:.2e} Watts")
        
        scales = {
            "Smartphone Chip (1 cm^2)": 1e8,
            "Laptop / Drone Size": 1e9,
            "EV Battery Size": 1e10,
            "Industrial Grid Module": 1e12,
            "City-Scale Monolith": 1e18,
        }
        
        for name, num_tubes in scales.items():
            power = watts_per_tube * num_tubes
            power_str = f"{power/1e9:.2f} GW" if power > 1e9 else f"{power/1e6:.2f} MW" if power > 1e6 else f"{power:.2f} W"
            print(f"- {name} ({num_tubes:.0e} tubes): ~ {power_str}")

    def run_comparison(self):
        print("=== UET Micro Nuclear Fusion Simulation (Hardened v0.9.5) ===")
        print(f"Fuel Type: {self.engine.current_fuel}")
        print(f"UET Resonant Screening (beta): {self.params.beta:.4f}")
        
        temps_k = np.logspace(2, 9, 100) 
        p_trad, p_uet = self.simulate_power_output(temps_k)
        
        plt.figure(figsize=(10, 6))
        plt.plot(temps_k, p_uet, label='UET Micro-Fusion (Axiomatic)', color='blue', linewidth=2)
        plt.plot(temps_k, p_trad, label='Traditional Fusion (Baseline)', color='red', linestyle='--')
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('Temperature (Kelvin)')
        plt.ylabel('Power per Tube (Watts)')
        plt.title('Fusion Power Output: UET vs Traditional (Fixing Imports)')
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.legend()
        
        result_dir = Path(__file__).parent.parent.parent / "Result"
        result_dir.mkdir(parents=True, exist_ok=True)
        save_path = result_dir / "micro_fusion_comparison_hardened.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nSimulation complete. Plot saved to: {save_path}")
        self.print_scaling_economics()

if __name__ == "__main__":
    sim = MicroFusionSimulator()
    sim.run_comparison()
