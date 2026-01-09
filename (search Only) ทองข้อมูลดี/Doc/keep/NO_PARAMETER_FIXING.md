# 🚨 NO PARAMETER FIXING POLICY
## UET Validation Standard v0.8.7

---

## ⚠️ CRITICAL RULE

**ALL UET PARAMETERS MUST BE FREE — NO FITTING TO DATA!**

---

## What This Means

1. **κ (kappa)** — Must be derived from Bekenstein bound, NOT adjusted
2. **β (beta)** — Must come from coupling theory, NOT fit to match data
3. **All constants** — Must have theoretical justification, NOT empirical tuning

---

## Why This Matters

If we fit parameters to match experimental data, we are NOT testing UET.
We would just be doing curve fitting with extra steps.

**Honest science requires:**
- Predict FIRST, compare SECOND
- Accept disagreement when it happens
- Document limitations honestly

---

## Implementation

### ✅ ALLOWED
```python
# Derive from first principles
kappa = KAPPA_BEKENSTEIN  # From holographic bound
beta = 1.0  # Natural coupling strength
```

### ❌ FORBIDDEN
```python
# DO NOT DO THIS
kappa = 0.847  # "Calibrated" to match muon g-2
beta = 1.23   # "Optimized" for galaxy rotation
```

---

## Validation Checklist

- [ ] No `fit()` or `optimize()` calls on UET parameters
- [ ] κ comes from `uet_master_equation.py` WITHOUT modification
- [ ] β is justified theoretically, not empirically
- [ ] Error percentages are HONESTLY reported
- [ ] Disagreements with data are DOCUMENTED, not hidden

---

## Exception: Calibration for Comparison

When comparing UET vs Standard Model, we MAY use:
- **Standard Model parameters** (as baseline)
- **Known physical constants** (c, ℏ, G, etc.)

But UET's OWN parameters (κ, β, γ) must remain FREE.

---

## Sign-Off

All tests in `research_uet/lab/` must comply with this policy.

Date: 2026-01-03
Version: 0.8.7
