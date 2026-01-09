#!/usr/bin/env python3
"""
Strong Force - Master Run Script
================================
Run all Strong Force validation tests.

Usage:
    python run_all.py
"""
import sys
from pathlib import Path


def main():
    print("=" * 70)
    print("   STRONG FORCE VALIDATION - UET HARNESS v0.8.7")
    print("=" * 70)
    print()

    # Import and run test
    from test_strong import UETForceTest

    print("[1/3] Running UET Force Tests...")
    tester = UETForceTest(r_min=0.1, r_max=2.0, n_points=200)
    all_pass = tester.run_all_tests()

    print("\n[2/3] Generating plots...")
    figures_dir = Path(__file__).parent.parent / "figures"
    tester.plot_results(save_dir=figures_dir)

    print("\n[3/3] Summary...")
    print("=" * 70)

    if all_pass:
        print("✅ ALL TESTS PASSED!")
        print()
        print("Results:")
        for r in tester.results:
            print(f"  • {r.name}: {r.details}")
    else:
        print("❌ SOME TESTS FAILED")
        for r in tester.results:
            status = "✓" if r.success else "✗"
            print(f"  {status} {r.name}: {r.details}")

    print("=" * 70)
    print(f"Figures saved to: {figures_dir}")
    print("=" * 70)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
