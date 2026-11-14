# Method

## Problem target

This topic studies whether UET-inspired information-drag ideas can reproduce selected particle-mass hierarchy benchmarks.

The current audit-backed method is narrower than the topic title. The primary verifier checks Higgs coupling modifiers against the SM-normalized `kappa = 1` baseline. Lepton/Koide and Planck-exponential branches are diagnostic until they receive separate artifacts and source-locked data choices.

## Core components

### Engine components
- `Code/01_Engine/Engine_Mass_Higgs.py`

### Proof-oriented components
- `Code/02_Proof/Proof_Lepton_Mass.py`

### Research and comparison components
- `Code/03_Research/Research_Higgs_Coupling.py`
- `Code/03_Research/Research_Mass_Mechanism.py`
- `Code/03_Research/Verify_Mass_Generation.py`

The reviewed formula registry is `FORMULA_AUDIT.md`.

## Variable framing

- Primary modeled quantities: particle masses, coupling-strength terms, hierarchy ratios, and Koide-style quantities
- Current verifier-backed quantities: Higgs coupling modifiers `kappa`, particle masses in GeV, and average/max absolute deviation from `kappa = 1`.

## Assumptions

- The current package is an internal benchmark environment around selected lepton and Higgs-related files.
- The normalized Higgs `kappa` file already encodes a Standard Model comparison; passing the current gate is not by itself evidence for a UET-specific correction.

## Domain of validity

- Selected lepton-mass and coupling comparisons represented in topic-local PDG-style files.
- Current pass/fail interpretation is limited to the Higgs coupling verifier run contract.

## Excluded cases

- A complete derivation of all Standard Model masses or a full replacement of the Higgs mechanism.
- A formal proof of Koide, an independent prediction of tau mass from first principles, and a complete electroweak symmetry-breaking mechanism.

## Parameter sensitivity note

- Hierarchy fits and ratio claims remain sensitive to the chosen benchmark framing.
- Koide/tau claims are sensitive to whether the topic uses `lepton_data.json`, `pdg_2024_leptons.json`, or `PDG_Leptons.csv`.
