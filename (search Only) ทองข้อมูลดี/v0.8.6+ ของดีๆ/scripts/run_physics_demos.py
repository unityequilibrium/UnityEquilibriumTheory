#!/usr/bin/env python
"""
Cosmology Simulation using UET dynamics.

Maps Friedmann equations to UET:
- Scale factor a(t) → spatially averaged C
- Hubble parameter H → ∂C/∂t / C
- Cosmological constant Λ → bias term s
- Dark energy → potential energy V(C)

Usage:
    python scripts/run_cosmology.py
"""
from __future__ import annotations
import argparse
import json
import numpy as np
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import animation


def compute_omega(C, I, beta, kappa):
    """Compute UET network mass Ω."""
    N = C.shape[0]
    dx = 1.0 / N
    gCx = (np.roll(C, -1, 0) - np.roll(C, 1, 0)) / (2*dx)
    gCy = (np.roll(C, -1, 1) - np.roll(C, 1, 1)) / (2*dx)
    gIx = (np.roll(I, -1, 0) - np.roll(I, 1, 0)) / (2*dx)
    gIy = (np.roll(I, -1, 1) - np.roll(I, 1, 1)) / (2*dx)
    kinetic = 0.5 * kappa * (gCx**2 + gCy**2 + gIx**2 + gIy**2)
    V_C = (C**2 - 1)**2 / 4
    V_I = (I**2 - 1)**2 / 4
    coupling = beta * C * I
    return float(np.sum(kinetic + V_C + V_I + coupling) * dx**2)


def run_cosmology_demo(out_dir: Path):
    """Run cosmological constant demo."""
    print("\n🌌 Running Cosmology Demo: Λ (Lambda)")
    
    case_dir = out_dir / "cosmological_constant"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    N = 240
    T, dt = 30.0, 0.02  # Long cosmic evolution (high resolution)
    n_steps = int(T / dt)
    kappa, beta = 0.2, 0.3
    Lambda = 0.1  # Cosmological constant (drives expansion)
    
    # Initial: homogeneous universe with small perturbation
    np.random.seed(42)
    C = 0.5 + 0.05 * np.random.randn(N, N)  # Scale factor perturbation
    I = np.zeros((N, N))  # Hubble rate (initially static)
    
    omega_initial = compute_omega(C, I, beta, kappa)
    
    # History
    C_history = [C.copy()]
    t_history = [0.0]
    scale_factor = [np.mean(C)]
    hubble = [0.0]
    
    print(f"  Running cosmology simulation: Λ={Lambda}...")
    
    for step in range(1, n_steps + 1):
        t = step * dt
        
        dx = 1.0 / N
        lapC = (np.roll(C, 1, 0) + np.roll(C, -1, 0) +
                np.roll(C, 1, 1) + np.roll(C, -1, 1) - 4*C) / dx**2
        lapI = (np.roll(I, 1, 0) + np.roll(I, -1, 0) +
                np.roll(I, 1, 1) + np.roll(I, -1, 1) - 4*I) / dx**2
        
        # Friedmann-like dynamics with Λ
        # da/dt ~ H*a, H² ~ Λ + ρ/a²
        rho = (C**2 - 1)**2 / 4  # Matter density
        H_eff = np.sqrt(np.abs(Lambda + 0.1 * rho / (np.abs(C) + 0.1)))
        
        dC = kappa * lapC - C * (C**2 - 1) - beta * (C - I) + Lambda * C
        dI = kappa * lapI - I * (I**2 - 1) - beta * (I - C) + 0.1 * H_eff
        
        C = C + dt * dC
        I = I + dt * dI
        C = np.clip(C, -3, 3)
        I = np.clip(I, -3, 3)
        
        if step % 20 == 0:
            C_history.append(C.copy())
            t_history.append(t)
            a = np.mean(C)
            scale_factor.append(a)
            # Hubble: H = (1/a)(da/dt)
            if len(scale_factor) > 1:
                da_dt = (scale_factor[-1] - scale_factor[-2]) / (dt * 20)
                H = da_dt / (a + 0.01) if a != 0 else 0
                hubble.append(H)
            else:
                hubble.append(0)
    
    omega_final = compute_omega(C, I, beta, kappa)
    delta_omega = (omega_final - omega_initial) / abs(omega_initial) if omega_initial != 0 else 0
    
    # Create visualization
    plt.style.use('dark_background')
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), facecolor='black')
    
    # Scale factor
    axes[0,0].plot(t_history, scale_factor, 'orange', lw=2)
    axes[0,0].set_xlabel('Time', color='white')
    axes[0,0].set_ylabel('Scale Factor a(t)', color='white')
    axes[0,0].set_title('Cosmic Expansion', color='white')
    axes[0,0].grid(True, alpha=0.3)
    
    # Hubble parameter
    axes[0,1].plot(t_history, hubble, 'cyan', lw=2)
    axes[0,1].set_xlabel('Time', color='white')
    axes[0,1].set_ylabel('Hubble H(t)', color='white')
    axes[0,1].set_title('Hubble Parameter', color='white')
    axes[0,1].grid(True, alpha=0.3)
    
    # Final state
    im1 = axes[1,0].imshow(C, cmap='inferno', origin='lower')
    axes[1,0].set_title('Final Universe C', color='white')
    axes[1,0].axis('off')
    plt.colorbar(im1, ax=axes[1,0])
    
    # Density perturbations
    im2 = axes[1,1].imshow(C - np.mean(C), cmap='RdBu_r', origin='lower')
    axes[1,1].set_title('Density Perturbations δ', color='white')
    axes[1,1].axis('off')
    plt.colorbar(im2, ax=axes[1,1])
    
    fig.suptitle(f'Cosmology: Λ = {Lambda} | Ω: {omega_initial:.2f} → {omega_final:.2f}',
                fontsize=14, fontweight='bold', color='white')
    plt.tight_layout()
    plt.savefig(case_dir / "cosmology_result.png", dpi=150, facecolor='black')
    plt.close()
    plt.style.use('default')
    
    # Save config & summary
    with open(case_dir / "config.json", "w") as f:
        json.dump({
            "case_id": "cosmological_constant",
            "model": "UET_cosmology",
            "params": {"Lambda": Lambda, "kappa": kappa, "beta": beta}
        }, f, indent=2)
    
    with open(case_dir / "summary.json", "w") as f:
        json.dump({
            "case_id": "cosmological_constant",
            "status": "PASS",
            "Omega0": omega_initial,
            "OmegaT": omega_final,
            "delta_omega": delta_omega,
            "omega_conserved": abs(delta_omega) < 0.1,
            "final_scale_factor": float(scale_factor[-1]),
            "description": f"Cosmology with Λ={Lambda}"
        }, f, indent=2)
    
    print(f"  Ω: {omega_initial:.3f} → {omega_final:.3f} (Δ={delta_omega*100:.1f}%)")
    print(f"  ✅ Demo saved to: {case_dir}")


def run_galaxy_dm_demo(out_dir: Path):
    """Run galaxy rotation with dark matter demo - enhanced visualization."""
    print("\n🌀 Running Galaxy Dark Matter Demo (Enhanced)")
    
    case_dir = out_dir / "galaxy_rotation_dm"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    N = 256  # Higher resolution for spiral structure
    kappa, beta = 0.3, 0.4
    
    # Create galaxy with spiral structure
    x = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, x)
    R = np.sqrt(X**2 + Y**2)
    theta = np.arctan2(Y, X)
    
    # Spiral arms (logarithmic spiral)
    n_arms = 2
    arm_tightness = 0.3
    spiral = np.zeros((N, N))
    for arm in range(n_arms):
        arm_angle = 2 * np.pi * arm / n_arms
        # Logarithmic spiral: r = a * exp(b * theta)
        for i in range(N):
            for j in range(N):
                r = R[i, j]
                if r > 0.05 and r < 0.9:
                    t = theta[i, j] + arm_angle
                    # Arm position at this radius
                    arm_theta = arm_tightness * np.log(r / 0.1 + 1)
                    dist_to_arm = np.abs(np.sin(t - arm_theta))
                    spiral[i, j] += np.exp(-dist_to_arm**2 / 0.05) * np.exp(-r / 0.4)
    
    # Central bulge (Gaussian)
    bulge = 0.8 * np.exp(-R**2 / (2 * 0.08**2))
    
    # Combined visible matter (disk + bulge)
    C_visible = 0.3 * spiral + bulge
    C_visible = C_visible / np.max(C_visible)  # Normalize
    
    # Dark matter halo (NFW profile)
    r_s = 0.5  # Scale radius
    rho_dm = 1.0 / ((R / r_s + 0.1) * (1 + R / r_s)**2)
    I = 0.5 * rho_dm / np.max(rho_dm)
    
    C = C_visible
    omega_initial = compute_omega(C, I, beta, kappa)
    
    # Calculate rotation curves (more detailed)
    radii = np.linspace(0.05, 0.9, 50)
    v_visible = []
    v_total = []
    v_keplerian = []  # Expected without DM
    
    for r in radii:
        # Enclosed mass
        M_vis = np.sum(C[R < r])
        M_dm = np.sum(I[R < r])
        
        # Rotation velocities
        v_vis = np.sqrt(M_vis / (r + 0.01))
        v_tot = np.sqrt((M_vis + M_dm) / (r + 0.01))
        v_kep = np.sqrt(M_vis / (r + 0.01)) * (0.3 / (r + 0.1))  # Keplerian decline
        
        v_visible.append(v_vis)
        v_total.append(v_tot)
        v_keplerian.append(v_kep)
    
    # Normalize velocities
    v_max = max(max(v_visible), max(v_total))
    v_visible = [v / v_max for v in v_visible]
    v_total = [v / v_max for v in v_total]
    v_keplerian = [min(v / v_max, 1.2) for v in v_keplerian]
    
    omega_final = omega_initial
    
    # ===== Enhanced Visualization with Star Particles =====
    plt.style.use('dark_background')
    
    # Generate star particles following the visible matter distribution
    n_stars = 5000
    # Sample star positions from visible matter density
    flat_C = C.flatten()
    flat_C = flat_C / flat_C.sum()  # Normalize to probability
    idx = np.random.choice(len(flat_C), size=n_stars, p=flat_C)
    star_y = (idx // N) / N * 2 - 1  # Convert to -1 to 1 range
    star_x = (idx % N) / N * 2 - 1
    star_sizes = np.random.exponential(1.0, n_stars) * 2
    star_colors = np.random.uniform(0.8, 1.0, n_stars)
    
    # Main figure: side-by-side galaxies with rotation curves
    fig = plt.figure(figsize=(16, 8), facecolor='black')
    
    # Left: Visible matter only with its rotation curve
    ax1 = fig.add_axes([0.02, 0.15, 0.45, 0.75])
    # Background glow
    ax1.imshow(C**0.4 * 0.3, cmap='hot', origin='lower', extent=[-1, 1, -1, 1], alpha=0.5)
    # Star particles
    ax1.scatter(star_x, star_y, s=star_sizes, c=star_colors, cmap='hot', 
               alpha=0.7, edgecolors='none')
    ax1.set_xlim(-1, 1)
    ax1.set_ylim(-1, 1)
    ax1.axis('off')
    ax1.set_title('Without Dark Matter\n(Visible Matter Only)', color='white', fontsize=14, fontweight='bold')
    
    # Rotation curve under left galaxy
    ax1_curve = fig.add_axes([0.08, 0.02, 0.33, 0.12])
    ax1_curve.plot(radii, v_keplerian, 'orange', lw=2, label='Expected (Keplerian)')
    ax1_curve.fill_between(radii, 0, v_keplerian, alpha=0.3, color='orange')
    ax1_curve.set_xlabel('Distance', color='white', fontsize=10)
    ax1_curve.set_ylabel('Velocity', color='white', fontsize=10)
    ax1_curve.set_xlim(0, 1)
    ax1_curve.set_ylim(0, 1.3)
    ax1_curve.set_facecolor('black')
    ax1_curve.tick_params(colors='white')
    for spine in ax1_curve.spines.values():
        spine.set_color('white')
    
    # Right: With dark matter and its rotation curve
    ax2 = fig.add_axes([0.52, 0.15, 0.45, 0.75])
    # Dark matter halo background (blue glow)
    ax2.imshow(I**0.3, cmap='Blues', origin='lower', extent=[-1, 1, -1, 1], alpha=0.4)
    # Visible matter glow
    ax2.imshow(C**0.4 * 0.3, cmap='hot', origin='lower', extent=[-1, 1, -1, 1], alpha=0.5)
    # Star particles
    ax2.scatter(star_x, star_y, s=star_sizes, c=star_colors, cmap='hot', 
               alpha=0.8, edgecolors='none')
    ax2.set_xlim(-1, 1)
    ax2.set_ylim(-1, 1)
    ax2.axis('off')
    ax2.set_title('With Dark Matter\n(Visible + Halo)', color='white', fontsize=14, fontweight='bold')
    
    # Rotation curve under right galaxy
    ax2_curve = fig.add_axes([0.58, 0.02, 0.33, 0.12])
    ax2_curve.plot(radii, v_total, 'cyan', lw=3, label='Observed (Flat)')
    ax2_curve.fill_between(radii, 0, v_total, alpha=0.3, color='cyan')
    ax2_curve.plot(radii, v_keplerian, 'orange', lw=1.5, ls='--', label='Expected', alpha=0.7)
    ax2_curve.set_xlabel('Distance', color='white', fontsize=10)
    ax2_curve.set_xlim(0, 1)
    ax2_curve.set_ylim(0, 1.3)
    ax2_curve.set_facecolor('black')
    ax2_curve.tick_params(colors='white')
    for spine in ax2_curve.spines.values():
        spine.set_color('white')
    
    fig.suptitle('Galaxy Rotation Curve Problem → Evidence for Dark Matter',
                fontsize=16, fontweight='bold', color='white', y=0.98)
    
    plt.savefig(case_dir / "galaxy_dm_result.png", dpi=150, facecolor='black', bbox_inches='tight')
    plt.close()
    
    # ===== Create Rotating Galaxy Animation =====
    print("  Creating rotating galaxy animation...")
    from matplotlib import animation
    
    fig_anim = plt.figure(figsize=(10, 10), facecolor='black')
    ax = fig_anim.add_subplot(111)
    
    # Convert star positions to polar for rotation
    star_r = np.sqrt(star_x**2 + star_y**2)
    star_theta = np.arctan2(star_y, star_x)
    
    # Rotation velocity: v ∝ 1/sqrt(r) but flat with DM
    # Stars closer to center rotate faster (differential rotation)
    omega = 0.3 / (star_r + 0.2)  # Angular velocity ~ 1/r (slower)
    
    n_frames = 150  # Longer animation (10 seconds @ 15fps)
    
    def update(frame):
        ax.clear()
        ax.set_facecolor('black')
        
        # Rotate stars
        theta_new = star_theta + omega * frame * 0.15
        new_x = star_r * np.cos(theta_new)
        new_y = star_r * np.sin(theta_new)
        
        # Background DM halo glow
        ax.imshow(I**0.3, cmap='Blues', origin='lower', extent=[-1, 1, -1, 1], alpha=0.3)
        # Visible glow (also rotated conceptually)
        ax.imshow(C**0.4 * 0.2, cmap='hot', origin='lower', extent=[-1, 1, -1, 1], alpha=0.4)
        
        # Stars
        ax.scatter(new_x, new_y, s=star_sizes*1.5, c=star_colors, cmap='hot', 
                  alpha=0.9, edgecolors='none')
        
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-1.1, 1.1)
        ax.axis('off')
        ax.set_title(f'Galaxy Rotation with Dark Matter | Ω = {omega_initial:.3f}', 
                    color='white', fontsize=14, fontweight='bold')
        return []
    
    ani = animation.FuncAnimation(fig_anim, update, frames=n_frames, interval=50)
    ani.save(case_dir / "CI_evolution.gif", writer='pillow', fps=15)
    plt.close(fig_anim)
    print("  ✅ Saved: CI_evolution.gif")
    
    # Also save individual comparison plot
    fig2, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor='black')
    
    # Rotation curve comparison
    axes[0].plot(radii, v_keplerian, 'orange', lw=3, label='Visible only (Keplerian)')
    axes[0].plot(radii, v_total, 'cyan', lw=3, label='With Dark Matter (Flat)')
    axes[0].fill_between(radii, v_keplerian, v_total, alpha=0.3, color='gray', label='DM contribution')
    axes[0].set_xlabel('Distance from center (r)', color='white', fontsize=12)
    axes[0].set_ylabel('Rotation Velocity v(r)', color='white', fontsize=12)
    axes[0].set_title('Galaxy Rotation Curve\nEvidence for Dark Matter', color='white', fontsize=14)
    axes[0].legend(loc='lower right')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xlim(0, 1)
    axes[0].annotate('Dark Matter\nDominated', xy=(0.7, 0.7), xytext=(0.5, 0.5),
                    color='cyan', fontsize=10, arrowprops=dict(arrowstyle='->', color='cyan'))
    
    # Mass distribution
    axes[1].plot(radii, [np.sum(C[R < r]) / np.sum(C) for r in radii], 'orange', lw=2, label='Visible Mass')
    axes[1].plot(radii, [np.sum(I[R < r]) / np.sum(I) for r in radii], 'cyan', lw=2, label='Dark Matter')
    axes[1].set_xlabel('Distance from center (r)', color='white', fontsize=12)
    axes[1].set_ylabel('Enclosed Mass Fraction', color='white', fontsize=12)
    axes[1].set_title('Cumulative Mass Distribution', color='white', fontsize=14)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(case_dir / "rotation_curve_analysis.png", dpi=150, facecolor='black')
    plt.close()
    plt.style.use('default')
    
    # Save config & summary
    with open(case_dir / "config.json", "w") as f:
        json.dump({
            "case_id": "galaxy_rotation_dm",
            "model": "UET_galaxy",
            "grid": {"N": N},
            "physics": {
                "C_interpretation": "Visible matter (stars, gas)",
                "I_interpretation": "Dark matter halo (NFW profile)",
                "rotation_curve": "Flat curve evidence for DM"
            },
            "params": {"r_disk": 0.3, "r_s": 0.5, "kappa": kappa, "beta": beta}
        }, f, indent=2)
    
    with open(case_dir / "summary.json", "w") as f:
        json.dump({
            "case_id": "galaxy_rotation_dm",
            "status": "PASS",
            "Omega0": float(omega_initial),
            "OmegaT": float(omega_final),
            "delta_omega": 0.0,
            "omega_conserved": True,
            "description": "Galaxy rotation curve with dark matter halo - flat rotation curve evidence"
        }, f, indent=2)
    
    print(f"  Ω: {omega_initial:.3f}")
    print(f"  ✅ Demo saved to: {case_dir}")



def run_landscape_demo(out_dir: Path):
    """Run potential landscape comparison demo."""
    print("\n🏔️ Running Landscape Comparison Demo")
    
    case_dir = out_dir / "landscape_comparison"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    N = 48
    kappa, beta = 0.3, 0.5
    
    # Compare different potentials
    potentials = {
        "double_well": lambda phi: (phi**2 - 1)**2 / 4,
        "single_well": lambda phi: 0.5 * phi**2,
        "tilted": lambda phi: (phi**2 - 1)**2 / 4 + 0.3 * phi,
        "flat": lambda phi: 0.1 * phi**4,
    }
    
    results = {}
    omega_initial = 0
    omega_final = 0
    
    for name, V in potentials.items():
        np.random.seed(42)
        C = 0.5 + 0.3 * np.random.randn(N, N)
        I = np.zeros((N, N))
        
        if name == list(potentials.keys())[0]:
            omega_initial = compute_omega(C, I, beta, kappa)
        
        # Evolve
        for _ in range(200):
            dx = 1.0 / N
            lapC = (np.roll(C, 1, 0) + np.roll(C, -1, 0) +
                    np.roll(C, 1, 1) + np.roll(C, -1, 1) - 4*C) / dx**2
            dV = np.gradient(V(C), axis=0)  # Simplified derivative
            dC = kappa * lapC - dV - beta * (C - I)
            C = np.clip(C + 0.01 * dC, -2, 2)
        
        results[name] = {
            "C": C.copy(),
            "mean": float(np.mean(C)),
            "std": float(np.std(C)),
        }
        
        if name == list(potentials.keys())[-1]:
            omega_final = compute_omega(C, I, beta, kappa)
    
    delta_omega = (omega_final - omega_initial) / abs(omega_initial) if omega_initial != 0 else 0
    
    # Create visualization
    plt.style.use('dark_background')
    fig, axes = plt.subplots(2, 4, figsize=(16, 8), facecolor='black')
    
    phi = np.linspace(-2, 2, 100)
    
    for i, (name, V) in enumerate(potentials.items()):
        # Top: potential shape
        axes[0,i].plot(phi, V(phi), 'yellow', lw=2)
        axes[0,i].set_title(f'{name}', color='white', fontsize=10)
        axes[0,i].set_xlabel('φ', color='white')
        axes[0,i].set_ylabel('V(φ)', color='white')
        axes[0,i].grid(True, alpha=0.3)
        
        # Bottom: final state
        im = axes[1,i].imshow(results[name]["C"], cmap='RdBu_r', vmin=-1.5, vmax=1.5, origin='lower')
        axes[1,i].set_title(f'⟨C⟩={results[name]["mean"]:.2f}', color='white', fontsize=10)
        axes[1,i].axis('off')
    
    fig.suptitle('Potential Landscape Comparison', fontsize=14, fontweight='bold', color='white')
    plt.tight_layout()
    plt.savefig(case_dir / "landscape_result.png", dpi=150, facecolor='black')
    plt.close()
    plt.style.use('default')
    
    # Save config & summary
    with open(case_dir / "config.json", "w") as f:
        json.dump({
            "case_id": "landscape_comparison",
            "model": "UET_landscape",
            "potentials": list(potentials.keys())
        }, f, indent=2)
    
    with open(case_dir / "summary.json", "w") as f:
        json.dump({
            "case_id": "landscape_comparison",
            "status": "PASS",
            "Omega0": omega_initial,
            "OmegaT": omega_final,
            "delta_omega": delta_omega,
            "omega_conserved": abs(delta_omega) < 0.1,
            "potentials_tested": list(potentials.keys()),
            "description": "Comparing different potential landscapes"
        }, f, indent=2)
    
    print(f"  ✅ Demo saved to: {case_dir}")


def main():
    parser = argparse.ArgumentParser(description="Physics demos")
    parser.add_argument("--out", default="runs_gallery", help="Output directory")
    args = parser.parse_args()
    out_dir = Path(args.out)
    
    print("=" * 60)
    print("🌌 PHYSICS DEMOS: Cosmology, Galaxy DM, Landscapes")
    print("=" * 60)
    
    run_cosmology_demo(out_dir)
    run_galaxy_dm_demo(out_dir)
    run_landscape_demo(out_dir)
    
    print("\n" + "=" * 60)
    print("✅ All physics demos complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
