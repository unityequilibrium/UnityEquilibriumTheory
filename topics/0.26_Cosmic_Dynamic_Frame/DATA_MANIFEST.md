# Data Manifest

Current data reality status: "real source referenced with local working copies"

External-source audit status: `Laniakea/Cosmicflows/Pioneer source records pinned; raw tables and preprocessing still open`.

Priority remediation:

- Archive raw Cosmicflows/Laniakea flow tables and Pioneer residual/telemetry tables where
  they support the dynamic-frame argument.
- Add observer-frame metadata for every cosmic-flow dataset: reference frame, velocity
  convention, distance calibration, redshift correction, and whether values are observed or
  model-inferred.
- Treat local subsets as working derivatives until raw source, preprocessing, and hashes are
  documented.
- See `docs/meta/core_data_external_source_audit.md` for the cross-topic data-hardening plan.

| Item | Local path | Source | Provenance status |
|:--|:--|:--|:--|
| Laniakea source record | `docs/data/external/cosmology/laniakea/tully_2014/source_record.json` | Tully et al. 2014 Nature, DOI `10.1038/nature13674` | Source record present; SHA-256 `880397cf02e92fd472b434a1e9f8d2bee6a0ac09d03c40daf90ebf5bb6c40eec`; raw peculiar-velocity reconstruction not stored. |
| Cosmicflows-3 source record | `docs/data/external/cosmology/cosmicflows/cosmicflows3/source_record.json` | Tully, Courtois, Sorce 2016 AJ, DOI `10.3847/0004-6256/152/2/50` | Source record present; SHA-256 `72c130a7c003dc69e01d82adb8ba1d9e3a4aa6426caf585f0fd5b64a2af70b17`; raw catalog extraction not verified. |
| Pioneer anomaly source record | `docs/data/external/spacecraft/pioneer_anomaly/anderson_2002/source_record.json` | Anderson et al. 2002 PRD, DOI `10.1103/PhysRevD.65.082004` | Source record present; SHA-256 `aa71373b211ffb9e1f36e72bc16cdae00f6917d4b2b17a6364bc0d3e921c612f`; telemetry/residual raw tables not stored. |
| source_lock_manifest.json | `Data/03_Research/source_lock_manifest.json` | Topic-derived source-lock package tying local working copies to source records | Present; SHA-256 `eb6c07a3cc54ca8d6de672f63f8bcbb4d4a0c0fafb0139ef0bba7b7986478816`; upgrades provenance but not physical claim class. |
| Laniakea_Flows.json | `Data/03_Research/Laniakea_Flows.json` | Topic-local landmark working copy tied to Laniakea source record | Visualization input only; not raw flow reconstruction. |
| Cosmicflows_3_Subset.csv | `Data/Cosmicflows_3_Subset.csv` | Topic-local subset tied to Cosmicflows-3 source record | Working copy; frame, calibration, and extraction path still need audit. |
| Download_Cosmic_Data.py | `Data/Download_Cosmic_Data.py` | Topic-local working copy or generated benchmark input | Manual, placeholder, or partially scripted data handling is still present. |
| Pioneer_Anomaly_Data.csv | `Data/Pioneer_Anomaly_Data.csv` | Topic-local working copy tied to Pioneer anomaly source record | Diagnostic only; competitor thermal-recoil baseline absent. |

Repository note:

- This manifest was created during the repo standards pass and should be tightened further in a later provenance-normalization wave.
- Until raw tables, observer-frame metadata, preprocessing notes, and upstream hashes are frozen, treat the dataset package as source-referenced working copies rather than an archival release.
