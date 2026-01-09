# 🌌 UET Research Directory

> **Unity Equilibrium Theory — A Cross-Domain Simulation Framework**  
> **Version 0.8.7** | Last Updated: 2026-01-09

![Tests](https://img.shields.io/badge/Tests-117_(98.3%25_PASS)-brightgreen)
![Topics](https://img.shields.io/badge/Topics-20_Domains-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚫 Important: Unity ≠ Universal

> **UET is "Unity" (ความเป็นหนึ่งเดียว), NOT "Universal" (สากล)**

| Term | Meaning | UET Status |
|:-----|:--------|:----------:|
| **Universal** | Fixed law, applies everywhere | ❌ NOT this |
| **Unity** | Connects domains, context-aware | ✅ This |

UET is a **simulation framework**, NOT a universal law.

---

## 📊 Test Results (v0.8.7)

### Overall Score: **117 Tests across 20 Domains** (98.3% pass)

| Category | Tests | Topics | Real Data |
|:---------|:-----:|:-------|:----------|
| **Astrophysics** | 31 | 0.1, 0.2, 0.3, 0.15 | SPARC, Planck, EHT, LIGO |
| **Particle** | 41 | 0.5-0.9, 0.16-0.18, 0.20 | PDG 2024, NuFIT, NIST |
| **Condensed** | 29 | 0.4, 0.10-0.14 | CODATA, Casimir |
| **Gravity/GR** | 9 | 0.19 | Eöt-Wash, MICROSCOPE |
| **Total** | **117** | **20** | Real Data |

---

## 🎯 Core Equation

$$\Omega[C,I] = \int \left[ \underbrace{V(C)}_{\text{Physical Cost}} + \underbrace{\frac{\kappa}{2}|\nabla C|^2}_{\text{Interaction Limit}} + \underbrace{\beta C I}_{\text{THE BRIDGE}} \right] dx$$

| Variable | Meaning |
|:---------|:--------|
| **C** | Capacity (mass, liquidity, connectivity) |
| **I** | Information (entropy, stimulus) |
| **V** | Potential (cost of becoming) |
| **κ** | Gradient penalty |
| **β** | Coupling constant |

---

## 📁 Structure

```text
research_uet/
├── 📊 topics/                    # 20 Verified Physics Domains
│   └── run_all_tests.py          # MASTER VALIDATION SCRIPT
├── 📋 SINGLE_SOURCE_OF_TRUTH.md  # Canonical Metrics & DOIs
├── 📄 UET_FINAL_PAPER_SUBMISSION.md
├── 📄 UET_FULL_PAPER.tex
├── 📚 references.bib
├── 🗂️ DATA_SOURCE_MAP.md
├── 🧪 THEORY_MAP.md
├── 💡 EXPLANATION_STRATEGY.md
└── 🔗 UET_RESEARCH_HUB.md
```

---

## 🚀 Quick Start

```bash
# Run ALL validation tests
python research_uet/topics/run_all_tests.py

# Expected: 117 tests, 98.3% pass
```

---

## 📚 Key Documents

| Document | Description |
|:---------|:------------|
| [UET_RESEARCH_HUB.md](UET_RESEARCH_HUB.md) | Full test matrix with DOIs |
| [DATA_SOURCE_MAP.md](DATA_SOURCE_MAP.md) | All data sources |
| [THEORY_MAP.md](THEORY_MAP.md) | UET ↔ Physics dictionary |
| [topics/](topics/) | 20 topic folders with tests |

---

*Unity Equilibrium Theory — A Simulation Framework, Not a Universal Law*

*[GitHub](https://github.com/unityequilibrium/Equation-UET-v0.8.7) | [View Experiments](topics/)*
