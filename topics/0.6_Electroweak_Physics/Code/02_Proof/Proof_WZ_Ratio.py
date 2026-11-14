"""
UET Proof: Electroweak Unification
==================================
Topic: 0.6 - Electroweak Physics
"""

import sys
from pathlib import Path


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


try:
    import importlib.util

    engine_file = (
        ROOT
        / "docs"
        / "topics"
        / "0.6_Electroweak_Physics"
        / "Code"
        / "01_Engine"
        / "Engine_Electroweak.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Electroweak", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETElectroweakSolver = getattr(module, "UETElectroweakSolver")
except Exception as exc:
    print(f"Error loading Engine: {exc}")
    sys.exit(1)


from docs.core.uet_parameters import get_params


def prove_electroweak():
    print("=" * 60)
    print("UET PROOF: ELECTROWEAK UNIFICATION")
    print("=" * 60)

    params = get_params("0.6")
    solver = UETElectroweakSolver(params=params)
    result = solver.solve()

    print(f"  Runtime kappa:                 {params.kappa:.6f}")
    print(f"  Runtime beta:                  {params.beta:.6f}")
    print(f"  Weinberg Angle (sin^2 theta):  {result.sin2_theta_W:.4f}")
    print(f"  Higgs Mass (Axiomatic):        {result.m_Higgs_predicted:.2f} GeV")

    if 0.18 < result.sin2_theta_W < 0.25 and 120.0 < result.m_Higgs_predicted < 130.0:
        print("  PASS: Runtime electroweak outputs stay within proof-window bounds.")
        return True

    print("  FAIL: Runtime electroweak outputs diverge from proof-window bounds.")
    return False


if __name__ == "__main__":
    sys.exit(0 if prove_electroweak() else 1)
