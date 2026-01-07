# 🖥️ Numerical Methods

> วิธีเชิงตัวเลขและการ Validate สำหรับ UET

---

## 1. Discretization

### 1.1 Spatial Discretization

```
Domain: [0, L]ⁿ
Grid: N points per dimension
dx = L / N

u_i = u(i·dx)  (discrete values)
```

### 1.2 Gradient Operator

```
Central difference:
(∇u)_i = (u_{i+1} - u_{i-1}) / (2dx)

Laplacian:
(∇²u)_i = (u_{i+1} - 2u_i + u_{i-1}) / dx²
```

### 1.3 Time Discretization

```
dt = time step
u^n = u at time n·dt
```

---

## 2. Semi-Implicit Scheme

### 2.1 Why Semi-Implicit?

```
Explicit: u^{n+1} = u^n + dt·f(u^n)
  → CFL constraint: dt < dx²/(2κ)
  → Very small dt for stability

Implicit: u^{n+1} = u^n + dt·f(u^{n+1})
  → Unconditionally stable
  → But need to solve nonlinear system

Semi-implicit: Split linear and nonlinear parts
  → Larger dt than explicit
  → Easier than fully implicit
```

### 2.2 Operator Splitting

```
∂u/∂t = -M·[V'(u) - κ∇²u]

Split into:
  Linear part: -κ∇²u  (treat implicitly)
  Nonlinear part: V'(u)  (treat explicitly)
```

### 2.3 Scheme

```
(u^{n+1} - u^n)/dt = -M·[V'(u^n) - κ∇²u^{n+1}]

Rearrange:
(I - α∇²)u^{n+1} = u^n - dt·M·V'(u^n)

Where α = dt·M·κ
```

### 2.4 Solving Linear System

```
(I - α∇²)u = rhs

Use spectral method (FFT) for periodic BC:
  In Fourier space: (1 + α·k²)·û = r̂hs
  → û = r̂hs / (1 + α·k²)
  → u = IFFT(û)
```

---

## 3. Energy Guarantee

### 3.1 Backtracking

```
ถ้า Ω^{n+1} > Ω^n (energy increased):
  → Reduce dt
  → Retry step
  → Repeat until Ω^{n+1} ≤ Ω^n
```

### 3.2 Algorithm

```python
def step_with_backtrack(u, dt, max_tries=10):
    Omega_current = compute_energy(u)
    
    for attempt in range(max_tries):
        u_new = semi_implicit_step(u, dt)
        Omega_new = compute_energy(u_new)
        
        if Omega_new <= Omega_current:
            return u_new, dt
        else:
            dt = dt / 2  # reduce
    
    raise Exception("Backtracking failed")
```

---

## 4. CFL Conditions

### 4.1 Stability Constraints

```
dt_max = min(dt_potential, dt_diffusion, dt_coupling)

dt_potential = 0.5 / |a|
dt_diffusion = dx² / (4κ)
dt_coupling = 0.5 / |β|
```

### 4.2 Extreme Parameters

```
Ratio R = |a| / δ

Normal:   R < 1e6    → standard dt
Elevated: R < 1e10   → reduce dt
Extreme:  R < 1e15   → very small dt
Beyond:   R > 1e15   → may not compute
```

---

## 5. Validation Tests

### 5.1 Energy Monotonicity

```python
def test_energy_decreasing():
    """Energy must decrease at every step"""
    energies = [compute_energy(u) for u in trajectory]
    
    for i in range(1, len(energies)):
        assert energies[i] <= energies[i-1] + tol
```

### 5.2 Conservation (if applicable)

```python
def test_mass_conservation():
    """Total mass conserved for Cahn-Hilliard"""
    masses = [np.sum(u) for u in trajectory]
    
    assert np.allclose(masses, masses[0])
```

### 5.3 Known Solutions

```python
def test_known_solution():
    """Compare with analytical solution"""
    # For simple cases like heat equation
    u_numerical = solve(...)
    u_analytical = exact_solution(...)
    
    error = np.linalg.norm(u_numerical - u_analytical)
    assert error < tolerance
```

### 5.4 Convergence

```python
def test_convergence():
    """Refine dx and dt, error should decrease"""
    errors = []
    for N in [32, 64, 128, 256]:
        u = solve(N=N)
        u_ref = solve(N=512)  # reference
        errors.append(compute_error(u, u_ref))
    
    # Check convergence rate
    rates = [errors[i]/errors[i+1] for i in range(len(errors)-1)]
    assert all(r > 1.5 for r in rates)  # at least O(dx^1.5)
```

---

## 6. Performance

### 6.1 Complexity

```
Per time step:
  FFT-based:    O(N log N)
  Matrix-based: O(N³) for 2D

Total:
  T_total = n_steps × O(per_step)
```

### 6.2 GPU Acceleration

```python
# JAX implementation
import jax.numpy as jnp
from jax import jit

@jit
def step_jax(u, dt):
    # Automatic GPU/TPU acceleration
    return semi_implicit_step_jax(u, dt)
```

---

## 7. Implementation in UET Harness

### 7.1 Key Files

```
uet_core/
├── potential.py    # V(u) and V'(u)
├── energy.py       # Ω computation
├── solver.py       # Semi-implicit + backtracking
└── grader.py       # Validation grading
```

### 7.2 Solver Interface

```python
from uet_core.solver import solve

result = solve(
    model="C_I",
    params={"a": -1, "delta": 0.1, "beta": 2.0},
    domain={"L": 10, "N": 64},
    time={"T": 10, "dt": 0.01},
)

# result.trajectory: field evolution
# result.energies: Ω(t)
# result.status: PASS/FAIL
```

---

## 8. Summary

| Component | Method | Guarantee |
|-----------|--------|-----------|
| Space | Spectral/FD | 2nd order accurate |
| Time | Semi-implicit | Stable for larger dt |
| Energy | Backtracking | dΩ/dt ≤ 0 always |
| Solve | FFT | O(N log N) |

---

*Document: 01-core/04-numerics*
*Version: 0.9*
*Date: 2025-12-29*
