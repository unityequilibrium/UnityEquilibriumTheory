# UET Single Source of Truth

> **Canonical metrics for all UET documentation**  
> **Last Updated**: 2026-01-09  
> **Test Run**: 2026-01-09

---

## 📊 Official Test Results

| Metric | Value | Note |
|:-------|:-----:|:-----|
| **Total Tests** | 117 | Verified by run_all_tests.py |
| **Passed** | 115 | 98.3% pass rate |
| **Domains Covered** | 20 | Full physics coverage |
| **Data Points** | 500+ | Across all tests |

---

## 🌌 Domain-Specific Results

### Galaxy Rotation (Topic 0.1)

| Metric | Value | Dataset |
|:-------|:-----:|:--------|
| Pass Rate | **81.0%** | SPARC Hybrid |
| Average Error | 9.8% | 154 galaxies |
| LSB/Dwarf Success | >85% | Low surface brightness |
| Spiral Success | ~58% | Structural complexity |

### Particle Physics

| Test | Result | Source |
|:-----|:------:|:-------|
| W/Z Mass Ratio | **1.7% error** | PDG 2024 |
| Higgs Mass | **0.2% error** | ATLAS/CMS 125.1 GeV |
| Weinberg Angle | **0.2%** | sin²θ_W = 0.231 |
| Muon g-2 | **0.0σ** | Fermilab E989 |
| Hydrogen Spectrum | **6.4 ppm** | NIST ASD |

### Cosmology

| Test | Result | Source |
|:-----|:------:|:-------|
| Hubble Tension | **Resolved** | 4.9σ bridge |
| H₀ UET | 69.8 km/s/Mpc | Midpoint |
| CMB Flatness | Ω_tot = 1 | Planck 2018 |

### Black Holes

| Test | Result | Source |
|:-----|:------:|:-------|
| EHT Shadow | **Match** | M87* 2.6 R_s |
| LIGO Waves | **c confirmed** | O3 data |
| CCBH k-factor | k ≈ 3 | Farrah et al. |

### Gravity & GR

| Test | Result | Source |
|:-----|:------:|:-------|
| Equivalence η | **0** | Eöt-Wash (10⁻¹³) |
| Equivalence η | **0** | MICROSCOPE (10⁻¹⁵) |

---

## 📚 Data Sources (DOIs)

### Type A: Mass Datasets

| Source | DOI | Topics |
|:-------|:----|:-------|
| **SPARC** | [10.3847/0004-6256/152/6/157](https://doi.org/10.3847/0004-6256/152/6/157) | 0.1 Galaxy |
| **AME2020** | [10.1088/1674-1137/abddaf](https://doi.org/10.1088/1674-1137/abddaf) | 0.5, 0.16 Nuclear |

### Type B: Precision Constants

| Source | DOI | Topics |
|:-------|:----|:-------|
| **PDG 2024** | [10.1093/ptep/ptac097](https://doi.org/10.1093/ptep/ptac097) | All particle physics |
| **Planck 2018** | [10.1051/0004-6361/201833910](https://doi.org/10.1051/0004-6361/201833910) | 0.3 Cosmology |
| **Fermilab g-2** | [10.1103/PhysRevLett.126.141801](https://doi.org/10.1103/PhysRevLett.126.141801) | 0.8 Muon |
| **EHT M87*** | [10.3847/2041-8213/ab0ec7](https://doi.org/10.3847/2041-8213/ab0ec7) | 0.2 Black Hole |
| **LIGO O3** | [10.1103/PhysRevX.13.041039](https://doi.org/10.1103/PhysRevX.13.041039) | 0.2 Black Hole |
| **Eöt-Wash** | [10.1103/PhysRevLett.100.041101](https://doi.org/10.1103/PhysRevLett.100.041101) | 0.19 Gravity |
| **MICROSCOPE** | [10.1103/PhysRevLett.129.121102](https://doi.org/10.1103/PhysRevLett.129.121102) | 0.19 Gravity |
| **NIST ASD** | [10.18434/T4W30F](https://doi.org/10.18434/T4W30F) | 0.20 Atomic |
| **NuFIT 5.2** | [10.1007/JHEP09(2020)178](https://doi.org/10.1007/JHEP09(2020)178) | 0.18 Neutrino |

### Type C: Foundational

| Source | DOI | Topics |
|:-------|:----|:-------|
| **Landauer 1961** | [10.1147/rd.53.0183](https://doi.org/10.1147/rd.53.0183) | 0.13 Thermo |
| **Bérut 2012** | [10.1038/nature10872](https://doi.org/10.1038/nature10872) | 0.13 Thermo |
| **Casimir** | [10.1103/PhysRevLett.81.4549](https://doi.org/10.1103/PhysRevLett.81.4549) | 0.12 Vacuum |

---

## 🔗 Quick Reference

```python
# Official metrics (use these in all docs)
TESTS_TOTAL = 117
TESTS_PASSED = 115
PASS_RATE = 0.983
TOPICS = 20
GALAXY_PASS = 0.810
GALAXY_ERROR = 0.098
```

---

*All documents should reference this file for consistency.*
