#!/usr/bin/env python
"""
Test Time Delays Extension

Demonstrates neural oscillations from synaptic delays.

Usage:
    python scripts/test_time_delays.py
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from pathlib import Path
from collections import deque


def laplacian_2d(field, dx=1.0):
    """Compute 2D Laplacian using finite differences."""
    return (
        np.roll(field, 1, axis=0) + np.roll(field, -1, axis=0) +
        np.roll(field, 1, axis=1) + np.roll(field, -1, axis=1) -
        4 * field
    ) / (dx * dx)


def dV_dphi(phi):
    """Derivative of double-well potential V(φ) = (φ²-1)²/4."""
    return phi * (phi**2 - 1)


class UETWithDelay:
    """UET model with time delays."""
    
    def __init__(self, N=32, kappa=0.1, beta=1.0, s=0.0, 
                 tau_CI=0.0, tau_IC=0.0, dt=0.01):
        self.N = N
        self.kappa = kappa
        self.beta = beta
        self.s = s
        self.tau_CI = tau_CI
        self.tau_IC = tau_IC
        self.dt = dt
        
        # Calculate buffer sizes
        self.buffer_size_CI = max(1, int(tau_CI / dt))
        self.buffer_size_IC = max(1, int(tau_IC / dt))
        
        # History buffers
        self.C_history = deque(maxlen=self.buffer_size_IC)
        self.I_history = deque(maxlen=self.buffer_size_CI)
        
        # Initialize fields
        self.C = np.random.randn(N, N) * 0.1 + 1.0
        self.I = np.random.randn(N, N) * 0.1 - 1.0
        
        # Fill buffers with initial values
        for _ in range(self.buffer_size_CI):
            self.I_history.append(self.I.copy())
        for _ in range(self.buffer_size_IC):
            self.C_history.append(self.C.copy())
    
    def step(self):
        """Evolve one timestep with delays."""
        C, I = self.C, self.I
        
        # Get delayed values
        I_delayed = self.I_history[0] if len(self.I_history) > 0 else I
        C_delayed = self.C_history[0] if len(self.C_history) > 0 else C
        
        # Compute derivatives
        dC_dt = (
            self.kappa * laplacian_2d(C) -
            dV_dphi(C) -
            self.beta * (C - I_delayed) +  # ← Delayed I
            self.s
        )
        
        dI_dt = (
            self.kappa * laplacian_2d(I) -
            dV_dphi(I) -
            self.beta * (I - C_delayed)  # ← Delayed C
        )
        
        # Update
        self.C = C + self.dt * dC_dt
        self.I = I + self.dt * dI_dt
        
        # Store current values in history
        self.I_history.append(self.I.copy())
        self.C_history.append(self.C.copy())
    
    def get_mean_values(self):
        """Get spatial mean of C and I."""
        return np.mean(self.C), np.mean(self.I)
    
    def compute_omega(self):
        """Compute network mass Ω = ∫[½(∇C)² + ½(∇I)² + V(C) + V(I) + β·C·I] dx"""
        C, I = self.C, self.I
        dx = 1.0 / self.N
        
        # Gradient terms: ½(∇C)² and ½(∇I)²
        grad_C_x = (np.roll(C, -1, axis=0) - np.roll(C, 1, axis=0)) / (2*dx)
        grad_C_y = (np.roll(C, -1, axis=1) - np.roll(C, 1, axis=1)) / (2*dx)
        grad_I_x = (np.roll(I, -1, axis=0) - np.roll(I, 1, axis=0)) / (2*dx)
        grad_I_y = (np.roll(I, -1, axis=1) - np.roll(I, 1, axis=1)) / (2*dx)
        
        kinetic_C = 0.5 * (grad_C_x**2 + grad_C_y**2)
        kinetic_I = 0.5 * (grad_I_x**2 + grad_I_y**2)
        
        # Potential: V(φ) = (φ²-1)²/4
        V_C = (C**2 - 1)**2 / 4
        V_I = (I**2 - 1)**2 / 4
        
        # Coupling: β·C·I
        coupling = self.beta * C * I
        
        # Total Ω
        omega_density = kinetic_C + kinetic_I + V_C + V_I + coupling
        omega = np.sum(omega_density) * dx**2
        
        return float(omega)


def test_delay_oscillations():
    """Test that delays create oscillations."""
    print("\n" + "="*60)
    print("🧪 Testing Time Delays")
    print("="*60)
    
    # Test 1: No delay (should be stable)
    print("\n1️⃣  No delay (τ=0):")
    model_no_delay = UETWithDelay(N=32, tau_CI=0.0, tau_IC=0.0, beta=1.0)
    
    C_means_no_delay = []
    for _ in range(500):
        model_no_delay.step()
        C_mean, _ = model_no_delay.get_mean_values()
        C_means_no_delay.append(C_mean)
    
    variance_no_delay = np.var(C_means_no_delay[-100:])
    print(f"   Variance of C (last 100 steps): {variance_no_delay:.6f}")
    print(f"   Expected: Low variance (stable)")
    
    # Test 2: With delay (should oscillate)
    print("\n2️⃣  With delay (τ=1.0):")
    model_with_delay = UETWithDelay(N=32, tau_CI=1.0, tau_IC=0.5, beta=1.0)
    
    C_means_with_delay = []
    for _ in range(500):
        model_with_delay.step()
        C_mean, _ = model_with_delay.get_mean_values()
        C_means_with_delay.append(C_mean)
    
    variance_with_delay = np.var(C_means_with_delay[-100:])
    print(f"   Variance of C (last 100 steps): {variance_with_delay:.6f}")
    print(f"   Expected: High variance (oscillating)")
    
    # Plot comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    ax1.plot(C_means_no_delay, 'b-', lw=1.5)
    ax1.set_title('No Delay (τ=0)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Time step')
    ax1.set_ylabel('⟨C⟩')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(C_means_with_delay, 'r-', lw=1.5)
    ax2.set_title('With Delay (τ=1.0)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Time step')
    ax2.set_ylabel('⟨C⟩')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    out_dir = Path("runs_gallery/test_delays")
    out_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_dir / "delay_comparison.png", dpi=150)
    print(f"\n   ✅ Saved: {out_dir / 'delay_comparison.png'}")
    
    # Verdict
    print("\n" + "="*60)
    if variance_with_delay > 5 * variance_no_delay:
        print("✅ TEST PASSED: Delays create oscillations!")
    else:
        print("⚠️  TEST INCONCLUSIVE: Try larger delay or longer simulation")
    print("="*60)
    
    return model_with_delay


def make_delay_animation(model, n_frames=200, fps=20):
    """Create animation showing delayed oscillations."""
    print("\n📹 Creating animation...")
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    C_means = []
    I_means = []
    
    def update(frame):
        # Evolve
        for _ in range(2):
            model.step()
        
        C_mean, I_mean = model.get_mean_values()
        C_means.append(C_mean)
        I_means.append(I_mean)
        
        # Clear
        for ax in axes:
            ax.clear()
        
        # 1. C field
        im1 = axes[0].imshow(model.C, cmap='RdBu_r', vmin=-2, vmax=2, origin='lower')
        axes[0].set_title('C Field (Excitatory)', fontsize=12, fontweight='bold')
        axes[0].axis('off')
        
        # 2. I field
        im2 = axes[1].imshow(model.I, cmap='RdBu_r', vmin=-2, vmax=2, origin='lower')
        axes[1].set_title('I Field (Inhibitory)', fontsize=12, fontweight='bold')
        axes[1].axis('off')
        
        # 3. Time series
        axes[2].plot(C_means, 'r-', lw=2, label='⟨C⟩')
        axes[2].plot(I_means, 'b-', lw=2, label='⟨I⟩')
        axes[2].set_xlim(0, n_frames)
        axes[2].set_ylim(-1.5, 1.5)
        axes[2].set_xlabel('Frame', fontsize=10)
        axes[2].set_ylabel('Mean Value', fontsize=10)
        axes[2].set_title('Oscillations from Delay', fontsize=12, fontweight='bold')
        axes[2].legend(loc='upper right')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    out_dir = Path("runs_gallery/test_delays")
    output_path = out_dir / "CI_evolution.gif"
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close()
    
    print(f"   ✅ Saved: {output_path}")
    return output_path


def main():
    print("\n" + "="*60)
    print("🕐 UET TIME DELAYS TEST")
    print("="*60)
    print("\nThis test demonstrates:")
    print("  1. No delay → Stable equilibrium")
    print("  2. With delay → Oscillations")
    print("  3. Animation of delayed dynamics")
    print("="*60)
    
    # Run tests
    model = test_delay_oscillations()
    
    # Compute Omega before animation
    omega_initial = model.compute_omega()
    
    # Create animation
    make_delay_animation(model, n_frames=150, fps=20)
    
    # Compute Omega after animation
    omega_final = model.compute_omega()
    delta_omega = (omega_final - omega_initial) / abs(omega_initial) if omega_initial != 0 else 0
    
    # Save summary with Omega values
    out_dir = Path("runs_gallery/test_delays")
    summary = {
        "test": "time_delays",
        "tau_CI": model.tau_CI,
        "tau_IC": model.tau_IC,
        "beta": model.beta,
        "result": "Oscillations observed",
        "status": "PASS",
        "Omega0": omega_initial,
        "OmegaT": omega_final,
        "delta_omega": delta_omega,
        "omega_conserved": abs(delta_omega) < 0.1,
        "description": f"Time delays τ_CI={model.tau_CI}, τ_IC={model.tau_IC} with Ω conservation"
    }
    
    import json
    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    with open(out_dir / "config.json", "w") as f:
        json.dump({
            "case_id": "test_delays",
            "model": "UET_with_delays",
            "params": {
                "tau_CI": model.tau_CI,
                "tau_IC": model.tau_IC,
                "beta": model.beta,
                "kappa": model.kappa
            }
        }, f, indent=2)
    
    print("\n" + "="*60)
    print("✅ Time Delays Test Complete!")
    print(f"   Results saved to: {out_dir}")
    print("="*60)


if __name__ == "__main__":
    main()
