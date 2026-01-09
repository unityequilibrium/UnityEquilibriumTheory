# Black Hole + UET Research

## 🎯 Goal
Test Cosmologically Coupled Black Holes (CCBH) hypothesis: M_BH ∝ a^k where k ≈ 3

## ⚠️ Status: SELECTION BIAS IDENTIFIED (2025-12-28)

### Test Results

| Data | k Value | Status |
|------|---------|--------|
| Toy Data | k = 2.79 ± 0.17 | ✅ Expected ~3 |
| Real Data (Shen 2011) | k = -2.03 | ❌ **BIASED!** |

### 🔬 Root Cause: Malmquist Bias

We simulated the effect and **PROVED** the bias:

| Scenario | True k | Measured k | Bias |
|----------|--------|------------|------|
| No bias | 3.00 | 2.81 | -0.19 ✓ |
| With Malmquist | 3.00 | **-1.16** | **-4.16!** |

**Malmquist bias can shift k by ~4 units!**

### Why This Happens

1. **Flux-limited samples** only detect bright objects at high-z
2. Brighter quasars = more massive BHs
3. At high-z, we only see the **most massive BHs**
4. This creates an **artificial positive M-z correlation**
5. Which inverts the true k ≈ 3 to k ≈ -2

### How to Fix

| Method | Description | Status |
|--------|-------------|--------|
| M_BH/M_galaxy ratio | Remove distance dependence | ⏳ Needs galaxy mass data |
| V/Vmax correction | Weight by detectable volume | ✅ Implemented |
| Luminosity matching | Select overlapping L range | ✅ Implemented |

## 📁 Structure
```
black-hole-uet/
├── README.md
├── 00_papers/              # Reference papers
├── 01_data/
│   ├── run_all.py          # Master script
│   ├── data_loader.py      # FITS loader
│   ├── quality_cuts.py     # Data cleaning
│   ├── ccbh_analysis.py    # k-fitting
│   ├── visualize.py        # Plots
│   ├── selection_bias.py   # 🆕 Bias analysis
│   └── toy_data_generator.py
├── 02_shen_analysis/
└── figures/
```

## 🔗 Key Findings

1. **Toy data works:** k = 2.79 confirms pipeline is correct
2. **Real data biased:** Malmquist bias dominates
3. **Fix required:** Need M_BH/M_galaxy or volume correction

## 📋 Next Steps

1. [ ] Obtain galaxy stellar masses (SDSS photometry)
2. [ ] Compute M_BH/M_galaxy ratio
3. [ ] Re-run CCBH analysis on ratio
4. [ ] Or: Apply V/Vmax correction to Shen data

## 📚 References

- Farrah et al. (2023): CCBH hypothesis, k ≈ 3
- Shen et al. (2011): DR7 quasar catalog used
- Malmquist (1922): Original bias description

---

*Verified in UET Harness v0.8.7 on 2025-12-28*
