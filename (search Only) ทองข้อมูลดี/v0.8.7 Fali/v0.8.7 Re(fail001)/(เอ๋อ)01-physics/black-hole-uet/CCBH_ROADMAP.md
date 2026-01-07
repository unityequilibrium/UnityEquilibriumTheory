# 🗺️ CCBH Research Roadmap: From k = -2 to k = +2.8

## 1. Problem Definition
Current analysis shows **k ≈ -1.93 ± 0.02** using Quasar data (Shen 2011). This contradicts the UET prediction of **k = 2.8**.

**Hypothesis**: The discrepancy is caused by **Selection Bias (Malmquist Bias)** and **AGN Accretion**, not a failure of the UET core theory.

---

## 2. Phase 1: Bias Correction & Simulations (Week 1-2)

### 2.1 Malmquist Bias Correction
- **Task**: Implement a sophisticated volume-weighting ($V/V_{max}$) or Maximum Likelihood method in `selection_bias.py`.
- **Goal**: See if correcting for luminosity limits shifts $k$ toward zero or positive.

### 2.2 Mock Catalog Simulation
- **Task**: Generate "Mock Quasars" with a built-in UET growth ($k=2.8$).
- **Task**: Apply SDSS flux limits to this mock data.
- **Goal**: Can we reproduce an "observed" $k \approx -2$ even when the "true" $k$ is $2.8$?

---

## 3. Phase 2: Data Quality Upgrade (Week 3-4)

### 3.1 Quiescent Galaxy Focus
- **Task**: Filter SDSS DR16 for "Dead" Elliptical galaxies (Low Star Formation Rate).
- **Goal**: Eliminate growth from gas accretion (AGN masking).

### 3.2 Host-Matching Analysis
- **Task**: Instead of $M_{BH}$ vs $z$, analyze $\Gamma = M_{BH} / M_{stellar}$.
- **Goal**: Test if the ratio evolves as $(1+z)^{-k}$.

---

## 4. Phase 3: Theoretical Refinement (Week 5+)

### 4.1 Coupling Variance
- **Task**: Investigate if $k$ is a constant or if it varies with local energy density.
- **Goal**: Derive the "Back-reaction" term in UET for dense objects like BHs.

### 4.2 Multi-Energy Validation
- **Task**: Test alternative energy functionals (e.g., incorporating Bekenstein-Hawking entropy).

---

## 5. Success Criteria

| Milestone | Metric | Status |
|-----------|--------|--------|
| Replicate $k=-2$ in simulation | Bias confirmed | ⏳ Pending |
| Shift binned k toward positive | Correction success | ⏳ Pending |
| Clean Elliptical Sample | N > 100 at z > 0.5 | ⏳ Pending |

---

> [!IMPORTANT]
> **Honest Reporting**: We must continue to report the $k \approx -2$ finding in all public summaries until it is mathematically proven to be a bias artifact.

*Last updated: 2025-12-29*
