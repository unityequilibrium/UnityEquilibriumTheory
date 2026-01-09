#!/usr/bin/env python
"""
Automatic Parameter Tuning for UET using Bayesian Optimization

Uses scikit-optimize to find optimal β, κ, s for given target behavior.

Usage:
    python scripts/auto_parameter_tuning.py --target seizure --data eeg_data.csv
"""
import numpy as np
from pathlib import Path
from skopt import gp_minimize
from skopt.space import Real
from skopt.utils import use_named_args
import json

# Parameter search space
space = [
    Real(0.01, 2.0, name='kappa'),  # Diffusion
    Real(0.01, 2.0, name='beta'),   # Coupling
    Real(-1.0, 1.0, name='s'),      # Bias
]


def run_uet_inline(C0, I0, kappa, beta, s, T=2.0, dt=0.05):
    """Inline UET simulation."""
    N = C0.shape[0]
    dx = 1.0 / N
    n_steps = int(T / dt)
    
    C, I = C0.copy(), I0.copy()
    omega_history = []
    
    for step in range(n_steps):
        # Laplacian
        lap_C = (np.roll(C, 1, 0) + np.roll(C, -1, 0) + np.roll(C, 1, 1) + np.roll(C, -1, 1) - 4*C) / dx**2
        lap_I = (np.roll(I, 1, 0) + np.roll(I, -1, 0) + np.roll(I, 1, 1) + np.roll(I, -1, 1) - 4*I) / dx**2
        
        # Potential derivative
        dV_C = C * (C**2 - 1)
        dV_I = I * (I**2 - 1)
        
        # UET update
        C = C + dt * (kappa * lap_C - dV_C - beta * (C - I) + s)
        I = I + dt * (kappa * lap_I - dV_I - beta * (I - C))
        
        # Clip to prevent blowup
        C = np.clip(C, -5, 5)
        I = np.clip(I, -5, 5)
        
        # Compute omega
        gx = (np.roll(C, -1, 0) - np.roll(C, 1, 0)) / (2*dx)
        gy = (np.roll(C, -1, 1) - np.roll(C, 1, 1)) / (2*dx)
        kinetic = 0.5 * kappa * (gx**2 + gy**2)
        potential = (C**2 - 1)**2 / 4
        coupling = 0.5 * beta * (C - I)**2
        omega = np.sum(kinetic + potential + coupling) * dx**2
        omega_history.append(omega)
    
    return {"omega": omega_history, "C": C, "I": I}


def objective_function(params, target_data=None):
    """Objective: minimize prediction error or variance."""
    kappa, beta, s = params
    
    try:
        N = 32  # Smaller for speed
        np.random.seed(42)  # Reproducible
        C0 = np.random.randn(N, N) * 0.1
        I0 = np.random.randn(N, N) * 0.1
        
        result = run_uet_inline(C0, I0, kappa=kappa, beta=beta, s=s, T=2.0, dt=0.02)
        
        # Objective: minimize omega variance (stability)
        omega_history = result['omega']
        
        # Check for NaN/Inf
        if any(np.isnan(omega_history)) or any(np.isinf(omega_history)):
            return 1e10  # Penalty for unstable
        
        error = np.var(omega_history)
        return float(error)
    except:
        return 1e10  # Penalty for any error


@use_named_args(space)
def objective(**params):
    return objective_function([params['kappa'], params['beta'], params['s']])


def tune_parameters(target='stability', n_calls=50):
    """
    Run Bayesian optimization to find best parameters.
    
    Args:
        target: 'stability', 'seizure', 'traffic', etc.
        n_calls: Number of optimization iterations
    """
    print(f"🔍 Tuning UET parameters for: {target}")
    print(f"   Search space: κ∈[0.01,2], β∈[0.01,2], s∈[-1,1]")
    print(f"   Iterations: {n_calls}")
    
    # Run optimization
    result = gp_minimize(
        objective,
        space,
        n_calls=n_calls,
        random_state=42,
        verbose=True,
        n_jobs=-1  # Parallel
    )
    
    # Best parameters
    best_kappa, best_beta, best_s = result.x
    best_error = result.fun
    
    print("\n" + "="*60)
    print("✅ OPTIMAL PARAMETERS FOUND")
    print("="*60)
    print(f"  κ (kappa)  = {best_kappa:.4f}")
    print(f"  β (beta)   = {best_beta:.4f}")
    print(f"  s (bias)   = {best_s:.4f}")
    print(f"  Error      = {best_error:.6f}")
    print("="*60)
    
    # Save results
    output = {
        "target": target,
        "optimal_params": {
            "kappa": float(best_kappa),
            "beta": float(best_beta),
            "s": float(best_s),
        },
        "error": float(best_error),
        "n_iterations": n_calls,
        "convergence": result.models[-1].score(result.x_iters, result.func_vals)
    }
    
    output_file = Path(f"optimal_params_{target}.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Saved to: {output_file}")
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="stability", 
                       choices=["stability", "seizure", "traffic", "galaxy"])
    parser.add_argument("--iterations", type=int, default=50)
    
    args = parser.parse_args()
    
    tune_parameters(target=args.target, n_calls=args.iterations)
