#!/usr/bin/env python
"""
UET KPI Dashboard - Backend
Balanced Scorecard tracker using UET field dynamics.

Usage:
    python scripts/run_kpi_dashboard.py --input data/sample_kpi.csv
    python scripts/run_kpi_dashboard.py --input data/my_kpis.csv --out dashboard
"""
from __future__ import annotations
import argparse
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation


def load_kpi_data(csv_path: Path) -> pd.DataFrame:
    """
    Load KPI data from CSV.
    
    Expected columns:
    - date: YYYY-MM-DD
    - revenue: Financial metric
    - customer_sat: Customer satisfaction (0-100)
    - process_eff: Process efficiency (0-100)
    - innovation: Innovation index (0-100)
    """
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    return df.sort_values('date')


def create_kpi_fields(df: pd.DataFrame, N: int = 32) -> tuple:
    """
    Convert KPI time series to 2D fields.
    
    Grid: departments/sectors (rows) × time periods (cols)
    """
    n_periods = len(df)
    
    # Normalize to [-1, 1] range
    def normalize(series):
        mean = series.mean()
        std = series.std() if series.std() > 0 else 1
        return (series - mean) / (std * 2)
    
    # Create fields
    C_base = normalize(df['revenue']).values
    I_base = normalize(df['customer_sat']).values
    
    # Expand to 2D (simulate different departments)
    C0 = np.zeros((N, N))
    I0 = np.zeros((N, N))
    
    # Fill with variations (simulate sector differences)
    for i in range(N):
        for j in range(N):
            # Add spatial variation
            noise_c = np.random.randn() * 0.1
            noise_i = np.random.randn() * 0.1
            
            # Use latest value as base
            C0[i, j] = C_base[-1] + noise_c
            I0[i, j] = I_base[-1] + noise_i
    
    return C0, I0, df


def compute_kpi_metrics(C: np.ndarray, I: np.ndarray, df: pd.DataFrame) -> dict:
    """Compute KPI-specific metrics."""
    # Balance score (Ω-like)
    balance = float(np.mean((C - I)**2))
    
    # Health score (how close to optimal)
    health = float(100 * (1 - min(balance, 1)))
    
    # Coupling strength
    coupling = float(np.corrcoef(C.flatten(), I.flatten())[0, 1])
    
    # Trend (derivative)
    c_mean = float(np.mean(C))
    i_mean = float(np.mean(I))
    
    return {
        "balance_score": balance,
        "health_score": health,
        "coupling": coupling,
        "revenue_level": c_mean,
        "customer_level": i_mean,
    }


def run_kpi_simulation(C0: np.ndarray, I0: np.ndarray, df: pd.DataFrame,
                       config: dict, n_snapshots: int = 60):
    """Run KPI evolution simulation."""
    N = C0.shape[0]
    L = config.get("L", 10.0)
    T = config.get("T", 3.0)
    dt = config.get("dt", 0.02)
    beta = config.get("beta", 0.6)
    kappa = config.get("kappa", 0.3)
    
    # Extract forcing from innovation metric
    innovation_norm = (df['innovation'].values[-1] - 50) / 50  # -1 to 1
    s_strength = innovation_norm * 0.5
    
    n_steps = int(T / dt)
    snapshot_every = max(1, n_steps // n_snapshots)
    
    C = C0.copy()
    I = I0.copy()
    s = np.ones((N, N)) * s_strength  # Innovation forcing
    
    # Histories
    C_history = [C.copy()]
    I_history = [I.copy()]
    t_history = [0.0]
    metrics_history = [compute_kpi_metrics(C, I, df)]
    
    print(f"  Running KPI simulation: {N}×{N} grid, {n_steps} steps...")
    
    for step in range(1, n_steps + 1):
        t = step * dt
        
        # Laplacian (cross-department influence)
        def laplacian(f):
            return (
                np.roll(f, 1, axis=0) + np.roll(f, -1, axis=0) +
                np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1) - 4*f
            ) * (N / L)**2
        
        lapC = laplacian(C)
        lapI = laplacian(I)
        
        # UET dynamics for KPIs
        dC = kappa * lapC - C * (C**2 - 1) - beta * (C - I) + s
        dI = kappa * lapI - I * (I**2 - 1) - beta * (I - C) * 0.5
        
        C = C + dt * dC
        I = I + dt * dI
        
        # Decay forcing
        s = s * 0.98
        
        # Clip
        C = np.clip(C, -2, 2)
        I = np.clip(I, -2, 2)
        
        if step % snapshot_every == 0:
            C_history.append(C.copy())
            I_history.append(I.copy())
            t_history.append(t)
            metrics_history.append(compute_kpi_metrics(C, I, df))
    
    return {
        "C": C_history,
        "I": I_history,
        "t": t_history,
        "metrics": metrics_history,
        "kpi_data": df,
    }


def make_kpi_animation(output_dir: Path, history: dict, fps: int = 12) -> Path:
    """Create KPI dashboard animation."""
    C_history = history["C"]
    I_history = history["I"]
    t_history = history["t"]
    metrics = history["metrics"]
    
    n_frames = len(C_history)
    c_lim = 1.5
    
    fig = plt.figure(figsize=(16, 9))
    
    def update(frame):
        fig.clear()
        
        C = C_history[frame]
        I = I_history[frame]
        t = t_history[frame]
        m = metrics[frame]
        
        # Layout: 2x3 grid
        ax1 = fig.add_subplot(231)  # Financial field
        ax2 = fig.add_subplot(232)  # Customer field
        ax3 = fig.add_subplot(233)  # Metrics
        ax4 = fig.add_subplot(234)  # Balance over time
        ax5 = fig.add_subplot(235)  # Health over time
        ax6 = fig.add_subplot(236)  # Coupling
        
        # Financial field
        im1 = ax1.imshow(C, cmap='RdYlGn', vmin=-c_lim, vmax=c_lim)
        ax1.set_title('💰 Financial Performance', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Sub-units')
        ax1.set_ylabel('Departments')
        plt.colorbar(im1, ax=ax1, shrink=0.7)
        
        # Customer field
        im2 = ax2.imshow(I, cmap='YlGnBu', vmin=-c_lim, vmax=c_lim)
        ax2.set_title('😊 Customer Satisfaction', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Sub-units')
        ax2.set_ylabel('Departments')
        plt.colorbar(im2, ax=ax2, shrink=0.7)
        
        # Current metrics (gauges)
        ax3.axis('off')
        metrics_text = f"""
        ⚖️ Balance Score: {m['balance_score']:.2f}
        
        🎯 Health Score: {m['health_score']:.1f}%
        
        🔗 Coupling: {m['coupling']:.2f}
        
        📈 Revenue Level: {m['revenue_level']:+.2f}
        
        😊 Customer Level: {m['customer_level']:+.2f}
        """
        ax3.text(0.1, 0.5, metrics_text, fontsize=14, 
                verticalalignment='center', family='monospace')
        ax3.set_title('📊 Current Metrics', fontsize=12, fontweight='bold')
        
        # Balance score over time
        balance_vals = [m['balance_score'] for m in metrics[:frame+1]]
        ax4.plot(t_history[:frame+1], balance_vals, 'b-', lw=2)
        ax4.fill_between(t_history[:frame+1], 0, balance_vals, alpha=0.3)
        ax4.set_xlim(0, t_history[-1])
        ax4.set_ylim(0, max(balance_vals) * 1.2 if balance_vals else 1)
        ax4.set_xlabel('Time')
        ax4.set_ylabel('Balance Score')
        ax4.set_title('⚖️ Balance Score (Lower = Better)', fontsize=11)
        ax4.grid(True, alpha=0.3)
        
        # Health score over time
        health_vals = [m['health_score'] for m in metrics[:frame+1]]
        ax5.plot(t_history[:frame+1], health_vals, 'g-', lw=2)
        ax5.fill_between(t_history[:frame+1], 0, health_vals, color='green', alpha=0.3)
        ax5.set_xlim(0, t_history[-1])
        ax5.set_ylim(0, 100)
        ax5.set_xlabel('Time')
        ax5.set_ylabel('Health %')
        ax5.set_title('🎯 Organization Health', fontsize=11)
        ax5.grid(True, alpha=0.3)
        
        # Coupling strength
        coupling_vals = [m['coupling'] for m in metrics[:frame+1]]
        ax6.plot(t_history[:frame+1], coupling_vals, 'purple', lw=2)
        ax6.axhline(0, color='gray', lw=0.5)
        ax6.set_xlim(0, t_history[-1])
        ax6.set_ylim(-1, 1)
        ax6.set_xlabel('Time')
        ax6.set_ylabel('Coupling')
        ax6.set_title('🔗 Revenue-Customer Coupling', fontsize=11)
        ax6.grid(True, alpha=0.3)
        
        fig.suptitle(f'🎯 UET KPI Dashboard | t = {t:.2f}', 
                     fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    output_path = output_dir / "kpi_evolution.gif"
    print(f"  Saving KPI animation...")
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close(fig)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def generate_predictions(history: dict, horizon: int = 10) -> dict:
    """Generate simple predictions based on trends."""
    metrics = history["metrics"]
    
    # Extract recent trends
    recent = metrics[-10:]
    
    balance_trend = np.mean(np.diff([m['balance_score'] for m in recent]))
    health_trend = np.mean(np.diff([m['health_score'] for m in recent]))
    
    predictions = {
        "balance_forecast": "increasing" if balance_trend > 0.01 else "stable" if abs(balance_trend) < 0.01 else "improving",
        "health_forecast": "improving" if health_trend > 1 else "stable" if abs(health_trend) < 1 else "declining",
        "warnings": []
    }
    
    # Generate warnings
    if balance_trend > 0.05:
        predictions["warnings"].append("⚠️ Balance score increasing - organization becoming less aligned")
    if health_trend < -2:
        predictions["warnings"].append("⚠️ Health declining - intervention needed")
    if metrics[-1]['coupling'] < 0.3:
        predictions["warnings"].append("⚠️ Low coupling - revenue not aligned with customer satisfaction")
    
    if not predictions["warnings"]:
        predictions["warnings"].append("✅ All metrics healthy")
    
    return predictions


def save_dashboard_data(output_dir: Path, history: dict, predictions: dict):
    """Save data for HTML dashboard."""
    metrics = history["metrics"]
    t = history["t"]
    
    # Convert DataFrame to dict with date as string
    kpi_records = history["kpi_data"].copy()
    kpi_records['date'] = kpi_records['date'].dt.strftime('%Y-%m-%d')
    
    dashboard_data = {
        "timestamp": datetime.now().isoformat(),
        "current": metrics[-1],
        "history": {
            "time": t,
            "balance": [m['balance_score'] for m in metrics],
            "health": [m['health_score'] for m in metrics],
            "coupling": [m['coupling'] for m in metrics],
        },
        "predictions": predictions,
        "kpi_data": kpi_records.to_dict('records'),
    }
    
    output_path = output_dir / "dashboard_data.json"
    with open(output_path, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"  ✅ Saved: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="UET KPI Dashboard")
    parser.add_argument("--input", required=True, help="Input CSV file with KPI data")
    parser.add_argument("--out", default="kpi_dashboard", help="Output directory")
    parser.add_argument("--N", type=int, default=32, help="Grid size")
    parser.add_argument("--T", type=float, default=3.0, help="Simulation time")
    
    args = parser.parse_args()
    
    print("🎯 UET KPI Dashboard - Backend")
    print("=" * 50)
    
    # Load data
    print(f"\n📊 Loading KPI data from {args.input}...")
    df = load_kpi_data(Path(args.input))
    print(f"  Loaded {len(df)} time periods")
    print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Create output directory
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize fields
    print(f"\n🔧 Initializing {args.N}×{args.N} fields...")
    C0, I0, df = create_kpi_fields(df, N=args.N)
    
    # Run simulation
    config = {
        "L": 10.0,
        "T": args.T,
        "dt": 0.02,
        "beta": 0.6,
        "kappa": 0.3,
    }
    
    print(f"\n🚀 Running simulation...")
    history = run_kpi_simulation(C0, I0, df, config)
    
    # Generate predictions
    print(f"\n🔮 Generating predictions...")
    predictions = generate_predictions(history)
    
    # Create visualizations
    print(f"\n🎨 Creating visualizations...")
    make_kpi_animation(output_dir, history)
    
    # Save data
    print(f"\n💾 Saving dashboard data...")
    save_dashboard_data(output_dir, history, predictions)
    
    # Summary
    print("\n" + "=" * 50)
    print("✅ KPI Dashboard Backend Complete!")
    print(f"\nOutput directory: {output_dir}")
    print(f"  - kpi_evolution.gif (animation)")
    print(f"  - dashboard_data.json (data for frontend)")
    
    print(f"\n📊 Current Status:")
    current = history["metrics"][-1]
    print(f"  Balance Score: {current['balance_score']:.2f}")
    print(f"  Health Score: {current['health_score']:.1f}%")
    print(f"  Coupling: {current['coupling']:.2f}")
    
    print(f"\n🔮 Predictions:")
    for warning in predictions["warnings"]:
        print(f"  {warning}")
    
    print(f"\nNext: Create HTML dashboard to visualize this data")


if __name__ == "__main__":
    main()
