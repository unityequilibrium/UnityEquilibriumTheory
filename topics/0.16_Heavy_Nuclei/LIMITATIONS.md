# Limitations

- The current UET bridge is implemented as a SEMF/liquid-drop mapping, not an independent first-principles derivation.
- The primary verifier uses AME2020 only for the U-235 binding checkpoint; Ba-141 and Kr-92 fragment masses are still bridge-derived.
- Artifact status is expected to be `WARN` until source-locked fragment masses and evaluated fission-energy thresholds are added.
- The current artifact does not validate the island of stability, shell corrections, half-lives, decay channels, or superheavy stability.
- `Data/AME2020_mass.txt` exists locally, but the engine parser still uses curated fallback checkpoints; this must not be presented as a fully parsed AME2020 pipeline.
- Secondary heavy-binding plots and pass rates are not primary evidence until they write machine-readable artifact rows.
- Downstream core topics must inherit these limitations before using `0.16` as nuclear evidence.
