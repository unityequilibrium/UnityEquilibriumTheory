# Measurement card and bounded alternative-testbed screen

Date: 2026-10-17. Owner: Topic13. Area: research-core.
Basis: completed [observer-discrimination result](Result/T13_OBSERVER_DISCRIMINATION_2026-10-17.md), commit `7e59d13ba`.
Status: source-backed feasibility/design decision, not new physical evidence or an executed cross-channel calculation.

## One-page measurement card

**Question:** Does a specified material realization support the inherited weak-response mechanical kernel and its independently constrained input/output relations? Do not start with “which curve can UET fit?”

**Three different claims:**

- A physical analog can test computation, inference and observer corrections, without validating the physical meaning of UET variables.
- A material effective-model test needs an independently justified mapping of variables, coefficients, sources and readouts to that material.
- A UET-specific mechanism test additionally needs a prediction or relation that an independently specified ordinary-material competitor cannot reproduce. Shared pole shape is not sufficient.

**Minimum package for the existing single-kernel discriminator:**

| Requirement | What must be recorded | Why it matters |
| --- | --- | --- |
| Material and state | Specimen, geometry, mode/eigenvector normalization, temperature, stress and boundary conditions | Different states cannot silently supply one common response curve |
| Drive | Same-state distinct controlled weak drives, angular-frequency/clock calibration and phase reference | One free ring-down is not several independently driven kernel samples |
| Response | Signed complex displacement Q1,Q2,Q3, or an independently established equivalent mechanical kernel | Intensity or magnitudes alone lose the needed phase/sign |
| Linear operator | Independent propagator and mode identification, with damping/domain treatment | A fitted resonance is not automatically the inherited lossless operator |
| Detector | Gain/sign, nonlinear response, bandwidth, exposure/integration, temporal transfer and reconstruction order | A detector can generate or hide harmonics |
| Unwanted forcing | Independent absence/bounds of direct harmonic drive, other modes and ordinary nonlinear forces | Do not assign every harmonic to the candidate mechanism |
| Error | Joint output/input bounds, correlation information or justified conservative enclosure | UNKNOWN is not zero and missing covariance is not independence |
| Data roles | Exact record identities, license/access, processing, calibration vs comparison, earlier exposure | Prevent circular validation and false blind-test claims |
| Discrimination | Frozen error rule, competitor prediction sets and a reserved comparison | Passing a curve shape does not establish a uniquely UET cause |

In the inherited conditional displacement lane, use x=(2*omega)^2 with omega in rad/s and kernel units m^-2 s^-2; raw frequency in Hz is not x. No numeric material coefficient, uncertainty threshold or gain floor is selected in this card.

**Admission decision:** an exploratory comparison can expose gaps, but physical acceptance cannot bypass missing model/operator/units/uncertainty requirements. For a new system, write its mapping before scoring observations; the graphite formula is not automatically portable. Existing He-4 needs its own stationary condensed state/current/observable operator and is not admitted by this card.

## Screen boundary and method

The new question is whether alternative platforms expose independent modal channels/calibration, not whether the parked graphite search can be repeated. Four source roles below were checked through primary publisher/author-repository material and repository metadata. No raw archive, supplementary movie, measured rows or reserved target was downloaded or scored; no author was contacted. A publisher access failure is recorded as incomplete inspection, not evidence that data do not exist.

### S1 — Tunable mechanical internal resonance: method candidate

[Ramini, Hajjaj and Younis (2016), Tunable Resonators for Nonlinear Modal Interactions](https://www.nature.com/articles/srep34717), DOI 10.1038/srep34717; [archived article](https://pmc.ncbi.nlm.nih.gov/articles/PMC5048135/).

The primary article describes electrothermal tuning and electrostatic actuation of arch resonators, including a 2:1 regime and spectra at the drive and half-drive frequencies (Figs. 5–6). This supports a platform/protocol lead, not a supplied phase-resolved kernel package. Numerical row access, same-state full transfer/error bounds and UET variable mapping were not established in this screen. Tuning temperature/bias changes the state and cannot be pooled as a fixed-coefficient frequency scan without review.

Disposition: **candidate for operator/protocol review**, not accepted data. Primary indexed article text/figure descriptions were available; direct publisher navigation failed. The archived result exposed supplement descriptions, not verified raw records or a raw-data license.

### S2 — Two-mode Hamiltonian: comparator source, not experimental dataset

[Theoretical insights into 1:2 and 1:3 internal resonance for frequency stabilization in nonlinear micromechanical resonators](https://link.springer.com/article/10.1007/s11071-025-10987-7), DOI 10.1007/s11071-025-10987-7.

Section 2, Eqs. (1)–(5), presents a simplified two-mode model with interaction Hc=alpha*u1^n*u2, n=2 or 3, and damping. This gives a concrete comparator for checking interaction order, but not a specimen-specific parameter derivation. Its Data availability section states that no datasets were generated or analysed. It cannot supply validation rows. The n=2 coupling is a structural analogy only; damping, forcing, coordinate normalization and omitted terms prevent automatic identification with the current UET lane.

Disposition: **ordinary-material/theoretical comparator**, not experimental calibration or proof of UET correspondence. Full publisher text was inspected, including the explicit simplified-model limitation. The proposed use is qualitative operator review, not importing its frequency-stabilization results.

### S3 — Public numeric archive with wrong resonance order

[Shaw et al., Experimental data, Periodic responses of a structure with 3:1 internal resonance](https://zenodo.org/records/48133), DOI 10.5281/zenodo.48133; associated article DOI 10.1016/j.ymssp.2016.03.008.

The repository lists dataset.zip (364.8 MB) and repository-reported MD5 c01759ff57ac041e8ccf3a4c9487fb30. Metadata establish an accessible archive listing, not locally verified contents, SHA-256, phase coverage, units or reuse permission. The record is explicitly 3:1: it is not the present mediated 2*omega channel. No payload downloaded; license not established from the inspected page.

Disposition: **possible future numerical/competitor-method benchmark only**, not admitted to this kernel test. Do not download the archive merely to produce a fit; a 3:1 extension would require a separate question and operator derivation.

### S4 — Quadratic optical observation: detector control, not mechanical cubic kernel

[Brawley et al. (2016), Nonlinear optomechanical measurement of mechanical motion](https://www.nature.com/articles/ncomms10988), DOI 10.1038/ncomms10988; [author-article bibliographic/abstract record](https://pubmed.ncbi.nlm.nih.gov/26996234/).

The author abstract reports observing displacement-squared thermal motion through nonlinear optomechanical measurement. This is relevant to observer/operator controls, not evidence that an optical harmonic directly measures our cubic mechanical kernel. Full publisher/PMC page retrieval failed during this screen; no raw-data package, actual calibration table or complete methods was admitted.

Disposition: **detector-method reference with incomplete full-method inspection**, not a physical testbed selected on abstract evidence.

## Selection and what changes next

No inspected source is currently an admitted physical UET test package. This is a four-role screen, not a theorem that suitable data are absent everywhere.

The useful new direction is **dual-channel mechanical-model review**, with S1 as a platform lead and S2 as an explicitly ordinary comparator. Observing the auxiliary mode can potentially add an independent constraint that a single response curve lacks; that possibility must be demonstrated, not assumed from having two sensors.

The next research question is:

> Within the existing action's allowed approximation, can independently characterized modal dynamics and cross-channel couplings predict a second channel or a reserved nonlinear response without refitting it?

Required order before a new experiment/data fit:

1. Reuse the existing q/Phi kernel derivation. List which two physical coordinates could map to it and which pieces remain unmatched; do not rename a beam mode Phi by analogy.
2. Compare the candidate full, mass-normalized source/detector equations with the inherited action, including reciprocal couplings, self-nonlinear terms, forcing and damping. A shared monomial or a rotating-wave reduction alone is insufficient. Either derive an omission bound or keep the comparison outside the lossless physical lane.
3. Establish whether independently calibrated cross-channel data remove a specific ambiguity from W1. Include independent channel gains, mode masses/normalization and source transfer; two unknown gains can preserve nonidentifiability.
4. Specify one overidentifying relation and exactly which separate calibration measurements would lock its parameters. Any conservative reciprocity relation must be derived with units and tested against ordinary mechanics as well; it is not automatically UET-specific.
5. Only if these pass, assess exact record availability or design a measurement. No unattended author email, laboratory build, purchase, large archive download or experiment is authorized by this screen.

**Stop:** if all predicted relations coincide with the ordinary comparator after independently justified mapping, report a useful effective-model/measurement benchmark, not confirmation of a new field. To test UET specifically, return to an independently constrained distinguishing prediction; do not add a new term simply to make the models distinguishable.

## Handoff and verification boundary

RESULT: one reusable measurement card and four-role alternative-platform screen completed.
NEW_EVIDENCE: public 3:1 archive distinguished from current 2:1 eligibility; explicit two-mode theoretical comparator identified as non-dataset; tunable mechanical platform and nonlinear observer reference assigned separate roles.
REUSED_EVIDENCE: prior W1–W3 joint identifiability, readout ordering and no-admitted-graphite-package decision; no repeated source search or algebra run.
CONTROLLING_BLOCKER: a new material's action/source/observer correspondence and independent cross-channel calibration are not yet established; accessible data alone cannot supply them.
CLAIM_BOUNDARY: no new numeric calculation, physical acceptance, SI Phi anchor, entropy identity, He-II completion or dependency unlock.
VERIFICATION: primary-source roles and access limits recorded, local document links checked, scoped diff reviewed. No scientific producer changed, so unchanged verifiers were not rerun.
NEXT_ACTION: one bounded dual-channel operator/identifiability review, starting from existing action and an explicit ordinary comparator; source acquisition only after the measured quantity is fixed.
