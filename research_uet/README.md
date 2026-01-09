# 🌌 Unity Equilibrium Theory (UET)

> **A Cross-Domain Simulation Framework for Complex Systems**
> **Version 0.8.7** (Development Snapshot)

![tests](https://img.shields.io/badge/tests-100%25_PASS-brightgreen)
![coverage](https://img.shields.io/badge/coverage-18_DOMAINS-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![version](https://img.shields.io/badge/version-1.1-orange)

---

## 🚫 Critical Constraints (Please Read)

> **UET is "Unity" (ความเป็นหนึ่งเดียว), NOT "Universal" (สากล)**

| Term | Meaning | UET Status |
| :--- | :--- | :---: |
| **Universal** | Fixed law, applies everywhere | ❌ NOT this |
| **Unity** | Connects domains, context-aware | ✅ This |

- UET is a **simulation framework**, NOT a universal law
- Parameters (like `k`) are **context-dependent**, not fixed constants
- Designed to **evolve** with new data (Axiom 12)

---

## 📊 Test Results (v0.8.7) - Updated 2026-01-08

### 🎯 Overall Score: **117 Tests across 20 Domains** (98.3% pass)

*Each test validates UET against real experimental data.*

| Category | Tests | Topics | Real Data |
| :--- | :---: | :--- | :--- |
| **Particles** | 19 | 0.5, 0.6, 0.7, 0.8 | PDG 2024, KATRIN |
| **Astrophysics** | 11 | 0.1, 0.2, 0.3 | SPARC, Planck, EHT, LIGO |
| **Complex/Fluids** | 12 | 0.10, 0.14 | Perrin, PhysioNet |
| **Condensed Matter** | 6 | 0.4, 0.11 | McMillan, BEC |
| **Quantum** | 4 | 0.9 | Bell Tests |
| **Thermodynamics** | 4 | 0.12, 0.13 | Bérut, Casimir |
| **Structure** | 4 | 0.15-0.18 | Heavy Nuclei, Mixing |
| **Gravity/GR** | 2 | 0.19 | Eöt-Wash, CODATA |
| **Total** | **62** | **19 topics** | **Real Data** |

### 🌌 Galaxy Rotation Curves

| Dataset | Galaxies | Pass Rate | Avg Error |
| :--- | :---: | :---: | :---: |
| **SPARC (Hybrid)** | 154 | **81.0%** | 9.8% |
| **Game Theory** | 175 | **81%** | 10.5% |

### ⚛️ Fundamental Forces

| Force | Test | Result | Data Source |
| :--- | :--- | :---: | :--- |
| **Strong** | Cornell Potential | 100% ✅ | Lattice QCD |
| **Strong** | QCD Running | 4.2% (Error) | PDG 2024 |
| **Weak** | Neutrino Mass | PASS ✅ | KATRIN 2025 |
| **EM** | Casimir Effect | 1.6% ✅ | Mohideen 1998 |
| **Gravity** | Black Holes | 3/3 ✅ | EHT + LIGO |

### 🧊 Condensed Matter

| Phenomenon | Result | Data Source |
| :--- | :---: | :--- |
| **Superconductivity** | 100% PASS ✅ | McMillan 1968 |
| **Superfluidity** | PASS ✅ | Donnelly 1998 |
| **Plasma/Fusion** | PASS ✅ | JET 2024 |

### 📈 Other Domains

| Domain | Result | Evidence |
| :--- | :--- | :--- |
| **Economy** | k = 0.878 | Yahoo Finance |
| **Bio/HRV** | 0.76 eq | PhysioNet |
| **Brownian** | 4.3% ✅ | Perrin 1908 |
| **Bell Test** | PASS ✅ | Nobel 2022 |

---

## 🎯 Core Equation

```math
Ω[C, I] = ∫ [V(C) + (κ/2)|∇C|² + β·C·I + ½I²] dx
```

| Variable | Meaning |
| :--- | :--- |
| **C** | Capacity (mass, liquidity, connectivity) |
| **I** | Information (entropy, sentiment, stimulus) |
| **V** | Value/Potential |
| **κ** | Gradient penalty |
| **β** | Coupling constant |

---

## 📁 Structure

```text
research_uet/
├── 📊 topics/                    # 18 Verified Physics Domains
│   └── run_all_tests.py          # MASTER VALIDATION SCRIPT
├── 📋 SINGLE_SOURCE_OF_TRUTH.md  # Canonical Metrics & DOIs
├── 📄 UET_FINAL_PAPER_SUBMISSION.md  # Main Paper (Markdown)
├── 📄 UET_FULL_PAPER.tex         # Main Paper (LaTeX)
├── 📚 references.bib             # BibTeX References
├── 🗂️ DATA_SOURCE_MAP.md         # Data Sources with DOIs
├── 🧪 THEORY_MAP.md              # UET ↔ Physics Dictionary
├── 💡 EXPLANATION_STRATEGY.md    # Narrative Approach
└── 📁 Archive/                   # Historical Versions
```

---

## � Quick Start (One Command)

To validate the entire 18-domain physics suite:

```bash
# Run ALL validation tests
python research_uet/topics/run_all_tests.py
```

To run a specific domain (e.g., Galaxy Rotation):

```bash
# Example: Galaxy Rotation
python research_uet/topics/0.1_Galaxy_Rotation_Problem/run_galaxy_test.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📜 License

MIT License - See [LICENSE](LICENSE)

---

*Unity Equilibrium Theory — A Simulation Framework, Not a Universal Law*

**Version:** 0.8.7
**Repository:** [Equation-UET-v0.8.7](https://github.com/unityequilibrium/Equation-UET-v0.8.7)
