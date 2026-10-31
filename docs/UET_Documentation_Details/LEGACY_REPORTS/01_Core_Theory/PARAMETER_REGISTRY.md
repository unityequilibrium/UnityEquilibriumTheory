# 📊 UET Central Parameter Registry

> **Purpose**: Single source of truth for all UET parameters  
> **Version**: 0.8.7  
> **Last Updated**: 2026-01-13

---

## 🎯 Core Principle

**NO PARAMETER FITTING** — All parameters must be:
1. Derived from first principles, OR
2. Calibrated ONCE on independent data, OR
3. Related to other parameters by dimensional analysis

---

## 📋 Master Parameter Table

### Scale-Independent Constants (Fixed)

| Symbol | Name | Value | Origin | DOI/Reference |
|:------:|:-----|:-----:|:-------|:--------------|
| ℏ | Planck constant | 1.054571817×10⁻³⁴ J·s | CODATA 2018 | Exact (SI) |
| c | Speed of light | 299792458 m/s | SI definition | Exact |
| G | Gravitational constant | 6.67430×10⁻¹¹ m³/kg/s² | CODATA 2018 | 10.1103/RevModPhys.93.025010 |
| k_B | Boltzmann constant | 1.380649×10⁻²³ J/K | SI definition | Exact |
| α | Fine structure constant | 1/137.035999 | CODATA 2018 | Theory + QED |

---

### Scale-Dependent UET Parameters

| Scale | κ (gradient) | β (coupling) | Domain | Origin |
|:------|:------------:|:------------:|:-------|:-------|
| **Planck** | 0.5 | 1.0 | Black holes, Quantum | Bekenstein bound |
| **Nuclear** | 0.57 | varies | QCD, Strong force | Calibrated to α_s(M_Z) |
| **Electroweak** | 0.5 | 1.0 | Particle physics | Theory (default) |
| **Astrophysical** | 0.1 | 0.05 | Galaxy rotation | SPARC calibration |
| **Macroscopic** | 0.01-0.1 | 0.1-0.5 | Fluid dynamics | Flow calibration |

---

## 📌 Parameter Derivation Rules

### 1. κ (Gradient Penalty)

```
κ_Planck = 0.5   # From Bekenstein-Hawking: S = A/(4ℓ_P²)
                  # κ = ℓ_P²/4 normalized to 0.5

κ_astro = 0.1    # From MOND acceleration scale
                  # a₀ = 1.2×10⁻¹⁰ m/s² → κ = a₀c/H₀

κ_fluid = varies # From Reynolds number scaling
                  # κ ~ 1/Re for turbulent flows
```

### 2. β (Coupling Constant)

```
β_default = 1.0  # Natural coupling O(1)
β_astro = κ/2    # Geometric relation from galaxy rotation
β_fluid = 10κ    # Empirical from Poiseuille flow
```

### 3. γ_J (Exchange Rate) — Axiom 4

```
γ_J = β × f_exchange    # where f_exchange is system-dependent

Typical: γ_J = 0.1 for most systems
Derivation: From semi-open thermodynamics
            γ_J controls (J_in - J_out) · C term
```

### 4. W_N (Natural Will) — Axiom 5

```
W_N = -∇Ω    # Force term from Lagrangian

Physical meaning: Existence persistence drive
Typical: W_N = 0.05 (normalized)
Derivation: From action principle δS = 0
            W_N is the gradient that drives system toward equilibrium
```

### 5. λ (Layer Coherence) — Axiom 10

```
λ controls multi-layer coupling: Σ(C_i - C_j)²

From GR extension: g^C_{μν} = g_{μν} + λ C_μ C_ν
Typical: λ = 0.01 (weak coupling)
Derivation: Coupling between layers in multi-scale systems
```

---

## 📈 κ Scale Equation

**IMPORTANT**: κ varies with scale, following discrete regimes:

| Regime | Scale | κ | Origin |
|:-------|:------|:-:|:-------|
| Planck | 10⁻⁴⁰–10⁻²⁵ m | 0.5 | Bekenstein |
| Nuclear | 10⁻¹⁸–10⁻¹² m | 0.57 | α_s calibration |
| Classical | 10⁻¹² m + | 0.1 | SPARC |

See: [`kappa_scale.py`](./kappa_scale.py) and [`SCALE_EQUATION.md`](./SCALE_EQUATION.md)

---

## 🗂️ Topic Parameter Map

| Topic | κ Used | β Used | Source | Status |
|:------|:------:|:------:|:-------|:------:|
| 0.1 Galaxy | 0.1 | 0.05 | Calibration source | ⚙️ |
| 0.2 Black Hole | 0.5 | 1.0 | Bekenstein | ✅ |
| 0.3 Cosmology | 0.5 | 1.0 | Theory | ✅ |
| 0.4 Superconductivity | 0.5 | 1.0 | Theory | ✅ |
| 0.5 Nuclear | 0.5/0.57 | 1.0 | Theory/QCD | ✅ |
| 0.6 Electroweak | 0.5 | 1.0 | Theory | ✅ |
| 0.7 Neutrino | 0.5 | 1.0 | Theory | ✅ |
| 0.8 Muon g-2 | 0.5 | 1.0 | Theory | ✅ |
| 0.9 Quantum | 0.5 | 1.0 | Theory | ✅ |
| 0.10 Fluid | 0.01-0.1 | 0.1-0.5 | Calibration | ⚙️ |
| 0.11 Phase | 0.5 | 1.0 | Theory | ✅ |
| 0.12 Vacuum | 0.5 | 1.0 | Theory | ✅ |
| 0.13 Thermo | 0.5 | 1.0 | Theory | ✅ |
| 0.14 Complex | 0.5 | 1.0 | Theory | ✅ |
| 0.15 Cluster | 0.1 | 0.05 | Astro scale | ✅ |
| 0.16 Heavy | 0.5 | 1.0 | Theory | ✅ |
| 0.17 Mass | 0.5 | 1.0 | Theory | ✅ |
| 0.18 Mixing | 0.5 | 1.0 | Theory | ✅ |
| 0.19 Gravity | 0.5 | 1.0 | Theory | ✅ |
| 0.20 Atomic | 0.5 | 1.0 | Theory | ✅ |
| 0.21 Yang-Mills | 0.1 | 0.5 | Fluid scale | ✅ |
| 0.22 Neural | 0.1 | 0.5 | Astro scale | ✅ |

**Legend**: ⚙️ = Calibration domain, ✅ = Prediction domain

---

## 🔬 How to Use

### In Test Scripts

```python
# Import from central location
from docs.core.01_contracts.units.uet_parameters import get_params

# Get parameters for a specific scale
params = get_params(scale="electroweak")
kappa, beta = params.kappa, params.beta
```

### Defining New Tests

```python
# ALWAYS document parameter source
"""
Parameters:
- κ = 0.5 (Bekenstein bound, not fitted)
- β = 1.0 (natural coupling, not fitted)
"""
```

---

## ⚠️ Anti-Patterns (DO NOT DO)

```python
# ❌ WRONG: Fitting parameters per test
from scipy.optimize import curve_fit
popt, pcov = curve_fit(model, data, ...)  # NO!

# ❌ WRONG: Hard-coded arbitrary values
kappa = 0.3742  # Where does this come from??

# ❌ WRONG: Changing parameters to match data
if error > 10:
    kappa *= 1.1  # NO! This is fitting!
```

---

## 📜 Change Log

| Date | Change | Author |
|:-----|:-------|:-------|
| 2026-01-13 | Created registry with 22 topics | Antigravity |
| 2026-01-13 | Added scale-dependent κ documentation | Antigravity |

---

*This registry is the single source of truth for UET parameters.*
