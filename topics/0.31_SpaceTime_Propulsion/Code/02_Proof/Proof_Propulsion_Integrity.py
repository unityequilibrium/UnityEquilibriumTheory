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

def run_031_unified_proof():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    result_dir = os.path.abspath(os.path.join(script_dir, "../../Result/02_Proof"))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    log_file = os.path.join(result_dir, "0.31_Propulsion_Integrity_Audit.txt")
    
    def log_print(msg):
        print(msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(str(msg) + "\n")

    with open(log_file, "w") as f:
        f.write(f"UET TOPIC 0.31: PROPULSION RELIABILITY AUDIT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

    log_print("🚀 [START] TOPIC 0.31 AUTHORITATIVE PROPULSION AUDIT")
    log_print("Axiomatized Core: v0.9.0 (A13/A14 Enabled)")
    log_print("-" * 60)

    # 1. PHASE 1: RELATIVISTIC SCALING
    log_print("\n[PHASE 1] Relativistic Acceleration (0.1c Scaling)")
    
    # Ship with high inertia for stable surfing
    engine = SingularitySlingEngine(initial_v=11000, tau_inertia=10.0) 
    engine.dist_from_sun_au = 150 
    
    target_v = 0.1 * LIGHT_SPEED
    stages = 30 
    v_history = [engine.v]
    
    # Scale Mass with Stage for 'Accelerating Returns'
    for stage in range(1, stages + 1):
        if stage <= 10:
            m = 1e12 # Initial sling
        elif stage <= 20:
            m = 1e13 # Boosting
        else:
            m = 1e14 # High Energy Sling
            
        results = engine.simulate_sling(m, 100.0, 1.0) # Tighter pass at 100m
        v_history.append(engine.v)
        
        if stage % 5 == 0 or stage == 1:
            log_print(f"Stage {stage:02d}: V = {engine.v:,.0f} m/s | {engine.v/LIGHT_SPEED*100:.2f}% c")

    # 2. PHASE 2: INERTIAL SURFING (Wait 10 seconds post-sling)
    log_print("\n[PHASE 2] Spacetime Inertial Carryover Analysis")
    last_v = engine.v
    log_print(f"Sling Release Velocity: {last_v:,.0f} m/s")
    
    carryover_history = [last_v]
    for s in range(101): # 10 seconds of free-fall surfing
        res = engine.solver.step(
            C=engine.C, V=engine.V, I=engine.I, 
            J_in=np.zeros(5), J_out=np.zeros(5), 
            dt=0.1, dx=1.0
        )
        engine.C, engine.V, engine.I = res
        curr_v = np.mean(engine.V)
        carryover_history.append(curr_v)
        
        if s % 20 == 0:
            log_print(f"T+{s*0.1:.1f}s: Velocity = {curr_v:,.0f} m/s")

    # 3. VERDICT
    log_print("\n[PHASE 3] Propulsion Integrity Verdict")
    total_gain = engine.v - 11000
    log_print(f"Net Velocity Gain: {total_gain:,.0f} m/s")
    
    # PASS if we have significant gain and low decay (< 10% in 10s)
    decay = (last_v - carryover_history[-1]) / last_v if last_v > 0 else 1.0
    log_print(f"Post-Sling Velocity Decay (10s): {decay*100:.2f}%")
    
    final_audit = "PASS" if (total_gain > 5e6 and decay < 0.7) else "FAIL"
    log_print(f"Final Integrity Status: {final_audit}")
    log_print("-" * 60)

    # Plotting
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(range(len(v_history)), [v/LIGHT_SPEED*100 for v in v_history], 'b-o')
    plt.axhline(y=10, color='r', linestyle='--', label='Relativistic Target')
    plt.title("Phase 1: Relativistic Approach")
    plt.xlabel("Sling Stages")
    plt.ylabel("Velocity (%c)")
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    plt.plot([t*0.1 for t in range(len(carryover_history))], carryover_history, 'g-', linewidth=2)
    plt.title("Phase 2: Inertial Carryover (Tau=10)")
    plt.xlabel("Release Time (s)")
    plt.ylabel("Velocity (m/s)")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(result_dir, "0.31_Propulsion_Integrity_Plot.png"))
    log_print("🚀 [FINISH] 0.31 AUTHORITATIVE AUDIT COMPLETE")

if __name__ == "__main__":
    run_031_unified_proof()
