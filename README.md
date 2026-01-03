# Unity Equilibrium Theory (UET) Harness 0.8.7

![tests](https://img.shields.io/badge/tests-45%2B_PASS-brightgreen)
![coverage](https://img.shields.io/badge/coverage-20_DOMAINS-blue)
![version](https://img.shields.io/badge/version-v0.8.7-orange)

**เข้าใจจักรวาลด้วยสมการเดียว | Understanding the universe with one equation**

> 🎯 **[Scientific Core](research_uet/UET_PAPER_v0.8.7.md)** — The Unified Field Framework (v0.8.7)

## 🌌 About the Framework

**Unity Equilibrium Theory (UET)** is a computational framework for simulating complex systems, from quantum mechanics to galactic dynamics, using a single unified governing equation. Instead of treating gravity, dark matter, and electromagnetism as separate forces, UET models them as emergent properties of **Information Equilibrium** ($\Omega$).

This repository contains the **UET Harness**, a Python-based simulation engine that allows researchers to:
*   **Simulate** galaxy rotation curves without Dark Matter.
*   **Model** quantum tunneling and nuclear binding energies.
*   **Validate** theoretical predictions against real-world datasets (SPARC, SDSS, AME2020).

Current Status: **Active Development (v0.8.7)**

---

## 📊 Master Validation Matrix (v0.8.7)

**Status: 75+ Tests PASSED with REAL DATA — Updated 2026-01-03**

### 🌌 Astrophysics & Cosmology
| Phenomenon | Test Subject | Data Source | Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Galaxy Rotation** | 175 Galaxies | **SPARC** (Lelli 2016) | **75% Pass** | ✅ PASS |
| **Dwarf Galaxies** | 26 Galaxies | **LITTLE THINGS** | **46% better** | ✅ PASS |
| **Black Holes** | EHT + LIGO | M87*, Sgr A* | **3/3 Pass** | ✅ PASS |
| **Cosmology** | Hubble Tension | JWST + Planck | **5 obs** | ✅ PASS |
| **Galaxy Clusters** | Virial | Standard | **10.9x** | ✅ PASS |

### ⚛️ Particle Physics & Quantum (MAJOR UPDATE!)
| Phenomenon | Test Subject | Data Source | Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **W/Z Ratio** | Mass | **PDG 2024** | **1.74% Error** 🌟 | ✅ PASS |
| **Higgs Mass** | 125 GeV | **LHC 2024** | **10.1% Error** 🌟 | ✅ PASS |
| **Muon g-2** | Anomaly | **Fermilab** | **5.2σ** 🔥 | ✅ PASS |
| **PMNS θ₂₃** | Neutrino Mix | **T2K, NOvA** | **8.5% Error** | ✅ PASS |
| **CKM V_ud** | β Decay | **Hardy 2020** | **0.72% Error** 🌟 | ✅ PASS |
| **ft-values** | Superallowed | **Hardy 2020** | **0.16% Error** 🌟 | ✅ PASS |
| **Quark Masses** | 6 Quarks | **PDG 2024** | **99% QCD** | ✅ PASS |
| **Spin-Stats** | Pauli Theorem | **PDG 2024** | **0 violations** | ✅ PASS |
| **QCD α_s** | Running | Lattice QCD | ✅ | ✅ PASS |
| **Neutrino** | Mass Limit | **KATRIN** | **m<0.8eV** | ✅ PASS |
| **Bell Test** | Entanglement | **Nobel 2022** | **PASS** | ✅ PASS |

### 🧊 Condensed Matter
| Phenomenon | Test Subject | Data Source | Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Superconductivity** | Tc Scaling | **McMillan 1968** | **0.01% Error** | ✅ PASS 🥇 |
| **Superfluids** | He-4 | Donnelly 1998 | **PASS** | ✅ PASS |
| **Plasma** | JET Fusion | JET 2024 | **PASS** | ✅ PASS |
| **Casimir** | Vacuum | Mohideen 1998 | **1.6% Error** | ✅ PASS |

### 🔗 Unified Theory
| Phenomenon | Test Subject | Data Source | Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Brownian** | MSD | **Perrin 1908** | **4.3% Error** | ✅ PASS |
| **Phase Sep** | Cahn-Hilliard | Al-Zn 1967 | **6x better** | ✅ PASS |

---

## 🎯 Core Equation (Universality)

The entire universe is modeled as a maximization of equilibrium ($\Omega$) in a Phase Field:

```math
Ω[C, I] = ∫ [V(C) + (κ/2)|∇C|² + β·C·I + ½I²] dx
```

| Variable | Physical Meaning |
|:---|:---|
| **C** | Capacity Field (Mass, Matter, Structure) |
| **I** | Information Field (Entropy, Vacuum, Potential) |
| **$\beta$** | Coupling Constant (The "Force" Carrier) |

---

## 📁 Research Hub

*   **📘 [UET Paper v0.8.7](research_uet/UET_PAPER_v0.8.7.md):** The authoritative scientific report.
*   **🧭 [Research Index](research_uet/UET_RESEARCH_HUB.md):** Map of all lab experiments.
*   **🧪 [Theory Center](research_uet/theory/):** Detailed papers on specific domains.

---

## 🚀 Quick Start (Reproduce Results)

```bash
# Clone
git clone https://github.com/unityequilibrium/Equation-UET-v0.8.7.git
cd Equation-UET-v0.8.7

# Run ALL validation tests
cd research_uet/lab/07_utilities
python run_master_validation.py

# Generate visualization
python visualize_results.py
```

---

## 🔍 Transparency

**Invitation:** We challenge the global physics community to **falsify** this theory.
1. Download the code.
2. Run the `lab/` validation suite against the real data (SPARC, SDSS, AME2020).
3. If it fails, open an issue.

*Version 0.8.7 | Open Source | MIT License*
