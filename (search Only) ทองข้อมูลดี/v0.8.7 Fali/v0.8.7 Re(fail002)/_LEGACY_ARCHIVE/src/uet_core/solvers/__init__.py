"""
UET Solvers Package

GPU-accelerated and CPU solvers for UET simulations.

Quick Start:
    from uet_core.solvers import UETSolver, UETParams
    
    # Simple usage
    solver = UETSolver(N=64, kappa=0.3, beta=0.5)
    results = solver.run_batch(1000)
    
    # With params object
    params = UETParams(N=64, T=2.0, dt=0.01, kappa=0.3, beta=0.5, s=0.1)
    solver = UETSolver(params=params)
    results = solver.run_batch(5000)
    
    # Parameter sweep
    from uet_core.solvers import run_sweep
    results = run_sweep('s', [-0.5, 0, 0.5], n_runs=100)
"""

from .jax_solver import (
    UETSolver,
    UETParams,
    run_sweep,
    check_jax_devices,
    JAX_AVAILABLE,
)

__all__ = [
    'UETSolver',
    'UETParams', 
    'run_sweep',
    'check_jax_devices',
    'JAX_AVAILABLE',
]
