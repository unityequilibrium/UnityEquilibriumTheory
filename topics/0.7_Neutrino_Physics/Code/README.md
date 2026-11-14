# Topic 0.7: Neutrino Physics - Code

This module covers neutrino hierarchy, PMNS-style mixing, oscillation formulas, and
source-locked benchmark comparisons. Current scripts support internal benchmark
compatibility checks; they do not certify a full first-principles neutrino-sector proof.

## 5x4 Structure

```text
Code/
  01_Engine/
    Engine_Neutrino.py         # hierarchy proxy, geometric angles, absolute-mass branch
    Engine_Mixing_Neutrino.py  # oscillation formula and runtime benchmark parameters
  02_Proof/
    Proof_PMNS_Angles.py       # proof-oriented PMNS angle note/script
  03_Research/
    Research_PMNS_Mixing.py              # legacy PMNS comparison path
    Research_NuFit_6_0_Comparison.py     # current NuFIT 6.0/KATRIN 2025 verifier
```

## Run Commands

```powershell
cd C:\Users\santa\Desktop\uet_harness

# Diagnostic angle/hierarchy engine
python docs/topics/0.7_Neutrino_Physics/Code/01_Engine/Engine_Neutrino.py

# Diagnostic oscillation simulation
python docs/topics/0.7_Neutrino_Physics/Code/01_Engine/Engine_Mixing_Neutrino.py

# Current source-locked benchmark validation
python docs/topics/0.7_Neutrino_Physics/Code/03_Research/Research_NuFit_6_0_Comparison.py
```

## Current Test Status

| Script | Role | Status meaning |
| :-- | :-- | :-- |
| `Engine_Neutrino.py` | angle path and absolute mass branch | diagnostic engine, not final proof |
| `Engine_Mixing_Neutrino.py` | oscillation formula and runtime benchmark params | diagnostic engine, includes benchmark-fed values |
| `Research_NuFit_6_0_Comparison.py` | NuFIT 6.0/KATRIN 2025 declared verifier | currently FAILS the live engine angle gate |

The current verifier is intentionally strict: it reads live angle outputs from
`Engine_Neutrino.py`. The latest artifact fails the engine-angle gate while preserving passing
runtime mass-splitting, KATRIN, and provenance checks. See `../FORMULA_AUDIT.md` and
`../LIMITATIONS.md` before using results in public wording.

## Key Formula

```text
P(alpha -> beta) = sin^2(2 theta) * sin^2(1.27 * Delta_m^2 * L / E)
```

Unit convention for this script-level formula:

- `theta`: radians internally after degree conversion
- `Delta_m^2`: eV^2
- `L`: km
- `E`: GeV
- `1.27`: standard unit-conversion factor for this convention

## ASCII Note

This README is kept ASCII-only for Windows console compatibility.
