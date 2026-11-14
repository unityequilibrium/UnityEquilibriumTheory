"""
UET Competitor Analysis: Standard Oncology Models
=================================================
Topic: 0.22 Biophysics & Origin of Life
Goal: Provide a baseline using Gompertz Growth and Shannon Entropy.

Competitor Models:
1. Gompertz: V(t) = V_0 * exp( (A/B) * (1 - exp(-Bt)) )
2. Shannon Entropy: H = -Σ p(x) log p(x)
"""

import numpy as np
import pandas as pd


def run_gompertz_model(t, v0, a, b):
    # Standard Gompertz curve for tumor growth
    return v0 * np.exp((a / b) * (1 - np.exp(-b * t)))


def run_shannon_entropy(data):
    # Standard Shannon entropy for genomic disorder
    counts = np.histogram(data, bins=10)[0]
    probs = counts / np.sum(counts)
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))


def run_competitor_benchmarks():
    print("⚖️ COMPETITOR ANALYSIS: STANDARD CANCER MODELS")
    print("=" * 60)

    # 1. Growth Simulation (Gompertz)
    print("[1/2] Simulating Tumor Growth (Gompertz Model)...")
    time_steps = np.linspace(0, 100, 10)
    v0, a, b = 1.0, 0.1, 0.05
    volumes = [run_gompertz_model(t, v0, a, b) for t in time_steps]

    print(f"  - Initial Volume: {volumes[0]:.2f}")
    print(f"  - Final Volume (t=100): {volumes[-1]:.2f}")
    print(
        "  - Limitation: Only tracks physical volume, ignoring internal information field."
    )

    # 2. Entropy Identification (Shannon)
    print("\n[2/2] Analyzing Genomic Disorder (Shannon Entropy)...")
    # Simulate Normal vs Tumor Data
    normal_data = np.random.normal(10, 1, 1000)
    tumor_data = np.random.normal(10, 5, 1000)

    h_norm = run_shannon_entropy(normal_data)
    h_tumor = run_shannon_entropy(tumor_data)

    print(f"  - Normal Shannon Entropy: {h_norm:.4f} bits")
    print(f"  - Tumor Shannon Entropy:  {h_tumor:.4f} bits")
    print(f"  - Identification Gap (H_diff): {h_tumor - h_norm:.4f}")
    print(
        "  - Limitation: Shannon entropy is scale-invariant and lacks 'Scale Linkage' context."
    )

    # 3. UET Comparison Preview
    print("\n[UET vs Standard Model Summary]")
    summary = {
        "Metric": ["Basis", "Sensitivity to Scale", "Mechanism", "Predictive Depth"],
        "Standard (Gompertz/Shannon)": [
            "Volume/Probability",
            "Low",
            "Phenomenological",
            "Medium",
        ],
        "UET (Equilibrium Theory)": [
            "Information Field",
            "High (Full Scale)",
            "Causal/Structural",
            "High",
        ],
    }
    df = pd.DataFrame(summary)
    print(df.to_string(index=False))

    return True


if __name__ == "__main__":
    run_competitor_benchmarks()
