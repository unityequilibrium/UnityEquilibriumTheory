# Baseline Comparison

- Primary comparison is against published Planck and SH0ES values
- Topic documentation uses LCDM as the contextual baseline where the tension remains
- Any claim stronger than `internal benchmark comparison` should require a fuller documented
  inference workflow and independent rerun

## Current scalar benchmark

| Quantity | Value | Unit | Source role |
| :-- | --: | :-- | :-- |
| Planck H0 | 67.4 | `km s^-1 Mpc^-1` | early/CMB baseline |
| SH0ES H0 | 73.04 | `km s^-1 Mpc^-1` | late/local comparator |
| Observed gap | 5.64 | `km s^-1 Mpc^-1` | benchmark target |
| UET scalar gap | 5.758 | `km s^-1 Mpc^-1` | model output |
| Relative error | 2.085 | percent | primary metric |

Artifact: `Result/artifacts/hubble_comparison_validation.json`

## Boundary

This is a scalar H0-gap comparison. It does not validate the full Planck likelihood, SH0ES
distance ladder, BAO consistency, SN covariance, structure growth, or dark-energy sector.
