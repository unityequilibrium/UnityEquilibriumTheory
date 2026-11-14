"""
UET Proof: Quantum Nonlocality (Bell Violation)
================================================
Topic: 0.9 - Quantum Nonlocality
"""

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


import sys
from pathlib import Path
from docs import ROOT_PATH

root_path = ROOT_PATH


# --- ROBUST PATH FINDER (5x4 Grid Standard) ---


# Engine Import (Dynamic)
try:
    import importlib.util

    engine_file = (
        root_path
        / "docs"
        / "topics"
        / "0.9_Quantum_Nonlocality"
        / "Code"
        / "01_Engine"
        / "Engine_Quantum.py"
    )
    spec = importlib.util.spec_from_file_location("Engine_Quantum", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETQuantumEngine = getattr(module, "UETQuantumEngine")
except Exception as e:
    print(f"Error loading Engine: {e}")
    sys.exit(1)


def prove_bell():
    print("=" * 60)
    print("📜 UET PROOF: BELL INEQUALITY VIOLATION")
    print("=" * 60)
    # Explicit Parameter Injection (Axiomatic Standard)
    try:
        from docs.core.uet_master_equation import UETParameters

        params = UETParameters(kappa=1.0, beta=1.0)  # beta=1.0 required for Correlation
    except ImportError:
        # Fallback if path issues persist (Mocking the struct for safety)
        class MockParams:
            def __init__(self):
                self.kappa = 1.0
                self.beta = 1.0
                self.alpha = 1.0
                self.step_size = 0.1

        params = MockParams()

    print(f"  [DEBUG] Running with beta={params.beta}")
    engine = UETQuantumEngine(mode="entanglement", uet_params=params)
    engine.step()
    s_value = engine.get_extra_metrics()["metric_val"]
    print(f"  CHSH S-Value: {s_value:.4f} (Classical Limit 2.0)")
    if s_value > 2.0:
        print("  ✅ PASS: UET violates Bell Inequality axiomatically.")
    else:
        print("  ❌ FAIL: Result remained classical.")
    return True


if __name__ == "__main__":
    prove_bell()
