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

## Mode-eligibility source and diagnostic package

Contract: Data/03_Research/fluid_second_sound_mode_eligibility_contract.json.
Candidate coefficients come from the existing normalized vector contract and
canonical Core scalar AST; the new derivative/card/registry/verifier plus the
Topic 13 protocol/contact-response context are input hashed in the current artifact.
No He-4 speed, matching constant or material transport value is a numerical input.

Primary method source: [Nikuni and Griffin](https://arxiv.org/abs/cond-mat/0009333),
Section IV (86)-(88), Appendix C (C1)-(C10), accessed 2026-09-30.
General two-fluid sound/entropy structure is used; dilute-gas/trap coefficients
are not transferred to liquid He-II. Existing NIST tables are observable context
only, and J02 calibration/response source-overlap restrictions remain.

The invalid complex-metric preview retains its original payload and SHA256 in
Result/artifacts/fluid_second_sound_mode_initial_metric_diagnostic.json.
The repaired artifact and three regression tests explicitly separate this
unaccepted preview from reference evidence. No independent observation is added.

## Two-fluid/EOS source requirements

New requirements and standard reference controls:
Data/03_Research/he4_two_fluid_thermodynamic_input_requirements.json and
Data/03_Research/fluid_two_fluid_eos_reference_contract.json.
No real He-II numeric row is extracted; all material values/uncertainties are null.
NIST Section 1 density/expansion follows SVP, Section 7 note (9) defines C_s at
saturation pressure, notes (11),(13) state enthalpy-path correction and unit
conversion; Section 8 notes (8),(9) identify calorimetry-integrated entropy and
its units. Fountain-pressure entropy is a separate candidate method with its
own source/uncertainty record. No statistical independence is assumed.

Nikuni-Griffin (86)-(88), (C1)-(C10) supplies general two-fluid structure; its
dilute-gas condensate-density and transport identities are not assigned to liquid
helium. The current artifact hashes eight local inputs. Prior mode/vector/action
source files stay unchanged, and Topic 13 protocol/calibration boundaries persist.

## He-II fixed-constraint candidate acquisition

Candidate: Data/03_Research/he4_tn1334_fixed_constraint_eos_source_candidate.json.
Card: HE4_FIXED_CONSTRAINT_EOS_SOURCE_CARD.md.
Verifier/output: Code/03_Research/Research_He4_Fixed_Constraint_EOS_Source.py;
Result/artifacts/he4_tn1334_fixed_constraint_eos_source_audit.json.

Source: https://nvlpubs.nist.gov/nistpubs/Legacy/TN/nbstechnicalnote1334.pdf,
September 1998 revised PDF, SHA256
1532e4c65e1d2bc29da10db9e9ffd57e48ed46070a583bd8019581b44dc81c22.
Full rendered printed pages 3,4,14,15 reviewed. Three liquid rows at
1.650/1.700/1.750 K preserve raw tokens and the corresponding derivative columns.
Temporary PDF path and upstream filename are recorded in the package; it is
not committed or required to rerun the offline audit. Numeric facts with
attribution only are distributed, not the full PDF.

Role: fitted-EOS source candidate and printing diagnostic, not independent
experimental validation. MPa and J/g units and dimensionless derivative
products are converted explicitly; all transport blanks/physical uncertainties
stay null. These rows are now ingested only in the new source package. The
previous two-fluid reference's statement of no numeric ingestion remains
correct for that historical wave; its hashed inputs and unassigned requirements
are unchanged. Topic 13 data/calibration/protocol are consumed read only.
