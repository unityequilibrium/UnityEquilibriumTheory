# Limitations

- The root baseline comparison is present, but numeric acceptance boundaries are still provisional until a saved artifact is generated and reviewed.
- Current data posture is "real source referenced", which is below a fully normalized archival dataset package.
- The topic still needs a clearer split between exploratory test files and the single canonical verification workflow.
- The current primary verifier tests only the beta critical exponent against a topic-local 3D Ising/liquid-gas working copy.
- Gamma, nu, scaling relations, morphology metrics, and material critical-point datasets are not yet gated.
- The spectral Cahn-Hilliard solver is normalized; its grid units and parameters are not yet mapped to a specific material system.
- Internal script execution does not by itself establish external replication, formal proof, or broad physical closure.
- Topic-level source-evidence and branch-claim gates now make that boundary explicit: accepted evidence stops at the selected beta benchmark and normalized mechanism lane, not universal phase-transition closure.
- The artifact-level `phase_transition_claim_scope_gate` is the export controller: a passing
  beta gate remains topic-level `WARN` until source archives, full exponent/scaling checks,
  material critical-point gates, and renormalization-group closure are available.
- Wave 4 synthetic scaling showed the historical UET terms stayed near mean-field behavior, not the 3D Ising exponent.
- Wave 5 adds an opt-in `spatial_coupled_v1` core candidate, but the current dynamics verifier remains `WARN`: engine alignment and spatial-operator gates pass, while `universality_shift_gate` is `BLOCKED`.
- The current spatial-coupled candidate estimates beta near mean-field (`0.5081`), so it must stay a diagnostic heuristic bridge until a revised operator or derivation changes the gate result.
- Wave 6 coefficient sensitivity found beta only in the `0.4729` to `0.5243` range across the tested coefficient grid; coefficient-only tuning is not evidence for escaping mean-field behavior.
- Wave 7 correlation-length diagnostics found only weak correlation growth (`xi_near/xi_far ~= 1.07`, `nu_proxy ~= 0.03`), so the current synthetic window/estimator is not adequate for RG or universality-class claims.
- Wave 8 finite-size diagnostics found `finite_size_coverage_gate == PASS` and `binder_crossing_gate == PASS`, but `correlation_window_gate == BLOCKED` and `operator_separation_gate == BLOCKED`; the current grid/window still cannot support universality-class claims.
- Wave 9 critical-window relaxation found that closer-to-Tc temperatures and longer runs still keep spatial `xi/L` below `0.074`, with no baseline separation; runtime/window extension alone is not a supported repair path.
- Wave 10 operator-form requirement aggregation keeps `operator_form_requirement_gate == BLOCKED`; the next candidate needs a nonlocal, conserved, or scale-dependent operator form plus fresh unit/formula/scaling gates before any dynamics claim can be upgraded.
- Wave 11 adds a first `spatial_coupled_v2` core candidate with screened nonlocal memory and conserved interface/game drive, but the diagnostic still keeps dynamics claims blocked: v2 `max_xi/L` is `0.0733`, below baseline `0.0798`, and lane separation is negative.
- Wave 12 component ablation found that v2 info-only, game-only, full, short-memory, and long-memory profiles all remain below baseline `xi/L`; the current v2 component family should be treated as correlation-neutral or damping under this synthetic window.
- Wave 13 Model C diagnostics pass mechanism gates for conserved-order dynamics, but the result is normalized 2D mechanism evidence only; it still needs opt-in core integration plus finite-size/exponent gates before any dynamics or universality claim is upgraded.
- Wave 14 integrates `conserved_order_v1` as an opt-in core candidate, but the explicit core finite-difference path does not yet reproduce the Wave 13 mechanism response; core conserved median `xi` growth is `0.87`, below the legacy core comparison `1.47`.
- Wave 15 identifies the next blocker as numerical/operator-form stiffness, not coefficient strength: applying the Wave 13 spectral settings to an explicit core path implies a stiffness proxy of `32685`, about `335544x` the Wave 14 explicit candidate setting, so a spectral or semi-implicit conserved-order core path is required before claim upgrades.
- Wave 16 adds `conserved_order_spectral_v1` and passes the core spectral bridge under normalized 2D Wave 13-like settings, but it remains diagnostic-only: finite-size scaling, exponent fits, material calibration, and RG closure are still open.
- Wave 17 runs that next finite-size/exponent check and keeps claims blocked: max near-critical `xi/L` is `0.145`, below the `0.20` correlation-window threshold, and median beta is `1.77`, far from the 3D Ising reference.
- Wave 18 finds that relaxation/window-only changes still do not repair the `xi/L` blocker, while high-kappa cases that pass `xi/L` erase the order signal below the declared floor; this is a smoothing tradeoff, not universality evidence.
- Wave 19 finds one spinodal-window case that preserves order while passing `xi/L`, but the target seed replicate pass fraction is only `0.25`; the candidate window remains diagnostic until seed-margin and finite-size replication gates pass.
- Wave 20 repairs the single-grid seed-margin blocker for the `T=0.900`, `kappa=0.100`, `4000`-step window, but it is still a normalized `L=16` result; finite-size replication, exponent fits, material calibration, and RG closure remain blocked.
- Wave 21 tests that same window across `L=8,12,16` and two seed sets; `L=16` fresh seeds are not robust (`1/3` pass, min `xi/L = 0.1944`), so finite-size replication remains blocked.
- Wave 22 shows that longer `L=16` relaxation alone does not repair the fresh-seed `xi/L` margin: `4000`, `4800`, and `5600` step groups each pass only `1/3` seeds, even while order amplitude increases.
- Wave 23 shows that the `L=16` fresh-seed `xi/L` blocker is sensitive to the axis-autocorrelation crossing threshold: the default `e^-1` gate reproduces Wave 22 at `3/9` passes, while lower thresholds pass `9/9`; this is an estimator-design blocker, not evidence for accepting a new threshold or upgrading universality claims.
- Wave 24 shows that a threshold-free structure-factor RMS length proxy detects long-wavelength structure in all `L=16` fresh-seed cases, but the proxy is near the single-grid domain scale (`xi/L` max `0.5799`), so it requires multi-grid calibration before it can support finite-size or exponent gates.
- Wave 25 confirms that this domain-scale issue is not fixed by multi-grid replication: structure-factor margin passes `18/18` cases, but median `xi/L` remains near domain scale (`0.997` at `L=8`, `0.717` at `L=12`, `0.566` at `L=16`), so exponent and universality gates remain blocked.
- Wave 26 shows partial larger-grid relief at `L=20` (`6/6` cases pass, median `xi/L = 0.4347`), but this does not accept the estimator: the derived acceptance-rule gate remains blocked by the prior `L=8` domain-scale value and missing structure-factor/axis-estimator reconciliation.
- Wave 27 defines a topic-derived structure-factor acceptance preflight, but the current artifact chain fails it: `L=8` is excluded as domain-scale, `L20/L16` absolute `xi` is `0.9599`, and the structure-factor/axis-lower estimator ratio remains `2.6261`.
- Wave 28 narrows estimator disagreement: the structure-factor/axis-lower ratio is stable across L16 and L20 (`~2.66`), but that factor is not source-backed or derived and both estimators show declining absolute length from L16 to L20.
- Wave 29 scans the local reference package and finds no text-source support for structure-factor, second-moment correlation length, Fourier estimator definition, or finite-size admissibility; external source candidates remain unaccepted until packaged.
- Wave 30 packages three primary estimator-source candidates in a manifest, but formula extraction, local full-text support, and calibration acceptance remain blocked.
- Wave 31 extracts the source-family second-moment estimator boundary, but the current RMS inverse-k proxy is not source-matched and remains diagnostic-only for claim use.
- Wave 32 implements the literal lowest-mode second-moment candidate, but all current L16/L20 snapshot cases are invalid for that formula because raw `S(0)` is not larger than `S(k_min)`; no surrogate `S(0)` is accepted.
- Wave 33 tests ensemble and spatial-variance `S(0)` lanes, but the source-closer ensemble lane remains invalid under the conserved-mean constraint and the spatial-variance proxy remains diagnostic-only.
- Wave 34 defines estimator-policy requirements, but no source-backed conserved-order susceptibility or finite-k/canonical estimator policy is accepted yet.
- Wave 35 packages source candidates for fixed-composition/canonical and finite-k policy review, but candidate metadata is not formula extraction and no estimator policy is accepted.
- Wave 36 extracts source boundaries only at abstract/policy level; no conserved-order S0, finite-k estimator, calibration factor, or normalization mapping is accepted.
- Wave 37 shows rendered/abstract access is insufficient for accepted formulas; local TeX/PDF math extraction is still required before estimator policy or exponent gates.
- Wave 38 localizes arXiv source archives only in a temporary cache; raw sources are not repo-archived and no TeX formulas are accepted yet.

- Wave 43 preserves 19 TeX formula fragments in a manifest, but the rerun reports `source_archive_availability_gate == BLOCKED` and `source_formula_fragment_gate == WARN`; `accepted_estimator_policy_gate`, `uet_normalization_mapping_gate`, and `next_path_gate` remain `BLOCKED`; no exponent, RG, universality, material, or Tier A claim is upgraded.
- Wave 45 restores all three arXiv source archives under the declared repo paths and makes `repo_archive_availability_gate == PASS`; fresh formula extraction now passes from repo archives, but estimator-policy acceptance, UET normalization mapping, and exponent gates remain blocked.
- Wave 46 maps the restored formula fragments to source-policy lanes and identifies the Cahn-Hilliard finite-k structure-factor lane as the strongest candidate family, but no estimator is accepted: UET lattice normalization, finite-size q-window admissibility, and a rerun of finite-size/exponent gates are still blocked.
- Wave 47 makes that normalization blocker explicit: the FFT q-grid convention is declared and passes in lattice units, but centered UET `C` is still a proxy for source concentration fluctuations, source coefficients are unmapped, no accepted finite-k `xi` rule exists, and q-window/domain-scale admissibility remains blocked.
- Wave 48 implements the CH finite-k peak estimator candidate and gets useful diagnostic passes (`implementation_coverage_gate`, `q_window_diagnostic_gate`, `domain_scale_guard_gate`, and `finite_size_trend_gate`), but it is not accepted: `coefficient_policy_gate` and `estimator_acceptance_gate` remain `BLOCKED`, pass fraction is `12/18`, and the finite-k peak hits the low-window edge in `11/18` cases.
- Wave 49 defines the acceptance policy and makes the remaining blocker sharper: strict policy excludes low-window-edge peaks and accepts only `6/18` rows, all at `L20`; `accepted_row_coverage_gate`, `source_dynamics_coefficient_mapping_gate`, `estimator_acceptance_gate`, and `exponent_rerun_gate` remain `BLOCKED`.
- Wave 50 repairs accepted-row coverage only as a probe: the unchanged policy accepts `L20:6`, `L24:2`, and `L28:2` rows, but centered `C` remains proxy-normalized, source CH dynamics coefficients remain unmapped, and estimator acceptance/exponent rerun gates remain `BLOCKED`.
- Wave 51 separates coefficient policy by claim lane: measurement-only finite-k `q_peak` extraction may exclude source dynamics coefficients, but source-equivalent field normalization for centered `C` remains `BLOCKED`; estimator replacement and exponent rerun remain `BLOCKED`.
- Wave 52 narrows the field-normalization blocker: source symbols and centered-`C` proxy use pass for diagnostic `S(q)` measurement, but amplitude/variance normalization and ensemble/time-averaging convention are still `BLOCKED`, so estimator replacement and exponent rerun remain blocked.
- Wave 53 permits amplitude-invariant `q_peak` inspection only as a shape-only diagnostic. Source `S(q)` amplitude, susceptibility normalization, source ensemble/time averaging, estimator replacement, and exponent rerun remain `BLOCKED`.
- Wave 54 keeps current rows diagnostic-only for uncertainty: accepted multi-grid seed aggregation passes, but L24/L28 have only two accepted rows each, no source time-window/ensemble averaging policy is accepted, and no uncertainty interval propagation exists for exponent fits.
- Wave 55 only chooses the next hardening path. It selects replicate/temporal acquisition because no replacement observable policy is accepted, but it creates no new rows, accepts no estimator, reruns no exponent gate, and upgrades no universality, material, RG, or Tier A claim.

## Noether-phase-field dependency boundary

- Core Wave 9 verifies an exact affine map only between an already declared coarse signed O(2) charge density/current and fixed normalized `C/J` coordinates.
- The present Topic 0.11 `C` field is a normalized conserved-order diagnostic; no accepted artifact identifies it as the signed O(2) Noether charge.
- Microscopic O(2) fields and coarse microstates cannot be reconstructed from `C`; both inverse steps are many-to-one by explicit counterexample.
- The symmetric double well is an exact constitutive coordinate map, not an equation of state derived from the covariant O(2) action.
- Covariant coarse graining, susceptibility, mobility, relaxation, gradient-coefficient, entropy-current, and system-specific SI matching remain blocked.
- Matter-space `Phi` and derived trace `R` are excluded from this map and cannot supply hidden feedback or missing physical closure.
- This dependency lane does not alter Wave 55, accept an estimator, rerun an exponent, or support universality, material, RG, GR, global-universe, external-validation, or solved-theory claims.
