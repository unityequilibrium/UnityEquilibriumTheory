# Topic 0.21: Yang-Mills Mass Gap - Code

This module tests a UET-inspired curvature-gap mechanism against a selected
lattice-QCD glueball benchmark. The code is a calibration-aware research harness,
not a standalone mathematical proof package.

## Code Structure

| Layer | Path | Role |
|:--|:--|:--|
| Engine | `01_Engine/Engine_Mass_Gap.py` | Computes a curvature-derived positive gap proxy |
| Diagnostic | `02_Proof/Proof_Mass_Gap.py` | Runs an internal scaling sanity check |
| Research verifier | `03_Research/Research_Mass_Gap.py` | Sweeps `alpha`, compares scalar glueball mass, writes artifact |
| Sweep utility | `03_Research/Research_Mass_Gap_Sweep.py` | Explores coupling sensitivity |

## Primary Command

```powershell
python docs/topics/0.21_Yang_Mills_Mass_Gap/Code/03_Research/Research_Mass_Gap.py
```

## Artifact Contract

The primary verifier writes:

- `Result/artifacts/mass_gap_validation.json`
- dataset and source-lock hashes
- best-fit `alpha`
- predicted and reference scalar glueball mass in MeV
- residual, reference uncertainty, and `PASS` or `WARN` status

## Interpretation

`PASS` means the calibrated scalar-glueball residual is inside the selected
reference-row uncertainty. `WARN` means the verifier ran but the current model is
outside that uncertainty. Neither status establishes the general mathematical
mass-gap problem by itself.
