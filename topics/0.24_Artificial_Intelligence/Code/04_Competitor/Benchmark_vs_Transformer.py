"""
UET vs Competitor Benchmark
===========================
Topic: 0.24 Artificial Intelligence
Folder: 04_Competitor

Goal: Compare UET Optimizer vs Standard Dense Optimizer.
Competitors:
1. "Dense Transformer" (Llama-3 Style) - Uses StandardOptimizer
2. "UET Sparse Engine" (DeepSeek Style) - Uses UETOptimizer

Data Source:
- deepseek_moe_data.json (Target benchmarks)
"""

import sys
import json
import matplotlib.pyplot as plt
from pathlib import Path

# --- ROBUST PATH FINDER ---
current_path = Path(__file__).resolve()
ROOT = None
for parent in [current_path] + list(current_path.parents):
    if (parent / "docs").exists():
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
    print("=" * 60)
    print("⚔️  COMPETITOR BENCHMARK: DENSE vs UET-SPARSE")
    print("=" * 60)

    # 1. Setup Dense Model (Llama-3 70B Simulator)
    dense_opt = StandardOptimizer()
    dense_loss = 10.0
    dense_ratio = 1.0
    dense_history = []

    # 2. Setup UET Model (DeepSeek-V2 Simulator)
    uet_opt = UETOptimizer(entropy_pressure=0.15, decay_rate=0.12)
    uet_loss = 10.0
    uet_ratio = 1.0
    uet_history = []

    steps = 100

    # Run Simulation
    for i in range(steps):
        # Step Dense
        dense_loss, dense_ratio = dense_opt.step(dense_loss, dense_ratio)
        dense_history.append((dense_loss, dense_ratio))

        # Step UET
        uet_loss, uet_ratio = uet_opt.step(uet_loss, uet_ratio)
        uet_history.append((uet_loss, uet_ratio))

    # Analysis
    final_dense_loss, final_dense_ratio = dense_history[-1]
    final_uet_loss, final_uet_ratio = uet_history[-1]

    # Viz
    result_dir = (
        ROOT
        / "docs"
        / "topics"
        / "0.24_Artificial_Intelligence"
        / "Result"
        / "04_Competitor"
    )
    result_dir.mkdir(parents=True, exist_ok=True)

    # Plot Active Ratio Evolution
    steps_range = range(steps)
    dense_ratios = [x[1] for x in dense_history]
    uet_ratios = [x[1] for x in uet_history]
    dense_losses = [x[0] for x in dense_history]
    uet_losses = [x[0] for x in uet_history]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Ax1: Sparsity (The Phase Transition)
    ax1.plot(steps_range, dense_ratios, "b--", label="Dense (Llama Type)")
    ax1.plot(steps_range, uet_ratios, "r-", label="UET (DeepSeek Type)")
    ax1.set_title("Structure Evolution: Phase Transition")
    ax1.set_xlabel("Training Steps")
    ax1.set_ylabel("Active Parameters (Ratio)")
    ax1.legend()
    ax1.grid(True)

    # Ax2: Loss
    ax2.plot(steps_range, dense_losses, "b--", label="Dense Loss")
    ax2.plot(steps_range, uet_losses, "r-", label="UET Loss")
    ax2.set_title("Performance: Accuracy Cost")
    ax2.set_xlabel("Training Steps")
    ax2.set_ylabel("Loss (Log Scale)")
    ax2.set_yscale("log")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig(result_dir / "benchmark_evolution.png")
    print(f"\n[Viz] Saved: {result_dir / 'benchmark_evolution.png'}")

    print(f"{'Metric':<20} | {'Dense (Llama-3)':<15} | {'UET (DeepSeek)':<15}")
    print("-" * 60)
    print(
        f"{'Final Loss':<20} | {final_dense_loss:.4f}          | {final_uet_loss:.4f}"
    )
    print(
        f"{'Active Params':<20} | {final_dense_ratio*100:.1f}%           | {final_uet_ratio*100:.1f}%"
    )

    # Unity Score = 1 / (Loss * Active_Ratio)
    dense_unity = 1.0 / (final_dense_loss * final_dense_ratio)
    uet_unity = 1.0 / (final_uet_loss * final_uet_ratio)

    print(f"{'Unity Score':<20} | {dense_unity:.2f}            | {uet_unity:.2f}")

    print("-" * 60)
    if uet_unity > dense_unity * 10:
        print("WINNER: UET Engine dominates via Efficiency.")
    elif final_uet_loss > final_dense_loss * 2:
        print("WINNER: Dense Engine wins on pure quality (Loss).")
    else:
        print("DRAW: Trade-offs are balanced.")

    return True


if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)
