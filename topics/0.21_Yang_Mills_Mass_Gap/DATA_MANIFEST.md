# Data Manifest

## Source Inventory

| Item | Local path | Source | Provenance status | Benchmark role |
|:--|:--|:--|:--|:--|
| External source record | `docs/data/external/particle_physics/glueball/morningstar_peardon_1999/source_record.json` | Morningstar and Peardon, DOI `10.1103/PhysRevD.60.034509` | Source-pinned publication record | Primary bibliographic anchor |
| Lattice-QCD working copy | `data/03_Research/lattice_qcd_spectrum.json` | Curated topic working copy from the cited lattice-QCD reference | Derived/local working table | Scalar glueball benchmark input |
| Source-lock manifest | `data/03_Research/source_lock_manifest.json` | Topic manifest tying source record, derived table, and verifier | Hashable run input | Reproducibility gate |
| Benchmark citation | `docs/references.bib#morningstar_1999` | Published lattice-QCD benchmark | Citation-backed reference | Cross-document citation |

## Unit Convention

| Quantity | Unit | Source or conversion |
|:--|:--|:--|
| `mass_r0_units` | dimensionless lattice `m r0` | Topic working copy |
| `r0_physical_value_fm` | fm | Topic working-copy metadata |
| `hc_mev_fm` | MeV fm | Topic working-copy metadata |
| `mass_mev` | MeV | `mass_r0_units * hc_mev_fm / r0_physical_value_fm` |
| `reference_uncertainty_mev` | MeV | `uncertainty * hc_mev_fm / r0_physical_value_fm` |

## Integrity Requirements

- The verifier records hashes for the lattice working copy, source-lock manifest, benchmark script, engine script, and source record.
- This topic currently keeps its historical lowercase `data/` directory; future normalization can rename it to `Data/` repo-wide, but the verifier and manifest now point to the real tracked path.
- The current dataset is a curated topic table, not a full raw-table extraction package from the publisher.
- Any stronger result must first replace or supplement the working copy with reproducible upstream extraction notes and multi-state benchmark coverage.
