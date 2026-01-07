# ⚡ Free Energy Concept

> แนวคิดพลังงานอิสระสำหรับ UET

---

## 1. What is Free Energy?

### 1.1 Physical Meaning

```
Free Energy = พลังงานที่ "ใช้ได้" จริงๆ ในการทำงาน
            = Total Energy - "ถูกล็อก" โดย Entropy
```

### 1.2 Helmholtz Free Energy (F)

```
F = U - TS

U = Internal energy (พลังงานภายใน)
T = Temperature (อุณหภูมิ)
S = Entropy (เอนโทรปี)
```

**ใช้เมื่อ:** ระบบที่ T และ V คงที่

### 1.3 Gibbs Free Energy (G)

```
G = H - TS = U + PV - TS

H = Enthalpy = U + PV
```

**ใช้เมื่อ:** ระบบที่ T และ P คงที่

---

## 2. Why Free Energy Minimizes

### 2.1 Second Law Rewritten

จากกฎข้อ 2 (Entropy increases):
```
dS_universe ≥ 0
dS_system + dS_surroundings ≥ 0
```

ที่ constant T:
```
dS_surroundings = -Q/T = -dU/T
```

รวมกัน:
```
dS_system - dU/T ≥ 0
T·dS - dU ≥ 0
-(dU - T·dS) ≥ 0
-dF ≥ 0
dF ≤ 0  ✓
```

> [!IMPORTANT]
> **Spontaneous processes ต้องทำให้ F ลด!**

---

## 3. Connection to UET

### 3.1 UET Energy Functional

```
Ω[u] = ∫ [V(u) + (κ/2)|∇u|²] dx
```

### 3.2 Mapping to Free Energy

| Free Energy | UET |
|-------------|-----|
| F = U - TS | Ω = ∫ω dx |
| U (internal) | V(u) (potential) |
| -TS (entropy) | κ|∇u|² (interface) |

### 3.3 Key Insight

```
Ω plays the role of Free Energy!

dΩ/dt ≤ 0 ↔ dF/dt ≤ 0 (Second Law)
```

---

## 4. Proof: Ω = Free Energy (Formal)

### 4.1 Setup

ระบบ field u(x,t) ที่ constant T:

```
Total entropy: S = -∫ s(u, ∇u) dx
Internal: U = ∫ e(u, ∇u) dx
```

### 4.2 Free Energy Functional

```
F[u] = U[u] - T·S[u]
     = ∫ [e(u,∇u) + T·s(u,∇u)] dx
     = ∫ f(u, ∇u) dx
```

### 4.3 Standard Form

เลือก:
```
f(u, ∇u) = V(u) + (κ/2)|∇u|²
```

→ `F[u] = Ω[u]` ✓

---

## 5. Variational Principle

### 5.1 Equilibrium = Minimum F

```
At equilibrium:
  δF/δu = 0
  → V'(u) - κ∇²u = 0
```

### 5.2 Euler-Lagrange Equation

```
δΩ/δu = ∂V/∂u - κ∇²u = 0
```

นี่คือสมการที่กำหนด equilibrium state!

---

## 6. Examples

### 6.1 Ideal Gas

```
F = NkT[ln(N/V) - 1 + const]
dF = -SdT - PdV + μdN
```

### 6.2 Phase Transition (Landau)

```
F = ∫ [a(T-Tc)φ² + bφ⁴] dx
```

### 6.3 UET Double-Well

```
Ω = ∫ [aφ² + δφ⁴ - sφ + (κ/2)|∇φ|²] dx
```

---

## 7. Summary

| Concept | Definition | Role in UET |
|---------|------------|-------------|
| Free Energy | F = U - TS | Model for Ω |
| Minimization | dF ≤ 0 | → dΩ/dt ≤ 0 |
| Equilibrium | δF = 0 | → δΩ/δu = 0 |
| Second Law | Spontaneous | Gradient flow |

---

*Document: 00-foundation/02-free-energy*
*Version: 0.9*
*Date: 2025-12-29*
