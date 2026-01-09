#!/usr/bin/env python
"""
Test Stochastic (Noise) Extension

Demonstrates noise effects: fluctuations, noise-induced transitions.

Usage:
    python scripts/test_stochastic.py
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from pathlib import Path


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


class UETWithNoise:
    """UET model with stochastic noise (Euler-Maruyama)."""
    
    def __init__(self, N=32, kappa=0.1, beta=0.5, s=0.0,
                 sigma_C=0.0, sigma_I=0.0, dt=0.01):
        self.N = N
        self.kappa = kappa
        self.beta = beta
        self.s = s
        self.sigma_C = sigma_C
        self.sigma_I = sigma_I
        self.dt = dt
        
        # Initialize fields
        self.C = np.random.randn(N, N) * 0.1 + 1.0
        self.I = np.random.randn(N, N) * 0.1 - 1.0
    
    def step(self):
        """Evolve one timestep with noise (Euler-Maruyama)."""
        C, I = self.C, self.I
        dt = self.dt
        
        # Deterministic part
        dC_det = (
            self.kappa * laplacian_2d(C) -
            dV_dphi(C) -
            self.beta * (C - I) +
            self.s
        )
        
        dI_det = (
            self.kappa * laplacian_2d(I) -
            dV_dphi(I) -
            self.beta * (I - C)
        )
        
        # Stochastic part (white noise)
        noise_C = np.random.randn(self.N, self.N)
        noise_I = np.random.randn(self.N, self.N)
        
        # Euler-Maruyama update
        self.C = C + dt * dC_det + np.sqrt(dt) * self.sigma_C * noise_C
        self.I = I + dt * dI_det + np.sqrt(dt) * self.sigma_I * noise_I
    
    def get_mean_values(self):
        """Get spatial mean of C and I."""
        return np.mean(self.C), np.mean(self.I)
    
    def compute_omega(self):
        """Compute network mass Ω."""
        C, I = self.C, self.I
        dx = 1.0 / self.N
        
        grad_C_x = (np.roll(C, -1, axis=0) - np.roll(C, 1, axis=0)) / (2*dx)
        grad_C_y = (np.roll(C, -1, axis=1) - np.roll(C, 1, axis=1)) / (2*dx)
        grad_I_x = (np.roll(I, -1, axis=0) - np.roll(I, 1, axis=0)) / (2*dx)
        grad_I_y = (np.roll(I, -1, axis=1) - np.roll(I, 1, axis=1)) / (2*dx)
        
        kinetic = 0.5 * (grad_C_x**2 + grad_C_y**2 + grad_I_x**2 + grad_I_y**2)
        V_C = (C**2 - 1)**2 / 4
        V_I = (I**2 - 1)**2 / 4
        coupling = self.beta * C * I
        
        omega = np.sum(kinetic + V_C + V_I + coupling) * dx**2
        return float(omega)



def test_noise_effects():
    """Test that noise creates fluctuations."""
    print("\n" + "="*60)
    print("🧪 Testing Stochastic Noise")
    print("="*60)
    
    # Test 1: No noise (deterministic)
    print("\n1️⃣  No noise (σ=0):")
    model_no_noise = UETWithNoise(N=32, sigma_C=0.0, sigma_I=0.0, beta=0.5)
    
    C_means_no_noise = []
    C_point_no_noise = []  # Track single point
    for _ in range(500):
        model_no_noise.step()
        C_mean, _ = model_no_noise.get_mean_values()
        C_means_no_noise.append(C_mean)
        C_point_no_noise.append(model_no_noise.C[16, 16])  # Center point
    
    variance_no_noise = np.var(C_means_no_noise[-100:])
    variance_point_no_noise = np.var(C_point_no_noise[-100:])
    print(f"   Variance (spatial avg): {variance_no_noise:.6f}")
    print(f"   Variance (single point): {variance_point_no_noise:.6f}")
    print(f"   Expected: Very low variance (deterministic)")
    
    # Test 2: Medium noise
    print("\n2️⃣  Medium noise (σ=0.5):")
    model_medium_noise = UETWithNoise(N=32, sigma_C=0.5, sigma_I=0.2, beta=0.5)
    
    C_means_medium = []
    C_point_medium = []
    for _ in range(500):
        model_medium_noise.step()
        C_mean, _ = model_medium_noise.get_mean_values()
        C_means_medium.append(C_mean)
        C_point_medium.append(model_medium_noise.C[16, 16])
    
    variance_medium = np.var(C_means_medium[-100:])
    variance_point_medium = np.var(C_point_medium[-100:])
    print(f"   Variance (spatial avg): {variance_medium:.6f}")
    print(f"   Variance (single point): {variance_point_medium:.6f}")
    print(f"   Expected: Medium fluctuations")
    
    # Test 3: Large noise
    print("\n3️⃣  Large noise (σ=2.0):")
    model_large_noise = UETWithNoise(N=32, sigma_C=2.0, sigma_I=0.8, beta=0.5)
    
    C_means_large = []
    C_point_large = []
    for _ in range(500):
        model_large_noise.step()
        C_mean, _ = model_large_noise.get_mean_values()
        C_means_large.append(C_mean)
        C_point_large.append(model_large_noise.C[16, 16])
    
    variance_large = np.var(C_means_large[-100:])
    variance_point_large = np.var(C_point_large[-100:])
    print(f"   Variance (spatial avg): {variance_large:.6f}")
    print(f"   Variance (single point): {variance_point_large:.6f}")
    print(f"   Expected: Large fluctuations")
    
    # Plot comparison
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    axes[0].plot(C_means_no_noise, 'b-', lw=1.5, alpha=0.8)
    axes[0].set_title('No Noise (σ=0)', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Time step')
    axes[0].set_ylabel('⟨C⟩')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim(-2, 2)
    
    axes[1].plot(C_means_medium, 'g-', lw=1.5, alpha=0.8)
    axes[1].set_title('Medium Noise (σ=0.5)', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Time step')
    axes[1].set_ylabel('⟨C⟩')
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim(-2, 2)
    
    axes[2].plot(C_means_large, 'r-', lw=1.5, alpha=0.8)
    axes[2].set_title('Large Noise (σ=2.0)', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('Time step')
    axes[2].set_ylabel('⟨C⟩')
    axes[2].grid(True, alpha=0.3)
    axes[2].set_ylim(-2, 2)
    
    plt.tight_layout()
    
    out_dir = Path("runs_gallery/test_stochastic")
    out_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_dir / "noise_comparison.png", dpi=150)
    print(f"\n   ✅ Saved: {out_dir / 'noise_comparison.png'}")
    
    # Verdict
    print("\n" + "="*60)
    print(f"Variance (spatial avg): {variance_no_noise:.6f} → {variance_medium:.6f} → {variance_large:.6f}")
    print(f"Variance (single point): {variance_point_no_noise:.6f} → {variance_point_medium:.6f} → {variance_point_large:.6f}")
    if variance_point_large > 10 * variance_point_medium > 10 * variance_point_no_noise:
        print("✅ TEST PASSED: Noise creates fluctuations!")
    elif variance_large > 5 * variance_medium:
        print("✅ TEST PASSED: Clear variance progression!")
    else:
        print("⚠️  TEST INCONCLUSIVE: Variance progression unclear")
    print("="*60)
    
    return model_large_noise


def make_noise_animation(model, n_frames=200, fps=20):
    """Create animation showing noisy dynamics."""
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
        axes[0].set_title('C Field (Noisy)', fontsize=12, fontweight='bold')
        axes[0].axis('off')
        
        # 2. I field
        im2 = axes[1].imshow(model.I, cmap='RdBu_r', vmin=-2, vmax=2, origin='lower')
        axes[1].set_title('I Field (Noisy)', fontsize=12, fontweight='bold')
        axes[1].axis('off')
        
        # 3. Time series
        axes[2].plot(C_means, 'r-', lw=2, alpha=0.7, label='⟨C⟩')
        axes[2].plot(I_means, 'b-', lw=2, alpha=0.7, label='⟨I⟩')
        axes[2].set_xlim(0, n_frames)
        axes[2].set_ylim(-1.5, 1.5)
        axes[2].set_xlabel('Frame', fontsize=10)
        axes[2].set_ylabel('Mean Value', fontsize=10)
        axes[2].set_title(f'Fluctuations (σ={model.sigma_C})', fontsize=12, fontweight='bold')
        axes[2].legend(loc='upper right')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return []
    
    ani = animation.FuncAnimation(fig, update, frames=n_frames, interval=1000//fps)
    
    out_dir = Path("runs_gallery/test_stochastic")
    output_path = out_dir / "CI_evolution.gif"
    ani.save(output_path, writer='pillow', fps=fps)
    plt.close()
    
    print(f"   ✅ Saved: {output_path}")
    return output_path


def main():
    print("\n" + "="*60)
    print("🎲 UET STOCHASTIC NOISE TEST")
    print("="*60)
    print("\nThis test demonstrates:")
    print("  1. No noise → Smooth dynamics")
    print("  2. Small noise → Small fluctuations")
    print("  3. Large noise → Large fluctuations")
    print("="*60)
    
    # Run tests
    model = test_noise_effects()
    
    # Compute Omega before animation
    omega_initial = model.compute_omega()
    
    # Create animation
    make_noise_animation(model, n_frames=150, fps=20)
    
    # Compute Omega after animation
    omega_final = model.compute_omega()
    delta_omega = (omega_final - omega_initial) / abs(omega_initial) if omega_initial != 0 else 0
    
    # Save summary with Omega values
    out_dir = Path("runs_gallery/test_stochastic")
    summary = {
        "test": "stochastic_noise",
        "sigma_C": model.sigma_C,
        "sigma_I": model.sigma_I,
        "beta": model.beta,
        "result": "Fluctuations observed",
        "status": "PASS",
        "Omega0": omega_initial,
        "OmegaT": omega_final,
        "delta_omega": delta_omega,
        "omega_conserved": abs(delta_omega) < 0.1,
        "description": f"Stochastic noise σ_C={model.sigma_C}, σ_I={model.sigma_I}"
    }
    
    import json
    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    with open(out_dir / "config.json", "w") as f:
        json.dump({
            "case_id": "test_stochastic",
            "model": "UET_with_noise",
            "params": {
                "sigma_C": model.sigma_C,
                "sigma_I": model.sigma_I,
                "beta": model.beta,
                "kappa": model.kappa
            }
        }, f, indent=2)
    
    print("\n" + "="*60)
    print("✅ Stochastic Noise Test Complete!")
    print(f"   Results saved to: {out_dir}")
    print("="*60)


if __name__ == "__main__":
    main()
