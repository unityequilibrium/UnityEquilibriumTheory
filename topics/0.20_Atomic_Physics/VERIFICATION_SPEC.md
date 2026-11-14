# Verification Spec

## Primary Command

```powershell
python docs/topics/0.20_Atomic_Physics/Code/03_Research/Research_Rydberg_Validation.py
```

## Inputs

| Input | Role | Required identity |
| :-- | :-- | :-- |
| `Data/03_Research/nist_hydrogen_spectrum.json` | NIST hydrogen line working copy | SHA256 and source DOI/URL recorded in artifact |
| `Data/03_Research/codata_2018_atomic.json` | CODATA atomic constants working copy | SHA256 and DOI recorded in artifact |

## Metrics

- Per-line predicted vacuum wavelength in nm.
- Per-line wavelength error in ppm.
- Average wavelength error in ppm.
- Maximum wavelength error in ppm.
- Fitted slope through origin for `1/lambda` vs. Rydberg geometric term.
- Slope error relative to CODATA `R_H`.

## Fixed Thresholds

| Metric | PASS threshold |
| :-- | :-- |
| Average wavelength error | `<= 100 ppm` |
| Maximum wavelength error | `<= 250 ppm` |
| Fitted slope error | `<= 250 ppm` |

## Artifact Target

- `Result/artifacts/0_20_atomic_physics_verification.json`

The artifact must record:

- PASS/FAIL status and claim class
- command and timestamp
- dataset paths, hashes, source labels, DOI/URL
- formula IDs
- thresholds, metrics, per-line residuals, and limitations

## Interpretation

A PASS supports only a Claim Class C internal hydrogen-spectrum benchmark using the standard Rydberg relation. It does not derive `R_H` from UET first principles and does not validate fine structure, Lamb shift, helium, or many-electron atoms.
