# Method

## Problem Target

This topic investigates whether UET-style information-field terms can organize selected cluster-scale missing-mass and offset diagnostics. The current hardening target is a reproducible diagnostic workflow, not a finished cluster dark-matter replacement.

## Evidence Lanes

| Lane | Code path | Current status |
| :-- | :-- | :-- |
| Virial/missing-mass scale | `Code/01_Engine/cluster_solver.py`, `Code/02_Proof/Proof_Virial_Mass.py`, `Code/03_Research/Research_Cluster_Virial.py` | heuristic bridge with source-labeled secondary datasets |
| Information-halo grid model | `Code/01_Engine/Engine_Cluster_Dynamics.py` | model-unit engine diagnostic |
| Bullet Cluster offset | `Code/03_Research/Research_BulletCluster_Offset.py` | primary qualitative artifact, expected `WARN` |
| JWST/formation-rate side lane | `Code/03_Research/Research_JWST_Formation_Rate.py` | excluded from primary cluster-dynamics claims |

## Variable Framing

| Variable | Meaning | Unit convention | Current role |
| :-- | :-- | :-- | :-- |
| `R` | cluster radius | m in engine; Mpc in datasets | virial comparator |
| `v` / `sigma` | velocity dispersion | m/s in engine; km/s in datasets | virial comparator |
| `M` | mass | kg in engine; `Msun` in datasets | mass comparator |
| `a0` | acceleration bridge | m/s^2 | heuristic UET/MOND-like anchor |
| `C` | baryonic grid field | model units | information-halo diagnostic |
| `I_halo` | information-halo field | model units | effective-mass diagnostic |
| `offset_kpc` | observed lensing/X-ray separation | kpc | primary Bullet Cluster data value |
| `offset_model_units` | toy gas/halo separation | dimensionless | qualitative sign diagnostic |

## Primary Verification Method

1. Load `Data/Bullet_Cluster_Coordinates.json`.
2. Record source label, unit convention, and file hash.
3. Run a one-dimensional toy gas/halo drag simulation.
4. Compare only the sign of separation, not the magnitude.
5. Write artifact status `WARN` when qualitative sign matches but kpc calibration is absent.

## Assumptions

- Gas is represented as a dragged component; lensing/halo is represented as an undragged component.
- The toy model is intentionally dimensionless.
- A positive model offset is a diagnostic, not a fitted Bullet Cluster prediction.
- Virial acceleration bridge terms require separate multi-cluster testing before claim promotion.

## Domain of Validity

- Internal diagnostic workflow for selected cluster-dynamics ideas.
- Claim Class D qualitative diagnostic for the current Bullet Cluster artifact.

## Excluded Cases

- Predicting the observed 480 kpc and 120 kpc Bullet Cluster offsets.
- Reproducing lensing maps or mass reconstructions.
- Solving the cluster missing-mass problem.
- Replacing dark matter across cluster cosmology.

## Dependency Policy

- `0.0_Grand_Unification` may list `0.15` only as an unresolved cluster-diagnostics module.
- `0.1_Galaxy_Rotation_Problem`, `0.3_Cosmology_Hubble_Tension`, `0.23_Unity_Scale_Link`, and `0.26_Cosmic_Dynamic_Frame` must inherit the dimensional-calibration limitation if they depend on `0.15`.
