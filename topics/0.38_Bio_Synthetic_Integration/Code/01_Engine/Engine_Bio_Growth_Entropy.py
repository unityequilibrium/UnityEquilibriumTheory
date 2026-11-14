import numpy as np
import json
import os

class BioGrowthEngine:
    """
    Simulation of Bio-Synthetic Material integrity over time.
    Compares Closed-System (Metal) vs Open-System (Bone) dynamics.
    """
    
    def __init__(self):
        # Time parameters (Years)
        self.time_span = 50
        self.steps = 500
        self.t = np.linspace(0, self.time_span, self.steps)
        
    def simulate_legacy_decay(self, initial_integrity=1.0, decay_rate=0.03):
        """
        Closed System Model: Entropy always increases, integrity decreases.
        S(t) = S0 * e^(-kt)
        """
        # Linear + Exponential decay (Fatigue + Corrosion)
        decay = initial_integrity * np.exp(-decay_rate * self.t)
        return decay

    def simulate_bio_growth(self, initial_integrity=0.1, max_integrity=1.0, metabolic_rate=0.15):
        """
        Open System Model: Metabolic Energy maintains order.
        Logistic growth + homeostatic repair.
        """
        # Integrity climbs to a stable plateau and stays there via repair
        # Logistic Differential Equation: dI/dt = r*I*(1 - I/K)
        # Simplified closed-form for step-wise simulation
        integrity = []
        current_i = initial_integrity
        
        for _ in self.t:
            # Growth/Repair term
            growth = metabolic_rate * current_i * (1 - current_i / max_integrity)
            # Natural wear term (Entropy)
            wear = 0.02 * current_i
            
            current_i += (growth - wear)
            integrity.append(current_i)
            
        return np.array(integrity)

    def run_simulation(self):
        print("UET Research: Topic 0.38 - Bio-Synthetic Growth Engine")
        print("=" * 60)
        
        # 1. Legacy Metal Chassis (Dead Material)
        metal_integrity = self.simulate_legacy_decay()
        
        # 2. Bio-Synthetic Bone Chassis (Living Material)
        bone_integrity = self.simulate_bio_growth()
        
        # Calculate Reliability at T=30 years
        idx_30 = int(30 / self.time_span * self.steps)
        metal_30 = metal_integrity[idx_30]
        bone_30 = bone_integrity[idx_30]
        
        print(f"\n[INTEGRITY REPORT @ YEAR 30]")
        print(f"Legacy Metal Chassis: {metal_30:.2%} (Needs Replacement)")
        print(f"Bio-Synthetic Bone  : {bone_30:.2%} (Self-Maintained)")
        
        results = {
            "time_years": list(self.t),
            "metal_chassis": list(metal_integrity),
            "bone_chassis": list(bone_integrity),
            "summary": {
                "year_30_metal": metal_30,
                "year_30_bone": bone_30,
                "advantage_multiplier": bone_30 / metal_30
            }
        }
        
        # Verification Logic
        if results["summary"]["advantage_multiplier"] > 2.0:
            print(f"\nPASS: Bio-Synthetic structural advantage confirmed (>2x life).")
        else:
            print("\nFAIL: Metabolic repair rates insufficient.")

        # Save results
        output_dir = "docs/topics/0.38_Bio_Synthetic_Integration/Result"
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "bio_growth_comparison.json"), "w") as f:
            json.dump(results, f, indent=4)
            
        return results

if __name__ == "__main__":
    engine = BioGrowthEngine()
    engine.run_simulation()
