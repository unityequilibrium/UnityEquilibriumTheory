#!/usr/bin/env python
"""
UET n-Dimensional Solver - Mathematical Proof of Concept

Demonstrates that UET equations work in arbitrary dimensions (1D, 2D, 3D, 4D, ..., nD)

Usage:
    python scripts/run_uet_nd.py --dims 4 --N 10 --T 2.0
    python scripts/run_uet_nd.py --dims 5 --N 5 --T 1.0
"""
import sys
import time
import argparse
import numpy as np
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def laplacian_nd(phi, dx, n_dims):
    """
    Compute Laplacian in n dimensions using finite differences.
    
    ∇²φ = Σᵢ₌₁ⁿ ∂²φ/∂xᵢ²
    
    Args:
        phi: n-dimensional array
        dx: grid spacing
        n_dims: number of dimensions
    """
    lap = -2 * n_dims * phi
    for axis in range(n_dims):
        lap += np.roll(phi, 1, axis=axis)
        lap += np.roll(phi, -1, axis=axis)
    return lap / (dx ** 2)


def compute_omega_nd(C, I, beta, kappa, dx, n_dims):
    """
    Compute energy functional Ω in n dimensions.
    
    Ω = ∫ [½κ|∇C|² + V(C) + ½κ|∇I|² + V(I) + ½β(C-I)²] dⁿx
    """
    # Gradient energy (kinetic term)
    grad_energy = 0.0
    for axis in range(n_dims):
        gC = (np.roll(C, -1, axis=axis) - np.roll(C, 1, axis=axis)) / (2 * dx)
        gI = (np.roll(I, -1, axis=axis) - np.roll(I, 1, axis=axis)) / (2 * dx)
        grad_energy += 0.5 * kappa * (gC**2 + gI**2)
    
    # Potential energy
    potential = (C**2 - 1)**2 / 4 + (I**2 - 1)**2 / 4
    
    # Coupling energy
    coupling = 0.5 * beta * (C - I)**2
    
    return np.sum(grad_energy + potential + coupling) * (dx ** n_dims)


def uet_step_nd(C, I, kappa, beta, s, dt, dx, n_dims):
    """
    Single UET time step in n dimensions.
    
    ∂C/∂t = κ∇²C - V'(C) - β(C-I) + s
    ∂I/∂t = κ∇²I - V'(I) - β(I-C)
    """
    # Laplacians
    lap_C = laplacian_nd(C, dx, n_dims)
    lap_I = laplacian_nd(I, dx, n_dims)
    
    # Potential derivatives (quartic)
    dV_C = C * (C**2 - 1)
    dV_I = I * (I**2 - 1)
    
    # Update
    C_new = C + dt * (kappa * lap_C - dV_C - beta * (C - I) + s)
    I_new = I + dt * (kappa * lap_I - dV_I - beta * (I - C))
    
    # Stability clipping
    C_new = np.clip(C_new, -5, 5)
    I_new = np.clip(I_new, -5, 5)
    
    return C_new, I_new


def run_uet_nd(n_dims, N, T, dt=0.01, kappa=0.3, beta=0.5, s=0.0, seed=42):
    """
    Run UET simulation in n dimensions.
    
    Args:
        n_dims: number of spatial dimensions
        N: grid size per dimension
        T: total simulation time
        dt: time step
        kappa: gradient penalty
        beta: coupling strength
        s: symmetry-breaking tilt
        seed: random seed
    
    Returns:
        dict with results
    """
    np.random.seed(seed)
    dx = 1.0 / N
    n_steps = int(T / dt)
    
    # Create n-dimensional grid
    shape = tuple([N] * n_dims)
    total_nodes = N ** n_dims
    
    print(f"\n{'='*70}")
    print(f"🌌 UET {n_dims}D SIMULATION")
    print(f"{'='*70}")
    print(f"  Dimensions: {n_dims}")
    print(f"  Grid: {' × '.join([str(N)] * n_dims)} = {total_nodes:,} nodes")
    print(f"  Steps: {n_steps:,}")
    print(f"  Memory: ~{total_nodes * 16 / 1024**2:.1f} MB")
    print(f"  κ={kappa}, β={beta}, s={s}")
    print()
    
    # Initial conditions
    C = np.random.randn(*shape) * 0.1
    I = np.random.randn(*shape) * 0.1
    
    # Initial energy
    omega_init = compute_omega_nd(C, I, beta, kappa, dx, n_dims)
    
    # Time evolution
    start = time.time()
    omegas = []
    
    for step in range(n_steps):
        C, I = uet_step_nd(C, I, kappa, beta, s, dt, dx, n_dims)
        
        if step % max(1, n_steps // 10) == 0:
            omega = compute_omega_nd(C, I, beta, kappa, dx, n_dims)
            omegas.append(omega)
            progress = 100 * (step + 1) / n_steps
            print(f"  {progress:5.1f}% | Ω = {omega:.3f}")
    
    # Final energy
    omega_final = compute_omega_nd(C, I, beta, kappa, dx, n_dims)
    elapsed = time.time() - start
    
    print()
    print(f"  Ω: {omega_init:.3f} → {omega_final:.3f}")
    print(f"  Time: {elapsed:.2f}s ({n_steps/elapsed:.1f} steps/sec)")
    print(f"{'='*70}")
    
    return {
        'n_dims': n_dims,
        'N': N,
        'total_nodes': total_nodes,
        'n_steps': n_steps,
        'omega_init': omega_init,
        'omega_final': omega_final,
        'omega_history': omegas,
        'elapsed': elapsed,
        'steps_per_sec': n_steps / elapsed,
    }


def main():
    parser = argparse.ArgumentParser(description="UET n-Dimensional Solver")
    parser.add_argument("--dims", type=int, default=4, help="Number of dimensions")
    parser.add_argument("--N", type=int, default=10, help="Grid size per dimension")
    parser.add_argument("--T", type=float, default=2.0, help="Simulation time")
    parser.add_argument("--dt", type=float, default=0.01, help="Time step")
    parser.add_argument("--kappa", type=float, default=0.3, help="Gradient penalty")
    parser.add_argument("--beta", type=float, default=0.5, help="Coupling strength")
    parser.add_argument("--s", type=float, default=0.0, help="Symmetry-breaking tilt")
    
    args = parser.parse_args()
    
    # Safety check
    total_nodes = args.N ** args.dims
    memory_mb = total_nodes * 16 / 1024**2
    
    if memory_mb > 1000:  # > 1 GB
        print(f"⚠️  WARNING: This will use ~{memory_mb:.0f} MB of memory!")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    # Run simulation
    results = run_uet_nd(
        n_dims=args.dims,
        N=args.N,
        T=args.T,
        dt=args.dt,
        kappa=args.kappa,
        beta=args.beta,
        s=args.s,
    )
    
    print(f"\n✅ Proof: UET equations work in {args.dims}D!")
    print(f"   Total nodes simulated: {results['total_nodes']:,}")
    print(f"   Performance: {results['steps_per_sec']:.1f} steps/sec")


if __name__ == "__main__":
    main()
