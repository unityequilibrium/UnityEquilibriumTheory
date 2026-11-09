---
layout: article
title: "UET Topic 0.19: Gravity GR"
description: "Gravity constant, weak-field formula, and GR-bridge diagnostics within the Unity Equilibrium Theory framework."
---

# 0.19 Gravity & General Relativity

> [!NOTE]
> **AI-Digest**: This topic currently has a CODATA gravitational-constant checkpoint and a reviewed weak-field formula registry. The primary artifact verifies that the engine constant package matches the local CODATA working copy; it does not yet derive Einstein's equations, validate light bending/perihelion precession, or solve singularities.

![Status](https://img.shields.io/badge/Status-Constant%20Checkpoint-blue)
![Claim_Class](https://img.shields.io/badge/Claim%20Class-C%20Internal%20Checkpoint-yellow)
![Verifier](https://img.shields.io/badge/Verifier-Artifact%20Required-blue)

## Research Role

Topic `0.19` is the gravity/GR bridge layer. Its immediate role is to keep constants, weak-field formulas, equivalence-principle diagnostics, and short-range gravity datasets auditable before any stronger theoretical claim is made. It is important for `0.0`, `0.2`, `0.3`, `0.21`, `0.23`, and `0.26`, but those topics must inherit its current limitations.

## Conceptual Map

```mermaid
flowchart LR
    codata["CODATA 2018 working copy"] --> constants["G, c, hbar constant package"]
    constants --> planck["Planck unit definitions"]
    constants --> verifier["Research_G_Constant.py artifact"]
    verifier --> claim["Claim Class C: constant checkpoint"]

    weak["Weak-field formulas"] --> demo["Engine demos: g, r_s, n(r)"]
    eq["Equivalence eta script"] --> open["Open: not experimental validation"]
    short["Eot-Wash / MICROSCOPE data"] --> future["Future artifacts"]
    open --> deps["Inherited limitation for downstream topics"]
    future --> deps
```

## Evidence and Status Matrix

| Layer | Current status | Evidence path | Claim allowed now | Blocker |
| :-- | :-- | :-- | :-- | :-- |
| Data | CODATA/Eot-Wash/MICROSCOPE working copies with source labels | `Data/03_Research/*.json` | Local constants and comparator datasets are inspectable. | Some source URLs/licenses and extraction notes still need normalization. |
| Formula | Reviewed registry | `FORMULA_AUDIT.md` | Constant package, Planck definitions, Newtonian/Schwarzschild diagnostics, eta, and Yukawa comparator are mapped. | Several theoretical bridges remain diagnostics or open lanes. |
| Verification | Runnable primary artifact | `Code/03_Research/Research_G_Constant.py` | Confirms engine `G` matches CODATA working copy under declared threshold. | This is a copied/source-constant checkpoint, not a derivation. |
| Source evidence workflow | Structured provenance gate | `Data/03_Research/source_evidence_intake_stub.json`, `source_evidence_readiness_matrix.json` | source-review queue | Weak-field, equivalence, and short-range packages still need dedicated artifacts. |
| Branch claim gate | Structured claim ceiling | `Data/03_Research/branch_claim_gate.json` | checkpoint-only claim control | Constant checkpoint does not promote GR closure claims. |
| Claim-scope gate | Artifact export controller | `gravity_claim_scope_gate` in artifact | blocks GR/quantum-gravity overclaim | Constant PASS remains topic-level `WARN` until physical GR tests and derivation artifacts exist. |
| Core GR program dependency | Candidate mathematics / blocked | `CORE_GR_PROGRAM_DEPENDENCY_SPEC.md`, `Result/artifacts/0_19_core_gr_program_dependency_gate.json` | exact implemented response-null, local balance, bounded causal/reduction statements | physical GR benchmarks, curved 3+1, EOS/transport, and global closure remain blocked |
| Claims | Bounded to internal checkpoint | this README, `METHOD.md`, `LIMITATIONS.md` | May state that the engine constant package is internally consistent with CODATA. | Cannot claim GR derivation, light-bending validation, or singularity avoidance. |
| Dependencies | High-impact core bridge | `0.0`, `0.2`, `0.3`, `0.21`, `0.23`, `0.26` | Downstream topics may cite constants/weak-field formulas with limitations. | Strong GR/cosmology claims need future artifacts. |

## Primary Verification

```powershell
python docs/topics/0.19_Gravity_GR/Code/03_Research/Research_G_Constant.py
```

Expected artifact:

- `Result/artifacts/0_19_gravity_gr_verification.json`

The artifact records dataset hash, CODATA DOI, formula IDs, threshold, engine `G`, and Planck-unit metrics.

## Core GR program dependency (candidate mathematics)

- Contract: [CORE_GR_PROGRAM_DEPENDENCY_SPEC.md](./CORE_GR_PROGRAM_DEPENDENCY_SPEC.md)
- Runner: [Research_Core_GR_Program_Dependency_Gate.py](./Code/03_Research/Research_Core_GR_Program_Dependency_Gate.py)
- Artifact: [0_19_core_gr_program_dependency_gate.json](./Result/artifacts/0_19_core_gr_program_dependency_gate.json)
- Result: `BLOCKED / CORE_CANDIDATE_GR_PARENT_AVAILABLE_TOPIC_PHYSICAL_VALIDATION_OPEN`.
- Accepted scope: the implemented `epsilon_nc = 0` branch has an exact response-null; the candidate parent has a local exchange-balance identity; the constitutive causal result is restricted to a flat local 1+1 lane; the response reduction is partial.
- Preserved boundary: the primary Topic 0.19 artifact remains a Claim Class C CODATA/Planck checkpoint with export controller `WARN`.
- Open controller: source-backed light bending, perihelion, MICROSCOPE eta, Eot-Wash, curved 3+1, EOS/coarse-graining/transport/KMS, entropy-current, and holdout comparison are still missing.
- Global statement: universe closure remains `UNRESOLVED`; `epsilon_nc` is a nesting coupling, not an openness percentage.
- Status impact: none. Topic 0.19 remains `Draft / Tier B`.

## Key Files

- `FORMULA_AUDIT.md`: formula registry, units, constants, proof status, and failure modes.
- `DATA_MANIFEST.md`: CODATA, Eot-Wash, and MICROSCOPE working-copy provenance.
- `VERIFICATION_SPEC.md`: primary command, threshold, and artifact contract.
- `CORE_GR_PROGRAM_DEPENDENCY_SPEC.md`: bounded mapping from the core candidate program into Topic 0.19.
- `UPDATE_LOG.md`: durable record of dependency hardening passes.
- `METHOD.md`: evidence lanes and dependency policy.
- `LIMITATIONS.md`: boundaries for GR, equivalence, and singularity claims.
- `Code/01_Engine/Engine_Gravity_GR.py`: constant package and weak-field calculations.
- `Code/03_Research/Research_G_Constant.py`: primary verifier.
