"""
UET JAX Solvers - GPU-accelerated simulation kernels

Modular solver components for running UET simulations at scale.
Supports CPU, NVIDIA GPU (CUDA), and Apple Metal.

Installation:
    pip install jax jaxlib          # CPU
    pip install jax[cuda12]         # NVIDIA GPU  
    pip install jax[metal]          # Apple M1/M2/M3

Example:
    from uet_core.solvers.jax_solver import UETSolver
    
    solver = UETSolver(N=64, kappa=0.3, beta=0.5, s=0.0)
    omegas = solver.run_batch(n_runs=10000)
"""

import time
from dataclasses import dataclass
from typing import Tuple, Optional, Any
import numpy as np

# Modular Potentials
from uet_core.potentials import AbstractPotential, QuarticPotential

# JAX imports (optional)
try:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap, random
    # Register implicit PyTreeNode compatibility if needed, 
    # but flax.struct.PyTreeNode handles it.
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False
    jnp = None


@dataclass
class UETParams:
    """UET simulation parameters."""
    N: int = 32          # Grid size
    T: float = 2.0       # Total simulation time
    dt: float = 0.02     # Time step
    kappa: float = 0.3   # Surface tension / gradient penalty
    beta: float = 0.5    # Coupling strength
    s: float = 0.0       # Symmetry-breaking tilt
    seed: int = 42       # Random seed for reproducibility
    
    @property
    def dx(self) -> float:
        """Grid spacing."""
        return 1.0 / self.N
    
    @property
    def n_steps(self) -> int:
        """Number of time steps."""
        return int(self.T / self.dt)


def check_jax_devices():
    """Check available JAX devices and return device type."""
    if not JAX_AVAILABLE:
        return "numpy_fallback", []
    
    devices = jax.devices()
    device_type = devices[0].platform
    return device_type, devices


# ============================================================================
# JAX Kernels (JIT-compiled)
# ============================================================================

if JAX_AVAILABLE:
    @jit
    def _laplacian_2d(phi, dx):
        """JIT-compiled 2D Laplacian with periodic boundary conditions."""
        return (jnp.roll(phi, 1, 0) + jnp.roll(phi, -1, 0) +
                jnp.roll(phi, 1, 1) + jnp.roll(phi, -1, 1) - 4*phi) / (dx**2)

    @jit
    def _compute_omega(C, I, beta, kappa, dx, pot_C: AbstractPotential, pot_I: AbstractPotential):
        """JIT-compiled Omega (energy functional) calculation."""
        # Gradient components
        gx = (jnp.roll(C, -1, 0) - jnp.roll(C, 1, 0)) / (2*dx)
        gy = (jnp.roll(C, -1, 1) - jnp.roll(C, 1, 1)) / (2*dx)
        
        # Energy terms
        kinetic = 0.5 * kappa * (gx**2 + gy**2)
        
        # Modular potential energy
        # Note: Omega usually assumes s is part of potential energy
        potential = pot_C.V(C) + pot_I.V(I)
        
        coupling = 0.5 * beta * (C - I)**2
        
        return jnp.sum(kinetic + potential + coupling) * dx**2

    @jit
    def _uet_step(C, I, kappa, beta, dt, dx, pot_C: AbstractPotential, pot_I: AbstractPotential):
        """Single UET time step (JIT-compiled)."""
        # Laplacians
        lap_C = _laplacian_2d(C, dx)
        lap_I = _laplacian_2d(I, dx)
        
        # Modular Potential derivatives
        dV_C = pot_C.dV(C)
        dV_I = pot_I.dV(I)
        
        # UET coupled field update
        # Equations: dC/dt = kappa*Lap(C) - dV(C) - beta(C-I)
        # Note: s is already inside pot_C.dV(C) as "-s", so dV(C) returns a*u + delta*u^3 - s
        # so -dV(C) becomes -a*u - delta*u^3 + s. Correct.
        C_new = C + dt * (kappa * lap_C - dV_C - beta * (C - I))
        I_new = I + dt * (kappa * lap_I - dV_I - beta * (I - C))
        
        # Clip for numerical stability
        C_new = jnp.clip(C_new, -5, 5)
        I_new = jnp.clip(I_new, -5, 5)
        
        return C_new, I_new

    def _run_single_simulation(key, N, T, dt, kappa, beta, pot_C, pot_I):
        """Run a single UET simulation and return final Omega."""
        dx = 1.0 / N
        n_steps = int(T / dt)
        
        # Random initial conditions
        key1, key2 = random.split(key)
        C = random.normal(key1, (N, N)) * 0.1
        I = random.normal(key2, (N, N)) * 0.1
        
        # Time evolution
        for _ in range(n_steps):
            C, I = _uet_step(C, I, kappa, beta, dt, dx, pot_C, pot_I)
        
        # Compute final energy functional
        omega = _compute_omega(C, I, beta, kappa, dx, pot_C, pot_I)
        return omega

    # Vectorized batch processing
    # in_axes: key is 0 (mapped), others are None (broadcast)
    _run_batch_vmap = vmap(_run_single_simulation, 
                           in_axes=(0, None, None, None, None, None, None, None))


# ============================================================================
# NumPy Fallback (for systems without JAX)
# ============================================================================

def _run_single_numpy(seed, N, T, dt, kappa, beta, s):
    """NumPy fallback for single simulation (Classic Hardcoded)."""
    # NOTE: This fallback still uses hardcoded Quartic for safety/legacy
    dx = 1.0 / N
    n_steps = int(T / dt)
    
    np.random.seed(seed)
    C = np.random.randn(N, N) * 0.1
    I = np.random.randn(N, N) * 0.1
    
    for _ in range(n_steps):
        lap_C = (np.roll(C, 1, 0) + np.roll(C, -1, 0) +
                 np.roll(C, 1, 1) + np.roll(C, -1, 1) - 4*C) / dx**2
        lap_I = (np.roll(I, 1, 0) + np.roll(I, -1, 0) +
                 np.roll(I, 1, 1) + np.roll(I, -1, 1) - 4*I) / dx**2
        
        dV_C = C * (C**2 - 1)
        dV_I = I * (I**2 - 1)
        
        C = C + dt * (kappa * lap_C - dV_C - beta * (C - I) + s)
        I = I + dt * (kappa * lap_I - dV_I - beta * (I - C))
        
        C = np.clip(C, -5, 5)
        I = np.clip(I, -5, 5)
    
    gx = (np.roll(C, -1, 0) - np.roll(C, 1, 0)) / (2*dx)
    gy = (np.roll(C, -1, 1) - np.roll(C, 1, 1)) / (2*dx)
    kinetic = 0.5 * kappa * (gx**2 + gy**2)
    potential = (C**2 - 1)**2 / 4
    coupling = 0.5 * beta * (C - I)**2
    omega = np.sum(kinetic + potential + coupling) * dx**2
    
    return omega

# ============================================================================
# Main Solver Class
# ============================================================================

class UETSolver:
    """
    UET Solver with automatic backend selection.
    
    Supports:
    - JAX with GPU acceleration (CUDA/Metal) -> Uses Modular Potentials
    - NumPy fallback -> Uses Classic Quartic
    """
    
    def __init__(self, params: Optional[UETParams] = None, 
                 pot_C: Optional[AbstractPotential] = None, 
                 pot_I: Optional[AbstractPotential] = None, 
                 **kwargs):
        """
        Initialize solver.
        
        Args:
            params: UETParams dataclass with all parameters
            pot_C: Potential for Conscience field (optional)
            pot_I: Potential for Instinct field (optional)
            **kwargs: Individual parameters (override params if given)
        """
        if params is None:
            params = UETParams()
        
        # Allow kwargs to override
        self.params = UETParams(
            N=kwargs.get('N', params.N),
            T=kwargs.get('T', params.T),
            dt=kwargs.get('dt', params.dt),
            kappa=kwargs.get('kappa', params.kappa),
            beta=kwargs.get('beta', params.beta),
            s=kwargs.get('s', params.s),
            seed=kwargs.get('seed', params.seed),
        )
        
        # Initialize Potentials based on params if not provided
        # This maintains backward compatibility
        if pot_C is None:
            self.pot_C = QuarticPotential(s=self.params.s)
        else:
            self.pot_C = pot_C
            
        if pot_I is None:
            self.pot_I = QuarticPotential(s=0.0)
        else:
            self.pot_I = pot_I

        # Check backend
        self.device_type, self.devices = check_jax_devices()
        self.use_jax = JAX_AVAILABLE and self.device_type != "numpy_fallback"
    
    def run_batch(self, n_runs: int, verbose: bool = True) -> dict:
        """
        Run batch of simulations.
        """
        p = self.params
        
        if verbose:
            print(f"Running {n_runs:,} simulations...")
            print(f"  Backend: {'JAX (' + self.device_type + ')' if self.use_jax else 'NumPy'}")
        
        start = time.time()
        
        if self.use_jax:
            omegas = self._run_jax(n_runs)
        else:
            if not isinstance(self.pot_C, QuarticPotential):
                print("WARNING: NumPy fallback only supports QuarticPotential. Ignoring custom potential.")
            omegas = self._run_numpy(n_runs, verbose)
        
        elapsed = time.time() - start
        
        # Statistics
        results = {
            'omegas': omegas,
            'omega_mean': float(np.mean(omegas)),
            'omega_std': float(np.std(omegas)),
            'omega_ci_95': [float(np.percentile(omegas, 2.5)), 
                           float(np.percentile(omegas, 97.5))],
            'n_runs': n_runs,
            'elapsed_seconds': elapsed,
            'runs_per_second': n_runs / elapsed,
            'backend': 'jax' if self.use_jax else 'numpy',
            'device': self.device_type,
            'params': {
                'N': p.N, 'T': p.T, 'dt': p.dt,
                'kappa': p.kappa, 'beta': p.beta, 's': p.s
            }
        }
        
        if verbose:
            print(f"  Completed in {elapsed:.2f}s ({n_runs/elapsed:.1f} runs/sec)")
        
        return results
    
    def _run_jax(self, n_runs: int) -> np.ndarray:
        """Run with JAX backend."""
        p = self.params
        master_key = random.PRNGKey(p.seed)
        keys = random.split(master_key, n_runs)
        
        omegas = _run_batch_vmap(keys, p.N, p.T, p.dt, p.kappa, p.beta, self.pot_C, self.pot_I)
        return np.array(omegas)
    
    def _run_numpy(self, n_runs: int, verbose: bool) -> np.ndarray:
        """Run with NumPy fallback."""
        p = self.params
        omegas = []
        
        for i in range(n_runs):
            omega = _run_single_numpy(
                p.seed + i, p.N, p.T, p.dt, p.kappa, p.beta, p.s
            )
            omegas.append(omega)
            
            if verbose and (i + 1) % 100 == 0:
                print(f"    Progress: {i+1}/{n_runs}")
        
        return np.array(omegas)

    def step(self, C: Any, I: Any) -> Tuple[Any, Any]:
        """
        Advance state by one time step.
        Dispatches to JAX or NumPy backend.
        """
        p = self.params
        
        if self.use_jax:
            # JIT compiled step
            C_new, I_new = _uet_step(C, I, p.kappa, p.beta, p.dt, p.dx, self.pot_C, self.pot_I)
            return C_new, I_new
        else:
            # NumPy step (manual implementation to avoid strictly private function usage)
            dx = p.dx
            dt = p.dt
            
            lap_C = (np.roll(C, 1, 0) + np.roll(C, -1, 0) +
                     np.roll(C, 1, 1) + np.roll(C, -1, 1) - 4*C) / dx**2
            lap_I = (np.roll(I, 1, 0) + np.roll(I, -1, 0) +
                     np.roll(I, 1, 1) + np.roll(I, -1, 1) - 4*I) / dx**2
            
            # Helper for potential derivative fallback
            def get_dV(pot, u):
                try:
                    return pot.dV(u)
                except:
                    # Fallback to hardcoded quartic
                    return u * (u**2 - 1)

            dV_C = get_dV(self.pot_C, C)
            dV_I = get_dV(self.pot_I, I)
            
            C_new = C + dt * (p.kappa * lap_C - dV_C - p.beta * (C - I))
            I_new = I + dt * (p.kappa * lap_I - dV_I - p.beta * (I - C))
            
            C_new = np.clip(C_new, -5, 5)
            I_new = np.clip(I_new, -5, 5)
            
            return C_new, I_new


# ============================================================================
# Convenience functions
# ============================================================================

def run_sweep(param_name: str, param_values: list, n_runs: int = 100, 
              base_params: Optional[UETParams] = None, **kwargs) -> list:
    """
    Run parameter sweep.
    """
    results = []
    
    for value in param_values:
        # Create params with sweep value
        sweep_kwargs = {**kwargs, param_name: value}
        solver = UETSolver(params=base_params, **sweep_kwargs)
        
        result = solver.run_batch(n_runs, verbose=False)
        result['sweep_param'] = param_name
        result['sweep_value'] = value
        results.append(result)
        
        print(f"  {param_name}={value:.3f}: Ω={result['omega_mean']:.4f} ± {result['omega_std']:.4f}")
    
    return results
