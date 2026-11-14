"""
UET Parameter Engine Validation
===============================
Verifies that "Self-Driving" parameters match Reality (NIST).
"""

import importlib.util

from docs.core.core_paths import canonical_existing_path


_ENGINE_PATH = canonical_existing_path("docs/core/test/parameter_engine/engine.py")
_ENGINE_SPEC = importlib.util.spec_from_file_location("uet_parameter_engine_canonical", _ENGINE_PATH)
if _ENGINE_SPEC is None or _ENGINE_SPEC.loader is None:
    raise ImportError(f"Unable to load parameter engine from {_ENGINE_PATH}")
_ENGINE_MODULE = importlib.util.module_from_spec(_ENGINE_SPEC)
_ENGINE_SPEC.loader.exec_module(_ENGINE_MODULE)
UETParameterEngine = _ENGINE_MODULE.UETParameterEngine


def test_engine():
    print("=" * 60)
    print("UET SELF-DRIVING PARAMETER ENGINE")
    print("Deriving Constants from Geometry...")
    print("=" * 60)

    engine = UETParameterEngine()
    results = engine.run_derivation_suite()

    # NIST 2024 Values (Approx)
    NIST = {"inverse_alpha": 137.035999, "sin2_theta_w": 0.23122}

    print(f"\n{'Constant':<20} {'Derived':<15} {'NIST Ref':<15} {'Error':<10}")
    print("-" * 65)

    # Verify Alpha
    inv_alpha = results["inverse_alpha"]
    err_alpha = abs(inv_alpha - NIST["inverse_alpha"])
    print(f"{'1/Alpha':<20} {inv_alpha:<15.6f} {NIST['inverse_alpha']:<15.6f} {err_alpha:.1e}")

    # Verify Weinberg
    sin2w = results["sin2_theta_w"]
    err_w = abs(sin2w - NIST["sin2_theta_w"])
    print(f"{'sin^2 Theta_W':<20} {sin2w:<15.5f} {NIST['sin2_theta_w']:<15.5f} {err_w:.1e}")

    print("-" * 65)

    if err_alpha < 1e-4 and err_w < 1e-4:
        print("\nPASSED: Engine Logic Matches Reality.")
        return True
    else:
        print("\nFAILED: Derivation Deviation.")
        return False


if __name__ == "__main__":
    test_engine()
