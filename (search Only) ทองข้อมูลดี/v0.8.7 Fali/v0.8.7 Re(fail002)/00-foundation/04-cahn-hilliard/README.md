# 🧪 Cahn-Hilliard & Landau-Ginzburg

> สมการพื้นฐานที่ UET ต่อยอด

---

## 1. Historical Context

```
1937: Landau - Phase transition theory
1950: Ginzburg-Landau - Superconductivity
1958: Cahn-Hilliard - Phase separation
2024: UET - Extension to cross-domain
```

---

## 2. Landau-Ginzburg Theory

### 2.1 Order Parameter

```
φ(x,t) = Order parameter

Examples:
  - Magnetization (magnetic)
  - Density difference (binary mixture)
  - Superconducting order (SC)
```

### 2.2 Free Energy Functional

```
F[φ] = ∫ [f(φ) + (κ/2)|∇φ|²] dx

Where:
  f(φ) = local free energy density
  κ|∇φ|² = interface energy (gradient penalty)
```

### 2.3 Double-Well Potential

```
f(φ) = a(T - Tc)φ² + bφ⁴

Below Tc: Two minima (phase separation)
Above Tc: One minimum (mixed phase)
```

---

## 3. Cahn-Hilliard Equation

### 3.1 Conservation Constraint

ถ้า φ คือ concentration → ต้อง conserve!

```
∫ φ dx = constant
```

### 3.2 Dynamics

```
∂φ/∂t = ∇·(M∇μ)

Where:
  μ = δF/δφ = chemical potential
  M = mobility
```

### 3.3 Full Equation

```
∂φ/∂t = M∇²(f'(φ) - κ∇²φ)

นี่คือ 4th-order PDE!
```

---

## 4. Allen-Cahn Equation

### 4.1 Non-Conserved Dynamics

ถ้า φ ไม่ต้อง conserve:

```
∂φ/∂t = -M·δF/δφ
      = -M(f'(φ) - κ∇²φ)

นี่คือ 2nd-order PDE!
```

### 4.2 Comparison

| Property | Allen-Cahn | Cahn-Hilliard |
|----------|------------|---------------|
| Order | 2nd | 4th |
| Conservation | ❌ No | ✅ Yes |
| Use case | Phase field | Phase separation |

---

## 5. UET Extension

### 5.1 UET Energy Functional

```
Ω[C,I] = ∫ [V_C(C) + V_I(I) - βCI 
         + (κ_C/2)|∇C|² + (κ_I/2)|∇I|²] dx
```

### 5.2 Comparison

| Cahn-Hilliard | UET |
|---------------|-----|
| Single field φ | Two fields C, I |
| f(φ) | V_C(C) + V_I(I) |
| — | -βCI (coupling!) |
| κ|∇φ|² | κ_C|∇C|² + κ_I|∇I|² |

### 5.3 Key Addition: Coupling Term

```
-β·C·I

Meaning:
  β > 0: C and I attract (stable coupling)
  β < 0: C and I repel (unstable)
```

---

## 6. Dynamics Comparison

### 6.1 Cahn-Hilliard

```
∂φ/∂t = M∇²(δF/δφ)
```

### 6.2 UET (Allen-Cahn type)

```
∂C/∂t = -M_C · δΩ/δC
∂I/∂t = -M_I · δΩ/δI
```

### 6.3 Explicit Form

```
∂C/∂t = -M_C(V'_C(C) - βI - κ_C∇²C)
∂I/∂t = -M_I(V'_I(I) - βC - κ_I∇²I)
```

---

## 7. Phase Separation Example

### 7.1 Setup

```
Initial: φ = 0 + small noise
Potential: V(φ) = -φ²/2 + φ⁴/4 (double-well)
```

### 7.2 Evolution

```
t = 0:    Random noise
t > 0:    Spinodal decomposition
t → ∞:    Two phases separated
```

### 7.3 UET Analogy

```
C = "open" phase
I = "closed" phase
β = coupling strength

→ System finds balance between C and I
```

---

## 8. Mathematical Properties

### 8.1 Energy Decay

```
dF/dt ≤ 0  (both Allen-Cahn and Cahn-Hilliard)
dΩ/dt ≤ 0  (UET)
```

### 8.2 Equilibrium

```
δF/δφ = 0  (Cahn-Hilliard)
δΩ/δC = 0, δΩ/δI = 0  (UET)
```

### 8.3 Stability

```
Lyapunov: Ω is Lyapunov function
→ All three are stable!
```

---

## 9. What UET Adds

| Standard | UET Extension |
|----------|---------------|
| Single order parameter | Multiple (C, I) |
| Phase separation | Coupled dynamics |
| Materials science | Cross-domain |
| — | C/I interpretation |

---

## 10. Summary

```
Landau-Ginzburg (1950s)
        │
        ▼
  Cahn-Hilliard (1958)
        │
        ▼
   Allen-Cahn (1979)
        │
        ▼
      UET (2024)
   ┌────┴────┐
   │ C + I   │
   │ + β     │
   │ coupling│
   └─────────┘
```

UET = Cahn-Hilliard + Two fields + Coupling + Cross-domain interpretation

---

*Document: 00-foundation/04-cahn-hilliard*
*Version: 0.9*
*Date: 2025-12-29*
