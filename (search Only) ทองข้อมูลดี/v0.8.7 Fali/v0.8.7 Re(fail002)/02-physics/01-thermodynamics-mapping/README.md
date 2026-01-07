# 🌡️ Thermodynamics ↔ UET Mapping

> การ map ระหว่าง Thermodynamics และ UET อย่างเป็นทางการ

---

## 1. Core Mapping

```
┌─────────────────────────────────────────────────────────────────┐
│                 THERMODYNAMICS ↔ UET                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Thermodynamics         UET                                     │
│  ─────────────────────  ─────────────────────                   │
│  Free Energy F          Ω (Energy functional)                   │
│  dF ≤ 0                 dΩ/dt ≤ 0                              │
│  F = U - TS             Ω = ∫[V + κ|∇u|²]dx                    │
│  Chemical potential μ   δΩ/δu                                  │
│  Equilibrium dF = 0     δΩ/δu = 0                              │
│  Work W = -ΔF           𝒱 = -ΔΩ                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Mapping

| Thermodynamics | Symbol | UET | Symbol |
|----------------|--------|-----|--------|
| Free Energy | F | Energy Functional | Ω |
| Internal Energy | U | Potential Energy | ∫V(u)dx |
| Entropy term | -TS | Interface Energy | ∫κ|∇u|²dx |
| Temperature | T | (implicit in V) | — |
| Chemical Potential | μ = ∂F/∂N | Functional Derivative | δΩ/δu |
| Available Work | W_max = -ΔF | Value | 𝒱 = -ΔΩ |

---

## 3. Laws Correspondence

### 3.1 Zeroth Law

```
Thermo: Systems in mutual equilibrium have same T
UET:    Systems at equilibrium have δΩ/δu = 0
```

### 3.2 First Law

```
Thermo: ΔU = Q - W (energy conservation)
UET:    Ω conserved in isolated system
```

### 3.3 Second Law

```
Thermo: dS_universe ≥ 0, or dF ≤ 0 (at const T)
UET:    dΩ/dt ≤ 0 (gradient flow guarantee)

THIS IS THE KEY CONNECTION!
```

### 3.4 Third Law

```
Thermo: S → 0 as T → 0
UET:    At ground state, Ω is at minimum
```

---

## 4. Gradient Flow as Relaxation

### 4.1 Thermodynamic Relaxation

```
ระบบ thermodynamic ที่ไม่อยู่ที่สมดุล จะ relax ไปหา equilibrium

Rate ~ (driving force) × (mobility)
     ~ ∇μ × M

→ Diffusion equation, Fourier's law, etc.
```

### 4.2 UET Dynamics

```
∂u/∂t = -M · δΩ/δu

Same structure!
- δΩ/δu = driving force (like -∇μ)
- M = mobility
```

---

## 5. Phase Transitions

### 5.1 Landau Theory (Thermo)

```
F(φ, T) = F₀ + a(T-Tc)φ² + bφ⁴

T > Tc: Single minimum at φ = 0
T < Tc: Two minima (phase separation)
```

### 5.2 UET Double-Well

```
V(u) = (a/2)u² + (δ/4)u⁴

a > 0: Single well
a < 0: Double well (phase separation!)

Same physics, same math!
```

---

## 6. Examples

### 6.1 Heat Diffusion

```
Thermo: ∂T/∂t = α∇²T  (Fourier's law)

UET:    Ω = ∫(1/2)|∇T|² dx
        δΩ/δT = -∇²T
        ∂T/∂t = -M·(-∇²T) = M∇²T  ✓
```

### 6.2 Chemical Diffusion

```
Thermo: ∂c/∂t = D∇²c  (Fick's law)

UET:    Ω = ∫f(c) + (κ/2)|∇c|² dx
        ∂c/∂t = M∇²(δΩ/δc)  (Cahn-Hilliard)
```

---

## 7. What UET Adds to Thermo

| Standard Thermo | UET Extension |
|-----------------|---------------|
| Single variable (T, P, c) | Field u(x,t) |
| Homogeneous systems | Spatial variation |
| Discrete states | Continuous dynamics |
| — | C/I interpretation |
| — | Cross-domain language |

---

## 8. Validation

### 8.1 Test: Heat Equation

```
Run UET simulation with:
- V(u) = 0 (no local potential)
- κ > 0 (diffusion)

Expected: ∂u/∂t = κM∇²u
Result: Matches heat equation ✓
```

### 8.2 Test: Phase Separation

```
Run UET simulation with:
- V(u) = double-well
- κ > 0

Expected: Spinodal decomposition
Result: Matches Cahn-Hilliard ✓
```

---

## 9. Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Thermodynamics provides the PHYSICAL BASIS for UET:          │
│                                                                 │
│   - Free Energy F → Ω                                          │
│   - Second Law dF ≤ 0 → dΩ/dt ≤ 0                              │
│   - Equilibrium dF = 0 → δΩ/δu = 0                             │
│   - Available Work → Value 𝒱                                   │
│                                                                 │
│   UET is NOT new physics, it's Thermodynamics in field form!   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

*Document: 02-physics/01-thermodynamics-mapping*
*Version: 0.9*
*Date: 2025-12-29*
