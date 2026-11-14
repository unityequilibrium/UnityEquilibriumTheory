# UPDATE LOG: UET GR Closed-Limit and Non-Closed Response

> **Scope:** `docs/core` with foundation dependency on `0.19_Gravity_GR`
> **Owner:** UET research collaboration
> **Purpose:** Record each blocker-narrowing wave in the GR correspondence
> program without upgrading claims ahead of generated evidence.

## Entries

### 2026-08-30 - Close prescribed Topic 13 stress-energy wiring

- Scope: bounded He-4/O(2) stress-energy construction, 3+1 projection, GH source, unit scaling, parent gate, and registry sync
- Wave type: formula/source composition, algebraic reconstruction, negative-control, ontology, dependency, and claim-boundary pass
- Result: `CORE_CURVED_3P1_TOPIC13_PRESCRIBED_MATTER_WIRING_READY` is `CLOSED_FOR_LANE`; parent is `PARTIAL_CURVED_3P1_GH_PERIODIC_PRESCRIBED_MATTER_READY`; Gravity remains blocked
- Verified with: 23/23 audit checks, rest/boost/nonzero-shift reconstruction, vacuum-null source, natural/SI scaling, and seven focused tests
- Still open: constraint-preserving non-periodic boundaries, self-consistent matter evolution/conservation, physical SI Einstein coupling, and dimensional detector observables
- Next controller: `curved_3p1_constraint_preserving_boundaries_and_dimensional_observable_mapping_missing`
- Claim impact: prescribed source interface only; no matter-coupled spacetime solution, Einstein-equation derivation, or external validation
### 2026-08-29 - Close the periodic generalized-harmonic time-evolution lane

- Scope: periodic vacuum RK4 evolution, characteristic CFL policy, exact harmonic gauge wave, and propagated gauge/reduction/curl constraints
- Wave type: numerical integration, analytic-control, convergence, constraint-damping, gate, registry, and claim-boundary pass
- Added or changed: GH evolution module, verifier, three artifacts, focused tests, Core exports, parent gate, equation-registry addendum, dependency reporting, and branch/research specifications
- Verified with: Minkowski exact fixed point; spatial orders `1.9845, 1.9961`; temporal order `3.9266`; `gamma2` damping relative error below `1e-8`; CFL and no-projection/filtering controls
- Result: `CORE_CURVED_3P1_GH_PERIODIC_VACUUM_EVOLUTION_READY` is `CLOSED_FOR_LANE`; parent is `PARTIAL_CURVED_3P1_GH_PERIODIC_VACUUM_EVOLUTION_READY`; Gravity remains blocked
- Blocker narrowed: time integration, CFL, periodic constraint propagation, and temporal convergence are no longer open
- Still open: constraint-preserving non-periodic boundaries, Topic 13 stress-energy wiring, strong-field/multi-chart controls, and dimensional detector observables
- Next controller: `curved_3p1_constraint_preserving_boundaries_and_topic13_stress_energy_wiring_missing`
- Claim impact: no promotion to production numerical relativity, matter-coupled UET, Gravity compatibility, or external validation

### 2026-08-28 - Close the generalized-harmonic nonlinear vacuum-RHS lane

- Scope: source-locked GH Eqs. (35)-(40), metric-state reconstruction, nonlinear vacuum RHS, and algebraic `gamma0` gauge-constraint damping
- Wave type: formula/source pass, independent-index operator verification, negative-control gate, registry/dependency sync, and claim-boundary pass
- Added or changed: nonlinear GH module path, verifier, three artifacts, focused tests, Core exports, parent gate, equation-registry addendum, dependency reporting, and branch/research specifications
- Verified with: Minkowski exact fixed point; constant-grid and spatially varying explicit-index references; gauge-source derivative injection; `gamma0` isolation and linear scaling; kinematics, tensor-symmetry, invalid-metric, and no-fit/no-clipping controls
- Result: `CORE_CURVED_3P1_GH_NONLINEAR_VACUUM_RHS_READY` is `CLOSED_FOR_LANE`; parent is `PARTIAL_CURVED_3P1_GH_NONLINEAR_VACUUM_RHS_READY`; Gravity remains blocked
- Blocker narrowed: nonlinear RHS transcription and algebraic gauge damping are no longer open; controller is now `curved_3p1_generalized_harmonic_time_integration_and_constraint_propagation_missing`
- Still open: time integrator/CFL, propagated gauge/reduction constraints, temporal convergence, constraint-preserving boundaries, matter wiring, and SI observables
- Claim impact: no promotion to a time-integrated numerical-relativity solver, matter-coupled curved UET parent, or Gravity compatibility

### 2026-08-28 - Close the generalized-harmonic principal-system lane

- Scope: source-locked first-order GH principal equations, characteristic fields, symmetrizer, gauge/reduction constraints, and reduction damping
- Wave type: formula/source pass, formal hyperbolicity gate, manufactured convergence gate, negative-control gate, registry/dependency sync, and claim-boundary pass
- Added or changed: GH module, verifier, formula/verification/branch artifacts, source equation locators, focused tests, Core exports, parent gate, registry addendum, dependency reporting, and branch specification
- Verified with: 15 direction/parameter principal symbols; complete rank-5 transforms; analytic symmetrizer positivity and symmetry; characteristic roundtrip; Minkowski gauge constraint; reduction/curl controls; three-resolution manufactured convergence
- Result: `CORE_CURVED_3P1_GH_PRINCIPAL_SYSTEM_READY` is `CLOSED_FOR_LANE`; parent remains `PARTIAL`; Gravity remains blocked
- Blocker narrowed: GH formulation/hyperbolicity is no longer open at principal level; controller is now `curved_3p1_generalized_harmonic_nonlinear_rhs_and_gamma0_constraint_damping_missing`
- Still open: complete nonlinear GH RHS, gamma0 gauge damping, time integration/CFL, full constraint propagation, temporal convergence, constraint-preserving boundaries, matter wiring, and SI observables
- Claim impact: no promotion to a complete Einstein evolution, numerical-relativity solver, or Gravity compatibility

### 2026-08-28 - Close ADM RHS operator and fixed-gauge hyperbolicity no-go

- Scope: nonlinear periodic ADM metric/K right-hand sides and formulation selection
- Wave type: source/formula pass, analytic and convergence controls, principal-symbol no-go, registry/dependency sync, and claim-boundary pass
- Added or changed: ADM evolution module, verifier, four artifacts, two source records, focused tests, Core exports, GH branch specification, parent gate, and dependency reporting
- Verified with: Minkowski and dust-FLRW controls; lapse/shift second-order convergence; five-direction principal-symbol audit; invalid-input controls; focused curved 3+1 tests
- Result: `CORE_CURVED_3P1_ADM_EVOLUTION_RHS_READY` is `CLOSED_FOR_LANE`; fixed-geodesic ADM is `CLOSED_AS_NO_GO`; GH is selected but not implemented; Gravity remains blocked
- Blocker narrowed: open-ended gauge/evolution work is reduced to `curved_3p1_generalized_harmonic_evolution_constraint_damping_and_propagation_missing`
- Still open: GH characteristic fields, time integration/CFL, constraint damping/propagation, temporal convergence, constraint-preserving boundaries, Topic 13 stress-energy projection, and SI observables
- Next controller: `curved_3p1_generalized_harmonic_evolution_constraint_damping_and_propagation_missing`
- Claim impact: no promotion to a well-posed numerical-relativity solver or Gravity compatibility

### 2026-08-28 - Close the periodic spatial geometry operator lane

- Scope: Core curved 3+1 periodic single-chart differential geometry and ADM-input integration
- Wave type: formula pass, numerical implementation, analytic-control/convergence gate, negative-control gate, registry/dependency sync, and claim-boundary pass
- Added or changed: periodic-grid Levi-Civita/Ricci/divergence module, verifier, formula and verification artifacts, focused tests, Core exports, parent gate, registry addendum, source scope, and dependency reporting
- Verified with: flat exact-zero control; conformally-flat analytic Ricci control; manufactured off-diagonal-`K` divergence control; three-resolution spatial convergence; ADM adapter and negative matter/spacing controls; focused curved 3+1 tests
- Result: `CORE_CURVED_3P1_GEOMETRY_OPERATOR_READY` is `CLOSED_FOR_LANE`; Ricci observed orders are `1.9660, 1.9914`, divergence orders are `1.9852, 1.9963`; parent remains `PARTIAL` and Gravity remains `BLOCKED_DEPENDENCY`
- Blocker narrowed: `metric_to_ricci_operator` and periodic covariant momentum-divergence implementation are now `PASS` with second-order spatial convergence
- Still open: lapse/shift gauge, metric/extrinsic-curvature evolution, strong hyperbolicity, constraint propagation/damping, temporal convergence, non-periodic boundaries/multiple charts, Topic 13 stress-energy projection, and dimensional observables
- Next controller: `curved_3p1_gauge_evolution_hyperbolicity_and_constraint_propagation_missing`
- Claim impact: Class B retained; no continuum proof, numerical-GR validation, Einstein-equation derivation, Gravity unlock, or global promotion
- Workflow linkage: second post-Topic-13 Core hardening wave under the F0-F8 and major-result contracts

### 2026-08-28 - Add the curved 3+1 ADM constraint interface

- Scope: Core curved 3+1 parent, standard ADM initial-value constraints, analytic controls, and dependency reporting
- Wave type: formula/source pass, artifact pass, negative-control gate, unit/ontology audit, and dependency-boundary pass
- Added or changed: ADM constraint module, Gourgoulhon source record, strict verifier, verification/formula/parent-gate/register-addendum artifacts, focused tests, Core exports, and major-result/dependency integration
- Verified with: `audit_uet_curved_3p1_constraints.py`, focused ADM tests, major-result register regeneration, dependency-gate regeneration, and Core regression
- Result: `CORE_CURVED_3P1_ADM_CONSTRAINT_INTERFACE_READY` is `CLOSED_FOR_LANE`; `CORE_CURVED_3P1_OBSERVABLE_PARENT_READY` is `PARTIAL`; Gravity remains `BLOCKED_DEPENDENCY`
- Blocker narrowed: `curved_3p1_dynamical_metric_and_gr_constraints_not_implemented` is split into a passing algebraic ADM constraint interface and named open differential-geometry/evolution/gauge/propagation requirements
- Still open: metric-to-Ricci and covariant-divergence grid operators, gauge choice, metric/extrinsic-curvature evolution, strong hyperbolicity, constraint propagation/damping, convergence, Topic 13 stress-energy projection, and dimensional observables
- Next controller: `curved_3p1_differential_geometry_evolution_gauge_and_constraint_propagation_missing`
- Claim impact: Class B retained; no Einstein-equation derivation, numerical-GR validation, Gravity unlock, or global claim promotion
- Workflow linkage: first post-Topic-13 Core hardening wave under the major-result closure/dependency contract

### 2026-07-23 - Derive finite-density O(2) EOS and lock the T=0 Kubo boundary

- Scope: homogeneous signed-charge EOS, canonical Legendre transform, response reciprocity, covariant T=0 pure-superfluid current/stress, and longitudinal Kubo/entropy/causal interface
- Wave type: formula derivation, deterministic artifact pass, negative comparator gate, source-role packaging, claim-boundary pass, and monotonic-state repair
- Added or changed: two core modules and public exports, one research spec, three new source records plus the existing Jain-Kovtun record, four generated Wave 10 artifacts plus the shared program gate, focused/alignment tests, and Wave 9/10 monotonic generator hooks
- Verified with: strict Wave 10 audit; 26 focused EOS/transport/artifact tests; 64 GR/state-map monotonic regression tests
- Final core regression: `384/386` passed; the two remaining failures are the pre-existing flattened time-dependent Noether shape mismatch (`1000` field values versus `100` coordinate values) already quarantined from proof use
- Result: EOS audit `PASS`, transport audit `PASS`, formula audit `WARN`, transport contract/program gate `BLOCKED`; stationarity residual `3.55e-15`, maximum grand-canonical derivative residual `1.06e-9`, first-law residual `2.22e-11`, inverse-susceptibility finite-difference residual `3.18e-9`, Lorentz residual below `1e-10`, and non-negative synthetic entropy production
- EOS layer: `q=Z*mu^2-m_eff^2>0` gives the tree-level condensed branch, stable signed canonical inversion, susceptibility, sound speed, and reciprocal fixed-`mu`/fixed-`n` response derivatives
- Comparator result: the fixed `-1<=C<=1` exact-EOS versus symmetric-double-well relative residual is `1.0`, so the double well remains constitutive and is not accepted as action-derived
- Transport layer: action-derived current/stress are restricted to the T=0 pure-superfluid sector; a finite-temperature normal component is not inferred
- Dissipative boundary: Kubo records have no numerical defaults; synthetic controls require explicit opt-in and cannot count as physical coefficient evidence
- Blocker narrowed: the broad EOS/transport-matching blocker is replaced by physical Kubo coefficient evidence, full finite-temperature/superfluid transport closure, covariant coarse graining, and curved 3+1 evolution
- Still open: physical correlator extraction, finite-temperature normal component, complete superfluid transport tensor, SK/KMS derivation, gradient-EFT `kappa_C`, SI map, covariant coarse graining, curved 3+1 solver, and external physical validation
- Next controller: `physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing`
- Claim impact: class B retained; program remains `BLOCKED`; Topic 0.11 and Topic 0.19 receive no status promotion; global-universe closure remains `UNRESOLVED`
- Provenance boundary: Son, Chapman-Hoyos-Oz, Jain-Kovtun, and Haehl-Loganayagam-Rangamani constrain EFT/Kubo/readiness roles only; they do not derive UET coefficients or validate UET

### 2026-07-22 - Factor the Noether-charge to phase-field state map

- Scope: signed O(2) Noether charge, frame-projected/coarse hydrodynamic variables, normalized phase-field coordinates, and the equation-of-state/transport dependency boundary
- Wave type: ontology repair, exact coordinate derivation, non-invertibility falsification, primary-source provenance, formula audit, dependency-gate, and monotonic-state pass
- Added or changed: state-map module and public exports, Cahn-Hilliard and Hohenberg-Halperin source records, strict verifier, three generated Wave 9 artifacts plus the shared program gate, focused/alignment tests, monotonic upstream logic, specification, update log, and work ledger
- Verified with: nine strict audits in dependency order and a 309-test trace, matter-space/pilot, legacy-alignment, covariant, sourced-comparator, fixed-cone, and state-map regression suite
- Result: audit `PASS`, evidence `PARTIAL_HYDRODYNAMIC_STATE_COORDINATE_MAP`, formula audit `WARN`, dependency/program gates `BLOCKED`; 64 random cases gave affine round-trip error `6.66e-16`, continuity-scaling error `3.55e-15`, external-coordinate round-trip error `7.11e-15`, free-energy derivative error `1.28e-9`, and polar-current identity error `5.55e-17`
- Non-invertibility result: two distinct O(2) states produced the same current within `8.88e-16` while their state distance was `1.06`; two distinct sub-cell profiles produced exactly the same coarse averages while differing by `1.0`
- Exact layer: at fixed declared scales, `C=(n_bar-n_ref)/n_scale` and `J=j_bar/(n_scale L/T)` are bijective and preserve the continuity residual exactly
- Constitutive layer: `f=n_scale*mu_scale*(C^2-1)^2/4` gives `df/dn_bar=mu_scale*(C^3-C)` and normalized local coefficients `a=-1`, `b=+1`; this equation of state is not derived from the O(2) action
- Blocker narrowed: microscopic inversion is rejected as a category error; the controlling unknown is now the signed-charge equation of state, covariant coarse-graining, susceptibility, and transport matching
- Still open: equation of state from the covariant O(2) matter action, covariant hydrodynamic matching, entropy-current/dissipative-Bianchi closure, CTP/KMS completion, curved 3+1 solver, SI map, external numerical replication, and physical validation
- Next controller: `noether_charge_equation_of_state_and_covariant_transport_matching_missing`
- Claim impact: class B retained; program remains `BLOCKED`; Topic 0.11 and Topic 0.19 status remain unchanged; global-universe closure remains `UNRESOLVED`
- Ontology boundary: the variable is signed O(2) charge, not established mass or particle number; external `varphi` is not UET `Phi`; trace is absent and cannot feed back
- Provenance boundary: Cahn-Hilliard 1958 and Hohenberg-Halperin 1977 are metadata/full-text-inspection role sources only; neither derives the UET state map, matter equation of state, or transport coefficients

### 2026-07-22 - Derive fixed-light-cone feasibility and isolate the covariant state-map blocker

- Scope: normalized analytic feasibility over `|C| <= 1.25`, exact local `J=q/tau` current-law mapping, and covariant/thermal transport readiness boundaries
- Wave type: formula derivation, negative-limit control, primary-source provenance, claim-boundary, dependency-gate, and monotonic-state pass
- Added or changed: fixed-cone bridge module and public exports, two relativistic-transport source records, strict verifier, three generated Wave 8 artifacts, focused/alignment tests, monotonic upstream hook, regenerated GR-chain artifacts, specification, update log, and work ledger
- Verified with: eight strict audits in dependency order and a 275-test trace, matter-space, legacy-alignment, covariant, sourced-comparator, and causal-feasibility regression suite
- Result: audit `PASS`, evidence `PARTIAL_ANALYTIC_CAUSAL_BRIDGE`, formula audit `WARN`, covariant mapping gate `BLOCKED`; 64 random feasible controls matched the analytic speed bound with residual `0.0`, all negative controls were rejected, and the local current-law residual was `1.33e-15`
- Fixed-cone result: strict domain hyperbolicity requires `alpha>1`; the exact normalized bounds are `tau >= (alpha+3*C_max^2-1)/c_hat^2` and `beta >= gamma/c_hat^2`
- No-common-limit result: at fixed finite `c_hat`, `alpha->infinity` forces the causal lower bound on `tau` to diverge, so it cannot also satisfy the exact parabolic target `tau->0`; this result is restricted to the declared comparator
- Tradeoff control: quasistatic chemical error fell from `4.39e-2` to `7.89e-4` while the minimum fixed-cone `tau` rose from `11.6875` to `515.6875`; the source scaling remained outside the cone at every sampled point
- Blocker narrowed: the external `q` law maps exactly to the mobility-one local Maxwell-Cattaneo law, but external order parameter `C` is not yet mapped to the conserved UET Noether density
- Still open: Noether-density/order-parameter state map, UET-native covariant phase-field action, entropy-current and dissipative-Bianchi closure, CTP/KMS transport matching, curved 3+1 well-posedness, SI mapping, external numerical replication, and physical validation
- Next controller: `noether_density_to_phase_field_order_parameter_map_missing`
- Claim impact: class B retained; program remains `BLOCKED`; Topic 0.11 and Topic 0.19 status remain unchanged; global-universe closure remains `UNRESOLVED`
- Ontology boundary: source auxiliary `varphi` is not UET `Phi`, information, or trace; derived trace remains absent from and cannot feed back into the physical map
- Provenance boundary: Jain-Kovtun 2024 and Crossley-Glorioso-Liu 2017 DOI/arXiv identities, formula/readiness locators, temporary-source hashes, units, and claim roles are recorded; their TeX archives are not redistributed


### 2026-07-22 - Source and audit a first-order hyperbolic phase-field comparator

- Scope: formula-level transcription of the Dhaouadi-Dumbser-Gavrilyuk first-order hyperbolic Cahn-Hilliard system into an isolated normalized 1D periodic comparator
- Wave type: primary-source provenance, formula transcription, Lyapunov/constraint closure, characteristic, singular-limit, dependency-gate, and claim-boundary pass
- Added or changed: external source record, comparator module and public exports, strict verifier, three generated artifacts, focused/alignment tests, shared monotonic-stage policy, regenerated upstream artifacts, and specification/controller updates
- Files touched: `uet_hyperbolic_phase_field.py`, its source record/audit/tests/artifacts, core exports/specification/log, the prior diffusion/reduction controller contracts, six upstream audits and alignment tests, and the shared program gate
- Verified with: seven strict audits in dependency order and a 235-test trace, matter-space, legacy, covariant, diffusion, and hyperbolic-comparator regression suite
- Result: audit `PASS`, evidence `PARTIAL_EXTERNAL_COMPARATOR`, formula audit `WARN`; mass residual `2.22e-17`, energy closure `4.34e-18`, characteristic-eigenvalue error `2.22e-16`, cone leakage/arrival error `0.0`, and quasistatic chemical-limit order `0.968`
- Blocker narrowed: a sourced first-order fixed-parameter hyperbolic phase-field comparator now exists and closes its periodic semi-discrete mass, Lyapunov, constraint, and principal-speed identities
- Still open: UET-native covariant derivation, mapping of the comparator order parameter to the coarse-grained Noether density, uniformly subluminal Cahn-Hilliard recovery, CTP/KMS transport matching, dissipative Bianchi closure, curved 3+1 evolution, SI mapping, numerical benchmark replication, and physical validation
- Next controller: `uniform_subluminal_hyperbolic_phase_field_and_covariant_mapping_missing`
- Claim impact: class B retained; program remains `BLOCKED`; Topic 0.11 and Topic 0.19 status remain unchanged; global-universe closure remains unresolved
- Workflow linkage: the provenance audit locks DOI/arXiv identity and formula locators while the formula audit keeps external transcription separate from UET derivation
- Notes: the source auxiliary `varphi` is not UET `Phi`; fixed-parameter hyperbolicity is not automatically subluminal, and the paper scaling drives maximum sampled speed from `10.0` to `249.8` as `gamma` falls from `0.2` to `0.025`
- Provenance boundary: the arXiv source archive was inspected temporarily and hashed but is not redistributed; the publisher PDF was blocked by a JavaScript/cookie challenge and is not claimed as parsed

### 2026-07-22 - Add conserved-current bridge and restrict causal scope

- Scope: local-frame decomposition of the O(2) Noether current into a coarse-grained conserved density and spatial current in a normalized 1D constitutive lane
- Wave type: formula-closure, discrete-conservation, energy-ledger, adiabatic-limit, principal-symbol, and claim-boundary pass
- Added or changed: covariant diffusion module, public exports, strict verifier, three generated artifacts, focused tests, monotonic upstream gates, and specification/reduction drift repair
- Files touched: `uet_covariant_diffusion.py`, its audit and tests, public exports, diffusion/program artifacts, upstream audits/tests/artifacts, the reduction contract, and this specification/log
- Verified with: six strict audits in dependency order and a 164-test combined covariant, causal, reduction, matter-action, diffusion, legacy-alignment, and matter-space regression suite
- Result: audit `PASS`, evidence `PARTIAL`, formula audit `WARN`; mass residual at most `5.55e-17`, energy-identity residual at most `2.88e-16`, Model-B limit residual at most `2.27e-13`, matter-space RHS mismatch `0.0`, exact-null-branch response mismatch `0.0`, and local-cone leakage/arrival error `0.0`
- Blocker narrowed: the regular covariant-to-diffusive map closes only as a declared coarse-grained constitutive-current bridge with an exact semi-discrete Model-B limit
- Still open: microscopic amplitude-to-charge-density matching, first-order hyperbolic closure for gradient/spinodal phase fields, closed-time-path/KMS coefficient matching, dissipative Bianchi closure, curved 3+1 reduction, SI mapping, and physical validation
- Next controller: `first_order_hyperbolic_phase_field_uv_closure_missing`
- Claim impact: class B retained; program remains `BLOCKED`; Topic 0.11 and Topic 0.19 status remain unchanged; global-universe closure remains unresolved
- Workflow linkage: the formula and claim audits separate the causal local-convex control from the fourth-order ultraviolet obstruction in the full Cahn-Hilliard lane
- Notes: finite flux relaxation alone does not make the gradient/spinodal equation relativistically causal; the trace remains derived and has no feedback, and no scalar amplitude is identified with density

### 2026-07-22 - Add conservative covariant matter-action pilot

- Scope: one complex scalar represented by an O(2) real doublet, coupled reciprocally to the covariant response scalar through one conservative action
- Wave type: formula-closure, action-reciprocity, current-conservation, dependency-gate, and claim-boundary pass
- Added or changed: covariant matter module, exact interaction derivatives, O(2) Noether current identity, coupled metric residual, strict verifier, three generated artifacts, focused tests, public exports, and monotonic upstream generators
- Files touched: `uet_covariant_matter.py`, `audit_uet_gr_covariant_matter.py`, core exports, two matter test files, generated matter/program artifacts, upstream audits/tests, and this specification/log
- Verified with: five strict audits in dependency order and a 129-test combined covariant, causal, reduction, matter-action, legacy-alignment, and matter-space regression suite
- Result: audit `PASS`, evidence `PARTIAL`, formula audit `WARN`; reciprocal finite-difference error `1.77e-13`, Noether identity and on-shell current-divergence errors `0.0`, tensor transformation error `6.94e-18`, and exact `epsilon_nc = 0` interaction residual `0.0`
- Blocker narrowed: a conservative scalar pilot now derives reciprocal response/matter coupling and an on-shell O(2) current from the same action
- Still open: amplitude-to-density identification, regular covariant-to-diffusive reduction, Cahn-Hilliard/closed-time-path derivation, coupled Bianchi identity with the new matter action, SI map, and particle or antimatter identification
- Next controller: `regular_covariant_to_diffusive_matter_reduction_missing`
- Claim impact: class B retained; program remains `BLOCKED`; Topic 0.11 and Topic 0.19 status remain unchanged
- Workflow linkage: the formula and claim audits separate exact conservative identities from the still-missing dissipative constitutive bridge
- Notes: the conserved O(2) charge is not yet the normalized matter field `C`; it establishes neither global-universe closure nor a particle-species interpretation

### 2026-07-22 - Map the covariant response sector to the normalized matter-space operator

- Scope: declared local-rest-frame and weak-curvature reduction of the response equation only
- Wave type: controlled-reduction, formula-map, dependency-gate, and claim-boundary pass
- Added or changed: exact coefficient/scaling map, reduction adapter, strict verifier, generated reduction contract, focused tests, public exports, and monotonic upstream generators
- Files touched: `uet_covariant_reduction.py`, `audit_uet_gr_weak_field_reduction.py`, core exports, two reduction test files, generated reduction artifacts, upstream audits/tests, and this specification/log
- Verified with: four strict audits in dependency order and a 110-test combined covariant, causal, reduction, legacy-alignment, and matter-space regression suite
- Result: audit `PASS`, evidence `PARTIAL`; response-acceleration mismatch `8.33e-17`, mapped speed error `0.0`, matter template preserved, and the `epsilon_nc = 0` adapter branch rejected
- Blocker narrowed: `controlled_covariant_to_matter_space_reduction_missing` is closed only for the response-sector coefficient map
- Still open: covariant matter action, reciprocal matter coupling, derivation of the required causal source, curved 3+1 reduction, principal/ghost analysis, SI map, and physical validation
- Next controller: `covariant_matter_action_and_reciprocal_coupling_missing`
- Claim impact: class B retained; program remains `BLOCKED`; Topic 0.11 and Topic 0.19 status remain unchanged
- Workflow linkage: formula and claim audits force the partial result to remain distinct from a full coupled derivation
- Notes: no derived trace feeds back; the reduction is disabled at the exact GR null branch and does not establish global-universe non-closure

### 2026-07-21 - Add restricted causal non-closed constitutive kernel

- Scope: retarded source history on a declared 1+1-dimensional local rest-frame slice
- Wave type: causal-support, characteristic, exchange, and claim-boundary pass
- Added or changed: exact telegraph Green evaluator, event-history convolution, causal exchange adapter, strict verifier, formula/contract artifacts, public API, tests, and monotonic upstream gates
- Files touched: `uet_covariant_nonclosed.py`, `audit_uet_gr_causal_nonclosed.py`, two focused test files, core exports, generated artifacts, and upstream generators/tests
- Verified with: strict causal audit, 20 focused tests, and a 92-test combined covariant/causal/legacy/matter-space regression suite
- Result: outside-cone leakage `0.0`, arrival error `0.0`, coordinate-scalar error `2.22e-16`, future-event influence `0.0`, and exchange closure `0.0`
- Blocker narrowed: a causal constitutive source exists on the restricted local slice
- Still open: closed-time-path derivation, curved 3+1 Green solver, parent-action ghost analysis, observable source map, controlled reduction, and physical validation
- Next controller: `controlled_covariant_to_matter_space_reduction_missing`
- Claim impact: class B retained; causal result is a constitutive ansatz and Topic 0.19 remains unchanged
- Notes: the physical source `j_phi` is not the derived trace `R`; global-universe closure remains unresolved

### 2026-07-21 - Close the conservative covariant exchange identity

- Scope: `docs/core` Noether/Bianchi identity and exchange-completed local ledger
- Wave type: derivation, gate, and claim-boundary pass
- Added or changed: covariant balance module, strict symbolic/numeric verifier, exchange contract, public exports, focused tests, and monotonic upstream generator behavior
- Files touched: `uet_covariant_balance.py`, `audit_uet_gr_covariant_balance.py`, two focused test files, core exports, generated artifacts, and prior closed-limit generator/tests
- Verified with: strict balance audit and a 72-test combined covariant, legacy-alignment, and matter-space regression suite
- Result: symbolic identity exact; numeric identity difference `1.39e-17`; exchange and sourced-shell closure `0.0`
- Blocker narrowed: `covariant_bianchi_exchange_balance_missing` is closed for the local candidate identity scope
- Still open: no causal source kernel, influence functional, curved-derivative solver, global energy theorem, characteristic analysis, or physical validation
- Next controller: `causal_nonclosed_influence_functional_missing`
- Claim impact: class B retained; program and Topic 0.19 remain blocked
- Notes: matter-number conservation remains an independent equation and global-universe closure remains unresolved

### 2026-07-21 - Implement conservative covariant parent and exact GR null limit

- Scope: `docs/core` covariant response formula evaluator and generated evidence
- Wave type: formula-closure and exact-limit verification pass
- Added or changed: natural-unit scalar-response action evaluator, tensor residuals, public exports, verifier, focused tests, and three generated artifacts
- Files touched: `uet_covariant_response.py`, `__init__.py`, `audit_uet_gr_closed_limit.py`, two focused test files, and core artifacts
- Verified with: strict generated audit and a 61-test covariant, legacy-alignment, and matter-space regression suite
- Result: exact GR closed-limit residual `0.0`; local tensor-transformation error `2.22e-16`; 61 tests passed
- Blocker narrowed: `covariant_parent_action_missing` is closed for the candidate formula-evaluator scope
- Still open: no Bianchi/exchange identity, causal influence functional, characteristic analysis, metric PDE solver, SI map, or physical GR validation
- Next controller: `covariant_bianchi_exchange_balance_missing`
- Claim impact: model evidence advances to class B; program and Topic 0.19 promotion remain blocked
- Notes: `epsilon_nc` is a nesting parameter, not a percentage openness; global-universe closure remains unresolved

### 2026-07-21 - Quarantine legacy Lorentz and Noether proof exports

- Scope: `docs/core/uet_lorentz.py`, `docs/core/uet_noether.py`, and generated alignment evidence
- Wave type: gate pass and claim-boundary pass
- Added or changed: explicit legacy evidence-status constants, removed completion banners, source audit, regression tests, and machine-readable alignment gate
- Files touched: `uet_lorentz.py`, `uet_noether.py`, `docs/scripts/audit/audit_uet_gr_legacy_alignment.py`, `test/test_gr_legacy_alignment.py`, `artifacts/legacy_covariance_alignment_gate.json`
- Verified with: `python docs/scripts/audit/audit_uet_gr_legacy_alignment.py --print-summary --strict` and `python -m pytest docs/core/test/test_gr_legacy_alignment.py -q`
- Result: audit `PASS`; physical covariance evidence `BLOCKED`; 5 tests passed
- Blocker narrowed: legacy PASS labels can no longer be exported as Lorentz, curved-spacetime, Noether, or Einstein-equation evidence
- Still open: six field-transform methods alias the original field; curved metrics are not wired; Noether diagnostics use an ad hoc spatial update
- Next controller: `covariant_parent_action_missing`
- Claim impact: wording narrowed; no readiness or evidence upgrade
- Workflow linkage: formula and claim audit applied before creating the replacement parent
- Notes: the legacy APIs remain available for compatibility and code archaeology
- Regression note: the broader legacy suite retains two failures in its time-dependent Noether case because a 1,000-point flattened field is combined with a 100-point coordinate vector; this pre-existing path remains outside proof use

### 2026-07-21 - Lock closure taxonomy and GR null hypothesis

- Scope: core ontology and research contract
- Wave type: claim-boundary pass
- Added or changed: research specification, ontology contract, claim gate, and
  handoff from the normalized matter-space prototype
- Files touched: `UET_GR_NONCLOSED_RESEARCH_SPEC.md`,
  `artifacts/gr_nonclosed_ontology_contract.json`,
  `artifacts/gr_correspondence_claim_gate.json`
- Verified with: JSON parse and focused document/claim review
- Result: `PASS` for ontology visibility; program remains `BLOCKED`
- Blocker narrowed: `universe_open_wording_ambiguous` is replaced by separate
  matter-number, stress-exchange, GR-limit, and global-closure states
- Still open: no covariant parent action or generated GR-limit artifact exists
- Next controller: `covariant_parent_action_missing`
- Claim impact: wording narrowed; no evidence or readiness upgrade
- Workflow linkage: applies the shared hardening and formula-audit standards
- Notes: global closure is explicitly unresolved; `epsilon_nc = 0` is the GR
  null model and `epsilon_nc != 0` remains an empirical hypothesis
