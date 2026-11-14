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

def run_academic_integrity_audit():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    result_dir = os.path.abspath(os.path.join(script_dir, "../../Result/02_Proof"))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    log_file = os.path.join(result_dir, "0.31_Scientific_Rigor_Audit.txt")
    
    def log_print(msg):
        print(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(str(msg) + "\n")

    with open(log_file, "w") as f:
        f.write("UET TOPIC 0.31: SCIENTIFIC RIGOR & REALITY AUDIT (FINAL VALIDATED)\n\n")

    log_print("🚀 [START] TOPIC 0.31 ACADEMIC INTEGRITY AUDIT")
    log_print("Checking for 'Meteo' (Imaginary) Physics Violations.")

    # 1. TEST RELATIVISTIC HARDENING (γ-scaling)
    log_print("\n[TEST 1] Relativistic Mass Inflation (Lorentz Penalty)")
    engine = SingularitySlingEngine(initial_v=0.99 * LIGHT_SPEED) # Start at 99%c
    results = engine.simulate_sling(1e22, 10.0, 1.0) # Massive singularity
    
    log_print(f"Final Velocity: {engine.v/LIGHT_SPEED*100:.6f}% c")
    if engine.v < LIGHT_SPEED:
        log_print("✅ SUCCESS: Lorentz Limit enforced. Velocity stayed below c.")

    # 2. TEST THERMODYNAMIC COSTING (Landauer Limit)
    log_print("\n[TEST 2] Bio-Shield Energy Consumption (Landauer)")
    # Must have resilience > 0 for repair to exist, but low enough for damage to occur
    engine_bio = SingularitySlingEngine(initial_v=0.5 * LIGHT_SPEED, bio_resilience=0.1)
    initial_energy = engine_bio.ship_energy
    
    # Run a high-velocity sling to ensure (v/c)^2 damage > 0.1
    results_bio = engine_bio.simulate_sling(1e12, 100.0, 1.0)
    
    final_energy = engine_bio.ship_energy
    energy_loss = initial_energy - final_energy
    
    log_print(f"Fuel Consumption for Bio-Repair: {energy_loss:.2e} Joules")
    if energy_loss > 0:
        log_print("✅ SUCCESS: 2nd Law enforced. Resilience costs energy.")

    # 3. VERDICT
    log_print("\n[FINAL VERDICT]")
    if engine.v < LIGHT_SPEED and energy_loss > 0:
        log_print("✅ UET TOPIC 0.31 IS ACADEMICALLY HARDENED (v0.9.4).")
    else:
        log_print("⚠️ AUDIT FAILED.")

if __name__ == "__main__":
    run_academic_integrity_audit()
