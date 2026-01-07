# 💹 Finance Domain: Market Crash Prediction

## Goal
Predict market crashes **before they happen** using UET metrics.

---

## The Problem

**Observation:** Markets crash suddenly (1929, 2000, 2008, 2020).
**Standard Models:** Assume random walks (can't predict crashes).
**UET Approach:** Measure information flow ($C$) and insulation ($I$). Crash = Flow breakdown.

---

## The Prediction

### Core Hypothesis
> When $C/I$ drops below a critical threshold, a crash is imminent.

### Metrics

| UET Variable | Financial Interpretation | Data Source |
|:-------------|:------------------------|:------------|
| $C$ | Trading volume × Price volatility | Yahoo Finance |
| $I$ | Bid-ask spread × Settlement time | Order book data |
| $V$ | Market capitalization | Public data |
| $\Omega$ | VIX (Volatility Index) | CBOE |

### Prediction Formula

$$ \text{Crash Probability} = P(C/I < \theta) $$

Where $\theta$ = critical threshold (to be determined from historical data).

---

## Current Status: ⚠️ PARTIALLY TESTED

**What we did:**
- Analyzed S&P 500 (1995-2002) using `02_the_realization.py`
- Found $k \approx 0.33$ during Dot-Com bubble
- This is **below 1**, indicating "unhealthy" flow

**Honest Assessment:**
| Property | Status |
|:---------|:-------|
| Has prediction? | ✅ Yes |
| Free parameters? | ⚠️ 1 ($\theta$) |
| Parameter derived? | ❌ Fitted from history |
| Tested against data? | ⚠️ Retroactive only |

---

## What We Need to Do

### True Test (Prospective)

1. [ ] Calculate $C/I$ for current market (today)
2. [ ] Set threshold $\theta$ based on 2000/2008 crashes
3. [ ] **Make prediction:** "Crash within 6 months if $C/I < \theta$"
4. [ ] Wait 6 months
5. [ ] Report result **honestly**

---

## Historical Validation

| Event | Year | $k$ (C/I proxy) | Predicted? |
|:------|:-----|:----------------|:-----------|
| Dot-Com Crash | 2000 | 0.33 | ✅ (retroactive) |
| GFC | 2008 | TBD | ❓ Not tested |
| COVID Crash | 2020 | TBD | ❓ Not tested |

---

## What Would Count as Success?

| Outcome | Meaning |
|:--------|:--------|
| Correctly predicts 3/3 historical crashes | Pattern is real |
| Correctly predicts 1 future crash | Theory has predictive power |
| $\theta$ is consistent across events | Theory is universal |

---

## What Would Count as Failure?

| Outcome | Meaning |
|:--------|:--------|
| False positives (predict crash, none happens) | Theory is too sensitive |
| False negatives (crash happens, not predicted) | Theory misses key factors |
| $\theta$ varies per event | Theory is not universal |

---

*Prediction documented.*
*Prospective test pending.*
