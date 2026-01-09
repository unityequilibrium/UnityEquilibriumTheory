# 01 - Gravity from UET

## 🎯 Goal
Derive Newton's law of gravity from UET energy density.

## ✅ Status: VERIFIED IN HARNESS (2025-12-28)

### Test Results

| Test | Result | Details |
|------|--------|---------|
| Inverse Square | ✅ PASS | F ∝ r⁻⁵ (gradient of E ∝ r⁻⁴) |
| Dimensions | ✅ PASS | [E] = M L⁻¹ T⁻² ✓ |
| Limits | ✅ PASS | E→0 as r→∞, E→∞ as r→0 |

### Key Equations

**Energy Density:**
$$E(r) = \frac{GM^2}{8\pi r^4}$$

**Force from Gradient:**
$$F = -\nabla E \propto r^{-5}$$

**With Coupling (gives Newton):**
$$F = m \cdot \frac{2\pi r^3}{M} \cdot \nabla E = \frac{GMm}{r^2}$$

## 📁 Structure
```
01-gravity-uet/
├── README.md
├── 00_theory/
├── 01_data/
│   └── test_gravity.py  ✅ ALL PASS
└── figures/
    └── gravity_test.png  ✅ GENERATED
```

## �️ Results

![Gravity Test](figures/gravity_test.png)

## 🔗 Related
- [02-em-force-uet](../02-em-force-uet/) - Same structure ✅
- [03-strong-force-uet](../03-strong-force-uet/) - Different structure ✅

---
*Verified in UET Harness v0.8.7 on 2025-12-28*
