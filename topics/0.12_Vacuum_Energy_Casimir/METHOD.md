# Method

## Problem Target

This topic tests the implemented vacuum/Casimir engine against a measured sphere-plate Casimir force curve. The current hardening target is not a full cosmological-constant solution; it is a controlled benchmark that can be audited for data, units, formulas, thresholds, and artifacts.

## Core Components

- Engine: `Code/01_Engine/Engine_Vacuum.py`
- Primary verifier: `Code/03_Research/Research_Casimir.py`
- Formula registry: `FORMULA_AUDIT.md`
- Primary dataset: `Data/03_Research/mohideen_1998_casimir.json`

## Variable Framing

| Variable | Meaning | Unit convention | Current role |
| :-- | :-- | :-- | :-- |
| `d` | separation | dataset nm, engine m | independent benchmark axis |
| `R` | sphere radius | dataset/model um, engine m | geometry parameter |
| `F_exp` | measured attractive force magnitude | pN converted to nN | reference target |
| `F_uet` | model force | nN | predicted benchmark value |
| `lambda_p` | gold plasma wavelength heuristic | m | finite-conductivity correction |
| `beta` | UET coupling parameter | dimensionless | currently `1.0`; not fit in the primary verifier |

## Verification Method

1. Load the Mohideen/Roy working dataset.
2. Convert force and geometry units explicitly.
3. Evaluate the sphere-plate PFA formula plus finite-conductivity correction.
4. Compute per-point relative error, average relative error, and maximum relative error.
5. Write a schema `1.1` artifact with dataset hash, thresholds, metrics, and limitations.

## Assumptions

- The primary comparison is a sphere-plate Casimir benchmark, not a parallel-plate pressure benchmark.
- The finite-conductivity correction is a heuristic model component; the clipped floor must be treated as a possible source of artificial agreement.
- The model radius is currently `200 um` while the dataset radius is `196 um`; this is close but not identical and must be tracked.

## Domain of Validity

- Topic-local Casimir force comparison over the separation range present in the primary dataset.
- Claim Class C internal benchmark, if the artifact passes fixed thresholds.

## Excluded Cases

- A derivation of observed dark-energy density.
- A solution to the vacuum catastrophe.
- A theorem-level proof of Planck-scale vacuum discreteness.
- Any downstream core-theory claim that uses `0.12` as cosmology evidence without a separate dark-energy bridge artifact.

## Dependency Policy

- `0.0_Grand_Unification` may index `0.12` as a Casimir benchmark and must inherit the open dark-energy limitation.
- `0.13_Thermodynamic_Bridge`, `0.23_Unity_Scale_Link`, and `0.26_Cosmic_Dynamic_Frame` may cite `0.12` only for verified boundary-force behavior unless a future cosmology verifier is added.
