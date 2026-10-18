# Observer-aware predictive discrimination — W1/W2/W3 decision

Evidence class: FORMAL CONDITIONAL / source-feasibility review, not physical validation.
This note supplies the derivations; exact verifier controls supplement, not replace, the proofs.
Owner: Topic13. Plan: [research design](../RESEARCH_DESIGN_OBSERVABLE_DISCRIMINATION_2026-10-17.md).
Contract: [joint observer path](../calculation_contracts/observer_discrimination.json).

## Scope frozen before calculation

One conditional output only: a real off-pole, weak-response, propagator-corrected mechanical cubic kernel. The owner readout is signed, phase-resolved displacement Q3/Q1^3, optionally corrected with Q2 for the specified ordinary cubic competitor. Optical THG intensity is not this quantity. Measured imaginary response, unmodeled damping, nonlinear readout or mixed modes invalidate this particular real scalar model; do not discard them as noise.

No actual source/readout is admitted. The new formal investigation asks what would be inferable IF a properly reconstructed kernel were read through the declared residual transfer. It does not simplify raw diffraction intensity to a scalar gain: the owner temporal and finite-stack forward operators remain prerequisites. No new material parameters are selected.

Reuse evidence at owner commit `0f17012ffd6ad456c150b10e048efd868ce95588`:

- `Result/T13_INVARIANT_POLE_DISCRIMINATION_2026-10-15.md`: exact inverse, output-affine invariance, sign and curvature restrictions;
- `Result/T13_NONLINEAR_READOUT_MAP_2026-10-15.md`: mechanical-harmonic operator, independent drives, cubic-force subtraction and phase/units;
- `Result/T13_TEMPORAL_READOUT_CONTROL_2026-10-15.md`: convolution before intensity inversion, false-harmonic counterexample;
- `Result/T13_FINITE_STACK_READOUT_2026-10-15.md`: higher-order mode profile not determined by linear readout;
- `Result/T13_NONLINEAR_SOURCE_ADMISSION_DECISION_2026-10-15.md` and its source manifest: no admitted nine-route package.

Owner branch head was checked equal to that commit at execution start. This is a local/pinned scope, not a fetch or claim about public main. No owner code was copied or regenerated. The new work assembles the JOINT nuisance decision and bounded-error discrimination rule; it does not claim the older invariance or source-search result as a new discovery.

## W1: recoverable combinations, not all physical constants

Inherited kernel `F(x)=L-B/(p-x)`, p>0, B>=0, evaluated off pole. Let x=a*z, a>0 be a common multiplicative squared-frequency calibration and let y=g*F(a*z)+c. Here a is the square of a multiplicative angular-frequency clock factor; it is NOT an additive frequency offset. A frequency offset produces cross terms and requires a different forward model.

Exact rearrangement for ALL off-pole z gives

```text
y(z) = A - D/(P-z)
A=g*L+c; D=g*B/a; P=p/a.
```

Thus the inherited three-point inverse can recover A,D,P in its nondegenerate exact domain, but not L,B,p,g,c,a separately. This is global nonuniqueness, not just a rank deficiency: for any t>0, replacing (a,p,B) by (t*a,t*p,t*B) preserves A,D,P for all z. For any u>0, replacing g by u*g, B by B/u, and choosing L',c' with u*g*L'+c'=g*L+c preserves the same output. These transformations respect p>0 and B>=0. The exact verifier supplies two distinct parameter witnesses.

| Instrument knowledge | Inferable in nondegenerate noiseless domain | Minimum extra information |
| --- | --- | --- |
| Independent a,g,c | L,B,p via inherited inverse | Material/operator correspondence still needed |
| a known; g,c unknown common constants | p and observed A,D, not L/B separately | Independent g plus c (or equivalent known response) for L/B |
| a unknown; common constant g,c | Instrument-coordinate P=p/a, A,D | Independent clock scale for dimensional p; gain/background for amplitudes |
| g sign unknown | Pole shape may remain; sign(D) is not sign(B) | Independent gain/phase sign convention |
| Arbitrary c_i or unconstrained frequency transfer | No unique pole identification | Restrict transfer with independent calibration, not target fitting |

Last row proof: for any candidate F_i choose c_i=y_i-g_i*F_i. Any proposed p then matches any finite record. This is a deliberately invalid rescue policy, not a claim actual instruments have arbitrary backgrounds. B=0 or g=0 produces a constant curve and leaves p unidentified. Near-zero curvature is a precision problem; a sampled pole is outside the contract, not a point to regularize.

Units: in a conditional SI displacement lane, z,x,P,p have s^-2; a dimensionless; F,L have m^-2 s^-2. If y is in those same calibrated kernel units, g is dimensionless, c,A have m^-2 s^-2 and D has m^-2 s^-4. If y is detector counts, g and c must instead carry the corresponding conversion units; no SI amplitude follows. Synthetic verifier fixtures are abstract rational coordinates, not laboratory constants. Natural-unit coefficients must use the inherited conversion separately.

## W2: an explicit falsification rule and its limits

Use exact declared instrument coordinates z1<z2<z3 with no pole in the sampled domain. Define

```text
T = (y3-y2)/(z3-z2) - (y2-y1)/(z2-z1)
w = (1/(z2-z1), -1/(z2-z1)-1/(z3-z2), 1/(z3-z2))
```

Every affine output y=A+v*z has T=0. For the pole output above, subtraction gives

```text
T = -D*(z3-z1)/[(P-z1)*(P-z2)*(P-z3)].
```

If observations have a justified JOINT enclosure |e_i|<=delta_i, the triangle inequality gives |T_observed-T_true|<=E=sum |w_i|*delta_i. This bound assumes no statistical independence; correlated errors may attain it. Under a common constant-gain/background baseline with deviations bounded by eta_g_i,eta_c_i and |F_i|<=M_i, one permissible allocation is delta_i=eta_g_i*M_i+eta_c_i+eta_e_i. M and all eta must be independently supported; UNKNOWN is not zero.

**Frozen rule:** |T_observed|>E rejects the affine-only response under this admitted operator and these bounds. Otherwise it is inconclusive, not a pole acceptance. Units of T and E are [y]/[z]. A pole prediction set could be rejected only by disjointness under its full nuisance bounds; this three-point contrast is NOT a general pole-rejection or nonlinear-feasibility solver. Three calibration points do not constitute a held-out prediction. Preserve the inherited fourth-point rule when attempting a pole overidentification test.

Coordinates matter: the fixed-weight rule is not valid if uncertain true coordinates are silently substituted. Either calibrate z to the declared accuracy and propagate its remaining uncertainty jointly, or use a justified derivative bound. For y=A-D/(P-z) with independently known |D|<=Dmax and |P-z|>=r>0 along the entire coordinate uncertainty segment, |dy/dz|<=Dmax/r^2 bounds the additional output error by Dmax*eta_z/r^2. No such physical Dmax,r is supplied here. Pure common clock scaling is accounted for by P above, not by fitting one clock value per point.

### Why more computation cannot guarantee separation

For ANY finite design z_i and any positive error epsilon, choose P>max(z_i,0), d=min_i |P-z_i|>0 and D=epsilon*d/2>0. Then all |y_i-A|=D/|P-z_i|<=epsilon/2. This nonzero-coupling finite pole lies within epsilon of a constant affine comparator at every sample. Therefore no strictly positive uniform separation exists over the unrestricted branch with arbitrarily small observable residue. Exact B=0 is not needed for this counterexample. No amount of finite grid refinement repairs the missing physical lower bound.

An ordinary material pole with identical A,D,P produces identical y over the entire model domain, not merely at the sampled frequencies. Instrument optimization cannot distinguish these mechanism labels. A new independent observable or independently constrained microscopic relation is needed to claim a UET-specific cause; compatibility with this curve is not that claim.

### Bounded conditional design control

Because no independent physical parameter bounds are admitted, no physical optimum or SNR is computed. A preregistered SYNTHETIC method check fixes endpoints z=0,2, P=4,D=3,A=5 and delta=1/100. Search midpoints i/n for n=4,8,16: exactly 7+15+31=53 rational candidates, one run, no adaptive extension, pole distance at least 2. Score |T|/E; maximize on each finite grid and report refinement. At midpoint 1, T=-1/4 and E=1/25, so the conditional control is distinguishable. Nested grids cannot reduce the best score. These numbers test the decision procedure only; they are not selected physical tolerances. All arithmetic is exact rational (numerical roundoff zero in these operations); grid maxima are not advertised as continuum/global optima. Tests also include indistinguishable controls, unknown-gain flattening and near-pole sensitivity without clipping.

## W3: feasibility completion, not an endless source search

The pinned manifest's `bounded_search_decision.admitted_discriminator_records` is empty. Existing source roles were checked against the exact same-state mechanical readout requirements, not against the word “nonlinear.” Optical THG/CARS do not directly supply Q3; a different resonator system does not establish the same material correspondence; structural capability alone does not supply original records, mode profile or calibrated nonlinear transfer. W1/W2 do not supply those missing links. The producer records each existing route's disposition, missing fields and immutable source identity without downloading or copying raw data.

The missing-input card in the W3 artifact specifies: same-state Q1/Q2/Q3 or an admitted equivalent kernel; independently identified material/mode and controlled drives; absence/bounds of direct harmonic forcing; independent clock/sign/gain and full readout transfer; correct convolution/inversion order; joint uncertainty and prior-exposure/calibration ancestry. Owner is Topic13 source/readout, with Core review for material correspondence. Reopen only for a new eligible record/operator match or separately authorized acquisition, not another unchanged keyword search or email.

He-4 remains outside this kernel test: its missing condensed stationary UET state/current/longitudinal operator is not solved by this scalar instrument algebra. No Full Topic13/Core unlock follows.

## Reproduce and inspect

Verifier: [Research_T13_Observer_Discrimination.py](../Code/03_Research/Research_T13_Observer_Discrimination.py).
Tests: [test_t13_observer_discrimination.py](../Code/03_Research/test_t13_observer_discrimination.py).
Generated outputs (canonical location only):

- [W1 joint equivalence](../../../core/07_artifacts/topic13/t13_observer_discrimination_w1.json)
- [W2 bounded discrimination](../../../core/07_artifacts/topic13/t13_observer_discrimination_w2.json)
- [W3 feasibility decision](../../../core/07_artifacts/topic13/t13_observer_discrimination_w3.json)

From repository root, using an available Python runtime:

```text
python -B -m unittest discover -s docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research -p test_t13_observer_discrimination.py -v
python -B docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Observer_Discrimination.py --check
python -B docs/scripts/audit/audit_calculation_completeness.py --check
```

Only `--emit` rewrites these three small generated outputs after identity validation. `--check` refuses missing/drifted output without writing. A changed or unavailable pinned source is a visible execution prerequisite, not a scientific result. Physical acceptance remains blocked; this is the research plan's scoped formal/feasibility stopping point, not a declaration that UET is right, wrong or untestable everywhere.

## 2026-10-18 continuation completion audit — whole approved research round

This audit uses the original design's stated alternatives and stop conditions, not a new goal defined around the latest passing test. The design calls for conditional identifiability/discrimination, a scoped equivalence or minimum-input result, and a physical-feasibility decision; it explicitly does NOT require Full Topic13/Core validation. No physical test is substituted for a missing material/operator map.

The owner worktree's current tracked HEAD remains `0f17012ffd6ad456c150b10e048efd868ce95588`. A read-only status/diff check found no newer tracked nonlinear evidence. One untracked local input directory was excluded: its contents and eligibility were not inspected, imported or promoted as a new measurement packet. This is a local lineage audit, not a remote-main freshness claim or an assertion that every owner's private input is empty.

| Original requirement or continued question | Authoritative evidence checked | Decision and limit |
| --- | --- | --- |
| W1 joint inverse, degeneracy and units | Sections W1 above; current W1 artifact and pinned owner readout/invariant sources | A,D,P are conditionally inferable; physical L,B,p and source/detector charts are not separately identified. Zero residue and unbounded transfer cases explicit |
| W2 comparators and useful rejection rule | W2 proof/artifact, bounded 53-candidate method control | Affine-null rejection rule with a joint error enclosure; ordinary identical-pole mechanism remains indistinguishable. No universal positive separation for the unrestricted residue family |
| W3 exact measured quantity and physical eligibility | W3 artifact, nine pinned source dispositions, complete missing-input card | No admitted same-state signed mechanical kernel/source/error package; no physical kernel test run. Reopen only for a new eligible record/operator match, not another unchanged search |
| Observer/source extensions and two-channel ambiguity | [dual-channel result](T13_DUAL_CHANNEL_IDENTIFIABILITY_2026-10-17.md), existing contract/artifact and exact tests | Independent control can resolve the declared passive ambiguity; uncalibrated two channels do not establish a material identity |
| Native mechanical source admission | [physical-route decision](T13_PHYSICAL_ROUTE_ADMISSION_2026-10-18.md), hashed source coefficients and verifier | Native MIMO source/inertia retained; useful comparator, not an admitted UET material/source map |
| Could a fuller existing action provide unique predictions? | [action-class proof](T13_ACTION_DISCRIMINATION_2026-10-18.md), matching artifact and current implementation controls | Explicit canonical comparator and allowed zero-response member limit uniqueness in the stated action class. No theorem about every UET sector or every open/quantum extension |
| Source feedback, phase and absolute scale prerequisites | [source-feedback proof](T13_SOURCE_FEEDBACK_PROTOCOL_2026-10-18.md), stable four-state certificate and conditional inverse/shared-scale controls | Apparent cubic need not be intrinsic mechanics. Some necessary-condition tests need neither unique phase nor separate absolute flux, but still require admitted transfer/state/error conditions |
| One actual processed experimental source, not another fixture | [actual-readout diagnostic](T13_READOUT_ADMISSION_2026-10-18.md), verified small CSV/manifest and generated diagnostic | Real low-power candidate profiled without clipping; central ideal pointwise inverse and constant-gain-only repair not admitted. Optimistic error enclosure is not a noise estimate or UET rejection |
| Completeness, provenance and claim boundary | Current contract identities and changed-path audit, source hashes/CRC, logs and scoped commits | Methodological coverage verified for these paths; no physical acceptance, independent SI Phi anchor, blind-holdout reset or foundation promotion |

Completion verification: 100 tests across the six relevant existing modules passed. All six current producer `--check` commands reproduced their saved artifacts, including W1/W2/W3, without acquisition or source mutation. The shared completeness audit reports zero errors across 13 contracts; repository-wide legacy/unreviewed coverage is not claimed complete. Foundation errors and its BLOCKED parent gate remain separate from this research-round outcome. Final proof-note identity and generated metadata are refreshed after this audit section, not by rerunning owner physics or rewriting old measured results.

**Research-round outcome:** conditional discrimination and structural/feasibility conclusions delivered, including a real-data readout stress check. These satisfy the approved finite W1-W3 outcomes and their continued source/comparator questions. They do not establish physical UET correctness, incorrectness or Full Topic13 completion. More identical simulations cannot identify parameters or mechanism labels absent from the forward map.

**Next research decision, not an automatic extension:** for the original kernel, supply an independently justified same-state material/source/operator correspondence plus permitted phase-resolved harmonic records and joint errors. For a uniquely UET claim, a justified physical constraint outside the demonstrated comparator freedom is additionally required. A native cavity-noise study is a separate apparatus objective and must not silently replace this one. Keep the current research round closed unless one of these prerequisites changes or a genuinely different scoped research objective is selected; do not restart it merely to prolong execution.
