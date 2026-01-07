# UET R0-E3 — Nondimensionalization Recipe v0.1
**Goal:** สูตรแปลง physical → dimensionless ที่ชัด เพื่อให้เทียบสากล/ทำ calibration ได้จริง  
(harness ปัจจุบันใช้ dimensionless mode อยู่แล้ว)

---

## 1) Choose reference scales
เลือกสเกล:
- \(L_0\) length scale
- \(C_0, I_0\) field scales
- \(e_0\) energy density scale ([E]/[L]^d)
- \(t_0\) time scale

Define:
\[
\tilde x=x/L_0,\quad \tilde t=t/t_0,\quad \tilde C=C/C_0,\quad \tilde I=I/I_0
\]
and \(dx=L_0^d d\tilde x\).

---

## 2) Scale Ω (C-only)
Assume \(V(C)=e_0 \tilde V(\tilde C)\).  
Then:
\[
\tilde\Omega := \frac{\Omega}{e_0 L_0^d}
= \int\Big(\tilde V(\tilde C)+\frac{\tilde\kappa}{2}|\tilde\nabla \tilde C|^2\Big)\,d\tilde x
\]
with:
\[
\boxed{\tilde\kappa=\frac{\kappa C_0^2}{e_0 L_0^2}}
\]

---

## 3) Scale coupling (C+I)
\[
-\beta CI = -\beta C_0 I_0\,\tilde C\tilde I
\quad\Rightarrow\quad
\boxed{\tilde\beta=\frac{\beta C_0 I_0}{e_0}}
\]
and:
\[
\tilde\kappa_C=\frac{\kappa_C C_0^2}{e_0 L_0^2},\quad
\tilde\kappa_I=\frac{\kappa_I I_0^2}{e_0 L_0^2}
\]

---

## 4) Quartic coefficients
If \(V(C)=aC^2/2+\delta C^4/4+sC\) then:
\[
\boxed{\tilde a=\frac{aC_0^2}{e_0}},\quad
\boxed{\tilde\delta=\frac{\delta C_0^4}{e_0}},\quad
\boxed{\tilde s=\frac{sC_0}{e_0}}
\]
(and similarly for I)

---

## 5) Scale dynamics (Allen–Cahn)
\[
\partial_t C=-M_C\mu_C
\]
leads to:
\[
\partial_{\tilde t}\tilde C = -\tilde M_C \tilde\mu_C,\quad
\boxed{\tilde M_C=\frac{t_0 M_C e_0}{C_0^2}}
\]
Similarly:
\[
\boxed{\tilde M_I=\frac{t_0 M_I e_0}{I_0^2}}
\]

**Convenient choice:** pick \(t_0=C_0^2/(M_C e_0)\) so \(\tilde M_C=1\).

---

## 6) How to use this in the project
- ถ้า “dimensionless mode”: ถือว่าพารามิเตอร์ในโค้ดคือ \(\tilde{\cdot}\) ทั้งหมด  
- ถ้าอยาก “โยงสากล/ของจริง”: กำหนด (L0,C0,I0,e0,t0) แล้วแปลงย้อนกลับ

Dimensional Gap ปิดเมื่อเราพูดได้ชัดว่า “ชุด demo นี้อยู่ในสเกลอะไร”
