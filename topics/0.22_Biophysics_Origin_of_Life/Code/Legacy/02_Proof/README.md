# 🧠 UET Neural Dynamics

> **Topic 0.21**: Applying UET to Neural/Brain Dynamics
> **Status**: NEW (ported from v0.9.0)

---

## Overview

This topic applies the UET framework to model neural dynamics, specifically:
- **Seizure prediction** (pre-ictal detection)
- **Sleep stage classification**
- **Brain state transitions**

## UET Mapping

| UET Symbol | Neural Interpretation |
|:-----------|:---------------------|
| **C** | Excitatory neural activity (observable from EEG) |
| **I** | Inhibitory/metabolic state (hidden) |
| **κ** | Spatial connectivity between brain regions |
| **β** | Excitatory-Inhibitory (E-I) coupling |
| **V(C)** | Bistable neural states (double-well potential) |
| **Ω** | Brain "energy" / disequilibrium |
| **𝒱** | Neural Value = adaptation = learning |

## Dynamics

The UET neural model uses:

```
∂C/∂t = κ∇²C - dV/dC - β(C - I) + s
∂I/∂t = κ∇²I - dV/dI - β(I - C)
```

Where:
- `V(φ) = (φ² - 1)² / 4` — bistable (double-well) potential
- `s` — external drive (stimulus)

## Key Insight

> **Why does this work?**
>
> The brain maintains E-I balance to minimize "disequilibrium" Ω.
> Seizures = runaway excitation = elevated Ω.
> Sleep stages = different Ω minima.
> Learning = 𝒱 = -ΔΩ = reduction in neural disorder.

## Data Sources

| Source | Description | DOI/URL |
|:-------|:------------|:--------|
| CHB-MIT | Scalp EEG seizure database | physionet.org/content/chbmit |
| Sleep-EDF | Sleep stage EEG | physionet.org/content/sleep-edfx |

## Tests

| Test | Description | Status |
|:-----|:------------|:-------|
| `test_neural_dynamics.py` | Seizure + Sleep tests | ✅ |

## Results

- UET successfully fits EEG dynamics
- Hidden state I captures inhibitory activity
- Ω correlates with brain state changes
- Value equation tracks neural adaptation

---

*"The brain is an equilibrium-seeking system — UET makes this explicit."*
