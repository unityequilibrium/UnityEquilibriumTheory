# Data Manifest

| Item | Local path | Source | Provenance status |
|:--|:--|:--|:--|
| Canonical fluid reference | `docs/references.bib#reynolds_1883` | Reynolds 1883 | Citation-backed reference |
| Internal benchmark configs | Topic-local files under `Data/` | Repository-generated | Internal benchmark material |
| Benchmark outputs | Topic-local files under `Result/` | Repository-generated | Internal results only |
| Source-lock manifest | `Data/03_Research/source_lock_manifest.json` | Topic-derived provenance package | Hashed by primary verifier |

External-source audit status: `internal benchmark package`.

Priority remediation:

- Add at least one external CFD/turbulence validation dataset before treating this topic as
  externally data-grounded.
- Candidate sources: Johns Hopkins Turbulence Database, NASA CFD validation cases, and
  standard ERCOFTAC-style benchmark cases.
- Keep current internal speed/stability artifacts, but do not treat them as replacement for
  real fluid-observation or high-fidelity CFD benchmark data.
- Current primary artifact now records the source-lock manifest hash, benchmark-script hash,
  and core master-equation hash.

## J01 evidence package

- Manufactured fields are generated analytically by Code/03_Research/Research_Fluid_State_Velocity_Representability.py; they are periodic internal controls, not an external dataset.
- Topic 10 engine and Core source paths, roles, unit scope, and SHA-256 hashes are recorded in Result/artifacts/fluid_state_velocity_representability_audit.json.
- The engine source is audited, but a trajectory was not executed in the current runtime.
