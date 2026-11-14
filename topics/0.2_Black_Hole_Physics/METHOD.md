# Method

## Problem target

This topic studies whether UET-style black-hole and sink-field models can reproduce selected black-hole observables and imaging-related benchmarks.

## Core components

### Engine components
- `Code/01_Engine/Engine_BlackHole.py`
- `Code/01_Engine/Engine_Supersonic_Sink.py`

### Proof-oriented components
- `Code/02_Proof/Proof_Singularity_Resolution.py`

### Research and comparison components
- `Code/03_Research/Research_CCBH_Analysis.py`
- `Code/03_Research/Research_EHT_Validation.py`
- `Code/03_Research/Research_GW_Validation.py`

## Variable framing

- Primary modeled quantities: black-hole mass, radius, horizon-scale quantities, sink strength, and imaging residual terms
- Formula registry: see `FORMULA_AUDIT.md` for the current distinction between standard GR identities, EHT benchmark inputs, heuristic saturation terms, and data-blocked CCBH paths.

## Assumptions

- The topic uses effective modeling against selected observational references rather than a first-principles quantum-gravity derivation.

## Domain of validity

- Internal benchmark comparisons on selected black-hole catalog and imaging-style observables.

## Excluded cases

- A full replacement of general relativity or a complete singularity-resolution proof for all regimes.

## Parameter sensitivity note

- Boundary-condition choices and calibration terms remain important in several scripts.
- The primary verification gate is currently the EHT shadow-size comparison because its local working-copy inputs are present in the repository.
- The CCBH path is methodologically important but blocked as a primary gate until the Shen/Kormendy upstream datasets are preserved in the repo external-data cache with hashes and preprocessing notes.

## Dependency policy

- `0.13_Thermodynamic_Bridge` may reuse the entropy identity only with unit conversion and entropy/information-bit distinction.
- `0.19_Gravity_GR` may cite the EHT shadow gate as a benchmark comparison, not as a GR replacement proof.
- `0.0_Grand_Unification` should index the saturation-core path as a heuristic bridge until its physical core scale and verifier threshold are closed.
