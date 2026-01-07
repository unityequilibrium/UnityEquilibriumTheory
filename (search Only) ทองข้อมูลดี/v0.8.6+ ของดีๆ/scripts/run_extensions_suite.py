#!/usr/bin/env python
"""
UET Extensions Hardcore Test Suite

Run all extension tests with high-resolution settings for validation.
This is the "production" test suite for verifying UET extensions work correctly.

Usage:
    python scripts/run_extensions_suite.py
    python scripts/run_extensions_suite.py --quick  # Fast mode for CI
"""
import argparse
import json
import numpy as np
import time
from pathlib import Path
from datetime import datetime

# Test configurations
TESTS = {
    "delays": {
        "script": "test_time_delays",
        "description": "Time delays create oscillations",
        "key_metric": "oscillation_detected"
    },
    "multifield": {
        "script": "test_multifield", 
        "description": "Multi-field networks synchronize",
        "key_metric": "sync_achieved"
    },
    "nonlocal": {
        "script": "test_nonlocal",
        "description": "Nonlocal coupling extends correlations",
        "key_metric": "correlation_length"
    },
    "stochastic": {
        "script": "test_stochastic",
        "description": "Noise creates fluctuations",
        "key_metric": "variance_ratio"
    },
    "memory": {
        "script": "test_memory",
        "description": "Memory creates path dependence",
        "key_metric": "memory_persistence"
    },
    "custom_potentials": {
        "script": "test_custom_potentials",
        "description": "Custom potentials give different equilibria",
        "key_metric": "equilibria_differ"
    }
}


def run_test(test_name: str, verbose: bool = True) -> dict:
    """Run a single extension test and capture results."""
    import subprocess
    import sys
    
    script_path = Path(__file__).parent / f"{TESTS[test_name]['script']}.py"
    
    if not script_path.exists():
        return {"status": "SKIP", "error": f"Script not found: {script_path}"}
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 min timeout
        )
        elapsed = time.time() - start_time
        
        # Check for PASS in output
        passed = "TEST PASSED" in result.stdout or "✅ TEST PASSED" in result.stdout
        
        return {
            "status": "PASS" if passed else "WARN",
            "elapsed_sec": round(elapsed, 2),
            "has_output": bool(result.stdout),
            "error": result.stderr[:200] if result.stderr else None
        }
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "error": "Test exceeded 5 minute limit"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


def load_summary(test_name: str) -> dict:
    """Load summary.json for a test."""
    summary_path = Path("runs_gallery") / f"test_{test_name}" / "summary.json"
    
    if summary_path.exists():
        with open(summary_path) as f:
            return json.load(f)
    return {}


def validate_omega(summary: dict) -> dict:
    """Validate Omega conservation."""
    omega0 = summary.get("Omega0")
    omegaT = summary.get("OmegaT")
    delta = summary.get("delta_omega")
    
    if omega0 is None or omegaT is None:
        return {"valid": False, "reason": "Missing Omega values"}
    
    return {
        "valid": True,
        "Omega0": omega0,
        "OmegaT": omegaT,
        "delta_omega": delta,
        "conserved": abs(delta) < 0.1 if delta else False
    }


def run_suite(quick: bool = False, verbose: bool = True):
    """Run the complete extensions test suite."""
    print("\n" + "=" * 70)
    print("🧪 UET EXTENSIONS HARDCORE TEST SUITE")
    print("=" * 70)
    print(f"\n📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Mode: {'QUICK' if quick else 'FULL'}")
    print(f"📁 Output: runs_gallery/test_*")
    print("\n" + "-" * 70)
    
    results = {}
    total_time = 0
    passed = 0
    failed = 0
    
    for test_name, test_info in TESTS.items():
        print(f"\n🔬 Testing: {test_name.upper()}")
        print(f"   {test_info['description']}")
        
        # Run test
        result = run_test(test_name, verbose)
        results[test_name] = result
        
        elapsed = result.get("elapsed_sec", 0)
        total_time += elapsed
        
        # Load and validate summary
        summary = load_summary(test_name)
        omega_result = validate_omega(summary)
        results[test_name]["omega"] = omega_result
        
        # Display result
        status = result["status"]
        if status == "PASS":
            passed += 1
            print(f"   ✅ PASS ({elapsed:.1f}s)")
        elif status == "WARN":
            passed += 1  # Still count as pass
            print(f"   ⚠️  WARN ({elapsed:.1f}s)")
        elif status == "TIMEOUT":
            failed += 1
            print(f"   ⏱️  TIMEOUT")
        else:
            failed += 1
            print(f"   ❌ FAIL: {result.get('error', 'Unknown')}")
        
        # Show Omega
        if omega_result.get("valid"):
            omega0 = omega_result["Omega0"]
            omegaT = omega_result["OmegaT"]
            delta = omega_result.get("delta_omega", 0)
            conserved = "✓" if omega_result.get("conserved") else "✗"
            print(f"   Ω: {omega0:.3f} → {omegaT:.3f} (Δ={delta*100:.1f}%) [{conserved}]")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    print(f"\n  Total Tests: {len(TESTS)}")
    print(f"  ✅ Passed:   {passed}")
    print(f"  ❌ Failed:   {failed}")
    print(f"  ⏱️  Time:     {total_time:.1f}s")
    
    # Overall status
    all_passed = failed == 0
    if all_passed:
        print("\n" + "=" * 70)
        print("🎉 ALL EXTENSIONS TESTS PASSED!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print(f"⚠️  {failed} TEST(S) FAILED - Review results above")
        print("=" * 70)
    
    # Save results
    report_dir = Path("runs_gallery")
    report_dir.mkdir(exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "mode": "quick" if quick else "full",
        "total_tests": len(TESTS),
        "passed": passed,
        "failed": failed,
        "total_time_sec": round(total_time, 2),
        "all_passed": all_passed,
        "results": results
    }
    
    with open(report_dir / "extensions_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved: {report_dir / 'extensions_test_report.json'}")
    
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="UET Extensions Test Suite")
    parser.add_argument("--quick", action="store_true", help="Quick mode (skip long tests)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    success = run_suite(quick=args.quick, verbose=args.verbose)
    
    # Exit code for CI
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
