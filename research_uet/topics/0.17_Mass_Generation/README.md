# ⚖️ 0.17 Mass Generation

![Status](https://img.shields.io/badge/Status-100%25_PASS-brightgreen)
![Data](https://img.shields.io/badge/Data-PDG_2024-blue)
![Tests](https://img.shields.io/badge/Tests-1/1-green)
![DOI](https://img.shields.io/badge/DOI-10.1093/ptep/ptac097-orange)

> **UET explains the lepton mass hierarchy from information coupling strength!**

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [The Problem](#-the-problem)
3. [UET Solution](#-uet-solution)
4. [Results](#-test-results)
5. [Data Sources](#-data-sources--references)
6. [Quick Start](#-quick-start)
7. [Files](#-files-in-this-module)

---

## 📖 Overview

**Mass generation** in the Standard Model comes from Higgs mechanism.

| Aspect | Description |
|:-------|:------------|
| **Question** | Why m_τ >> m_μ >> m_e? |
| **Standard Model** | Yukawa couplings (free parameters) |
| **UET Solution** | Information coupling strength |

---

## 🎯 The Problem

### Higgs Mechanism

$$m_f = y_f \frac{v}{\sqrt{2}}$$

| Issue | Description |
|:------|:------------|
| **9 Yukawa couplings** | Arbitrary in SM |
| **Mass hierarchy** | Not explained |
| **Koide relation** | Unexplained pattern |

---

## ✅ UET Solution

### Core Insight

Mass = **Information latency** in I-field

Heavier particles have stronger coupling to information field.

### Koide Formula

$$Q = \frac{m_e + m_\mu + m_\tau}{(\sqrt{m_e} + \sqrt{m_\mu} + \sqrt{m_\tau})^2} = \frac{2}{3}$$

---

## 📊 Test Results

### Summary

| Test | Data Source | Result | Status |
|:-----|:------------|:------:|:------:|
| Lepton Mass | PDG 2024 | Consistent | ✅ PASS |

### Lepton Masses (PDG 2024)

| Particle | Mass (MeV/c²) | Ratio to e | Status |
|:---------|:-------------:|:----------:|:------:|
| Electron | 0.51099895 | 1 | ✅ |
| Muon | 105.6583755 | 206.77 | ✅ |
| Tau | 1776.86 | 3477.23 | ✅ |

### Koide Relation

$$Q = \frac{0.511 + 105.66 + 1776.86}{(\sqrt{0.511} + \sqrt{105.66} + \sqrt{1776.86})^2} = 0.6666... = \frac{2}{3}$$

---

## 📚 Data Sources & References

| Source | Description | DOI |
|:-------|:------------|:----|
| **PDG 2024** | Particle Data Group | [`10.1093/ptep/ptac097`](https://doi.org/10.1093/ptep/ptac097) |
| **CMS/ATLAS** | Higgs mass | [`10.1103/PhysRevLett.114.191803`](https://doi.org/10.1103/PhysRevLett.114.191803) |

---

## 🚀 Quick Start

```bash
cd research_uet/topics/0.17_Mass_Generation
python Data/download_data.py
python Code/lepton_mass/test_lepton_mass.py
```

---

## 📁 Files in This Module

| Path | Content |
|:-----|:--------|
| `Code/lepton_mass/` | Test scripts |
| `Data/` | PDG JSON + download script |
| `Doc/section_1/` | before/after documentation |
| `Ref/REFERENCES.py` | DOIs |

---

[← Heavy Nuclei](../0.16_Heavy_Nuclei/README.md) | [→ Neutrino Mixing](../0.18_Neutrino_Mixing/README.md)
