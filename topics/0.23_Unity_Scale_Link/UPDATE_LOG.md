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

## 2026-11-17 — Author reading of item 7
- The author answered, tentatively, that "written onto space" means things that already exist (light, heat, spacetime curvature), reasoning from massless photons: a body reaches light speed only by turning all its mass into light.
- Consequence: item 7 needs no new field; route B stays a constraint (T020), not a UET-only breaker. Recorded in core/AUTHOR_PROPOSITION.md open issues.

## 2026-11-17 — Stress test 05: information budget and black holes
- Question: how many bits can a body write by burning, and what does the rule give for a black hole? Note: `Doc/STRESS_05_INFORMATION_BUDGET.md`.
- New numbers: human lifetime ~1e32 bits; Sun main sequence 2.9e63 bits (0.068 percent of Mc^2); same mass evaporating as a black hole 1.5e77 bits, about 1e10 times more.
- Applied to Hawking evaporation the rule gives exactly S_BH/(k ln 2) (radiation entropy 4/3 S_BH, as Zurek 1982), an identity of black-hole thermodynamics, not a UET-only test.
- Future topic: whether information leaves a black hole (Page curve); not measurable now.

## 2026-11-17 — Stress test 06: which known thing could psi be?
- Question: is psi something physics already knows (antimatter, neutrinos, Higgs, vacuum energy, a fluid)? Note: `Doc/STRESS_06_WHAT_IS_PSI.md`.
- Antimatter cannot be psi (spin 1/2, charged, nearly absent today; ALPHA-g: antihydrogen falls at 0.75 +- 0.21 g, recalled). UET's complex chi makes antimatter couple to psi like matter.
- Neutrinos are fermions but a psi-neutrino lane would escape the nucleon bounds (T005/T016/T019); the Higgs fits mathematically (xi h^2 R) but its 1.6e-18 m range removes late-time effects; a single scalar cannot be a vortical fluid (topic 0.10 no-go).
- No known field matches all properties; next: author decision on a neutrino lane.

## 2026-11-17 — Stress test 07: psi and the quantum vacuum
- Question: must psi match the quantum statement that empty space is not empty, and what does that force on psi? Note: `Doc/STRESS_07_PSI_AND_QUANTUM_VACUUM.md`.
- The quantum vacuum (fluctuations, Higgs and QCD condensates, vacuum energy) is well evidenced and made of known fields; psi fits as one more field but is not required by it.
- New number: matter loops through the portal lift the psi mass by ~g_c/(4 pi); the EMG branch (m_eff ~2.8e-28 eV) stays natural only if g_c <~1.1e-27 eV, about 1e15 below the T019 limit.
- Muon g-2 shift from the portal ~1e-46 (irrelevant); vacuum-energy mismatch 1e31-1e120 remains unsolved by UET.

## 2026-11-17 — Stress test 08: four candidates where UET could differ
- Question: do species survival, history-dependent Casimir, readable records and black-hole information offer UET-distinct tests? Note: `Doc/STRESS_08_FOUR_DISTINCT_CANDIDATES.md`.
- Species survival: fossil molluscs show higher metabolic rate goes with extinction (Strotz et al. 2018; Rojas-Ariza et al. 2026: survival odds -11 percent per mW, bivalves only); direction matches layer 3 but known and not UET-distinct; best next Test Card with new data and a predicted slope.
- Readable records: CMB readable fraction ~1e-82 of its entropy; black-hole area law confirmed by GW250114 (equals "stored bits never decrease"); Casimir history dependence lacks a UET equation and conflicts with the author's no-feedback reading.

## 2026-11-17 — Stress test 09: species-survival test design
- Question: which species should persist longer under layer 3, and what do fossil data already show? Note: `Doc/STRESS_09_SPECIES_SURVIVAL_DESIGN.md`.
- Known results disagree on P: high whole-animal metabolism goes with extinction in molluscs and mammals, but small marine genera go extinct more often across the Phanerozoic (Monarrez, Heim and Payne 2023), where geographic range is the strongest predictor.
- No single choice of P fits all three; range-as-F is a post-hoc reading. Proposed a pre-declared composite F/P test; waits for the author's choice of P and F.

## 2026-11-17 — Author fixes P for species survival
- The author chose P = whole-animal resource use (not per kilogram). Recorded in core/AUTHOR_PROPOSITION.md.
- Monarrez, Heim and Payne 2023 already fitted size and range jointly: smaller genera go extinct more often (significant in bivalves and gastropods), opposite to layer 3 if size stands for P; Neogene bivalve BMR (Rojas-Ariza et al. 2026) agrees with layer 3.
- Body size is a poor proxy for P; a test needs BMR from size and temperature, declared before seeing new data.

## 2026-11-17 — Stress test 10: is psi needed
- Question: does the author's picture (space forces behaviour, matter collects into black holes, shared behaviour around them) need psi? Note: `Doc/STRESS_10_IS_PSI_NEEDED.md`.
- Finding: no. Every element maps to GR + Lambda + thermodynamics; with psi = 0 all passed cards stand and only the EMG Hubble-tension mechanism is lost.
- New numbers: accretion turns 6-42% of rest mass into light versus about 0.7% for fusion; black holes hold most cosmic entropy (~1e104 k, recalled, unverified).
- Next: author chooses psi in the core (drop) or as an optional extension; a black-hole persistence test needs a declared meaning of survival first.

## 2026-11-20 — Stress test 11: is the readable fraction r of energy-written bits constant?
- Question: the reversed-Landauer rule (bits = Q/(kT ln 2)) is the second law; UET would be distinct only if the readable fraction r of those bits followed a law. Note: `Doc/STRESS_11_READABLE_FRACTION.md`.
- Finding: r spans more than 75 orders of magnitude: E. coli genome copy 7e-6 to 6e-5 (5.7e9 to 5e10 ATP per division), memory 7e-10 to 1e-8 (0.3 to 3.97 pJ/bit), CMB ~3e-82; r also depends on the reader.
- Consequence: trace feedback cannot take w = r E/(kT ln 2) with a universal r; w must come from each system's mechanism.
- Open (L0): selected recorders (genomes, memory) have far higher r than incidental records; "selection for persistence raises r" is a testable hypothesis.

## 2026-11-27 — Stress test 12: parameter scaling returns in the parent action
- Question: does the parent action escape the legacy problem that kappa had to change with scale? Note: `Doc/STRESS_12_PARAMETER_SCALING_RETURNS.md`.
- Finding: no running is needed, but the action fixes no value: 5 dimensionful parameters leave 4 unpredicted ratios to the Planck mass, lane choice plays the role of the per-domain kappa table, and data push the couplings toward zero.
- New numbers: the dark-energy lane needs m_psi = 4.3e-33 eV = 1.8e-60 reduced Planck masses; at the T041 best point Lambda_eff is 97.8% of dark energy and xi_c psi0^2 = 7.2e-5.
- Literature: scale symmetry broken spontaneously (Higgs-dilaton, arXiv:1107.2163, ties n_s to w0) is the closest mechanism; also asymptotic safety, cosmological natural selection, trackers. The author decides which to pursue.

## 2026-11-27 — Wave S1: option A of STRESS_12 (scale symmetry)
- The author chose option A. Core wave S1 (`core/03_lanes/scalar_tensor/uet_scale_symmetry.py`, claim C_S1_SCALE_INVARIANT_RESTRICTION at L1).
- Finding: scale symmetry alone fixes the dimensionful parameters (7 become 3 plus one scale) but forbids the portal, all masses and the thawing dark energy, and moves the vacuum-energy hierarchy into lambda/xi^2 = 2.9e-120.
- Next: restoring exchange and masses needs Higgs-dilaton terms (quartic portal, xi_chi |chi|^2 R); that is a Theory Card v2 decision for the author.

## 2026-11-27 — Wave D1: option D of STRESS_12 (attractors)
- Core wave D1 (`core/03_lanes/scalar_tensor/uet_attractor.py`, claim C_D1_ATTRACTOR_INITIAL_CONDITIONS at L1).
- Finding: the card's potential has no tracker (1 + w0 = 0.256 psi_i^2); the S1 restriction broken by the mass term gives the cosmon exponential, which removes psi_i but not the vacuum-energy tuning, and Cassini makes it look like Lambda.

## 2026-11-27 — Wave C1: option C of STRESS_12 (persistence selection)
- Core wave C1 (`core/03_lanes/scalar_tensor/uet_selection_of_scale.py`, claim C_C1_PERSISTENCE_SELECTS_STATES_NOT_COUPLINGS at L1).
- Finding: inside one universe selection picks states, not couplings; the S1 scale is a flat direction (neutral); with the mass breaking G drifts at <= 2.3e-5 H. Fixing couplings this way needs them as fields (action change) or many universes.

## 2026-11-27 — Wave B1: option B of STRESS_12 (RG fixed point)
- Core wave B1 (`core/03_lanes/scalar_tensor/uet_rg_closure.py`, claim C_B1_RG_FIXES_ONLY_DIMENSIONLESS at L1).
- Finding: a fixed point can fix only dimensionless couplings, so it cannot touch the 1.8e-60 hierarchy; S1 and a fixed point are complementary. The card is not closed under one-loop renormalization: a xi_chi |chi|^2 R term is generated.
