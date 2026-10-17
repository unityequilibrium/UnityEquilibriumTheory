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
