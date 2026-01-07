# 🧬 Biophysics: F = -∇Ω in Chemotaxis

## Status: 🔄 IN PROGRESS

---

## Summary

| Metric | Value |
|--------|-------|
| Data source | Simulated |
| Cells | 50 |
| Time steps | 500 |
| Samples | 25,000 |
| Correlation | r = -0.26 |
| p-value | 0 |

---

## Domain Mapping

| GDS Symbol | Biophysics | Units |
|------------|------------|-------|
| Ω | Chemical concentration | mol/m³ |
| F | Cell velocity | m/s |
| ∇Ω | Concentration gradient | mol/m⁴ |
| λ | Mobility / Diffusion | m²/(mol·s) |

---

## Equation (Fick's Law / Chemotaxis)

```
v = -D ∇C

Cell velocity = -Diffusion × Concentration gradient
```

---

## Results

| Test | Value | Status |
|------|-------|--------|
| Correlation | -0.264 | ✅ |
| p-value | 0 | ✅ |
| Slope | -0.504 | ✅ |

---

## TODO

- [ ] Find real cell tracking data
- [ ] Add morphogen gradient examples
- [ ] Protein folding connection

---

*Last updated: 2025-12-28*
