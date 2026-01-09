#!/usr/bin/env python3
"""
Weak Force - Master Run Script
"""
import sys
from pathlib import Path


def main():
    print("=" * 70)
    print("   WEAK FORCE VALIDATION - UET HARNESS v0.8.7")
    print("=" * 70)

    from test_weak import WeakForceUET

    print("[1/3] Running Weak Force Tests...")
    weak = WeakForceUET()
    all_pass = weak.run_all_tests()

    print("\n[2/3] Generating plots...")
    figures_dir = Path(__file__).parent.parent / "figures"
    weak.plot_results(save_dir=figures_dir)

    print("\n[3/3] Summary...")
    print("=" * 70)

    if all_pass:
        print("✅ ALL WEAK FORCE TESTS PASSED!")
        print("   ✓ Range test (short-range verified)")
        print("   ✓ Beta decay (neutron lifetime)")
        print("   ✓ Electroweak unification")
    else:
        print("❌ SOME TESTS FAILED")

    print("=" * 70)
    print(f"Figures saved to: {figures_dir}")
    print("=" * 70)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
