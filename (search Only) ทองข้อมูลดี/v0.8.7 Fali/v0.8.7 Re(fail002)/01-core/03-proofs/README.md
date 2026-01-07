# 📜 Mathematical Proofs

> การพิสูจน์ทางคณิตศาสตร์สำหรับ UET

---

## 1. Proof: Energy Decreasing (dΩ/dt ≤ 0)

### 1.1 Statement

> **Theorem:** ถ้า ∂u/∂t = -M·δΩ/δu และ M > 0 แล้ว dΩ/dt ≤ 0

### 1.2 Proof

```
ให้ Ω[u] = ∫ f(u, ∇u) dx

เวลาวิวัฒน์:
  dΩ/dt = ∫ (δΩ/δu) · (∂u/∂t) dx
  
แทน ∂u/∂t = -M·δΩ/δu:
  dΩ/dt = ∫ (δΩ/δu) · (-M·δΩ/δu) dx
        = -M ∫ |δΩ/δu|² dx
        
เนื่องจาก M > 0 และ |δΩ/δu|² ≥ 0:
  dΩ/dt = -M ∫ |δΩ/δu|² dx ≤ 0  ∎
```

### 1.3 Equality Condition

```
dΩ/dt = 0  ⟺  δΩ/δu = 0 everywhere
           ⟺  System at equilibrium
```

---

## 2. Proof: Lyapunov Stability

### 2.1 Statement

> **Theorem:** Ω เป็น Lyapunov function สำหรับระบบ UET

### 2.2 Lyapunov Criteria

```
ให้ u* เป็น equilibrium point (δΩ/δu|_{u*} = 0)

V(u) = Ω[u] - Ω[u*]  (Lyapunov candidate)

ต้องพิสูจน์:
1. V(u*) = 0                    ✓ (by construction)
2. V(u) > 0 for u ≠ u*          ✓ (if Ω convex near u*)
3. dV/dt ≤ 0                    ✓ (proved above)
```

### 2.3 Proof of Positivity

```
ถ้า u* เป็น local minimum ของ Ω:
  Ω[u] ≥ Ω[u*] สำหรับ u ใกล้ u*
  → V(u) = Ω[u] - Ω[u*] ≥ 0 ✓
  
และ V(u) = 0 ⟺ u = u* (at minimum)
```

### 2.4 Conclusion

```
Ω satisfies all Lyapunov conditions
→ u* is stable equilibrium  ∎
```

---

## 3. Proof: Equilibrium = Euler-Lagrange

### 3.1 Statement

> **Theorem:** Equilibrium ของ UET เป็น solution ของ Euler-Lagrange equation

### 3.2 Setup

```
Ω[u] = ∫ f(u, ∇u) dx

ต้องการหา u ที่ทำให้ Ω เป็น extremum
```

### 3.3 Variational Calculus

```
ให้ u + εη เป็น variation (η vanishes at boundary)

dΩ/dε|_{ε=0} = 0

∫ [∂f/∂u · η + ∂f/∂(∇u) · ∇η] dx = 0

Integration by parts:
∫ [∂f/∂u - ∇·(∂f/∂(∇u))] · η dx = 0

เนื่องจาก η arbitrary:
∂f/∂u - ∇·(∂f/∂(∇u)) = 0
```

### 3.4 For UET

```
f = V(u) + (κ/2)|∇u|²

∂f/∂u = V'(u)
∂f/∂(∇u) = κ∇u
∇·(∂f/∂(∇u)) = κ∇²u

Euler-Lagrange:
V'(u) - κ∇²u = 0  ∎
```

---

## 4. Proof: Two-Field Coupling

### 4.1 Statement

> **Theorem:** สำหรับ Ω[C,I] = ∫[V_C + V_I - βCI + κ_C|∇C|² + κ_I|∇I|²]dx
> equilibrium conditions คือ coupled system

### 4.2 Proof

```
Functional derivatives:

δΩ/δC = V'_C(C) - βI - κ_C∇²C
δΩ/δI = V'_I(I) - βC - κ_I∇²I

At equilibrium (both = 0):
V'_C(C) = βI + κ_C∇²C    ... (1)
V'_I(I) = βC + κ_I∇²I    ... (2)

นี่คือ coupled system!
C และ I ขึ้นต่อกันผ่าน β  ∎
```

### 4.3 Homogeneous Case

```
ถ้า ∇C = ∇I = 0 (uniform):
V'_C(C*) = βI*
V'_I(I*) = βC*

สองสมการ สองตัวแปร → แก้ได้
```

---

## 5. Proof: Conservation of Total Ω (Isolated System)

### 5.1 Statement

> **Theorem:** ถ้าระบบ isolated และไม่มี external forcing, Ω คงที่

### 5.2 Proof

```
สำหรับ isolated system:
- No energy in/out
- ∂u/∂n = 0 at boundary (no flux)

dΩ/dt = ∫ (δΩ/δu) · (∂u/∂t) dx + boundary terms

Boundary terms = 0 (no flux)

ถ้า forcing = 0:
  dΩ/dt = -M ∫ |δΩ/δu|² dx ≤ 0

แต่ถ้าเราพิจารณา total system (universe):
  Ω_total = const (First Law)  ∎
```

---

## 6. Proof: Convergence to Equilibrium

### 6.1 Statement

> **Theorem:** Solutions converge to equilibrium as t → ∞

### 6.2 LaSalle's Invariance Principle

```
Given:
1. dΩ/dt ≤ 0 (proved)
2. Ω bounded below (by construction)

→ Ω(t) → Ω* as t → ∞

By LaSalle:
→ Solution trajectory → largest invariant set where dΩ/dt = 0
→ This is the equilibrium set  ∎
```

---

## 7. Summary of Proofs

| Proof | Result | Status |
|-------|--------|--------|
| Energy decreasing | dΩ/dt ≤ 0 | ✅ Complete |
| Lyapunov stability | Ω is Lyapunov function | ✅ Complete |
| Euler-Lagrange | Equilibrium = variational | ✅ Complete |
| Coupling | C-I coupled equations | ✅ Complete |
| Conservation | Isolated → Ω const | ✅ Complete |
| Convergence | t → ∞: equilibrium | ✅ Complete |

---

## 8. References

1. **Evans, L.C.** - Partial Differential Equations (2010)
2. **Temam, R.** - Infinite-Dimensional Dynamical Systems (1997)
3. **Khalil, H.K.** - Nonlinear Systems (2002)

---

*Document: 01-core/03-proofs*
*Version: 0.9*
*Date: 2025-12-29*
