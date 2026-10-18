# Topic 13 — Observer-aware predictive discrimination

Date: 2026-10-17. Status: research design, not an executed scientific result.
Owner: Topic 13; Core correspondence review required before physical promotion.
Primary area: research-core. No new action term, calibration or physics gate is approved here.

## 1. คำถามและผลที่ต้องส่งมอบ

**คำถามหลัก:** ภายใต้ nonlinear kernel ที่มีอยู่ เมื่อรวมความไม่แน่นอนของตัวกระตุ้นและเครื่องตรวจแล้ว ยังมีปริมาณใดระบุได้ และเงื่อนไขใดใช้ปฏิเสธแบบจำลองสาขานี้ได้?

เป้าหมายไม่ใช่พิสูจน์ UET ทั้งทฤษฎีหรือปิด Full Topic 13 ในรอบเดียว แต่ต้องจบด้วยอย่างใดอย่างหนึ่ง:

1. คำทำนายแบบมีเงื่อนไขที่ล็อกได้ พร้อมปริมาณวัด ขอบเขต หน่วย และเกณฑ์ปฏิเสธ;
2. บทสรุปเชิงโครงสร้างว่าชุดการวัดที่ประกาศแยกสิ่งที่สนใจไม่ได้ พร้อม counterexample;
3. ข้อกำหนดการวัดหรือ calibration อิสระขั้นต่ำที่แก้ ambiguity ที่ระบุได้จริง;
4. ข้อสรุปว่าตัวเลือกนี้แยก UET จาก comparator ที่ระบุไม่ได้ จึงไม่ควรใช้ยืนยันกลไกเฉพาะ UET.

ข้อ 1 อาจเป็นเพียง FORMAL/SYNTHETIC ไม่ใช่ physical prediction หาก material/source/readout matching ยังขาด ต้องรายงานขอบเขตนี้ตรง ๆ.

## 2. หลักฐานตั้งต้นและ lineage

Current design checkout: branch `codex/research/observable-discrimination-design`, based on `93a12313a`.
Owner evidence: commit `0f17012ffd6ad456c150b10e048efd868ce95588`, LOCAL_ONLY; do not merge or copy its implementation silently.

- Existing [formal contract](calculation_contracts/nonlinear_formal.json) pins the October 15 invariant-pole note and artifact.
- Existing [physical contract](calculation_contracts/nonlinear_physical.json) records the missing physical kernel/source/readout package.
- Existing [gain audit](../../core/07_artifacts/topic13/t13_actuation_readout_identifiability_audit.json): `D Phi=b U`, `DeltaT=alpha Phi`, hence `H=alpha*b/D`; reciprocal gain changes leave this transfer invariant. Do not repeat that proof as new progress.
- Owner path `Result/artifacts/T13_TWOMODE_SOURCE_VISIBILITY.md`: two eigenmodes need not produce two measured peaks; physical material-state/source matching remains open.
- Owner path `Result/T13_INVARIANT_POLE_DISCRIMINATION_2026-10-15.md`: reuse the inverse/rank/sign/curvature results, not new copies of their fixtures.
- [Adoption review](../../meta/CALCULATION_COMPLETENESS_REVIEW.md) distinguishes methodological coverage from scientific closure.

At execution start verify these pinned objects and check for newer owner evidence. Inspect the delta only. Missing lineage is an execution prerequisite, not a physical no-go. Do not substitute the older September checkout narrative for October owner results.

## 3. แบบจำลองและสิ่งที่ห้ามสับสน

Inherited conditional kernel, not a new UET equation:

```text
F(x; L,B,p) = L - B/(p-x)
p>0, B>=0; x off the pole; existing real/lossless tree-level branch
```

The owner note distinguishes natural-unit x=nu^2 from the conditional mechanical coordinate x=(2*omega)^2. Do not interchange drive frequency and mediated-channel frequency, Hz and rad/s, or natural and SI units. L,p,B are field-chart invariants, not independently predicted material constants.

Start with the following CONDITIONAL instrument model only after checking the existing readout derivation supports it for the chosen protocol:

```text
y_j = g_j F(x_j; theta) + c_j + e_j, theta=(L,B,p)
```

Here y is the declared measured response, g the combined admissible source/readout transfer, c an additive background, e a bounded residual. This is not a universal input-output law: a nonlinear detector, mode mixing, finite-band convolution or a different measured quantity requires an explicitly derived replacement. Unknown g/c must not be assumed constant to obtain identifiability.

Analyze separately: independently calibrated transfer; unknown constant gain/background; independently bounded frequency-dependent transfer. An unconstrained frequency-by-frequency transfer is a negative control, not a legitimate method to rescue a fit. Separate field-coordinate freedom, instrument ambiguity, physical parameter uncertainty and numerical conditioning.

Observer means relevant physical instrument state (gain, clock/frame, orientation, thermal response, integration/memory where applicable), not consciousness. Additional source backaction requires an actual coupling/exchange law or an omission bound. Dissipation history is not the complete observable state. Universal entropy organization is a separate unestablished hypothesis, not an assumption of this project.

## 4. สาม wave ที่มีจุดตัดสิน

### W1 — Joint identifiability, before more data or simulation

- Read existing actuation, readout, invariant and source-visibility results; list only unresolved joint questions.
- Freeze one protocol, observable, domain, instrument family and nuisance parameters before calculation. Maintain the existing formal/physical contracts; update their identities for any genuinely new producer.
- Determine equivalence transformations and identifiable combinations for the joint model. Use a constructive inverse or exact degeneracy witness; Jacobian rank is only local and must not be represented as a global uniqueness proof.
- Check zero coupling, near-pole exclusion, unresolved curvature, gain/background ambiguity and frequency calibration. Distinguish structural degeneracy from poor finite-noise precision.
- Deliver one short decision table: recoverable quantity, assumptions, ambiguity, minimum extra independent observable/calibration. Reuse known inverses instead of deriving them again.

Exit: identify at least one genuinely unresolved ambiguity and resolve it conditionally, or document that the candidate adds nothing beyond prior work. If all questions are already answered, skip W1 calculations and move directly to the missing physical prerequisite.

### W2 — Discriminating measurement design, only for surviving quantities

- Compare the inherited pole family with an affine/null response and an ordinary material pole with the same admissible response. The last comparator tests mechanism equivalence: shared input-output behavior cannot establish a uniquely UET cause.
- Optimize measurement locations/channels to separate predeclared candidate prediction sets under admissible nuisance/error bounds; do not optimize target-data agreement. State which common nuisance values span frequencies/channels; do not let each row refit them independently.
- If independent parameter bounds exist, use a bounded design search and report worst-case separation. Otherwise produce a parameter-conditional design or a proof that uniform separation is unavailable; do not manufacture favorable ranges.
- Predeclare the search grid/refinement, pole guard, error norm and computational cap before running. Synthetic examples verify the method only. Include a deliberately indistinguishable pair and a distinguishable control.
- For a bounded-error test, reject only when the measured uncertainty set and the full admissible candidate prediction set do not intersect under the frozen rule. Overlap is inconclusive. A sampled failure to find overlap is not a certified global exclusion; use validated bounds or label the conclusion numerical/conditional.
- Set numerical tolerance from the declared error budget and check convergence. No invented covariance, significance level, SI calibration or physical precision.

Exit: one measurement specification with needed frequency/channel coverage, independent calibration, uncertainty limits and conditional rejection rule; or a demonstrated observational equivalence/no-uniform-design result for the declared family.

### W3 — Physical feasibility and one locked test, conditional on admission

- Check only existing source packages against W2's exact quantity/state/drive/readout/unit/error requirements. Do not restart the parked nine-route source search without a new eligible lead.
- If no package qualifies, finish with an actionable missing-input card: measured quantity, material/state, protocol, independent calibration, processing, error/correlation needs, owner and reopening trigger. Missing covariance may allow justified conservative bounds, not presumed independence.
- If a package qualifies, record calibration/validation ancestry and previous exposure. Do not call previously exposed rows blind holdout. Freeze the contract, parameters/nuisance treatment and rejection rule before scoring reserved observations.
- Run at most the single scoped comparison authorized by that admission decision. Exploratory use remains diagnostic; changing the model after scoring requires a new version and new validation, not a relabeled pass.

Exit: scoped rejection, consistency without unique confirmation, inconclusive measurement, or an exact external prerequisite. Full Topic 13 and Core claims still depend on their existing gates.

## 5. ฮีเลียมเป็นสายรอง ไม่ใช่ช่องทางหนีบล็อก

He-4's current missing prerequisite is a named admissible stationary condensed finite-T UET state and longitudinal observable/current/stiffness mapping. The frozen normal branch is not repaired by a better thermometer model. Do not fit an arbitrary source vector to manufacture second sound.

Reuse conditional mode-visibility results for design only. A mode-identified phase-speed claim may need less amplitude calibration than a full waveform/detectability claim; evaluate the actual output rather than demanding every instrument detail indiscriminately. Only resume a physical He-4 comparison after the same-state model/operator prerequisite changes. Do not expand simultaneously to Topics 10/23 or new entropy theory during W1-W2.

## 6. Evidence, compute and stop policy

- One active wave at a time in this chat; parallel read-only checks may be used only where dependencies are independent. Do not create extra chats or worktrees automatically.
- This design is not itself a running Goal. Start long execution only when the user enables/resumes it. No unattended automation is created by this document.
- Before every run state the new input/method and the decision it can change. Reuse unchanged prior results. After two no-new-evidence attempts on one route, stop that route and reassess instead of increasing cell count.
- Set a finite job count, sample count and timeout per numerical job before execution. Never increase these automatically after an inconclusive result. Check disk space before writing; a full disk is an execution block, not scientific evidence.
- Save one compact generated result per wave with contract/input/config/code identities, convergence/error summary and failure witness. No per-cell JSON, large embedded history, repeated raw copies or unbounded sweeps.
- A formal claim needs a proof; numerical rank/examples alone do not establish it. A physical claim needs admitted material/input-output correspondence and existing science gates in addition to the completeness standard.
- Update the existing topic UPDATE_LOG and daily WORK_LEDGER only for actual completed work; scoped commit per coherent verified unit. No force push, direct-main bypass, private/raw publication, email, external contact, model-term invention or threshold relaxation.

Handoff: RESULT; NEW_EVIDENCE; REUSED_EVIDENCE; OBSERVABLE_AND_UNITS; VERIFICATION; CONTROLLING_BLOCKER; CLAIM_BOUNDARY; NEXT_ACTION. Report whether the closure is formal, synthetic, physical or a feasibility decision.

## 7. คำสั่งเริ่มงานในห้องนี้

> ทำตาม RESEARCH_DESIGN_OBSERVABLE_DISCRIMINATION_2026-10-17.md เริ่ม W1 ตรวจ lineage และ reuse ผลเดิมก่อน ศึกษา joint source–instrument identifiability เฉพาะส่วนที่ยังไม่ตอบ แล้วเดิน W2/W3 เมื่อ prerequisite ผ่าน เป้าหมายคือคำทำนายที่หักล้างได้ หรือข้อพิสูจน์/ข้อกำหนดการวัดที่อธิบายชัดว่าทำไมยังทดสอบไม่ได้ ไม่เพิ่มขอบเขตหรือรันซ้ำเพื่อให้ดูมีงาน ไม่เลื่อน claim อัตโนมัติ หยุดเมื่อถึงผลตัดสินที่กำหนดหรือจำเป็นต้องมี input/อำนาจเพิ่มเติม รายงานสิ่งใหม่ที่ได้และบล็อกถัดไปอย่างสั้น

## Design verification

Planning-only change. Existing evidence read, not regenerated. No data scored, no holdout accessed, no independent physical result produced, no science gate changed. The plan builds on the shared completeness standard; it does not replace it or the older funding plan outside this specific measurement-discrimination workstream.

## 8. Sequencing-standard pilot: history-dependent response versus derived record

Date: 2026-10-18. Baseline: `b307897a4`, canonical worktree
`C:/Users/santa/Desktop/uet_harness`, branch `codex/research/source-backaction-discrimination`.
Class: evidence-reuse/design audit, not a new calculation, physical test or W1-W3 restart.
Uses [standard 32](../For%20Work/32_Theory_Development_and_Research_Sequencing_Standard.md).

### Bounded work card

- **Question / intended claim:** Does the existing architecture already distinguish history
  that changes future response from a record computed after dynamics? This is a bounded
  reconstruction of the project's memory idea, not an assertion that the author defines
  all information as memory, entropy or a new field.
- **Stage and scope:** TD0-TD3 review of the named existing implementations only.
- **Already have:** the state/record distinction in the
  [main ontology](../../core/01_contracts/UET_MAIN_THEORY_AXIOMS_SPEC.md);
  [open-system implementation](../../core/02_equations/covariant/uet_covariant_open_system.py);
  its [formula audit](../../core/07_artifacts/correspondence/covariant_open_system_formula_audit.json)
  and [saved control](../../core/07_artifacts/verification/covariant_open_system_verification.json);
  [trace implementation](../../core/02_equations/matter_space/uet_trace.py);
  [trace/no-backreaction controls](../../core/07_artifacts/verification/matter_space_variational_verification.json);
  and the [existing comparator result](Result/T13_ACTION_DISCRIMINATION_2026-10-18.md).
- **Missing/disputed:** author acceptance of this narrower proposition as a sufficient
  expression of the intended information concept; physical origin and independent matching
  of memory coefficients; a justified restriction distinguishing it from ordinary memory models.
- **Controlling dependencies:** the formula audit's `open_items` and
  `claim_ceiling`, the open-system result's `research_status` and
  `coefficient_provenance.evidence_status`, and the existing calculation contract
  [CORE_MATTER_SPACE_OBSERVER_V1](../../core/00_governance/calculation_contracts/matter_space_observer.json).
  The latter covers the matter/trace distinction, NOT certification of the open-system path.
  Existing Topic13 physical/comparator controllers are unchanged.
- **One action and why:** compare actual function inputs and update order to saved
  results and the previously proved comparator boundary. This decides whether another
  demonstration or additional state is needed before any new theory design.
- **Outcomes / acceptance:** distinguish an implemented mechanism, an output-only record,
  or a missing mechanism; report constitutive assumptions separately from physical support.
  Completion is evidence-backed classification and an exact next decision, not a new PASS.
- **Stop / reopen:** stop this audit once the roles and remaining decision are explicit.
  Reopen calculations only for a changed hypothesis/input/implementation or demonstrably
  stale evidence. Do not restart the closed observer-discrimination round.
- **Reviewer question:** author: is physical history-dependent response the intended
  proposition, a narrower example, or insufficient? Subsequently, a statistical-mechanics
  reviewer should assess one chosen microscopic/state/transport correspondence.
- **Non-goals:** no new equation/term, universal information-mass identification, physical
  coefficient, material substitution, old-source hunt, scientific gate edit or status promotion.

### Findings and disposition

| Stage | Existing evidence and decision | Remaining gap |
| --- | --- | --- |
| TD0 | Existing ontology already separates physical memory from generated and observed records. This is not a newly discovered definition of the author's entire theory. | Author's intended breadth/identity of information remains unconfirmed. |
| TD1 | `open_system_evolution` accepts `force_history`; `_memory_convolution` computes the retarded input; `rate=-memory_force+source` advances the state before trace production. The full model includes history, not just its present state array. | Exponential kernel and coefficients are declared constitutive inputs, not uniquely forced by the broad concept. |
| TD2 | Saved open-system control reports internal support/normalization/KMS/positivity checks; its coefficient source is `internal://wave4-preregistered-control`, evidence `SIMULATION_ONLY`. Matter-space saved checks separately report trace-switch invariance and trace-history no-backreaction. | No fresh verifier run, universal well-posedness proof, microscopic derivation or measured coefficient is supplied here. |
| TD3 | Existing action-discrimination section D already constructs ordinary linear-filter/damped-oscillator comparators for these controls. | History dependence alone is not a uniquely UET prediction or proof of a new substance. |
| TD4-TD6 | Not executed by this pilot; original He-4, graphite and parent gates retain separate scope. | Physical realization, testing and transfer require their own existing prerequisites. |

**Decision:** the weak mathematical proposition is already represented: some named
models use history in their dynamics, while their generated trace is an output.
The trace-only path by itself does not establish feedback. No new field or duplicated
memory demonstration is needed to establish that implementation distinction.

This does NOT show that every information variable is a memory force, that the same
present reduced coordinates determine a closed Markov state, or that microscopic physics
has acquired new laws. It also does not establish a universal entropy/energy conversion.
The earlier action/comparator result remains in force.

**Next decision:** confirm whether the intended theory requires (a) this constitutive
history-dependent response as a scoped application, (b) a derivation/physical restriction
on the existing memory law, or (c) a genuinely different mathematical role for information.
Option (b) needs a specific source/microscopic hypothesis, not another constant sweep;
option (c) first needs a bounded proposition and state/observable definition. These are
alternatives for author review, not three automatically active research lanes.

**Verification:** direct source/formula/artifact/test-definition inspection and local
link/whitespace review only. Existing results reused, not regenerated or newly certified.
This completes one methodological pilot; physical research and theory closure are unchanged.

### Origin and closure follow-up: what the open-system control actually establishes

Reviewed 2026-10-18 at `407702088`; source, producer and saved artifacts are unchanged.
This is a TD1-TD3 source/code audit, not a new calculation or a physical falsification.

| Item | Authoritative source behavior | Consequence |
| --- | --- | --- |
| Exponential law | Formula ID `UET-OPEN-EXP-MEMORY-001` is explicitly a causal constitutive ansatz; the registry lists exponential memory as an assumption. | The broad history/response idea does not derive this kernel in the cited work. The function name `derive_retarded_kernel` evaluates the declared law; it does not establish its microscopic origin. |
| Coefficients and relaxation | Producer `_config` fixes L, tau and T as a simulation-only control with an internal source identity. | Positivity/normalization checks do not independently select material values or a unique memory law. |
| State-to-force closure | `open_system_evolution` accepts `force_history` independently of `physical_state`. `state_metric` is validated/stored but is not read in the evolution or force construction. | This helper advances a state under prescribed history; it does not by itself derive a thermodynamic force from a state functional or define a closed autonomous system. This is a scope limitation, not a demonstrated bug in its declared control role. |
| Noise consistency | `derive_noise_kernel` constructs covariance and its expected KMS expression using the same formula; the producer tests that residual. | The saved residual checks internal construction consistency, not independent microscopic derivation, measurement or simulation of a stochastic bath. |
| Entropy ledger | Nonnegative memory production is assigned through the PSD quadratic form; storage rate is the difference from force-memory power. | This bookkeeping does not alone prove a state-entropy identity for the prescribed trajectory or thermodynamic completeness of arbitrary force histories. |

Implementation locators: `OpenSystemConfig.__post_init__`, `derive_noise_kernel`,
`entropy_current_divergence`, and `open_system_evolution` in the linked module.
Producer: [audit_uet_covariant_open_system.py](../../scripts/audit/audit_uet_covariant_open_system.py),
especially `_config` and `build_artifacts`. Existing
[test definitions](../../core/05_tests/regression/root/test_uet_covariant_open_system.py)
were inspected, not rerun; their named checks do not establish the missing state-to-force map.
No saved PASS, numerical value or threshold is rewritten.

**Narrowed next dependency:** if the intended claim is a self-contained mathematical
theory of system response, first declare one state/force/free-energy correspondence and
its units, admissible histories and boundary/initial data. Then inspect whether the
existing memory ledger follows from that correspondence. Do not jump directly from
kernel positivity to a claim about nature, request a material dataset to repair this
mathematical gap, or silently set force equal to metric times state.

The matter-space lane already defines functional derivatives, but this audit does not
identify its C/Phi variables with the abstract open-system vector. Composing those
lanes would require an explicit justified interface and is NOT authorized by similarity
of terminology. For a prescribed-input application rather than an autonomous theory,
state-to-force closure is not required; the claim must retain that application scope.

**Decision:** keep this control as reusable constitutive mathematics. A stronger
foundational claim needs the missing state/force and microscopic/constitutive assumptions
made explicit, with the author's intended scope confirmed before implementation.
No new equation or full-theory impossibility conclusion follows.

### Existing state-to-force closure found: keep the lanes separate

Reviewed 2026-10-18 at `701030dfc`. This narrows the preceding finding: a missing
state-to-force map in the prescribed-input open-system HELPER is not evidence that
the entire repository lacks a closed state-to-rate construction.

The [matter-space specification](../../core/01_contracts/MATTER_SPACE_RESEARCH_SPEC.md),
sections 2-5, already declares the chain implemented by
`matter_space_free_energy`, `matter_space_chemical_potentials` and `matter_space_rhs`:

- State: C, Phi, Pi; configured coefficients, spatial operators, boundaries and sources.
- Generator: the declared normalized Omega[C,Phi], including the chosen quartics,
  gradient penalties and `-g*C^2*Phi/2` interaction.
- Forces: mu_C and mu_Phi are the generator's functional derivatives.
- Evolution: C follows its selected conserved/nonconserved rule; Phi_t=Pi and
  tau*Pi_t=-Pi-M_Phi*mu_Phi+J_Phi.
- Ledger: the extended energy includes Pi storage; declared source powers and
  nonnegative dissipation are accounted for. This is not an SI entropy derivation.
- Record: optional retarded trace is computed afterward; it is not the memory state.

Given the declared full discretized state and configuration, the RHS is explicit;
there is no arbitrary force_history input required by this implementation.
This observation is not a global existence/uniqueness theorem, an accepted continuum
causality proof or identification of these coordinates with a physical material.

Reuse the saved matter-space controls: variational derivatives, source-ledger closure,
trace-switch invariance and history separation. Their parent causal/SI/physical
limitations remain in force. No new numerical test, kernel substitution or coupling
between this lane and the open-system helper is necessary for this finding.


The term-origin review for this existing lane yields:

| Choice | Existing justification | What is NOT fixed by it |
| --- | --- | --- |
| Quadratic/quartic local potentials | Declared polynomial constitutive model; positive quartics control large amplitudes. | Unique coefficients, physical energy units or universal state meaning. |
| Gradient penalties | Declared spatial variation cost and discrete variational consistency. | A derivation of physical space, inertia or universal information storage. |
| C-squared/Phi coupling | Common generator fixes the paired C and Phi derivative factors/signs. | Why this interaction rather than another admissible one, or a measured g. |
| Conserved versus nonconserved C | Explicit alternative configuration choices. | Universal mass conservation for an unspecified relational C. |
| Pi relaxation and mobilities | Selected dissipative/inertial effective law with a declared ledger. | Microscopic bath reduction, physical relaxation time or unique optimization law. |

Thus the existing mathematics supplies conditional consistency constraints after choices
are made, but it does not make those constitutive choices unique consequences of the
author's broad principles. Further coefficient sweeps would not resolve that logical gap.
**Updated next dependency:** the TD1 construction and term-origin audit now exist in this
named lane. Reconcile whether the intended proposition supplies an additional constraint beyond an
ordinary coupled phase-field model. The specification explicitly calls the coupling
a constitutive choice, not a first-principles spacetime derivation. The existing TD3
ordinary-comparator result applies in its stated scope. Do not demand new experimental
data to establish the already-implemented algebra, and do not claim the author has
approved this ansatz as the unique realization of the foundational information idea.

## 9. Standards adoption W3: proposition and provenance reconciliation

Date: 2026-10-19; reviewed checkout `4b38514da`, same canonical worktree/branch
as section 8. Scope: one existing history-dependent-system proposition, not a
reconstruction of every historical UET idea. No new equation, run or data access.

**Bounded proposition:** a declared system may retain state/history that affects
its next response through specified couplings; a derived observation record need
not itself be an independently evolving source. Boundaries and receiver/source
roles are relative to the question and relationship, not permanent species.

| Origin / evidence | What is accepted for this review | What is NOT established |
| --- | --- | --- |
| Direct author clarification in this chat, 2026-10-19, paragraph beginning with the clarification about not inferring stronger impact from proximity | Study boundaries/categories and interacting subsystems must precede fixed source/detector labels; the same object may be treated at different system levels | No distance-strength law, new numerical coupling, universal entropy identity or approval of a particular action |
| Earlier AI translation / current graph schema | Distinct source, response and receiver nodes can be useful modeling choices | One exclusive role per node is an implementation restriction, not the author's ontological claim; repair in adoption W4 |
| Existing matter-space spec sections 1-5 and functions cited in section 8 | C/Phi/Pi are selected normalized states, the generator and dissipative laws define a specific implementation; R is postprocessing | This ansatz is not uniquely derived from the author's system idea; "ordered reference" and "space response" are lane definitions, not measured universal identifications |
| Imported/modeling mathematics exposed by the existing comparator, action-discrimination section D | Ordinary coupled order-parameter dynamics with the same generator, mobility, discretization and readout reproduce this named normalized lane | Shared mathematics does not establish a new UET-specific law, nor invalidate the utility of the model |
| Consequences conditional on the selected laws | Paired variational forces, configured state-to-rate closure and separated trace role already have scoped evidence in section 8 | No universal information-mass/entropy conversion, independent SI scale or empirical confirmation follows |

Identity boundary: the current tracked specification blob is
`cfc4a32ec9289d5e66c5119871db12ba4d15d659`, implementation blob
`1e1085a1af30a30d27339310e572dd843ed623c1`, and action-discrimination report blob
`fa8b751f43ff8e0b460757d5032c5dd6b0bce852`; those three working files are unchanged
at review. These are Git object identities, not contract SHA-256 values. Cross-tree
He4 results are not incorporated by this review.

**Decision:** the author's latest clarification settles the intended role/boundary
method, not the uniqueness or physical meaning of the ansatz. It is sufficient to
repair the graph representation next; do not require the author to invent another
equation before that methodological repair. Additional UET-specific restrictions
remain unconfirmed and cannot be invented to evade the comparator. The existing
implementation may remain an explicitly provisional normalized model in the meantime.

Verification: direct current source/specification/comparator and dirty-state review;
no re-derivation of the closed comparator, numeric sweep, new artifact or gate change.
Next: W4 compatibility-tested relational roles, then W5 Core scope/comparator pilot.

## 10. Standards adoption W5: Core pilot decision

Date: 2026-10-19, baseline `ced764b9b`. The existing
[matter-space contract](../../core/00_governance/calculation_contracts/matter_space_observer.json)
is actually migrated to RELATIONAL representation, not merely scheduled for review.
The old contract is pinned as Git evidence; no scientific artifact is rewritten.

| Chain | Evidence reused / decision |
| --- | --- |
| Proposition and state | Section 9's history/response proposition is a model-design idea; C/Phi/Pi are chosen normalized coordinates, not a universal information/entropy identity |
| Generator and evolution | Existing specification sections 2-4 and free_energy/chemical_potentials/RHS functions close the selected normalized chain; term choices remain constitutive |
| Nested accounting | C_system owns C; response owns Phi/Pi; source_system is their aggregate, with no independent state and no extra energy added to Omega plus Pi storage |
| Measurement | D remains a candidate receiver with UNKNOWN physical realization and backaction; a category or external location supplies no omission bound |
| Comparator | Existing action-discrimination section D constructs the same ordinary phase-field dynamics and readout in this named scope; boundary/role bookkeeping adds no distinguishing force law |
| Disposition | Retain the normalized model and existing conditional consequences; do not claim physical validation, unique UET mechanism or entropy production in SI |

Verification: current specification/implementation text equals the committed source
after LF normalization; contract identities and pinned baseline are checked by the
validator. Regression tests cover initializer agreement and preserved INCOMPLETE
detector status. No unchanged algebra, numeric sweep or scientific producer was rerun.
The independent foundation audit remains FAIL/BLOCKED (224 errors, including stale
pre-migration paths), not overridden by this methodological pilot.

W5 closes the scoped adoption decision, not the physics. Next controller: W6 reconstruct
He4/O2, graphite/TTG and nonlinear routes separately and name which new evidence could
change each decision; do not assume one dataset or new detector model repairs all three.

## 11. Standards adoption W6: separate Topic13 routes and prerequisites

Date: 2026-10-19; baseline `cc03b4ea9`. Review/adoption of existing results only.
The He4 and nonlinear physical contracts now expose a RELATIONAL admission topology;
all missing state/operator/accounting remain UNKNOWN, not manufactured equations.
The candidate state-vector labels in those graphs do not assert a physical number
of degrees of freedom. Formal contracts retain their no-apparatus scope.

| Route / controlling source | Already established in that source's scope | Missing prerequisite and action that could change the decision | Stop / boundary |
| --- | --- | --- | --- |
| He4 selected frozen bundle: he4_observation contract, pinned `0f17012ff` operator-domain decision, `g1_physical_protocol_status` | Scoped operator-domain audit; normal-branch calibration alone does not admit a stationary condensed He-II longitudinal response. Two-fluid visibility algebra separates eigenmode speed from source/readout visibility | Specify one fixed Ward-consistent condensed finite-T completion, independent material charge/stiffness/state map and relevant longitudinal operator. A mode-identified phase-speed comparison may require less amplitude calibration than a waveform/detectability claim | No repeated helium dataset search or same-bundle rank calculation; reopen only on model/operator admission, not better detector prose |
| Graphite thermal/TTG: current full-bridge gate, `status` / `controlling_blocker` | Scoped normalized thermal operators and material comparators are retained; aggregate graphite status BLOCKED_OPEN_T13_FULL_BRIDGE | Independent base-Phi dimensional mapping or eligible independent alpha calibration, with same-state C_src/transport/source-readout uncertainty for the actual claim | Another heat-capacity table or mismatched harmonic sample alone does not close this bridge; no automatic email or source acquisition |
| Graphite coherent-shear preparation: graphite_preparation_prediction FORMAL contract and its 2026-10-18 report | Conditional diffraction-coordinate inverse, closure channel, coupled-state requirement and prefix/suffix rejection design; ordinary comparator remains forward-equivalent | Admit actual simultaneous processed channels with common divisor or raw/reference corrections; bound source tail, temporal convolution and full coupled-state/parameter error set before a suffix forecast | This is not TTG or the prior driven four-frequency kernel. Fitted force is not independent input; prefix calibration is not held-out validation; no new response fit |
| Nonlinear formal invariant: nonlinear_formal contract, pinned pole-discrimination report | Conditional invariant `F(x)=L-B/(p-x)` inverse/finite-error design survives a field-coordinate rescaling; ordinary material poles remain comparators | Reuse algebra; integrate pinned lineage before public promotion. No new absolute Phi number is required just to state the invariant | Mathematical result does not admit a material, independent calibration or physical prediction |
| Nonlinear physical application: nonlinear_physical contract and native-source route report | Exact old invariant is reusable only with its specified source/response protocol; inspected MEMS native forcing differs from a source-free auxiliary channel | Admit same-state mode/source/readout matching in the actual coordinate/time chart, gains/phases, baseline and joint uncertainty. Absolute Phi normalization is required only for claims that actually depend on it | No substitution of extra native forcing, a fitted source or a generic laser/electrode setting into the old kernel; no repeated fixtures or model-term invention |

### Scope and lineage reconciliation

The 2026-09-27 aggregate gate retains `core_result_status =
T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY` and its earlier bounded O2/He4 Core
composition statement. The later frozen-bundle operator decision belongs to a
different owner (`0f17012ffd6ad456c150b10e048efd868ce95588`) and a narrower physical
second-sound question. Neither is silently merged into the other. The old scoped
composition does not establish the later operator; the later missing operator
does not erase every earlier O2 result. Parent physics gates remain unchanged.

Pinned evidence bytes were inspected using their actual Git commit, not a similarly
named working-tree artifact. Contract identity checks retain LOCAL_ONLY lineage
limitations: local availability is not publication or independent replication.
Graphite thermal coverage is referenced to its existing gate, not falsely declared
fully contract-migrated by a coherent-shear FORMAL contract; W7 must retain that gap.

**Decision:** He4's next dependency is model/operator admission; the nonlinear
physical dependency is native source/kernel/readout correspondence; thermal TTG's
is the independent physical bridge; coherent shear has a distinct preparation/data
admission packet. None is fixed by generic observer bookkeeping. Existing negatives
and formal results remain reusable. No data were acquired/scored, no holdout was
read, and no scientific producer, coefficient, threshold or gate was changed.

Next controller: W7 inventory and reasoned route/claim dispositions, while W9's
research-return choice may use these specific prerequisites without waiting for
archival cleanup. W8 astronomy adoption follows the successful methodological pilot,
not an assertion that Topic13 physics has passed.

## 12. Standards adoption W9: finite research-return admission decision

Date: 2026-10-19; checkout `6c259e611`. This freezes and answers a feasibility
question using existing evidence. It is NOT a locked numerical physical forecast,
a new derivation or a repetition of the closed algebra/fixtures.

### Locked question and rules

- **Question:** does the currently declared graphite preparation packet admit a
  prefix-calibrated, prospectively reserved suffix test of the existing coupled
  model now, rather than merely another fitted reproduction of the same trace?
- **Controller:** existing `T13_GRAPHITE_PREPARATION_PREDICTION_V1` contract,
  canonical payload SHA-256 `7a1e0986fef13bdf87c01f00ad64ee7299827f08f874148aeac306f5cb87e69c`.
  Its source/config/evidence identities validate at this checkout. The 2026-10-18
  report is reused, not rerun or silently superseded by this decision record.
- **Model/assumptions:** existing homogeneous collinear conservative matter/response
  candidate and its material/readout hypotheses. No new optical force, damping
  action, regularizing floor or universal Phi/entropy identity is introduced.
  The old static/driven kernel is not substituted for this transient protocol.
- **Comparator:** the explicitly forward-equivalent ordinary scalar model in the
  action-discrimination report. A successful forecast could support this restricted
  effective model, not identify UET uniquely. More precise identical records do
  not remove that comparator equivalence.
- **Parameter/state policy:** freeze model version and all admissible coefficient
  combinations independently or using an explicitly calibration-only prefix.
  Propagate the whole admitted coupled-state/parameter/error set; do not infer
  forces or hidden state anew from suffix targets. No numerical coefficients or
  cutoff time are invented in the absence of an admitted physical packet.
- **Observation/error policy:** use actual jointly identified channels, correction/
  divisor and exposure convention, time-zero, finite temporal memory, residual
  source/heating/damping and state-estimation bounds. Preserve correlation or use
  justified conservative joint bounds. Ratio cancellation does not remove unknown
  convolution, thermal evolution or the hidden response state's initial velocity.
  Absolute Phi amplitude is not required when a justified invariant/material chart
  suffices; the remaining evolution/measurement correspondence is still required.
- **Exposure policy:** prefix is calibration, not independent validation. Previously
  seen published figures are exposed. No suffix is retroactively called blind;
  a future reserved comparison needs recorded exposure and use restrictions.
- **Decision rule:** admit physical scoring only after the model-to-material map,
  complete finite state/parameter/error set, actual record identities and source/
  measurement protocol are supplied. Then reject the fixed model/protocol only
  when its joint prediction set is disjoint from the reserved measurement set;
  overlap is non-rejection, not proof. Missing/unbounded prerequisites mean
  inconclusive feasibility and no physical score, not a theoretical no-go.

### Evidence checked and outcome

The current contract has `uses_observations=false`, empty calibration/comparison
IDs and the unresolved component IDs `residual-source`, `carrier`, `clock`.
The identity check reports zero structural errors but INCOMPLETE. Its prior exact
readout/full-state results remain conditional; those results do not create measured
records or finite physical bounds. The local filename search supplied no new
candidate packet; this is NOT an assertion that none exists online or elsewhere.

**Outcome: physical scoring is not admitted for this declared packet.** This is a
completed finite admission decision with a precise prerequisite, not new empirical
support, rejection of UET, Full Topic13 closure or a license to run more fixtures.

**One reopening prerequisite:** an admitted same-state preparation/observation
packet: simultaneous full first-order channels with common applied-divisor identity
OR raw/reference correction evidence; declared time/exposure and joint error policy;
independently justified model/material/coefficient combinations and a finite coupled
state/source-tail set at a calibration-only cutoff. Check that packet against the
existing contract first. A figure, a fitted global force, a new generic heat-capacity
table or renamed observer category alone is insufficient. No email, external
acquisition, new chat or endless search is authorized by this record.

The normalized Core model and independent bounded formal tasks remain usable in
their own scopes; this feasibility stop does not freeze the whole project. The
standards-adoption goal can close with this explicit W9 prerequisite outcome while
the scientific research questions and triage queue remain open.
