# 🧶 Legacy Code Audit: UET Black Hole Analysis
**Date:** 2025-12-30
**Status:** Recovered
**Missing Link:** I previously ignored `research/(เอ๋อ)01-physics/black-hole-uet/01_data/code`.

---

## 1. Discovered Architecture
The user had a fully developed pipeline (`ultimate_ccbh_analysis.py`) that I failed to utilize.

### 📜 The "Old Equation" (Confirmed)
File: `ultimate_ccbh_analysis.py` (Line 218)
```python
def ccbh_model(log_a, log_M0, k):
    """CCBH model: log(M_BH) = log(M_0) + k * log(a)"""
    return log_M0 + k * log_a
```
This matches my derivation exactly. The friction wasn't mathematical; it was **Operational**.

### 🧪 What They Already Tested
| Script | Logic | Status |
|--------|-------|--------|
| `ultimate_ccbh_analysis.py` | Full multi-model fit ($k=0, 1, 2.8, 3$) | Used Shen 2011 (Quasars) + K&H (Local) |
| `test_uet_prediction.py` | Comparison of $k=2.8$ vs $k=3$ | V/Vmax corrected Shen data |
| `ccbh_real_analysis.py` | Attempt at High-z validation | **Failed due to Selection Bias** |

## 2. Why The User Was Angry
1.  **Duplication:** I wrote `ccbh_uet_test.py` which did 10% of what `ultimate_ccbh_analysis.py` already does.
2.  **Context Loss:** I treated Kormendy-Ho as a "new discovery", but they already had a loader for it (Lines 66-117 in `ultimate`).
3.  **The Real Challenge:** They didn't need me to *write* a script; they needed me to **fix the methodology** because their script kept finding $k < 0$ (Standard GR) when using Shen Quasars.

## 3. The Correct Forward Path
Don't write new scripts. **Fix theirs.**
- **Problem:** Shen 2011 is biased (Luminous Quasars).
- **Solution:** Modify `ultimate_ccbh_analysis.py` to filter for **"Dead" Progenitors** or use the **Progenitor-descendant evolution logic** I sketched in `ccbh_uet_test.py` but *integrated* into their robust framework.

**Next Step:** Propose to refactor `ultimate_ccbh_analysis.py` to include the specific "Dead Galaxy" logic which was missing from their "Quasar-focused" approach.
