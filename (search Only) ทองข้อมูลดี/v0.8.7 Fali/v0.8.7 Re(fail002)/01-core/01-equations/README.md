# ⚡ UET Core Equations

> สมการหลักของ Unity Equilibrium Theory

---

## 1. Energy Functional Ω

### 1.1 Single Field (Model C_only)

```
Ω[C] = ∫ [V(C) + (κ/2)|∇C|²] dx

Where:
  V(C) = Potential energy density
  κ|∇C|² = Interface/gradient energy
```

### 1.2 Two Fields (Model C_I)

```
Ω[C,I] = ∫ [V_C(C) + V_I(I) - β·C·I 
         + (κ_C/2)|∇C|² + (κ_I/2)|∇I|²] dx

Where:
  V_C(C) = Potential for C field
  V_I(I) = Potential for I field
  -β·C·I = Coupling term (β > 0)
  κ_C, κ_I = Gradient penalties
```

---

## 2. Quartic Potential V(u)

### 2.1 General Form

```
V(u) = (a/2)u² + (δ/4)u⁴ - s·u

Parameters:
  a = Curvature (can be negative for double-well)
  δ = Quartic stabilization (δ > 0 for bounded)
  s = Bias / symmetry breaking
```

### 2.2 Special Cases

| Case | Condition | Shape |
|------|-----------|-------|
| Single well | a > 0, s = 0 | Parabola |
| Double well | a < 0, s = 0 | Two minima |
| Biased | s ≠ 0 | Asymmetric |

### 2.3 Derivatives

```
V'(u) = a·u + δ·u³ - s
V''(u) = a + 3δ·u²
```

---

## 3. Dynamics (Gradient Flow)

### 3.1 General Form

```
∂u/∂t = -M · δΩ/δu
```

### 3.2 Functional Derivative

```
δΩ/δC = V'_C(C) - β·I - κ_C·∇²C
δΩ/δI = V'_I(I) - β·C - κ_I·∇²I
```

### 3.3 Full Dynamics

```
∂C/∂t = -M_C · [V'_C(C) - β·I - κ_C·∇²C]
∂I/∂t = -M_I · [V'_I(I) - β·C - κ_I·∇²I]
```

---

## 4. Value Definition

### 4.1 𝒱 = -ΔΩ

```
𝒱 := Ω(t₀) - Ω(t₁) = -ΔΩ

Meaning:
  𝒱 > 0: System improved (Ω decreased)
  𝒱 = 0: No change
  𝒱 < 0: System worsened (shouldn't happen!)
```

### 4.2 Properties

```
Since dΩ/dt ≤ 0:
  Ω(t₁) ≤ Ω(t₀)
  ΔΩ = Ω(t₁) - Ω(t₀) ≤ 0
  𝒱 = -ΔΩ ≥ 0  ✓
```

---

## 5. Equilibrium Conditions

### 5.1 At Equilibrium

```
∂C/∂t = 0, ∂I/∂t = 0

→ δΩ/δC = 0, δΩ/δI = 0
→ V'_C(C) - β·I - κ_C·∇²C = 0
→ V'_I(I) - β·C - κ_I·∇²I = 0
```

### 5.2 Homogeneous Solution

ถ้า ∇C = ∇I = 0 (uniform):
```
V'_C(C*) = β·I*
V'_I(I*) = β·C*
```

---

## 6. Parameters Table

| Symbol | Name | Typical Range | Unit |
|--------|------|---------------|------|
| a | Curvature | [-10, 10] | E/L² |
| δ | Quartic | [0.01, 10] | E/L⁴ |
| s | Bias | [-1, 1] | E/L |
| κ | Gradient penalty | [0.01, 1] | E·L² |
| β | Coupling | [0, 10] | E |
| M | Mobility | [0.1, 10] | L²/(E·T) |

---

## 7. Boundary Conditions

### 7.1 Periodic

```
u(0) = u(L)
∂u/∂x|₀ = ∂u/∂x|_L
```

### 7.2 Neumann (No-flux)

```
∂u/∂n|_∂Ω = 0
```

### 7.3 Dirichlet

```
u|_∂Ω = u₀ (fixed)
```

---

## 8. Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    EQUATION SUMMARY                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  State:     C(x,t), I(x,t)                                     │
│  Energy:    Ω[C,I]                                              │
│  Dynamics:  ∂u/∂t = -M·δΩ/δu                                   │
│  Guarantee: dΩ/dt ≤ 0                                          │
│  Value:     𝒱 = -ΔΩ ≥ 0                                        │
│  Equilib:   δΩ/δu = 0                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

*Document: 01-core/01-equations*
*Version: 0.9*
*Date: 2025-12-29*
