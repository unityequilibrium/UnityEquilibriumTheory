# UET R0-E3 — Dimensional & Scaling Checklist v0.1
**Goal:** checklist ตรวจหน่วย/สเกลทุกครั้งที่เพิ่มเทอมใน Ω หรือ PDE (กันพังเงียบ)

---

## A) Choose mode first
- [ ] Dimensionless mode (default)  
- [ ] Physical mode (provide L0,C0,I0,e0,t0)

---

## B) Ω integrand consistency
ทุกเทอมต้องเป็น energy density [E]/[L]^d (physical) หรือ order-1 (dimensionless).

- [ ] Potential term: V(C), V(I)
- [ ] Gradient term: +κ/2|∇u|²  (κ>0)
- [ ] Coupling: -βCI (หรือรูปอื่นที่ประกาศชัด)

---

## C) Variational derivative consistency
- [ ] μ_C has units ([E]/[L]^d)/[C]
- [ ] μ_I has units ([E]/[L]^d)/[I]
- [ ] sign rule: +κ/2|∇u|² ⇒ μ contains -κΔu

---

## D) Dynamics
Allen–Cahn:
- [ ] ∂t u = -M μ  (M>0)
Cahn–Hilliard (ถ้า conserved):
- [ ] ∂t u = ∇·(M ∇μ)  (units differ; re-derive)

---

## E) Scaling sanity (dimensionless mode)
- [ ] κ extremely small/large → stiffness marker
- [ ] β large → risk unboundedness unless coercivity conditions hold
- [ ] use backtracks_total / dt_min as objective stiffness signals

---

## F) Done criteria for “units solved”
- [ ] units table
- [ ] nondim recipe
- [ ] declare mode in demos/config
- [ ] coercivity/boundedness stated in scaled parameters
