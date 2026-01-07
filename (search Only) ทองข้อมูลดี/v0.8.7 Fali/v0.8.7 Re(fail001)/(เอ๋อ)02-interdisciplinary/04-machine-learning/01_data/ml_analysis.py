#!/usr/bin/env python3
"""
🤖 MACHINE LEARNING: F = -∇Loss Analysis
==========================================

Tests the gradient flow hypothesis on real neural network training:
- SGD dynamics as gradient descent on loss landscape
- Training curves as energy minimization

Hypothesis: θ(t+1) - θ(t) = -η ∇L(θ)

Note: This is trivially true BY DEFINITION for SGD.
We generate real training logs to demonstrate and verify.

Author: GDS Research Team
Date: 2025-12-28
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from dataclasses import dataclass
from typing import List, Tuple
import json

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(__file__).parent
RESULTS_DIR = DATA_DIR.parent / "results"
FIGURES_DIR = DATA_DIR.parent / "figures"


@dataclass
class TrainingResult:
    """Result from analyzing training dynamics."""

    model_name: str
    dataset: str
    n_epochs: int
    n_params: int
    correlation: float
    p_value: float
    final_loss: float
    loss_decrease: float
    consistent: bool

    def to_dict(self):
        return {
            "model_name": self.model_name,
            "dataset": self.dataset,
            "n_epochs": int(self.n_epochs),
            "n_params": int(self.n_params),
            "correlation": float(self.correlation),
            "p_value": float(self.p_value),
            "final_loss": float(self.final_loss),
            "loss_decrease": float(self.loss_decrease),
            "consistent": bool(self.consistent),
        }


def create_simple_neural_network(input_dim: int, hidden_dim: int, output_dim: int):
    """Create a simple 2-layer neural network."""
    np.random.seed(42)

    # Xavier initialization
    W1 = np.random.randn(input_dim, hidden_dim) * np.sqrt(2.0 / input_dim)
    b1 = np.zeros(hidden_dim)
    W2 = np.random.randn(hidden_dim, output_dim) * np.sqrt(2.0 / hidden_dim)
    b2 = np.zeros(output_dim)

    return {"W1": W1, "b1": b1, "W2": W2, "b2": b2}


def forward(params, X):
    """Forward pass."""
    h = np.maximum(0, X @ params["W1"] + params["b1"])  # ReLU
    out = h @ params["W2"] + params["b2"]
    return out, h


def compute_loss(params, X, y):
    """MSE loss."""
    pred, _ = forward(params, X)
    return np.mean((pred - y) ** 2)


def compute_gradients(params, X, y):
    """Compute gradients via backprop."""
    m = X.shape[0]
    pred, h = forward(params, X)

    # Output layer gradients
    d_out = 2 * (pred - y) / m
    dW2 = h.T @ d_out
    db2 = np.sum(d_out, axis=0)

    # Hidden layer gradients
    d_hidden = d_out @ params["W2"].T
    d_hidden[h <= 0] = 0  # ReLU derivative
    dW1 = X.T @ d_hidden
    db1 = np.sum(d_hidden, axis=0)

    return {"W1": dW1, "b1": db1, "W2": dW2, "b2": db2}


def flatten_params(params):
    """Flatten parameter dict to vector."""
    return np.concatenate([p.flatten() for p in params.values()])


def flatten_grads(grads):
    """Flatten gradient dict to vector."""
    return np.concatenate([g.flatten() for g in grads.values()])


def train_and_analyze(
    X_train,
    y_train,
    hidden_dim: int = 32,
    n_epochs: int = 100,
    learning_rate: float = 0.01,
    model_name: str = "MLP",
    dataset_name: str = "synthetic",
) -> TrainingResult:
    """Train network and analyze gradient flow."""

    print(f"\n🤖 Training {model_name} on {dataset_name}...")

    input_dim = X_train.shape[1]
    output_dim = y_train.shape[1] if len(y_train.shape) > 1 else 1
    if len(y_train.shape) == 1:
        y_train = y_train.reshape(-1, 1)

    params = create_simple_neural_network(input_dim, hidden_dim, output_dim)
    n_params = sum(p.size for p in params.values())

    print(f"   Parameters: {n_params}")

    # Training loop
    losses = []
    all_grads_norm = []
    all_updates_norm = []

    for epoch in range(n_epochs):
        # Compute loss and gradients
        loss = compute_loss(params, X_train, y_train)
        grads = compute_gradients(params, X_train, y_train)

        losses.append(loss)

        # Flatten for analysis
        grad_vec = flatten_grads(grads)
        update_vec = -learning_rate * grad_vec

        all_grads_norm.append(np.linalg.norm(grad_vec))
        all_updates_norm.append(np.linalg.norm(update_vec))

        # Update parameters
        for key in params:
            params[key] -= learning_rate * grads[key]

    # Analyze gradient flow
    grads_norm = np.array(all_grads_norm)
    updates_norm = np.array(all_updates_norm)

    # Test: updates should be proportional to gradients
    corr, p_value = stats.pearsonr(grads_norm, updates_norm)

    # Loss should decrease
    loss_decrease = (losses[0] - losses[-1]) / losses[0]
    consistent = (corr > 0.99) and (loss_decrease > 0)

    print(f"   Initial loss: {losses[0]:.4f}")
    print(f"   Final loss: {losses[-1]:.4f}")
    print(f"   Loss decrease: {loss_decrease:.1%}")
    print(f"   Correlation (|update| vs |∇L|): {corr:.4f}")
    print(f"   Consistent with θ' = -η∇L: {'✅ YES' if consistent else '❌ NO'}")

    return (
        TrainingResult(
            model_name=model_name,
            dataset=dataset_name,
            n_epochs=n_epochs,
            n_params=n_params,
            correlation=corr,
            p_value=p_value,
            final_loss=losses[-1],
            loss_decrease=loss_decrease,
            consistent=consistent,
        ),
        losses,
    )


def generate_synthetic_data(n_samples: int, input_dim: int, noise: float = 0.1):
    """Generate synthetic regression data."""
    np.random.seed(42)
    X = np.random.randn(n_samples, input_dim)
    true_w = np.random.randn(input_dim)
    y = X @ true_w + noise * np.random.randn(n_samples)
    return X, y


def run_full_analysis():
    """Run ML gradient flow analysis."""

    print("\n" + "🤖" * 30)
    print("   MACHINE LEARNING: F = -∇L ANALYSIS")
    print("🤖" * 30)

    results = []
    all_losses = {}

    # Test 1: Linear regression
    X, y = generate_synthetic_data(500, 10, noise=0.1)
    result, losses = train_and_analyze(
        X,
        y,
        hidden_dim=16,
        n_epochs=200,
        learning_rate=0.01,
        model_name="MLP-Small",
        dataset_name="Linear-10D",
    )
    results.append(result)
    all_losses["MLP-Small"] = losses

    # Test 2: Nonlinear function
    np.random.seed(43)
    X = np.random.randn(500, 5)
    y = np.sin(X[:, 0]) + np.cos(X[:, 1]) + 0.1 * np.random.randn(500)
    result, losses = train_and_analyze(
        X,
        y,
        hidden_dim=32,
        n_epochs=300,
        learning_rate=0.005,
        model_name="MLP-Medium",
        dataset_name="Nonlinear-5D",
    )
    results.append(result)
    all_losses["MLP-Medium"] = losses

    # Test 3: High-dimensional
    X, y = generate_synthetic_data(1000, 50, noise=0.5)
    result, losses = train_and_analyze(
        X,
        y,
        hidden_dim=64,
        n_epochs=200,
        learning_rate=0.001,
        model_name="MLP-Large",
        dataset_name="Linear-50D",
    )
    results.append(result)
    all_losses["MLP-Large"] = losses

    # Test 4: Classification (binary)
    np.random.seed(44)
    X = np.random.randn(500, 20)
    y = (X[:, 0] + X[:, 1] > 0).astype(float)
    result, losses = train_and_analyze(
        X,
        y,
        hidden_dim=32,
        n_epochs=150,
        learning_rate=0.01,
        model_name="MLP-Classifier",
        dataset_name="Binary-20D",
    )
    results.append(result)
    all_losses["MLP-Classifier"] = losses

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY: θ' = -η∇L Test")
    print("=" * 70)

    print(
        f"\n{'Model':<20} {'Dataset':<15} {'Params':<10} {'Corr':<10} {'Loss↓':<10} {'F=-∇L?':<10}"
    )
    print("-" * 75)

    n_consistent = 0
    for r in results:
        status = "✅ YES" if r.consistent else "❌ NO"
        if r.consistent:
            n_consistent += 1
        print(
            f"{r.model_name:<20} {r.dataset:<15} {r.n_params:<10} {r.correlation:>+.4f}   {r.loss_decrease:>6.1%}   {status}"
        )

    print("-" * 75)
    print(f"\n✅ {n_consistent}/{len(results)} experiments CONSISTENT with θ' = -η∇L")

    # Note about triviality
    print("\n⚠️  NOTE: This is trivially true BY DESIGN of SGD!")
    print("   SGD update rule IS θ' = θ - η∇L")
    print("   We're just verifying implementation correctness.")

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results_dict = {
        "experiments": [r.to_dict() for r in results],
        "summary": {
            "total": len(results),
            "consistent": n_consistent,
            "note": "SGD is gradient descent by definition",
        },
    }

    output_json = RESULTS_DIR / "ml_analysis.json"
    with open(output_json, "w") as f:
        json.dump(results_dict, f, indent=2)

    print(f"\n📄 Results saved: {output_json}")

    # Create figure
    create_summary_figure(results, all_losses)

    return results


def create_summary_figure(results: List[TrainingResult], all_losses: dict):
    """Create summary visualization."""

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Training curves
    ax = axes[0]
    for name, losses in all_losses.items():
        ax.plot(losses, label=name, alpha=0.8)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("Training Curves (Loss Minimization)")
    ax.set_yscale("log")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: Loss decrease by model
    ax = axes[1]
    names = [r.model_name for r in results]
    decreases = [r.loss_decrease * 100 for r in results]
    colors = ["green" if r.consistent else "red" for r in results]

    ax.bar(range(len(results)), decreases, color=colors, alpha=0.7)
    ax.set_xticks(range(len(results)))
    ax.set_xticklabels(names, rotation=45, ha="right")
    ax.set_ylabel("Loss Decrease (%)")
    ax.set_title("SGD Optimization Performance")
    ax.axhline(0, color="black", linestyle="--")

    plt.suptitle("Machine Learning: Gradient Descent Analysis", fontsize=14, fontweight="bold")
    plt.tight_layout()

    output = FIGURES_DIR / "ml_analysis.png"
    plt.savefig(output, dpi=150, bbox_inches="tight")
    print(f"📊 Figure saved: {output}")
    plt.close()


if __name__ == "__main__":
    run_full_analysis()
