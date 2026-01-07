"""
UET Stress Test: Random Parameter Validation
ทดสอบ Theory vs Reality ด้วย random parameters ที่โหด
"""
import sys
import json
import numpy as np
from pathlib import Path

# Add uet_core to path
sys.path.insert(0, str(Path(__file__).parent))

from uet_core.solver import run_case, StrictSettings
from uet_core.potentials import QuarticPotential

def run_stress_test(n_tests=10, seed=42):
    """Run stress tests with random parameters"""
    rng = np.random.default_rng(seed)
    results = []
    
    print("="*80)
    print("🧪 UET STRESS TEST: Theory vs Reality")
    print("="*80)
    print()
    print("CLAIM (ตามทฤษฎี):")
    print("  1. ΔΩ ≤ 0 ทุก step (Ω ต้อง monotonically decrease)")
    print("  2. 𝒱 = -ΔΩ ≥ 0 (Value ต้องไม่ติดลบ)")
    print("  3. ถ้า PASS: Ω_final < Ω_initial")
    print("  4. ถ้า parameters invalid: ต้อง FAIL หรือ WARN")
    print()
    print("="*80)
    print()
    
    for i in range(n_tests):
        # Random parameters - บางค่าอาจ invalid!
        a = rng.uniform(-5, 2)      # บางครั้งอาจ a > 0 (invalid)
        delta = rng.uniform(-1, 5)   # บางครั้งอาจ delta < 0 (invalid)
        s = rng.uniform(-2, 2)
        kappa = rng.uniform(-0.5, 2) # บางครั้งอาจ kappa < 0 (invalid)
        beta = rng.uniform(-0.5, 2)   # บางครั้งอาจ invalid
        
        # Time params
        dt = rng.uniform(0.001, 0.05)
        T = rng.uniform(0.5, 3.0)
        N = rng.choice([32, 48, 64])
        
        # Determine expected result based on theory
        expected_stable = (a < 0) and (delta > 0) and (kappa > 0) and (beta >= 0)
        expected_result = "PASS" if expected_stable else "FAIL/WARN"
        
        # Build config
        config = {
            "case_id": f"stress_test_{i}",
            "model": "C_I",
            "domain": {"L": 10.0, "dim": 2, "bc": "periodic"},
            "grid": {"N": int(N)},
            "time": {
                "dt": dt,
                "T": T,
                "max_steps": 500,
                "tol_abs": 1e-8,
                "tol_rel": 1e-8,
                "backtrack": {"factor": 0.5, "max_backtracks": 20}
            },
            "params": {
                "potC": {"type": "quartic", "a": a, "delta": delta, "s": s},
                "potI": {"type": "quartic", "a": a, "delta": delta, "s": s},
                "beta": beta,
                "kC": kappa,
                "kI": kappa,
                "MC": 1.0,
                "MI": 1.0
            }
        }
        
        print(f"Test {i+1}/{n_tests}:")
        print(f"  Parameters:")
        print(f"    a={a:.3f}, δ={delta:.3f}, s={s:.3f}")
        print(f"    κ={kappa:.3f}, β={beta:.3f}")
        print(f"    dt={dt:.4f}, T={T:.2f}, N={N}")
        print()
        print(f"  EXPECTED (ตามทฤษฎี):")
        print(f"    Valid params? {expected_stable}")
        print(f"    Expected status: {expected_result}")
        
        # Run simulation
        try:
            settings = StrictSettings()
            summary, timeseries = run_case(config, rng, settings)
            
            Omega0 = summary.get("Omega0", 0)
            OmegaT = summary.get("OmegaT", 0)
            status = summary.get("status", "UNKNOWN")
            V_value = Omega0 - OmegaT  # 𝒱 = -ΔΩ
            
            print()
            print(f"  ACTUAL (ผลจริง):")
            print(f"    Status: {status}")
            print(f"    Ω₀ = {Omega0:.6f}")
            print(f"    ΩT = {OmegaT:.6f}")
            print(f"    𝒱 = -ΔΩ = {V_value:.6f}")
            print(f"    Backtracks: {summary.get('dt_backtracks_total', 0)}")
            
            # Validate claims
            claim1 = V_value >= -1e-6  # ΔΩ ≤ 0 (with tolerance)
            claim2 = status == "PASS" if expected_stable else True  # Allow FAIL for invalid
            claim3 = (status != "PASS") if not expected_stable else True  # Should fail if invalid
            
            all_valid = claim1 and claim2
            
            print()
            print(f"  VALIDATION:")
            print(f"    Claim 1 (𝒱 ≥ 0): {'✅' if claim1 else '❌'} (𝒱 = {V_value:.6f})")
            print(f"    Claim 2 (Expected status): {'✅' if claim2 else '❌'}")
            if not expected_stable:
                print(f"    Claim 3 (Invalid → FAIL): {'✅' if status != 'PASS' else '⚠️ Passed anyway'}")
            print(f"    Overall: {'✅ VALID' if all_valid else '❌ INVALID'}")
            
            results.append({
                "test": i,
                "params": {"a": a, "delta": delta, "s": s, "kappa": kappa, "beta": beta},
                "expected_stable": expected_stable,
                "expected_status": expected_result,
                "actual_status": status,
                "Omega0": Omega0,
                "OmegaT": OmegaT,
                "V_value": V_value,
                "claim1_valid": claim1,
                "claim2_valid": claim2,
                "all_valid": all_valid
            })
            
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "test": i,
                "error": str(e),
                "expected_stable": expected_stable
            })
        
        print()
        print("-"*80)
        print()
    
    # Summary
    print("="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    valid_runs = [r for r in results if "error" not in r]
    claim1_pass = sum(1 for r in valid_runs if r.get("claim1_valid", False))
    claim2_pass = sum(1 for r in valid_runs if r.get("claim2_valid", False))
    all_pass = sum(1 for r in valid_runs if r.get("all_valid", False))
    
    print(f"Total tests: {n_tests}")
    print(f"Completed: {len(valid_runs)}")
    print(f"Errors: {n_tests - len(valid_runs)}")
    print()
    print(f"Claim 1 (𝒱 ≥ 0): {claim1_pass}/{len(valid_runs)} ({'✅' if claim1_pass == len(valid_runs) else '⚠️'})")
    print(f"Claim 2 (Expected status): {claim2_pass}/{len(valid_runs)}")
    print(f"All claims valid: {all_pass}/{len(valid_runs)}")
    
    return results

if __name__ == "__main__":
    results = run_stress_test(n_tests=5)
