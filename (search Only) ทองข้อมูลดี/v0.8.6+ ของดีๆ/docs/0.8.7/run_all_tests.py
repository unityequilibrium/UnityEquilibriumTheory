#!/usr/bin/env python3
"""
UET PRODUCTION TEST SUITE
=========================
Master test script that runs ALL tests multiple times
to validate production stability.

Usage:
    python run_all_tests.py           # Single run
    python run_all_tests.py --full    # 3 stability runs
    python run_all_tests.py --loops N # N stability runs

Author: UET Research Team
Date: 2025-12-28
"""

import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import argparse

# Base directory
BASE = Path(__file__).parent

# All test scripts to run
TEST_SCRIPTS = [
    # Phase 1: Four Forces
    ("01-gravity-uet", "01-gravity-uet/01_data/test_gravity.py"),
    ("02-em-force-uet", "02-em-force-uet/01_data/test_em.py"),
    ("03-strong-force-uet", "03-strong-force-uet/01_data/test_strong.py"),
    ("04-weak-force-uet", "04-weak-force-uet/01_data/test_weak.py"),
    ("05-unification", "05-unification/01_data/test_unification.py"),
    # Phase 2: Quantum
    ("06-quantum-extension", "06-quantum-extension/01_data/test_quantum.py"),
    # Phase 3: GR
    ("07-gr-effects", "07-gr-effects/01_data/test_gr.py"),
    # Phase 4: Constants
    ("08-unification-constants", "08-unification-constants/01_data/test_constants.py"),
    # Phase 5: Predictions
    ("09-experimental-predictions", "09-experimental-predictions/01_data/test_predictions.py"),
    # Phase 6: Lagrangian
    ("10-lagrangian-formalism", "10-lagrangian-formalism/01_data/test_lagrangian.py"),
    # Advanced Topics
    ("12-spin-statistics", "12-spin-statistics/01_data/test_spin.py"),
    ("13-pauli-exclusion", "13-pauli-exclusion/01_data/test_pauli.py"),
    ("14-gravitational-waves", "14-gravitational-waves/01_data/test_gw.py"),
    ("15-mass-generation", "15-mass-generation/01_data/test_mass.py"),
    ("16-hamiltonian", "16-hamiltonian/01_data/test_hamiltonian.py"),
]


def run_test(name: str, script_path: str, verbose: bool = False) -> dict:
    """Run a single test script and return results."""
    full_path = BASE / script_path

    if not full_path.exists():
        return {
            "name": name,
            "status": "SKIP",
            "error": f"File not found: {script_path}",
            "duration": 0,
        }

    start = time.time()
    try:
        import os

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            [sys.executable, str(full_path)],
            capture_output=True,
            timeout=120,
            env=env,
            encoding="utf-8",
            errors="replace",
        )
        duration = time.time() - start

        # Check if passed
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        output = stdout + stderr
        passed = result.returncode == 0 or "PASS" in output

        return {
            "name": name,
            "status": "PASS" if passed else "FAIL",
            "returncode": result.returncode,
            "duration": round(duration, 2),
            "output_snippet": output[-500:] if verbose else None,
        }
    except subprocess.TimeoutExpired:
        return {"name": name, "status": "TIMEOUT", "duration": 120}
    except Exception as e:
        return {"name": name, "status": "ERROR", "error": str(e), "duration": time.time() - start}


def run_all_tests(verbose: bool = False) -> dict:
    """Run all tests once and return summary."""
    print("\n" + "=" * 70)
    print("UET PRODUCTION TEST SUITE")
    print("=" * 70)

    results = []
    passed = 0
    failed = 0
    skipped = 0

    for name, script in TEST_SCRIPTS:
        print(f"\n  Running {name}...", end=" ", flush=True)
        result = run_test(name, script, verbose)
        results.append(result)

        if result["status"] == "PASS":
            print(f"PASS ({result['duration']:.1f}s)")
            passed += 1
        elif result["status"] == "SKIP":
            print(f"SKIP")
            skipped += 1
        else:
            print(f"FAIL ({result.get('error', 'unknown')})")
            failed += 1

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total": len(TEST_SCRIPTS),
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": round(passed / (passed + failed) * 100, 1) if (passed + failed) > 0 else 0,
        "results": results,
    }

    print("\n" + "=" * 70)
    print(f"SUMMARY: {passed}/{passed + failed + skipped} PASSED ({summary['pass_rate']}%)")
    print("=" * 70)

    return summary


def run_stability_test(loops: int = 3) -> dict:
    """Run multiple test loops to check stability."""
    print("\n" + "=" * 70)
    print(f"UET STABILITY TEST - {loops} LOOPS")
    print("=" * 70)

    all_runs = []
    total_start = time.time()

    for i in range(loops):
        print(f"\n--- LOOP {i+1}/{loops} ---")
        summary = run_all_tests()
        all_runs.append(summary)
        print(f"Loop {i+1}: {summary['passed']}/{summary['total']} PASSED")

    total_duration = time.time() - total_start

    # Analyze stability
    pass_rates = [r["pass_rate"] for r in all_runs]
    min_pass = min(pass_rates)
    max_pass = max(pass_rates)
    avg_pass = sum(pass_rates) / len(pass_rates)

    # Find flaky tests (pass in some runs, fail in others)
    test_results = {}
    for run in all_runs:
        for test in run["results"]:
            name = test["name"]
            if name not in test_results:
                test_results[name] = []
            test_results[name].append(test["status"])

    flaky = []
    for name, statuses in test_results.items():
        if len(set(statuses)) > 1:
            flaky.append({"name": name, "statuses": statuses})

    stability_report = {
        "timestamp": datetime.now().isoformat(),
        "loops": loops,
        "total_duration": round(total_duration, 1),
        "pass_rates": pass_rates,
        "min_pass_rate": min_pass,
        "max_pass_rate": max_pass,
        "avg_pass_rate": round(avg_pass, 1),
        "stable": min_pass == 100 and max_pass == 100,
        "flaky_tests": flaky,
        "runs": all_runs,
    }

    # Print stability summary
    print("\n" + "=" * 70)
    print("STABILITY REPORT")
    print("=" * 70)
    print(f"  Loops: {loops}")
    print(f"  Duration: {total_duration:.1f}s")
    print(f"  Pass rates: {pass_rates}")
    print(f"  Min/Max/Avg: {min_pass}% / {max_pass}% / {avg_pass:.1f}%")
    print(f"  Flaky tests: {len(flaky)}")
    if flaky:
        for f in flaky:
            print(f"    - {f['name']}: {f['statuses']}")
    print(f"\n  STABLE: {'YES' if stability_report['stable'] else 'NO'}")
    print("=" * 70)

    return stability_report


def save_report(report: dict, filename: str = "production_test_report.json"):
    """Save report to JSON file."""
    output = BASE / filename
    with open(output, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved: {output}")


def main():
    parser = argparse.ArgumentParser(description="UET Production Test Suite")
    parser.add_argument("--full", action="store_true", help="Run 3 stability loops")
    parser.add_argument("--loops", type=int, default=1, help="Number of test loops")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show test output")
    args = parser.parse_args()

    if args.full:
        args.loops = 3

    if args.loops > 1:
        report = run_stability_test(args.loops)
        save_report(report, "stability_test_report.json")
        return 0 if report["stable"] else 1
    else:
        summary = run_all_tests(args.verbose)
        save_report(summary, "production_test_report.json")
        return 0 if summary["pass_rate"] == 100 else 1


if __name__ == "__main__":
    exit(main())
