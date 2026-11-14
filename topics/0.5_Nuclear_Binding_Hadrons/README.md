---
layout: article
title: "UET Topic 0.5: Nuclear Binding Hadrons"
description: "Conservative overview for the nuclear-binding and hadron topic in the UET repository."
---

# 0.5 Nuclear Binding Hadrons

## Problem

This topic explores whether UET-style geometric or information-overlap models can reproduce
selected nuclear-binding, hadron-mass, proton-radius, and strong-force benchmark behavior.

## Current status

- Metadata status: `Draft`
- Audit tier: `B`
- Data status: `manifested real dataset` for AME2020 binding and proton-radius benchmark layers
- Claim posture: source-backed internal benchmark workflow, not a complete strong-force theory

## What currently exists

- Engine scripts for binding-energy, light-nuclei, hadron, and QCD-bridge experiments
- Research scripts for binding-energy comparison, proton radius, quark masses, and related checks
- Topic-local data files including `Data/03_Research/Data_AME2020_Binding.json` and
  `Data/03_Research/Data_PDG_Quarks_2024.json`
- Competitor and visualization folders that support internal comparisons and plotting
- Root standards docs for method, data manifest, baseline, verification, limitations, and
  formula audit

## What this topic does not currently establish

- It does not establish a general derivation of QCD from first principles.
- It does not establish a formal mathematical proof of confinement.
- It does not yet provide a full-table pass/fail proof across AME2020.
- It does not yet source-lock every hadron/QCD embedded constant.
- Any reported match to selected isotopes or radii should therefore be treated as an internal
  benchmark result rather than external confirmation.

## Data and evidence notes

- AME2020 raw table data is locked under `docs/data/external/particle_physics/ame2020/`.
- The strict binding gate uses a raw-derived selected subset, while the full parsed AME2020
  table is reported separately as a diagnostic artifact.
- Proton-radius data is a source-backed local JSON benchmark.
- PDG quark masses and some hadron/QCD constants remain legacy/local snapshots and are not yet
  source-locked at the same standard.

## Verification notes

- Primary command:
  - `Code/03_Research/Research_Nuclear_Binding_SourceLocked.py`
- Diagnostic command:
  - `Code/03_Research/Research_Nuclear_Binding_FullTable_Diagnostic.py`
- Current strict artifact:
  - `Result/artifacts/nuclear_binding_source_locked_validation.json`
- Current diagnostic artifact:
  - `Result/artifacts/nuclear_binding_full_table_diagnostic.json`

## Reproducibility

Current verification commands:

```powershell
python docs/topics/0.5_Nuclear_Binding_Hadrons/Code/03_Research/Research_Nuclear_Binding_SourceLocked.py
python docs/topics/0.5_Nuclear_Binding_Hadrons/Code/03_Research/Research_Nuclear_Binding_FullTable_Diagnostic.py
```

The first command is the strict selected-subset gate. The second command is a diagnostic
for broad AME2020 table behavior and must not be described as a full-table pass.

## Next remediation steps

1. Split SEMF baseline and UET correction metrics in the primary artifact.
2. Source-lock SEMF coefficients and embedded hadron/QCD constants.
3. Fix the `alpha_s_uet_v2` data-shape bug before using that QCD branch in any verifier.
4. Make the confinement proof script return real pass/fail status instead of printing a result
   and returning `True`.
5. Keep light nuclei outside the heavy-nucleus pass claim unless a dedicated light-nuclei
   verifier is added.

## Current readiness status

`Draft`
