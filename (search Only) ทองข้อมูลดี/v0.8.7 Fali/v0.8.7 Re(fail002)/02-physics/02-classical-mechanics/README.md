# ⚙️ Classical Mechanics ↔ UET Mapping

> การ map ระหว่าง Classical Mechanics และ UET

---

## 1. Core Mapping

```
┌─────────────────────────────────────────────────────────────────┐
│              CLASSICAL MECHANICS ↔ UET                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Classical Mech         UET                                     │
│  ─────────────────────  ─────────────────────                   │
│  Potential Energy V(x)  V(u) (per point)                       │
│  Total Energy E         Ω (functional)                          │
│  Force F = -∇V          δΩ/δu (functional derivative)          │
│  ẋ = v                 ∂u/∂t                                   │
│  Equilibrium ∇V = 0     δΩ/δu = 0                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Overdamped Limit

### 2.1 Full Newton's Law

```
m(d²x/dt²) = F - γ(dx/dt)

m = mass
F = -∇V (conservative force)
γ = friction coefficient
```

### 2.2 Overdamped (High Friction)

```
When γ >> m (friction dominates):
  m(d²x/dt²) ≈ 0
  
→ γ(dx/dt) = F = -∇V
→ dx/dt = -(1/γ)∇V
→ dx/dt = -M∇V

Where M = 1/γ (mobility)
```

### 2.3 This is Gradient Flow!

```
dx/dt = -M∇V  ⟷  ∂u/∂t = -M·δΩ/δu

Same structure!
```

---

## 3. Hamilton's Principle

### 3.1 Lagrangian Mechanics

```
L = T - V  (Kinetic - Potential)

Action: S = ∫ L dt

Hamilton's principle: δS = 0
```

### 3.2 UET Analogy

```
"Action" = Ω[u]
"Trajectory" = field configuration u(x)

Equilibrium: δΩ = 0
```

---

## 4. Conservative vs Dissipative

### 4.1 Conservative System

```
Newton: m(d²x/dt²) = -∇V
Energy: E = T + V = const

→ Oscillatory, reversible
```

### 4.2 Dissipative System (UET)

```
Overdamped: γ(dx/dt) = -∇V
Energy: dΩ/dt ≤ 0

→ Monotonic decay, irreversible
→ This is what UET describes!
```

---

## 5. Detailed Mapping

| Classical | Symbol | UET | Symbol |
|-----------|--------|-----|--------|
| Position | x | Field value | u |
| Velocity | v = dx/dt | Field rate | ∂u/∂t |
| Potential | V(x) | Local potential | V(u) |
| Force | F = -∇V | Functional derivative | -δΩ/δu |
| Mass | m | (absorbed in M) | — |
| Friction | γ | 1/Mobility | 1/M |
| Energy | E = T + V | Energy functional | Ω |

---

## 6. Particle in Potential

### 6.1 Classical 1D

```
V(x) = (a/2)x² + (b/4)x⁴  (Duffing oscillator)

Overdamped motion:
  γẋ = -V'(x) = -ax - bx³
  ẋ = -(M)(ax + bx³)
```

### 6.2 UET Field

```
V(u) = (a/2)u² + (δ/4)u⁴

Dynamics:
  ∂u/∂t = -M(au + δu³ - κ∇²u)
```

Same local dynamics, plus spatial diffusion!

---

## 7. Many-Body → Field

### 7.1 Discrete Particles

```
N particles at positions x₁, x₂, ..., xₙ
Each feels: F_i = -∂V/∂x_i

Equations of motion:
  γ(dx_i/dt) = -∂V/∂x_i
```

### 7.2 Continuum Limit

```
As N → ∞, dx → 0:
  x_i → u(x) (field)
  ∂V/∂x_i → δΩ/δu (functional derivative)
  
This is UET!
```

---

## 8. Examples

### 8.1 Harmonic Oscillator (Overdamped)

```
Classical:
  V(x) = (k/2)x²
  γẋ = -kx
  x(t) = x₀ exp(-kt/γ)

UET:
  V(u) = (k/2)u²
  ∂u/∂t = -Mku
  u(t) = u₀ exp(-Mkt)

Same exponential decay!
```

### 8.2 Double-Well

```
Classical:
  V(x) = -x² + x⁴
  Two stable positions at x = ±1

UET:
  V(u) = -u² + u⁴
  Two stable phases at u = ±1

Same bistability!
```

---

## 9. What UET Adds

| Classical | UET Extension |
|-----------|---------------|
| Point particles | Continuous field |
| Finite N | Infinite DOF |
| ODE | PDE |
| — | Interface energy κ|∇u|² |
| — | Spatial pattern formation |

---

## 10. Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   UET is the FIELD THEORY VERSION of overdamped mechanics:     │
│                                                                 │
│   Classical:   γẋ = -∇V(x)                                     │
│   UET:         ∂u/∂t = -M·δΩ/δu                                │
│                                                                 │
│   Key addition: Spatial structure via κ|∇u|²                   │
│                                                                 │
│   Both share:                                                   │
│   - Energy minimization                                         │
│   - Monotonic decay to equilibrium                              │
│   - Same potential functions V(u)                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

*Document: 02-physics/02-classical-mechanics*
*Version: 0.9*
*Date: 2025-12-29*
