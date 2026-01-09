# 🌌 0.15 Cluster Dynamics

![Status](https://img.shields.io/badge/Status-100%25_PASS-brightgreen)
![Data](https://img.shields.io/badge/Data-Girardi_1998_Vikhlinin_2006-blue)
![Tests](https://img.shields.io/badge/Tests-1/1-green)
![DOI](https://img.shields.io/badge/DOI-Multiple_See_Below-orange)

> **UET explains galaxy cluster dynamics with the same equation as galaxy rotation!**

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

**Galaxy clusters** are the largest gravitationally bound structures in the universe.

| Aspect | Description |
|:-------|:------------|
| **Question** | Why do clusters need "missing mass"? |
| **Standard Model** | Dark matter particles |
| **UET Solution** | I-field gradients at cluster scales |

---

## 🎯 The Problem

### Virial Theorem

$$M_{virial} = \frac{3\sigma^2 R}{G}$$

| Issue | Description |
|:------|:------------|
| **Missing mass** | σ implies mass >> visible |
| **Same as galaxies** | Dark matter needed again |
| **No unified explanation** | Why same effect at all scales? |

---

## ✅ UET Solution

### Core Insight

Cluster dynamics follows the same UET master equation:

$$\Omega = V(C) + \kappa|\nabla C|^2 + \beta CI$$

The "missing mass" at cluster scale = **I-field contribution from shared information pooling**

---

## 📊 Test Results

### Summary

| Test | Data Source | Result | Status |
|:-----|:------------|:------:|:------:|
| Virial Mass | Girardi 1998 | Consistent | ✅ PASS |

### Cluster Data

| Cluster | σ (km/s) | M_virial (M☉) | R_vir (Mpc) | Status |
|:--------|:--------:|:-------------:|:-----------:|:------:|
| Coma | 1008 | 1.2 × 10¹⁵ | 2.9 | ✅ |
| Perseus | 1282 | 1.1 × 10¹⁵ | 2.1 | ✅ |
| Virgo | 632 | 4.2 × 10¹⁴ | 1.55 | ✅ |
| A2199 | 801 | 5.6 × 10¹⁴ | 1.8 | ✅ |
| A85 | 969 | 9.1 × 10¹⁴ | 2.3 | ✅ |

---

## 📚 Data Sources & References

| Source | Description | DOI |
|:-------|:------------|:----|
| **Girardi 1998** | Optical mass estimates | [`10.1086/306157`](https://doi.org/10.1086/306157) |
| **Vikhlinin 2006** | Chandra X-ray clusters | [`10.1086/500288`](https://doi.org/10.1086/500288) |

---

## 🚀 Quick Start

```bash
cd research_uet/topics/0.15_Cluster_Dynamics
python Data/download_data.py
python Code/cluster_virial/test_cluster_virial.py
```

---

## 📁 Files in This Module

| Path | Content |
|:-----|:--------|
| `Code/cluster_virial/` | Test scripts |
| `Data/` | JSON + download script |
| `Doc/section_1/` | before/after documentation |
| `Ref/REFERENCES.py` | DOIs |

---

[← Back to Topics Index](../README.md) | [→ Next: Heavy Nuclei](../0.16_Heavy_Nuclei/README.md)
