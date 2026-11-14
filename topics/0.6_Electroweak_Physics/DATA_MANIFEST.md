# Data Manifest

Current data reality status: `manifested real dataset`

External-source audit status: `PDG 2025 masses are source-locked through SQLite; the effective weak-mixing-angle and Fermi-constant reference are carried in a structured checked reference package; the current PDG SQLite mapping audit records no direct upstream weak-mixing-angle match.`

Priority remediation:

- Keep `docs/data/external/particle_physics/pdg/pdg-2025-v0.2.2.sqlite` as the primary upstream source for `mW`, `mZ`, and `mH`.
- Keep `docs/data/external/particle_physics/pdg/electroweak_mapping_audit.json` as the explicit record of the upstream mapping search for `sin^2(theta_W)`.
- Keep `docs/data/external/particle_physics/pdg/electroweak_reference_package.json` as the structured electroweak comparison package for topic `0.6`.
- Keep `docs/data/external/particle_physics/pdg/electroweak_benchmark_package.json` as the expanded benchmark package that separates source-linked core observables from checked-local neutron and running-angle layers.
- Keep `Data/03_Research/source_lock_manifest.json` as the topic-local source-lock manifest that binds external source files, package hashes, unit roles, and benchmark roles for the verifier artifacts.
- Preserve `Data/03_Research/pdg_electroweak_2024.json` only as the checked local reference that currently supplies the effective weak-mixing-angle and Fermi-constant layer until a direct upstream mapping is added.
- Treat `Data/Download_Electroweak.py` as a legacy helper, not as the canonical scientific data path.

| Item | Local path | Source | Provenance status |
| :-- | :-- | :-- | :-- |
| PDG 2025 SQLite | `docs/data/external/particle_physics/pdg/pdg-2025-v0.2.2.sqlite` | PDG 2025 | Source-locked machine-readable benchmark |
| Electroweak mapping audit | `docs/data/external/particle_physics/pdg/electroweak_mapping_audit.json` | Query audit over PDG 2025 SQLite | Upstream mapping audit |
| Electroweak reference package | `docs/data/external/particle_physics/pdg/electroweak_reference_package.json` | Built from PDG 2025 SQLite plus checked local electroweak reference | Structured comparison package |
| Electroweak benchmark package | `docs/data/external/particle_physics/pdg/electroweak_benchmark_package.json` | Built from the reference package plus checked-local neutron and running-angle layers | Structured benchmark package |
| Source-lock manifest | `Data/03_Research/source_lock_manifest.json` | Topic-derived provenance package | Hashed by both primary verifier artifacts |
| Checked local electroweak reference | `Data/03_Research/pdg_electroweak_2024.json` | Topic-local checked reference | Checked local reference |
| Legacy electroweak CSV snapshot | `Data/Electroweak_LEP.csv` | Topic-local working copy | Legacy local snapshot |
| Legacy downloader | `Data/Download_Electroweak.py` | Topic-local helper | Legacy acquisition helper |

Repository note:

- Topic `0.6` now reads a structured electroweak reference package rather than carrying the weak-mixing-angle note inline in the verifier.
- Topic `0.6` also has an expanded benchmark package that keeps neutron lifetime as a checked-local benchmark gate and running-angle points as diagnostic-only.
- Both current verifier artifacts record hashes for the source-lock manifest, PDG SQLite files, mapping audit, reference package, and expanded benchmark package.
- The remaining caveat is specific and explicit: the effective weak-mixing-angle observable is not yet sourced from a direct upstream mapping in the current PDG SQLite workflow, and the mapping audit file records that negative result directly.
