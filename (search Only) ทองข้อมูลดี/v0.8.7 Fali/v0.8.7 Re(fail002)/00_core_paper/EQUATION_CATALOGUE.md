# UET Equation Catalogue

**สร้าง:** 2025-12-30
**วัตถุประสงค์:** รวบรวมทุก version ของสมการที่ใช้ใน project

---

## 📊 Summary Table

| Version | Equation | Source | Tested? |
|---------|----------|--------|---------|
| **UECT** | dE/dt = M·dC²/dt - S·dC/dt + ∇Φ | Before_Equation.md | ⚠️ Partial |
| **CH (C-only)** | ∂ₜC = -M·μ | MATH_CORE.md | ✅ Yes |
| **CH (C-I)** | ∂ₜC = -M·μ_C, ∂ₜI = -M·μ_I | MATH_CORE.md | ✅ Yes |
| **UCFE Tensor** | G_μν = (8πG/C⁴)𝒞_μν | Before_Equation.md | ❌ No |
| **IED** | E = kT·dI | Before_Equation.md | ❌ No |
| **Simplified** | 𝒱 = C/I · ΔΩ | EQUATION_STRUCTURE.md | ❌ No |

---

## 1️⃣ UECT (Original Vision)

**Source:** `research/ปรับ/เสริม/UET_Merged_2025-11-26_Before_Equation.md`

### Main Equation:
```
dE/dt = M·dC²/dt - S·dC/dt + ∇Φ - k₁∇S + k₂∇C
```

### Variables:
| Var | Meaning |
|-----|---------|
| M | Mass-Mechanism |
| C | Communication rate |
| S | Entropy |
| Φ | Synergy potential |
| E | Total energy |

### Collapse Claims:
- S=0, Φ=0, C=v → Newton: F = M·dC/dt ✓
- S=0, Φ=0, C=c → Einstein: E = MC² ✓
- C=const → Thermo: dE/dt = -k₁∇S ✓

**Status:** Original theory, not numerically implemented

---

## 2️⃣ Cahn-Hilliard (Current Code)

**Source:** `research/ปรับ/legacy_archive/docs/MATH_CORE.md`

### Single Field (C-only):
```
Ω[C] = ∫ [V(C) + (κ/2)|∇C|²] dx
∂C/∂t = -M · δΩ/δC = -M · μ
μ = V'(C) - κ∇²C
```

### Double Field (C-I):
```
Ω[C,I] = ∫ [V_C(C) + V_I(I) - β·C·I + gradients] dx
∂C/∂t = -M_C · μ_C
∂I/∂t = -M_I · μ_I
μ_C = V'_C(C) - βI - κ∇²C
```

### Potential:
```
V(u) = (a/2)u² + (δ/4)u⁴ - su
```

**Status:** ✅ Implemented in code, tested

---

## 3️⃣ UCFE (Tensor Field)

**Source:** `research/ปรับ/เสริม/UET_Merged_2025-11-26_Before_Equation.md`

### Field Equation:
```
G_μν = (8πG/C⁴) [M·C_μν - S_μν + Φ_μν + k₂∇_μC_ν - k₁∇_μS_ν]
```

### Tensors:
- C_μν = Communication Tensor
- S_μν = Entropy Tensor
- Φ_μν = Synergy Tensor

**Status:** ❌ Not implemented (needs tensor calculus library)

---

## 4️⃣ IED (Information-Energy)

**Source:** `research/ปรับ/เสริม/UET_Merged_2025-11-26_Before_Equation.md`

### Core Relation:
```
E = kT·dI    (Landauer principle)
dI/dt = α·dE/dt - β·dS/dt
dC/dt = λ(∇I - ∇S)
```

### Field Form:
```
G_μν = (8πG/C⁴) [M·C_μν - S_μν + Φ_μν + k₃T·I_μν]
```

**Status:** ❌ Not implemented

---

## 5️⃣ Simplified (Proposed)

**Source:** `research/ปรับ/legacy_archive/docs/UET_EQUATION_STRUCTURE.md`

### Value Equation:
```
𝒱 = C/I · (ΔΩ/Δt)

Where:
- 𝒱 = Value/Order gain
- C = Communication rate (openness)
- I = Isolation rate (closure)
- Ω = Disequilibrium potential
```

### Bridge Equations:
```
𝒱 ~ -T·dS/dt   (Thermodynamics bridge)
𝒱 ~ -dS_info/dt (Information bridge)
```

**Status:** ❌ Concept only, not tested

---

## 🔍 Key Differences

| Aspect | UECT | CH |
|--------|------|-----|
| **Variables** | M, C, S, Φ, E | C (or C,I) |
| **Structure** | Energy rate equation | Energy functional |
| **Dynamics** | dE/dt = ... | ∂C/∂t = -M·μ |
| **Tensors** | Yes (C_μν) | No |
| **Implemented** | No | Yes |
| **Collapse proofs** | Claimed | Not applicable |

---

## ⚠️ Conclusions

1. **มีหลาย versions ที่ต่างกัน!**
2. **UECT (original) ≠ CH (current)**
3. **Current code ใช้ CH ซึ่งไม่มี M, S, Φ variables**
4. **UCFE และ IED ไม่เคยถูก implement**

---

## 🎯 Recommendations

1. **Clarify which equation is "UET"**
2. **Test original UECT if possible**
3. **Be explicit in papers about which version**
4. **Don't mix terminology**

---

*Last Updated: 2025-12-30*
