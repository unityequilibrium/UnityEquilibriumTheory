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

## He-II entropy branch candidate (2026-09-30)

- Local numeric/source contract: [he4_entropy_source_and_reference_contract.json](Data/03_Research/he4_entropy_source_and_reference_contract.json).
- Official source: [Donnelly-Barenghi 1998](https://srd.nist.gov/jpcrdreprint/1.556028.pdf),
  DOI 10.1063/1.556028; SHA256 c3e03d88b803d36628587638be98e0f3af1e6613b15f81e04eedcc17f3d5442e.
- Full PDF pages 28-30 (printed 1243-1245) visually inspected. Preserve raw
  T90 and entropy tokens from Tables 8.3/8.5 at 1.65/1.70/1.75 K; convert
  J/(g K) by 1000. Recommended spline/integral values, not raw independent trials.
- Table 8.3 fountain-pressure ancestry differs from Table 8.5 calorimetry;
  the latter's zero-T integration convention is explicit and not transferred
  to TN1334. Row uncertainty/covariance and physical temperature-scale matching
  remain unknown. Source precision/accuracy is not assigned as row errors.
- Primary [Singsaas-Ahlers paper](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.29.4951)
  metadata gives 1984-05-01, despite review bibliography year 1983; abstract
  only, no full protocol/thesis acquired. Exact independence from sound-derived
  superfluid inputs remains unresolved.
- Public package contains small numerical facts/attribution only; copyrighted
  full PDF and render cache are ignored and not offline audit dependencies.
  TN1334 package, null admitted inputs and Topic 13 matching constants unchanged.

## Core common-flow source-function input package

[fluid_core_o2_common_flow_contract.json](Data/03_Research/fluid_core_o2_common_flow_contract.json)
lists canonical migrated Core paths, selected AST definitions, explicit fixed-Phi
natural-unit controls and versioned primary method sources. The result records
whole-file and extracted-definition hashes. Historical Core static artifact
and Topic 13 protocol hashes are boundary-context identities; obsolete historical
source paths are not asserted to be fresh runtime evidence.

No additional material measurements, He-II density/stiffness, entropy offset,
sound target, coefficient fit or SI mass conversion is ingested. Lambda=1 and
the five T/mu points are declared computational controls only. Previous TN1334,
entropy-source and Topic 13 packages remain byte-unchanged. The new candidate
composition failure is source-function evidence, not external validation.

## Gaussian phase-flow reference input package

[Flow contract](Data/03_Research/fluid_core_o2_flow_hessian_contract.json),
[derivation](CORE_O2_FLOW_HESSIAN_DERIVATION.md) and
[98-check artifact](Result/artifacts/fluid_core_o2_flow_hessian_audit.json)
identify current Core/Topic 13 inputs, previous source adapter and tree-only
FAIL artifact by hashes. Core and Topic 13 source files are unchanged.
The new finite-flow kernel is a topic-local derived reference, not source data.

The first output and exact verifier source are archived under Result/previews/.
The current artifact maps the original verifier hash to that archive explicitly;
its historical original-path hashes are not asserted to match today's verifier.
No new physical material values, fitting, SI assignment, source dataset or
independent measurement is introduced.

## Local ideal current/stress and mode inputs

[Contract](Data/03_Research/fluid_core_o2_ideal_modes_contract.json) and
[171-check artifact](Result/artifacts/fluid_core_o2_ideal_modes_audit.json)
identify the current Core source-mode functions, previous source/phase adapters
and the phase artifact by hashes. EOS derivatives are newly evaluated integrals,
not new experimental data. Core/Topic 13 sources and all prior packages are unchanged.

Entropy conservation is an additional ideal local-equilibrium assumption.
No collision/relaxation dataset or physical hydrodynamic frequency window is
provided. Local source/metric variations test a declared Taylor action.
Natural current coefficients and two acoustic pairs have no material SI map,
new calibration, fitted speed or independent He-II validation.

## Leading Goldstone collision input identity

[The contract](Data/03_Research/fluid_core_o2_goldstone_collision_contract.json)
and [current artifact](Result/artifacts/fluid_core_o2_goldstone_collision_audit.json)
hash the source-verbatim spectrum adapter, Core action, prior ideal artifact
and historical Topic13 collision/reconciliation/Kubo records. Old path strings
inside historical artifacts are evidence of their original layout, not current
source-fresh reruns. Existing source files and prior result packages are unchanged.

The first failed diagnostic and exact verifier are retained with explicit
historical roles. New rates have natural energy units; no experimental lifetime,
SI conversion, fitted material coupling or measured He-II source is supplied.
Primary references are selected leading-action/FGR/NR correspondence only.

## Shared Goldstone collision/current identity

[The new contract](Data/03_Research/fluid_core_o2_goldstone_galerkin_contract.json)
and [artifact](Result/artifacts/fluid_core_o2_goldstone_galerkin_audit.json)
hash the prior Goldstone card/source/artifact, current Core AST sources and
Topic13 normal scalar Galerkin/reconciliation evidence. Historical paths/records
remain historical; no old artifact is relabeled as a current full Core rerun.

New natural low-T/coupling controls are exploratory, not liquid-He rows or
recalibration of the earlier ideal lambda=1 states. Selected primary
arXiv1407.7431v2 equations10-23 supplies method/current-constraint correspondence
only; its downward-curving neutron/binary-collision rates are not transferred.
First diagnostic/source archives are explicitly historical. No material lifetime,
heat-current mapping, SI conductivity or independent response dataset is added.

## Stable-vector refinement input identity

[Contract](Data/03_Research/fluid_core_o2_vector_refinement_contract.json)
and [artifact](Result/artifacts/fluid_core_o2_vector_refinement_audit.json)
hash the prior Galerkin contract/verifier/artifact and propagate all its source
input identities, alongside the pre-execution method card/registry/current code.
No old hashed package is modified, and no historical proof is a current Core run.

Larger cutoffs/bases use the same low-T/coupling reference and energy validity
bound. Orthogonalization is a numerical coordinate change; SOFT is explicit
trial enrichment, neither an interaction adjustment nor data fitting.
No new He-II row, SI scale, material transport coefficient or blind source.

## Independent infrared trial source and repair identity

[Contract](Data/03_Research/fluid_core_o2_infrared_trials_contract.json)
and [artifact](Result/artifacts/fluid_core_o2_infrared_trials_audit.json)
hash the immutable vector package and all its input ancestors, new trial card/
registry and code, archived first source/output, plus the separate geometry
repair card/registry. First contract/card/registry bytes remain unchanged.
Historical source hashes are verified through the exact first-source archive.

Same low-T/coupling/material boundaries remain. Smooth epsilon is a numerical
trial parameter, not a scattering regulator or material length. Across30 banks,
576 near-collinear events use gap-only high precision; source B/r/mu consistency
is checked. The unchanged old matrix/response correspondence is below1.3e-13.
No new physical input, material coefficient, SI mapping or blind source is added.
