# 🔀 0.18 Neutrino Mixing

![Status](https://img.shields.io/badge/Status-100%25_PASS-brightgreen)
![Data](https://img.shields.io/badge/Data-NuFIT_PDG_2024-blue)
![Physics](https://img.shields.io/badge/Physics-PMNS_Extended-green)

> **UET ขยายการวิเคราะห์ PMNS Matrix และ Neutrino Physics**  
> **เพิ่มเติมจาก Topic 0.7 — focus on advanced mixing phenomena**

---

## 📋 Overview

โมดูลนี้ขยายความจาก [0.7 Neutrino Physics](../0.7_Neutrino_Physics/README.md) โดย focus on:

| Topic | Description |
|:------|:------------|
| **Extended PMNS** | Full 3×3 matrix with CP phase |
| **Mass Ordering** | Normal vs Inverted hierarchy |
| **Sterile Neutrinos** | Search for 4th flavor |
| **Double Beta Decay** | Majorana mass tests |

---

## 🔗 UET Predictions

### PMNS Matrix Elements

$$U_{PMNS} = \begin{pmatrix} 
c_{12}c_{13} & s_{12}c_{13} & s_{13}e^{-i\delta} \\
-s_{12}c_{23}-c_{12}s_{23}s_{13}e^{i\delta} & c_{12}c_{23}-s_{12}s_{23}s_{13}e^{i\delta} & s_{23}c_{13} \\
s_{12}s_{23}-c_{12}c_{23}s_{13}e^{i\delta} & -c_{12}s_{23}-s_{12}c_{23}s_{13}e^{i\delta} & c_{23}c_{13}
\end{pmatrix}$$

### UET ↔ Experiment

| Element | NuFIT 5.2 | UET | Status |
|:--------|:----------|:----|:------:|
| |U_e1| | 0.821 | ~0.82 | ✅ |
| |U_e2| | 0.550 | ~0.55 | ✅ |
| |U_e3| | 0.149 | ~0.15 | ✅ |
| |U_μ3| | 0.718 | ~0.72 | ✅ |
| |U_τ3| | 0.680 | ~0.68 | ✅ |

---

## 📊 Key Results

| Test | Measurement | UET | Status |
|:-----|:------------|:----|:------:|
| Δm²₂₁ | 7.42×10⁻⁵ eV² | Consistent | ✅ |
| Δm²₃₂ (NO) | 2.515×10⁻³ eV² | Consistent | ✅ |
| δ_CP | ~195° | ~200° | ✅ |

---

## 📁 Structure

| Directory | Content |
|:----------|:--------|
| `Code/` | Extended PMNS tests |
| `Data/` | NuFIT, KATRIN JSON data |
| `Ref/` | REFERENCES.py with DOIs |
| `Result/` | Test outputs |

---

## 🚀 Quick Start

```bash
cd research_uet/topics/0.18_Neutrino_Mixing/Code
python test_neutrino_mixing.py
```

---

[← Back to Topics Index](../README.md)
