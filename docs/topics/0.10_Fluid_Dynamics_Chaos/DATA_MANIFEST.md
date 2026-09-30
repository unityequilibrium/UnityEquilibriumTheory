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

## Vector-state reference source package (2026-09-30)

- Synthetic fields, amplitudes, coefficients and thresholds are recorded in
  Data/03_Research/fluid_vector_state_research_contract.json. No real fluid data,
  He-4 constants, alpha, Z, theta_T or e0 are imported.
- Canonical Core scalar expressions are extracted statically and hashed; 2D
  continuum extension and independent momentum/material-rate dynamics are stated
  constitutive assumptions.
- External method/reference: [Abels, Garcke and Grün, arXiv:1104.1336v1](https://arxiv.org/abs/1104.1336v1),
  Section 1, equations (1.1)-(1.4), accessed 2026-09-30. It supplies a standard
  constant-density capillary-stress comparator, not the proposed Q/Phi extension,
  UET SI calibration or numerical data.
- Result/artifacts/fluid_vector_state_contract_audit.json records nine local input
  SHA-256 identities. The initial insufficient-sensitivity FAIL remains separate.
- Controls were amended after preview without tolerance changes; this is not a
  blind holdout or preregistered physical comparison.
## Variational reference inputs

No external material data are added. Synthetic periodic spacetime controls,
thresholds and source roles are in
Data/03_Research/fluid_vector_variational_origin_contract.json. The action audit
hashes its script, helper, contract, parent contract, candidate registry/card and
canonical scalar source. Holm-Marsden-Ratiu and Holm-Trouve-Younes are primary
kinematic-method references; their external physical/image boundary conditions
are not imported. Coefficients use parent normalized controls only; no He-4
calibration, material transport, blind holdout or thermal-response input is used.
