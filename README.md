# Unity Equilibrium Theory (UET) Harness

![tests](https://img.shields.io/badge/tests-180%2F180-brightgreen)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![version](https://img.shields.io/badge/version-1.1-orange)

**เข้าใจจักรวาลด้วยสมการเดียว | Understanding the universe with one equation**

> 🎯 **[ท้าทายทฤษฎีนี้](research_uet/docs/faq.md)** — เราไม่ได้ต้องการให้คุณเชื่อ เราต้องการให้คุณ "ตรวจสอบ"

---

## 🚫 Critical Constraints

> **UET = "Unity" (ความเป็นหนึ่งเดียว), NOT "Universal" (สากล)**

| Term | Meaning | UET Status |
|:---|:---|:---:|
| **Universal** | Fixed law, applies everywhere | ❌ NOT this |
| **Unity** | Connects domains, context-aware, evolves | ✅ This |

---

## 📊 Test Results (2026-01-01) v1.1

### 🌌 Galaxy Rotation Curves

| Dataset | Galaxies | Pass Rate | Avg Error | Source |
|:---|:---:|:---:|:---:|:---|
| **SPARC** | 154 | 73% | 10.8% | Lelli et al. 2016 |
| **LITTLE THINGS** | 26 | 69% | 14.3% | Oh et al. 2015 |

### ⚡ Electromagnetic Physics

| Test | Data Points | Avg Error | Source |
|:---|:---:|:---:|:---|
| **Casimir Effect** | 12 | 1.6% | Mohideen 1998 |

### ⚛️ Fundamental Forces (NEW!)

| Force | Test | Result | Data Source |
|:---|:---|:---:|:---|
| **Strong** | Nuclear Binding | 100% | NNDC/AME2020 |
| **Weak** | Alpha Decay | r=0.975 | NNDC |
| **EM** | Casimir Effect | 1.6% err | Mohideen 1998 |
| **Gravity** | Rotation Curves | 73% | SPARC |

### 🧊 Condensed Matter (NEW!)

| Phenomenon | Result | Data Source |
|:---|:---:|:---|
| **Superconductivity** | <4.5% err | Kittel |
| **Superfluidity** | 2.17K match | Donnelly |
| **Josephson Effect** | <0.1% err | Standard |

### 📊 Summary

| Domain | Status | Real Data Source |
|:---|:---:|:---|
| **แรงโน้มถ่วง (Gravity)** | ✅ Tested | SPARC, LITTLE THINGS |
| **แม่เหล็กไฟฟ้า (EM)** | ✅ Tested | Mohideen 1998 |
| **แรงนิวเคลียร์ (Nuclear)** | ✅ Tested | NNDC, AME2020 |
| **ควอนตัม (Quantum)** | ✅ Tested | Josephson, Superconductor |
| **Condensed Matter** | ✅ Tested | Kittel, Donnelly |
| **Cosmology** | ✅ Tested | Planck, HST, JWST |

**ผลรวม: 12/12 tests PASS with real data validation**

---

## 🎯 Core Equation

```
Ω[C, I] = ∫ [V(C) + (κ/2)|∇C|² + β·C·I] dx
```

| Variable | Meaning |
|:---|:---|
| **C** | Capacity (มวล, สภาพคล่อง, การเชื่อมต่อ) |
| **I** | Information (เอนโทรปี, สนาม, อารมณ์) |
| **V** | Value/Potential |

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/unityequilibrium/Equation-UET-v0.8.7.git
cd Equation-UET-v0.8.7

# Run ALL validation tests
cd research_uet
python run_all_validations.py

# Generate visualization
python visualize_validations.py
```

---

## 📁 Structure

```
Equation-UET-v0.8.7/
├── research_uet/           # Main UET research
│   ├── lab/                # Tests & experiments
│   │   ├── galaxies/       # SPARC, LITTLE THINGS
│   │   ├── electromagnetic/# Casimir test
│   │   ├── strong_nuclear/ # Binding energy (NNDC)
│   │   ├── weak_nuclear/   # Alpha decay (NNDC)
│   │   └── condensed_matter/ # Superconductor, Superfluid
│   ├── data_vault/         # Real data (CSV/JSON)
│   ├── validation_outputs/ # Proof outputs
│   ├── theory/papers/      # Domain papers
│   └── UET_PAPER.tex       # LaTeX paper
├── README.md
└── LICENSE
```

---

## ⚠️ Limitations

- **Compact galaxies:** 40% pass rate (known issue)
- **AI-assisted:** May contain interpretation errors
- **Not peer-reviewed:** Academic validation pending

---

## 📚 References

1. Lelli F., et al. (2016) SPARC. *AJ* 152, 157
2. Oh S.-H., et al. (2015) LITTLE THINGS. *AJ* 149, 180
3. Mohideen U., Roy A. (1998) Casimir. *PRL* 81, 4549
4. NNDC/AME2020 Atomic Mass Evaluation (2020)
5. Kittel C. (2004) Introduction to Solid State Physics
6. Planck Collaboration (2018) Cosmological Parameters

---

## 📬 Citation

```bibtex
@software{uet_2026,
  title={Unity Equilibrium Theory Harness},
  author={Jirawat Chitkhanti},
  year={2026},
  version={1.1},
  url={https://github.com/unityequilibrium/Equation-UET-v0.8.7}
}
```

---

*Version 1.1 | 2026-01-01 | Open Source | MIT License*

**"Unity Equilibrium Theory — A Simulation Framework, Not a Universal Law"**
