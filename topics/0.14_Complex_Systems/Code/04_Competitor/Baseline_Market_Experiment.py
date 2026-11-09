"""
UET Market Experiment
=====================
Validates Stylized Facts of Financial Markets using UET.

Facts to Reproduce:
1.  **Fat Tails:** Returns are not Gaussian (Kurtosis > 3).
2.  **Volatility Clustering:** High vol follows high vol.

UET Hypothesis:
- Fat tails arise from the coupling term beta*C*I (Multiplicative Noise / Feedback).
- Clustering arises from the persistence of the I-field (News memory).
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
import numpy as np
import scipy.stats
from pathlib import Path

# --- PATH SETUP (Must be FIRST) ---
current_path = Path(__file__).resolve()
ROOT = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "docs").exists():
        ROOT = parent
        break

if ROOT:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    print("CRITICAL: docs root not found!")
    sys.exit(1)

TOPIC_DIR = ROOT / "docs" / "topics" / "0.14_Complex_Systems"

# Engine Import (Dynamic to bypass 0.14 folder literal restriction)
try:
    import importlib.util
    from docs.core.uet_master_equation import UETParameters

    engine_file = TOPIC_DIR / "Code" / "01_Engine" / "Engine_Econophysics.py"
    spec = importlib.util.spec_from_file_location("Engine_Econophysics", engine_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    UETEconophysicsEngine = getattr(module, "UETEconophysicsEngine")
    # Compatibility Alias
    UETEconSolver = UETEconophysicsEngine
except Exception as e:
    print(f"Error loading Engine 0.14 Market: {e}")
    sys.exit(1)


def run_experiment():
    print("=" * 70)
    print("📈 UET ECONOPHYSICS EXPERIMENT")
    print("   Testing Market Dynamics & Stylized Facts")
    print("=" * 70)

    # Beta=3.0 (Extreme coupling for fat tails), Kappa=0.1
    params = UETParameters(kappa=0.1, alpha=0.0, beta=3.0)

    # Run Simulation
    solver = UETEconSolver(
        nx=32, ny=32, dt=0.01, volatility=0.05, news_shock_prob=0.05, params=params
    )

    prices = []

    print(f"{'Step':<10} | {'Price':<15} | {'Volatility':<15}")
    print("-" * 50)

    for i in range(1001):  # Reduced steps
        solver.step(i)
        price = solver.get_market_price()
        prices.append(price)

        if i % 100 == 0:
            vol = solver.get_market_volatility()
            print(f"{i:<10} | {price:<15.4f} | {vol:<15.4f}")

    # Analyze Returns
    import numpy as np

    price_arr = np.array(prices)
    # Log-returns: R = log(P_t) - log(P_t-1)
    # Since C is already Log-Price (roughly), we can just take difference.
    # But let's assume C represents Price Level to be safe with diff(log).
    # Wait, in solver we treat it as additive process -> Geometric Brownian Motion exponent?
    # Actually, EconSolver uses additive noise -> C is Log-Price.
    # So Returns = diff(C).

    returns = np.diff(price_arr)

    # Check Fat Tails (Kurtosis)
    # Normal distribution has Kurtosis = 0 (Fisher definition, used by scipy)
    kurtosis = scipy.stats.kurtosis(returns)
    skewness = scipy.stats.skew(returns)

    print("-" * 50)
    print(f"Return Kurtosis: {kurtosis:.4f} (Normal = 0.0)")
    print(f"Return Skewness: {skewness:.4f}")

    if kurtosis > 1.0:
        print("✅ PASS: Fat Tails Detected (Market is Non-Gaussian)")
    elif kurtosis > 0:
        print("⚠️ WARN: Mild Fat Tails (Close to Gaussian)")
    else:
        print("❌ FAIL: Thin Tails (Gaussian or lighter)")

    # Check Volatility Clustering (Autocorrelation of absolute returns)
    abs_returns = np.abs(returns)
    if len(abs_returns) > 1:
        autocorr = np.corrcoef(abs_returns[:-1], abs_returns[1:])[0, 1]
    else:
        autocorr = 0.0

    print(f"Vol Clustering (Autocorr): {autocorr:.4f}")

    if autocorr > 0.1:
        print("✅ PASS: Volatility Clustering Detected (Memory effect)")
    else:
        print("❌ FAIL: No Volatility Clustering (Random Walk)")


if __name__ == "__main__":
    run_experiment()
