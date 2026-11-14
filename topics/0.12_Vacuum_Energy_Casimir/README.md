---
layout: article
title: "UET Topic 0.12: Vacuum Energy Casimir"
description: "Casimir benchmark and vacuum-energy bridge boundary for the Unity Equilibrium Theory framework."
---

# 0.12 Vacuum Energy & Casimir Effect

> [!NOTE]
> **AI-Digest**: This topic currently has a source-backed internal benchmark for the Casimir force using a Mohideen/Roy sphere-plate working dataset. The vacuum-energy and dark-energy interpretation remains an open bridge: it is important to the theory, but it is not validated by the Casimir artifact alone.

![Status](https://img.shields.io/badge/Status-Structured%20Benchmark-blue)
![Claim_Class](https://img.shields.io/badge/Claim%20Class-C%20Casimir%20Benchmark-yellow)
![Verifier](https://img.shields.io/badge/Verifier-Artifact%20Required-blue)

## Research Role

Topic `0.12` is the vacuum/Casimir benchmark layer. Its immediate scientific job is to test whether the implemented engine reproduces a measured force-versus-distance Casimir curve with declared geometry, units, constants, and error thresholds. Its larger role in UET is to define a possible bridge from vacuum boundary effects toward vacuum-energy structure, but that bridge is not yet a cosmology proof.

## Conceptual Map

```mermaid
flowchart LR
    data["Mohideen/Roy sphere-plate data"] --> units["Unit normalization: nm, pN, um"]
    units --> pfa["Sphere-plate PFA formula"]
    pfa --> corr["Gold finite-conductivity correction"]
    corr --> verifier["Research_Casimir.py artifact"]
    verifier --> claim["Claim Class C: Casimir benchmark"]

    anchor["Dark-energy density anchor"] --> open["Open bridge: not validated by Casimir artifact"]
    open --> deps["Inherited limitation for 0.0 / 0.13 / 0.23 / 0.26"]
```

## Evidence and Status Matrix

| Layer | Current status | Evidence path | Claim allowed now | Blocker |
| :-- | :-- | :-- | :-- | :-- |
| Data | Real source referenced, topic-local working copy | `Data/03_Research/mohideen_1998_casimir.json` | The benchmark uses a declared Mohideen/Roy-style sphere-plate dataset. | Upstream archival URL/DOI and transcription audit still need freezing. |
| Formula | Reviewed registry | `FORMULA_AUDIT.md` | PFA Casimir and finite-conductivity formulas are mapped to code and units. | Parallel-plate pressure function is still named as force; dark-energy anchor is not derived. |
| Verification | Runnable primary artifact | `Code/03_Research/Research_Casimir.py` | Casimir force agreement can be judged by average and max relative error thresholds. | Needs radius/material sensitivity runs and independent baseline comparison. |
| Claims | Bounded to Casimir benchmark | this README, `METHOD.md`, `LIMITATIONS.md` | Supports internal benchmark claims only. | Does not solve the vacuum catastrophe or establish dark energy. |
| Dependencies | Limited downstream use | `0.0`, `0.13`, `0.23`, `0.26` | Downstream topics may cite Casimir benchmark behavior. | Downstream topics must inherit dark-energy bridge limitations. |

## Primary Verification

```powershell
python docs/topics/0.12_Vacuum_Energy_Casimir/Code/03_Research/Research_Casimir.py
```

Expected artifact:

- `Result/artifacts/0_12_vacuum_energy_casimir_verification.json`

The verifier must record PASS/FAIL, dataset hash, geometry, model radius, formula IDs, thresholds, and per-point residuals.

## Key Files

- `FORMULA_AUDIT.md`: formula registry, units, proof status, failure modes.
- `DATA_MANIFEST.md`: dataset provenance, local paths, hashes, benchmark roles.
- `VERIFICATION_SPEC.md`: primary command, thresholds, artifact contract.
- `METHOD.md`: modeling assumptions and dependency policy.
- `LIMITATIONS.md`: explicit boundaries for vacuum-energy and cosmology claims.
- `Code/01_Engine/Engine_Vacuum.py`: current engine implementation.
- `Code/03_Research/Research_Casimir.py`: primary benchmark verifier.
