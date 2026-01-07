# 🏦 Econophysics: F = -∇Ω in Financial Markets

## Status: ✅ COMPLETE

---

## Summary

| Metric | Value |
|--------|-------|
| Data source | Yahoo Finance (real) |
| Symbols tested | 12 (4 indices + 8 stocks) |
| Data points | 48,130 |
| Correlation (indices) | r = -0.17 |
| p-value | < 10⁻²⁸ |
| Power law α | 2.94 ± 0.15 |

---

## Domain Mapping

| GDS Symbol | Econophysics | Units |
|------------|--------------|-------|
| Ω | Market stress (deviation²) | - |
| F | Price returns | $/day |
| ∇Ω | Stress gradient | - |
| λ | Market inertia⁻¹ | - |

---

## Equation

```
ΔPrice = -β ∇(Market Stress)

Where:
  Market Stress = (Price - Moving Average)² / σ²
```

---

## Results

### Market Indices (PASS ✅)
| Symbol | Correlation | p-value | Status |
|--------|-------------|---------|--------|
| SP500 | -0.181 | 10⁻³¹ | ✅ |
| NASDAQ | -0.151 | 10⁻²² | ✅ |
| DOW | -0.184 | 10⁻³² | ✅ |

### Individual Stocks (Mixed)
| Symbol | Correlation | Status |
|--------|-------------|--------|
| AAPL | -0.029 | ⚠️ Not significant |
| TSLA | +0.067 | ❌ Opposite |
| AMZN | +0.096 | ❌ Opposite |

---

## Files

| Path | Description |
|------|-------------|
| `00_theory` | Theory & equations |
| `01_data/` | Market data + scripts |
| `02_refs/` | Literature references |
| `03_results/` | Analysis outputs |

---

*Last updated: 2025-12-28*
