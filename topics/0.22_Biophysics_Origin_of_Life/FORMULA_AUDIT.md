# Formula Audit: 0.22 Biophysics & Origin of Life

Audit status: registered relations T22-001 through T22-018 are catalogued below. T22-013 through T22-018 are Wave-0 candidate mappings only; none is promoted to a formal proof or universal biological law by this package.

| ID | Ontology and relation | Variables / units | Conversion and unit closure | Parameter origin / derivation | Observable and code/artifact link | Status and failure mode | Next hardening |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T22-001 | Biophysical Omega score from normalized biological/neural field | C normalized field; Omega dimensionless; dx grid spacing | Normalization hides raw units and preprocessing; no SI closure | Inherited UET engine relation; model score | Legacy Engine_Biophysics.py; no active artifact | Model relation; not an observable identity | Add dataset preprocessing and raw-input identity |
| T22-002 | S_internal += decay_rate - information_intake | S_internal normalized proxy; decay_rate=phi_loss/I_max; information_intake=beta/I_max | Dimensionless ledger; no environment entropy or energy conversion | Topic/UET parameter heuristic; not external biology constant | Legacy Engine_Life_Entropy.py; no active artifact | Heuristic bridge; not living thermodynamics | Add open-system entropy ledger and Topic 0.13 link |
| T22-003 | S_internal >= max(0.01, 1-kappa) | Normalized proxy; kappa topic coefficient | Numerical clamp only; no physical lower-bound derivation | Topic numerical guardrail | Legacy life-entropy engine | Heuristic clamp can manufacture apparent pass behavior | Keep explicitly numerical, not biological |
| T22-004 | Entropy_Reduction=(Omega_random-Omega_life)/(Omega_random+1e-9) | Omega dimensionless; reduction fraction dimensionless | Ratio closed as a proxy fraction only | Random field versus imposed sinusoidal field | Legacy origin/DNA scripts | Pattern is imposed, not emergent chemistry | Replace with source-backed reaction-network gate |
| T22-005 | Neural diversity as std(state) after mean-field synchronization | Diversity dimensionless; coupling dimensionless | Synthetic state has no EEG unit contract | Topic-local generator; simulation relation | Legacy neural scripts | Not EEG evidence without source windows | Add raw-window, phase-label, and held-out gate |
| T22-006 | EEG reference band powers, synchrony, and variance | Band powers and synchrony dimensionless; variance proxy | Depends on raw signal units and preprocessing, both open | Source-referenced local summary | seizure_phase_data.json; provenance only | Local reference, not raw source | Freeze raw records, preprocessing, and hashes |
| T22-007 | stability=1/(1+variance) | Variance in arbitrary synthetic expression units; stability dimensionless | Closed only within synthetic matrix; no clinical unit map | Seeded synthetic positive-control generator | Active biomarker verifier and WARN artifact | Class-C diagnostic; not clinical evidence | Compare with source-backed expression matrix and baseline |
| T22-008 | dC/dt=-beta I+kappa laplacian(C) proxy | C normalized coherence; I pressure proxy; engine time step | No biological calibration or SI closure | UET engine/topic proxy | Legacy cancer-cell script | Heuristic bridge; synthetic threshold risk | Tie to real omics/cell-state data |
| T22-009 | C=1/(1+0.1 mean(var(expression))) | Expression units depend on assay; C dimensionless | Coefficient 0.1 lacks source/unit derivation | Mock matrix with TCGA source target | Legacy TCGA script; figure only | Mock data is not TCGA analysis | Add real matrix, assay units, cohort, baseline |
| T22-010 | `E_HP = -sum(1)` over H-H pairs with Manhattan distance 1 and residue-index gap > 1 | `sequence_i` is H/P; `r_i` is an integer coordinate in `Z^2`; `E_HP` is dimensionless HP model units | Closed within the finite lattice model; the `-1` term is a benchmark anchor, not SI energy or protein free energy | Topic-declared HP contact rule; `-1` is `benchmark_anchor`; exhaustive enumeration is exact only for the declared finite search space | `Code/03_Research/Research_Protein_Folding_HP_Benchmark.py`; `Result/artifacts/0_22_protein_folding_hp_benchmark.json` | Model definition and checked local benchmark; no biological correspondence, solvent, temperature, side-chain, or experimental mapping | Add a governed source-backed structure benchmark and independent replication only if the lane expands beyond the finite HP model |
| T22-011 | sum(I_field)/(std(C_field)+1e-9) | Normalized fields; complexity dimensionless | Proxy ratio only; no chemical concentration conversion | Topic-local heuristic | Legacy protocell script; data/artifact incomplete | No emergent chemistry closure | Source-lock prebiotic yields and write artifact |
| T22-012 | T-cell/cancer/clinical strategy scores | Mixed normalized scores; units vary | No common unit contract or endpoint mapping | Topic-local virtual subjects and heuristics | Legacy immune/clinical scripts | Biomedical claims not independently gated | Split lanes, define endpoints, governed data and baseline |

T22-010 derivation note: `derivation_class=model_definition_with_exact_finite_oracle`; `constant_origin=benchmark_anchor`; `proof_status=checked_local_benchmark`; `standard_physics_correspondence=open`.

The exact oracle closes only the finite declared lattice search. It does not close atomistic forces, solvent effects, temperature, side-chain chemistry, native-state free energy, or a biological measurement operator.


## Protein-folding dynamics candidate formulas

The following entries are registered for the new lane but are not executed by
the Wave-0 preflight. They are candidate mappings, not atomistic laws or
closed free-energy relations.

| ID | Ontology and relation | Variables / units | Conversion and unit closure | Parameter origin / derivation | Observable and code/artifact link | Status and failure mode | Next hardening |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T22-013 | X_micro -> C_l lane-specific coarse graining from atomistic coordinates to contact, secondary-structure, compactness, and native-basin coordinates | X_micro has source/runtime coordinate units; each C_l component must declare dimensionless, length, angle, or rate units | Open until topology, frame convention, residue mapping, stride, and information-loss report are frozen | topic_derived_relation; adapter not yet implemented | Future dynamics adapter; Wave-0 gate artifact only | Candidate/open; failure if C_l is treated as universal UET coordinate or if hidden normalization changes its meaning | Implement adapter with explicit state schema, residue mapping, and synthetic unit tests |
| T22-014 | Omega[C,Phi] candidate effective folding landscape/readout | C_l lane-specific; Phi candidate response; coefficients require declared energy or normalized lane | Open; not SI free energy and not a force until dimensional closure is complete | heuristic_bridge using existing UET effective-functional family; no new core axiom | Future readout/coupling comparison; no current result artifact | Candidate/open; failure if normalized ledger is called free energy or used as atomistic force without mapping | Declare standard-physics correspondence, coefficients, uncertainty, and observable mapping |
| T22-015 | K_R(t)=theta(t) exp(-t/tau) L/tau candidate memory kernel for solvent/chaperone/history | t and tau require time units; L and response/force units depend on the selected lane | Open; kernel normalization is mathematical only until physical response units are assigned | topic_derived_relation from existing linear open-system control; not microscopic protein derivation | Future memory readout and ablation artifact | Candidate/open; failure if classical linear memory is presented as cellular microscopic transport | Fit or source-lock a response observable and audit causality, PSD, and uncertainty |
| T22-016 | J_translation + J_chaperone + J_environment exchange-channel decomposition | Each J must declare whether it is count rate, mass/particle flux, energy/power, or normalized diagnostic | Open; no mixing of ATP turnover, residue emergence, solvent exchange, and normalized ledger | heuristic_bridge; channel ontology not yet source-locked | Future co-translational/chaperone state-transition artifact | Candidate/open; failure if exchange is treated as closed equilibrium or hidden feedback | Freeze channel definitions, units, source records, and non-equilibrium transition rule |
| T22-017 | P_C=eta_C (dC/dt)^2 plus persistence/failure ledger | P_C remains normalized path-cost unless eta_C and C are physically mapped | Open; not measured power, heat, or entropy production | Existing UET persistence candidate; heuristic_bridge | Future persistence, misfolding, aggregation, or basin-exit readout | Candidate/open; failure if path-cost is called physical power or a universal optimizer | Map to work/heat/transition/failure observable with uncertainty and baseline |
| T22-018 | dP(z,t)/dt = sum[k(z'->z)P(z') - k(z->z')P(z)] kinetic transition/readout operator | P is probability; k has inverse-time units; z is declared conformational/cellular state | Closed only as a probability-conservation identity when rates are valid; physical rate mapping remains open | topic_derived_relation / open kinetic model; detailed balance is conditional and not global in cellular lanes | Future MFPT, survival/hazard, folding probability, and holdout artifact | Candidate/open; failure if rates are fitted retrospectively or detailed balance is imposed on ATP-driven lanes | Define state discretization, rate provenance, holdout policy, and transition uncertainty |

Wave-0 formula gate status: BLOCKED. No entry above supports atomistic
results, biological folding claims, PDB/CASP validation, AlphaFold
replication, or external replication.

## Formula readiness vocabulary

| Label | Meaning |
| :-- | :-- |
| derived_relation | Algebraic relation implemented from declared assumptions; not automatically a physical derivation |
| heuristic | Topic/model rule whose physical or biological mapping remains open |
| calibration | Parameter fit or mapping requiring a declared source and uncertainty |
| placeholder | Mechanics or mock relation retained for future gate work |

## Guardrails

- Normalized ledgers are not SI energy, entropy, temperature, heat flux, or clinical risk.
- A source record is not a measurement and a local summary is not raw data.
- The synthetic stability relation supports only the class-C internal diagnostic artifact.
- A simulated field with an imposed pattern is not emergent chemistry.
- No formula in this registry closes external validation or topic promotion.
- The exact HP optimum is an oracle for the declared finite lattice model only; it is not a native protein state or a physical free-energy minimum.
