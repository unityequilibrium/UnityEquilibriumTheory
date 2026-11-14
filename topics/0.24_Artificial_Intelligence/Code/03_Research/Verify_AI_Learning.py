"""
Verify_AI_Learning.py
=====================
Grand Production Upscale: Verification of Topic 0.24.
Checks if UET Cortex Engine (V4.0) can actually learn Non-Linear Logic (XOR)
via Gradient Descent with Entropy Regularization.

Target:
    1. Loss Convergence (< 0.1)
    2. XOR Accuracy (100%)
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
from pathlib import Path
from docs import ROOT_PATH

root_path = ROOT_PATH

# --- ROBUST PATH FINDER ---


# Local Engine Import
engine_dir = root_path / "docs/topics/0.24_Artificial_Intelligence/Code/01_Engine"
if str(engine_dir) not in sys.path:
    sys.path.insert(0, str(engine_dir))

from UET_AI_Core import UetcortexNeuralNet
from docs.core.uet_parameters import UETParameters


# Standardized UET Root Path


def run_verification():
    print("🧠 UET CORTEX AI: PRODUCTION VERIFICATION")
    print("=========================================")
    print("Target: XOR Logic Gate (Non-Linear Learning)\n")

    # 1. Setup Data (XOR)
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y = np.array([[0], [1], [1], [0]])  # XOR Truth Table

    # 2. Initialize Engine (Entropy Pressure = 0.001 to allow learning)
    params = UETParameters(kappa=0.1, beta=0.001)
    net = UetcortexNeuralNet(input_size=2, hidden_size=6, output_size=1, params=params)

    print("  [1] Training (Backpropagation)...")
    epochs = 5000
    for i in range(epochs):
        loss = net.train_step(X, y, learning_rate=0.5)
        if i % 1000 == 0:
            print(f"      Epoch {i}: Loss = {loss:.5f}")

    final_loss = net.loss_history[-1]
    print(f"      Final Loss: {final_loss:.5f}")

    # 3. Verify Predictions
    print("\n  [2] Testing Predictions")
    preds = net.forward(X)
    rounded = np.round(preds)

    # Accuracy
    accuracy = np.mean(rounded == y) * 100

    for i in range(4):
        print(f"      Input {X[i]} -> Pred {preds[i][0]:.4f} (Target {y[i][0]})")

    print(f"\n      Accuracy: {accuracy:.2f}%")

    if accuracy == 100.0 and final_loss < 0.1:
        print("\n✅ STATUS: SUCCESS (Genuine Gradient Descent Confirmed)")
        print("   The network learned the XOR function from scratch.")
    else:
        print("\n❌ STATUS: FAILED (Did not converge)")


if __name__ == "__main__":
    run_verification()
