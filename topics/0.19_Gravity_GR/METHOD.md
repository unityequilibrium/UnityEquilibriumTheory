# Method

## Problem Target

This topic organizes UET gravity and GR bridge work into auditable lanes: source constants, weak-field formulas, equivalence-principle diagnostics, short-range gravity constraints, and future GR validation artifacts.

## Evidence Lanes

| Lane | Code/data path | Current status |
| :-- | :-- | :-- |
| CODATA constant checkpoint | `Research_G_Constant.py`, `codata_2018_gravity.json` | primary artifact, Claim Class C |
| Weak-field engine demos | `Engine_Gravity_GR.py` | formula registry only; no primary validation artifact |
| Equivalence principle | `Proof_Equivalence_Principle.py`, `microscope_2022.json` | open diagnostic; not experimental validation yet |
| Short-range gravity | `Research_ShortRange_Gravity.py`, Eot-Wash data | secondary comparator lane; needs artifact |
| Fluid-gravity derivation visuals | `Engine_Fluid_Gravity.py` | illustrative/derivation lane; not primary evidence |

## Variable Framing

| Variable | Meaning | Unit convention | Current role |
| :-- | :-- | :-- | :-- |
| `G` | Newtonian gravitational constant | m^3 kg^-1 s^-2 | primary checkpoint |
| `c` | speed of light | m/s | Planck-unit definition |
| `hbar` | reduced Planck constant | J s | Planck-unit definition |
| `M` | source mass | kg | weak-field demo |
| `r` | radius/separation | m | weak-field demo |
| `eta` | Eotvos parameter | dimensionless | open equivalence lane |
| `alpha`, `lambda` | Yukawa short-range correction strength/scale | dimensionless, m | secondary short-range lane |

## Primary Verification Method

1. Load CODATA 2018 gravity constants working copy.
2. Load engine constants through `UETGravityEngine.get_planck_units()`.
3. Compare engine `G` to CODATA `G`.
4. Record Planck-unit metrics.
5. Write artifact with hash, DOI, threshold, metrics, and limitations.

## Assumptions

- The primary run is a source-constant checkpoint.
- Matching CODATA does not imply derivation.
- Weak-field formulas are standard diagnostics until separately validated.

## Domain of Validity

- Internal source-constant consistency check for the gravity engine.
- Formula registry for selected weak-field and comparator relations.

## Excluded Cases

- Derivation of Einstein field equations.
- Light-bending or Mercury-perihelion validation.
- Experimental equivalence-principle validation.
- Singularity avoidance.
- Quantum-gravity closure.

## Dependency Policy

- `0.0_Grand_Unification`, `0.2_Black_Hole_Physics`, `0.3_Cosmology_Hubble_Tension`, `0.21_Yang_Mills_Mass_Gap`, `0.23_Unity_Scale_Link`, and `0.26_Cosmic_Dynamic_Frame` may cite this topic only as a constants/weak-field registry unless they cite future dedicated GR artifacts.
