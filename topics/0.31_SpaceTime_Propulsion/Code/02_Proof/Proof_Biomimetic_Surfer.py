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

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Path setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

engine_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../01_Engine"))
if engine_dir not in sys.path:
    sys.path.insert(0, engine_dir)

from Engine_Slingshot import SingularitySlingEngine
from docs.core.uet_parameters import C as LIGHT_SPEED

def run_biomimetic_surfer_proof():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    result_dir = os.path.abspath(os.path.join(script_dir, "../../Result/02_Proof"))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    log_file = os.path.join(result_dir, "0.31_Biomimetic_Shield_Audit.txt")
    
    def log_print(msg):
        print(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(str(msg) + "\n")

    with open(log_file, "w") as f:
        f.write(f"UET TOPIC 0.31: BIOMIMETIC SHIELD INTEGRITY AUDIT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

    log_print("🚀 [START] BIOMIMETIC HULL RESILIENCE TESTING (v2)")
    log_print("Extremophile Logic: Tardigrade-Inspired Self-Repair (Topic 0.22/0.30)")
    log_print("-" * 60)

    # 1. SCENARIO A: STANDARD GRAPHENE HULL (No Bio-Resilience)
    log_print("\n[SCENARIO A] Standard Graphene Hull (Resilience = 0.0)")
    engine_std = SingularitySlingEngine(initial_v=11000, bio_resilience=0.0) 
    
    results_std = engine_std.simulate_sling(1e14, 200.0, 1.0) # Standard pass
    
    v_std = [r['velocity'] for r in results_std]
    integrity_std = [r['bio_integrity'] for r in results_std]
    
    log_print(f"Final V: {engine_std.v:,.0f} m/s")
    log_print(f"Final Hull Integrity: {engine_std.bio_integrity:.2f}%")

    # 2. SCENARIO B: BIO-HYBRID HULL (Optimal Resilience)
    log_print("\n[SCENARIO B] Bio-Hybrid Hull (Resilience = 2.0)")
    engine_bio = SingularitySlingEngine(initial_v=11000, bio_resilience=2.0) 
    
    results_bio = engine_bio.simulate_sling(1e14, 200.0, 1.0)
    
    v_bio = [r['velocity'] for r in results_bio]
    integrity_bio = [r['bio_integrity'] for r in results_bio]
    
    log_print(f"Final V: {engine_bio.v:,.0f} m/s")
    log_print(f"Final Hull Integrity: {engine_bio.bio_integrity:.2f}%")

    # 3. VERDICT
    log_print("\n[FINAL VERDICT]")
    if engine_bio.bio_integrity > 0.0 and engine_std.bio_integrity <= 0.0:
        log_print("✅ BIOMIMETIC SUPERIORITY CONFIRMED: Bio-Hybrid survived where Standard Hull dissolved.")
    elif engine_bio.bio_integrity > engine_std.bio_integrity:
        log_print("✅ BIOMIMETIC ADVANTAGE: Resilience significantly delayed structural dissolution.")
    else:
        log_print("⚠️ TEST INCONCLUSIVE.")

    # Plotting
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot([r['time'] for r in results_std], integrity_std, 'r--', label='Standard Hull')
    plt.plot([r['time'] for r in results_bio], integrity_bio, 'g-', label='Bio-Hybrid Hull')
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.title("Structural Integrity (Non-Enropy Matter Stability)")
    plt.xlabel("Time (s)")
    plt.ylabel("Integrity (%)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    plt.plot([r['time'] for r in results_std], [v/LIGHT_SPEED*100 for v in v_std], 'r--', label='Standard Hull')
    plt.plot([r['time'] for r in results_bio], [v/LIGHT_SPEED*100 for v in v_bio], 'g-', label='Bio-Hybrid Hull')
    plt.title("Propulsion Efficiency Comparison")
    plt.xlabel("Time (s)")
    plt.ylabel("Velocity (%c)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plot_path = os.path.join(result_dir, "0.31_Biomimetic_Hull_Success_Plot.png")
    plt.savefig(plot_path)
    log_print(f"✅ Success Plot saved to: {plot_path}")
    log_print("🚀 [FINISH] BIOMIMETIC RESEARCH AUDIT COMPLETE")

if __name__ == "__main__":
    run_biomimetic_surfer_proof()
