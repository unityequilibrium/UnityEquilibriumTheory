# Topic 0.1: Galaxy Rotation Problem - Code

Validates UET against the Galaxy Rotation Problem using SPARC and LITTLE THINGS datasets.
- **Information Field Coupling** -> gamma term
- **Northern Acceleration** -> grad(C) term

## 5x4 Structure

```
Code/
  01_Engine/
    Engine_Galaxy_V3.py   # Main Axiomatic Solver (Zero-Parameter)
  02_Proof/
    Proof_Unity_Density_Law.py  # Symbolic Flat Curve Verification
  03_Research/
    Research_Galaxy_Rotation.py  # SPARC 154 Benchmark
    Research_Dwarf_Galaxies.py   # LITTLE THINGS Stress Test
    Research_Alpha_Learning.py   # AI Alpha-Law Discovery Tool
    Research_Residual_Analysis.py  # Diagnostic Compass
```

## 🚀 Run Commands

```powershell
# Navigate to project root
cd c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0

# Run validation benchmark
python docs/topics/0.1_Galaxy_Rotation_Problem/Code/03_Research/Research_Galaxy_Rotation.py

# Run dwarf stress test
python docs/topics/0.1_Galaxy_Rotation_Problem/Code/03_Research/Research_Dwarf_Galaxies.py


python docs/topics/0.1_Galaxy_Rotation_Problem/Code/01_Engine/Engine_Galaxy_V3.py

python docs/topics/0.1_Galaxy_Rotation_Problem/Code/02_Proof/Proof_Unity_Density_Law.py

python docs/topics/0.1_Galaxy_Rotation_Problem/Code/03_Research/Research_Alpha_Learning.py
python docs/topics/0.1_Galaxy_Rotation_Problem/Code/03_Research/Research_Galaxy_Rotation.py
python docs/topics/0.1_Galaxy_Rotation_Problem/Code/03_Research/Research_Dwarf_Galaxies.py
python docs/topics/0.1_Galaxy_Rotation_Problem/Code/03_Research/Research_Residual_Analysis.py

python docs/topics/0.1_Galaxy_Rotation_Problem/Code/04_Competitor/Competitor_NFW.py

```

## 📊 Test Results

| Script | Tests | Status |
|--------|-------|--------|
| Engine_Galaxy_V3.py | 154/154 | PASS (9.9% Error) |
| Proof_Unity_Density_Law.py | 1/1 | PASS (Symbolic) |
| Research_Dwarf_Galaxies.py | 26/26 | PASS (3.8 km/s Bias) |

**Total: 3/3 PASS**

## Data Sources (with DOIs)

- **Lelli et al. (2016)** SPARC: Mass Models for 175 Late-type Galaxies - DOI: 10.3847/1538-3881/152/6/157
- **Hunter et al. (2012)** LITTLE THINGS: Local Irregulars That Trace Luminosity Extremes - DOI: 10.1088/0004-6256/144/5/134

## Engine/Proof Analysis

### Current Status
Uses `Engine_Galaxy_V3.py` (v3.3) with the refined Alpha-Law coupling.

### Recommendation
- **Engine needed?** Yes - v3.3 solved the Dwarf over-prediction issue.
- **Proof needed?** Yes - Axiom 3 symbolic derivation is required for theoretical grounding.

## 🧬 Key Physics

```
v^2 = G * (M_b + M_I) / r
M_I = M_b * (rho / rho_unity)^(-gamma)
```

## ASCII Note

All Unicode replaced with ASCII for Windows compatibility.
