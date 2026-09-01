# Limitations

## Transition-Rate Dimension Boundary (2026-09-01)

Conservation, PSD and algebraic resolvent checks do not repair a dimensional
mismatch. The current finite-channel operator cannot be interpreted as a
frequency, width or physical relaxation rate. Its absolute `1e-14` eigenmode
cutoff is also not energy-scale covariant. Historical response numbers remain
diagnostics and must not be globally rescaled into physical rates.

## Dressed Pair/Rung Boundary (2026-09-01)

The RA-pair calculation assumes a narrow positive-energy quasiparticle pole
with a positive width. It proves normalization, not the physical value of the
width. The width must be obtained from the same charge-resolved four-point
kernel used in the ladder. Legacy finite-channel results cannot be repaired
by a universal factor because `Phi` exchange is channel and kinematics
dependent. Number-changing and response channels also remain open.

## Retarded/Advanced Proper-Vertex Scope (2026-09-01)

The declared RA result is the proper bare+mixed+vacuum three-point function.
It excludes the response-relaxed bath insertion and does not yet attach
dressed external propagators. Its finite zero-transfer limit therefore does
not contradict transport pinch resummation: the pinch pair belongs to the
current-current correlator and ladder equation. `eta` is an analytic
continuation control, not a collision width or fitted damping rate.

## Microscopic Current/Ladder Matching Boundary (2026-09-01)

The exact tree source match does not license inserting the new one-loop vertex
into older kinetic artifacts without an explicit action/state configuration.
Their defaults differ in matter quartic, response coupling, `epsilon_nc`, and
response mass. The audit supplies a zero-residual configuration bridge but
does not rerun or promote those older finite-cutoff results.

Ward and static checks constrain only the longitudinal/static information.
They do not select a transverse analytic continuation, external-leg residue,
or microscopic four-point Bethe-Salpeter kernel. Existing resolvent identities
and Gram projections remain formal finite-cutoff interfaces, not substitutes
for those microscopic inputs.

## Static Confluent Vertex Scope (2026-09-01)

The static result uses the thermodynamic Euclidean `P=Q=0` order of limits.
It closes the coincident-pole density-source derivative at strict one loop,
not the collisionless retarded `omega,k -> 0` ordering. Spatial current is
zero by isotropy only at this declared point; no finite-k transverse form is
inferred from it.

The agreement with the static inverse-propagator derivative does not produce
a Kubo coefficient, collision ladder, heat current, entropy production,
material SI scale, or `alpha_Phi_K`. `R_gen` and `R_obs` remain excluded, and
the O(2) sign `q` is not core `C`. Full Topic 13 stays open.

## Explicit Current-Vertex Scope (2026-09-01)

The current result covers generic nonzero bosonic Matsubara transfer with
collinear external spatial momenta and full internal polar angle. Its static
confluent companion is now closed separately above. It has not been
analytically continued to a retarded transverse vertex, and it does not supply
a collision ladder, conductivity or heat-current Kubo coefficient.

Ward agreement alone would not verify the transverse bath insertion. That
piece is separately calculated and its continuum-shift transversality is
checked without projection. Its response-relaxed component results from
allowing the mean response displacement to follow the external source; it is
not silently relabeled as a proper multi-field 1PI triangle.

Off-shell vacuum/current components depend on the declared response-axis and
charged kinetic subtraction. Their relative sizes are not physical rates or
uncertainties. The full cubic/quartic/current counterterm match and static
renormalization remain open.

The Matsubara routing correction changes the representation of the earlier
independent witness, not its real pole, cuts, KMS relation, thresholds or
material boundary. No source, calibration, holdout, causal threshold or
collision artifact is changed.

## Charged Two-Point Matching (2026-09-01)

The new result closes only the declared normal k=0 charged two-point
calculation at strict one-loop order, including the mean-shift insertion.
The zero-mu integrated determinant witness and nonzero-mu fixed-momentum
Euclidean determinant do not establish a full finite-temperature phase diagram.

The evaluated real pole domain lies strictly between the Landau and pair
cuts. Cut-supported spectral functions are handled separately, not by adding
an arbitrary width. Positive-frequency cut routing currently declares m>=M0;
reversed mass ordering is rejected rather than guessed. Zero on-shell width
does not remove higher-order scattering or finite-k damping.

Temporal Ward reconstruction fixes only a longitudinal vertex requirement.
It does not close transverse/current vertices, physical Kubo coefficients,
collision resummation, full two-fluid transport or entropy-current balance.
Partial Dyson reuse is not the full next loop, and refinement differences
are not source or truncation uncertainty. The old collision artifact, causal
baseline, He-4/graphite distinction and Xie holdout remain unchanged.

## One-Loop Response Match (2026-09-01)

The new axis scheme includes vacuum subtraction missing from the thermal-only
result below, but it does not supply a complete charged-sector renormalized
action. Zero-field response self-energy and mean-shift loop orders are kept
separate. Neither the stationary one-loop functional nor a partial Dyson
root is an all-orders solution or an omitted-order uncertainty estimate.

The k=0 pair-cut KMS/FDT witness is not a full interacting SK/KMS or current
matching result. A zero on-shell one-loop width below the pair threshold
does not imply absence of higher-order collision damping. Finite-k transport,
collision resummation and full two-fluid/heat-current tensors remain open.
Static curvature cannot be substituted for a quasiparticle pole.

The 21.1% difference between stationary and strict mean at T=1 in the declared
natural-unit grid cautions against an unqualified high-T extrapolation.
Agreement of quadratures to displayed precision is not zero physical error.
The previous collision result, He-4 calibration, graphite source boundary,
Xie holdout and all causal thresholds are unchanged.

## Thermal-Only Stationary Background (2026-09-01)

The local normal-response minimum uses a fixed zero-temperature polynomial
plus the thermal one-loop determinant only. It does not supply vacuum
counterterms, a complete interacting gap equation, the charged/condensed phase
diagram or a renormalized finite-temperature effective action. A positive
response curvature and positive tree Bose gap are not full phase stability.

The next matching requirement is consistency at a declared approximation
order with disclosed truncation error, not an exact all-orders solution.

The previous zero-response collision result remains a fixed-background
control. Maintaining that background under the new thermal functional would
require an explicit holding-source contract; it is not automatically a
source-free thermal equilibrium. No earlier collision rate was overwritten.

Shifting the background induces a tree cubic vertex. Inserting only shifted
masses is inconsistent even with that shifted tree action. Including the
induced vertex alone still omits other thermal-loop corrections. Static
curvature is not a pole mass. Large pointwise squared-amplitude ratios near
comparator cancellations are not integrated rate enhancements or reliable
high-temperature predictions. No SI mapping, alpha calibration, holdout access
or physical dependency unlock follows from this diagnostic.

## Coupled Collision Scope (2026-09-01)

The new gain/loss operator covers seven reversible 2-to-2 reaction classes
only. Total quasiparticle count remains conserved in this truncation, not in
the full interacting action. On-shell collision energy/momentum balance is
not a full open-system ledger or a causal domain-of-dependence test.

Stable quadrature did not make the initial current basis adequate: adding
relative sector-momentum directions increased its projected charge response
by about 13.75 times at the reference state. The small changes under later
nested basis extensions are not a certified infinite-basis error bound.
The cutoff changes the incoming domain, not an invariant four-leg regulator;
the full reverse-paired integral is recovered only in the cutoff limit.

The normal tree background, finite-temperature self-energy, number-changing
channels, full Kubo/SK-KMS/current matching, physical heat frame and material/SI
calibration remain open. He-4 calibration is neither discarded nor transferred
to graphite. No holdout is used. Central acceptance and its existing local edits
are untouched; this candidate registry addendum does not unlock Full Topic 13.

## Named Elastic Diagnostic Boundary (2026-09-01)

The new tree elastic branch includes contact/Phi-exchange interference,
not all collision channels. Phi remains an effective response; using its
internal propagator does not establish a physical particle identity.
The normal background is tree-level, not a self-consistent finite-temperature
solution. A response pole in the thermal integration domain is rejected rather
than regularized with an invented width. Response/inelastic channels, the full
gain/loss operator and current/entropy matching remain open. Grid refinement
is not material uncertainty or a continuum proof. No physical dependency is
unlocked by this diagnostic.

## Full-Scope Review Supersedes Bounded Handoff (2026-08-31)

The 2026-08-28 Core-ready language below describes a bounded O(2)/He-4
composition, not the requested Full Topic 13 completion. Complete thermal
transport, condensate/current/material matching and interacting SK/KMS
remain open. Retain independent He-4 source/calibration evidence within its
declared lane; do not equate it with graphite calibration or discard it merely
because a different branch's spectrum was repaired.

The fixed-Phi EOS/static-response repair is independently tested, but dependent
artifacts are not all refreshed. General-Z kinetic inputs and charge-sign
handling are now repaired. Other charged SK/vertex consumers still require
review, and the legacy quartic tensor does not match the fourth derivative of
the production potential at the same coupling. The repair artifacts retain
full_core_unlock=false.
The existing full-acceptance artifact has pre-existing local edits and was not
overwritten in this wave; its scope/freshness logic requires a separate repair.

## Core-Ready Claim Boundary (2026-08-28)

The bounded O(2)/He-4 bridge is now `CLOSED_FOR_CORE`, but the following limits remain controlling for stronger claims:

- `CLOSED_FOR_CORE` is an internal integration result, not external replication or proof of UET.
- The physical transport admission is one source-locked He II normal-component shear-viscosity channel. It is not bulk Fourier conductivity and not a complete two-fluid transport tensor.
- The permitted Ding Fig. 1d package is a 432-row normalized comparison source, not raw-author PBTE data and not a He-4 calibration source.
- Xie 2026 remains a locked, unread holdout and cannot be used for fitting, tuning, calibration, or threshold changes.
- Berut, Jun, and Hong retain external numeric-row/uncertainty gaps; Peterson remains a scoped source-identity no-go. Their Core dependency role is closed only because Landauer is an imported constraint, not a route to `alpha`, `beta`, EOS, or transport.
- The original conserved-`C` local-gradient candidate remains blocked. The finite-cone flux/Phi branch is a separately named branch and does not replace that baseline.
- The natural action state and the 1.7 K He-4 physical state are connected only through declared `theta_T`, `Z_Phi`, and `e0` mappings; they are not silently identified.
- Curved 3+1, Gravity, graphite TTG external validation, and global UET closure remain open.

- The root baseline comparison is present, but numeric acceptance boundaries are still provisional until a saved artifact is generated and reviewed.
- Current data posture is source-referenced but still below a fully normalized archival dataset package.
- Berut 2012 and exact SI/CODATA source records are now pinned under `docs/data/external/...`, but the Berut numeric rows used by the verifier remain topic-derived summaries rather than raw archived tables.
- The data package still contains manual literature summaries, so the topic cannot yet claim fully standardized data provenance.
- `Research_Landauer.py` verifies exact-constant consistency and lower-bound behavior; it does not prove the complete UET bridge mechanism.
- Bekenstein, Unruh, Hawking, and Josephson formulas are established physics/metrology identities. They constrain the bridge but do not independently validate UET dynamics.
- The Cattaneo benchmark is synthetic and fitted; it is useful for model-shape checking but cannot be cited as external experimental evidence.
- The vacuum entropy-sink script is an open hypothesis sandbox. It requires conservation-law accounting and an independently motivated physical mechanism before it can support core theory claims.
- Internal script execution does not by itself establish external replication, theorem-level proof, or broad physical closure.

## Current Claim Boundary

| Claim area | Allowed wording now | Blocker to stronger wording |
|:--|:--|:--|
| Landauer bridge | Source-record-backed lower-bound consistency check | Raw external source package, uncertainty table, and dynamic UET prediction beyond the lower bound. |
| Thermodynamic gravity links | Consistency with standard formulas | Formal derivation showing how UET field variables produce the relation, not only reuse it. |
| Non-equilibrium heat transport | Synthetic Cattaneo-style lag demonstration | Real dataset or declared simulation-only role with fixed parameters. |
| Vacuum entropy sink | Hypothesis sandbox | Physical mechanism, conservation accounting, and falsifiable test. |
| Provenance workflow | Intake/readiness gate exists for missing source packages | Filled evidence entries, archived upstream files, and source-review closure. |
| Dependent theory topics | May inherit lower-bound and standard-formula constraints from the foundation claim gate | UET bridge proof, source-normalized dataset closure, uncertainty propagation, and dependency proof. |

## Core Thermodynamic Constraint Boundary

- The Landauer quantity `k_B T ln(2)` is an imported lower-bound constraint. It does not derive the UET coefficient `beta`, an equation of state, mobility, or a core coupling coefficient.
- Bekenstein, Unruh, Hawking, and related standard identities constrain candidate mappings but do not supply a UET entropy current, dissipative-Bianchi closure, or covariant transport law.
- The Cattaneo artifact remains analytical and synthetic. Passing its control gates is not external heat-transport validation.
- The matter-space thermal pilot remains `SIMULATION_ONLY / FAIL`: physical pre-arrival leakage and external numeric-source readiness remain failed gates.
- The thermal source review now closes only the standard normalized TTG measurement operator `Delta_Tq(t)/Delta_Tq(0)` and the candidate normalized UET operator `Delta_Phi(t)/Delta_Phi(0)`; it does not establish a dimensional map.
- `alpha_Phi_K` remains an open calibration-dependent coefficient. Heat flux and entropy production are downstream derived quantities, not direct TTG observables in this package.
- The 2026 graphite source declares source data provided with the study but remains a locked holdout and is not locally archived or consumed here; the 2022 source remains request-based.
- Normalized `Phi` and derived trace `R` are not temperature, heat flux, entropy, information matter, or feedback variables without a separately justified dimensional observable map.
- The four active Berut, Jun, Hong, and Peterson source-row controllers remain independent and unchanged.
- The dependency packet cannot promote Topic `0.13` beyond `Draft / B`; it records what may be inherited and what remains blocked.

## Ding 2022 OA Numeric-Input Availability (2026-08-11)

The complete captured official `PMC8755757.1/` prefix has no force constants, Phonopy/ShengBTE inputs, scattering matrix, mode-resolved heat-capacity data, or numeric `C_src(T)`. The article gives computational grid/supercell details but routes supporting data to a corresponding-author request. This closes only the current official-OA search route. It does not show that author-held data are unavailable and does not permit reconstruction of `C_src(T)` from normalized TTG curves.


## Declared finite-temperature real-time component lane (T13-121)

The declared 1<->3 and representative 2<->2 natural-unit channels now have a numerical retarded/advanced/Keldysh component interface with a checked FDT relation. This remains an internal action-derived lane: it does not close the complete off-shell all-channel 1PI object, select a physical renormalization anchor, emit physical Kubo transport, provide an SI `Phi` map, calibrate `alpha_Phi_K`, validate TTG, or promote Full Topic 13.

## T13-122 Threshold-Crossing Boundary
The below/above-threshold lane is a declared natural-unit response result, not a complete finite-temperature 1PI theory. The `2<->2` below-threshold witness does not supply a physical transport coefficient, and the `1<->3` threshold witness does not select a physical renormalization scheme. No dimensional `Phi` mapping, independent `alpha_Phi_K`, TTG validation, EOS, entropy current, or external claim is promoted.
## T13-123 All 2-to-2 Permutation Boundary
The three equal-mass signed-cut permutations are covered by a unit-Jacobian relabeling identity. This does not prove a physical transport normalization, complete off-shell 1PI renormalization, a dimensional `Phi` map, or an independent `alpha_Phi_K`. The aggregate graph weight remains an action-level contract, not a calibrated SI coefficient.
## T13-124 source boundary

The IAEA GR-280 lane closes only the availability of a same-temperature Cp row and density row in one official source. It does not provide a standard uncertainty for density, a direct volumetric measurement, or a source-matched `c_v` correction. GR-280 reactor graphite is not treated as Ding HOPG/TTG, so the lane cannot substitute for Ding `C_src` or calibrate `alpha_Phi_K`. The result remains a comparison-only lane and does not unlock Core, Gravity, transport, Galaxy, or external validation.
## T13-125 high-temperature Cp comparator limitations

- The workbook reports `C_p`, not `c_v`; no density, `alpha_V`, or `K_T` rows are supplied for a volumetric conversion.
- The same-block isotropic graphite material is not asserted to be Ding HOPG/TTG, so it cannot supply Ding `C_src(T)` or `alpha_Phi_K`.
- VINCA rows have no reported row uncertainty; no uncertainty was inferred from the other laboratories.
- LNE/PTB expanded uncertainty is not a substitute for a source-grade `c_v` uncertainty budget.
- The comparator is not used for fit, tuning, calibration, or Xie 2026 holdout access.

## T13-126 - IG210 expansion boundary
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` only.
WHAT_IS_ACTUALLY_CLOSED: A source-traceable IG210 mean linear-expansion comparator with a conditional isotropic `alpha_V` mapping and an explicit 10 percent expanded uncertainty boundary at `k=2`.
WHAT_REMAINS_OPEN: The workbook does not provide same-state isothermal `K_T`, density uncertainty, `Cp/Cv`, Ding TTG equivalence, or any base-`Phi` energy amplitude. The factor `3` is a geometry assumption, not an extra measurement.
DEPENDENCY_UNLOCKED: No Cp-to-Cv, Ding `C_src`, `alpha_Phi_K`, transport, Core, Gravity, or Galaxy dependency.
STATUS: `PASS_SCOPED_IG210_ALPHA_L_SOURCE`; global Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: The source was archived, hashed, audited, and projected into the full gate/register/dependency contract.
EQUATION_OR_MAPPING: `alpha_V=3*alpha_l` is conditional; no numerical `alpha_Phi_K` or thermal prediction is emitted.
VERIFICATION: `17/17` source checks and `2` focused tests passed; no fit and no Xie 2026 access.
CONTROLLING_BLOCKER: `same_state_alpha_V_K_T_and_Ding_material_regime_mapping_missing` for this source route.
NEXT_ACTION: Continue the paired thermodynamic input route and independent dimensional `Phi` anchor route.
CLAIM_BOUNDARY: This lane cannot be used as external validation or calibration.
## T13-128 - IG210 published-source boundary
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` only.
WHAT_IS_ACTUALLY_CLOSED: A source-traceable IG-210 thermophysical comparator with density, `C_p`, diffusivity, `alpha_l`, conductivity, and stated `k=2` uncertainty bounds.
WHAT_REMAINS_OPEN: `K_T`, `C_v`, Ding TTG equivalence, Ding `C_src`, dimensional `Phi`, and independent `alpha_Phi_K` remain open.
DEPENDENCY_UNLOCKED: None beyond the comparison lane.
STATUS: `PASS_SCOPED_FAROOQUI_IG210_THERMOPHYSICAL_SOURCE`; global Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Published NPL PDF, package, audit, focused test, and gate projections were added.
EQUATION_OR_MAPPING: `alpha_V=3*alpha_l` is conditional; no Cp-to-Cv correction or UET calibration is emitted.
VERIFICATION: Audit `15/15`; focused test `3 passed`; no fit and no Xie 2026 access.
CONTROLLING_BLOCKER: Same-state `K_T` and independent `Phi` dimensional anchor.
NEXT_ACTION: Continue source acquisition and independent calibration research without substituting IG-210 for Ding.
CLAIM_BOUNDARY: Comparator only; not physical UET closure or external validation.

## T13-129 IG210 K_T limitation boundary
MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for a source-availability no-go.
WHAT_IS_ACTUALLY_CLOSED: The public NPL IG210 thermophysical source route is now explicit: same-grade C_p and alpha_l rows exist, but the source package contains no same-state K_T or C_v.
WHAT_REMAINS_OPEN: A missing K_T record cannot be repaired by relabeling conductivity, diffusivity, elastic bulk modulus, or a different graphite grade. Ding equivalence, C_src, alpha_Phi_K, and full thermal closure remain open.
DEPENDENCY_UNLOCKED: None beyond the scoped source-boundary lane.
STATUS: PASS_SCOPED_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY_NO_GO; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE / PARTIAL.
WHAT_CHANGED: Added IG210 to the existing no-go inventory without changing the threshold, ontology, holdout policy, or claim boundary.
EQUATION_OR_MAPPING: c_p^V-c_v^V=T*alpha_V^2*K_T remains a contract, not a computed result.
VERIFICATION: Source-boundary audit passed; focused regression 2 passed; no fit, tuning, synthetic replacement, or holdout access.
CONTROLLING_BLOCKER: same_state_IG210_K_T_missing.
NEXT_ACTION: Search for a permissioned same-state IG210 K_T record; otherwise keep this route blocked and move to the independent Phi energy-anchor route.
CLAIM_BOUNDARY: Comparator/no-go only; not material validation, not calibration, and not Full Topic 13 closure.
## T13-130 - Symbolic action-to-SI conversion limitation
MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE only.
WHAT_IS_ACTUALLY_CLOSED: Conditional symbolic conversion factors from natural units to SI units are now explicit and audited.
WHAT_REMAINS_OPEN: No physical E_ref, covariant Phi_scale, base Phi -> Phi_E, e0, response coefficient, or independent alpha_Phi_K calibration is established.
DEPENDENCY_UNLOCKED: None beyond the symbolic formula lane.
STATUS: Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE / PARTIAL.
WHAT_CHANGED: Added an auditable conversion module and kept all physical inputs open.
EQUATION_OR_MAPPING: u_SI=u_nat*E_ref^4/(hbar*c)^3; Delta_Tq=(E_ref/k_B)*Delta_theta; normalization requires Phi_scale.
VERIFICATION: Scoped audit passed; full gate remains at 10 blockers; holdout access remains false.
CONTROLLING_BLOCKER: energy_reference_and_base_Phi_normalization_provenance_missing.
NEXT_ACTION: Search for independent action/field coefficient provenance; do not turn the symbolic contract into calibration.
CLAIM_BOUNDARY: Conditional dimensional bookkeeping only, not SI calibration, prediction, or Full Topic 13 closure.

## T13-131 - Huberman public PBTE source limitation

The Huberman 2019 arXiv package is a useful graphite transport comparator and method record, but it is not an accepted Ding `C_src` input. Its embedded supplementary methods refer to Ding-derived force constants without depositing the raw force constants, scattering matrix, mode-resolved heat capacities, source-grade uncertainty, or convergence payload. The lane therefore closes only the public-source boundary and leaves the full Topic 13 source blocker unchanged.

`alpha_Phi_K` remains open; no PDF-derived curve, printed value, or normalized TTG trace is permitted to calibrate it.

## Invariant-rate finite-operator boundary

The repaired operator closes the missing energy dimension only in a finite representative channel basis. Each existing exact elastic channel receives one declared solid-angle cell; those cells are not a converged angular quadrature for a connected multi-shell collision integral. The resulting rate must not be reused as a physical damping width or Kubo coefficient.

The legacy `E^2` operator remains preserved and rejected as a rate. The new `E^1` candidate does not repair `alpha_Phi_K`, TTG source provenance, SI normalization, number-changing channels, or the response-sector width.

## Invariant scalar Galerkin boundary

The multi-shell/angular Galerkin result removes the disconnected representative-cell blocker only for a finite scalar isotropic basis. Its three null modes are the two elastic species numbers and total energy represented in that scalar basis; momentum conservation is checked eventwise but vector momentum modes are not yet basis variables.

The result cannot be called a self-consistent quasiparticle width or conductivity. A tagged/spectral width must be derived from the same collision kernel, and heat/current response requires vector and tensor basis functions. The cutoff and feature-basis limits also remain open.

The older continuum-collocation total can appear dimensionally acceptable because its diagonal width term scales as `E`, but its mapped legacy transition vertex scales as `E^2`. That vertex remains blocked from microscopic reuse.

## Same-kernel tree-width boundary

The momentum-resolved `Gamma_q(p)` is an elastic tree width on the declared nonresonant normal background. It is derived rather than fitted and is suitable as a controlled input to the next dressed-RA diagnostic, but it is not yet a self-consistent dressed width.

Response-sector resonances, number-changing cuts, finite-temperature self-energy feedback, pole-mass iteration, and off-shell spectral normalization remain absent. The relation `-Im Sigma_R=2E Gamma` is an on-shell interface, not an independent loop calculation or physical conductivity.

## Vector heat-rank no-go boundary

The current elastic equal-mass two-charge lane has one independent Landau-projected vector source, not two. Since `J_Q=P-mu J_charge`, removing conserved momentum forces `J_Q_perp=-mu J_charge_perp`; at zero chemical potential the projected heat source is zero.

This no-go must not be hidden by reporting the formal heat response form as an independent thermal conductivity. A second heat channel requires additional normal-component structure, response-sector carriers, unequal species, number-changing processes, or another declared physical extension. Which extension is physically admissible remains open.
