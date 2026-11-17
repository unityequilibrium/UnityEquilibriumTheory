# Topic 0.23 update log

## 2026-11-15 — Test-admission review, no scientific rerun
- Reviewed all 13 test-named candidate modules in this Topic; source-bound roles, evidence symbols, reasons and reopening prerequisites are in `topics/test_suite_config.json`.
- Findings include numerical candidates whose outcomes are not enforced, document/report producers, simulated submission/peer review, synthetic laboratory labels and literal proof-status dictionaries. None are accepted as an independent physical result or automatic regression by these labels.
- All 13 remain visible as NOT_ADMITTED; source changes, disappearance or relabeling invalidate the review and withhold Topic execution. Original code and artifacts are preserved.
- The real outside-repository `--topic 0.23` call ran no candidate, reported its coverage gap and returned 2; this is not a Topic pass or a decision against UET principles.
- Remaining: satisfy the per-source execution/result/provenance prerequisites before selecting a bounded adapter; do not run generators merely to produce a positive status.

## 2026-11-17 — Rebuilt as the UET falsification register
- The author designated this Topic for testing what breaks UET. New entry point: `FALSIFICATION_REGISTER.md` (kill condition, test status and null comparison for every claim of the current parent action and engine).
- The legacy kappa/beta falsification uses assumed scalings and always exits PASS; it stays preserved as LEGACY_UNREVIEWED. README keeps its content with a notice on top.
- New numbers: the standard-physics null passes all 13 L2 claims; portal alpha <= 5.1e-12 for lambda >= 7e6 m; no registered bound between 3.9e-5 m and 1e5 m.

## 2026-11-17 — Stress test 01: cross-scale layer 3
- Question: can N = b tau with tau = F/P fail outside physics where the field's own theory does not fail? Note: `Doc/STRESS_01_LAYER3_CROSS_SCALE.md`.
- Finding: not in its current form. N = b tau is Little's law (identity at steady state); tau = F/P is each field's standard energetics; layer 3 carries no shared constant to transfer across fields.
- New number: pygmy-possum starvation data reproduce 307/189/124 vs 310/195/127 days, but only because P was inferred from mass loss (identity, not a test).
- Next: author chooses a pre-declared scope (exhaustion vs hazard lifetime shape) or a theory step (shared constant, or route B layer-2 term).

## 2026-11-17 — Stress test 02: pre-declared scope for layer 3
- Question: which pre-declared scope lets tau = F/P fail where the field's own theory does not? Note: `Doc/STRESS_02_LAYER3_SCOPE.md`.
- Correction to STRESS_01 item 4.3: with income, reserve is a random walk and lifetime is a first-passage time (Levinthal 1991); firm lifetimes cannot separate UET from the null.
- Finding: only the cross-species lifespan scope (rate-of-living: lifetime energy per gram constant) is UET-distinct; biology already rejects it, so the expected outcome is FAILED (disclosed prior knowledge).
- Draft T018 written in the note (AnAge, fit log LEP = a + s log M + d bird; fail if CI of |s| > 0.10 or d > 0.30); not registered, no data downloaded.
- Next: author decides whether UET claims individual lifespan as reserve-limited.

## 2026-11-17 — T018: cross-species lifespan scope of layer 3
- Question: is lifetime energy per gram (metabolic rate / mass x max longevity) the same across birds and mammals, as the author-declared lifespan scope requires?
- Result: FAILED. AnAge Build 15 (128 birds, 170 mammals): bird offset d = 0.392 (95% 0.330-0.455, fail line 0.30), birds 2.47 times mammals; mass slope s = -0.114.
- First UET-distinct failure: current biology does not claim rate-of-living, so the null does not fail. Removes only the individual-lifespan scope; tau = F/P for closed reserves and N = b tau stand.
- Caveat: no phylogenetic correction (intervals too narrow). Next: record in the register; pick the next candidate breaker.

## 2026-11-17 — Yukawa gap, globular-cluster data, route B
- Yukawa gap: registered Smith et al. 2000 (Rot-Wash, baryon charge) and drafted T019 for 1 cm - 1e5 m (estimate alpha <= 6.5e-6 at lambda >= 1 m); awaits author approval, not run.
- T002/T014: no independent new HB/RGB count set exists (Zoccali 2000 overlaps T002's WFPC2 base; Sandquist 2000 has known Y = 0.20 systematics); no card drafted.
- Route B (`Doc/STRESS_03_ROUTE_B_DISSIPATION_COUPLING.md`): if dissipation sources psi, one shared constant tau_beta (a time) sets an extra force proportional to power per mass; LLR estimate tau_beta < 9e15 s; tau_beta = 1/H0 would exceed LLR by thousands.
- Next: author approves T019; decides whether to adopt the route-B term and a minimum tau_beta.

## 2026-11-17 — T019 run: portal bound in the 1 cm - 1e5 m gap
- Author approved T019 before the run (commit 321d5e7ad); outcome PASS (constraint; g_c = 0 admissible).
- alpha_max = 0.50 at 1 cm, 2.5e-5 at 10 cm, 6.6e-6 at 1 m, 6.4e-6 from 2 m to 1e5 m; g_c_max = 1.30e-12 eV there. Signal Delta a is 0.36 sigma from zero.
- Not UET-distinct. Result record waits for the author's L2 decision.

## 2026-11-17 — T020 drafted: LLR bound on route B
- Question: how large can the shared route-B time constant tau_beta be, given lunar laser ranging?
- Registered LLR equivalence-principle values (Biskupek et al. 2021 primary, Williams et al. 2012 sensitivity); route-B claim at L0; T020 DRAFT (constraint).
- Drafting estimate: tau_beta <= 4.6e15 s (about 1.5e8 yr); tau_beta = 1/H0 would exceed the allowed Delta about 1e4 times. Not run.

## 2026-11-17 — T020 run: LLR bound on route B
- Author approved T020 before the run (commit 75ef4b0df); outcome PASS (constraint; tau_beta = 0 admissible).
- tau_beta <= 4.61e15 s (1.46e8 yr); 1.02e16 s with Williams 2012; 5.2e15 s with the worst-case mass-portal cross term.
- Benchmark tau_beta = 1/H0 (AI choice, not deciding) predicts Delta = -6.8e-10, about 9,900 times the allowed value. Result record waits for the author's L2 decision.

## 2026-11-17 — Stress test 04: does the proposition force a route-B minimum?
- Question: do the author's items 7-8 force a minimum coupling for route B? Note: `Doc/STRESS_04_ROUTE_B_MINIMUM.md`.
- Correction: the T020 model (psi sourced by the current rate P) is not a persistent record, so item 7 does not force tau_beta > 0.
- New numbers: if a fraction g of written bits must be carried by a massless one-dof psi, the Sun must emit P_psi >= 1.26 g^(4/3) L_sun; g = 1 needs 126 percent of L_sun (excluded by solar energy-loss limits of about 3-10 percent, recalled, not yet checked), so g <~ 0.06-0.15.
- A thermal psi background T_psi would forbid dissipation below T_psi; nanokelvin experiments force T_psi < ~1 nK.
