---
layout: article
title: "UET Topic 0.17: Mass Generation"
description: "Evidence-bounded overview for the mass-generation topic in the UET repository."
---

# 0.17 Mass Generation

Topic status: core research, draft.

This topic studies selected particle-mass and Higgs-coupling benchmarks. The current primary verifier checks a topic-local Higgs coupling modifier dataset against the Standard Model normalized baseline `kappa = 1`. Lepton/Koide material is retained as a separate diagnostic branch until it has its own artifact, source-locked dataset choice, and threshold.

## Current Claim Class

- Claim class: internal benchmark/run-contract support for Higgs coupling consistency.
- Current artifact: `Result/artifacts/0_17_mass_generation_verification.json`.
- Current verifier: `Code/03_Research/Research_Higgs_Coupling.py`.
- Data posture: source-referenced local working copies, not raw-source archived.

## Evidence Boundary

The repository can currently support conservative statements such as:

- The Higgs coupling verifier runs on the declared local `higgs_coupling_data.json` input.
- The current dataset has average absolute deviation from the SM-normalized baseline `kappa = 1`.
- Koide/tau calculations exist as diagnostic algebraic branches.

The current evidence package does not establish a first-principles mass-generation mechanism, a replacement for the Higgs mechanism, a complete Standard Model mass hierarchy derivation, or a formal proof of Koide from UET.

## Core Files

- `FORMULA_AUDIT.md`: reviewed registry for Higgs coupling, Koide, tau prediction, Planck exponential ansatz, and mass ratios.
- `DATA_MANIFEST.md`: source-referenced local data files, hashes, unit conventions, and benchmark roles.
- `VERIFICATION_SPEC.md`: primary verifier command and artifact contract.
- `METHOD.md`: method boundary and excluded cases.
- `LIMITATIONS.md`: scientific and verification limitations.
- `Code/03_Research/Research_Higgs_Coupling.py`: current primary verifier.

## Verification

Primary command:

```powershell
$env:PYTHONIOENCODING='utf-8'; $env:PYTHONUTF8='1'; .\.venv\Scripts\python.exe docs\topics\0.17_Mass_Generation\Code\03_Research\Research_Higgs_Coupling.py
```

A pass means the primary script ran, wrote the artifact, and the average absolute `kappa` deviation remained below the working threshold. It does not certify the broader mass-generation theory.

## Next Hardening Tasks

1. Source-lock the exact upstream Higgs coupling table and preserve raw/provenance material under `docs/data/external/particle_physics/...`.
2. Replace the average-deviation gate with an uncertainty-aware metric such as pulls or chi-square.
3. Create a separate Koide/tau verifier artifact with the normative lepton dataset, tau uncertainty, and explicit "Koide-constrained inference" wording.
4. Decide whether the Planck exponential ansatz is a derived model, a fitted model, or an exploratory hypothesis; do not use it as proof until the parameter path is explicit.
5. Keep paper-facing claims tied to artifact ID, formula ID, dataset hash, and limitations.
