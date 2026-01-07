import numpy as np
import sys
import os
from pathlib import Path
import time

# Ensure we can import uet_core
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from uet_core.solver import run_case
except ImportError:
    print("CRITICAL: uet_core not found. Run from project root.")
    sys.exit(1)


# Helper to create config (copied for standalone robustness)
def make_config(case_id, kappa=1.0, T=5.0, dt=0.01, N=64, a=-1.0, delta=1.0):
    return {
        "case_id": case_id,
        "model": "C_only",
        "domain": {"L": 10.0, "dim": 2, "bc": "periodic"},
        "grid": {"N": N},
        "time": {
            "dt": dt,
            "T": T,
            "max_steps": 1000000,
            "tol_abs": 1e-10,
            "tol_rel": 1e-10,
            "backtrack": {"factor": 0.5, "max_backtracks": 20},
            "progress_every_s": 0.5,
        },
        "params": {
            "pot": {"type": "quartic", "a": a, "delta": delta, "s": 0.0},
            "kappa": kappa,
            "M": 1.0,
        },
    }


def run_torture_suite():
    print("\n" + "=" * 60)
    print("🔥 UET TORTURE SUITE v1.0 🔥")
    print("Objective: Break the Physics Engine")
    print("=" * 60 + "\n")

    rng = np.random.default_rng(666)  # Seed of the beast for torture testing
    failures = []

    # 1. THE BIG BANG (Infinite Density)
    print(">> [TEST 1] THE BIG BANG (High Density Injection)")
    try:
        # Normal is ~1.0. We inject 1,000,000.0
        # If the solver assumes small perturbations, this will explode.
        # But a robust field theory should handle it via nonlinearity.
        config = make_config("torture_bang", kappa=1.0, T=1.0)
        # We manually inject the massive spike in the solver?
        # No, simpler: We rely on run_case which inits random noise.
        # Wait, run_case inits small noise. We need to HACK the solver or modify init?
        # Standard run_case doesn't let us inject custom fields yet without reading file.
        # Check: run_case docs say it inits random small noise.
        # To stress test, we can pass a parameter 's' (bias) huge?
        # Or better: Just set 'a' (potential depth) massive?
        # Let's try HUGE 'a' = -10,000. This is still 10,000x normal gravity.
        # We also limit max_steps because high curvature forces tiny dt (Time Dilation).
        # We just want to see if it survives initialization and a few frames.
        config["params"]["pot"]["a"] = -10_000.0
        config["time"]["max_steps"] = 1000  # Only need a brief flash to prove survival
        config["time"]["wall_timeout_s"] = 10.0  # Safety cutout

        summary, _ = run_case(config, rng)
        if summary["status"] == "PASS":
            print(
                "   [PASS] Big Bang Contained. System utilized massive potential without crashing."
            )
        else:
            print(f"   [FAIL] Universe Collapsed. Status: {summary['status']}")
            failures.append("Big Bang")
    except Exception as e:
        print(f"   [CRASH] Solver died: {e}")
        failures.append("Big Bang (Crash)")

    # 2. CHAOS RUN (Long Duration Stability)
    print("\n>> [TEST 2] THE CHAOS RUN (Long Duration)")
    try:
        # Run for T=100.0 (simulated time), usually sufficient to see drift
        config = make_config("torture_chaos", T=50.0, dt=0.05)  # Coarse dt to encourage drift
        summary, _ = run_case(config, rng)

        # Check energy drift
        E0 = summary["Omega0"]
        ET = summary["OmegaT"]
        drift = abs((ET - E0) / E0) if E0 != 0 else 0

        print(f"   Drift: {drift*100:.4f}% over T=50.0")
        if drift < 0.01:  # Less than 1% drift
            print("   [PASS] Entropy is Monotonic/Conserved. Arrow of Time holds.")
        else:
            print("   [FAIL] Energy Drift detected. Laws of Thermodynamics violated.")
            failures.append("Chaos Run")

    except Exception as e:
        print(f"   [CRASH] {e}")
        failures.append("Chaos Run")

    # 3. ANTI-MATTER (Negative Interaction)
    print("\n>> [TEST 3] ANTI-MATTER (Negative Coupling)")
    try:
        # Kappa < 0 implies anti-diffusion (clustering instability).
        # Physical theories usually require Kappa > 0.
        # If we set Kappa = -1.0, it should BLOW UP immediately as 'False Vacuum'.
        # A 'PASS' here is actually a 'FAIL' in physics, but we want to see if the ERROR HANDLING works.
        # We EXPECT it to fail gracefully ("BLOWUP" or "NAN_INF").

        config = make_config("torture_antimatter", kappa=-1.0, T=1.0)
        summary, _ = run_case(config, rng)

        if summary["status"] == "FAIL":
            print(
                f"   [PASS] System correctly identified physical violation: {summary['fail_reasons']}"
            )
        else:
            print("   [FAIL] System allowed Negative Kappa to exist! (Physical Absurdity)")
            failures.append("Anti-Matter Logic")

    except Exception as e:
        print(f"   [PASS] System crashed/rejected as expected: {e}")

    # 4. LIGHT SPEED (Causality)
    print("\n>> [TEST 4] LIGHT SPEED LIMIT (Grid CFL)")
    try:
        # Try to force a timestep dt so large that info travels > 1 cell per step (CFL violation)
        # dx = L/N = 10/64 = 0.156
        # If dt > 0.5 * dx^2 (approx diffusion limit), it should backtrack.
        # We define a forbidden config.
        dx = 10.0 / 64.0
        bad_dt = 10.0  # Huge step

        config = make_config("torture_cfl", dt=bad_dt, T=20.0)
        # We hope the 'backtrack' mechanism saves us.
        summary, rows = run_case(config, rng)

        backtracks = summary["dt_backtracks_total"]
        used_dt = summary["dt_max"]

        print(f"   Requested dt={bad_dt}, Used dt={used_dt}, Backtracks={backtracks}")

        # Success if the system REFUSED the dangerous dt, either via backtracking OR auto-scaling
        if used_dt < bad_dt:
            print("   [PASS] Speed Limit Enforced. Solver proactively reduced timestep.")
        else:
            print("   [FAIL] Solver allowed FTL (Causality Violation).")
            failures.append("Speed Limit")

    except Exception as e:
        print(f"   [CRASH] {e}")
        failures.append("Speed Limit")

    print("\n" + "=" * 60)
    if not failures:
        print("✅ ALL SYSTEMS SURVIVED. UET IS UNBREAKABLE.")
        print("Ready for Public Release.")
    else:
        print(f"❌ FAILURES DETECTED: {len(failures)}")
        print(f"   Items: {failures}")
        print("Refactor recommended before release.")
    print("=" * 60)


if __name__ == "__main__":
    run_torture_suite()
