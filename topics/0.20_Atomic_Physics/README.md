---
layout: article
title: "UET Topic 0.20: Atomic Physics"
description: "Hydrogen spectrum benchmark and atomic-model diagnostics within the Unity Equilibrium Theory framework."
---

# 0.20 Atomic Physics

> [!NOTE]
> **AI-Digest**: This topic currently has a source-backed hydrogen Rydberg benchmark using a NIST hydrogen spectrum working copy and CODATA `R_H`. The current artifact supports internal hydrogen-spectrum agreement only; it does not yet prove a UET derivation of the Rydberg formula or validate fine structure, Lamb shift, helium, or many-electron atoms.

![Status](https://img.shields.io/badge/Status-Hydrogen%20Benchmark-blue)
![Claim_Class](https://img.shields.io/badge/Claim%20Class-C%20Internal%20Benchmark-yellow)
![Verifier](https://img.shields.io/badge/Verifier-Artifact%20Required-blue)

## Research Role

Topic `0.20` is the atomic benchmark layer for UET. Its near-term job is to make hydrogen spectral formulas, constants, NIST data, and residual thresholds auditable before the theory uses atomic physics as evidence for broader information-channel claims.

## Conceptual Map

```mermaid
flowchart LR
    nist["NIST hydrogen spectrum"] --> rows["Balmer/Lyman vacuum wavelengths"]
    codata["CODATA R_H"] --> formula["Rydberg wavelength relation"]
    rows --> verifier["Research_Rydberg_Validation.py artifact"]
    formula --> verifier
    verifier --> claim["Claim Class C: hydrogen spectrum benchmark"]

    levels["Hydrogen level data"] --> secondary["Secondary level-energy lane"]
    many["Three-body / multi-electron scripts"] --> open["Open: not primary evidence"]
    open --> deps["Inherited limitation for downstream topics"]
```

## Evidence and Status Matrix

| Layer | Current status | Evidence path | Claim allowed now | Blocker |
| :-- | :-- | :-- | :-- | :-- |
| Data | NIST/CODATA source-labeled working copies | `Data/03_Research/nist_hydrogen_spectrum.json`, `codata_2018_atomic.json` | Hydrogen line and constant inputs are inspectable with hashes. | Wavelength precision and source-transcription notes still need normalization. |
| Formula | Reviewed registry | `FORMULA_AUDIT.md` | Rydberg relation, `R_H` checkpoint, and residual metrics are mapped to code. | UET derivation of `R_H` is not artifact-backed. |
| Verification | Runnable primary artifact | `Code/03_Research/Research_Rydberg_Validation.py` | Supports hydrogen-spectrum internal benchmark claims. | Many-electron and QED effects are outside the verifier. |
| Claims | Bounded to hydrogen benchmark | this README, `METHOD.md`, `LIMITATIONS.md` | May state that selected hydrogen lines match the standard Rydberg relation within declared thresholds. | Cannot claim full atomic theory or first-principles UET derivation. |
| Dependencies | Atomic constants/levels bridge | `0.6`, `0.17`, `0.21`, `0.23`, `0.0` | Downstream topics may cite the hydrogen benchmark with limitations. | Stronger claims need fine-structure/many-electron artifacts. |

## Primary Verification

```powershell
python docs/topics/0.20_Atomic_Physics/Code/03_Research/Research_Rydberg_Validation.py
```

Expected artifact:

- `Result/artifacts/0_20_atomic_physics_verification.json`

The artifact records dataset hashes, NIST/CODATA source IDs, line residuals, fitted slope, thresholds, and limitations.

## Key Files

- `FORMULA_AUDIT.md`: formula registry, units, constants, proof status, and failure modes.
- `DATA_MANIFEST.md`: NIST/CODATA working-copy provenance and benchmark roles.
- `VERIFICATION_SPEC.md`: primary command, thresholds, and artifact contract.
- `METHOD.md`: evidence lanes and dependency policy.
- `LIMITATIONS.md`: boundaries for derivation, QED, helium, and many-electron claims.
- `Code/01_Engine/Engine_Atomic_Hydrogen.py`: hydrogen engine and local Rydberg formula.
- `Code/03_Research/Research_Rydberg_Validation.py`: primary verifier.
