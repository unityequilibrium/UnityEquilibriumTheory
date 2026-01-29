"""
Research: Quantum Inspired AI (UET Hamiltonian)
================================================
Comparing Standard Gradient Descent vs Quantum-Inspired Energy Minimization.
"""

import sys
from pathlib import Path

# --- ROBUST PATH FINDER ---
current_path = Path(__file__).resolve()
ROOT = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "research_uet").exists():
        ROOT = parent
        break

if ROOT and str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Engine Import
engine_dir = current_path.parent.parent / "01_Engine"
if str(engine_dir) not in sys.path:
    sys.path.insert(0, str(engine_dir))

try:
    from UET_AI_Core import UETOptimizer, StandardOptimizer
except ImportError:
    print("CRITICAL: Engine import failed.")
    sys.exit(1)


def run_benchmark():
    print("🧠 Starting AI Optimizer Benchmark...")
    print("-------------------------------------")

    steps = 200
    initial_loss = 10.0

    # Initialize Optimizers
    opt_std = StandardOptimizer()
    opt_uet = UETOptimizer(entropy_pressure=0.08, decay_rate=0.05)

    loss_std = initial_loss
    ratio_std = 1.0
    loss_uet = initial_loss
    ratio_uet = 1.0

    print(f"{'Step':<5} | {'STD Loss':<10} {'STD Ratio':<10} | {'UET Loss':<10} {'UET Ratio':<10}")
    print("-" * 60)

    for i in range(1, steps + 1):
        loss_std, ratio_std = opt_std.step(loss_std, ratio_std)
        loss_uet, ratio_uet = opt_uet.step(loss_uet, ratio_uet)

        if i % 20 == 0:
            print(
                f"{i:<5} | {loss_std:<10.4f} {ratio_std:<10.1f} | {loss_uet:<10.4f} {ratio_uet:<10.1f}"
            )

    print("-" * 60)
    print("RESULTS:")
    print(f"Standard Final: Loss={loss_std:.4f}, Active Params={ratio_std*100:.1f}%")
    print(f"UET Final:      Loss={loss_uet:.4f}, Active Params={ratio_uet*100:.1f}%")

    efficiency_gain = (1.0 - ratio_uet) * 100
    loss_diff = abs(loss_std - loss_uet)

    if efficiency_gain > 30 and loss_diff < 0.5:
        print("\n✅ PASS: UET Optimizer achieved Natural Sparsity (>30%) with comparable accuracy.")
        return True
    else:
        print("\n❌ FAIL: UET Optimizer did not meet efficiency targets.")
        return False


if __name__ == "__main__":
    run_benchmark()
