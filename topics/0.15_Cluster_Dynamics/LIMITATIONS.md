# Limitations

- The primary Bullet Cluster verifier is qualitative and dimensionless; it does not predict the observed kpc offsets.
- The expected honest artifact status is `WARN`, not `PASS`, until dimensional calibration and numeric thresholds exist.
- The gas/halo drag constants are heuristic toy parameters and can produce separation by construction.
- The virial acceleration bridge uses `a0 = 0.8e-10 m/s^2`; this is a heuristic/benchmark anchor until provenance and multi-cluster sensitivity are documented.
- The information-halo grid engine uses model-unit density fields and should not be interpreted as physical lensing mass without unit mapping.
- Local source-labeled datasets exist, but DOI/URL capture and transcription audit are not complete for every working copy.
- This topic does not currently solve the Bullet Cluster, the cluster virial discrepancy, or the general dark-matter problem.
- Downstream core topics must inherit these limitations before using `0.15` as support for broader theory claims.
