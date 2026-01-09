# UET R0-E3 — Symbols & Units Table v0.1
**Goal:** ปิด “Dimensional Gap” โดยล็อกหน่วย/มิติของสัญลักษณ์หลักให้ชัด  
**โหมดที่รองรับ**
1) **Dimensionless mode (default ใน harness)**: ทุกอย่างเป็นไร้มิติ  
2) **Physical mode (optional)**: กำหนดสเกลอ้างอิง (L0,C0,I0,e0,t0) แล้วแปลงเป็นไร้มิติ

---

## 1) Base dimensions (symbolic)
- **[L]**: length  
- **[T]**: time  
- **[E]**: energy  
- **[C]**: unit of field C  
- **[I]**: unit of field I  

ใน d-dimensional domain:
- \(dx^d\): [L]^d
- energy density: [E]/[L]^d

> ใน harness ใช้ 2D (d=2) และ periodic BC (spectral).

---

## 2) Canonical Ω (continuous)
C-only:
\[
\Omega_C=\int\Big(V_C(C)+\frac{\kappa}{2}|\nabla C|^2\Big)\,dx
\]

C+I:
\[
\Omega_{CI}=\int\Big(V_C(C)+V_I(I)-\beta CI+\frac{\kappa_C}{2}|\nabla C|^2+\frac{\kappa_I}{2}|\nabla I|^2\Big)\,dx
\]

---

## 3) Units table (physical mode)
### 3.1 Fields & coordinates
| Symbol | Meaning | Units |
|---|---|---|
| x | position | [L] |
| t | time | [T] |
| C(x,t) | field C | [C] |
| I(x,t) | field I | [I] |

### 3.2 Potential & derivatives
| Symbol | Meaning | Units |
|---|---|---|
| V_C(C) | potential energy density | [E]/[L]^d |
| V_C'(C) | dV/dC | ([E]/[L]^d)/[C] |
| V_I(I), V_I'(I) | analogous | ([E]/[L]^d), ([E]/[L]^d)/[I] |

### 3.3 Gradient penalties
Because \(|\nabla C|^2\sim [C]^2/[L]^2\):
\[
[\kappa]=\frac{[E]/[L]^d}{[C]^2/[L]^2}=\frac{[E]\,[L]^{2-d}}{[C]^2}
\]
Similarly:
\[
[\kappa_C]=\frac{[E]\,[L]^{2-d}}{[C]^2},\quad
[\kappa_I]=\frac{[E]\,[L]^{2-d}}{[I]^2}
\]

### 3.4 Coupling β
From \(-\beta CI\) is energy density:
\[
[\beta]=\frac{[E]/[L]^d}{[C][I]}
\]

### 3.5 Mobility (Allen–Cahn form)
For \(\partial_t C=-M_C\mu_C\) and \([\mu_C]=([E]/[L]^d)/[C]\):
\[
[M_C]=\frac{[C]/[T]}{([E]/[L]^d)/[C]}=\frac{[C]^2[L]^d}{[E][T]}
\]
\[
[M_I]=\frac{[I]^2[L]^d}{[E][T]}
\]

---

## 4) Quartic coefficients (used in harness)
If:
\[
V(C)=\frac{a}{2}C^2+\frac{\delta}{4}C^4+sC
\]
then:
\[
[a]=\frac{[E]/[L]^d}{[C]^2},\quad
[\delta]=\frac{[E]/[L]^d}{[C]^4},\quad
[s]=\frac{[E]/[L]^d}{[C]}
\]
(analogous for I)

---

## 5) Dimensionless mode (default)
Declare:
- C, I are dimensionless order-1
- x, t are scaled already
- Ω is dimensionless energy-like functional (strict mode enforces monotone decrease)

In this mode: κ, β, a, δ, s, M are all dimensionless numbers.

---

## 6) What “Dimensional Gap closed” means in this project
ขั้นต่ำต้องมี:
- units table (ไฟล์นี้)
- nondimensionalization recipe (R0-E3_Nondimensionalization_Recipe)
- ระบุว่ารันงานนี้ใช้ mode ไหน (dimensionless/physical) ใน demo narratives หรือ config
