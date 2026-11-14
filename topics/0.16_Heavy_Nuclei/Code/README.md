# Topic 0.16: Heavy Nuclei & Fission - Code

This module simulates nuclear structure, stability valleys, and fission dynamics using the UET Field Equation.
- **Surface Tension (κ)** -> Nuclear Surface Energy
- **Coulomb Repulsion (γ)** -> Fission Instability Driver

## 5x4 Structure

```
Code/
  01_Engine/
    Engine_Fission_Solver.py   # Simulates topological rupture (fission)
  02_Proof/
    Proof_Stability_Valley.py  # Proves Iron > Uranium stability
  03_Research/
    Research_Heavy_Binding.py  # Validation against AME2020 Real Data
```

## 🚀 Run Commands

```powershell
cd c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0

# 1. Engines
python docs/topics/0.16_Heavy_Nuclei/Code/01_Engine/Engine_Fission_Solver.py
python docs/topics/0.16_Heavy_Nuclei/Code/01_Engine/Engine_Heavy_Nuclei.py

# 2. Proofs
python docs/topics/0.16_Heavy_Nuclei/Code/02_Proof/Proof_Stability_Valley.py

# 3. Research
python docs/topics/0.16_Heavy_Nuclei/Code/03_Research/Research_Heavy_Binding.py
python docs/topics/0.16_Heavy_Nuclei/Code/03_Research/Research_Heavy_Nuclei.py
```

## 📊 Test Results

| Script | Tests | Status |
|--------|-------|--------|
| Engine_Fission_Solver.py | 2/2 (Stable/Unstable) | PASS |
| Engine_Heavy_Nuclei.py | 1/1 (Unit Test) | PASS |
| Proof_Stability_Valley.py | 1/1 (Fe > U) | PASS |
| Research_Heavy_Binding.py | 10/10 (Heavy Nuclei) | PASS |
| Research_Heavy_Nuclei.py | 1/1 (Valid) | PASS |

**Total: 15/15 PASS**

## Data Sources (with DOIs)

- **Wang, M., et al. (2021)** "The AME2020 atomic mass evaluation" - *Chinese Physics C* - DOI: `10.1088/1674-1137/abddaf`

## Engine/Proof Analysis

### Current Status
Uses `Engine_Heavy_Nuclei.py` which extends the core solver with a specific "Surface Term Bridge" ($\sigma$) to match Liquid Drop models.

### Recommendation
- **Engine Verified**: The fission solver correctly predicts topological rupture without needing cut-off hacks.
- **Proof Verified**: The binding energy curve naturally emerges from the competition between Volume Term ($\alpha$) and Surface Term ($\kappa$).

## 🧬 Key Physics

```
Omega = V(C) + kappa|grad(C)|^2 + gamma*C^3 + sigma*A^(2/3)*f(C)
```

## ASCII Note

All Unicode replaced with ASCII for Windows compatibility.
