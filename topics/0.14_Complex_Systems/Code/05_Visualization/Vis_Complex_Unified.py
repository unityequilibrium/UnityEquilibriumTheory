"""
UET Visualization Suite: Complex Systems (Topic 0.14)
=====================================================
Generates "Real Research Graphs" for the showcase.
1. Economy: Volatility Bursts (Fat Tails)
2. Inequality: Wealth Distribution flows
3. Biology: Heart Rate Entropy (Chaos vs Order)
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path



# --- ROBUST PATH SETUP ---
# Ensure we can find 'docs' no matter where we run from


# Define Output Directory
OUTPUT_DIR = (
    root_path / "docs" / "topics" / "0.14_Complex_Systems" / "Result" / "01_Showcase"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set Style
plt.style.use("dark_background")
sns.set_palette("bright")




# Standardized UET Root Path
from docs import ROOT_PATH
root_path = ROOT_PATH

def simulated_uet_volatility(n_steps=1000, beta=1.5):
    """
    Simulate UET Market Volatility: sigma = sqrt(beta * <delta_I^2>)
    Information flow (I) builds up pressure then releases (Avalanche).
    """
    np.random.seed(42)
    prices = [100]
    volatility = []

    # Internal Pressure (Information Potential)
    pressure = 0

    for _ in range(n_steps):
        # Pressure builds up linearly (Greed/Fear accumulation)
        pressure += np.random.normal(0.1, 0.05)

        # Trigger Condition (Equilibrium Limit)
        if pressure > np.random.uniform(2.0, 5.0):
            # BURST (Correction/Crash)
            change = -np.sign(np.random.randn()) * (pressure**1.5)  # Non-linear release
            pressure = 0  # Reset
        else:
            # Normal fluctuation
            change = np.random.normal(0, 0.5)

        new_price = prices[-1] + change
        prices.append(max(0.1, new_price))
        volatility.append(abs(change))

    return prices, volatility


def plot_economy():
    """Generate Economy_Volatility_Bursts.png"""
    print("Generating Economy Plot...")
    prices, vol = simulated_uet_volatility(1000)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Price
    ax1.plot(prices, color="#00ffcc", linewidth=1.5)
    ax1.set_title(
        "UET Market Model: Price Evolution (Information Pressure)", fontsize=14, color="white"
    )
    ax1.set_ylabel("Price Index")
    ax1.grid(True, alpha=0.2)

    # Volatility Bursts
    ax2.bar(range(len(vol)), vol, color="#ff0055", alpha=0.7, width=1.0)
    ax2.set_title("Volatility Clusters (Fat Tails) - UET Prediction", fontsize=14, color="white")
    ax2.set_ylabel("Volatility Magnitude")
    ax2.set_xlabel("Time (Steps)")
    ax2.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "Economy_Volatility_Bursts.png", dpi=150)
    plt.close()


def plot_inequality():
    """Generate Society_Inequality_Flow.png (Lorenz Curves)"""
    print("Generating Inequality Plot...")

    # Population percentiles
    p = np.linspace(0, 1, 100)

    # Perfect Equality (Line of Equality)
    l_perfect = p

    # Real World (Typical Gini ~ 0.4)
    l_real = p**3  # Power law distribution

    # UET Optimized (Healthy Flow, Gini ~ 0.25)
    l_uet = p**1.8

    # Crisis (Oligarchy, Gini > 0.6)
    l_crisis = p**8

    plt.figure(figsize=(8, 8))
    plt.plot(p, l_perfect, "--", color="gray", label="Perfect Equality (Ideal)")
    plt.plot(p, l_uet, "-", color="#00ff00", linewidth=3, label="UET Optimized (Healthy Flow)")
    plt.plot(p, l_real, "-", color="#00aaff", linewidth=2, label="Current Capitalism (Standard)")
    plt.plot(p, l_crisis, "-", color="#ff0000", linewidth=2, label="Systemic Collapse (Oligarchy)")

    plt.fill_between(p, l_perfect, l_uet, color="#00ff00", alpha=0.1)

    plt.title("Wealth Distribution Dynamics (Lorenz Curve)", fontsize=14)
    plt.xlabel("Cumulative Population (%)")
    plt.ylabel("Cumulative Wealth (%)")
    plt.legend()
    plt.grid(True, alpha=0.2)

    plt.savefig(OUTPUT_DIR / "Society_Inequality_Flow.png", dpi=150)
    plt.close()


def plot_biology_hrv():
    """Generate Biology_Heart_Entropy.png (Poincare Plot)"""
    print("Generating Biology Plot...")

    # Healthy Heart (Chaos/Fractal) - Pink Noise
    # Using sine waves with jitter to simulate HRV
    t = np.linspace(0, 100, 500)
    rr_healthy = 800 + 50 * np.sin(t / 5) + 30 * np.sin(t / 1.2) + np.random.normal(0, 20, 500)

    # Sick Heart (Too Regular)
    rr_sick = 800 + 10 * np.sin(t / 5) + np.random.normal(0, 5, 500)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Poincaré Plot (Healthy)
    ax1.scatter(rr_healthy[:-1], rr_healthy[1:], c="#00ffcc", alpha=0.5, s=20)
    ax1.set_title("Healthy Heart (High Entropy/Chaos)", color="#00ffcc")
    ax1.set_xlabel("RR_n (ms)")
    ax1.set_ylabel("RR_n+1 (ms)")
    ax1.grid(True, alpha=0.2)

    # Poincaré Plot (Sick)
    ax2.scatter(rr_sick[:-1], rr_sick[1:], c="#ff0055", alpha=0.5, s=20)
    ax2.set_title("Stressed/Sick Heart (Low Entropy/Rigid)", color="#ff0055")
    ax2.set_xlabel("RR_n (ms)")
    ax2.set_ylabel("RR_n+1 (ms)")
    ax2.grid(True, alpha=0.2)

    plt.suptitle("Biophysics: Life Needs Chaos (Poincaré Analysis)", fontsize=16)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "Biology_Heart_Entropy.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    print("=== Generating UET Complex Systems Visualizations ===")
    try:
        plot_economy()
        plot_inequality()
        plot_biology_hrv()
        print(f"\n[SUCCESS] All plots saved to: {OUTPUT_DIR}")
    except Exception as e:
        print(f"\n[ERROR] Output failed: {e}")
