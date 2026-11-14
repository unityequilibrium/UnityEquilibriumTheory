# Limitations

- Current data posture is source-referenced local working copies, not a fully normalized archival dataset package.
- Laniakea, Cosmicflows-3, and Pioneer source records are pinned under `docs/data/external/...`, but raw tables, observer-frame metadata, preprocessing scripts, and upstream hashes are still open.
- The primary verifier is a visualization/provenance gate. It does not test a cosmological model fit, dark-matter replacement, Bullet Cluster wake model, or Pioneer-drag physics.
- The galaxy-rotation branch must inherit the data, baseline, and uncertainty limits of `0.1_Galaxy_Rotation_Problem`; it cannot bootstrap stronger credibility from this topic alone.
- The Pioneer branch lacks a thermal-recoil competitor baseline and full telemetry/residual source package.
- Toroidal-cycle and dynamic-frame visualizations remain conceptual until converted into observable predictions and falsifiable gates.
- Internal script execution does not by itself establish external replication, formal proof, or broad physical closure.

## Current Claim Boundary

| Claim area | Allowed wording now | Blocker to stronger wording |
| :-- | :-- | :-- |
| Laniakea flow map | source-record-backed visualization/provenance artifact | raw flow table, frame convention, and residual benchmark |
| Dynamic frame | exploratory mechanism hypothesis | derivation with explicit units and model-vs-baseline fit |
| Galaxy rotation support | dependency candidate for `0.1` | SPARC-linked residual comparison and uncertainty-aware baseline |
| Pioneer drag | diagnostic source-referenced branch | raw telemetry, thermal-recoil competitor, and reproducible fit |
| Dark-matter replacement | not supported as a claim | multi-dataset lensing/rotation/cosmology model comparison |
| Toroidal cosmology | conceptual visualization | observable prediction and falsifiable verifier |
