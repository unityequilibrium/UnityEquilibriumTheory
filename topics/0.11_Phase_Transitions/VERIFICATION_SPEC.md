# Verification Spec

- Primary command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Critical_Exponents.py`
- Inputs:
  - `Data/03_Research/critical_exponents.json`
- Baseline:
  - 3D Ising / liquid-gas beta exponent values from the topic-local critical-exponent working copy.
- Reported metrics:
  - UET beta projection
  - experimental fluid beta benchmark
  - 3D Ising theoretical beta benchmark
  - relative beta error in percent
  - machine-readable `phase_transition_claim_scope_gate.controller_status`
- Fixed threshold:
  - beta relative error against the experimental fluid benchmark must be <= 5 percent
  - the script must write a machine-readable artifact under `Result/artifacts/`
- Artifact target:
  - Result/artifacts/0_11_phase_transitions_verification.json
  - Data/03_Research/source_evidence_intake_stub.json
  - Data/03_Research/source_evidence_readiness_matrix.json
  - Data/03_Research/branch_claim_gate.json
- Interpretation:
  - Treat output as an internal selected-exponent benchmark only.
  - A pass does not prove the full phase-transition theory, because `gamma`, `nu`, scaling relations, morphology, and material critical-point datasets are not yet primary gates.
  - Topic-level source-evidence and branch-claim gates further limit the topic to selected-benchmark and mechanism-diagnostic usage unless stronger provenance and derivation packages are added.
  - `phase_transition_claim_scope_gate.controller_status == WARN` is expected when the
    selected beta benchmark passes while source archives, full exponent/scaling gates, and
    renormalization-group closure remain open.
## Wave 5 Spatial-Coupling Dynamics Verifier

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Spatial_Coupling_Scaling.py`
- Artifact target:
  - `Result/artifacts/0_11_spatial_coupling_scaling.json`
  - `Result/gl_spatial_coupling_scaling_stats.csv`
- Purpose:
  - Test the opt-in `spatial_coupled_v1` core operator against baseline TDGL and the historical local-additive UET lane.
  - Keep this separate from the selected beta projection in `critical_exponents.json`.
- Required gates:
  - `engine_alignment_gate.status == PASS`
  - `spatial_operator_gate.status == PASS`
  - `universality_shift_gate.status == PASS` before any dynamics-based universality-shift claim is allowed.
- Current Wave 5 result:
  - overall status `WARN`
  - `engine_alignment_gate == PASS`
  - `spatial_operator_gate == PASS`
  - `universality_shift_gate == BLOCKED`
  - beta estimates: baseline `0.4912`, legacy local UET `0.5050`, spatial-coupled candidate `0.5081`
- Interpretation:
  - The candidate fixes the implementation availability of spatial operators in core mode.
  - The current candidate does not move the dynamics away from mean-field behavior.
  - Public or README language must not claim RG closure, universality-class shift, or phase-transition solution from this artifact.

## Wave 6 Spatial-Coupling Coefficient Sensitivity

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Spatial_Coupling_Sensitivity.py`
- Artifact target:
  - `Result/artifacts/0_11_spatial_coupling_sensitivity.json`
  - `Result/gl_spatial_coupling_sensitivity_stats.csv`
- Purpose:
  - Test whether changing only the spatial-coupled candidate coefficients can move the fitted beta exponent toward the 3D Ising benchmark.
  - Keep this as triage for the blocked `universality_shift_gate`, not as a replacement for the full Wave 5 scaling verifier.
- Required gates:
  - `coefficient_sensitivity_gate.status == PASS` before treating coefficient tuning as a plausible repair path.
  - `operator_form_revision_gate.status != BLOCKED` before rerunning stronger dynamics claims without an operator revision.
- Current Wave 6 result:
  - overall status `WARN`
  - `coefficient_sensitivity_gate == BLOCKED`
  - `operator_form_revision_gate == BLOCKED`
  - tested coefficient cases: `20`
  - best beta found: `0.4729`
  - beta range: `0.4729` to `0.5243`
  - near-3D-Ising cases: `0`
- Interpretation:
  - Coefficient-only tuning of the current spatial candidate remains mean-field-like.
  - The next useful repair path is a revised operator form, nonlocal/scale-dependent term, or correlation-length-aware estimator.

## Wave 7 Correlation-Length Estimator Diagnostic

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Correlation_Length_Diagnostics.py`
- Artifact target:
  - `Result/artifacts/0_11_correlation_length_diagnostics.json`
  - `Result/gl_correlation_length_diagnostics_stats.csv`
- Purpose:
  - Test whether the current synthetic temperature window exposes connected correlation-length growth alongside the order-parameter beta fit.
  - Separate beta-only curve fitting from a stronger critical-scaling or universality claim.
- Required gates:
  - `critical_window_gate.status == PASS`
  - `estimator_adequacy_gate.status == PASS`
  - `operator_separation_gate.status == PASS`
- Current Wave 7 result:
  - overall status `WARN`
  - `critical_window_gate == BLOCKED`
  - `estimator_adequacy_gate == BLOCKED`
  - `operator_separation_gate == BLOCKED`
  - spatial beta `0.5081`
  - spatial correlation-length proxy `nu_proxy ~= 0.0324`
  - spatial `xi_near/xi_far ~= 1.0668`
- Interpretation:
  - The current order-parameter beta fit remains mean-field-like and is not paired with critical correlation growth.
  - The next useful repair path is a finite-size/correlation-length-aware scaling design before any stronger universality claim.

## Wave 8 Finite-Size Scaling Readiness Diagnostic

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Finite_Size_Scaling_Diagnostics.py`
- Artifact target:
  - `Result/artifacts/0_11_finite_size_scaling_diagnostics.json`
  - `Result/gl_finite_size_scaling_diagnostics_stats.csv`
- Purpose:
  - Test whether multiple grid sizes show enough near-critical `xi/L`, Binder-style crossing behavior, and spatial-vs-baseline separation to justify a stronger finite-size scaling pass.
- Required gates:
  - `finite_size_coverage_gate.status == PASS`
  - `correlation_window_gate.status == PASS`
  - `binder_crossing_gate.status == PASS`
  - `operator_separation_gate.status == PASS`
- Current Wave 8 result:
  - overall status `WARN`
  - `finite_size_coverage_gate == PASS`
  - `binder_crossing_gate == PASS`
  - `correlation_window_gate == BLOCKED`
  - `operator_separation_gate == BLOCKED`
  - max spatial near-critical `xi/L == 0.0961`
  - max baseline near-critical `xi/L == 0.1045`
  - best Binder-style spread `0.0058`
- Interpretation:
  - The diagnostic has enough grid/temperature coverage to expose the blocker.
  - The current finite-size window keeps correlations too local and does not separate the spatial candidate from baseline.

## Wave 9 Critical-Window Relaxation Diagnostic

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Critical_Window_Relaxation_Diagnostics.py`
- Artifact target:
  - `Result/artifacts/0_11_critical_window_relaxation_diagnostics.json`
  - `Result/gl_critical_window_relaxation_diagnostics_stats.csv`
- Purpose:
  - Test whether moving closer to `Tc` and increasing relaxation steps can lift spatial `xi/L` without changing the operator form.
- Required gates:
  - `critical_window_extension_gate.status == PASS`
  - `relaxation_sensitivity_gate.status == PASS`
  - `operator_separation_gate.status == PASS`
- Current Wave 9 result:
  - overall status `WARN`
  - `critical_window_extension_gate == BLOCKED`
  - `relaxation_sensitivity_gate == BLOCKED`
  - `operator_separation_gate == BLOCKED`
  - max spatial `xi/L == 0.0737`
  - max baseline `xi/L == 0.0797`
  - nearest-T relaxation gain from `700` to `2800` steps: `-0.0024`
- Interpretation:
  - The current small-correlation blocker is not resolved by this closer-to-Tc/longer-run window.
  - The next useful repair path is operator-form or dynamics redesign that creates measurable connected correlation growth.

## Wave 10 Operator-Form Requirement Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Operator_Form_Requirement_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_operator_form_requirement_gate.json`
- Purpose:
  - Aggregate Waves 5-9 into a machine-readable design gate before proposing any `spatial_coupled_v2` operator.
  - Separate allowed design work from unsupported claim promotion.
- Required gates:
  - `prior_artifact_chain_gate.status == PASS`
  - `core_engine_alignment_gate.status == PASS`
  - `coefficient_only_path_gate.status == PASS` or documented replacement by a revised operator path
  - `finite_size_signal_gate.status == PASS`
  - `critical_window_path_gate.status == PASS`
  - `operator_form_requirement_gate.status == PASS` before describing a new operator as claim-bearing.
- Current Wave 10 result:
  - overall status `WARN`
  - `prior_artifact_chain_gate == PASS`
  - `core_engine_alignment_gate == PASS`
  - `coefficient_only_path_gate == BLOCKED`
  - `finite_size_signal_gate == BLOCKED`
  - `critical_window_path_gate == BLOCKED`
  - `operator_form_requirement_gate == BLOCKED`
- Interpretation:
  - The next useful work is operator-form redesign, not coefficient-only tuning or simply longer runs.
  - A future candidate must remain opt-in, use core engine paths, and demonstrate connected-correlation growth plus baseline separation before any dynamics claim is upgraded.

## Wave 11 Spatial-Coupled V2 Diagnostic

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Spatial_Coupled_V2_Diagnostic.py`
- Artifact target:
  - `Result/artifacts/0_11_spatial_coupled_v2_diagnostic.json`
  - `Result/gl_spatial_coupled_v2_diagnostic_stats.csv`
- Purpose:
  - Test the first opt-in `spatial_coupled_v2` core candidate required by Wave 10.
  - Keep candidate availability, safety, stability, correlation response, and operator separation as separate gates.
- Required gates:
  - `v2_core_operator_gate.status == PASS`
  - `v2_spatial_safety_gate.status == PASS`
  - `v2_stability_gate.status == PASS`
  - `v2_correlation_response_gate.status == PASS`
  - `v2_operator_separation_gate.status == PASS`
- Current Wave 11 result:
  - overall status `WARN`
  - `v2_core_operator_gate == PASS`
  - `v2_spatial_safety_gate == PASS`
  - `v2_stability_gate == PASS`
  - `v2_correlation_response_gate == BLOCKED`
  - `v2_operator_separation_gate == BLOCKED`
  - max `xi/L`: baseline `0.0798`, v1 `0.0813`, v2 `0.0733`
  - v2 minus baseline `xi/L`: `-0.0065`
- Interpretation:
  - The first v2 candidate satisfies the code-surface and safety requirements but does not yet create connected-correlation growth or lane separation.
  - The next useful repair path is another operator-form revision or stronger derivation of the nonlocal/conserved dynamics, not claim promotion.

## Wave 12 Spatial-Coupled V2 Component Ablation

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Spatial_Coupled_V2_Component_Ablation.py`
- Artifact target:
  - `Result/artifacts/0_11_spatial_coupled_v2_component_ablation.json`
  - `Result/gl_spatial_coupled_v2_component_ablation_stats.csv`
- Purpose:
  - Separate `spatial_coupled_v2` into information-only, game-only, full, short-memory, and long-memory profiles.
  - Determine whether any existing v2 component is a plausible correlation-growth repair direction before designing another operator form.
- Required gates:
  - `ablation_coverage_gate.status == PASS`
  - `force_lane_activity_gate.status == PASS`
  - `component_improvement_gate.status == PASS` before treating any v2 component profile as a plausible repair path.
  - `memory_length_response_gate.status == PASS` before treating memory-length changes as a plausible repair path.
- Current Wave 12 result:
  - overall status `WARN`
  - `ablation_coverage_gate == PASS`
  - `force_lane_activity_gate == PASS`
  - `component_improvement_gate == BLOCKED`
  - `memory_length_response_gate == BLOCKED`
  - baseline max `xi/L == 0.0801`
  - best profile: `v2_memory_long`, improvement over baseline `-0.0038`
- Interpretation:
  - The tested v2 components are correctly isolated and stable, but none improves correlation length over baseline.
  - The next useful repair path is a different operator structure or derivation, not recombining or length-tuning the current v2 components.

## Wave 13 Model C Conserved-Order Diagnostic

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Model_C_Conserved_Order_Diagnostic.py`
- Artifact target:
  - `Result/artifacts/0_11_model_c_conserved_order_diagnostic.json`
  - `Result/gl_model_c_conserved_order_diagnostic_stats.csv`
- Purpose:
  - Test Model C / Cahn-Hilliard conserved order-parameter dynamics as a different operator family after v2 component ablation blocked the current spatial-coupled terms.
  - Use the topic `Engine_Phase.py` Cahn-Hilliard engine rather than a hidden standalone accepted-equation lane.
- Required gates:
  - `model_c_engine_alignment_gate.status == PASS`
  - `mass_conservation_gate.status == PASS`
  - `domain_growth_gate.status == PASS`
  - `operator_distinction_gate.status == PASS`
  - `claim_boundary_gate.status == WARN` until finite-size/exponent gates and core formula integration exist.
- Current Wave 13 result:
  - overall status `PASS` for mechanism triage
  - `model_c_engine_alignment_gate == PASS`
  - `mass_conservation_gate == PASS`
  - `domain_growth_gate == PASS`
  - `operator_distinction_gate == PASS`
  - `claim_boundary_gate == WARN`
  - Model C max mass drift `~2.1e-16`
  - Model C median `xi` growth ratio `30.49`; baseline comparison `24.68`
  - Model C minus baseline median `xi` growth ratio `5.81`
- Interpretation:
  - Model C is now the strongest mechanism-level repair direction found after v2 ablation.
  - This does not validate a universality-class shift; next work needs opt-in core integration and finite-size/exponent gates.

## Wave 14 Conserved-Order Core Candidate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Core_Candidate.py`
- Artifact target:
  - `Result/artifacts/0_11_conserved_order_core_candidate.json`
  - `Result/gl_conserved_order_core_candidate_stats.csv`
- Purpose:
  - Verify that the Model C repair direction can be exposed through `docs/core/uet_master_equation.py` as opt-in `operator_mode="conserved_order_v1"` without changing legacy defaults.
  - Separate core integration, mass conservation, and mechanism response gates.
- Required gates:
  - `core_conserved_alignment_gate.status == PASS`
  - `legacy_compatibility_gate.status == PASS`
  - `conserved_mass_gate.status == PASS`
  - `core_mechanism_response_gate.status == PASS` before treating the explicit core path as a mechanism repair.
  - `claim_boundary_gate.status == WARN` until finite-size/exponent gates and formula audit closure exist.
- Current Wave 14 result:
  - overall status `WARN`
  - `core_conserved_alignment_gate == PASS`
  - `legacy_compatibility_gate == PASS`
  - `conserved_mass_gate == PASS`
  - `wave13_bridge_gate == PASS`
  - `core_mechanism_response_gate == BLOCKED`
  - `claim_boundary_gate == WARN`
  - core conserved max mass drift `~1.0e-17`; legacy core max mass drift `0.0149`
  - core conserved median `xi` growth ratio `0.87`; legacy core comparison `1.47`
- Interpretation:
  - Core exposure and conservation are now available as an opt-in candidate.
  - The explicit finite-difference core path does not yet reproduce the Wave 13 Cahn-Hilliard mechanism response; the next useful work is mechanism tuning or spectral/semi-implicit core integration, not claim promotion.

## Wave 15 Conserved-Order Numerics-Gap Diagnostic

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Numerics_Gap.py`
- Artifact target:
  - `Result/artifacts/0_11_conserved_order_numerics_gap.json`
- Purpose:
  - Compare Wave 13 spectral Cahn-Hilliard settings and Wave 14 explicit core settings using the dimensionless stiffness proxy `dt * kappa * (pi / dx)^4`.
  - Decide whether the next core repair can be coefficient or mobility tuning, or whether it needs a spectral/semi-implicit conserved-order update.
- Required gates:
  - `artifact_chain_gate.status == PASS`
  - `mechanism_gap_gate.status == PASS`
  - `explicit_core_viability_gate.status == PASS` before treating the explicit core finite-difference path as a viable direct replacement.
  - `spectral_core_requirement_gate.status != BLOCKED` before proceeding with coefficient-only tuning.
- Current Wave 15 result:
  - overall status `WARN`
  - `artifact_chain_gate == PASS`
  - `mechanism_gap_gate == PASS`
  - `explicit_core_viability_gate == BLOCKED`
  - `spectral_core_requirement_gate == BLOCKED`
  - Wave 13 explicit stiffness proxy `32685`
  - Wave 14 explicit stiffness proxy `0.097`
  - Wave 13-to-Wave 14 stiffness ratio `335544`
- Interpretation:
  - The explicit core conserved-order path is not yet a viable direct replacement under Wave 13-like settings.
  - The next supported implementation path is a spectral or semi-implicit conserved-order core candidate, not mobility-only tuning or recombining the current spatial v2 components.

## Wave 16 Conserved-Order Spectral Core Candidate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Core_Candidate.py`
- Artifact target:
  - `Result/artifacts/0_11_conserved_order_spectral_core_candidate.json`
  - `Result/gl_conserved_order_spectral_core_candidate_stats.csv`
- Purpose:
  - Verify that `operator_mode="conserved_order_spectral_v1"` is exposed through `docs/core/uet_master_equation.py` without changing legacy defaults.
  - Compare the opt-in core spectral lane against the existing topic spectral Cahn-Hilliard engine under Wave 13-like settings.
  - Confirm that the Wave 15 explicit-core stiffness blocker is repaired by a stable spectral/semi-implicit core path before rerunning scaling claims.
- Required gates:
  - `core_spectral_alignment_gate.status == PASS`
  - `legacy_compatibility_gate.status == PASS`
  - `spectral_mass_stability_gate.status == PASS`
  - `topic_engine_bridge_gate.status == PASS`
  - `mechanism_response_gate.status == PASS`
  - `wave15_repair_gate.status == PASS`
  - `claim_boundary_gate.status == WARN` until finite-size/exponent gates and formula audit closure exist.
- Current Wave 16 result:
  - overall status `PASS`
  - `core_spectral_alignment_gate == PASS`
  - `legacy_compatibility_gate == PASS`
  - `spectral_mass_stability_gate == PASS`
  - `topic_engine_bridge_gate == PASS`
  - `mechanism_response_gate == PASS`
  - `wave15_repair_gate == PASS`
  - `claim_boundary_gate == WARN`
  - core spectral max mass drift `4.86e-16`
  - max topic-engine field delta `2.89e-12`
  - core spectral median `xi` growth ratio `30.49`
  - explicit `conserved_order_v1` stable case count under Wave 13-like settings `0`
- Interpretation:
  - The core spectral candidate repairs the implementation bridge blocker identified in Wave 15.
  - The next useful work is a finite-size/exponent scaling verifier using the opt-in spectral core candidate; this result is not a universality, material, or RG-closure claim.

## Wave 17 Conserved-Order Spectral Finite-Size Scaling

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Scaling.py`
- Artifact target:
  - `Result/artifacts/0_11_conserved_order_spectral_scaling.json`
  - `Result/gl_conserved_order_spectral_scaling_stats.csv`
- Purpose:
  - Run a normalized 3D finite-size/exponent sweep using the opt-in `conserved_order_spectral_v1` core candidate.
  - Keep implementation stability separate from finite-size correlation-window and universality-exponent claims.
- Required gates:
  - `wave16_bridge_gate.status == PASS`
  - `finite_size_coverage_gate.status == PASS`
  - `spectral_stability_gate.status == PASS`
  - `correlation_window_gate.status == PASS` before treating `xi/L` as adequate for finite-size scaling claims.
  - `universality_exponent_gate.status == PASS` before claiming a 3D Ising-like exponent shift.
  - `claim_boundary_gate.status == WARN` until material and RG closure gates exist.
- Current Wave 17 result:
  - overall status `WARN`
  - `wave16_bridge_gate == PASS`
  - `finite_size_coverage_gate == PASS`
  - `spectral_stability_gate == PASS`
  - `binder_crossing_gate == PASS`
  - `correlation_window_gate == BLOCKED`
  - `universality_exponent_gate == BLOCKED`
  - `claim_boundary_gate == WARN`
  - max near-critical `xi/L` `0.145`
  - beta range `1.61` to `1.83`; median beta `1.77`
  - median beta fit `R^2` `0.912`
- Interpretation:
  - The spectral core candidate remains stable in this normalized 3D sweep, but the finite-size window is still too local for universality claims.
  - The next useful work is a better finite-size/equilibration/scaling-window design, not claim promotion.

## Wave 18 Conserved-Order Spectral Window Repair

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Window_Repair.py`
- Artifact target:
  - `Result/artifacts/0_11_conserved_order_spectral_window_repair.json`
  - `Result/gl_conserved_order_spectral_window_repair_stats.csv`
- Purpose:
  - Test whether longer relaxation or closer-to-Tc windows repair the Wave 17 `xi/L` blocker.
  - Test whether kappa sensitivity can lift `xi/L` while preserving order-parameter signal.
- Required gates:
  - `wave17_chain_gate.status == PASS`
  - `relaxation_window_repair_gate.status == PASS` before treating runtime/window-only changes as sufficient.
  - `kappa_window_sensitivity_gate.status == PASS` only records that kappa can lift `xi/L`; it is not enough without signal preservation.
  - `signal_preservation_gate.status == PASS` before treating a high-`xi/L` case as scaling evidence.
  - `claim_boundary_gate.status == WARN` until full finite-size/exponent, material, and RG gates exist.
- Current Wave 18 result:
  - overall status `WARN`
  - `wave17_chain_gate == PASS`
  - `relaxation_window_repair_gate == BLOCKED`
  - `kappa_window_sensitivity_gate == PASS`
  - `signal_preservation_gate == BLOCKED`
  - `claim_boundary_gate == WARN`
  - max relaxation/window-only `xi/L` `0.113`
  - max kappa-sweep `xi/L` `0.377`
  - best high-`xi/L` order parameter `0.000377`
  - viable high-`xi/L` plus preserved-signal case count `0`
- Interpretation:
  - Relaxation/window-only changes do not repair the finite-size blocker.
  - Kappa can increase `xi/L`, but only by producing a very low-amplitude order signal in this diagnostic; this should be treated as a smoothing tradeoff, not universality evidence.


## Wave 19 Conserved-Order Spectral Spinodal Window

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Spinodal_Window.py`
- Artifact target:
  - `Result/artifacts/0_11_conserved_order_spectral_spinodal_window.json`
  - `Result/gl_conserved_order_spectral_spinodal_window_stats.csv`
- Purpose:
  - Test whether a targeted positive spinodal-margin window can lift `xi/L` while preserving order-parameter signal.
  - Separate a single-grid candidate window from seed-robust finite-size scaling evidence.
- Required gates:
  - `wave18_chain_gate.status == PASS`
  - `spinodal_access_gate.status == PASS`
  - `order_signal_window_gate.status == PASS` before treating the window as a candidate repair.
  - `seed_margin_gate.status == PASS` before treating the candidate window as robust enough for finite-size replication.
  - `finite_size_claim_boundary_gate.status == WARN` until multi-grid scaling, material, and RG gates exist.
- Current Wave 19 result:
  - overall status `WARN`
  - `wave18_chain_gate == PASS`
  - `spinodal_access_gate == PASS`
  - `order_signal_window_gate == PASS`
  - `seed_margin_gate == BLOCKED`
  - `finite_size_claim_boundary_gate == WARN`
  - best viable case: `T = 0.900`, `kappa = 0.100`, `steps = 2400`, `xi/L = 0.204`, order `0.0126`
  - target replicate pass fraction `0.25`, median replicate `xi/L = 0.1965`, minimum replicate `xi/L = 0.1942`
- Interpretation:
  - The Wave 18 low-signal blocker is narrowed: an order-preserving `xi/L` candidate exists in a targeted spinodal window.
  - The window is not seed-robust yet and remains single-grid, so it does not support universality, finite-size scaling, material, or RG-closure claims.


## Wave 20 Conserved-Order Spectral Seed-Margin Repair

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Seed_Margin.py`
- Artifact target:
  - `Result/artifacts/0_11_conserved_order_spectral_seed_margin.json`
  - `Result/gl_conserved_order_spectral_seed_margin_stats.csv`
- Purpose:
  - Test whether the Wave 19 target window becomes seed-robust when relaxation is extended to `4000` steps.
  - Move the blocker from seed-margin robustness to finite-size replication only if all target seeds pass the declared `xi/L` and order thresholds.
- Required gates:
  - `wave19_chain_gate.status == PASS`
  - `seed_group_coverage_gate.status == PASS`
  - `seed_margin_repair_gate.status == PASS` before treating the single-grid seed margin as repaired.
  - `relaxation_margin_gate.status == PASS` before treating the longer target as a real improvement over the 2400-step baseline group.
  - `finite_size_replication_gate.status == PASS` before any finite-size or universality claim is allowed.
- Current Wave 20 result:
  - overall status `WARN`
  - `wave19_chain_gate == PASS`
  - `seed_group_coverage_gate == PASS`
  - `seed_margin_repair_gate == PASS`
  - `relaxation_margin_gate == PASS`
  - `finite_size_replication_gate == BLOCKED`
  - `claim_boundary_gate == WARN`
  - target group `T = 0.900`, `kappa = 0.100`, `steps = 4000`, `L = 16`
  - target pass fraction `1.0`, min `xi/L = 0.2004`, median `xi/L = 0.2059`, min order `0.0505`
- Interpretation:
  - The Wave 19 seed-margin blocker is repaired for the declared single-grid target window.
  - This is still not finite-size scaling evidence; the next controlling blocker is multi-grid replication and then exponent/universality gates.


## Wave 21 Conserved-Order Spectral Finite-Size Replication

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Finite_Size_Replication.py`
- Artifact target:
  - `Result/artifacts/0_11_conserved_order_spectral_finite_size_replication.json`
  - `Result/gl_conserved_order_spectral_finite_size_replication_stats.csv`
- Purpose:
  - Test whether the Wave 20 seed-margin-passing spinodal window replicates across `L=8`, `L=12`, and `L=16` with both the Wave 20 seed set and a fresh seed set.
  - Keep finite-size replication separate from exponent fitting and universality claims.
- Required gates:
  - `wave20_chain_gate.status == PASS`
  - `finite_size_coverage_gate.status == PASS`
  - `grid_replication_gate.status == PASS` before treating the target window as finite-size replicated.
  - `seed_set_generalization_gate.status == PASS` before treating the window as seed-generalized.
  - `exponent_claim_gate.status == PASS` only in a separate exponent/universality verifier.
- Current Wave 21 result:
  - overall status `WARN`
  - `wave20_chain_gate == PASS`
  - `finite_size_coverage_gate == PASS`
  - `grid_replication_gate == BLOCKED`
  - `seed_set_generalization_gate == BLOCKED`
  - `exponent_claim_gate == BLOCKED`
  - `claim_boundary_gate == WARN`
  - `L=8` pass fraction `1.0`, min `xi/L = 0.4499`
  - `L=12` pass fraction `1.0`, min `xi/L = 0.2423`
  - `L=16` pass fraction `0.667`, fresh seed pass fraction `0.333`, min `xi/L = 0.1944`
- Interpretation:
  - The Wave 20 seed-margin result does not yet generalize robustly across grid sizes and fresh seeds.
  - The next useful work is to revise the finite-size/window scaling design or estimator before rerunning exponent or universality gates.


## Wave 22 Conserved-Order Spectral L16 Relaxation Repair

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_L16_Relaxation_Repair.py`
- Artifact target:
  - `Result/artifacts/0_11_conserved_order_spectral_l16_relaxation_repair.json`
  - `Result/gl_conserved_order_spectral_l16_relaxation_repair_stats.csv`
- Purpose:
  - Test whether longer single-grid relaxation repairs the Wave 21 `L=16` fresh-seed `xi/L` blocker.
  - Separate order-amplitude growth from robust correlation-length margin.
- Required gates:
  - `wave21_chain_gate.status == PASS`
  - `l16_case_coverage_gate.status == PASS`
  - `relaxation_repair_gate.status == PASS` before treating longer relaxation as a sufficient repair path.
  - `order_signal_gate.status == PASS` to confirm the failure is not caused by lost order signal.
  - `next_path_gate.status != BLOCKED` before rerunning longer single-grid cases as the default next path.
- Current Wave 22 result:
  - overall status `WARN`
  - `wave21_chain_gate == PASS`
  - `l16_case_coverage_gate == PASS`
  - `relaxation_repair_gate == BLOCKED`
  - `order_signal_gate == PASS`
  - `next_path_gate == BLOCKED`
  - `claim_boundary_gate == WARN`
  - `4000`, `4800`, and `5600` step groups each pass only `1/3` fresh seeds
  - longest group min `xi/L = 0.1950`, median `xi/L = 0.1992`, min order `0.1359`
- Interpretation:
  - Longer relaxation increases order amplitude but does not create a robust `L=16` fresh-seed `xi/L` margin.
  - The next useful work is estimator, finite-size-window, or scaling-design repair before exponent or universality gates are rerun.


## Wave 23 Conserved-Order Spectral L16 Estimator Sensitivity

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_L16_Estimator_Sensitivity.py`
- Artifact target:
  - `Result/artifacts/0_11_conserved_order_spectral_l16_estimator_sensitivity.json`
  - `Result/gl_conserved_order_spectral_l16_estimator_sensitivity_stats.csv`
- Purpose:
  - Test whether the Wave 22 `L=16` fresh-seed `xi/L` blocker is controlled by the current axis-autocorrelation crossing threshold.
  - Keep estimator-threshold sensitivity separate from accepting a new estimator or making dynamics/universality claims.
- Required gates:
  - `wave22_chain_gate.status == PASS`
  - `engine_path_gate.status == PASS`
  - `estimator_case_coverage_gate.status == PASS`
  - `default_estimator_reproduction_gate.status == PASS`
  - `threshold_sensitivity_gate.status == PASS` only records sensitivity; it does not accept a non-default threshold.
  - `next_path_gate.status != BLOCKED` before a non-default threshold can be used for exponent or universality gates.
- Current Wave 23 result:
  - overall status `WARN`
  - `wave22_chain_gate == PASS`
  - `engine_path_gate == PASS`
  - `estimator_case_coverage_gate == PASS`
  - `default_estimator_reproduction_gate == PASS`
  - `threshold_sensitivity_gate == PASS`
  - `next_path_gate == BLOCKED`
  - default `e^-1` threshold reproduces Wave 22: `3/9` passes, min `xi/L = 0.1938`
  - lower threshold `0.30`: `9/9` passes, min `xi/L = 0.2067`
  - lower threshold `0.25`: `9/9` passes, min `xi/L = 0.2161`
  - lower threshold `0.20`: `9/9` passes, min `xi/L = 0.2256`
  - all tested thresholds crossed in all 9 cases; no max-radius saturation was needed
- Interpretation:
  - The `L=16` blocker is now narrower: the field dynamics are stable and order-preserving, but the current `xi/L` gate is estimator-threshold-sensitive.
  - A non-default threshold remains unaccepted until it is derived, calibrated, or replaced by a better source-backed correlation estimator and then rerun through finite-size/exponent gates.


## Wave 24 Conserved-Order Spectral L16 Structure-Factor Estimator

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_L16_Structure_Factor_Estimator.py`
- Artifact target:
  - `Result/artifacts/0_11_conserved_order_spectral_l16_structure_factor_estimator.json`
  - `Result/gl_conserved_order_spectral_l16_structure_factor_estimator_stats.csv`
- Purpose:
  - Add a threshold-free Fourier-domain characteristic-length proxy, `xi_sf = 2*pi / sqrt(<k^2>_S)`, for the same `L=16` fresh-seed fields.
  - Separate long-wavelength structure detection from accepted critical correlation-length or universality claims.
- Required gates:
  - `wave23_chain_gate.status == PASS`
  - `engine_path_gate.status == PASS`
  - `estimator_case_coverage_gate.status == PASS`
  - `default_estimator_reproduction_gate.status == PASS`
  - `structure_factor_margin_gate.status == PASS` only records a candidate threshold-free margin.
  - `domain_scale_guard_gate.status == PASS` before treating the single-grid structure-factor length as unsaturated.
  - `next_path_gate.status != BLOCKED` before exponent or universality gates may use this estimator.
- Current Wave 24 result:
  - overall status `WARN`
  - `wave23_chain_gate == PASS`
  - `engine_path_gate == PASS`
  - `estimator_case_coverage_gate == PASS`
  - `default_estimator_reproduction_gate == PASS`
  - `structure_factor_margin_gate == PASS`
  - `domain_scale_guard_gate == WARN`
  - `estimator_disagreement_gate == WARN`
  - `next_path_gate == BLOCKED`
  - axis default summary: `3/9` passes, min `xi/L = 0.1938`
  - axis lower `0.30` summary: `9/9` passes, min `xi/L = 0.2067`
  - structure-factor RMS summary: `9/9` passes, min `xi/L = 0.5549`, max `xi/L = 0.5799`
- Interpretation:
  - The threshold-free estimator confirms long-wavelength structure in the `L=16` fields, but the length is close to the domain scale on a single grid.
  - The next useful work is multi-grid structure-factor calibration/replication, not universality or exponent promotion.


## Wave 25 Conserved-Order Spectral Structure-Factor Multi-Grid Calibration

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Structure_Factor_Multigrid_Calibration.py`
- Artifact target:
  - `Result/artifacts/0_11_conserved_order_spectral_structure_factor_multigrid_calibration.json`
  - `Result/gl_conserved_order_spectral_structure_factor_multigrid_calibration_stats.csv`
- Purpose:
  - Rerun the Wave 24 structure-factor RMS estimator over `L=8,12,16` and both Wave 20 plus fresh seed sets.
  - Decide whether the threshold-free estimator behaves like a calibratable finite-size diagnostic or a domain-scale proxy.
- Required gates:
  - `wave24_chain_gate.status == PASS`
  - `inbox_chain_gate.status == PASS`
  - `engine_path_gate.status == PASS`
  - `multigrid_coverage_gate.status == PASS`
  - `structure_factor_margin_replication_gate.status == PASS` only records replicated high `xi/L`.
  - `domain_scale_calibration_gate.status == PASS` before exponent or universality gates may use this estimator.
  - `next_path_gate.status != BLOCKED` before claim promotion.
- Current Wave 25 result:
  - overall status `WARN`
  - `wave24_chain_gate == PASS`
  - `inbox_chain_gate == PASS`
  - `engine_path_gate == PASS`
  - `multigrid_coverage_gate == PASS`
  - `structure_factor_margin_replication_gate == PASS`
  - `domain_scale_calibration_gate == BLOCKED`
  - `estimator_disagreement_gate == WARN`
  - `next_path_gate == BLOCKED`
  - structure-factor RMS margin: `18/18` passes, min `xi/L = 0.5549`, max `xi/L = 0.9985`
  - median structure-factor `xi/L` by grid: `L=8 -> 0.9972`, `L=12 -> 0.7166`, `L=16 -> 0.5661`
  - median absolute structure-factor `xi` by grid: `L=8 -> 7.978`, `L=12 -> 8.599`, `L=16 -> 9.057`
- Interpretation:
  - The structure-factor estimator is reproducible, but the multi-grid check shows domain-scale saturation, especially at smaller grids.
  - The next useful work is a larger-grid/source-backed estimator benchmark or a derived acceptance rule, not exponent or universality promotion.


## Wave 26 Conserved-Order Spectral Structure-Factor L20 Probe

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Conserved_Order_Spectral_Structure_Factor_L20_Probe.py`
- Artifact target:
  - `Result/artifacts/0_11_conserved_order_spectral_structure_factor_l20_probe.json`
  - `Result/gl_conserved_order_spectral_structure_factor_l20_probe_stats.csv`
- Purpose:
  - Add an `L=20` larger-grid probe after Wave 25 domain-scale saturation.
  - Decide whether the structure-factor estimator is ready for exponent gates or still needs an explicit acceptance rule.
- Required gates:
  - `wave25_chain_gate.status == PASS`
  - `inbox_chain_gate.status == PASS`
  - `engine_path_gate.status == PASS`
  - `larger_grid_probe_gate.status == PASS`
  - `l20_margin_gate.status == PASS`
  - `derived_acceptance_rule_gate.status == PASS` before exponent or universality gates may use this estimator.
  - `next_path_gate.status != BLOCKED` before claim promotion.
- Current Wave 26 result:
  - overall status `WARN`
  - `larger_grid_probe_gate == PASS`
  - `l20_margin_gate == PASS`
  - `l20_domain_scale_relief_gate == PASS`
  - `extended_scaling_gate == WARN`
  - `derived_acceptance_rule_gate == BLOCKED`
  - `next_path_gate == BLOCKED`
  - L20 structure-factor margin: `6/6` passes, median `xi/L = 0.4347`, min `xi/L = 0.4333`
  - extended medians by grid: `L=8 -> 0.9972`, `L=12 -> 0.7166`, `L=16 -> 0.5661`, `L=20 -> 0.4347`
  - L20/L16 absolute `xi` ratio: `0.9599`; four-grid log `xi` vs log `L` slope: `0.1110`
  - structure-factor to lower-axis estimator ratio at L20: `2.6261`
- Interpretation:
  - L20 reduces the largest-grid domain-scale symptom, but this does not validate the estimator for exponent fitting.
  - The next useful work is a source-backed or derived estimator acceptance rule that defines admissible grids and reconciles estimator disagreement.


## Wave 27 Structure-Factor Acceptance-Rule Preflight

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Acceptance_Rule_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_acceptance_rule_gate.json`
- Purpose:
  - Convert the Wave 26 missing-rule blocker into an explicit topic-derived preflight rule.
  - Decide whether current Wave 24-26 structure-factor artifacts are admissible inputs for a future exponent/universality verifier.
- Required gates:
  - `artifact_chain_gate.status == PASS`
  - `candidate_rule_definition_gate.status == PASS`
  - `domain_scale_exclusion_gate.status == PASS` before using the full grid chain.
  - `admissible_subset_gate.status == PASS` before any declared subset can be considered.
  - `absolute_length_consistency_gate.status == PASS` before treating `xi_sf` as scaling length.
  - `estimator_reconciliation_gate.status != BLOCKED` before exponent gates may use the estimator.
  - `acceptance_rule_application_gate.status == PASS` before rerunning exponent or universality gates.
- Current Wave 27 result:
  - overall status `WARN`
  - `artifact_chain_gate == PASS`
  - `candidate_rule_definition_gate == PASS`
  - `admissible_subset_gate == PASS` for candidate grids `L=12,16,20`
  - `domain_scale_exclusion_gate == BLOCKED` because `L=8` remains domain-scale
  - `absolute_length_consistency_gate == BLOCKED` because `L20/L16 = 0.9599`
  - `estimator_reconciliation_gate == BLOCKED` because the L20 structure-factor/axis-lower ratio is `2.6261`
  - `acceptance_rule_application_gate == BLOCKED`
- Interpretation:
  - The missing-rule blocker is now narrower: a topic-derived preflight rule exists, but the current evidence does not satisfy it.
  - The next useful work is estimator reconciliation, source-backed calibration, or a dynamics/window repair that makes absolute `xi_sf` consistent before exponent claims are rerun.


## Wave 28 Structure-Factor / Axis-Estimator Reconciliation Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Estimator_Reconciliation_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_estimator_reconciliation_gate.json`
- Purpose:
  - Test whether the Wave 27 estimator disagreement is unstable/noisy or a stable but unaccepted calibration-factor gap.
  - Separate estimator calibration from the shared absolute-length decline seen between L16 and L20.
- Required gates:
  - `wave27_chain_gate.status == PASS`
  - `ratio_stability_gate.status == PASS` before studying any calibration factor.
  - `magnitude_reconciliation_gate.status == PASS` or an explicit source/derivation before accepting the factor.
  - `shared_absolute_length_trend_gate.status == PASS` before treating the issue as estimator-only.
  - `calibration_factor_gate.status == PASS` before exponent gates may use a rescaled estimator.
  - `reconciliation_application_gate.status == PASS` before rerunning exponent or universality gates.
- Current Wave 28 result:
  - overall status `WARN`
  - `wave27_chain_gate == PASS`
  - `ratio_stability_gate == PASS` with ratio drift `0.0219`
  - `magnitude_reconciliation_gate == BLOCKED` because the raw ratio remains above `2.0`
  - `shared_absolute_length_trend_gate == BLOCKED`: structure-factor `L20/L16 = 0.9548`, axis-lower `L20/L16 = 0.9762`
  - `calibration_factor_gate == BLOCKED` because the candidate factor `2.6555` is observed but not source-backed or derived
  - `reconciliation_application_gate == BLOCKED`
- Interpretation:
  - The estimator disagreement is structured enough to study, but not accepted.
  - The next useful work is either source-backed estimator calibration or a window/dynamics repair that restores absolute-length growth before exponent gates are rerun.


## Wave 29 Structure-Factor Calibration Source-Support Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Calibration_Source_Support_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_calibration_source_support_gate.json`
- Purpose:
  - Check whether the local reference package can source-back the observed calibration factor or current RMS inverse-k structure-factor proxy.
  - Record external primary-source candidates as candidates only, not accepted proof.
- Required gates:
  - `wave28_chain_gate.status == PASS`
  - `local_source_packaging_gate.status == PASS` before accepting estimator calibration locally.
  - `empirical_calibration_factor_gate.status == PASS` before using the observed factor in exponent fits.
  - `formula_alignment_gate.status == PASS` before treating the RMS inverse-k proxy as an accepted critical length.
  - `next_path_decision_gate.status != BLOCKED` before rerunning exponent or universality gates.
- Current Wave 29 result:
  - overall status `WARN`
  - `wave28_chain_gate == PASS`
  - `local_source_packaging_gate == BLOCKED`: required local match counts are zero for structure factor, second-moment correlation length, Fourier estimator definition, and finite-size admissibility.
  - `external_candidate_gate == WARN`: candidate primary sources are recorded but not packaged.
  - `empirical_calibration_factor_gate == BLOCKED` for candidate factor `2.6555`
  - `formula_alignment_gate == BLOCKED`
  - `next_path_decision_gate == BLOCKED`
- Interpretation:
  - The source-backed path is not ready locally.
  - The next useful work is to package primary second-moment/finite-size estimator sources with formula boundaries, or choose the window/dynamics repair path without pretending the calibration is accepted.


## Wave 30 Structure-Factor Estimator Source-Manifest Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Source_Manifest_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_source_manifest_gate.json`
- Source manifest:
  - `Data/03_Research/structure_factor_estimator_source_manifest.json`
- Purpose:
  - Package primary estimator-source candidates with DOI/URL, formula role, and claim boundary.
  - Keep metadata packaging separate from formula extraction and calibration acceptance.
- Required gates:
  - `wave29_chain_gate.status == PASS`
  - `manifest_schema_gate.status == PASS`
  - `primary_source_metadata_gate.status == PASS` before source-review work can proceed.
  - `local_formula_extraction_gate.status == PASS` before source formulas can support calibration.
  - `calibration_acceptance_gate.status == PASS` before any estimator rescaling or exponent rerun.
- Current Wave 30 result:
  - overall status `WARN`
  - `wave29_chain_gate == PASS`
  - `manifest_schema_gate == PASS`
  - `primary_source_metadata_gate == PASS` with three ready source rows
  - `local_formula_extraction_gate == BLOCKED`
  - `calibration_acceptance_gate == BLOCKED`
  - `next_path_gate == BLOCKED`
- Interpretation:
  - The source candidates are now packaged for review, but no formula has been extracted or mapped to the current estimator.
  - The next useful work is source-formula extraction and a map/reject decision for the current RMS inverse-k proxy.

## Wave 31 Structure-Factor Estimator Formula-Boundary Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Formula_Boundary_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_formula_boundary_gate.json`
- Formula-boundary manifest:
  - `Data/03_Research/structure_factor_estimator_formula_boundary.json`
- Purpose:
  - Extract the source-family second-moment correlation-length boundary from the packaged primary-source candidates.
  - Decide whether the current all-nonzero-mode RMS inverse-k proxy can be treated as that source-backed estimator.
- Required gates:
  - `wave30_chain_gate.status == PASS`
  - `formula_boundary_schema_gate.status == PASS`
  - `source_formula_extraction_gate.status == PASS` before replacement work can proceed.
  - `current_proxy_source_match_gate.status == PASS` before the current proxy can be used for calibration or exponent gates.
  - `calibration_acceptance_gate.status == PASS` before any Wave 28 calibration factor can be applied.
  - `replacement_path_gate.status != BLOCKED` before rerunning exponent or universality gates.
- Current Wave 31 result:
  - overall status `WARN`
  - `wave30_chain_gate == PASS`
  - `formula_boundary_schema_gate == PASS`
  - `source_formula_extraction_gate == PASS`
  - `current_proxy_source_match_gate == BLOCKED`
  - `calibration_acceptance_gate == BLOCKED`
  - `replacement_path_gate == BLOCKED`
- Interpretation:
  - The source formula boundary is now extracted, so the blocker is no longer vague formula absence.
  - The current RMS inverse-k proxy does not match the source-family lowest-mode second-moment relation and must stay diagnostic-only.
  - The next useful work is to implement a lowest-mode second-moment estimator candidate or repair the window/dynamics path before exponent claims are rerun.

## Wave 32 Lowest-Mode Second-Moment Estimator Candidate Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Lowest_Mode_Candidate_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_lowest_mode_candidate_gate.json`
- Purpose:
  - Implement the literal source-family lowest-mode estimator on the same L16/L20 conserved-order fields used by prior structure-factor diagnostics.
  - Separate formula implementation from observable availability so no surrogate `S(0)` quietly replaces the source relation.
- Required gates:
  - `wave31_chain_gate.status == PASS`
  - `formula_boundary_gate.status == PASS`
  - `lowest_mode_implementation_gate.status == PASS`
  - `lowest_mode_observable_gate.status == PASS` before the candidate can replace the RMS proxy.
  - `finite_size_trend_gate.status == PASS` before exponent gates may use the candidate.
  - `replacement_acceptance_gate.status == PASS` before rerunning exponent or universality gates.
- Current Wave 32 result:
  - overall status `WARN`
  - `wave31_chain_gate == PASS`
  - `formula_boundary_gate == PASS`
  - `lowest_mode_implementation_gate == PASS`
  - `lowest_mode_observable_gate == BLOCKED`
  - `finite_size_trend_gate == BLOCKED`
  - `replacement_acceptance_gate == BLOCKED`
  - valid lowest-mode cases: `0/15`
  - invalid reason: `zero_mode_not_larger_than_lowest_mode`
- Interpretation:
  - The replacement formula can be implemented, but the current single-snapshot conserved-order lane does not provide the source-family `S(0)` susceptibility observable.
  - The next useful work is to derive an ensemble/connected susceptibility second-moment lane or repair the window/dynamics path before exponent claims are rerun.

## Wave 33 Ensemble Susceptibility S0 Lane Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Ensemble_Susceptibility_Lane_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_ensemble_susceptibility_lane_gate.json`
- Purpose:
  - Separate the source-closer ensemble magnetization `S(0)` lane from the spatial-variance diagnostic proxy.
  - Prevent `N * Var_space(C)` from silently replacing source-family zero-mode susceptibility.
- Required gates:
  - `wave32_chain_gate.status == PASS`
  - `ensemble_susceptibility_definition_gate.status == PASS`
  - `raw_ensemble_susceptibility_gate.status == PASS` before a source-closer `S(0)` lane can feed a replacement estimator.
  - `source_equivalence_gate.status == PASS` before any `S(0)` proxy can be accepted for exponent use.
  - `finite_size_trend_gate.status == PASS` before exponent or universality gates may rerun.
  - `replacement_acceptance_gate.status == PASS` before replacing the RMS proxy.
- Current Wave 33 result:
  - overall status `WARN`
  - `wave32_chain_gate == PASS`
  - `ensemble_susceptibility_definition_gate == PASS`
  - `raw_ensemble_susceptibility_gate == BLOCKED`
  - `spatial_variance_proxy_gate == WARN`
  - `source_equivalence_gate == BLOCKED`
  - `finite_size_trend_gate == BLOCKED`
  - ensemble valid groups: none
  - spatial proxy valid groups: `L16_4000`, `L20_4000`
- Interpretation:
  - The source-closer ensemble magnetization lane is blocked by the conserved-mean constraint.
  - The spatial variance proxy can produce numbers, but it is not accepted as source-equivalent `S(0)`.
  - The next useful work is to source-back a conserved-order susceptibility policy, switch to a source-backed finite-k/canonical estimator, or repair the window/dynamics path.

## Wave 34 Estimator-Policy Source-Support Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Estimator_Policy_Source_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_estimator_policy_source_gate.json`
- Policy requirements manifest:
  - `Data/03_Research/structure_factor_estimator_policy_requirements.json`
- Purpose:
  - Define the source requirements for conserved-order susceptibility, finite-k/canonical replacement, and spatial-variance proxy exclusion.
  - Prevent estimator replacement until a policy path is source-backed and explicitly accepted.
- Required gates:
  - `wave33_chain_gate.status == PASS`
  - `policy_requirement_manifest_gate.status == PASS`
  - `conserved_susceptibility_source_gate.status == PASS` or `finite_k_policy_source_gate.status == PASS` before replacement work may continue.
  - `spatial_variance_proxy_policy_gate.status == PASS` to keep the proxy diagnostic-only unless source-backed.
  - `estimator_policy_selection_gate.status == PASS` before exponent or universality gates may rerun.
- Current Wave 34 result:
  - overall status `WARN`
  - `wave33_chain_gate == PASS`
  - `policy_requirement_manifest_gate == PASS`
  - `conserved_susceptibility_source_gate == BLOCKED`
  - `finite_k_policy_source_gate == BLOCKED`
  - `spatial_variance_proxy_policy_gate == PASS`
  - `estimator_policy_selection_gate == BLOCKED`
- Interpretation:
  - The policy requirements are explicit, but neither source-backed replacement path is accepted.
  - The next useful work is to package policy-specific sources or choose window/dynamics repair without pretending an estimator is accepted.

## Wave 35 Estimator-Policy Source-Candidate Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Policy_Source_Candidate_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_policy_source_candidate_gate.json`
- Source-candidate manifest:
  - `Data/03_Research/structure_factor_estimator_policy_source_candidates.json`
- Purpose:
  - Package fixed-magnetization/canonical and Cahn-Hilliard structure-factor source candidates for policy review.
  - Keep candidate metadata separate from accepted formula extraction and estimator replacement.
- Required gates:
  - `wave34_chain_gate.status == PASS`
  - `source_candidate_manifest_gate.status == PASS`
  - `conserved_policy_candidate_gate.status in {WARN, PASS}` as candidate coverage only.
  - `finite_k_policy_candidate_gate.status in {WARN, PASS}` as candidate coverage only.
  - `formula_extraction_gate.status == PASS` before policy acceptance work may continue.
  - `accepted_policy_gate.status == PASS` before exponent or universality gates may rerun.
- Current Wave 35 result:
  - overall status `WARN`
  - `wave34_chain_gate == PASS`
  - `source_candidate_manifest_gate == PASS`
  - `conserved_policy_candidate_gate == WARN`
  - `finite_k_policy_candidate_gate == WARN`
  - `spatial_variance_boundary_gate == PASS`
  - `formula_extraction_gate == BLOCKED`
  - `accepted_policy_gate == BLOCKED`
- Interpretation:
  - Policy-specific source candidates are packaged, but no candidate formula is extracted or accepted.
  - The next useful work is to extract policy formula boundaries or choose window/dynamics repair without pretending an estimator is accepted.

## Wave 36 Estimator-Policy Formula-Boundary Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Policy_Formula_Boundary_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_policy_formula_boundary_gate.json`
- Formula-boundary manifest:
  - `Data/03_Research/structure_factor_estimator_policy_formula_boundary.json`
- Purpose:
  - Extract conservative source boundaries from fixed-magnetization/canonical and Cahn-Hilliard structure-factor source candidates.
  - Prevent abstract-level source notes from becoming accepted estimator formulas.
- Required gates:
  - `wave35_chain_gate.status == PASS`
  - `source_candidate_chain_gate.status == PASS`
  - `formula_boundary_manifest_gate.status == PASS`
  - `abstract_boundary_gate.status == PASS` as boundary extraction only.
  - `accepted_estimator_formula_gate.status == PASS` before estimator replacement may continue.
  - `normalization_mapping_gate.status == PASS` before exponent or universality gates may rerun.
- Current Wave 36 result:
  - overall status `WARN`
  - `wave35_chain_gate == PASS`
  - `source_candidate_chain_gate == PASS`
  - `formula_boundary_manifest_gate == PASS`
  - `abstract_boundary_gate == PASS`
  - `accepted_estimator_formula_gate == BLOCKED`
  - `normalization_mapping_gate == BLOCKED`
  - `spatial_variance_boundary_gate == PASS`
- Interpretation:
  - Abstract-level policy boundaries are now explicit, but no estimator formula is accepted.
  - The next useful work is full-text formula extraction or explicit window/dynamics repair without accepting an estimator.

## Wave 37 Full-Text Formula-Extraction Readiness Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Full_Text_Formula_Readiness_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_full_text_formula_readiness_gate.json`
- Readiness manifest:
  - `Data/03_Research/structure_factor_full_text_formula_extraction_readiness.json`
- Purpose:
  - Record whether rendered/abstract source access is sufficient for formula acceptance.
  - Keep rendered text as boundary evidence only until local TeX/PDF math extraction is available.
- Required gates:
  - `wave36_chain_gate.status == PASS`
  - `formula_boundary_chain_gate.status == PASS`
  - `readiness_manifest_gate.status == PASS`
  - `local_math_source_gate.status == PASS` before formula extraction may be accepted.
  - `accepted_formula_source_gate.status == PASS` before estimator replacement may continue.
  - `normalization_mapping_gate.status == PASS` before exponent or universality gates may rerun.
- Current Wave 37 result:
  - overall status `WARN`
  - `wave36_chain_gate == PASS`
  - `formula_boundary_chain_gate == PASS`
  - `readiness_manifest_gate == PASS`
  - `rendered_boundary_gate == WARN`
  - `local_math_source_gate == BLOCKED`
  - `accepted_formula_source_gate == BLOCKED`
  - `normalization_mapping_gate == BLOCKED`
- Interpretation:
  - Rendered and abstract source access is boundary evidence only, not accepted formula extraction.
  - The next useful work is to localize TeX/PDF math sources or choose window/dynamics repair without accepting an estimator.

## Wave 38 Source-Archive Localization Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Source_Archive_Localization_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_source_archive_localization_gate.json`
- Localization manifest:
  - `Data/03_Research/structure_factor_source_archive_localization_manifest.json`
- Purpose:
  - Verify temporary local arXiv source archives, hashes, and main TeX member discovery.
  - Keep archive localization separate from formula extraction and estimator acceptance.
- Required gates:
  - `wave37_chain_gate.status == PASS`
  - `readiness_chain_gate.status == PASS`
  - `localization_manifest_gate.status == PASS`
  - `temporary_local_archive_gate.status == PASS`
  - `tex_member_identification_gate.status == PASS`
  - `formula_extraction_gate.status == PASS` before estimator replacement may continue.
- Current Wave 38 result:
  - overall status `WARN`
  - `wave37_chain_gate == PASS`
  - `localization_manifest_gate == PASS`
  - `temporary_local_archive_gate == PASS`
  - `tex_member_identification_gate == PASS`
  - `repo_archival_policy_gate == WARN`
  - `formula_extraction_gate == BLOCKED`
- Interpretation:
  - Source archives and main TeX members are localized in a temporary cache, but formulas are not extracted or accepted.
  - The next useful work is exact TeX formula-fragment extraction or a repo archival policy decision, without accepting an estimator.

## Wave 44 Source-Archive Policy Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Source_Archive_Policy_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_source_archive_policy_gate.json`
- Source-archive policy manifest:
  - `Data/03_Research/structure_factor_source_archive_policy.json`
- Purpose:
  - Record acquisition URLs, expected hashes, candidate repo archive paths, and claim boundary for the three structure-factor source archives.
  - Keep formula-fragment preservation separate from raw source availability and estimator-policy acceptance.
- Required gates:
  - `wave43_chain_gate.status == PASS`
  - `formula_fragment_preservation_gate.status == PASS`
  - `source_archive_policy_manifest_gate.status == PASS`
  - `repo_archive_availability_gate.status == PASS` before fresh formula extraction is repo-reproducible.
  - `estimator_policy_gate.status == PASS` before exponent or universality gates may rerun.
- Current Wave 44 result:
  - overall status `WARN`
  - `wave43_chain_gate == PASS`
  - `formula_fragment_preservation_gate == PASS` with `19` preserved fragments
  - `source_archive_policy_manifest_gate == PASS`
  - `repo_archive_availability_gate == PASS` after all `3/3` repo archives were restored and hash-verified
  - `temporary_cache_availability_gate == BLOCKED`; temp cache is no longer the reproducibility source
  - `estimator_policy_gate == BLOCKED`
- Interpretation:
  - The source policy is now machine-readable and repo source availability is restored.
  - The next useful work is estimator-policy/UET normalization mapping using the restored source archives and preserved formula fragments.

## Wave 43 TeX Formula-Fragment Extraction Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Tex_Formula_Fragment_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_tex_formula_fragment_gate.json`
- Formula-fragment manifest:
  - `Data/03_Research/structure_factor_tex_formula_fragments.json`
- Purpose:
  - Extract exact TeX formula fragments from the three localized source archives identified in Wave 38.
  - Keep formula extraction separate from estimator-policy acceptance, UET normalization mapping, and exponent reruns.
- Required gates:
  - `wave38_chain_gate.status == PASS`
  - `formula_fragment_manifest_gate.status == PASS`
  - `source_archive_availability_gate.status == PASS` before fragments can be refreshed from source archives.
  - `source_formula_fragment_gate.status == PASS` for a fresh extraction, or `WARN` only when prior extracted fragments exist but the temporary cache is missing.
  - `accepted_estimator_policy_gate.status == PASS` before estimator replacement or exponent gates may rerun.
  - `uet_normalization_mapping_gate.status == PASS` before claim-bearing scaling use.
- Current Wave 43 result:
  - overall status `WARN`
  - `wave38_chain_gate == PASS`
  - `formula_fragment_manifest_gate == PASS`
  - `source_archive_availability_gate == PASS` using the repo archive fallback from Wave 44/45
  - `source_formula_fragment_gate == PASS` with fresh extraction restored
  - extracted fragments: `19` total from `3` source lanes
  - `accepted_estimator_policy_gate == BLOCKED`
  - `uet_normalization_mapping_gate == BLOCKED`
  - `next_path_gate == BLOCKED`
- Interpretation:
  - The source-formula absence blocker is narrowed: TeX formula fragments now exist in a machine-readable manifest and can be freshly regenerated from repo archives.
  - No source fragment is accepted as the current UET conserved-order estimator policy yet.
  - The next useful work is UET normalization mapping and estimator-policy selection or explicit rejection before exponent, material, RG, universality, or Tier A claims.

## Wave 46 Estimator Policy Normalization-Map Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Estimator_Normalization_Map_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_estimator_normalization_map_gate.json`
- Normalization-map manifest:
  - `Data/03_Research/structure_factor_estimator_normalization_map.json`
- Purpose:
  - Map the restored Wave 45 source formula fragments to estimator-policy lanes before accepting any replacement estimator.
  - Separate fixed-magnetization/canonical susceptibility boundary evidence from the Cahn-Hilliard finite-k structure-factor candidate lane.
  - Keep UET lattice normalization and finite-size admissibility as explicit blockers before exponent reruns.
- Required gates:
  - `wave43_chain_gate.status == PASS`
  - `wave44_archive_gate.status == PASS`
  - `fragment_coverage_gate.status == PASS`
  - `policy_mapping_manifest_gate.status == PASS`
  - `uet_normalization_mapping_gate.status == PASS` before any source formula can be used in scaling claims.
  - `finite_size_admissibility_gate.status == PASS` before finite-size/exponent gates may rerun.
  - `estimator_policy_acceptance_gate.status == PASS` before estimator replacement is accepted.
- Current Wave 46 result:
  - overall status `WARN`
  - `wave43_chain_gate == PASS`
  - `wave44_archive_gate == PASS`
  - `fragment_coverage_gate == PASS`
  - `policy_mapping_manifest_gate == PASS`
  - `finite_k_policy_candidate_gate == WARN`
  - `conserved_susceptibility_policy_gate == BLOCKED`
  - `uet_normalization_mapping_gate == BLOCKED`
  - `finite_size_admissibility_gate == BLOCKED`
  - `estimator_policy_acceptance_gate == BLOCKED`
- Interpretation:
  - Source formulas are now mapped rather than merely preserved.
  - The Cahn-Hilliard finite-k `S(q,t)` source lane is the strongest candidate family, but it is not accepted until UET lattice normalization, q-window admissibility, and estimator implementation pass.
  - Do not rerun exponent, universality, material, RG, or Tier A gates from this artifact alone.

## Wave 47 Cahn-Hilliard Finite-K Normalization Preflight

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Normalization_Preflight.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_ch_finite_k_normalization_preflight_gate.json`
- Preflight manifest:
  - `Data/03_Research/structure_factor_ch_finite_k_normalization_preflight.json`
- Purpose:
  - Convert the Wave 46 CH finite-k candidate into explicit normalization and admissibility checks.
  - Declare what is closed in lattice units and what still blocks estimator acceptance.
  - Prevent exponent reruns from using a source formula before field normalization, coefficient policy, xi extraction, and q-window admissibility are ready.
- Required gates:
  - `wave46_chain_gate.status == PASS`
  - `ch_candidate_chain_gate.status == PASS`
  - `preflight_manifest_gate.status == PASS`
  - `fourier_convention_gate.status == PASS`
  - `field_normalization_gate.status == PASS` before field mapping is accepted.
  - `coefficient_mapping_gate.status == PASS` before source dynamics coefficients are used as source-backed.
  - `xi_extraction_rule_gate.status == PASS` before a finite-k length can feed scaling.
  - `finite_size_admissibility_gate.status == PASS` before exponent fits rerun.
  - `implementation_acceptance_gate.status == PASS` before estimator replacement is accepted.
- Current Wave 47 result:
  - overall status `WARN`
  - `wave46_chain_gate == PASS`
  - `ch_candidate_chain_gate == PASS`
  - `preflight_manifest_gate == PASS`
  - `fourier_convention_gate == PASS`
  - `field_normalization_gate == WARN`
  - `coefficient_mapping_gate == BLOCKED`
  - `xi_extraction_rule_gate == BLOCKED`
  - `finite_size_admissibility_gate == BLOCKED`
  - `implementation_acceptance_gate == BLOCKED`
  - `estimator_acceptance_preflight_gate == BLOCKED`
- Interpretation:
  - The q-grid convention is now explicit in lattice units, but that is not enough to accept the estimator.
  - The next useful work is an implementation verifier for a source-backed CH finite-k estimator candidate with q-window diagnostics and explicit coefficient inclusion/exclusion policy.
  - Do not rerun exponent, universality, material, RG, or Tier A gates from this preflight alone.

## Wave 48 Cahn-Hilliard Finite-K Estimator Candidate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Estimator_Candidate.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_ch_finite_k_estimator_candidate_gate.json`
  - `Result/gl_structure_factor_ch_finite_k_estimator_candidate_stats.csv`
- Purpose:
  - Implement the source-linked CH finite-k `S(q)` candidate required by Wave 47.
  - Use centered UET `C`, the declared FFT q-grid, and a finite-k peak rule instead of the rejected all-nonzero RMS inverse-k proxy.
  - Emit q-window, low-mode, domain-scale, and finite-size trend diagnostics before any exponent rerun.
- Required gates:
  - `wave47_chain_gate.status == PASS`
  - `source_formula_linkage_gate.status == PASS`
  - `implementation_coverage_gate.status == PASS`
  - `q_window_diagnostic_gate.status == PASS`
  - `domain_scale_guard_gate.status == PASS`
  - `finite_size_trend_gate.status == PASS` as diagnostic readiness only.
  - `coefficient_policy_gate.status == PASS` before source dynamics coefficients are treated as mapped.
  - `estimator_acceptance_gate.status == PASS` before exponent gates may use the candidate.
- Current Wave 48 result:
  - overall status `WARN`
  - blocker label `ch_finite_k_candidate_implemented_acceptance_policy_open`
  - `wave47_chain_gate == PASS`
  - `source_formula_linkage_gate == PASS`
  - `implementation_coverage_gate == PASS`
  - `q_window_diagnostic_gate == PASS`
  - `domain_scale_guard_gate == PASS`
  - `finite_size_trend_gate == PASS`
  - `coefficient_policy_gate == BLOCKED`
  - `estimator_acceptance_gate == BLOCKED`
  - median `xi/L = 0.5`; pass fraction `12/18`; peak low-window-edge count `11/18`
- Interpretation:
  - The candidate is now implemented and source-linked, so the blocker is no longer missing implementation.
  - It is still not an accepted estimator because coefficient policy, field normalization, q-window acceptance, and exponent rerun gates remain open.
  - Do not rerun exponent, universality, material, RG, or Tier A gates from this candidate alone.


## Wave 49 Cahn-Hilliard Finite-K Acceptance Policy

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Acceptance_Policy_Gate.py`
- Artifact target:
  - `Data/03_Research/structure_factor_ch_finite_k_acceptance_policy.json`
  - `Result/artifacts/0_11_structure_factor_ch_finite_k_acceptance_policy_gate.json`
- Purpose:
  - Define row-level acceptance before any estimator replacement or exponent rerun.
  - Keep measurement-only `S(q)` diagnostics separate from source dynamics coefficient claims.
  - Exclude finite-k peaks that hit the low-window edge from claim-bearing exponent rows.
- Required gates:
  - `wave48_chain_gate.status == PASS`
  - `acceptance_policy_manifest_gate.status == PASS`
  - `coefficient_exclusion_policy_gate.status == PASS` for measurement-only diagnostics.
  - `source_dynamics_coefficient_mapping_gate.status == PASS` before source dynamics coefficients are accepted.
  - `accepted_row_coverage_gate.status == PASS` before finite-size/exponent reruns may use the candidate.
  - `estimator_acceptance_gate.status == PASS` before estimator replacement is accepted.
  - `exponent_rerun_gate.status == PASS` before any exponent, universality, material, RG, or Tier A claim changes.
- Current Wave 49 result:
  - overall status `WARN`
  - blocker label `ch_finite_k_acceptance_policy_defined_finite_size_coverage_and_normalization_open`
  - `wave48_chain_gate == PASS`
  - `acceptance_policy_manifest_gate == PASS`
  - `coefficient_exclusion_policy_gate == PASS`
  - `low_window_edge_policy_gate == PASS`
  - `field_normalization_policy_gate == WARN`
  - `accepted_row_coverage_gate == BLOCKED`
  - `source_dynamics_coefficient_mapping_gate == BLOCKED`
  - `estimator_acceptance_gate == BLOCKED`
  - `exponent_rerun_gate == BLOCKED`
  - accepted rows `6/18`, accepted grid count `1`, all accepted rows at `L20`
- Interpretation:
  - The policy gate narrows the blocker from open acceptance policy to finite-size row coverage plus field/coefficient normalization.
  - The candidate remains diagnostic-only because strict policy leaves no accepted multi-grid coverage.
  - Do not rerun exponent, universality, material, RG, or Tier A gates from this policy artifact alone.


## Wave 50 Cahn-Hilliard Finite-K Extended-Grid Coverage Probe

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Extended_Grid_Coverage_Probe.py`
- Artifact target:
  - `Result/artifacts/0_11_structure_factor_ch_finite_k_extended_grid_coverage_probe.json`
  - `Result/gl_structure_factor_ch_finite_k_extended_grid_coverage_probe_stats.csv`
- Purpose:
  - Test whether the Wave 49 accepted-row coverage blocker can be repaired by adding larger grids under the unchanged strict policy.
  - Keep this as a coverage probe, not estimator acceptance or exponent rerun.
- Required gates:
  - `wave49_chain_gate.status == PASS`
  - `extended_grid_probe_gate.status == PASS`
  - `policy_application_gate.status == PASS`
  - `accepted_multi_grid_coverage_gate.status == PASS` before coverage is treated as repaired.
  - `field_normalization_policy_gate.status == PASS` before source-equivalent field normalization is accepted.
  - `source_dynamics_coefficient_mapping_gate.status == PASS` before source CH dynamics coefficients are accepted.
  - `estimator_acceptance_gate.status == PASS` before estimator replacement is accepted.
  - `exponent_rerun_gate.status == PASS` before any exponent, universality, material, RG, or Tier A claim changes.
- Current Wave 50 result:
  - overall status `WARN`
  - blocker label `ch_finite_k_extended_grid_coverage_repaired_normalization_and_coefficients_open`
  - `wave49_chain_gate == PASS`
  - `extended_grid_probe_gate == PASS`
  - `policy_application_gate == PASS`
  - `accepted_multi_grid_coverage_gate == PASS` with accepted grid counts `L20:6`, `L24:2`, `L28:2`
  - `field_normalization_policy_gate == WARN`
  - `source_dynamics_coefficient_mapping_gate == BLOCKED`
  - `estimator_acceptance_gate == BLOCKED`
  - `exponent_rerun_gate == BLOCKED`
- Interpretation:
  - The row-coverage blocker is narrowed: larger grids can satisfy the strict policy's minimum multi-grid row coverage.
  - The estimator remains unaccepted because field normalization and source coefficient mapping are still unresolved.
  - Do not rerun exponent, universality, material, RG, or Tier A gates from this coverage probe alone.


## Wave 51 Cahn-Hilliard Finite-K Field/Coefficient Policy Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Field_Coefficient_Policy_Gate.py`
- Artifact target:
  - `Data/03_Research/structure_factor_ch_finite_k_field_coefficient_policy.json`
  - `Result/artifacts/0_11_structure_factor_ch_finite_k_field_coefficient_policy_gate.json`
- Purpose:
  - Separate the measurement-only finite-k `S(q)` lane from source-dynamics and material-claim lanes.
  - Keep Wave 50 coverage as diagnostic evidence only until field normalization is source-equivalent or replaced.
- Required gates:
  - `wave50_chain_gate.status == PASS`
  - `measurement_field_centering_gate.status == PASS`
  - `measurement_only_coefficient_exclusion_gate.status == PASS`
  - `source_equivalent_field_normalization_gate.status == PASS` before estimator replacement is accepted.
  - `accepted_estimator_replacement_gate.status == PASS` before exponent gates rerun.
  - `exponent_rerun_gate.status == PASS` before any exponent, universality, material, RG, or Tier A claim changes.
- Current Wave 51 result:
  - overall status `WARN`
  - blocker label `ch_finite_k_field_normalization_open_measurement_coefficient_policy_separated`
  - `wave50_chain_gate == PASS`
  - `measurement_field_centering_gate == PASS`
  - `measurement_only_coefficient_exclusion_gate == PASS`
  - `diagnostic_measurement_lane_gate == PASS`
  - `source_equivalent_field_normalization_gate == BLOCKED`
  - `source_dynamics_coefficient_mapping_gate == BLOCKED` for source-dynamics/material claims
  - `accepted_estimator_replacement_gate == BLOCKED`
  - `exponent_rerun_gate == BLOCKED`
- Interpretation:
  - The source-coefficient blocker is no longer allowed to block the measurement-only diagnostic lane.
  - The topic still cannot accept the finite-k estimator for exponent use because centered `C` is not source-equivalent.
  - The next useful work is a field-normalization derivation, a replacement field observable, or a source-backed rule for centered `C` before exponent reruns.


## Wave 52 Cahn-Hilliard Finite-K Field-Normalization Decision Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Field_Normalization_Decision_Gate.py`
- Artifact target:
  - `Data/03_Research/structure_factor_ch_finite_k_field_normalization_decision.json`
  - `Result/artifacts/0_11_structure_factor_ch_finite_k_field_normalization_decision_gate.json`
- Purpose:
  - Decide how far centered UET `C` can be used against the source Cahn-Hilliard `S(q,t)` field symbols.
  - Separate diagnostic centered-field use from accepted source-equivalent field normalization.
- Required gates:
  - `wave51_chain_gate.status == PASS`
  - `source_field_symbol_gate.status == PASS`
  - `uet_centered_field_proxy_gate.status == PASS` for diagnostic finite-k measurement only.
  - `amplitude_normalization_gate.status == PASS` before source-equivalent field normalization can be accepted.
  - `averaging_convention_gate.status == PASS` before source-equivalent field normalization can be accepted.
  - `source_equivalent_field_acceptance_gate.status == PASS` before estimator replacement is accepted.
  - `exponent_rerun_gate.status == PASS` before exponent, universality, material, RG, or Tier A claim changes.
- Current Wave 52 result:
  - overall status `WARN`
  - blocker label `ch_finite_k_field_amplitude_and_averaging_normalization_open`
  - `wave51_chain_gate == PASS`
  - `source_field_symbol_gate == PASS`
  - `uet_centered_field_proxy_gate == PASS`
  - `diagnostic_measurement_lane_gate == PASS`
  - `amplitude_normalization_gate == BLOCKED`
  - `averaging_convention_gate == BLOCKED`
  - `source_equivalent_field_acceptance_gate == BLOCKED`
  - `accepted_estimator_replacement_gate == BLOCKED`
  - `exponent_rerun_gate == BLOCKED`
- Interpretation:
  - Centered `C` is acceptable only as a diagnostic finite-k proxy field.
  - The accepted-estimator path now specifically needs an amplitude/variance normalization policy and an ensemble/time-averaging convention.
  - Do not rerun exponent, universality, material, RG, or Tier A gates from this decision artifact alone.


## Wave 53 Cahn-Hilliard Finite-K Shape-Only Normalization Policy Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Shape_Only_Normalization_Policy_Gate.py`
- Artifact target:
  - `Data/03_Research/structure_factor_ch_finite_k_shape_only_normalization_policy.json`
  - `Result/artifacts/0_11_structure_factor_ch_finite_k_shape_only_normalization_policy_gate.json`
- Purpose:
  - Separate amplitude-invariant `q_peak` shape diagnostics from source-equivalent `S(q)` amplitude and susceptibility claims.
  - Preserve Wave 50/52 diagnostic coverage without accepting estimator replacement.
- Required gates:
  - `wave52_chain_gate.status == PASS`
  - `q_peak_amplitude_invariance_gate.status == PASS`
  - `diagnostic_seed_aggregation_gate.status == PASS`
  - `shape_only_diagnostic_lane_gate.status == PASS` for diagnostic use only.
  - `source_amplitude_normalization_gate.status == PASS` before source `S(q)` amplitude or susceptibility claims.
  - `source_averaging_convention_gate.status == PASS` before source-equivalent estimator use.
  - `source_equivalent_estimator_gate.status == PASS` before exponent rerun.
- Current Wave 53 result:
  - overall status `WARN`
  - blocker label `ch_finite_k_source_averaging_and_uncertainty_policy_open`
  - `wave52_chain_gate == PASS`
  - `q_peak_amplitude_invariance_gate == PASS`
  - `diagnostic_seed_aggregation_gate == PASS`
  - `shape_only_diagnostic_lane_gate == PASS`
  - `source_amplitude_normalization_gate == BLOCKED`
  - `source_averaging_convention_gate == BLOCKED`
  - `source_equivalent_estimator_gate == BLOCKED`
  - `exponent_rerun_gate == BLOCKED`
- Interpretation:
  - `q_peak` and `xi_peak = 2*pi/q_peak` can remain diagnostic shape-only measurements because positive amplitude scaling does not move the peak.
  - This does not accept source `S(q)` amplitude, susceptibility, ensemble/time averaging, estimator replacement, or exponent use.
  - The next useful work is a source averaging/uncertainty acceptance policy or a replacement observable policy.


## Wave 54 Cahn-Hilliard Finite-K Source Averaging/Uncertainty Policy Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Source_Averaging_Uncertainty_Gate.py`
- Artifact target:
  - `Data/03_Research/structure_factor_ch_finite_k_source_averaging_uncertainty_policy.json`
  - `Result/artifacts/0_11_structure_factor_ch_finite_k_source_averaging_uncertainty_gate.json`
- Purpose:
  - Separate diagnostic seed aggregation from claim-bearing source averaging and uncertainty propagation.
  - Define the replicate/time/uncertainty blockers before any estimator replacement or exponent rerun.
- Required gates:
  - `wave53_chain_gate.status == PASS`
  - `diagnostic_seed_aggregation_gate.status == PASS` for diagnostic use only.
  - `claim_bearing_replicate_gate.status == PASS` before claim-bearing uncertainty use.
  - `source_time_averaging_gate.status == PASS` before source-equivalent `S(q,t)` averaging use.
  - `uncertainty_interval_policy_gate.status == PASS` before finite-size/exponent fits.
  - `source_equivalent_estimator_gate.status == PASS` before exponent rerun.
- Current Wave 54 result:
  - overall status `WARN`
  - blocker label `ch_finite_k_replicate_temporal_averaging_or_replacement_observable_open`
  - `wave53_chain_gate == PASS`
  - `diagnostic_seed_aggregation_gate == PASS`
  - `claim_bearing_replicate_gate == BLOCKED`
  - `source_time_averaging_gate == BLOCKED`
  - `uncertainty_interval_policy_gate == BLOCKED`
  - `source_equivalent_estimator_gate == BLOCKED`
  - `exponent_rerun_gate == BLOCKED`
- Interpretation:
  - Current accepted rows are enough for diagnostic multi-grid seed aggregation only.
  - Accepted L24/L28 coverage has only two rows each, rows are final snapshots, and no uncertainty interval/fit propagation policy is accepted.
  - The next useful work is either more replicate/temporal averaging evidence or an explicit replacement observable policy before estimator acceptance.

## Wave 55 Cahn-Hilliard Finite-K Next-Path Decision Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_CH_Finite_K_Next_Path_Decision_Gate.py`
- Artifact target:
  - `Data/03_Research/structure_factor_ch_finite_k_next_path_decision.json`
  - `Result/artifacts/0_11_structure_factor_ch_finite_k_next_path_decision_gate.json`
- Purpose:
  - Decide whether the next accepted-estimator path should be replicate/temporal acquisition or replacement-observable review.
  - Keep this decision separate from estimator acceptance, exponent rerun, and universality/material/RG claims.
- Required gates:
  - `wave54_chain_gate.status == PASS`
  - `replicate_temporal_acquisition_plan_gate.status == PASS` when no replacement observable is accepted.
  - `selected_next_path_gate.status == PASS`
  - `estimator_acceptance_gate.status == PASS` before exponent rerun.
  - `exponent_rerun_gate.status == PASS` before exponent, universality, material, RG, or Tier A claim changes.
- Current Wave 55 result:
  - overall status `WARN`
  - blocker label `ch_finite_k_replicate_temporal_acquisition_plan_defined_execution_open`
  - selected next path `replicate_temporal_acquisition`
  - `wave54_chain_gate == PASS`
  - `replicate_temporal_acquisition_plan_gate == PASS`
  - `selected_next_path_gate == PASS`
  - `replacement_observable_available_gate == BLOCKED`
  - `estimator_acceptance_gate == BLOCKED`
  - `exponent_rerun_gate == BLOCKED`
  - `next_path_gate == BLOCKED`
- Interpretation:
  - Replacement-observable policies remain unavailable for accepted use.
  - The next controller is execution of the acquisition plan: add at least two accepted L24 rows and two accepted L28 rows, plus temporal/ensemble averaging and uncertainty propagation, or accept a source-backed replacement observable.
  - Do not rerun exponent, universality, material, RG, or Tier A gates from this decision artifact alone.

## Core Wave 9 Noether-Phase-Field Dependency Gate

- Candidate command:
  - `python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Noether_Phase_Field_Dependency_Gate.py`
- Artifact target:
  - `Result/artifacts/0_11_noether_phase_field_dependency_gate.json`
- Regression command:
  - `python -m pytest docs/core/test/test_noether_phase_field_topic_0_11_dependency.py -q`
- Purpose:
  - Propagate the core Wave 9 coordinate result into Topic 0.11 without identifying the current topic field with a microscopic O(2) state or signed charge by assumption.
  - Preserve the independent Wave 55 estimator controller and the separation of Noether charge, matter-space `Phi`, and derived trace `R`.
  - Detect historical `Draft` snapshots while taking current readiness from canonical metadata.
- Required gates:
  - `core_hydrodynamic_coordinate_gate.status == PASS`
  - `microscopic_inverse_boundary_gate.status == PASS`
  - `trace_and_space_separation_gate.status == PASS`
  - `wave55_controller_preservation_gate.status == PASS`
  - `canonical_topic_status_gate.status == PASS`
  - `topic_C_signed_charge_identity_gate.status == PASS` before Topic 0.11 `C` may be called a signed O(2) charge coordinate.
  - `equation_of_state_and_transport_gate.status == PASS` before the phase-field constitutive law may be called action-derived.
  - `topic_promotion_gate.status == PASS` before any topic claim changes.
- Current result:
  - overall status `BLOCKED`
  - evidence status `CONDITIONAL_HYDRODYNAMIC_COORDINATE_COMPATIBILITY`
  - `core_hydrodynamic_coordinate_gate == PASS`
  - `microscopic_inverse_boundary_gate == PASS`
  - `trace_and_space_separation_gate == PASS`
  - `wave55_controller_preservation_gate == PASS`
  - `canonical_topic_status_gate == PASS` with `Structured / Tier B` before and after
  - `historical_pilot_status_snapshot_gate == WARN` because the earlier pilot retains its run-time `Draft` snapshot
  - `topic_C_signed_charge_identity_gate == BLOCKED`
  - `equation_of_state_and_transport_gate == BLOCKED`
  - `topic_promotion_gate == BLOCKED`
- Interpretation:
  - The final affine coordinate layer is exact only after physical charge identity, averaging, and scales are declared.
  - Topic 0.11 still lacks the system-specific charge map, covariant coarse graining, EOS derivation/calibration, and transport match.
  - `ch_finite_k_replicate_temporal_acquisition_plan_defined_execution_open` remains the topic controller; no simulation or estimator gate was rerun.
