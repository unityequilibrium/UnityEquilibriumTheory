"""
UET Master Test Runner for Topics
==================================
Runs all tests in topics/ and generates summary.
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

TOPICS = Path(__file__).parent


def find_all_tests():
    """Find all test files.

    Prioritizes 5x4 Grid structure for Topics 0.1-0.10:
    - Code/01_Engine/
    - Code/02_Proof/
    - Code/03_Research/
    - Code/04_Competitor/
    """
    tests = []
    seen_paths = set()

    # Priority 1: 5x4 Grid folders (Standard for ALL Topics 0.1-0.24)
    grid_folders = ["01_Engine", "02_Proof", "03_Research", "04_Competitor"]

    for topic_dir in TOPICS.iterdir():
        if not topic_dir.is_dir() or not topic_dir.name.startswith("0."):
            continue

        code_dir = topic_dir / "Code"
        if not code_dir.exists():
            # Support for legacy layout if 'Code' folder is missing (fallback)
            pass
        else:
            # Search in 5x4 Grid folders
            for grid_folder in grid_folders:
                folder = code_dir / grid_folder
                if folder.exists():
                    for py_file in folder.glob("*.py"):
                        if py_file.name.startswith("__"):
                            continue
                        if py_file not in seen_paths:
                            seen_paths.add(py_file)
                            tests.append(
                                {
                                    "path": py_file,
                                    "solution": topic_dir.name,
                                    "name": py_file.stem,
                                    "grid_folder": grid_folder,
                                }
                            )

    # Priority 2: Legacy fallback (for any files NOT in standard Grid structure)
    # Most should be picked up above now.

    # Also include Engine_, Proof_, Research_, Competitor_ files from legacy locations
    for extra_file in TOPICS.rglob("*.py"):
        if extra_file in seen_paths or extra_file.name.startswith("__"):
            continue
        if extra_file.name == "test_runner.py":
            continue

        # Skip visualization directories to avoid 'visual debt' during bulk runs
        if "05_Visualization" in str(extra_file):
            continue

        is_valid = (
            extra_file.name.startswith("Engine_")
            or extra_file.name.startswith("Proof_")
            or extra_file.name.startswith("Research_")
            or extra_file.name.startswith("Competitor_")
            or "benchmark" in extra_file.name
            or extra_file.name.startswith("experiment_")
        )

        if is_valid:
            solution = extra_file.relative_to(TOPICS).parts[0]
            seen_paths.add(extra_file)
            tests.append(
                {
                    "path": extra_file,
                    "solution": solution,
                    "name": extra_file.stem,
                }
            )

    return tests


def run_test(test_path):
    """Run a single test and return result."""
    try:
        # robust environment setup
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        # Inject standard paths
        project_root = TOPICS.parent.parent
        lab_path = project_root / "lab"
        docs = project_root / "docs"

        extra_paths = [
            str(project_root),
            str(docs),
            str(lab_path),
            str(lab_path / "01_galaxy_dynamics"),
            str(lab_path / "02_gravitational"),
            str(lab_path / "03_electroweak"),
            str(lab_path / "04_neutrino"),
            str(lab_path / "05_qcd_hadrons"),
            str(lab_path / "06_motion_dynamics"),
            str(lab_path / "07_complex_systems"),
            str(lab_path / "00_thermodynamic_bridge"),
        ]

        current_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = os.pathsep.join(extra_paths) + os.pathsep + current_pythonpath

        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(test_path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            cwd=str(test_path.parent),
            env=env,
        )

        output = result.stdout + result.stderr
        passed = result.returncode == 0

        # Try to extract pass count from output
        import re

        match = re.search(r"(\d+)/(\d+)\s*PASS", output)
        if match:
            passed_count = int(match.group(1))
            total_count = int(match.group(2))
        else:
            passed_count = 1 if passed else 0
            total_count = 1

        return {
            "passed": passed,
            "passed_count": passed_count,
            "total_count": total_count,
            "output": output,
        }
    except Exception as e:
        return {
            "passed": False,
            "passed_count": 0,
            "total_count": 1,
            "output": str(e),
        }


def main():
    """Run all tests and generate report."""
    print("=" * 70)
    print("UET MASTER TEST RUNNER")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    tests = find_all_tests()
    print(f"\nFound {len(tests)} test files")

    # Group by solution
    by_solution = {}
    for t in tests:
        sol = t["solution"]
        if sol not in by_solution:
            by_solution[sol] = []
        by_solution[sol].append(t)

    print(f"In {len(by_solution)} solutions:")
    for sol in sorted(by_solution.keys()):
        print(f"  {sol}: {len(by_solution[sol])} tests")

    # Run all tests
    print("\n" + "=" * 70)
    print("RUNNING TESTS...")
    print("=" * 70)

    total_passed = 0
    total_tests = 0
    results = []

    for sol in sorted(by_solution.keys()):
        print(f"\n>>> {sol}")

        for t in by_solution[sol]:
            print(f"  Running {t['name']}...", end=" ")
            result = run_test(t["path"])

            total_passed += result["passed_count"]
            total_tests += result["total_count"]

            status = "PASS" if result["passed"] else "FAIL"
            print(f"{status} ({result['passed_count']}/{result['total_count']})")

            results.append(
                {
                    "solution": sol,
                    "test": t["name"],
                    **result,
                }
            )

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\nTotal Test Files: {len(tests)}")
    print(f"Total Individual Tests: {total_tests}")
    print(f"Total Passed: {total_passed}")
    print(f"Pass Rate: {total_passed/total_tests*100:.1f}%")

    # By solution
    print("\nBy Solution:")
    for sol in sorted(by_solution.keys()):
        sol_results = [r for r in results if r["solution"] == sol]
        sol_passed = sum(r["passed_count"] for r in sol_results)
        sol_total = sum(r["total_count"] for r in sol_results)
        pct = sol_passed / sol_total * 100 if sol_total > 0 else 0
        status = "[OK]" if pct >= 70 else "[!!]"
        print(f"  {status} {sol}: {sol_passed}/{sol_total} ({pct:.0f}%)")

    print("\n" + "=" * 70)

    # Grade
    if total_tests >= 100 and total_passed / total_tests >= 0.90:
        print("GRADE: EXCELLENT (100+ tests, 90%+ pass)")
    elif total_tests >= 75 and total_passed / total_tests >= 0.85:
        print("GRADE: VERY GOOD (75+ tests, 85%+ pass)")
    elif total_tests >= 50 and total_passed / total_tests >= 0.80:
        print("GRADE: GOOD (50+ tests, 80%+ pass)")
    else:
        print(f"GRADE: IN PROGRESS ({total_tests} tests, {total_passed/total_tests*100:.0f}% pass)")

    print("=" * 70)

    return total_passed >= total_tests * 0.7


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
