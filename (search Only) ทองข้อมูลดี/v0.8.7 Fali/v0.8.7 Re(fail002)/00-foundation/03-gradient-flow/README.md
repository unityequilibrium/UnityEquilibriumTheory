# 🌊 Gradient Flow Mathematics

> คณิตศาสตร์พื้นฐานของ Gradient Flow สำหรับ UET

---

## 1. Definition

### 1.1 Basic Gradient Flow

```
∂u/∂t = -∇F(u)

Where:
  u = state variable
  F = objective function (energy-like)
  ∇F = gradient of F
```

### 1.2 Functional Gradient Flow

สำหรับ functional Ω[u]:

```
∂u/∂t = -M · δΩ/δu

Where:
  u(x,t) = field variable
  Ω[u] = energy functional
  δΩ/δu = functional derivative (variational)
  M = mobility (positive constant)
```

---

## 2. Functional Derivative

### 2.1 Definition

ถ้า `Ω[u] = ∫ f(u, ∇u) dx` แล้ว:

```
δΩ/δu = ∂f/∂u - ∇·(∂f/∂(∇u))
```

### 2.2 Example: UET Energy Functional

```
Ω = ∫ [V(u) + (κ/2)|∇u|²] dx

δΩ/δu = V'(u) - κ∇²u
```

---

## 3. Energy Decreasing Property

### 3.1 Theorem

> **Theorem:** ถ้า `∂u/∂t = -M · δΩ/δu` และ M > 0 แล้ว `dΩ/dt ≤ 0`

### 3.2 Proof

```
dΩ/dt = ∫ (δΩ/δu) · (∂u/∂t) dx

แทน ∂u/∂t = -M · δΩ/δu:

dΩ/dt = ∫ (δΩ/δu) · (-M · δΩ/δu) dx
      = -M ∫ |δΩ/δu|² dx
      ≤ 0  ∀t

เพราะ M > 0 และ |δΩ/δu|² ≥ 0 เสมอ  ∎
```

---

## 4. Equilibrium Conditions

### 4.1 Equilibrium State

ที่สมดุล: `∂u/∂t = 0`

จากสมการ: `-M · δΩ/δu = 0`

เนื่องจาก M ≠ 0: `δΩ/δu = 0`

### 4.2 Equilibrium Equation

```
δΩ/δu = 0
→ V'(u) - κ∇²u = 0
→ V'(u) = κ∇²u
```

นี่คือ **Euler-Lagrange equation** ของ Ω!

---

## 5. Lyapunov Stability

### 5.1 Ω as Lyapunov Function

```
V(u) = Ω[u] (Lyapunov function)

Conditions:
1. V(u*) = 0 at equilibrium u*     ✓ (can shift)
2. V(u) > 0 for u ≠ u*             ✓ (if Ω bounded below)
3. dV/dt ≤ 0                        ✓ (proved above!)
```

### 5.2 Conclusion

> Ω เป็น Lyapunov function → ระบบ stable!

---

## 6. Types of Gradient Flow

### 6.1 L² Gradient Flow (Allen-Cahn)

```
∂u/∂t = -δΩ/δu = -V'(u) + κ∇²u
```

ใช้สำหรับ: phase field, reaction-diffusion

### 6.2 H⁻¹ Gradient Flow (Cahn-Hilliard)

```
∂u/∂t = ∇·(M∇(δΩ/δu))
      = M∇²(V'(u) - κ∇²u)
```

ใช้สำหรับ: phase separation, conserved dynamics

### 6.3 UET Uses Both!

```
Model C_only: Allen-Cahn type
Model C_I:    Mixed type with coupling
```

---

## 7. Connection to Physics

| Physics | Gradient Flow Form |
|---------|-------------------|
| Heat diffusion | ∂T/∂t = α∇²T |
| Diffusion | ∂c/∂t = D∇²c |
| Overdamped mechanics | γẋ = -∇V(x) |
| Variational | ∂u/∂t = -δΩ/δu |

**ทั้งหมดมีรูปแบบเดียวกัน: ∂(state)/∂t = -∇(energy)**

---

## 8. Summary

| Property | Formula |
|----------|---------|
| Dynamics | ∂u/∂t = -M·δΩ/δu |
| Energy decrease | dΩ/dt ≤ 0 |
| Equilibrium | δΩ/δu = 0 |
| Stability | Ω is Lyapunov function |

---

*Document: 00-foundation/03-gradient-flow*
*Version: 0.9*
*Date: 2025-12-29*
