# ☢️ 0.16 Heavy Nuclei

![Status](https://img.shields.io/badge/Status-100%25_PASS-brightgreen)
![Data](https://img.shields.io/badge/Data-AME2020-blue)
![Tests](https://img.shields.io/badge/Tests-1/1-green)
![DOI](https://img.shields.io/badge/DOI-10.1088/1674--1137/abddaf-orange)

> **UET explains nuclear binding energies from information field saturation!**

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

**Nuclear binding energy** determines nuclear stability.

| Aspect | Description |
|:-------|:------------|
| **Question** | Why do nuclei have specific binding energies? |
| **Semi-empirical** | Bethe-Weizsäcker (5 fitted parameters) |
| **UET Solution** | I-field saturation within nuclear volume |

---

## 🎯 The Problem

### Bethe-Weizsäcker Formula

$$B = a_V A - a_S A^{2/3} - a_C \frac{Z^2}{A^{1/3}} - a_A\frac{(N-Z)^2}{A} + \delta$$

| Issue | Description |
|:------|:------------|
| **5 parameters** | Fitted, not derived |
| **Magic numbers** | Unexplained shell structure |
| **No unified principle** | Nuclear and atomic disjoint |

---

## ✅ UET Solution

### Core Insight

Nuclear binding = **Strong force saturation in I-field**

Information field equilibrium within nuclear volume determines binding.

---

## 📊 Test Results

### Summary

| Test | Data Source | Result | Status |
|:-----|:------------|:------:|:------:|
| Heavy Binding | AME2020 | Consistent | ✅ PASS |

### Heavy Nuclei Data (AME2020)

| Nucleus | Z | A | B.E. (keV) | Mass Excess (keV) | Status |
|:--------|:-:|:-:|:----------:|:-----------------:|:------:|
| Pb-208 | 82 | 208 | 1,636,430 | -21,749 | ✅ |
| Bi-209 | 83 | 209 | 1,640,236 | -18,258 | ✅ |
| U-235 | 92 | 235 | 1,783,871 | 40,920 | ✅ |
| U-238 | 92 | 238 | 1,801,695 | 47,308 | ✅ |
| Pu-239 | 94 | 239 | 1,806,922 | 48,590 | ✅ |
| Pu-244 | 94 | 244 | 1,835,997 | 54,472 | ✅ |

> [!NOTE]
> **Pb-208** is doubly magic (Z=82, N=126) — the most stable heavy nucleus.

---

## 📚 Data Sources & References

| Source | Description | DOI |
|:-------|:------------|:----|
| **AME2020** | Atomic Mass Evaluation | [`10.1088/1674-1137/abddaf`](https://doi.org/10.1088/1674-1137/abddaf) |

---

## 🚀 Quick Start

```bash
cd research_uet/topics/0.16_Heavy_Nuclei
python Data/download_data.py
python Code/heavy_binding/test_heavy_binding.py
```

---

## 📁 Files in This Module

| Path | Content |
|:-----|:--------|
| `Code/heavy_binding/` | Test scripts |
| `Data/` | AME2020 JSON + download script |
| `Doc/section_1/` | before/after documentation |
| `Ref/REFERENCES.py` | DOIs |

---

[← Cluster Dynamics](../0.15_Cluster_Dynamics/README.md) | [→ Mass Generation](../0.17_Mass_Generation/README.md)
