# 🌌 Physics Domain: Galaxy Rotation Curves

## Goal
Predict galaxy rotation velocities **without dark matter** and **without free parameters**.

---

## The Problem

**Observation:** Stars at the edge of galaxies rotate faster than Newtonian gravity predicts.
**Standard Solution:** Dark matter halo (adds mass we can't see).
**UET Approach:** Information flow modifies effective gravity.

---

## The Prediction

### Method (Honest Description)

1. **Input:** Observable galaxy properties only
   - $M_{visible}$ = Total visible mass (stars + gas)
   - $R$ = Galaxy radius
   - $T$ = Average stellar temperature

2. **UET Calculation:**
   - $C_{galaxy}$ = Information exchange rate ∝ $\sqrt{GM/R}$
   - $I_{galaxy}$ = Insulation ∝ $R/c$ (signal crossing time)
   - $V_{gravity}$ = UET value ∝ $(C/I)^\alpha$

3. **Prediction:**
   $$ v_{rot}(r) = v_{Newton}(r) \cdot \left[ 1 + \frac{V_{UET}(r)}{V_{ref}} \right]^{1/2} $$

---

## Current Status: ⚠️ NOT YET TESTED

**Why?**
- We need to derive $\alpha$ theoretically (not fit it).
- Without theoretical $\alpha$, this is just curve fitting.

**Honest Assessment:**
| Property | Status |
|:---------|:-------|
| Has prediction? | ✅ Yes |
| Free parameters? | ⚠️ 1 ($\alpha$) |
| Parameter derived? | ❌ Not yet |
| Tested against data? | ❌ Not yet |

---

## Next Steps

1. [ ] Derive $\alpha$ from Landauer + Gravity theory
2. [ ] Calculate $v_{rot}$ for 10 galaxies (SPARC data)
3. [ ] Compare to observations
4. [ ] Report results **honestly** (pass or fail)

---

## What Would Count as Success?

| Outcome | Meaning |
|:--------|:--------|
| $\chi^2 < 2$ | UET fits data well |
| $\alpha$ matches derivation | Theory is self-consistent |
| Better than MOND | UET has advantage |
| Better than $\Lambda$CDM | UET is competitive |

---

## What Would Count as Failure?

| Outcome | Meaning |
|:--------|:--------|
| $\chi^2 > 10$ | UET doesn't fit data |
| $\alpha$ varies per galaxy | Theory is not universal |
| Worse than Newton alone | UET makes things worse |

---

*Prediction documented.*
*Waiting for rigorous test.*
