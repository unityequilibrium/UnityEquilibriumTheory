# Verification Spec

- Primary command:
  - `python docs/topics/0.3_Cosmology_Hubble_Tension/Code/03_Research/Research_Hubble_Comparison.py`
- Inputs:
  - Planck 2018 H0 reference
  - SH0ES 2022 H0 reference
  - NIST/CODATA fine-structure constant record for `alpha_em`
  - `Data/03_Research/source_lock_manifest.json`
- Reported metrics:
  - Absolute H0 gap
  - Relative percentage error in gap explanation
  - Hubble-frame coupling and its source
  - scalar H0 uncertainties as recorded in source records
  - source-lock manifest hash and source-record hashes
- Fixed threshold:
  - Current script uses an internal pass threshold of `< 20%` relative error
- Artifact target:
  - `Result/artifacts/hubble_comparison_validation.json`
- Latest rerun:
  - artifact status: `PASS`
  - relative error: about `2.085%`
  - observed gap: about `5.64 km s^-1 Mpc^-1`
  - UET scalar gap: about `5.758 km s^-1 Mpc^-1`
- Interpretation:
  - Treat output as an internal comparison record, not external cosmology validation
  - The comparison must not optimize beta against the H0 values; the accepted coupling source
    is `sqrt(alpha_em)` from the central constants module
  - A PASS does not close BAO/SN/CMB likelihood consistency, high-z behavior, or dark energy.
