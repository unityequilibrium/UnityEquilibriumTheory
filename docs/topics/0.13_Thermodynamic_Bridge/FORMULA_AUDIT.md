# Formula Audit: 0.13_Thermodynamic_Bridge

## Normal Thermal Response Stationarity (2026-09-01)

Candidate ID: uet.o2.thermal.normal_response_stationarity. This extends the
normal-background question, not the existing fixed-Phi Hartree calculation.
Let x=sqrt(epsilon*K)*Delta_Phi_natural, m_chi^2(x)=m0^2-G*x and
M_response^2(x)=M0^2+3*lambda_response*x^2. At chi=0 the two charged and one
neutral thermal determinants add to V_tree(x). The field-dependent vacuum
determinant and counterterms are omitted explicitly; this is not a complete
renormalization prescription. Matter quartic effects enter interacting
self-energies/higher loops and are not supplied by this Gaussian determinant.

For I_i=integral f_i/(2E_i) and J_i=partial I_i/partial m_i^2,
Omega_x=M0^2*x+lambda_response*x^3-G*I_chi+6*lambda_response*x*I_response.
Solving Omega_x=0 with positive Omega_xx gives a local stationary response
inside the strict normal-mode gap. No global or condensed-phase minimum is
claimed. The stationary pressure obeys the envelope relation, with
chi_stationary=chi_fixed+Omega_xmu^2/Omega_xx. The small-displacement estimate
is x_star approximately G*I_chi(0)/(M0^2+6*lambda_response*I_response(0)+G^2*J_chi(0)).

The shifted tree response vertex is H_cubic=6*lambda_response*x_star.
Consequently mixed scattering contains
M=G^2*(1/(s-m_chi^2)+1/(u-m_chi^2))-G*H_cubic/(t-M_response^2).
The last term is absent in a mass-only update. Shifted-tree sensitivity is not
a full thermal loop amplitude: other terms at the same perturbative order
must be matched. The static Hessian Omega_xx is not a pole-mass prescription.

[Floerchinger's thermal determinant and stationary-pressure derivation](https://www.tpi.uni-jena.de/~floerchinger/qft2/lecture22/)
provides method context only, not numerical coefficients or evidence for UET.

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-NORMAL-THERMAL-BACKGROUND-20260901 | Omega_x=0; p=-Omega(x_star); H_cubic=6*lambda_response*x_star | docs/scripts/audit/audit_topic13_normal_thermal_background.py | x,T,mu,H_cubic natural energy; Omega energy^4; force energy^3; curvature energy^2 | declared tree action plus thermal Bose determinant, no fit | checked local numerical approximation; full renormalized matching open | diagnostic-only stationary response and shifted-vertex handoff | mass-only update drops exchange term; static Hessian mistaken for pole mass | consistent thermal background, propagator, vertices and current matching |

## Coupled Bose Collision Form (2026-09-01)

Candidate registry ID: uet.o2.thermal.normal_coupled_gain_loss. The named
normal-state diagnostic adds response-mode quartic self-scattering, mixed
matter/response scattering and charge-pair conversion to the preceding elastic
action calculation. The response label is a kinetic-lane assumption, not a
physical-particle interpretation of Phi. C is not charge or population count.

For dimensionless population affinity psi, delta f=f*(1+f)*psi,
F=f1*f2*(1+f3)*(1+f4), R=f3*f4*(1+f1)*(1+f2), and
delta(F-R)=F_eq*(psi1+psi2-psi3-psi4). The scalar collision form is
the invariant four-leg phase-space integral of
abs(M)^2*F_eq*Delta_psi_a*Delta_psi_b/(S_in*S_out*S_reverse).
The vector form additionally uses the isotropic component average 1/3.
Each identical pair gives a factor 2; S_reverse=2 for an elastic species
multiset, otherwise 1 for a conversion orientation listed once. Full ordered
species enumeration with prefactor 1/8 independently reproduces these weights.

The projected-current response is S_perp^T*L_active^-1*S_perp. L has natural
energy dimension 4, the susceptibility has dimension 3, its generalized rates
dimension 1, and this response dimension 2. It is not SI conductivity.
Nested trial bases use the same collision nodes, so their variational response
is compared without a simultaneous quadrature change. The smallest basis omits
neutral*p/T, a relative sector-momentum direction whose relaxation form scales
as G^4. At G=0 this is an additional conserved momentum and the current inverse
is rejected rather than given an artificial regulator. At mu=0 the charge
source has no overlap with this charge-even slow mode.

The entropy witness checks (F-R)*log(F/R)>=0 for reversible Bose events; it is
not a complete interacting SK/KMS construction or a spacetime entropy current.
The thermal background is not self-consistently renormalized and number-changing
higher-order channels are missing. The derivation-to-transport distinction is
consistent with [Jeon's linearized Boltzmann framework](https://arxiv.org/abs/hep-ph/9409250);
the paper supplies method context, not these action coefficients or numerical inputs.

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-NORMAL-GAINLOSS-20260901 | L_ab=integral abs(M)^2 F_eq Delta_psi_a Delta_psi_b / reaction_factors | docs/scripts/audit/audit_topic13_coupled_gain_loss_operator.py | q=species label, not C; psi dimensionless; L energy^4; response energy^2 | declared synthetic action, invariant phase space; no fit | checked local tree-level and finite-basis approximation; physical mapping open | diagnostic-only candidate addendum | missing relative-momentum trial direction; extra truncation invariants; incomplete thermal background | independent basis/completeness and physical current/entropy matching |

## Named Elastic Contact/Phi Exchange (2026-09-01)

Candidate ID: uet.o2.thermal.normal_tree_elastic_scattering, stored in a
diagnostic-only registry addendum. For chi=0 and Phi=Phi_equilibrium in flat
space, canonical normalization gives phi_c=sqrt(epsilon*K)*deltaPhi,
G=sqrt(epsilon)*h/(Z*sqrt(K)), lambda_c=lambda/Z^2 and M_Phi^2=U''/K.
The contact tensor and s/t/u response exchange are contracted with charge
polarizations before taking the squared amplitude. The relative sign agrees
with eliminating the massive response at low energy; interference is retained.

The full-solid-angle cross section uses
d_sigma/d_Omega=|M|^2/(64*pi^2*s*S_final).
S_final is 2 for identical outgoing charges, otherwise 1. Each unlike final
ordering is represented once. The tagged incoming particle introduces no
incoming pair-counting factor. Contact-only ratios to the old unit-channel
convention are therefore 8 and 16 for like and unlike charges, not one global
multiplier. Full gain/loss operator and physical transport remain open.

Phase-space and scalar-exchange conventions were checked against
[Tong, Interacting Fields, sections 3.5 and 3.6.3](https://www.damtp.cam.ac.uk/user/tong/qft/qfthtml/S3.html).
This is method context, not numeric calibration or evidence of UET validity.

## Kinetic Normalization and Action-Tensor Boundary (2026-08-31)

The normal kinetic setup now uses m_c^2=m_eff^2/Z,
lambda_c=lambda_action/Z^2 and signed mu. Occupations are
n_s=[exp((sqrt(k^2+m_c^2)-s*mu)/T)-1]^-1 with fixed species order (-1,+1).
Changing mu to -mu swaps these species rather than silently replacing mu by
its magnitude. The existing unit-channel comparator cross section remains
lambda_c^2/(16*pi*s); its overall action/channel convention is not repaired
by changing the input scale.

Independent fourth differences of the production matter_potential, at three
field normalizations and three step sizes, give
V_abcd=2*lambda_c*(delta_ab*delta_cd+delta_ac*delta_bd+delta_ad*delta_bc).
The legacy _tree_vertex_tensor(lambda_c) instead has coefficient lambda_c.
Contracting the action derivative with unit charge polarizations
e_plus,e_plus,e_minus,e_minus gives magnitude 4*lambda_c. The unit-channel
comparator amplitude lambda_c must not be equated to this derivative.

This is a local quartic/contact normalization finding, not a completed
scattering cross section, symmetry-factor prescription, exchange-channel sum,
or retarded Kubo result. Preserve previous comparator outputs as such; audit
the channel-resolved action mapping rather than globally multiplying rates.
See t13_kinetic_canonical_action_match_audit.json: canonical covariance passes,
but legacy action matching is BLOCKED and Full Topic 13 remains open.

## Fixed-Phi Implementation Correction (2026-08-31)

This corrects implementations of the existing fixed-background quadratic
action, not a new core equation. With q=Z*mu^2-m_eff^2>0, a=q/Z and
B=2*mu^2+a, the roots obey
(E^2-k^2)*(E^2-k^2-2*a)-4*mu^2*E^2=0.
Evaluate E_plus^2=k^2+B+sqrt(B^2+4*mu^2*k^2) and the rationalized
E_minus^2=k^2*(k^2+2*a)/E_plus^2 without clipping.
The normal energies are sqrt(k^2+m_eff^2/Z) +/- mu.

Canonical chi_c=sqrt(Z)*chi changes m_c^2=m_eff^2/Z and
lambda_c=lambda/Z^2, not chemical potential or time. Pressure and static
momentum response must be invariant under this field redefinition. For the
ideal relativistic normal branch only, integration by parts gives
chi_perp=epsilon+p; this is not a full condensed two-fluid identity.

The regression and independent repair audit verify these relations for the
declared synthetic grid. At Z=m_eff^2=lambda=1 and mu^2=3, the old gap squared
20 and sound squared 0.4 become 16 and 0.25. Phi is held fixed; this is not
the live-Phi three-mode spectrum. The repair artifact preserves the old git
identity and marks downstream review. It supplies no SI or full-core unlock.
The older bounded Core-ready composition below must not be read as full
thermal-bridge completion.

## T13 Core-Ready Composition (2026-08-28)

MAJOR_RESULT_CLOSURE: `T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY` is `CLOSED_FOR_CORE` with final acceptance `13/13`.
EQUATION_OR_MAPPING: `Delta_Tq=alpha_Phi_K*Delta_Phi_norm`; `Delta_Phi_norm=Z_Phi*Delta_Phi_natural`; `T_K=theta_T*T_natural`; `f_SI=e0*f_natural`; `beta_T13=beta_natural/Z_Phi^2`; `beta_SI=e0*beta_T13`; `eta=-lim_(omega->0+) Im G_R^(xy,xy)/omega`; `nabla_mu J_S^mu` contains `2 eta sigma_mu_nu sigma^mu_nu/T >= 0`.
UNITS: `alpha_Phi_K` is K per normalized base Phi; `Z_Phi` is normalized base Phi per natural action Phi; `e0` is J m^-3; `beta_SI` is J m^-3 per normalized Phi squared; `eta` is Pa s.
DERIVATION_CLASS: Natural bridge and beta origin are action-derived; `alpha`, `Z_Phi`, `theta_T`, and `e0` are lane-specific external calibration/scale inputs; `eta` is a source-locked external transport input; Landauer is an imported constraint only.
VERIFICATION: `alpha_Phi_K=-1.02237987858849 +/- 0.056753979576408715`; `Z_Phi=-0.017488421860832278`; `e0=512994.17164886114 J m^-3`; `beta_T13=-0.007936042649802305 +/- 0.0008831273413443808`; `beta_SI=-4071.143625305366 +/- 453.5201739147111 J m^-3` per normalized Phi squared; `eta=(1.29e-6 +/- 5e-8) Pa s`.
CLAIM_BOUNDARY: These are bounded O(2)/He-4 Core mappings, not universal identities for `Phi`, not graphite TTG external validation, and not global UET closure. `R_gen` remains absent from the state vector and has no backreaction.

## T13-094 - Condensed Dissipative Transport Identifiability Boundary

MAJOR_RESULT_CLOSURE: CLOSED_AS_NO_GO for T13_UET_O2_CONDENSED_DISSIPATIVE_TRANSPORT_IDENTIFIABILITY_NO_GO; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: The declared condensed static lane has zero condensate entropy in its tree-sector records and does not expose a relative-flow variable, collision kernel, or retarded correlator. Distinct positive-semidefinite matrices L_A=[[1,0],[0,1]] and L_B=[[2,0],[0,0.5]] both give zero entropy production at X_static=(0,0), but distinct responses at X_probe=(1,0).
WHAT_REMAINS_OPEN: A microscopic condensed collision kernel, physical Kubo/Onsager coefficient, complete two-fluid constitutive tensor, SI Phi map, alpha calibration, source closure, and Full Topic 13.
VERIFICATION: PASS_SCOPED_CONDENSED_DISSIPATIVE_TRANSPORT_IDENTIFIABILITY_NO_GO; 5 focused unit tests passed; static witnesses agree and probe responses differ; no source rows, fitting, target data, or holdout were used.
CLAIM_BOUNDARY: Scoped identifiability no-go for the current condensed static lane only; no physical transport coefficient or complete two-fluid closure is emitted.
EVIDENCE: docs/core/artifacts/t13_uet_o2_condensed_dissipative_transport_audit.json.

## T13-093 - Current Continuum-Limit Boundary

MAJOR_RESULT_CLOSURE: CLOSED_AS_NO_GO for T13_UET_O2_CONTINUUM_LIMIT_CURRENT_SCHEME_NO_GO; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: Existing finite-cutoff radial/channel resolution sequence is source-linked; the unchanged repository controller max(relative change)<=1e-2 is applied; current maximum adjacent DC-response change is 0.47541462972440046, so continuum promotion is rejected and no extrapolated response is emitted.
WHAT_REMAINS_OPEN: This is not a mathematical no-go for every future discretization. New basis/cutoff control or matched extrapolation, loop-renormalized vertex, microscopic SK/KMS, physical Kubo, SI map, alpha_Phi_K, Ding C_src, and Full Topic 13 remain open.
VERIFICATION: PASS_SCOPED_CONTINUUM_LIMIT_CURRENT_SCHEME_NO_GO; sequence (0.47541462972440046, 0.2421143231506593, 0.04027765595323908); focused regression 4 passed.
CLAIM_BOUNDARY: Scoped no-go for the declared current scheme only; no continuum proof, physical Kubo, SI calibration, alpha, TTG validation, or Full Topic 13 closure.
EVIDENCE: docs/core/artifacts/t13_uet_o2_continuum_limit_boundary_audit.json.

## T13-092 - Finite-Temperature Two-Fluid Static Response

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_UET_O2_FINITE_T_TWO_FLUID_STATIC_RESPONSE_LANE; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: Action/EOS condensate-normal pressure, charge, entropy, energy, and susceptibility split; branch-resolved static normal response; condensed tree stiffness; normal-branch finite-cutoff covariant heat-flux and entropy balance interface.
WHAT_REMAINS_OPEN: Static susceptibility is not a Landau normal density or retarded Kubo coefficient. Condensed dissipative transport, interacting self-energy, microscopic SK/KMS matching, SI map, alpha_Phi_K, Ding C_src, and Full Topic 13 remain open.
VERIFICATION: PASS_ACTION_DERIVED_FINITE_T_TWO_FLUID_STATIC_RESPONSE_LANE; all checks passed; normal kappa_natural 257.3728668627025; focused regression 4 passed.
CLAIM_BOUNDARY: Natural-unit action-derived static two-sector lane and normal-branch formal heat balance only; no physical Kubo, SI calibration, alpha, TTG validation, or Full Topic 13 closure.
EVIDENCE: docs/core/artifacts/t13_uet_o2_finite_temperature_two_fluid_response_audit.json.

## T13-091 - Action-Derived Natural Phi-to-Thermal Bridge

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_UET_O2_ACTION_NATURAL_PHI_THERMAL_BRIDGE_LANE; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: epsilon=-p+T*partial_T p+mu*partial_mu p; Delta_epsilon^nat=(partial_Phi epsilon)_(T,mu)*Delta_Phi; C_epsilon_T^nat=(partial_T epsilon)_(mu,Phi); Delta_T_q^nat=Delta_epsilon^nat/C_epsilon_T^nat.
WHAT_REMAINS_OPEN: C_epsilon_T is not source c_v; physical Phi SI anchor, alpha_Phi_K, Ding C_src, dimensional TTG map, physical transport, and Full Topic 13 remain open.
VERIFICATION: PASS_ACTION_DERIVED_NATURAL_PHI_THERMAL_BRIDGE_LANE; identity residual 0; alpha_Phi_T^nat 0.0023138578447835533; linearization residual 3.321118889703099e-05; focused regression 4 passed.
CLAIM_BOUNDARY: Natural action-derived bridge only; no SI Kelvin prediction, physical c_v relabeling, alpha calibration, TTG validation, or Full Topic 13 closure.
EVIDENCE: docs/core/artifacts/t13_uet_o2_action_thermal_observable_bridge_audit.json.

Audit status: reviewed registry, replacing the bootstrap scaffold.

Scope note: this topic is a core bridge between information, entropy, energy cost, and gravity-adjacent thermodynamic identities. The audit below separates established physics identities from UET bridge hypotheses and from synthetic benchmark demos.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-001` | `S(E,N) ~= (E+N) ln(E+N) - E ln(E) - N ln(N)` | `Code/01_Engine/Engine_Thermodynamics.py::compute_entropy`; `Code/02_Proof/Proof_Entropy_Max.py` | `E` = dimensionless energy quanta; `N` = particle count; `S` = dimensionless entropy proxy | Stirling approximation to microstate count; topic-local proxy | heuristic/statistical proxy, not a theorem proof | Supports entropy-increase demo and engine equilibrium trend | Invalid for low `E`, low `N`, non-equiprobable states, or dimensional entropy claims | Add exact combinatorial baseline for small `E,N`; record seed and monotonicity threshold in verifier |
| `T13-002` | `1/T = dS/dE = ln((E+N)/E)`, so `T = 1 / ln(1 + N/E)` | `Code/01_Engine/Engine_Thermodynamics.py::compute_temperature` | `T` = dimensionless temperature proxy; `E` = quanta; `N` = count | derivative of `T13-001` proxy | derived from the topic proxy | Checks energy-sharing equilibrium in engine demos | Can be mistaken for Kelvin temperature; fails at `E <= 0`; coarse-graining dependent | Rename/report as `T_proxy` in future outputs or add conversion convention if a physical scale is introduced |
| `T13-003` | contact transition rates imply equilibrium `E_A/N_A ~= E_B/N_B` | `Code/01_Engine/Engine_Thermodynamics.py::step` | `E_A,E_B` = dimensionless quanta; `N_A,N_B` = particle counts | topic simulation rule | model hypothesis for contact dynamics | Engine-level bridge test for zeroth-law behavior | Random-walk update is stochastic and lacks detailed-balance proof in current implementation | Add seeded ensemble runs with mean/variance and acceptance band against equipartition |
| `T13-004` | `E_min = k_B T ln(2)` | `Code/01_Engine/Engine_Thermodynamics.py::get_landauer_limit`; `Code/03_Research/Research_Landauer.py` | `E_min` = joule; `T` = kelvin; `k_B` = J/K | SI exact Boltzmann constant; Landauer principle literature | source-backed identity/lower-bound benchmark | Primary verifier metric: engine value must match CODATA expression and external measurements must not fall below the lower bound | External data can be overread as exact prediction; measured dissipation above bound is not model error | Source-lock Berut/Jun/Peterson values under `docs/data/external/...` with DOI and preprocessing notes |
| `T13-005` | `E_eV = E_J / e` | `Code/03_Research/Research_Landauer.py::landauer_energy_eV` | `E_eV` = eV; `E_J` = joule; `e` = `1.602176634e-19` J/eV | SI exact elementary charge | unit conversion, source-backed | Converts Landauer cost for comparisons to eV-scale measurements | Any remaining rounded constants in other scripts can drift at high precision | Audit duplicate eV conversions in non-primary scripts |
| `T13-006` | `S_max_bits = 2 pi R E / (hbar c ln 2)` | `Code/01_Engine/Engine_Thermodynamics.py::get_region_entropy_bound`; `Code/03_Research/Research_Landauer.py::bekenstein_bound` | `R` = m; `E` = J; `S_max_bits` = bits; `hbar` = J s; `c` = m/s | Bekenstein bound literature and CODATA constants | source-backed bound formula | Demonstrates information-density bound relationship | Bound is not an independent UET prediction; arbitrary example systems are illustrative only | Add citation/source table and distinguish illustrative examples from validation datasets |
| `T13-007` | `S_BH = A / (4 l_P^2)`, `A = 4 pi (2GM/c^2)^2` | `Code/01_Engine/Engine_Thermodynamics.py::get_bekenstein_entropy`; `Data/03_Research/experimental_data.py::bekenstein_hawking_entropy` | `M` = kg; `A` = m^2; `l_P^2 = hbar G / c^3`; entropy in Planck units | Bekenstein-Hawking relation; CODATA constants | source-backed theoretical identity | Formula-consistency check for black-hole entropy scaling and area-theorem examples | Observed BH masses are copied manually; entropy is computed, not directly observed | Source-lock LIGO/EHT mass tables and propagate mass uncertainty to entropy ratio |
| `T13-008` | `T_Unruh = hbar a / (2 pi k_B c)` | `Code/01_Engine/Engine_Thermodynamics.py::get_unruh_temperature`; `Code/03_Research/Research_Landauer.py::unruh_temperature` | `a` = m/s^2; `T` = K | standard Unruh relation; CODATA constants | source-backed theoretical identity | Formula-consistency check for Jacobson bridge discussion | Extremely small values are not experimental validation of UET | Keep as theory-link formula; do not promote to empirical bridge without an explicit observable |
| `T13-009` | `T_H = hbar c^3 / (8 pi G M k_B)` | `Code/01_Engine/Engine_Thermodynamics.py::get_hawking_temperature`; `Data/03_Research/experimental_data.py::hawking_temperature` | `M` = kg; `T_H` = K | Hawking temperature relation; CODATA constants | source-backed theoretical identity | Supports black-hole thermodynamic context | Not directly measured for astrophysical black holes; manual mass inputs dominate outputs | Add uncertainty propagation and mark as computed theoretical observable in manifest |
| `T13-010` | `tau dq/dt + q = -k grad(T)`; Euler form `q_i = q_{i-1} + (target - q_{i-1}) dt/tau` | `Code/03_Research/Research_NonEquilibrium_Validation.py`; `Data/03_Research/cattaneo_data.json` | `tau` = ps in topic data; `q` = synthetic heat-flux units; `grad(T)` = synthetic K/m proxy; `k` = fitted proxy | synthetic Cattaneo-Vernotte benchmark | illustrative benchmark, not external validation | Shows lag/hysteresis behavior relative to Fourier instant response | Units are mixed/proxy; `k_cond=0.95` is fitted in code; data is synthetic | Replace with sourced second-sound/heat-pulse dataset or declare as simulation-only in README |
| `T13-011` | vacuum sink update `T_vac += dS_input / capacity`; matter cooling `T_sys *= (1-rate)` | `Code/03_Research/Proof_Vacuum_Entropy_Sink.py` | `T_vac,T_sys` = K labels; `dS_input` = proxy entropy; `capacity` = dimensionless large number | topic-local hypothesis | open heuristic | Stress-tests a proposed UET cooling/sink mechanism | Treats 0 K/infinite capacity as an assumption; does not prove physical vacuum behavior | Reframe as hypothesis sandbox; require physical mechanism and conservation accounting before core use |
| `T13-012` | Josephson constant `K_J = 2e/h` | `Data/03_Research/experimental_data.py`; `Code/03_Research/Research_Real_Data_Validation.py::test_josephson_quantum` | `K_J` = Hz/V; `e` = C; `h` = J s | exact SI constants since 2019 | source-backed metrology identity | Auxiliary exact-constant check, not central to thermodynamic bridge | Irrelevant if used as evidence for UET thermodynamic mechanism | Keep as constants sanity check only or move to a constants/metrology appendix |
| `T13-013` | `y_TTG=Delta_Tq(t;Lambda)/Delta_Tq(0;Lambda)` | `docs/core/thermal_source_observable_map.py`; `THERMAL_SOURCE_OBSERVABLE_MAPPING_SPEC.md` | `Delta_Tq` = quasi-temperature difference; raw K after calibration; `y_TTG` dimensionless; `Lambda` = m; `t` = s | source-backed measurement-operator definition from graphite TTG papers | derived observable definition, not UET derivation | Locks the normalized external measurement target before numeric intake | Quasi-temperature is not automatically equilibrium temperature; heat flux is not directly measured | Archive source rows and run a pre-registered normalized comparison |
| `T13-014` | `y_TTG^UET=Delta_Phi(t;Lambda)/Delta_Phi(0;Lambda)` | `docs/core/thermal_source_observable_map.py`; `docs/scripts/audit/audit_thermal_source_observable_mapping.py` | `Phi` = normalized UET response coordinate; `y_TTG^UET` dimensionless | topic-derived measurement operator candidate | open calibration-dependent relation | Defines a falsifiable shape-comparison lane without assigning SI meaning to `Phi` | A normalized shape match would not derive `alpha_Phi_K` or validate UET dynamics by itself | Freeze parameters, archive source rows, and compare against holdout only after core gates |
| `T13-015` | `Delta_Tq=alpha_Phi_K*Delta_Phi` | `docs/core/thermal_source_observable_map.py`; `matter_space_thermal_source_review.json` | `alpha_Phi_K` = K per normalized `Phi`; `Delta_Tq` = K after calibration | open placeholder / calibration bridge | open | Dimensional mapping blocker | Hidden calibration or fitted scale can turn a comparator into an apparent prediction | Derive or source-lock the scale with uncertainty and an independent calibration lane |

## Formula-to-Claim Guardrails

| Claim area | Maximum current claim class | Reason |
| :-- | :-- | :-- |
| Landauer information-energy bridge | `C` | Formula is exact/source-backed, but topic data is still local working copy and verifier checks lower-bound consistency rather than a full UET dynamic prediction. |
| Bekenstein/Jacobson gravity bridge | `D/C` | Relations are established theoretical identities; UET-specific bridge remains interpretive until dependency to core field equations is formalized. |
| Non-equilibrium heat-flux benchmark | `D` | Current Cattaneo dataset is synthetic/proxy and has a fitted conductivity parameter. |
| Vacuum entropy sink | `E/D` | Open UET hypothesis sandbox; cannot support core claims without conservation-law accounting and physical source. |

## Required Follow-Up

- Move external raw source records for Berut/Jun/Peterson, LIGO, EHT, and CODATA/NIST constants into `docs/data/external/...` or explicitly document why a local working copy is used.
- Keep `Research_Landauer.py` artifact checks tied to formula/hash/status checks. Current target: `Result/artifacts/0_13_thermodynamic_bridge_verification.json`.
- Split validation language: Landauer lower-bound consistency, black-hole formula consistency, synthetic Cattaneo simulation, and open UET vacuum-sink hypothesis are different evidence classes.
- Add uncertainty propagation for manually copied black-hole masses and Landauer heat measurements.

## Audit Link

- Core audit report: `docs/meta/core_research_hardening_audit.md`

## Ding 2022 PBTE energy-temperature source mapping (2026-08-11)

- Source locator: Ding 2022 Supplementary Information p.3 Eq. S4 and p.5 Eq. S10.
- Source mapping: `Delta_u_ph = sum_mu(g_mu)` and `Delta_Tq = Delta_u_ph/C_src`.
- Unit closure: `(J m^-3)/(J m^-3 K^-1) = K`.
- Conditional named branch: `Phi_E = Delta_u_ph/e0`, `alpha_Phi_E_K = e0/C_src`.
- Ontology boundary: source `C_src` is heat capacity per volume and is not UET `C`; `Phi_E` is not base `Phi`; `R_gen` remains a derived trace.
- Derivation class: source-backed standard linearized PBTE mapping; UET dimensional correspondence remains open.
- Numeric status: no `C_src(T)`, `e0`, or alpha value is emitted; Xie 2026 remains unread.


## Covariant Field-Normalization Identifiability (2026-08-11)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-016` | `delta_phi' = s delta_phi`; `Z'=Z/s^2`; `m_Phi^2'=m_Phi^2/s^2`; `lambda'=lambda/s^4`; `xi'=xi/s^2`; `Phi_scale'=s Phi_scale` | `docs/core/uet_covariant_response.py`; `docs/scripts/audit/audit_topic13_covariant_field_normalization_identifiability.py` | `delta_phi` = natural mass dimension 1; `Phi_normalized=delta_phi/Phi_scale` dimensionless only after a declared scale; `e0` = J m^-3 and `alpha_Phi_K` = K per normalized Phi remain unassigned | algebraic field redefinition of the declared natural-unit scalar action | scoped identifiability no-go; not an SI derivation | prevents a canonical kinetic convention or default coefficient from becoming a fictitious thermal calibration | a source-locked observable amplitude, physical residue, or SI coefficient contract would break the current under-identification and requires a new audit | source-lock a covariant field normalization plus system-specific SI energy-density contract, or an independent non-TTG alpha calibration; then derive base `Phi -> Phi_E` |

The rescaling preserves the scalar action sector and the hypothetical normalized coordinate when both the covariant displacement and `Phi_scale` rescale. It therefore does not identify an absolute field amplitude. This audit does not identify base `Phi` with `Phi_E`, temperature, heat flux, entropy, or `R_gen`.


## Beta Symbol Separation and Non-Circularity (2026-08-11)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-017` | `beta_th = 1/(k_B T)` and `E_L = k_B T ln(2) = ln(2)/beta_th`; `beta_core != beta_th` unless a separately declared mapping is derived | `docs/core/uet_parameters.py`; `docs/core/uet_hyperbolic_phase_field.py`; `docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_Thermodynamic_Bridge.py`; `docs/scripts/audit/audit_topic13_beta_symbol_separation.py` | `beta_th` = J^-1 after externally supplied `T` in K; `E_L` = J; `beta_core` = dimensionless normalized coupling; `beta_wave` = comparator coefficient with no SI bridge declared | standard inverse-temperature/Landauer identity plus repository source audit | scoped symbol-identification no-go; not a UET beta derivation | prevents the standard Landauer identity, a normalized core coupling, or an auxiliary comparator coefficient from being silently substituted for a finite-temperature UET bridge coefficient | the legacy research print label calls a Landauer value a UET beta prediction although the current core helper explicitly rejects that derivation; neither current beta has a declared UET action/temperature/SI mapping | declare one `beta_UET` with an action term, units, finite-temperature coefficient provenance, and an observable/SI contract independent of Landauer; then audit the derivation |

This record distinguishes a standard thermodynamic inverse energy `beta_th` from
the legacy normalized core coupling `beta_core` and the hyperbolic-comparator
`beta_wave`. The standard identity can constrain a lower bound only after a
temperature is supplied; it cannot identify an independent UET coefficient.
No `Phi`, `R_gen`, temperature, heat flux, entropy, or calibration is relabeled
by this audit.


## Named Finite-Temperature beta_T13 Contract (2026-08-11)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-018` | `f_hat_T13=a_Phi(T) Phi^2/2+b_Phi Phi^4/4-g C^2 Phi/2`; `beta_T13=T0*(da_Phi/dT)|T0`; `a_Phi(T)=a_Phi(T0)+beta_T13*(T-T0)/T0`; `s=-e0 Phi^2 beta_T13/(2T0)` | `docs/core/thermal_response_beta_contract.py`; `docs/scripts/audit/audit_topic13_thermal_response_beta_contract.py` | `C,Phi,a_Phi,b_Phi,g,beta_T13` dimensionless in named normalized lane; `T,T0` = K; `da_Phi/dT` = K^-1; `e0` = J m^-3 external input; `f` = J m^-3 and `s` = J m^-3 K^-1 only after e0 is source-locked | declared finite-temperature response-functional definition, independent of Landauer | formal derivative/unit contract closed for named lane; coefficient provenance and physical correspondence open | makes one auditable meaning for beta_T13 while forbidding aliases to beta_th, beta_core, beta_wave, base covariant Phi, or R_gen | no physical value or SI map follows from declaration; entropy identity is not entropy-production positivity, SK/KMS, EOS, or transport closure | source-lock e0 and coefficient provenance, resolve base Phi correspondence, then test finite-temperature EOS/transport/KMS/entropy contracts |

The contract defines a local first-order temperature expansion only. It does
not set `beta_T13=beta_core`, use `k_B T ln(2)`, identify `Phi` with the legacy
`I` state, or claim a physical entropy-production law.


## Named Collective-Response EOS and Stability Contract (2026-08-11)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-019` | `f_hat=a_C C^2/2+b_C C^4/4+a_Phi(T) Phi^2/2+b_Phi Phi^4/4-g C^2 Phi/2`; `mu_C=a_C C+b_C C^3-g C Phi`; `mu_Phi=a_Phi Phi+b_Phi Phi^3-g C^2/2`; `H_CPhi=H_PhiC=-g C` | `docs/core/thermal_collective_response_eos.py`; `docs/scripts/audit/audit_topic13_collective_response_eos.py` | `C,Phi,a_C,b_C,a_Phi,b_Phi,g` dimensionless in the named lane; `T` = K; `e0` = J m^-3 only for physical density; Hessian is normalized-coordinate curvature | declared candidate response functional extending the named beta_T13 lane | formal EOS, mixed-derivative reciprocity, and local stability contract closed for named lane; physical coefficient provenance open | provides an explicit stability/reciprocity interface without relabeling C as charge/mass or Phi as an information/thermal field | no source coefficient, SI Phi anchor, physical charge EOS, transport, KMS, entropy production, or dissipative balance follows from local Hessian positivity | source-lock coefficients and Phi/e0 mapping, then test physical EOS and nonequilibrium closures |

`C` is deliberately called a collective coordinate, not a charge density. The
formal `mu_C` and `mu_Phi` are normalized derivatives, not measured chemical
potentials. `R_gen` is absent and does not backreact.

## Base-Phi Independent Calibration Requirement (2026-08-11)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-020` | `Phi_E = Delta_u/e0`; `Phi_E = s_material Phi_base`; `alpha_Phi_K = (e0/c_v) s_material` | `docs/core/artifacts/t13_base_phi_independent_calibration_requirement.json`; `docs/topics/0.13_Thermodynamic_Bridge/BASE_PHI_INDEPENDENT_CALIBRATION_PROTOCOL.md` | `Delta_u,e0` = J m^-3; `c_v` = J m^-3 K^-1; `Phi_E,Phi_base,s_material` = dimensionless; `alpha_Phi_K` = K per normalized base Phi | protocol-defined calibration bridge; no numerical constant supplied | open requirement, not a derivation or calibration | defines the minimum independent paired record needed before a base-Phi SI observable map can be considered | a named Phi_E coordinate or a TTG residual can be mistaken for a base-Phi calibration | obtain the paired record with locator, units, uncertainty, preprocessing, row identity, hash, and independence statement; then rerun the locked calibration audit |

The protocol is an acceptance contract only. It does not identify base `Phi`
with `Phi_E`, temperature, heat flux, entropy, or `R_gen`, and it emits no
numeric `alpha_Phi_K`.

## Formal SK/KMS and Entropy Interface (2026-08-11)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-021` | `S_SK = integral [Phi_a D_R Phi_r + i Phi_a N Phi_a/2]`; `N(omega)=coth(beta_th omega/2)*2 Im D_R`; `J_S^mu=s u^mu+q^mu/T`; `nabla_mu J_S^mu >= 0` under PSD `L` | `docs/core/thermal_sk_kms_entropy_contract.py`; `docs/core/artifacts/t13_sk_kms_entropy_contract_audit.json` | `Phi_r,Phi_a` = dimensionless contour response copies; `beta_th` = J^-1; `q` = W m^-2; `T` = K; `kappa` = W m^-1 K^-1; `J_S` = W m^-2 K^-1 | standard KMS/Onsager interface plus declared UET lane notation; no physical coefficient supplied | formal lane contract and algebraic positivity witness; not microscopic derivation | separates SK/KMS structure, entropy positivity, and exchange-current balance from physical Kubo matching | formal positivity can be mistaken for physical transport closure or a base-Phi SI map | source-lock or microscopically match coefficients, complete finite-temperature normal sector and curved 3+1, then rerun with physical units and provenance |

The contract keeps `beta_th` distinct from `beta_T13` and `beta_core`. `Phi_a`
is a contour-difference response copy, not a new physical field. `R_gen` is
absent and has no backreaction. The witness closes only the formal lane.

## Ding PBTE Author-Request Acquisition Contract (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-022` | `C_src(T) = sum_mu c_mu(T)`; `Delta_Tq = Delta_u_ph/C_src`; `Phi_E = Delta_u_ph/e0` | `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_pbte_author_request_manifest.json`; `docs/core/artifacts/t13_ding_pbte_author_request_audit.json` | `c_mu,C_src` = J m^-3 K^-1; `Delta_u_ph,e0` = J m^-3; `Phi_E` = dimensionless | published Ding notation plus a request specification; no numeric input supplied | request contract only, no derivation/calibration | checks that the external acquisition route is bounded and auditable before source acceptance | request can be mistaken for received data or independent alpha calibration | if authorized, send the request; hash and audit any returned payload before changing state |

The request package is not a data source. It does not identify base `Phi` with
`Phi_E`, does not emit `C_src`, `e0`, or `alpha_Phi_K`, and does not read Xie
2026.

## Physical Kubo Coefficient Provenance Gate (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-023` | `KuboCoefficientRecord -> constitutive coefficient` only when matched evidence passes | `docs/core/artifacts/t13_physical_kubo_coefficient_provenance_audit.json`; `docs/core/uet_covariant_superfluid_transport.py` | value and coefficient units are source-specific; temperature, chemical potential, response state, correlator locator, source path, and hash are required | external/microscopic input required; no value supplied | provenance gate passes; physical coefficient remains open | separates readiness/formula sources from physical coefficient evidence and synthetic controls | a structural Kubo source or synthetic value can be misreported as a physical UET transport coefficient | acquire one state-matched coefficient record and rerun transport/state/unit checks |

The gate does not derive a coefficient from the conservative action and does
not use synthetic controls, TTG target data, or Xie 2026 as physical evidence.

## Standard Graphite Transport Comparator (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-024` | `c_p^vol = c_p^mass rho_assumed`; `k = D c_p^vol`; `sigma_k` is reported and first-order propagated separately | `docs/core/artifacts/t13_gatech_standard_transport_comparator_audit.json`; `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/gatech_gen3csp_graphite_source_package.json`; `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/gen3csp_graphite.xlsx` | `c_p^mass` = J kg^-1 K^-1; `rho` = kg m^-3; `c_p^vol` = J m^-3 K^-1; `D` = m^2 s^-1; `k` = W m^-1 K^-1 | source-backed comparator algebra with assumed density; no UET derivation | comparator gate passes conditionally; density and c_p-to-c_v regime remain open | confirms source row, units, raw hash, reconstructed k, uncertainty separation, synthetic-control boundary, and holdout isolation | comparator could be mislabeled as UET Phi transport or Ding C_src | source-lock density/c_v regime or acquire a state-matched UET Kubo coefficient and base-Phi SI anchor |

The source-reported and first-order propagated `sigma_k` values are retained as
separate envelopes because source covariance and provider aggregation are not
locked. This comparator does not emit `Phi`, `alpha_Phi_K`, `C_src`, or a TTG
prediction.

## Covariant Transport Implementation Boundary (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-025` | `P=P(X,Phi)`; `N^mu=(Zq/lambda)xi^mu`; `T^mu_nu=f_s xi^mu xi^nu+p g^mu_nu`; `KuboRecord -> coefficient` only when matched evidence passes | `docs/core/uet_covariant_superfluid_transport.py`; `docs/core/artifacts/covariant_superfluid_transport_contract.json`; `docs/core/artifacts/t13_covariant_transport_implementation_boundary_audit.json` | implementation lane = natural units; frame = Landau; T=0 ideal sector; physical coefficient units must be source-declared | tree-level O(2) action for ideal sector; dissipative values require external/microscopic match | implementation boundary closes; physical coefficient, finite-T normal component, SI lane, and curved 3+1 remain open | prevents synthetic controls, natural-unit defaults, or T=0 ideal formulas from being promoted to physical full transport | a T=0/natural-unit interface can be mislabeled as finite-temperature SI constitutive closure | acquire state-matched Kubo record, derive normal component, and construct SI observable map |

The audit intentionally closes only the implementation boundary. It does not
emit a physical transport coefficient or use `R_gen` as transport state.

## Standard Finite-Temperature O(2) Normal Comparator (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-026` | `E_k=sqrt(k^2+m_eff(Phi)^2)`; `p_T=T integral [L(E_k-mu)+L(E_k+mu)]`; `n_T=partial p_T/partial mu`; `s_T=partial p_T/partial T`; `epsilon_T=-p_T+T s_T+mu n_T` | `docs/core/standard_o2_finite_temperature_comparator.py`; `docs/core/artifacts/t13_standard_o2_finite_temperature_comparator_audit.json`; `docs/core/uet_o2_finite_density_eos.py` | natural units; `T,mu,m_eff` = natural energy; `p_T,epsilon_T` = natural energy density; `n_T` = natural charge density; `chi_T` = charge-density per chemical-potential unit | standard free-complex-scalar grand-canonical thermodynamics, with UET `m_eff(Phi)` as an input only | standard comparator gate passes; finite-temperature UET action, condensate/normal sector, physical Kubo, SI map remain open | tests normal-domain positivity, charge/entropy derivatives, even/odd symmetries, and ontology separation | comparator can be mislabeled as UET finite-temperature closure or physical normal component | derive/source-lock UET finite-temperature action and two-fluid sector, then match Kubo/SI observables |

This comparator excludes zero-point and condensate terms and emits no
`alpha_Phi_K`, physical Kubo coefficient, SI scale, `C` relabeling, or `R_gen`
feedback.

## Action-Derived O(2) One-Loop Normal Branch (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-027` | `Omega_N^(1,T)=T integral log[(1-exp(-(E_k-mu)/T))(1-exp(-(E_k+mu)/T))]`; `E_k=sqrt(k^2+m_eff(Phi)^2)`; `partial p_N/partial Phi=-(partial m_eff^2/partial Phi)(1/2) integral[(n_-+n_+)/E_k]` | `docs/core/uet_o2_one_loop_normal_branch.py`; `docs/core/artifacts/t13_uet_o2_one_loop_normal_branch_audit.json`; `docs/core/uet_o2_finite_density_eos.py`; `docs/core/uet_covariant_matter.py` | natural units; `T,mu,m_eff` = energy; `p,Omega,epsilon` = energy density; `n` = charge density; `s` = entropy density; response derivative = action-energy density per natural Phi unit | thermal one-loop determinant from the declared conservative O(2) action mass map; no vacuum counterterm | normal-background action-derived lane passes; renormalization, condensate/two-fluid, Kubo, SK/KMS, SI remain open | verifies action mass derivative, thermodynamic derivatives, positivity, and exclusion boundary | thermal determinant can be overread as full finite-temperature UET EOS or physical transport | close renormalization and interacting finite-T action, then derive condensate/normal sector and match Kubo/SI observables |

This lane uses no `R_gen` state/feedback and emits no physical Kubo value,
`alpha_Phi_K`, or SI observable map.

## One-Loop Normal Branch Convergence (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-028` | `p in [0, 70 max(T,m_eff,|mu|)]`, Gauss-Legendre `N=256`, maximum plateau drift `<=1e-8` | `docs/core/artifacts/t13_uet_o2_one_loop_convergence_audit.json`; `docs/core/uet_o2_one_loop_normal_branch.py`; `docs/core/standard_o2_finite_temperature_comparator.py` | cutoff and momentum are natural units; declared thermodynamic outputs retain one-loop natural-unit contracts | deterministic numerical convergence policy for the thermal-only integral | convergence gate passes with reference `cutoff_factor=70`, `N=256`; vacuum/interaction physics remains open | prevents cutoff/order artifacts from being read as thermal response | low-order quadrature can drift at high cutoff; vacuum counterterm is not represented | keep reference baseline fixed and separately close renormalization/interacting finite-T response |

The convergence result is numerical evidence for the declared thermal-only
branch. It is not a renormalization proof or a physical transport coefficient.

## One-Loop Thermal UV Boundary (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-029` | `-log(1-exp(-x)) <= exp(-x)/(1-exp(-x))`; `I_0(Lambda) >= Lambda^4/(8 pi^2)`; `I_1(Lambda) >= (Lambda^2-m^2)/(4 sqrt(2) pi^2)` | `docs/core/artifacts/t13_uet_o2_one_loop_uv_boundary_audit.json`; `docs/core/uet_o2_one_loop_normal_branch.py`; `docs/core/standard_o2_finite_temperature_comparator.py` | natural-unit thermal observables and unweighted vacuum mode-integral diagnostics | analytic tail inequality and cutoff lower bounds; no counterterm constant supplied | thermal-only UV scope passes; vacuum renormalization remains open | prevents convergent thermal tails from being mistaken for a renormalized full one-loop action | omitted vacuum term could be silently treated as finite or renormalized | derive a source-backed counterterm/renormalization contract or retain the thermal-only boundary explicitly |

The audit closes the scope boundary, not the vacuum theory.  The thermal tail
is exponentially bounded on the normal branch; the omitted zero-point term has
recorded cutoff-growth lower bounds and is not used as a prediction.

## T=0 Condensate and Goldstone Ideal Lane (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-030` | `q=Z mu^2-m_eff^2`; `A^2=q/lambda`; `p=q^2/(4 lambda)`; `N^mu=(Z q/lambda) xi^mu`; `omega_G=+-c_s k` | `docs/core/artifacts/t13_uet_o2_condensate_goldstone_ideal_lane_audit.json`; `docs/core/uet_o2_finite_density_eos.py`; `docs/core/uet_covariant_matter.py`; `docs/core/uet_covariant_superfluid_transport.py` | natural units; `mu,m_eff,xi` = energy; `p` = energy density; O(2) charge/current = natural Noether units; `Phi` remains action response input | declared tree-level O(2) action and covariant phase reduction; no SI anchor or physical Kubo value supplied | T=0 ideal condensate/Goldstone lane passes; finite-T normal and dissipative physics remain open | separates tree-level ideal response from normal component and transport evidence | ideal condensate result can be mislabeled as a full finite-temperature two-fluid theory or physical Kubo closure | derive/source-lock the finite-temperature normal sector and acquire state-matched physical Kubo records; retain SI Phi and renormalization blockers |

Synthetic Kubo controls are used only to exercise the existing linear-mode
control path.  They are not physical transport evidence.

## T=0 Condensate Fluctuation Spectrum (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-031` | `det M=(omega^2-k^2)(omega^2-k^2-2q/Z)-4 mu^2 omega^2=0`; `omega_+-^2=k^2+q/Z+2mu^2 +- sqrt((q/Z+2mu^2)^2+4mu^2 k^2)` | `docs/core/artifacts/t13_uet_o2_condensate_fluctuation_spectrum_audit.json`; `docs/core/uet_o2_condensate_fluctuations.py`; `docs/core/uet_o2_finite_density_eos.py` | natural units; `omega,k,mu` = energy; `Phi` fixed response input; no SI map | quadratic expansion of the declared O(2) action at fixed Phi | determinant roots and low-k EOS matching pass; finite-T self-energy and transport remain open | checks the action spectrum independently of synthetic Kubo controls | T=0 roots can be misread as a normal-fluid or finite-T transport derivation | source-lock/derive finite-T self-energy and normal response; retain SI and renormalization blockers |

The low branch is a Goldstone mode only in the declared condensed T=0 lane;
the high branch is the mixed radial/phase mode and is not a separate physical
particle claim.

## O(2) Normal-Lane Thermodynamic Consistency (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-073` | `n=partial_mu p`; `s=partial_T p`; `epsilon=-p+T*s+mu*n`; `partial_Phi n=partial_mu(partial_Phi p)`; `partial_Phi s=partial_T(partial_Phi p)` | `docs/core/artifacts/t13_uet_o2_normal_thermodynamic_consistency_audit.json`; `docs/core/uet_o2_one_loop_normal_branch.py` | natural-unit thermodynamic densities and natural response-field derivative | action-derived thermal determinant; no external coefficient or fit | grid-level derivative, reciprocity, positivity, and Gibbs-Duhem checks pass; vacuum/condensate/transport/SI remain open | verifies internal consistency of the declared normal branch without target data | a local derivative pass can be overstated as a full finite-temperature UET closure | close renormalized/interacting and condensate/two-fluid sectors, then match physical Kubo and SI observables |

This result is a consistency closure for the normal-background lane only. It
does not derive a physical Kubo coefficient, `alpha_Phi_K`, an SI observable,
or a full finite-temperature UET EOS.

## Berut Source Package Availability Boundary (2026-08-12)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The Berut working copies in the current checkout are
classified as topic-derived summaries, not raw experimental rows. The captured
publisher surface is recorded as a Figure 3/PPT acquisition route, while the
absence of a local raw or separately exposed source-data package is explicit.

WHAT_REMAINS_OPEN: The official Figure 3 binary/hash, selected panel and axis
mapping, numeric transcription, row identity, preprocessing, and uncertainty
package remain open. No Berut numeric row is eligible for calibration.

DEPENDENCY_UNLOCKED: Berut source-acquisition decision only. No Full Topic 13,
Core, Gravity, or constitutive-transport dependency is unlocked.

STATUS: `PASS_SCOPED_BERUT_SOURCE_PACKAGE_BOUNDARY`

WHAT_CHANGED: `docs/core/artifacts/t13_berut_source_package_availability_boundary.json` records the source identity, publisher locator,
current local inventory, source-surface scope, and non-calibration policy.

EQUATION_OR_MAPPING: `E_min = k_B T ln(2)` remains an imported standard
constraint. No numeric `Delta_Tq = alpha_Phi_K * Delta_Phi` mapping is emitted.

VERIFICATION: All source identity, summary-role, no-raw-file, surface-scope,
holdout, no-fit, and no-calibration checks pass; accepted numeric rows emitted:
`0`.

CONTROLLING_BLOCKER: `berut_local_raw_or_permissioned_numeric_package_missing`

NEXT_ACTION: Archive the official Figure 3 PPT or an explicitly permitted numeric/supplement package, then select one panel and record axis ticks, selected points/curve, row identity, uncertainty, preprocessing, and SHA-256 before any source-normalized use.

CLAIM_BOUNDARY: This is a provenance and acquisition boundary, not a closed
Berut numeric row, uncertainty result, `alpha_Phi_K`, UET bridge, or external
validation.

## Berut Figure 3 Remote Binary Identity

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE

WHAT_IS_ACTUALLY_CLOSED: The official publisher Figure 3 route was
download-tested. Its remote binary identity is pinned by SHA-256, byte size,
OLE signature, retrieval date, and an explicit four-asset raster inventory.

WHAT_REMAINS_OPEN: No raster is accepted as a numeric row yet. Selected panel,
axis ticks and units, point or curve selection, digitization uncertainty,
preprocessing, and row identity remain open.

DEPENDENCY_UNLOCKED: Berut figure-acquisition route only. No numeric source,
alpha_Phi_K, Full Topic 13, Core, Gravity, or transport dependency is unlocked.

STATUS: PASS_REMOTE_FIGURE3_BINARY_IDENTITY

WHAT_CHANGED: docs/core/artifacts/t13_berut_figure3_remote_binary_identity.json records the official article/download locators,
binary hash e4bab6be849a093b7578bc52ce6df9be95dc25d83d51ecb718b4f798a37d50fa, size
479744 bytes, and embedded raster inventory.
The binary itself remains outside the repository.

EQUATION_OR_MAPPING: Figure 3 is a source-surface asset for the Berut
heat-versus-erasure-duration observable; no numeric Delta_Tq or alpha_Phi_K
mapping is emitted.

VERIFICATION: Binary identity and asset inventory checks pass; accepted numeric
rows emitted: 0; no fit, target data, calibration, or Xie 2026 holdout was used.

CONTROLLING_BLOCKER: berut_selected_panel_and_axis_tick_mapping_missing

NEXT_ACTION: Select one quantitative panel, record axis ticks and units, map selected points or curve with declared digitization uncertainty, and archive row identity and preprocessing before source-normalized use.

CLAIM_BOUNDARY: Remote binary identity only. This is not a source-normalized
numeric row, uncertainty result, calibration, prediction, or external validation.

## Fixed-Background Gaussian Finite-Temperature O(2) Lane (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-032` | `omega_+-^2=k^2+q/Z+2mu^2 +- sqrt((q/Z+2mu^2)^2+4mu^2 k^2)`; `Omega_G=T integral sum_a log(1-exp(-omega_a/T))`; `p_G=-Omega_G`; `epsilon_G=-p_G+T*s_G+mu*n_G` | `docs/core/artifacts/t13_uet_o2_condensate_gaussian_thermal_audit.json`; `docs/core/uet_o2_condensate_gaussian_thermal.py`; `docs/core/uet_o2_condensate_fluctuations.py`; `docs/core/uet_o2_finite_density_eos.py` | natural units; `T,mu,omega,k` = energy; `p,s,epsilon` = natural densities; `Phi` fixed action input; no SI map | quadratic O(2) action spectrum plus Gaussian thermal Bose determinant; no external source coefficients | fixed-background finite-T pressure, derivatives, positivity, mode roots, and convergence pass; background backreaction, renormalization, self-energy, transport, and SI remain open | establishes a finite-T action-derived quasiparticle lane without using the standard-fluid comparator as UET transport | Gaussian determinant can be overread as a self-consistent finite-T EOS or two-fluid closure | derive thermal background backreaction/self-consistent phase boundary and match physical normal/Kubo/SK/KMS sectors |

The lane uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026
holdout. It keeps `C`, `Phi`, `R_gen`, and `R_obs` in their declared roles.

## Off-Shell Gaussian O(2) Thermal Background Boundary (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-033` | `Omega_tree(A)=0.5*(m_eff(Phi)^2-Z*mu^2)*A^2+0.25*lambda*A^4`; `r_sigma=-q+3*lambda*A^2`; `r_pi=-q+lambda*A^2`; `det=(y-k^2-r_sigma/Z)*(y-k^2-r_pi/Z)-4*mu^2*y` | `docs/core/artifacts/t13_uet_o2_gaussian_offshell_background_audit.json`; `docs/core/uet_o2_gaussian_offshell_background.py`; `docs/core/uet_o2_condensate_gaussian_thermal.py`; `docs/core/uet_o2_condensate_fluctuations.py`; `docs/core/uet_o2_finite_density_eos.py` | natural units; `A,mu,T,omega,k` follow the declared O(2) action; grand potential is a natural thermodynamic density; no SI Phi map | off-shell Hessian of the declared conservative O(2) action plus thermal Bose determinant; no external coefficients | stationary-root recovery, stable-domain rejection, one-sided thermal tadpole, and quadrature convergence pass; renormalized finite-T phase boundary remains open | makes the thermal-background blocker measurable without treating fixed-background Gaussian pressure as a self-consistent EOS | tree-level stationary amplitude is not finite-T stationary under the thermal-only determinant; lower-amplitude side is unstable at the reference point | declare/derive thermal self-energy and vacuum renormalization, then solve a self-consistent finite-T phase boundary |

The audit uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared roles of `C`, `Phi`, `R_gen`, and `R_obs`.

## Conservative-Action Kubo Identifiability Boundary (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-034` | `S_cons[Phi,chi] -> P(X,Phi), N_ideal^mu, T_ideal^munu`; `J_diss^A=-L^(AB)X_B`; `nabla_mu J_S^mu=X_A L^(AB) X_B>=0` | `docs/core/artifacts/t13_transport_coefficient_identifiability_no_go.json`; `docs/core/uet_transport_coefficient_identifiability.py`; `docs/core/uet_covariant_superfluid_transport.py`; `docs/core/thermal_sk_kms_entropy_contract.py` | ideal sector = natural action units; dissipative coefficients require source-declared units and state matching; SI map remains open | conservative action fixes ideal sector; dissipative witnesses are internal underdetermined completions, not physical values | scoped structural no-go passes: two distinct PSD/positive-relaxation witnesses satisfy the formal entropy contract while differing in response | shows that entropy positivity/formal SK interface cannot identify a unique physical Kubo coefficient from the current action | a synthetic Onsager matrix or formal positivity witness could be mistaken for physical transport evidence | add a matched retarded correlator/source record or a declared microscopic open-system/SK collision-noise derivation |

The lane uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared meanings of `C`, `Phi`, `R_gen`, and `R_obs`.

## Action-Derived Normal Thermal Response Curvature (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-035` | `m_eff(Phi)^2=m^2-epsilon_nc*h*(Phi-Phi_*)`; `kappa_Phi^T=(partial_Phi m_eff^2)^2*partial_(m_eff^2)s_M`; `beta_action_natural=T*partial_T kappa_Phi^T`; `kappa_Phi=epsilon_nc*U''(Phi)+kappa_Phi^T` | `docs/core/artifacts/t13_uet_o2_normal_response_curvature_audit.json`; `docs/core/uet_o2_normal_response_curvature.py`; `docs/core/uet_o2_one_loop_normal_branch.py`; `docs/core/uet_covariant_response.py` | natural units; `Phi` has action-field mass dimension one; `kappa_Phi` has mass dimension two; `beta_action_natural` has mass dimension two; normalized `beta_T13` and SI `alpha_Phi_K` are not identified | declared covariant response map plus thermal one-loop normal determinant; no external calibration and no vacuum counterterm | action-derived normal-branch curvature, analytic derivatives, finite differences, and convergence pass; renormalization, SI, beta correspondence, and physical transport remain open | closes the natural-unit response-curvature lane without relabeling it as normalized beta or a thermal observable | the natural-unit slope could be mistaken for `beta_T13` or an SI coefficient if field normalization and observable mapping are not supplied | provide a declared normalized beta functional or independent source-backed coefficient, then close renormalization and SI Phi mapping |

The lane uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared meanings of `C`, `Phi`, `R_gen`, and `R_obs`.

## Action-Beta to Normalized beta_T13 Correspondence No-Go (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-036` | `beta_action_natural=T*partial_T(partial_Phi^2 Omega_T)` versus `beta_T13=T0*(da_Phi/dT)|T0`; required `beta_T13=F(field_normalization,free_energy_scale,temperature_unit,beta_action_natural)` | `docs/core/artifacts/t13_beta_action_normalized_correspondence_no_go.json`; `docs/core/uet_o2_beta_correspondence.py`; `docs/core/artifacts/t13_uet_o2_normal_response_curvature_audit.json`; `docs/core/artifacts/t13_thermal_response_beta_contract_audit.json` | action beta = natural mass dimension two; normalized beta = dimensionless local K-slope; `alpha_Phi_K` remains K per normalized Phi | action-derived curvature and declared candidate normalized functional have separate origins; scale map is not declared | scoped correspondence no-go passes with two distinct positive scale witnesses and no inferred physical coefficient | prevents relabeling an action slope as beta_T13 before field, energy, and Kelvin normalization are declared | scale witnesses could be mistaken for calibration if the map is silently chosen | derive/source-lock the missing scale map and beta coefficient independently of target fitting and Xie 2026 |

The no-go uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared meanings of `C`, `Phi`, `R_gen`, and `R_obs`.

## Renormalized Normal One-Loop Scheme Lane (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-074` | `V_vac^R(x)=integral[E(x)-E(x0)-(x-x0)E'(x0)-1/2*(x-x0)^2 E''(x0)] d^3k/(2*pi)^3`; `Omega_R=V_vac^R+Omega_N^(1,T)`; `kappa_Phi^R=epsilon_nc U''+kappa_Phi^T+(partial_Phi m_eff^2)^2 partial_x^2 V_vac^R` | `docs/core/artifacts/t13_uet_o2_renormalized_normal_branch_audit.json`; `docs/core/uet_o2_renormalized_normal_branch.py`; `docs/core/uet_o2_one_loop_normal_branch.py`; `docs/core/uet_o2_normal_response_curvature.py` | natural units; `x=m_eff^2`; vacuum potential is natural energy density; response curvature has natural mass dimension two; no SI alpha | declared mass-squared Taylor subtraction at `Phi_*`; no external counterterm measurement | reference conditions, mass-derivative finite difference, response curvature, convergence, and thermodynamic identities pass; microscopic matching remains open | closes a reproducible normal-branch subtraction scheme without claiming unique physical renormalization | subtracted potential is cancellation-sensitive and the scheme is not matched to interacting finite-T self-energy or physical data | derive finite-T self-energy/counterterm matching and then connect to physical Kubo, SK/KMS, entropy, SI map, and alpha | 

This lane uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared meanings of `C`, `Phi`, `R_gen`, and `R_obs`.

## Thermal-Only Quadratic Condensed Stability Boundary (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-075` | `q=Z*mu^2-m_eff(Phi)^2`; `r_pi(A)=-q+lambda*A^2`; `A_boundary^2=q/lambda`; `r_sigma(A_boundary)=2*q` | `docs/core/artifacts/t13_uet_o2_thermal_stability_boundary_audit.json`; `docs/core/uet_o2_thermal_stability_boundary.py`; `docs/core/uet_o2_gaussian_offshell_background.py`; `docs/core/uet_o2_finite_density_eos.py` | natural units; `A^2` and `q/lambda` are amplitude squared; Hessian entries are natural mass squared; no SI Phi map | declared O(2) tree-level Hessian plus thermal-only Gaussian mode witness; no interacting self-energy | analytic boundary, mode signs, below-boundary instability, one-sided thermal slope, and convergence pass; stationary finite-T backreaction remains open | closes the quadratic stability-domain boundary without calling it a phase transition or EOS closure | thermal determinant has a one-sided slope at the tree-level boundary; an interior finite-T stationary point requires self-energy/renormalized effective action | derive/source-lock thermal self-energy and solve the self-consistent stationary boundary before any phase-transition claim | 

This lane uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared meanings of `C`, `Phi`, `R_gen`, and `R_obs`.

## Collisionless O(2) Kubo Boundary (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |

## Action-Derived Dilute-Gas Kinetic Collision Lane (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-057 | E_s(k)=sqrt(k^2+m_eff^2)-s*sqrt(Z)*abs(mu); sigma_22(s)=lambda^2/(16*pi*s); Gamma_s(k)=sum_r integral[d^3p/(2*pi)^3] f_r v_rel sigma_22; D_s=(1/3) integral[d^3k/(2*pi)^3] k^2[-partial_E f_s]; K_kin=sum_s D_s/Gamma_s(k_ref) | docs/core/uet_o2_kinetic_collision_kubo.py; docs/scripts/audit/audit_topic13_uet_o2_kinetic_collision_kubo.py; docs/core/artifacts/t13_uet_o2_kinetic_collision_kubo_audit.json | natural units; lambda dimensionless; sigma_22 inverse energy squared; Gamma inverse time/energy; K_kin formal comparator; Phi has no SI map | action-derived constant-amplitude dilute-gas 2-to-2 phase-space comparator; no source rows or fitted width | CLOSED_FOR_LANE only; positivity, finite response, and quadrature/cutoff refinement pass | comparator coefficient can be mistaken for full quantum Kubo transport because final-state Bose factors, ladder vertices, condensed scattering, and microscopic SK matching are excluded | add quantum final-state factors and matched retarded/ladder response, then rerun physical transport/SK-KMS/entropy gates |

The lane is CLOSED_FOR_LANE only. The fixed reference is k_ref=max(T,m_eff,sqrt(Z)*abs(mu)); reference widths are 1.3919336977353308e-06 and K_kin=608.3842369966399 in the declared natural-unit comparator. Artifact SHA-256: 1f56e114e69e7c238d55921a3a3c2265b3e26e1655e7d69948072680499747a8.
| T13-056 | sigma(omega;gamma)=D/(gamma-i*omega); rho_JJ=2*D*omega*gamma/(gamma^2+omega^2); K_DC=D/gamma; gamma->0+ has no finite DC limit | docs/core/uet_o2_collisionless_kubo.py; docs/scripts/audit/audit_topic13_uet_o2_collisionless_kubo.py; docs/core/artifacts/t13_uet_o2_collisionless_kubo_audit.json | natural units; D is the declared static normal-response weight; gamma is a diagnostic inverse-time/energy width; Phi has no SI map | action-derived static response plus exact collisionless Drude boundary; no collision kernel or external coefficient | CLOSED_AS_NO_GO for the collisionless normal lane only | distinguishes a static witness and regulator from a physical retarded transport coefficient | a finite diagnostic width can be mistaken for a derived physical Kubo coefficient | derive a state-matched interaction collision kernel or obtain a microscopic retarded correlator with width, then rerun transport/SK-KMS |

The lane is CLOSED_AS_NO_GO only. The diagnostic widths span 0.1, 0.01, and 0.001 and produce D/gamma values that grow by 100x toward the collisionless limit. No physical transport coefficient, SI Phi map, alpha_Phi_K, or external validation is emitted. Artifact SHA-256: 122307d4c4549bc303fff9415d9c40c1f0217a6558922d6f60111cfb13ad82fb.

## Thermal Gaussian Condensate Stationarity No-Go (2026-08-12)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-038` | `x=A^2`; `x>=q/lambda`; `partial_x Omega_tree=0.5*(-q+lambda*x)>=0`; `partial_x omega_+-^2>0`; `partial_x omega_-^2>0`; `partial_x Omega_G>0` for stable Bose modes | `docs/core/artifacts/t13_uet_o2_gaussian_thermal_stationarity_no_go.json`; `docs/core/uet_o2_gaussian_thermal_stationarity_no_go.py`; `docs/core/uet_o2_gaussian_offshell_background.py`; `docs/core/uet_o2_finite_density_eos.py` | natural units; `x` is amplitude squared; `Omega` is natural density; no SI Phi map | declared tree O(2) potential and stable Gaussian determinant; no vacuum/interacting self-energy | scoped analytic no-go plus mode-derivative and finite-difference witnesses pass; conclusion explicitly limited to current branch | closes the thermal-only stationarity question as a no-go and forces a named renormalized/interacting branch for any finite-T stationary claim | a vacuum counterterm or interacting self-energy can alter the derivative and is not ruled out | derive/source-lock the named renormalized interacting branch before phase-boundary promotion | 

The no-go uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared meanings of `C`, `Phi`, `R_gen`, and `R_obs`.

## MP48 Harmonic Spectral C_src-like Reproduction (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-039` | `c_mu(T)=k_B*x_mu^2*exp(x_mu)/(exp(x_mu)-1)^2`, `C_src^DOS=N_A*integral[g(nu)c(nu,T)dnu]` | `docs/scripts/audit/audit_topic13_mp48_spectral_csrc_reproduction.py`; `docs/core/artifacts/t13_mp48_spectral_csrc_reproduction_audit.json` | `nu` = THz; `g(nu)` = modes THz^-1 per primitive cell; `c_mu` = J K^-1 per mode; result = J K^-1 mol^-1 primitive cell | source-locked CODATA constants plus MP48 deposited DOS and thermal-properties files | checked local harmonic cross-file reproduction; not Ding PBTE derivation | source-package comparator and quadrature diagnostic only | DOS grid, harmonic approximation, material volume, and source-regime mismatch can prevent equivalence to Ding `C_src`; no uncertainty is silently promoted | obtain Ding-compatible mode-resolved PBTE inputs or an accepted same-regime independent reproduction with convergence and uncertainty; keep base-Phi SI anchor and alpha open |

The lane is `CLOSED_FOR_LANE` only. Its maximum trapezoid residual against the deposited
MP48 thermal-properties rows is `0.009992863239339345`, and the maximum every-second-bin
quadrature difference is `0.014787789991730582`; these are reported envelopes, not
physical acceptance thresholds. The artifact hash is `5b2c6332fb70c6ae98749d96051cc4dbbffa04d37eed8f90e09168d35c61c091`. The result does
not emit `alpha_Phi_K`, does not use Xie 2026, and does not promote `Phi` to temperature.

## MP48 Named Phi_E Dimensional Comparator (2026-08-13)



| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-040` | `u_th(T)=N_A integral[g(nu) h nu/(exp(h nu/(k_B T))-1)dnu]`; `Phi_E=Delta_u_ph/e0(T0)`; `Delta_Tq=(e0(T0)/c_v(T0))*Phi_E` | `docs/scripts/audit/audit_topic13_mp48_phi_e_dimensional_comparator.py`; `docs/core/artifacts/t13_mp48_phi_e_dimensional_comparator_audit.json` | `u_th,e0` = J m^-3; `c_v` = J m^-3 K^-1; `Phi_E` = dimensionless; `alpha_Phi_E_K` = K per normalized Phi_E | source-locked CODATA constants plus MP48 deposited DOS, source volume, and harmonic heat-capacity package | checked local standard-physics comparator; base UET map open | dimensional-map diagnostic and named-coordinate boundary only | the base `Phi` may not equal `Phi_E`; harmonic energy is not a UET free-energy anchor; material/source regime mismatch remains possible | derive/source-lock `Phi_base -> Phi_E` with units and uncertainty or acquire a paired base-Phi/SI record; keep `alpha_Phi_K` blocked |

At `T0=300 K`, the conditional comparator gives `alpha_Phi_E_K=126.72529975005031 K`.
This number is not a UET coefficient and is not allowed to enter the `alpha_Phi_K`
gate. Artifact SHA-256: `46fad518feb670e7e3fe4faac47582f7a5e93b88985c53225d4da4e6fc7cde44`.

## MP48 Force-constant Harmonic Reconstruction (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-041` | `D_ij(q)=sum_R Phi_ij(R) exp(2*pi*i*q.R)/sqrt(m_i*m_j)`, `nu_mu=sign(lambda_mu)*sqrt(abs(lambda_mu))*conversion_factor` | `docs/scripts/audit/audit_topic13_mp48_force_constant_harmonic_reconstruction.py`; `docs/core/artifacts/t13_mp48_force_constant_harmonic_reconstruction_audit.json` | force constants = eV Angstrom^-2; masses = amu; q = dimensionless reciprocal fractional; frequency = THz | source-locked MP48 force constants and Phonopy metadata | checked harmonic reconstruction; not Ding PBTE or UET derivation | source-integrity, acoustic, Hermitian, and limited q-grid comparator | finite supercell, harmonic approximation, q-grid choice, and material-regime mismatch can prevent Ding `C_src` equivalence; no uncertainty is silently promoted | obtain Ding-compatible mode-resolved PBTE inputs or an accepted same-regime reproduction with convergence and uncertainty; keep base-Phi SI anchor and alpha open |

The lane is `CLOSED_FOR_LANE` only. The artifact hash is `3903fbbbc22476e1394305edd2c9ad3c948802d31a9a9c36c572b8eb395cedd1` and the
full-gate hash after integration is `f6005cb6225975168eaf9fdf41ff280a6a6c096c16b55129cc9a92fda01671fd`. The q-grid comparison is a
declared metadata envelope rather than an external-validation threshold. The
result does not emit `alpha_Phi_K`, does not use Xie 2026, and does not promote
`Phi` to temperature.

## NIST Graphite alpha_V Source Boundary (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-042` | `Delta_L/L[%] = -0.201 + 6.595e-4*T + 9.593e-8*T^2 - 3.427e-12*T^3`; `alpha_L=d(Delta_L/L)/dT/(1+Delta_L/L)`; `alpha_V=3 alpha_L` | `docs/scripts/audit/audit_topic13_nist_graphite_alpha_v_source_boundary.py`; `docs/core/artifacts/t13_nist_graphite_alpha_v_source_boundary_audit.json` | `T` = K; strain dimensionless; `alpha_L`, `alpha_V` = K^-1 | NIST SP 260-89 Eq. (5.5.2), Table 20 and archived PDF | checked source-boundary comparator; not UET derivation | source/provenance and standard thermodynamic geometry comparator | AXM-5Q1 state, isotropy assumption, program-level accuracy, missing `K_T`, and missing Ding sample mapping prevent `Cp -> Cv` promotion | source-lock `K_T` and material-state correspondence with uncertainty; keep alpha and base-Phi calibration separate |

Artifact hash: `392bf8c98de925ea806a86392cbf440029a47e4e32173c2839cd04ff2cb553d5`. Full-gate hash after integration: `4cc6d5b68e7ee84710da6fb357ec7b4c640ca30182835200b84b2be41507e2a8`. The lane does not emit `alpha_Phi_K` and does not read Xie 2026.

## Bosak Graphite Elastic Bulk Comparator (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-043` | `S=C_normal^-1`; `B_elastic=1/(2*S11+2*S12+4*S13+S33)` | `docs/scripts/audit/audit_topic13_graphite_elastic_bulk_modulus_source.py`; `docs/core/artifacts/t13_graphite_elastic_bulk_modulus_source_audit.json` | `C_ij` = GPa; `S_ij` = Pa^-1; `B_elastic` = Pa = J m^-3; source state = room-temperature single-crystal graphite | Bosak et al. 2007 IXS tensor, archived PDF, Table II | checked source comparator; not UET derivation and not isothermal `K_T` | source identity, unit-aware tensor inversion, and bulk-modulus reconstruction | dynamic/elastic B may not equal thermal isothermal `K_T`; no same-state `Cp/Cv` or Ding material mapping | source-lock same-state isothermal `K_T`, or derive a permitted dynamic-to-thermal conversion with matched `Cp/Cv` and uncertainty |

Artifact hash: `65238edbfb66b57c6b3c0a06f95d8b3d28d6dc613df7b83d825332aff4a996af`. The lane does not emit `K_T` or `alpha_Phi_K`, does not read Xie 2026, and does not promote `Phi` to temperature.

## Hanfland Graphite Isothermal K_T Source (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-044` | `K_T(T0,P0)=-V*(partial P/partial V)_T=dP/d(-ln V)`; source row `K_T(300 K,0)=33.8 +/- 3.0 GPa` | `docs/scripts/audit/audit_topic13_graphite_isothermal_kt_source.py`; `docs/core/artifacts/t13_graphite_isothermal_kt_source_audit.json` | `T` = K; `P` = GPa; `V` = Angstrom^3 per cell; `K_T` = GPa = 10^9 Pa | Hanfland et al. 1989 fixed-temperature powder-XRD Murnaghan EOS, archived PDF | source-locked standard thermodynamic input; no local refit and no UET derivation | source provenance, isothermal definition, scalar row identity, uncertainty, and unit boundary | natural graphite powder is not shown to be the Ding TTG sample; same-state alpha_V/density/Cp/Cv and temperature dependence remain open | map the K_T state to Ding, source-lock same-state alpha_V/density/Cp/Cv, then run Cp-to-Cv with uncertainty |

Artifact hash: `63f0518c78febda473f89f8a0c3927d14b9d98a102dc560277bcd2a9daf8c0c4`. The lane emits the declared standard `K_T` input but no `alpha_Phi_K`, does not read Xie 2026, and does not promote `Phi` to temperature.

## IHEP TPG Anisotropic Alpha_V Comparator (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-076` | `alpha_V=2*alpha_a+alpha_c`; `u(alpha_V)=sqrt((2*u(alpha_a))^2+u(alpha_c)^2)` | `docs/scripts/audit/audit_topic13_tpg_anisotropic_alpha_v_source.py`; `docs/core/artifacts/t13_tpg_anisotropic_alpha_v_source_audit.json` | `alpha_a`, `alpha_c`, `alpha_V` = K^-1; source scope approximately 25-60 deg C | IHEP 2001-32 TPG linear-expansion rows; zero covariance is an explicit comparator assumption, not source covariance | checked source comparator; not UET derivation and not same-specimen closure | source identity, anisotropic relation, range, sign, and uncertainty-boundary checks | separate axis rows, no same-state `K_T`/`Cp`/`Cv`, and no Ding material mapping | source-lock a same-specimen/same-state alpha_V and K_T pair or permitted direct volumetric heat-capacity route |

Artifact hash: `f8ed02677b5ef1aede683cc2b191538722bda56b520d1d6ba5af024638504c68`. The lane does not emit `K_T` or `alpha_Phi_K`, does not read Xie 2026, and does not promote `Phi` to temperature.

## Official Nelson-Riley Natural Graphite Alpha_V Comparator (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-045` | `alpha_a=-1.5e-6 K^-1`; `alpha_c=27.00e-6+3.05e-9*T_C`; `alpha_V=2*alpha_a+alpha_c` | `docs/scripts/audit/audit_topic13_natural_graphite_nelson_riley_alpha_v_source.py`; `docs/core/artifacts/t13_natural_graphite_nelson_riley_alpha_v_source_audit.json` | `T_C` = deg C; expansion coefficients = K^-1; comparison point = 300.15 K | Argonne ANL-5524 Table XIX, Nelson-Riley reported crystalline-graphite route | checked official table comparator; no UET derivation and no row uncertainty | source identity, table locator, temperature scope, formula reconstruction, and explicit uncertainty absence | no same-state uncertainty, no same specimen, and no Ding material mapping | source-lock same-specimen/same-state alpha_V and K_T with uncertainty or direct volumetric heat-capacity evidence |

Artifact hash: `c20b42f64b9107459b555dfaddc5150028c39b5254e4791782161b2b9861b861`. The lane does not emit `K_T` or `alpha_Phi_K`, does not read Xie 2026, and does not promote `Phi` to temperature.

## O(2) Hartree Finite-Temperature Self-Energy (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-046` | `I_T(M^2;T,mu)=1/2 integral[(n_B(E-mu)+n_B(E+mu))/E] d^3k/(2*pi)^3`; `Pi_T=(N+2)*lambda*I_T`; `M^2=m_eff^2(Phi)+Pi_T`; `dM^2/dPhi=(d m_eff^2/dPhi)/(1-dPi_T/dM^2)` | `docs/core/uet_o2_finite_temperature_self_energy.py`; `docs/scripts/audit/audit_topic13_uet_o2_finite_temperature_self_energy.py`; `docs/core/artifacts/t13_uet_o2_finite_temperature_self_energy_audit.json` | natural units; `T`, `mu`, and `M` are energy; `M^2` and `Pi_T` are energy squared; `Phi` remains an action response variable; no SI alpha | declared O(2) action and Hartree thermal tadpole; vacuum counterterm and microscopic finite-temperature scheme are not included | action-derived self-consistent normal gap, implicit response, convergence, and weak-coupling high-temperature witness pass; no microscopic matching or external validation | closes the finite-temperature Hartree self-energy lane only | vacuum subtraction, condensate/two-fluid completion, physical Kubo/SK-KMS match, SI `Phi` map, and independent `alpha_Phi_K` remain open | close the microscopic finite-temperature scheme and physical Kubo/SK-KMS interfaces without relabeling this lane as transport |

The lane is `CLOSED_FOR_LANE` only. It uses no external source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. The artifact reports gap residual `-3.551898358766792e-13` and implicit-response finite-difference error `1.1755950206360222e-09`. It does not promote `Phi` to temperature or `R_gen` to an independent state.
## O(2) Hartree Equilibrium Thermodynamic Consistency (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-047` | `Omega_H=Omega_1+(m_eff^2-M^2)I_T+(N+2)*lambda*I_T^2/2`; stationary gap; `p_H=p_1+(N+2)*lambda*I_T^2/2`; `n_H=n_1`; `s_H=s_1`; `epsilon_H=-p_H+T*s_H+mu*n_H` | `docs/core/uet_o2_finite_temperature_hartree_thermodynamics.py`; `docs/scripts/audit/audit_topic13_uet_o2_hartree_thermodynamic_consistency.py`; `docs/core/artifacts/t13_uet_o2_hartree_thermodynamic_consistency_audit.json` | natural units; pressure/energy = natural energy density; charge/entropy = natural densities; no SI alpha | declared thermal 2PI/Hartree functional from the O(2) action; vacuum term and microscopic matching excluded | pressure derivative, Maxwell, energy, stationarity, convergence, and positive equilibrium finite-difference checks pass; no physical transport matching | closes equilibrium thermodynamic consistency of the Hartree normal lane only | vacuum renormalization, unique microscopic scheme, condensate/two-fluid EOS, physical Kubo/SK-KMS, entropy-current transport, SI Phi map, and alpha remain open | close the named renormalized finite-temperature scheme, then match physical Kubo/SK-KMS and dimensional observables |

This lane is `CLOSED_FOR_LANE` only. Fixed-dressed-mass excitation susceptibility and heat capacity are kept distinct from stationary equilibrium finite-difference stability. No external rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout is used, and `Phi` is not promoted to temperature.

## O(2) Finite-Temperature Scheme Identifiability No-Go (2026-08-13)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-048` | `Delta V_a(x)=a*(x-x_*)^3/Lambda_*^2`; `Delta V_a(x_*)=partial_x Delta V_a(x_*)=partial_x^2 Delta V_a(x_*)=0`; off-reference values differ | `docs/core/uet_o2_finite_temperature_scheme_identifiability.py`; `docs/scripts/audit/audit_topic13_uet_o2_finite_temperature_scheme_identifiability.py`; `docs/core/artifacts/t13_uet_o2_finite_temperature_scheme_identifiability_no_go.json` | natural units; `x` and `x_*` = mass squared; `Lambda_*^2` = mass squared; `Delta V` = energy density; `a` dimensionless | algebraic finite-local-counterterm witness; no external source | scoped no-go passes; no physical counterterm or microscopic scheme selected | closes uniqueness/identifiability question only | physical renormalization/microscopic matching, interacting self-energy, condensate/two-fluid, Kubo/SK-KMS, entropy, SI map, alpha remain open | declare/source-lock a physical scheme and match it microscopically |

The lane is `CLOSED_AS_NO_GO` only. It demonstrates structural non-uniqueness under the current reference conditions; it does not select a physical scheme, supply external rows, or promote the named Hartree approximation to a unique theory.
Evidence artifact SHA-256: `AD00E5E1C0E2998536F82490FA56CF35022FCEC65717C2F65410A12F73FB06CA`.

## O(2) Hartree Normal-Branch One-Sided Stability Boundary (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-049` | `M^2=m_eff(Phi)^2+(N+2)*lambda*I_T`; `r_T=M^2-Z*mu^2`; `F(mu_c)=Z*mu_c^2-m_eff(Phi)^2-(N+2)*lambda*I_T(Z*mu_c^2;T,mu_c)=0` | `docs/core/uet_o2_finite_temperature_normal_stability.py`; `docs/scripts/audit/audit_topic13_uet_o2_hartree_normal_stability.py`; `docs/core/artifacts/t13_uet_o2_hartree_normal_stability_audit.json` | natural units; `T`, `mu`, `M` = energy; `r_T`, `M^2`, and `Pi_T` = energy squared; `Phi` remains action response input; no SI alpha | existing action-derived Hartree tadpole and declared determinant convention; vacuum counterterm and condensed branch excluded | one-sided critical root, Bose-domain margin, residual-sign probes, and quadrature/cutoff convergence pass; no renormalized phase-transition claim | closes the measurable normal-side stability boundary while keeping the condensed branch and physical transport separate | a Hartree normal-side boundary can be mistaken for a renormalized finite-temperature phase transition, especially because the current determinant convention requires `Z>1` for the regular witness | derive/source-lock a renormalized condensed branch, resolve the finite-temperature scheme, then match physical Kubo/SK/KMS and SI observables |

The lane is `CLOSED_FOR_LANE` only. It emits no condensed solution, physical Kubo coefficient, SI `Phi` map, `alpha_Phi_K`, target fit, or Xie 2026 holdout evidence. Reference critical values are `mu_c=0.659465499827425`, residual `1.9709581189353287e-13`, and Bose-domain margin `0.08697894909252707`; artifact SHA-256 is `d2b82c4f8b1429a091d2efeec21c450b5a1af595bf4be660c8ab4f94a1550d85`.

## O(2) Finite-Temperature Condensed Stationarity Scheme Boundary (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-050 | x=A^2; V_vac^R uses value/first/second Taylor subtraction at x_*; Delta V_a=a*(x-x_*)^3/Lambda_*^2; partial_x Omega=0 | docs/core/uet_o2_finite_temperature_stationarity_scheme.py; docs/scripts/audit/audit_topic13_uet_o2_stationarity_scheme_dependence.py; docs/core/artifacts/t13_uet_o2_finite_temperature_stationarity_scheme_dependence_audit.json | natural units; x, x_*, Lambda_*^2 are amplitude-squared lane variables; Omega is thermodynamic density; Phi has no SI map | declared internal two-scheme finite-counterterm witness; no external source or fit | CLOSED_AS_NO_GO for structural scheme identifiability only | distinguishes anchored scheme A no-stationarity witness from anchored scheme B interior stationary witness with positive modes | physical finite-temperature renormalization, condensed/two-fluid completion, Kubo/SK-KMS, entropy, SI map, alpha, and Ding C_src remain open | select/source-lock a physical finite-temperature scheme by independent microscopic matching |

The lane is not a physical phase-transition result. Both schemes share zero counterterm value, first derivative, and second derivative at x_*, while their off-reference stationarity differs. Artifact SHA-256: 884076c8400adc3611bd3a6daa2ef0f35e6721efd0a9506c3acd082049b4ac90.

## O(2) Renormalized Hartree Normal Functional (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-051 | V_vac^R uses second-order Taylor subtraction in mass squared; I_R = partial_M2(V_vac^R + Omega_1^T); M^2 = m_eff(Phi)^2 + (N+2)*lambda*I_R; p_H^R = p_1^T - V_vac^R + (N+2)*lambda*I_R^2/2; n = partial_mu p_H^R; s = partial_T p_H^R; epsilon = -p + T*s + mu*n | docs/core/uet_o2_finite_temperature_renormalized_hartree.py; docs/scripts/audit/audit_topic13_uet_o2_finite_temperature_renormalized_hartree.py; docs/core/artifacts/t13_uet_o2_finite_temperature_renormalized_hartree_audit.json | natural units; T, mu, M are energy; M^2, tadpole, and self-energy are energy squared; pressure and energy density are natural energy density; Phi has no SI map | action-derived vacuum subtraction plus stationary O(2) 2PI/Hartree normal functional; not microscopic matching | gap, functional stationarity, thermodynamic derivative, positivity, convergence, ontology, and holdout contracts pass; physical finite-temperature scheme and transport matching remain open | closes one declared interacting normal functional only | condensed/two-fluid EOS, physical Kubo/SK-KMS, entropy current/heat flux, dimensional Phi map, alpha_Phi_K, Ding C_src, and Full Topic 13 remain open | extend to the self-consistent condensed branch and match state-matched retarded Kubo/SK-KMS coefficients without promoting this lane |

This lane is CLOSED_FOR_LANE only. It combines vacuum and thermal contributions in one stationary natural-unit functional, but does not select the physical finite-temperature scheme, provide SI observables, calibrate alpha_Phi_K, validate TTG, or close Topic 13.
Artifact SHA-256: c8edc3ee3c9c9e29472c07d81271e7087c20c1c4b5281c21e2500cbc5eede5ed.

## O(2) Condensed Goldstone/Ward Boundary (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-052 | x_boundary=q/lambda; off-shell determinant (y-k^2-r_sigma/Z)(y-k^2-r_pi/Z)-4*mu^2*y=0; omega_G^2(k=0;x_boundary)=0 is the tree Ward point; the declared scheme-B stationary witness has omega_G^2(k=0)=0.05185301641084461 | docs/core/uet_o2_finite_temperature_stationarity_scheme.py; docs/core/uet_o2_gaussian_offshell_background.py; docs/scripts/audit/audit_topic13_uet_o2_condensed_goldstone_ward.py; docs/core/artifacts/t13_uet_o2_condensed_goldstone_ward_audit.json | natural units; x, r_sigma, r_pi, and omega^2 are natural energy-squared variables; T and mu are natural energy; Phi is fixed response input with no SI map | declared O(2) action determinant plus finite-temperature stationarity witness; primary literature context is Andersen and Leganger, arXiv:0810.5510; no numeric external input | CLOSED_AS_NO_GO for the current witness only; no universal no-go for future Ward-preserving schemes | rejects the current stationary witness as a broken-phase candidate while retaining the tree boundary as gapless | a stable stationary root can be mistaken for a symmetry-consistent condensate or phase transition when its Goldstone mode is gapped | implement a Ward-preserving symmetry-improved 2PI or controlled 1/N branch and rerun EOS/Kubo/SK-KMS gates |

The lane is CLOSED_AS_NO_GO only. It closes a consistency boundary for the current witness, not the condensed EOS or Topic 13. The external paper is context for the known 2PI-Hartree Goldstone issue, not a UET coefficient or calibration source. Artifact SHA-256: 93035a3c032e613820b2dac33bc0699bba2232c29853bde57755b65990b4183f.
The same audit records partial_x Omega_scheme_B(x_boundary)=-0.13207100582827716, so the current scheme cannot satisfy Ward and its own stationarity condition at that point.
Artifact SHA-256 after the incompatibility check: 968b073d053be004bcf2521ab649fddeee26ccc265dd4d4c9a5aee2b219acd06.

## Formal O(2) Ward-Constrained Condensed Stationarity (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-053 | x_W=q/lambda; a_W=-D_0(x_W)*Lambda_*^2/[3*(x_W-x_*)^2]; D_{a_W}(x_W)=0; omega_G^2(k=0;x_W)=0; one-sided D_{a_W}(x_W*(1+delta))>0 | docs/core/uet_o2_ward_constrained_condensed.py; docs/scripts/audit/audit_topic13_uet_o2_ward_constrained_condensed.py; docs/core/artifacts/t13_uet_o2_ward_constrained_condensed_audit.json | natural units; x_W, x_*, and mode squares are natural energy squared; T and mu are natural energy; a_W is dimensionless; Phi has no SI map | O(2) determinant plus algebraically Ward-constrained finite local counterterm; no target fit or external numeric input | CLOSED_FOR_LANE only; formal symmetry compatibility, not microscopic thermal closure | verifies that Ward and stationarity can coexist in one declared local formal completion and that the boundary is one-sided stable | formal Ward coefficient can be mistaken for a physical renormalization or complete condensed EOS | replace with source-backed/microscopic symmetry-improved 2PI or controlled 1/N branch, then derive full EOS and match Kubo/SK-KMS |

This lane is CLOSED_FOR_LANE only. The Ward-derived coefficient is not a fitted alpha, a physical Kubo value, or an external calibration. Artifact SHA-256: 9e1c3c8994059529da650a2c80285a1ab13a88e2850531fa586883abd5524911.

## Evidence-Chain Resynchronization (2026-08-14)

The renormalized Hartree implementation cleanup was semantics-preserving: one duplicated vacuum-term evaluation was removed, and the Hartree audit still passes with the same reference observables and tolerances. No formula ID, physical status, or claim boundary changed.
Current Hartree module SHA-256: 833517333209bd9b2e6f0deb42f0a792454769ee35400626deb18369396ce725. Current Hartree audit SHA-256: 2d63daeb2252fbb63b1f051a53d6da2c8fdd941a82aadf94141db111000e8f38.

## O(2) Ward-Constrained Coefficient State Dependence No-Go (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-054 | x_W=q/lambda; a_W(state)=-D_0(x_W;state)*Lambda_*^2/[3*(x_W-x_*)^2]; one common a must satisfy D_a(x_W;state)=0 across the declared state grid | docs/scripts/audit/audit_topic13_uet_o2_ward_coefficient_state_dependence.py; docs/core/artifacts/t13_uet_o2_ward_coefficient_state_dependence_audit.json | natural units; x_W and Lambda_*^2 are natural energy squared; a_W is dimensionless; Phi remains an effective response input with no SI map | algebraic Ward constraint evaluated across a fixed diagnostic state grid; no source rows, target fit, or holdout | CLOSED_AS_NO_GO for state-independence of the present one-counterterm construction only | six finite-temperature/response records are individually Ward-stationary, but coefficient intervals have no common intersection | the formal Ward coefficient can be mistaken for a state-independent physical renormalization scheme or condensed EOS | construct a state-independent microscopic or symmetry-improved finite-temperature scheme, then rerun condensed EOS and retarded Kubo/SK-KMS gates |

The lane is CLOSED_AS_NO_GO only. The coefficient range is -0.004429003695465447 to -0.003457384113108128, with spread 0.0009716195823573194; the residual-tolerance common interval is empty. This is a scoped boundary for the declared fixed reference and state grid, not a no-go for every higher-order or microscopic construction. Artifact SHA-256: fec9203a71d10330c63e415b2e8e264a39c392f14002a86ccbe583d79d0a4a8e.

## Fixed-Prescription Ward-Preserving Auxiliary-Field Condensed Lane (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-055 | Omega=(m_eff^2-Z*mu^2)*rho/2+lambda*rho^2/4+Omega_1^R(M^2)-(M^2-m_eff^2-lambda*rho)^2/(4*lambda); partial_rho Omega=(M^2-Z*mu^2)/2; partial_M2 Omega=I_R-(M^2-m_eff^2-lambda*rho)/(2*lambda); M^2=Z*mu^2; rho=(Z*mu^2-m_eff^2-2*lambda*I_R)/lambda | docs/core/uet_o2_auxiliary_field_condensed.py; docs/scripts/audit/audit_topic13_uet_o2_auxiliary_field_condensed.py; docs/core/artifacts/t13_uet_o2_auxiliary_field_condensed_audit.json | natural units; M^2 and I_R are energy squared; rho is amplitude squared; pressure and energy are natural densities; Phi has no SI map | action-derived auxiliary-field functional with fixed Taylor-subtracted one-loop determinant; formal leading-large-N-inspired normalization, not microscopic matching | CLOSED_FOR_LANE; six-state Ward gap, auxiliary gap, thermodynamic envelope, convergence, ontology, and no-holdout checks pass | separates a fixed-prescription formal condensed lane from state-wise counterterm tuning and physical transport claims | formal auxiliary-field equations can be mistaken for microscopic 2PI/controlled 1/N closure or a physical finite-temperature EOS | match to a microscopic symmetry-preserving 2PI or controlled 1/N construction, then rerun condensed EOS and retarded Kubo/SK-KMS gates |

The lane is CLOSED_FOR_LANE only. It uses no source rows, target curve, fit, alpha_Phi_K, or Xie 2026 holdout. The resummed Ward gap is zero across the declared state grid, but no physical Kubo coefficient, SI Phi map, or external calibration is supplied. Artifact SHA-256: 523b6b1e9202450f6d5b555657a72f3967b393e079dc8925fb179d795267d50f.

## Explicit Elastic Final-State Bose Enhancement (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-058 | B_34=(1+f_3)(1+f_4); Gamma_s^Q(k)=sum_r integral[d^3p/(2*pi)^3] f_r v_rel sigma_22 B_34; sigma_22=lambda^2/(16*pi*s) | docs/core/uet_o2_kinetic_collision_kubo.py; docs/scripts/audit/audit_topic13_uet_o2_quantum_collision_enhancement.py; docs/core/artifacts/t13_uet_o2_quantum_collision_enhancement_audit.json | natural units; f_s dimensionless; sigma_22 inverse energy squared; Gamma inverse time/energy; K_kin formal comparator; Phi is effective response, not temperature; C is not mass/charge; R_gen is derived history trace; R_obs is separate observer record | action-derived explicit elastic outgoing-state Bose factor in a constant-amplitude dilute-gas comparator; no source rows, fit, or SI calibration | CLOSED_FOR_LANE only; positive width increase and quadrature/cutoff refinement pass; not a physical Kubo derivation | verifies explicit quantum final-state enhancement separately from the classical comparator | enhancement can be mistaken for ladder-resummed microscopic transport or a physical Kubo coefficient | derive a matched retarded/ladder response and SK/KMS relation, then rerun heat-flux and entropy gates |
The lane remains natural-unit comparator evidence only. It emits no physical Kubo coefficient, SI observable, alpha_Phi_K, TTG prediction, or Xie 2026 holdout result. Artifact SHA-256: 5a74176a196435b7dcc4c8d670e2eb4b6d667b9eb611d2852cf9cd422c887760.

## Conserving Two-Channel Retarded Ladder Response (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-059 | P_perp=I-n*n^T/(n^T*n), n=(1,1); Gamma_rel=(Gamma_+ + Gamma_-)/2; L=Gamma_rel*P_perp; b_perp=P_perp*q*sqrt(D), q=(-1,+1); K_R(omega)=b_perp^T*(L-i*omega*I)^(-1)*b_perp | docs/core/uet_o2_charge_conserving_ladder_response.py; docs/scripts/audit/audit_topic13_uet_o2_charge_conserving_ladder_response.py; docs/core/artifacts/t13_uet_o2_charge_conserving_ladder_response_audit.json | natural units; T, mu, Gamma_rel, and omega are energy/inverse-time lane quantities; K_R is a formal finite-dimensional response; Phi has no SI map | action-derived corrected quantum collision width plus explicit two-channel conserving matrix-resolvent comparator; no source rows, fit, or SI calibration | CLOSED_FOR_LANE only; conserved zero mode, positive relative mode, retarded sign, DC identity, and refinement checks pass | finite-dimensional resolvent can be mistaken for microscopic Bethe-Salpeter ladder, physical Kubo, or SK/KMS transport matching | derive momentum-dependent microscopic ladder vertices and match the response to SK/KMS, entropy, heat flux, SI Phi mapping, and alpha_Phi_K without consuming Xie 2026 |

The lane is CLOSED_FOR_LANE only. Reference eigenvalues are `(0, 1.4210409948530135e-06)`, `K_R(0)=413.8909140423845`, and refined/reference real-response change is `2.5334741779713136e-06`. The conserved sum mode is exact in the declared two-channel projection; this does not establish a microscopic transport coefficient. Artifact SHA-256: 4e9109fde3d4691c5ba4fefa6ee536ee297ce14539ac3c9db70506ede415ec98.

The artifact keeps `physical_kubo_coefficient_emitted=false`, `numeric_alpha_Phi_K_emitted=false`, and `xie_2026_accessed=false`. `C`, `Phi`, `R_gen`, and `R_obs` retain their central ontology contracts.

## Momentum-Grid Action-Derived SK/KMS Interface (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-060 | w_s(k)=k^2/(2*pi^2*T)*f_s(E_k)*(1+f_s(E_k))*dk; c_(s,k)=q_s*sqrt(w_s(k)); P=I-c*c^T/(c^T*c); L=P*diag(Gamma_s(k))*P; b_(s,k)=q_s*(k/E_s(k))*sqrt(w_s(k)); b_perp=P*b; K_R(omega)=b_perp^T*(L-i*omega*I)^(-1)*b_perp; rho=2*Im(K_R); G^>=rho*(1+n_B); G^<=rho*n_B; N=rho*coth(beta_th*omega/2); sigma_formal=b_perp^T*L*b_perp/T | docs/core/uet_o2_momentum_ladder_sk_kms.py; docs/scripts/audit/audit_topic13_uet_o2_momentum_ladder_sk_kms.py; docs/core/artifacts/t13_uet_o2_momentum_ladder_sk_kms_audit.json | declared natural-unit finite momentum-grid lane; T, mu, Gamma, omega, and momentum are energy/inverse-time quantities; response, spectral density, and entropy production are formal lane quantities; Phi has no SI map; C is not mass or charge; R_gen is a derived history trace; R_obs is separate | action-derived quantum collision widths plus weighted charge-conserving projected resolvent and algebraic KMS/FDT interface; no source rows, fit, or SI calibration | CLOSED_FOR_LANE only; fixed-cutoff state-grid refinement, charge zero mode, positivity, retarded response, KMS/FDT algebra, and formal entropy witness pass | finite cutoff and omitted energy-momentum conservation can be mistaken for a microscopic Bethe-Salpeter/SK/KMS match or physical Kubo transport | derive the full energy-momentum conserving operator and microscopic vertex/SK match; then close entropy current, heat flux, dimensional Phi mapping, independent alpha_Phi_K, and authorized TTG source contracts |

The lane is CLOSED_FOR_LANE only at momentum cutoff `48.0`. It uses 64 states across two charge species, width spread `3.572274811684194`, positive-mode rate `3.845182613400187e-07`, entropy witness `4.662265988145945e-10`, and fixed-cutoff reference/refined response change `0.008022779716558905`. The algebraic KMS/FDT identities pass, but cutoff-limit convergence, full energy-momentum conservation, microscopic Bethe-Salpeter/SK matching, physical Kubo, SI Phi mapping, alpha_Phi_K, and external validation remain open. Artifact SHA-256: ecab85f83097a47104abeea8d25a289cb35f137e2c618757232b0c470b7dbffc.

The artifact records `physical_transport_coefficients_emitted=false`, `numeric_alpha_Phi_K_emitted=false`, `parameter_fitting_performed=false`, `target_data_used=false`, and `xie_2026_accessed=false`. The finite-cutoff boundary is part of the claim contract, not a hidden convergence assumption.

## Finite-Grid Charge and Four-Momentum Conserving Bethe-Salpeter Interface (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-061 | w_(s,k,n)=k^2/(2*pi^2*T)*f_s(E_k)*(1+f_s(E_k))*dk*dOmega/(4*pi); I_A=(q_s,E_k,p_x,p_y,p_z)*sqrt(w_(s,k,n)); Q=orth(I_A); P=I-Q*Q^T; L=P*diag(Gamma_s(k))*P; b_(s,k,n)=q_s*(p_x/E_k)*sqrt(w_(s,k,n)); G_R=(L-i*omega*I)^(-1); K_R=b_perp^T*G_R*b_perp; G_0=(gamma_ref*I-i*omega*I)^(-1); K_BS=gamma_ref*I-L; G_R=G_0+G_0*K_BS*G_R | docs/core/uet_o2_energy_momentum_conserving_bethe_salpeter.py; docs/scripts/audit/audit_topic13_uet_o2_energy_momentum_conserving_bethe_salpeter.py; docs/core/artifacts/t13_uet_o2_energy_momentum_conserving_bethe_salpeter_audit.json | declared natural-unit six-direction finite grid; T, mu, Gamma, omega, momentum, and energy are energy/inverse-time lane quantities; response, spectral density, and entropy production are formal; Phi has no SI map; C is not mass or charge; R_gen is a derived history trace; R_obs is separate | action-derived quantum collision widths plus finite discrete Gram projection onto charge and four-momentum invariants; algebraic Bethe-Salpeter resolvent identity and KMS/FDT interface; no microscopic transition kernel, source rows, fit, or SI calibration | finite-grid projected relaxation and algebraic ladder identity can be mistaken for a microscopic two-to-two collision kernel, Bethe-Salpeter vertex, SK action match, or physical Kubo coefficient | derive the action-derived two-to-two transition kernel with detailed balance and match its vertex to the SK/KMS response; retain finite-cutoff, entropy-current, dimensional Phi, alpha_Phi_K, and source gates |

The lane is CLOSED_FOR_LANE only. The reference has 336 states (`2*28*6`), the refined state has 384 states (`2*32*6`), invariant rank is 5 with exactly 5 zero modes, width spread is `3.5807734053859255`, positive-mode rate is `3.69167480144999e-07`, DC response is `48.44354939563658`, and entropy witness is `3.94107226021442e-10`. Fixed-cutoff radial response change is `0.011432789900851996`, angular response change is `4.286281547630234e-07`, and maximum algebraic Bethe-Salpeter residual is `2.838675109392314e-16`. Artifact SHA-256: a680c01bd50e8596a2ccc43d86e06f69c24b9785a40117f4ebe424ef5c34815b.

This closes the declared finite-grid charge and four-momentum conservation contract, not the microscopic vertex problem. The artifact keeps `microscopic_bethe_salpeter_match_completed=false`, `microscopic_sk_kms_match_completed=false`, `physical_kubo_coefficient_emitted=false`, `numeric_alpha_Phi_K_emitted=false`, `parameter_fitting_performed=false`, `target_data_used=false`, and `xie_2026_accessed=false`.

## Exact-Kinematic Action-Derived Two-to-Two Transition Kernel (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-062 | p1+p2=p3+p4; E1+E2=E3+E4; sigma_22=lambda^2/(16*pi*s); W_f=f1*f2*(1+f3)*(1+f4)*v_rel*sigma_22*dmu; W_r=f3*f4*(1+f1)*(1+f2)*v_rel*sigma_22*dmu; v_c=(+1/sqrt(w1),+1/sqrt(w2),-1/sqrt(w3),-1/sqrt(w4)); L=sum_c W_c*v_c*v_c^T; G_R=(L-i*omega*I)^(-1) | docs/core/uet_o2_action_derived_transition_kernel.py; docs/scripts/audit/audit_topic13_uet_o2_action_derived_transition_kernel.py; docs/core/artifacts/t13_uet_o2_action_derived_transition_kernel_audit.json | declared natural-unit finite exact-kinematic channel lane; mass, T, mu, momentum, and energy are energy; sigma_22 is inverse energy squared; channel rates and response are formal natural-unit quantities; Phi has no SI map; C is not mass or charge; R_gen is a derived history trace; R_obs is separate | action-derived constant-amplitude elastic cross section, exact center-of-mass kinematics, final-state Bose weights, forward/reverse detailed balance, and finite channel outer-product operator; no source rows, fit, or SI calibration | finite channel graph and algebraic ladder can be mistaken for a connected continuum collision operator, microscopic Bethe-Salpeter vertex, SK action match, or physical Kubo coefficient | connect channels into a continuum collision operator and derive/match the microscopic Bethe-Salpeter/SK vertex; retain finite-channel, entropy-current, dimensional Phi, alpha_Phi_K, and source gates |

The lane is CLOSED_FOR_LANE only. The reference contains 12 exact-kinematic channels and 48 leg states with invariant rank 5 and 44 finite-channel null modes. Maximum charge/energy/momentum residual is `1.3322676295501878e-14`, maximum detailed-balance residual is `5.691997389781759e-14`, maximum algebraic Bethe-Salpeter residual is `1.7446272552401067e-16`, and entropy witness is `5.802817311393105e-55`. The finite-channel nullspace is declared rather than hidden; connected-continuum and microscopic limits remain open. Artifact SHA-256: 03b74b8ec35685decfa8ddc2e4b518453f68b70b2547413ffde7997508dd7ded.

The artifact keeps `microscopic_bethe_salpeter_match_completed=false`, `microscopic_sk_kms_match_completed=false`, `physical_kubo_coefficient_emitted=false`, `numeric_alpha_Phi_K_emitted=false`, `parameter_fitting_performed=false`, `target_data_used=false`, and `xie_2026_accessed=false`.

## Conservative Continuum-Collocation Collision Operator (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-063 | w_(s,k,n)=k^2/(2*pi^2*T)*f_s(E_k)*(1+f_s(E_k))*dk*dOmega/(4*pi); I_A=(q_s,E_k,p_x,p_y,p_z)*sqrt(w); Q=orth(I_A); P=I-Q*Q^T; u_c=B*v_c; u_c^P=P*u_c; L_width=P*diag(Gamma_action_s(k))*P; K_transition=sum_c W_c*u_c^P*(u_c^P)^T; L_cont=L_width+K_transition; G_R=(L_cont-i*omega*I)^(-1); K_BS=gamma_ref*I-L_cont; G_R=G_0+G_0*K_BS*G_R | docs/core/uet_o2_continuum_collision_operator.py; docs/scripts/audit/audit_topic13_uet_o2_continuum_collision_operator.py; docs/core/artifacts/t13_uet_o2_continuum_collision_operator_audit.json | declared natural-unit finite-cutoff continuum-collocation lane; T, mu, Gamma, omega, momentum, and energy are energy/inverse-time lane quantities; response, spectral density, and entropy production are formal; Phi has no SI map; C is not mass or charge; R_gen is a derived history trace; R_obs is separate | action-derived quantum collision widths plus exact-kinematic channel sample, normalized interpolation, and Gram-projected conservative vertex correction; no microscopic vertex, physical Kubo, source rows, fit, SI calibration, or holdout | interpolation/Gram projection can be mistaken for a continuum-limit proof, microscopic Bethe-Salpeter vertex, SK action match, or physical Kubo coefficient | derive the continuum limit and microscopic Bethe-Salpeter/SK action match; retain entropy-current, dimensional Phi, alpha_Phi_K, and source gates |

The lane is `CLOSED_FOR_LANE` only. The reference has 96 shared basis states, 64 exact channel samples, one structural transition-support component, complete basis coverage, invariant rank 5, and exactly 5 physical zero modes. The raw mapped invariant residual is `0.05126807072913043`, the projected residual is `2.5325958237978373e-17`, the vertex trace ratio is `1.5806302954625802e-06`, the maximum algebraic Bethe-Salpeter residual is `4.513280234121269e-16`, and the entropy witness is `7.653163030092222e-10`. Fixed-cutoff refinement changes the DC response by `0.47541462972440046`; this is recorded, not promoted as continuum convergence. Artifact SHA-256: c51318e5a912bb12622fbbab53a52796aec257a46593717687f6af2df5e2bf63.

## Tree-Level Action Vertex and Formal SK/KMS/Bethe-Salpeter Interface (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-064 | `M_tree=lambda`; `sigma_22=|M_tree|^2/(16*pi*s)`; `L_cont=L_width+K_transition`; `K_BS=gamma_ref*I-L_cont`; `S_SK=integral[Phi_a D_R Phi_r+i Phi_a N Phi_a/2]`; `N=coth(beta_th*omega/2)*rho` | `docs/core/uet_o2_tree_level_bs_sk_match.py`; `docs/scripts/audit/audit_topic13_uet_o2_tree_level_bs_sk_match.py`; `docs/core/artifacts/t13_uet_o2_tree_level_bs_sk_match_audit.json` | declared natural units; lambda dimensionless action coupling; sigma inverse energy squared; response/noise/entropy formal; Phi is not temperature; C is not mass/charge; R_gen is derived; R_obs is separate | tree-level action-derived charged-sector vertex normalization, exact elastic kinematics, conservative collocation, algebraic BS identity, and formal SK/KMS/FDT interface; no source rows, fit, or SI calibration | CLOSED_FOR_LANE only; tree-level/formal interface passes while continuum, loop-renormalized microscopic matching, physical Kubo, and dimensional mapping remain open | finite-cutoff algebraic action/response matching can be mistaken for a loop-renormalized microscopic vertex or full interacting SK/KMS derivation | derive the loop-renormalized microscopic vertex and full interacting SK/KMS action match, then test continuum-limit convergence without consuming Xie 2026 |

The lane is `CLOSED_FOR_LANE` only. The action normalization residual is `1.1102230246251565e-16`, exact-channel kinematic residual is `1.4210854715202004e-14`, detailed-balance residual is `8.543090354715029e-14`, action-width decomposition residual is `2.4147484638442308e-22`, algebraic BS residual is `4.513280234121269e-16`, formal SK/KMS residual is `1.729285121923951e-16`, formal noise/FDT residual is `2.0024586688771869e-16`, and the formal entropy witness is `7.653163030092222e-10`.

The recorded continuum sequence has DC responses `(83.41842727925236, 43.76008656209477, 33.16514282309893, 31.829328610830117)` and adjacent relative changes `(0.47541462972440046, 0.2421143231506593, 0.04027765595323908)`. This is a visible nonconvergence controller, not a continuum proof. The artifact keeps `continuum_limit_completed=false`, `microscopic_bethe_salpeter_match_completed=false`, `microscopic_sk_kms_match_completed=false`, `physical_kubo_coefficient_emitted=false`, `numeric_alpha_Phi_K_emitted=false`, `parameter_fitting_performed=false`, `target_data_used=false`, and `xie_2026_accessed=false`. Artifact SHA-256: `0861c4dc1b453685ea479054919d2f42b59a2c088284c81d40a0a25244302506`.

This lane does not close `alpha_Phi_K`. The independent calibration search remains `PASS_SCOPED_NO_ELIGIBLE_PAIRED_ALPHA_RECORD` with zero eligible paired records; no base-`Phi` amplitude/SI response record with uncertainty and provenance is available.

## O(2) One-Loop Vertex and UV Boundary (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-065 | `V_abcd=lambda*(delta_ab*delta_cd+delta_ac*delta_bd+delta_ad*delta_bc)`; `B_E^Lambda(0)=integral[(1+2*n_B(E))/(4*E^3)+n_B(E)*(1+n_B(E))/(2*T*E^2)] d^3k/(2*pi)^3`; `Gamma_1PI=V-(B_s*(V.V)+B_t*(V.V)+B_u*(V.V))/2`; `V(phi_r+phi_a/2)-V(phi_r-phi_a/2)=lambda*(phi_r^2)*(phi_r.phi_a)+(lambda/4)*(phi_a^2)*(phi_r.phi_a)` | `docs/core/uet_o2_one_loop_vertex_uv_boundary.py`; `docs/scripts/audit/audit_topic13_uet_o2_one_loop_vertex_uv_boundary.py`; `docs/core/artifacts/t13_uet_o2_one_loop_vertex_uv_boundary_audit.json` | natural units; field has mass dimension one; lambda, bubble, and four-point tensor are dimensionless in 3+1; finite cutoff Lambda has energy units; Phi is not temperature; C is not mass/charge; R_gen is derived; R_obs is separate | action-derived O(2) bare tensor, Keldysh rotation, and zero-external-momentum one-loop Euclidean bubble; no counterterm or external data | CLOSED_FOR_LANE only; thermal bubble is cutoff-stable while vacuum bubble and one-loop correction grow with cutoff, so renormalized microscopic closure remains open | finite-cutoff vertex can be mistaken for a renormalized interacting vertex or finite-density charged SK/KMS match | derive/source-lock a vacuum counterterm and finite-density charged propagator/vertex, then match full interacting SK/KMS and rerun physical transport gates | |

The lane is `CLOSED_FOR_LANE` only. O(2) tensor permutation residual is `0`, rotation residual is `8.881784197001252e-16`, and tree-level contour identity residual is `3.4670477549072174e-16`. Thermal bubble relative change across the cutoff sequence is `2.9661695791593287e-14`, while vacuum bubble growth is `2.1590771346418225` and one-loop correction growth is `2.151163286423315`. Equilibrium KMS and FDT residuals are `0` and `2.1737996091473846e-16`. Artifact SHA-256: `951ba2138f42674076ba573d15411ac4f2f662396e9f2d5644e73f932a82e155`.

The result is a structural boundary, not a renormalized prediction. It keeps `one_loop_renormalized_vertex_completed=false`, `full_interacting_sk_kms_match_completed=false`, `physical_kubo_coefficient_emitted=false`, `numeric_alpha_Phi_K_emitted=false`, `parameter_fitting_performed=false`, `target_data_used=false`, and `xie_2026_accessed=false`.

## Finite-Density Charged Propagator and Vertex Scheme (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-066 | \`D_E^{-1}=(omega_n+i*mu_eff)^2+k^2+m_eff^2\`; \`E_particle=E-mu_eff\`; \`E_antiparticle=E+mu_eff\`; \`B_ch^R=B_vac(m)-B_vac(m_ref)+B_thermal(m,mu_eff)\`; \`Gamma_R^(4)=V-(B_s^R*(V.V)+B_t^R*(V.V)+B_u^R*(V.V))/2\` | \`docs/core/uet_o2_finite_density_charged_vertex.py\`; \`docs/scripts/audit/audit_topic13_uet_o2_finite_density_charged_vertex.py\`; \`docs/core/artifacts/t13_uet_o2_finite_density_charged_vertex_audit.json\` | natural units; temperature, mass, momentum, and chemical potential have energy units; bubble and vertex are dimensionless; charge density is natural charge density; Phi is not temperature; C is not mass/charge; R_gen is derived; R_obs is separate | action-derived charged normal propagator, particle/antiparticle thermal sector, and reference-subtracted one-loop vertex; no physical scheme match, fit, source row, or SI calibration | CLOSED_FOR_LANE only; stable normal branch and charged finite-density scheme pass while condensed/two-fluid, full SK/KMS, continuum, Kubo, dimensional, alpha, and source closure remain open | checks positive static gap, propagator factorization, charged KMS/FDT, charge conjugation, odd charge density, and exact neutral limit | a declared finite-density natural-unit scheme can be mistaken for unique physical renormalization or interacting transport | match the charged sector to a full interacting SK/KMS action and a declared physical renormalization; then close condensed/two-fluid and transport gates independently |

The lane is \`CLOSED_FOR_LANE\` only. The effective chemical potential is \`0.25\`, the static gap is \`0.433\`, and the sampled particle/antiparticle mode energies are \`0.5005557607533234\` and \`1.0005557607533233\`. Raw vacuum growth is \`2.543729386214107\`; charged thermal cutoff change is \`3.1691751332771736e-14\`; renormalized bubble and vertex adjacent-cutoff changes are \`1.1413950082964835e-05\` and \`3.137451738838419e-08\`.

Static propagator residual is \`1.2820127305140375e-16\`; propagator factorization residual is \`0\`; particle and antiparticle KMS residuals are both \`0\`; charge-conjugation bubble residual, odd-charge residual, neutral-limit bubble residual, and neutral-limit vertex residual are all \`0\`. Artifact SHA-256: \`5a1afa505dde3840923f67e9bded5acdbb05c01fde755396a218525b4701384d\`.

## Local Interacting SK/KMS Action Interface (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-067 | \`S_SK=S_E[Phi_r+Phi_a/2]-S_E[Phi_r-Phi_a/2]\`; \`D_tau Phi=partial_tau Phi+mu_eff*J*Phi\`; \`V(r+a/2)-V(r-a/2)=lambda*(r.r)*(r.a)+(lambda/4)*(a.a)*(r.a)\`; \`G_particle^>/G_particle^<=exp(beta*(E-mu_eff))\`; \`G_antiparticle^>/G_antiparticle^<=exp(beta*(E+mu_eff))\` | \`docs/core/uet_o2_interacting_sk_kms_action.py\`; \`docs/scripts/audit/audit_topic13_uet_o2_interacting_sk_kms_action.py\`; \`docs/core/artifacts/t13_uet_o2_interacting_sk_kms_action_audit.json\` | natural units; action density has natural energy-density units; beta is inverse energy; Phi is not temperature; C is not mass/charge; R_gen is derived; R_obs is separate | exact local O(2) contour action difference plus action-derived charged detailed balance and equilibrium KMS/FDT identities; no external source, fit, or SI calibration | CLOSED_FOR_LANE only; local contour/KMS interface passes while nonlocal influence functional, retarded self-energy, physical dissipation, condensed/two-fluid, Kubo, dimensional, alpha, and source closure remain open | checks exact r/a expansion, unitarity, reality, no pure-r interaction, r^3a and ra^3 vertices, charged KMS/FDT, detailed balance, and formal entropy witness | local action algebra can be mistaken for a nonlocal interacting influence functional or physical transport closure | derive the nonlocal SK influence functional and physical retarded/dissipative kernel, then close entropy-current and Kubo mappings independently |

The lane is \`CLOSED_FOR_LANE\` only. Contour expansion residual, unitarity residual, reality residual, and no-pure-\`r\` residual are all \`0\`; the resolved \`r^3a\` and \`ra^3\` weights are \`0.0009339120000000001\` and \`6.6780000000000008e-05\`. Particle/antiparticle KMS residuals are \`0\`; charged collision detailed-balance residual is \`2.8463221008786541e-14\`; collision KMS/FDT residuals are \`1.7292851219239511e-16\` and \`1.5019325358485805e-16\`; formal entropy witness is \`1.3611620264866121e-27\`.

The artifact keeps \`nonlocal_influence_functional_completed=false\`, \`microscopic_retarded_self_energy_completed=false\`, \`physical_kubo_coefficient_emitted=false\`, \`numeric_alpha_Phi_K_emitted=false\`, \`parameter_fitting_performed=false\`, \`target_data_used=false\`, and \`xie_2026_accessed=false\`. Artifact SHA-256: \`6131d8ffba0e365d172c52c8e97cc58fa5f3eae75432aa8875aee9bb54b6c4e2\`.

## Nonlocal SK/KMS Memory-Kernel Control (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-068 | \`S_IF=integral[Phi_a K_R Phi_r+i Phi_a N Phi_a/2]\`; \`g_R(t)=gamma_memory/memory_time*exp(-t/memory_time)*Theta(t)\`; \`K_R=kappa-chi*omega^2-i omega gamma_memory/(1-i omega memory_time)\`; \`rho=2 gamma_memory omega/(1+omega^2 memory_time^2)\`; \`N=rho*coth(beta omega/2)\` | \`docs/core/uet_o2_nonlocal_sk_kms_memory_kernel.py\`; \`docs/scripts/audit/audit_topic13_uet_o2_nonlocal_sk_kms_memory_kernel.py\`; \`docs/core/artifacts/t13_uet_o2_nonlocal_sk_kms_memory_kernel_audit.json\` | natural units; frequency and mass have energy/inverse-time units; gamma is a damping rate; memory_time is inverse energy; Phi is not temperature; C is not mass/charge; R_gen is derived; R_obs is separate | formal causal exponential memory kernel; gamma inherited from action-derived normal collision-width comparator; no target fit, external source, or SI calibration | CLOSED_FOR_LANE only; causal/KMS/FDT/positivity control passes while physical retarded self-energy, unique renormalization, condensed/two-fluid, Kubo, dimensional, alpha, and source closure remain open | checks causal support, retarded pole, damping sign, positive spectral density, transform identity, KMS/FDT, and formal entropy positivity | formal memory control can be mistaken for physical retarded self-energy or transport coefficient | obtain a state-matched microscopic retarded self-energy and entropy-current kernel; keep physical Kubo and SI/alpha mappings separate |

The lane is \`CLOSED_FOR_LANE\` only. Effective mass is \`0.7039176088151227\`, \`gamma_memory=3.0546703281336107e-06\`, \`memory_time=1.4206146400767916\`, and the memory pole imaginary part is \`-0.7039206634854508\`. Negative-time support is \`0\`; positive-time memory value is \`7.910311365058398e-07\`; spectral-density minimum is \`3.0393357701529953e-07\`; formal entropy witness is \`2.4883064269456041e-05\`.

The largest charged-memory KMS residual is \`7.488546547861213e-16\`; FDT residuals are at most \`4.2351647362715017e-22\`; causal-transform residuals are at most \`5.357171079777344e-14\`; all kernel-reality residuals are \`0\`. The collision-width source pair is \`(3.0546703281336107e-06, 3.0546703281336107e-06)\`. Artifact SHA-256: \`84081e77a4900f970a5306da97d6b24e430ff895e061dab14d6f9c278de7b74f\`.

## One-Loop Retarded Self-Energy Dissipation No-Go (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-069 | \`Sigma_R^(1)=3 lambda [I_vac^R(m_eff)+I_thermal(T,mu_eff)]\`; \`I_thermal=integral[(n_B(E-mu_eff)+n_B(E+mu_eff))/(4E)]d^3k/(2*pi)^3\`; \`Im Sigma_R^(1)=0\`; \`rho_Sigma^(1)=-2 Im Sigma_R^(1)=0\` | \`docs/core/uet_o2_one_loop_retarded_self_energy_no_go.py\`; \`docs/scripts/audit/audit_topic13_uet_o2_one_loop_retarded_self_energy_no_go.py\`; \`docs/core/artifacts/t13_uet_o2_one_loop_retarded_self_energy_no_go_audit.json\` | natural units; thermal tadpole and self-energy have mass-squared units; frequency has energy/inverse-time units; Phi is not temperature; C is not mass/charge; R_gen is derived; R_obs is separate | local quartic action-derived one-loop tadpole; structural no-go for dissipation; no fit, source row, or SI calibration | CLOSED_AS_NO_GO; one-loop local tadpole is real and frequency independent, so it cannot supply a nonzero dissipative spectral density | finite charged normal-domain tadpole is finite and positive; imaginary self-energy and spectral part are exactly zero across the declared frequency grid | one-loop real part can be mistaken for a physical dissipative self-energy or Kubo kernel | derive the two-loop sunset self-energy or obtain a source-locked microscopic retarded correlator; keep the zero one-loop spectral result as a no-go, not a transport prediction |

The result is \`CLOSED_AS_NO_GO\`, not a transport pass. Effective mass is \`0.7039176088151227\`, effective chemical potential is \`0.25\`, cutoff is \`33.78804522312589\`, thermal tadpole is \`0.00022235021208668495\`, and the real one-loop self-energy is \`0.000533640509008044\` at every sampled frequency. Imaginary self-energy and spectral-density arrays are identically zero; external-frequency-independence residual is \`0\`.

This closes the structural one-loop route only. The artifact keeps \`dissipative_self_energy_completed=false\`, \`two_loop_sunset_or_microscopic_source_required=true\`, \`physical_kubo_coefficient_emitted=false\`, \`numeric_alpha_Phi_K_emitted=false\`, \`target_data_used=false\`, and \`xie_2026_accessed=false\`. Artifact SHA-256: \`f240e594ea1c167cd7aeed88028b636b9ee25cfe1a2925087b4e05ae2bf7189f\`.

## Finite-Channel Two-Loop Sunset Cut (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-070 | \`W_>^(2)=integral dPi_1...dPi_4 delta^4(P_in-P_out)|M_22|^2 f1*f2*(1+f3)*(1+f4)\`; \`W_<^(2)=integral dPi_1...dPi_4 delta^4(P_in-P_out)|M_22|^2 f3*f4*(1+f1)*(1+f2)\`; \`W_cut^(2)=0.5*(W_>^(2)+W_<^(2))>0\`; \`W_>^(2)/W_<^(2)=1\` on the declared elastic equilibrium channels | \`docs/core/uet_o2_two_loop_sunset_cut.py\`; \`docs/scripts/audit/audit_topic13_uet_o2_two_loop_sunset_cut.py\`; \`docs/core/artifacts/t13_uet_o2_two_loop_sunset_cut_audit.json\`; \`docs/core/uet_o2_action_derived_transition_kernel.py\` | natural units; temperature, mass, momentum, chemical potential, energy, and formal rates use the action lane; \`Phi\` is not temperature; \`C\` is not mass or charge; \`R_gen\` is derived; \`R_obs\` is separate | action-derived order-lambda^2 finite-channel elastic phase-space cut using separately evaluated forward/reverse Bose weights; no source rows, fit, SI calibration, or holdout | CLOSED_FOR_LANE; all declared channels have positive cut weight, detailed balance passes, and inherited conservative/KMS/FDT/entropy witnesses remain valid | a finite-channel cut can be mistaken for the continuum 1PI sunset self-energy, a renormalized physical damping coefficient, or a Kubo/TTG observable | derive the continuum 1PI sunset integral with explicit regulator/subtraction and match its retarded KMS/entropy kernel; keep physical Kubo, dimensional \`Phi\`, alpha, and source gates independent |

The lane is \`CLOSED_FOR_LANE\` only. At the reference state (T,mu,Phi)=(0.22,0.25,0.15), the 12-channel forward, reverse, and symmetric cut totals are \`2.133294206254412e-18\`, \`2.1332942062544197e-18\`, and \`2.1332942062544158e-18\`; the maximum detailed-balance residual is \`1.755777910152043e-14\`. The inherited conservation residual is \`6.75000790405693e-29\`, KMS/FDT residuals are \`1.3467686071081029e-16\` and \`1.5206645789855688e-16\`, and the formal entropy witness is \`2.2494043957344814e-18\`.

This closes the first nonzero action-derived finite-channel phase-space cut after the one-loop tadpole no-go. It does not emit \`Im Sigma_R^(2)\`, a continuum-limit self-energy, physical Kubo coefficient, entropy-current/heat-flux balance, dimensional \`Phi\` map, \`alpha_Phi_K\`, TTG prediction, or Xie 2026 holdout result. Artifact SHA-256: \`23f01a422f3b217e3065bf531a29182496083cfabb1bc145ce8cb25fe8f5d73c\`.

## Finite-Channel Entropy Balance and H-Theorem (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-071 | \`A_c=log(W_f,c/W_r,c)\`; \`sigma_c=(W_f,c-W_r,c)*A_c/T>=0\`; \`partial_mu S^mu_discrete=sum_c sigma_c\`; equilibrium \`W_f=W_r\Rightarrow A_c=sigma_c=0\`; internal witness \`W_f->W_f exp(+a_c/2), W_r->W_r exp(-a_c/2)\` | \`docs/core/uet_o2_finite_channel_entropy_balance.py\`; \`docs/scripts/audit/audit_topic13_uet_o2_finite_channel_entropy_balance.py\`; \`docs/core/artifacts/t13_uet_o2_finite_channel_entropy_balance_audit.json\` | natural units; temperature is energy; channel rates and entropy production are formal natural-unit quantities; entropy current is not a covariant SI current; \`Phi\` is not temperature; \`C\` is not mass/charge; \`R_gen\` is derived; \`R_obs\` is separate | action-derived finite-channel H-theorem identity with an explicitly declared internal affinity witness; no source rows, fit, SI flux, or holdout | CLOSED_FOR_LANE; all channel entropy terms are nonnegative, perturbed production is positive, the balance identity closes, and inherited conservation/KMS/FDT controls pass | a finite-channel entropy identity can be mistaken for a covariant entropy current, physical heat flux, or dissipative transport coefficient | derive the covariant continuum entropy current and heat-flux balance from the retarded/KMS kernel; keep physical Kubo, dimensional \`Phi\`, alpha, and source gates independent |

The lane is \`CLOSED_FOR_LANE\` only. At the reference state with affinity scale \`0.05\`, the equilibrium entropy-production witness is \`3.5592569872372884e-52\`, the internal positive-affinity production is \`2.272374294421268e-27\`, the entropy-balance divergence is \`2.2723742944212683e-27\`, and the balance residual is \`3.5873240686715317e-43\`. The minimum channel production is \`7.6677620444810345e-67\`; detailed-balance, conservation, KMS, and FDT residuals are at most \`1.7563953011715103e-14\`, \`8.402120450629076e-32\`, \`1.3467686071081029e-16\`, and \`1.1629753146715762e-16\` respectively.

## Continuum Neutral On-Shell Sunset Cut (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-072 | `p=(E_p,0,0,0)`, `E_p=m_eff`; `Gamma_>^cut=integral d^3k/(2*pi)^3 n_k v_rel sigma_22 <(1+n_3)(1+n_4)>_CM`; `Gamma_<^cut=integral d^3k/(2*pi)^3 (1+n_k) v_rel sigma_22 <n_3 n_4>_CM`; `rho_cut=2*E_p*(Gamma_>-Gamma_<)`; `N_cut=2*E_p*(Gamma_>+Gamma_<)`; `Gamma_>/Gamma_<=exp(beta*E_p)` | `docs/core/uet_o2_continuum_sunset_cut.py`; `docs/scripts/audit/audit_topic13_uet_o2_continuum_sunset_cut.py`; `docs/core/artifacts/t13_uet_o2_continuum_sunset_cut_audit.json` | declared natural units; temperature, mass, momentum, energy, and cutoff have energy units; cut rates and spectral/noise quantities use the declared formal natural-unit normalization; `Phi` is not temperature; `C` is not mass or charge; `R_gen` is derived; `R_obs` is separate | action-derived neutral normal-state elastic 2-to-2 on-shell phase-space quadrature with independent radial, CM-angle, and cutoff refinements; no source rows, fit, SI calibration, or holdout | CLOSED_FOR_LANE; neutral p=0 continuum on-shell cut, KMS ratio, positive spectral/noise cut, and numerical convergence checks pass | on-shell continuum cut can be mistaken for the full 1PI retarded self-energy, real-part subtraction, off-shell analytic continuation, physical Kubo coefficient, or thermal observable map | derive and match the full 1PI retarded self-energy including real-part subtraction and off-shell continuation; then connect its KMS kernel to covariant entropy/heat-flux balance while keeping alpha/source/holdout gates independent |

The lane is `CLOSED_FOR_LANE` only. At `T=0.22`, neutral `mu=0`, `Phi=0.15`, and the declared O(2) configuration, `m_eff=E_p=0.7039176088151227`, radial cutoff is `16.894022611562946`, and the greater/lesser cut weights are `9.52491443174392e-07` and `3.8840193632612374e-08`. The spectral and noise cuts are `1.2862704057367969e-06` and `1.3956315906479364e-06`.

The KMS ratio is `24.523344352604553` against target `24.52334435260456`, with residual `2.8974136869086344e-16`. Independent radial, angular, and cutoff refinement residuals are `1.2354253257923907e-10`, `0`, and `1.7723202010929002e-09`, below the unchanged convergence threshold `1e-8`. This closes the declared on-shell continuum cut only; it does not emit a full 1PI self-energy, real-part subtraction, off-shell match, physical Kubo coefficient, covariant entropy current, heat flux, SI `Phi` map, `alpha_Phi_K`, TTG prediction, or Xie 2026 holdout result. Artifact SHA-256: `5944a7a18f8d657671a7c06f11fde6d7fa1c6d79cd94bc21dbf9c57d70bac663`.


The positive-affinity construction is an internal formal witness, not a measured gradient. It does not emit a covariant entropy current, physical heat-flux balance, physical Kubo coefficient, dimensional \`Phi\` map, \`alpha_Phi_K\`, TTG prediction, or Xie 2026 holdout result. Artifact SHA-256: \`7a21a03c87c0b39d619cb23bc459643a8c41b7ae792beed88425e0129996968d\`.
## Formal Subtracted Sunset Dispersion Interface (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-081 | `s(omega,k)=omega^2+m_eff^2+2*omega*E_k`; `rho_cut=2*omega*(Gamma_>-Gamma_<)`; `N_cut=2*omega*(Gamma_>+Gamma_<)`; `Sigma_R^eta=integral_0^Omega dnu/pi*rho_cut(nu)*[1/(omega-nu+i*eta)-1/(omega+nu+i*eta)]`; `Sigma_R,sub(omega;omega_*)=Sigma_R^eta(omega)-Sigma_R^eta(omega_*)` | `docs/core/uet_o2_sunset_dispersion_interface.py`; `docs/core/uet_o2_sunset_dispersion_interface_verified.py`; `docs/scripts/audit/audit_topic13_uet_o2_sunset_dispersion_interface.py`; `docs/core/artifacts/t13_uet_o2_sunset_dispersion_interface_audit.json` | declared natural units; temperature, mass, momentum, energy, and regulator eta have energy units; `Phi` is not temperature; `C` is not mass or charge; `R_gen` is derived; `R_obs` is separate | action-derived neutral elastic cut extended to a finite-regulator formal off-shell rest-energy dispersion interface; no source rows, fitting, SI calibration, or holdout | CLOSED_FOR_LANE only; KMS, spectral/noise positivity, retarded sign, reference subtraction, on-shell matching, and composite-quadrature convergence pass | a formal dispersion interface can be mistaken for a full 1PI self-energy, physical renormalization, Kubo coefficient, or thermal observable | derive the full 1PI retarded self-energy, zero-regulator limit, microscopic off-shell matching, and physical Kubo/entropy/observable maps independently |

The lane deliberately uses `eta=0.025` as a declared numerical regulator. Its interface status is not a physical zero-regulator self-energy and does not emit `alpha_Phi_K`, a TTG prediction, or an external validation claim.

Artifact SHA-256: `f63e6a0fe32727dbf79652d70a3eff2c8cc96050181a32e1580a461ff10fbdd8`.
## Action-Normalized O(2) Sunset Spectral Interface (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-082 | `W_int=lambda*(chi_a chi_a)^2/4`; `V_abcd=2*lambda*(delta_ab*delta_cd+delta_ac*delta_bd+delta_ad*delta_bc)`; `M2_action=sum_{b,c,d}|V_abcd|^2/(1+delta_cd)=28*lambda^2`; `sigma_action=M2_action/(16*pi*s)`; `Sigma_R,sub2=Sigma_R^eta(omega)-Sigma_R^eta(omega_*)-(omega^2-omega_*^2)*dSigma_R^eta/d(omega^2)|_omega_*` | `docs/core/uet_o2_action_sunset_1pi_spectral.py`; `docs/scripts/audit/audit_topic13_uet_o2_action_sunset_1pi_spectral.py`; `docs/core/test/test_topic13_uet_o2_action_sunset_1pi_spectral.py`; `docs/core/artifacts/t13_uet_o2_action_sunset_1pi_spectral_audit.json` | natural units; lambda and the contact matrix element are dimensionless; cross section has inverse-energy-squared units; cut rate has energy units; spectral density uses the declared natural-unit cut normalization; `Phi` is not temperature; `C` is not mass/charge; `R_gen` is derived; `R_obs` is separate | action-derived O(2) contact tensor with explicit species sum and identical-final-state symmetry factor, neutral thermal phase-space cut, and finite-regulator twice-subtracted interface; no source rows, fit, SI calibration, or holdout | CLOSED_FOR_LANE; vertex normalization, KMS, positivity, retarded sign, reference subtraction, derivative subtraction, on-shell comparator mapping, and quadrature convergence pass | an action-normalized spectral interface can be mistaken for a full physical 1PI self-energy, unique renormalization, Kubo coefficient, or TTG observable | derive the microscopic 1PI retarded self-energy and physical zero-regulator/renormalization match; then connect it to SK/KMS entropy-current and heat-flux balance while keeping alpha/source/holdout gates independent |

The `28*lambda^2` result is an explicit normalization mapping, not a replacement of the old comparator. The lane remains natural-unit and internal; it emits no physical Kubo coefficient, SI map, `alpha_Phi_K`, TTG validation, or Xie 2026 holdout result. Artifact SHA-256: `5475be102f350094e24f5607dfed18a133b7e2dd35ada519fff36610c45d0be5`.

The full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with `PARTIAL` closure; downstream major-result dependency audit remains blocked.
## Action-Matched O(2) Sunset Zero-Eta and Subtraction Interface (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-077 | `1/(x+i0)=PV(1/x)-i*pi*delta(x)`; `K(s,nu)=1/(sqrt(s)-nu+i0)-1/(sqrt(s)+nu+i0)`; `Sigma_R,sub2(s)=integral dnu/pi*rho(nu)*[K(s,nu)-K(0,nu)-s*dK/ds(0,nu)]`; `K(0,nu)=-2/nu`; `dK/ds(0,nu)=-2/nu^3`; `Im Sigma_R,sub2(omega)=-rho(omega)` | `docs/core/uet_o2_action_sunset_zero_eta.py`; `docs/scripts/audit/audit_topic13_uet_o2_action_sunset_zero_eta.py`; `docs/core/test/test_topic13_uet_o2_action_sunset_zero_eta.py`; `docs/core/artifacts/t13_uet_o2_action_sunset_zero_eta_audit.json` | natural units; invariant `s` and the self-energy response have energy-squared units in the declared lane; the cut spectral density is in the declared action-normalized natural-unit convention; `Phi` is not temperature; `C` is not mass/charge; `R_gen` is derived; `R_obs` is separate | action-matched O(2) contact tensor, continuum thermal sunset cut, distributional retarded prescription, analytic principal-value pole treatment, and declared BPHZ-like invariant subtraction; no source rows, fit, SI calibration, or holdout | CLOSED_FOR_LANE; KMS, positivity, retarded imaginary sign, subtraction conditions, distributional cut match, and principal-value convergence pass | a zero-eta/subtracted interface can be mistaken for a unique physical renormalized 1PI self-energy, Kubo coefficient, or TTG observable | complete the microscopic off-shell 1PI action derivation and match its subtraction to SK/KMS and physical transport; keep dimensional, alpha, source, and holdout gates independent |

This lane supplies an analytic principal-value control rather than an arbitrary finite pole-exclusion radius. It still emits no unique physical counterterm, physical Kubo coefficient, SI map, `alpha_Phi_K`, TTG validation, or Xie 2026 holdout result. Artifact SHA-256: `0d886b8c99cffbf1384779bbd4a75f1c31362051785ff95e3a12a83fc0a5609f`.

The full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with `PARTIAL` closure; downstream unlock remains false.
## Action-Derived O(2) 1PI Sunset Tensor Interface (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-078 | `V_abcd=2*lambda*(delta_ab*delta_cd+delta_ac*delta_bd+delta_ad*delta_bc)`; `S_ab=sum_ijk V_aijk V_bijk=12*(N+2)*lambda^2*delta_ab`; `Sigma_sunset,ab^(2)=S_ab/6*I3(p)=2*(N+2)*lambda^2*delta_ab*I3(p)`; `Sigma_R,ab(s)=Sigma_ab(s)-Sigma_ab(s_*)-(s-s_*)*dSigma_ab/ds|s_*`; `s=p^2=omega^2` | `docs/core/uet_o2_action_1pi_sunset_tensor.py`; `docs/scripts/audit/audit_topic13_uet_o2_action_1pi_sunset_tensor.py`; `docs/core/test/test_topic13_uet_o2_action_1pi_sunset_tensor.py`; `docs/core/artifacts/t13_uet_o2_action_1pi_sunset_tensor_audit.json` | natural 3+1 units; `lambda`, vertex tensor, `delta_Z`, and `delta_lambda` are dimensionless; `I3`, `Sigma`, and `delta_m2` have energy-squared units; `s` has energy-squared units; `Phi` is not temperature; `C` is not mass/charge; `R_gen` is derived; `R_obs` is separate | action-derived O(N) species contraction and explicit sunset symmetry factor; local two-point counterterm power-counting interface; no loop data, fit, SI calibration, or holdout | CLOSED_FOR_LANE; tensor contraction, O(2) diagonal/off-diagonal structure, `1/6` factor, counterterm basis, and invariant subtraction-variable match pass | tensor prefactor can be mistaken for the full off-shell loop or for a physical renormalization/transport coefficient | evaluate and regulate `I3(p)`, match its retarded continuation and subtraction to SK/KMS, then test physical Kubo/entropy and SI mappings independently |

The `8*lambda^2` O(2) prefactor is the sunset 1PI tensor coefficient after the explicit `1/6` graph symmetry factor. The `28*lambda^2` action scattering sum remains a separate comparator and is not silently identified with the 1PI coefficient. Artifact SHA-256: `05faeda1a55c07aa0055b15fe0c1e3155f8fe4b0cef0f99ec1f037f0bf7dbdde`.

The full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with `PARTIAL` closure; no downstream dependency is unlocked.
## Regulated Euclidean Off-Shell O(2) 1PI Sunset (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-079 | `D=alpha*beta+alpha*gamma+beta*gamma`; `I3_E(s;Lambda)=1/(4*pi)^4*integral_{alpha_i>=Lambda^-2} d^3alpha D^-2 exp[-m^2*(alpha+beta+gamma)-s*alpha*beta*gamma/D]`; `Sigma_E,R,ab(s)=Sigma_E,ab(s)-Sigma_E,ab(s_*)-(s-s_*)*dSigma_E,ab/ds|s_*` | `docs/core/uet_o2_action_1pi_sunset_euclidean.py`; `docs/scripts/audit/audit_topic13_uet_o2_action_1pi_sunset_euclidean.py`; `docs/core/test/test_topic13_uet_o2_action_1pi_sunset_euclidean.py`; `docs/core/artifacts/t13_uet_o2_action_1pi_sunset_euclidean_audit.json` | natural Euclidean 3+1 units; `alpha,beta,gamma` have inverse-energy-squared units; `Lambda` has energy units; `I3_E` and `Sigma_E` have energy-squared units; `s` has energy-squared units; `Phi` is not temperature; `C` is not mass/charge; `R_gen` is derived; `R_obs` is separate | action-derived equal-mass sunset, symmetric proper-time cutoff, numerical log-Schwinger quadrature, and invariant BPHZ subtraction; no thermal source, fit, SI calibration, or holdout | CLOSED_FOR_LANE; finite off-shell Euclidean loop, subtraction conditions, nonzero response, cutoff sequence, and refined quadrature pass | Euclidean off-shell result can be mistaken for retarded continuation or unique physical renormalization | derive and verify retarded `i0` continuation/discontinuity, then match finite-T SK/KMS and physical transport/entropy independently |

This is the first lane in the current wave that evaluates the off-shell loop integral itself rather than only its cut/tensor interface. It remains a regulated Euclidean result; the retarded and finite-temperature physical branches are not emitted. Artifact SHA-256: `fee12dfa1fea3ee455e45106f573c3fa841c0e2305fe4fa2391fa341856246e4`.

The full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with `PARTIAL` closure; no downstream dependency is unlocked.
## Vacuum Retarded O(2) Sunset Discontinuity Interface (2026-08-14)

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T13-080 | `s_th=9*m^2`; `Phi_3(s)=1/(128*pi^3*s)*integral ds12 sqrt(lambda(s,s12,m^2))*sqrt(lambda(s12,m^2,m^2))/s12`; `rho_disp=2*(N+2)*lambda^2*Phi_3/(2*pi)`; `Sigma_R(s)=integral_{s_th}^infty dsprime*rho_disp(sprime)/(sprime-s+i0)`; `Im Sigma_R=-pi*rho_disp` | `docs/core/uet_o2_action_1pi_sunset_retarded.py`; `docs/scripts/audit/audit_topic13_uet_o2_action_1pi_sunset_retarded.py`; `docs/core/test/test_topic13_uet_o2_action_1pi_sunset_retarded.py`; `docs/core/artifacts/t13_uet_o2_action_1pi_sunset_retarded_audit.json` | natural vacuum 3+1 units; `s`, mass squared, phase space, spectral measure, and self-energy have energy-squared units; `Phi` is not temperature; `C` is not mass/charge; `R_gen` is derived; `R_obs` is separate | action-derived equal-mass three-body cut, retarded `i0` convention, and subtracted spacelike dispersion; no thermal source, fit, SI calibration, or holdout | CLOSED_FOR_LANE; threshold support, negative imaginary sign, spacelike dispersion, Euclidean matching, and quadrature convergence pass | vacuum discontinuity can be mistaken for the full above-threshold principal-value real part or finite-temperature physical self-energy | evaluate the above-threshold PV real part, then perform finite-temperature SK/KMS and unique-renormalization matching |

This lane supplies the retarded discontinuity that the finite proper-time Euclidean regulator cannot emit by itself. It remains a vacuum, lane-level result; the above-threshold PV real part and finite-temperature physical branches are not emitted. Artifact SHA-256: `651fd640f52a67f054ba56995b0f48be87bbb9fe5e302674f7573af41d4fce8b`.

The full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with `PARTIAL` closure; no downstream dependency is unlocked.

## T13-081 - Vacuum Retarded O(2) Sunset Principal-Value Real-Part Interface
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_VACUUM_RETARDED_SUNSET_DISCONTINUITY_LANE`; this does not close Full Topic 13.
WHAT_IS_ACTUALLY_CLOSED: The above-threshold vacuum retarded real part is evaluated by subtracting the pole analytically and integrating the regularized spectral remainder with the action-derived O(2) measure.
WHAT_REMAINS_OPEN: Finite-temperature retarded 1PI, SK/KMS, unique physical renormalization, Kubo/transport, entropy-current/heat-flux balance, SI mapping, independent `alpha_Phi_K`, source provenance, and external validation.
DEPENDENCY_UNLOCKED: Vacuum PV real-part interface only; no Core, Gravity, full transport, Galaxy, SI, alpha, source, or external-validation dependency is unlocked.
STATUS: `PASS_ACTION_DERIVED_O2_VACUUM_RETARDED_SUNSET_DISCONTINUITY_LANE`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with `PARTIAL` closure.
WHAT_CHANGED: Added the analytic pole-subtraction equation, PV state/convergence fields, verifier checks, and full-gate/register integration. The branch remains natural-unit and action-derived.
EQUATION_OR_MAPPING: `K_sub(sprime)=1/(sprime-s)-1/(sprime-r)-(s-r)/(sprime-r)^2`, `r=-s_*`; `PV Sigma_R^sub(s)=integral [rho_disp(sprime)-rho_disp(s)] K_sub(sprime) dsprime + rho_disp(s) A`; `A=ln((s_th-r)/abs(s_th-s))-(s-r)/(s_th-r)`.
VERIFICATION: PV real part `0.0002769418930978005`; inner residual `1.7004689958380086e-06`; outer residual `2.788057860796576e-08`; Euclidean match residual `0.0013668039936996557`; retarded verifier and focused test pass.
CONTROLLING_BLOCKER: `full_finite_temperature_retarded_1PI_SK_KMS_and_unique_physical_renormalization_missing`; `alpha_Phi_K` remains an independent open calibration gate.
NEXT_ACTION: Derive the finite-temperature retarded/advanced/Keldysh continuation and SK/KMS match before emitting physical transport or entropy coefficients.
CLAIM_BOUNDARY: Lane-level vacuum PV interface only; not full physical retarded self-energy, unique renormalization, transport, entropy-current closure, SI, `alpha_Phi_K`, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module `faa8ebe67b6e816b66ad19f96f22242f88dc91aeba48c0cb2046fbcdb5b41932`; verifier `51d0ddc2dd3ac661f3089d22daf12ad5ea388b177df493c84393e2a2f64f939b`; artifact `fd1459deea427d60695e89631c68755444542c386199e695326a24f614b1ffca`; full gate `14880545c1a24ae79ad55c9e58f394f81bf74084b156734d9ac07ed5d0c5e030`; register `74101a54b8a74e337dbfb1fbdbf61452c3e8afbb1e014f8cf9082db0adf4077e`; dependency `a375552b4c940d6fc3496ff32e7c035a4adbd6f648e349f42914f4c4a9961f9e`.

## T13-082 - Finite-Temperature O(2) Sunset 1<->3 SK/KMS Channel
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_THREE_BODY_SUNSET_SK_KMS_LANE`; this does not close Full Topic 13.
WHAT_IS_ACTUALLY_CLOSED: Bose-weighted finite-temperature greater/lesser measures on the action-derived equal-mass three-body phase space, channel KMS/FDT identities, retarded sign, and vacuum normalization.
WHAT_REMAINS_OPEN: Other thermal cuts, full finite-temperature 1PI, real-part subtraction, unique renormalization, physical Kubo/transport, entropy-current/heat-flux balance, SI mapping, independent `alpha_Phi_K`, source provenance, and external validation.
DEPENDENCY_UNLOCKED: Named thermal `1 <-> 3` channel only; no Core, Gravity, full transport, Galaxy, SI, alpha, source, or external-validation dependency is unlocked.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_THREE_BODY_SUNSET_SK_KMS_LANE`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with `PARTIAL` closure.
WHAT_CHANGED: Added explicit thermal phase-space integration retaining the pair-rest-frame angle, channel contract equations, verifier/artifact, regression tests, and registry/full-gate integration.
EQUATION_OR_MAPPING: `rho_>=prefactor/(2*pi)*integral dPhi_3 prod(1+n_i)`; `rho_<=prefactor/(2*pi)*integral dPhi_3 prod(n_i)`; `log(rho_>/rho_<)=beta_th*sqrt(s)`; `N=(rho_>-rho_<)*coth(beta_th*sqrt(s)/2)`; `Im Sigma_R,T=-pi*(rho_>-rho_<)`.
VERIFICATION: KMS log residual `1.7763568394002505e-15`; FDT residual `1.8151885566908842e-16`; normalization residual `1.3737469372946146e-06`; quadrature residuals `1.7221750251008046e-16` and `1.3746648594070555e-06`; verifier and focused regression pass.
CONTROLLING_BLOCKER: `full_finite_temperature_1pi_all_channels_and_unique_physical_renormalization_missing`; `alpha_Phi_K` remains an independent open calibration gate.
NEXT_ACTION: Derive the remaining finite-temperature cuts and complete retarded/advanced/Keldysh matching with a physical subtraction scheme.
CLAIM_BOUNDARY: Lane-level finite-temperature `1 <-> 3` SK/KMS/FDT interface only; not full physical self-energy, unique renormalization, transport, entropy-current closure, SI, `alpha_Phi_K`, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module `f005ee16fcd063753f03668bd3abf248320ab9b5ba509f2d0faa8251f99297e7`; verifier `fa92115f76a6e1a74b65105bc4c51bae629584fa538f453bbac05c3f4a36a180`; artifact `c55c0592a3e0d614f09bd622fc94a8285a37101e1898a259f86bc5ff4933035f`; full gate `6dd02ba9014a117b6b9e1af62d0e4d59b349a7d2328e0fe16e819e88823fa701`; register `eef8b5eea6c4fb463efd6befd793309421323df1a37c3e2802805cc418bc668a`; dependency `19c43b725b4cac4ebcc536a1240580519b074506bd1a28564b677833180c1774`.

## T13-083 - Finite-Temperature Sunset Channel Pole-Subtracted Real Part
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_THREE_BODY_SUNSET_SK_KMS_LANE`; no Full Topic 13 promotion.
WHAT_IS_ACTUALLY_CLOSED: The declared natural-unit `1 <-> 3` thermal spectral channel has a pole-subtracted principal-value retarded real-part interface in addition to the previously checked KMS/FDT and retarded-sign relations.
WHAT_REMAINS_OPEN: All other thermal cuts, full finite-temperature 1PI, all-channel real-part subtraction, unique physical renormalization, Kubo/transport, entropy-current balance, SI mapping, independent `alpha_Phi_K`, numeric source provenance, and external validation.
DEPENDENCY_UNLOCKED: Thermal channel-level SK/KMS/FDT/PV interface only; no Core, Gravity, constitutive transport, Galaxy, SI, alpha, source, or external-validation unlock.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_THREE_BODY_SUNSET_SK_KMS_LANE`; full gate `BLOCKED_OPEN_T13_FULL_BRIDGE/PARTIAL`.
WHAT_CHANGED: Formula-audit entry `T13-083` records the thermal subtraction kernel, analytic pole term, unit lane, derivation class, observable, and machine-checked convergence fields.
EQUATION_OR_MAPPING: `K_sub(S)=1/(S-s)-1/(S-r)-(s-r)/(S-r)^2`, `r=-s_E`; `Re Sigma_R,T^sub(s)=PV integral_[s_th,infty] [rho_T(S)-rho_T(s)]K_sub(S)dS + rho_T(s)A(s)`; `A(s)=ln((s_th-r)/abs(s_th-s))-(s-r)/(s_th-r)`. `rho_T` is the action-derived thermal spectral difference; no `Phi` to SI or temperature calibration is inferred.
VERIFICATION: PV real part `0.000313708112388661`; inner residual `4.272571791753135e-07`; outer residual `1.841949608971285e-05`; KMS `1.7763568394002505e-15`; FDT `1.8151885566908842e-16`; verifier zero failed checks; focused regression `3 passed`.
CONTROLLING_BLOCKER: `full_finite_temperature_1pi_all_channels_and_unique_physical_renormalization_missing`; independent `alpha_Phi_K` and source gates remain separate.
NEXT_ACTION: Extend the same unit/derivation audit to remaining thermal cuts and match the complete retarded/advanced/Keldysh object to one declared physical subtraction scheme.
CLAIM_BOUNDARY: Lane-level action-derived thermal PV interface only; not full retarded 1PI, unique renormalization, transport, entropy, SI mapping, `alpha_Phi_K`, TTG prediction, external validation, or Full Topic 13.
EVIDENCE_HASHES: module `e9e2f057cbd16f37b8cc68013f7805ee3c9dba7f31ae4fecaa4741554e053aa2`; verifier `b86e20cc746426380ea3481db32c35828816bb2b31af67e905d25ef224810a99`; artifact `6d70f32ff2fb465e6932a5327be2e428d303b23f2a85f9ac68bd5fd1803936fc`; full gate `d71843ab712a8deba645056ef2cd851cebd53f5514a568911a6ca38e34228135`; register `3200812ba435008d6e9dcac793d4b1de6f20d2c3626ee475203a6de6305058e6`; dependency `f2a1ae5f3a16654fe0e261acbaa2779a2cf3f807d7f63c0fc2ba644bbc26f39a`.

## T13-084 - Finite-Temperature Labeled 2<->2 Sunset Scattering Cut
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`; full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE/PARTIAL`.
WHAT_IS_ACTUALLY_CLOSED: Action-derived labeled `2 <-> 2` sunset phase space, explicit `S_22=1/2`, greater/lesser Bose weights, channel KMS/FDT, retarded `i0` sign, and pole-subtracted channel PV real part.
WHAT_REMAINS_OPEN: Other thermal cuts, full finite-temperature 1PI, all-channel subtraction, unique physical renormalization, physical Kubo, entropy/heat-flux balance, dimensional map, `alpha_Phi_K`, source provenance, uncertainty, and external validation.
DEPENDENCY_UNLOCKED: Channel interface only; no Core or downstream dependency promotion.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_SCATTERING_SUNSET_SK_KMS_LANE`.
WHAT_CHANGED: Added the scattering module, verifier/artifact, test, full-gate mapping, registry/dependency sync, and machine-readable closure fields. It remains separate from the exact elastic transition-kernel lane.
EQUATION_OR_MAPPING: `P+k3=k1+k2`; `Q^2=s+m^2+2*sqrt(s)*E3`; `rho_>/rho_<=exp(beta_th*sqrt(s))`; `N=rho_T*coth(beta_th*sqrt(s)/2)`; `Im Sigma_R=-pi*rho_T`; twice-subtracted `K_sub` controls the channel PV real part. Natural units; `Phi` remains an effective response variable.
VERIFICATION: KMS/FDT residuals `0`; scattering inner/outer residuals `2.068736947527328e-16` and `1.141494787607428e-11`; PV inner/outer residuals `0.0015630214156617276` and `0.0009742158373661669`; verifier zero failed checks; focused regression `3 passed`.
CONTROLLING_BLOCKER: `full_finite_temperature_1pi_all_channels_and_unique_physical_renormalization_missing`; `alpha_Phi_K` and source gates remain independent and open.
NEXT_ACTION: Derive the remaining thermal cuts and complete the full retarded/advanced/Keldysh 1PI and physical subtraction match.
CLAIM_BOUNDARY: Lane-level action-derived scattering result only; no full bridge, transport, entropy, SI, alpha, TTG, or external-validation promotion.
EVIDENCE_HASHES: module `dbcd9212bf6738a71d6e1b550531adc98cdeaa966cc9875f9045709733dcea3a`; artifact `e4807a12749e6deaddfee7903d66f3b4c2f8cb4acbc1d127cb2ec0578d2554ec`; full gate `7b9d5510818281a9eb0fd41ce0a7427e337e5249dcb45092a128d40164789670`.

## T13-085 - Declared Full Finite-Temperature Sunset Cut Composition
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_DECLARED_FULL_SUNSET_SK_KMS_LANE`; Full Topic 13 remains `PARTIAL`.
WHAT_IS_ACTUALLY_CLOSED: Matched composition of the declared timelike equal-mass order-lambda^2 `1 <-> 3` and labeled `2 <-> 2` action-derived sunset cuts.
WHAT_REMAINS_OPEN: Complete off-shell 1PI, unique physical renormalization, transport/Kubo, entropy-current balance, dimensional map, independent `alpha_Phi_K`, source uncertainty, TTG, and external validation.
DEPENDENCY_UNLOCKED: Lane-level summed thermal-cut SK/KMS/FDT/PV interface only.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_DECLARED_FULL_SUNSET_SK_KMS_LANE`; zero failed checks; no Core unlock.
WHAT_CHANGED: Added a composition state that calls both audited channels with identical `T`, `m^2`, `lambda`, species count, invariant `s`, action prefactor, and subtraction reference. The maximum component PV residual is used as a conservative aggregate witness.
EQUATION_OR_MAPPING: `Sigma_R,T^declared=Sigma_R,T^13+Sigma_R,T^22`; `rho_>^declared=rho_>^13+rho_>^22`; `rho_<^declared=rho_<^13+rho_<^22`; `rho_T^declared=rho_>^declared-rho_<^declared`; `log(rho_>^declared/rho_<^declared)=beta_th*sqrt(s)`; `N_T^declared=rho_T^declared*coth(beta_th*sqrt(s)/2)`; `Im Sigma_R,T^declared=-pi*rho_T^declared`; `Re Sigma_R,T^declared,sub=Re Sigma_R,T,13^sub+Re Sigma_R,T,22^sub`.
VERIFICATION: Combined KMS/FDT residuals `0.0`/`0.0`; retarded imaginary `-5.64672936156317e-05`; PV `0.00022637188369854333`; component/aggregate PV residuals below `2e-2`; focused regression `30 passed`.
CONTROLLING_BLOCKER: Complete off-shell finite-temperature 1PI and unique physical renormalization are not yet derived; SI thermal mapping and independent calibration/source gates remain open.
NEXT_ACTION: Construct the full retarded/advanced/Keldysh 1PI continuation and select a physical subtraction scheme before transport or entropy promotion.
CLAIM_BOUNDARY: Composition closure is not complete 1PI, unique renormalization, physical transport, entropy balance, SI `Phi` map, `alpha_Phi_K`, TTG prediction, or Full Topic 13.
EVIDENCE_HASHES: aggregate module `01caf81cb0a29ed5d01d291b91accf600cbf75e1cbeaaaa1e7ef5d6c50702e43`; verifier `872261e6d4aeb18dd83f945c84a41c67dc8ad492ede24ebebf33a0f348196475`; artifact `276410bcadbb2db67038c136425dab6ba9451017c87e3a5ef673c83133d0f7ec`; full gate `65aff596de275f57cd02f16d63bf9742a386b5e960c6821f55a1c768fca73fff`.

## T13-086 - Finite-Temperature Sunset Vacuum-Limit Matching
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_SUNSET_VACUUM_MATCH_LANE`; Full Topic 13 remains `PARTIAL`.
WHAT_IS_ACTUALLY_CLOSED: Low-temperature finite-T spectral, retarded-sign, imaginary-part, and PV matching to the existing action-derived vacuum sunset.
WHAT_REMAINS_OPEN: Physical renormalization selection, complete finite-T 1PI, transport/Kubo, entropy, dimensional map, independent `alpha_Phi_K`, source uncertainty, TTG, and external validation.
DEPENDENCY_UNLOCKED: Consistency bridge only; no physical scheme or Core unlock.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_SUNSET_VACUUM_MATCH_LANE`; zero failed checks.
WHAT_CHANGED: Added an independent comparison state using the canonical vacuum retarded module and its Euclidean reference response, with matched invariant and action normalization.
EQUATION_OR_MAPPING: `lim_(T->0+) rho_T^declared=rho_vacuum`; `lim_(T->0+) Im Sigma_R,T^declared=Im Sigma_R,vacuum`; `lim_(T->0+) Re Sigma_R,T^declared,sub=Re Sigma_R,vacuum,sub`; `rho_T^(2<->2)->0`.
VERIFICATION: `T_low=0.05`; spectral residual `3.023525152150896e-06`; imaginary residual `3.0235251521003147e-06`; PV residual `2.3360451630664565e-05`; `2<->2` fraction `9.915909732624986e-07`; all checks passed.
CONTROLLING_BLOCKER: `physical_renormalization_scheme_match_missing`; the match does not choose a physical counterterm prescription.
NEXT_ACTION: Derive physical renormalization conditions and connect them to the complete finite-temperature SK/KMS 1PI object.
CLAIM_BOUNDARY: Low-T consistency only; not a physical renormalization proof, complete 1PI, transport, entropy, SI `Phi` map, `alpha_Phi_K`, TTG prediction, or Full Topic 13.
EVIDENCE_HASHES: module `5a428e64c5f50075d2cf2ae733366b99a1ffecae1ec83014eb82c9e0edb83ee5`; verifier `5d43586b1ab10d597c9d90a5af24c70b439b13cca4cd60f4a386703e4bd9b46d`; artifact `74f665736d6bbf49b248c7df0ffb4f9cb44bbaf59db00617747f57892260a7e9`; vacuum artifact hash is included in the machine-readable evidence list.

## T13-087 - Finite-Temperature Sunset Renormalization Identifiability No-Go
MAJOR_RESULT_CLOSURE: `CLOSED_AS_NO_GO` for `T13_UET_O2_FINITE_T_SUNSET_RENORMALIZATION_IDENTIFIABILITY_NO_GO`; physical renormalization remains open.
WHAT_IS_ACTUALLY_CLOSED: A scoped reference-dependence witness for the PV real part under fixed spectral/KMS/FDT cuts.
WHAT_REMAINS_OPEN: Independent physical conditions, complete finite-T 1PI, transport/Kubo, entropy, dimensional map, independent `alpha_Phi_K`, source uncertainty, TTG, and external validation.
DEPENDENCY_UNLOCKED: No-go statement only; no physical scheme or Core unlock.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_SUNSET_RENORMALIZATION_IDENTIFIABILITY_NO_GO`; zero failed checks.
WHAT_CHANGED: Swept declared subtraction references `0.25`, `0.5`, and `0.8` while preserving the same action-derived thermal cut calculations and convergence controls.
EQUATION_OR_MAPPING: `Re Sigma^sub(s;r1)-Re Sigma^sub(s;r2) != 0` while `rho_T(s;r1)=rho_T(s;r2)`, KMS, and FDT remain invariant.
VERIFICATION: PV relative span `0.36357759907026227`; spectral invariance `0.0`; KMS invariance `0.0`; FDT invariance `1.8151642882300236e-16`; all no-go checks passed.
CONTROLLING_BLOCKER: `physical_renormalization_scheme_selection_missing`.
NEXT_ACTION: Obtain or derive an independent physical renormalization condition set before promoting any PV real part.
CLAIM_BOUNDARY: No-go for current scheme identifiability only; not a physical renormalization proof or Full Topic 13 closure.
EVIDENCE_HASHES: module `dc43fe6e2ebd1fc3bde7bb180f885cd30029ca587b496d4851a63c50c04974f3`; verifier `55147b3266779b0bcc56fa2389f71f10627a44cc329f8b17130cccce908a80a7`; artifact `eedf7dbc290e944cbbe5b5e2b2a23a688b3f7b25e30eb57446b9673ac89b576e`; full gate `dd543a33ee3016ba19fc55c54df5e56ac1064d89933376bb8f9c8c453028c183`.


## T13-088 - Physical renormalization-condition contract

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-088` | `Gamma_R^(2)(s)=s-s_*-Sigma_R,sub(s;s_*)`; `Sigma_R,sub=Sigma_R(s)-Sigma_R(s_*)-(s-s_*)Sigma_R'(s_*)`; `Gamma_R^(2)(s_*)=0`; `Gamma_R^(2)'(s_*)=1`; `delta_m^2=Re Sigma_R(s_*)`; `delta_Z=-Re Sigma_R'(s_*)` | `docs/core/uet_o2_physical_renormalization_condition_contract.py`; `docs/scripts/audit/audit_topic13_uet_o2_physical_renormalization_condition_contract.py`; `docs/core/artifacts/t13_uet_o2_physical_renormalization_condition_contract.json` | `s`, `s_*`, and self-energy have natural energy-squared units; self-energy derivative, residue, and `delta_Z` are dimensionless; `Phi` remains an effective response variable | on-shell Taylor-condition contract; formal witness only until an external physical anchor is source-locked | `CLOSED_FOR_LANE`; below-threshold pole/residue algebra and external-anchor acceptance fields pass | formal contract can be mistaken for a physical mass/residue measurement or unique finite-temperature scheme | source-lock an independent pole/residue or microscopic renormalization record, then evaluate the complete finite-temperature 1PI object |

The witness uses `m_internal^2=0.5`, `s_*=0.75`, `s_th=9m_internal^2=4.5`, with zero pole and residue residuals. `physical_anchor_supplied=false`; no external scheme, numeric `alpha_Phi_K`, target curve, fit, or Xie 2026 holdout is used. Artifact SHA-256 is recorded in the machine-readable registry.

## T13-089 - Covariant Entropy and Heat-Flux Balance

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-089` | `h=(epsilon+p)/n`; `b_i=(E-h*q)(p_i/E)sqrt(w)`; `b_i^perp=P*b_i`; `K_ab=(b_a^perp)^T L_cont^+ b_b^perp`; `X_T^mu=-Delta^(mu nu)(nabla_nu T+T*a_nu)/T`; `q^mu=kappa_natural*X_T^mu`; `J_S^mu=s*u^mu+q^mu/T`; `sigma=X_T_mu*q^mu>=0`; `I_A^T L_cont delta_f=0` | `docs/core/uet_o2_covariant_entropy_heat_flux_balance.py`; `docs/scripts/audit/audit_topic13_uet_o2_covariant_entropy_heat_flux_balance.py`; `docs/core/test/test_topic13_uet_o2_covariant_entropy_heat_flux_balance.py`; `docs/core/artifacts/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json` | declared natural units; `T`, `mu`, `E`, and `h` are natural energies; `kappa_natural`, formal heat flux, and entropy current remain finite-cutoff natural moment quantities; no `W m^-1 K^-1`, SI heat flux, or `Phi` scale is emitted; `C`, `Phi`, `R_gen`, and `R_obs` retain their locked meanings | action-derived finite-temperature quasiparticle EOS plus finite-cutoff conservative collision operator, Landau moment subtraction, pseudoinverse response, and covariant projector lift; no source rows, fit, SI calibration, or holdout | `CLOSED_FOR_LANE`; positive response matrix, entropy identity, conserved charge/energy/momentum balance, local Lorentz lift, and equilibrium zero-flux controls pass | a formal natural-unit moment response can be mistaken for a physical Kubo coefficient, SI conductivity/heat flux, complete two-fluid transport, or `alpha_Phi_K` calibration | source-lock a state-matched microscopic retarded correlator or physical transport record with units/uncertainty; keep dimensional `Phi`, alpha, Ding source, and holdout gates independent |

At the reference state `(T,mu,Phi)=(0.22,0.35,0.15)`, the declared normal branch gives `kappa_natural=257.37286696883626`, response isotropy residual `4.433922804155191e-11`, entropy-balance residual `1.1411259492888348e-08`, kinetic equation residual `5.1199485579650025e-17`, charge/energy/momentum balance residuals below `2e-19`, and Lorentz-lift residual `1.4210854715202004e-14`. The lane emits no physical Kubo coefficient, numeric `alpha_Phi_K`, SI map, fit, target-data result, or Xie 2026 holdout result.

## T13-090 - Action-Derived Thermal Stiffness Beta

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-090` | `f_qp(T,mu,Phi)=-p_qp(T,mu,Phi)`; `a_Phi^nat(T)=partial_Phi^2 f_qp|_(T,mu,Phi_ref)`; `beta_Phi^nat=T*partial_T a_Phi^nat`; symmetric Phi/temperature differences provide the numerical derivative | `docs/core/uet_o2_action_thermal_stiffness_beta.py`; `docs/scripts/audit/audit_topic13_uet_o2_action_thermal_stiffness_beta.py`; `docs/core/test/test_topic13_uet_o2_action_thermal_stiffness_beta.py`; `docs/core/artifacts/t13_uet_o2_action_thermal_stiffness_beta_audit.json` | natural units; `T`, `mu`, and effective mass are natural energies; `a_Phi^nat` is a normalization-dependent natural response free-energy curvature; `beta_Phi^nat` is `T*partial_T a_Phi^nat`; normalized `beta_T13`, `e0`, SI Phi scale, and `alpha_Phi_K` are not emitted | action-derived finite-temperature quasiparticle pressure with explicit nonzero response coupling; fixed-state response curvature and refined symmetric temperature stencil; no Landauer identity, source rows, fit, or holdout | `CLOSED_FOR_LANE`; normal branch remains fixed over the stencil, action beta is finite/nonzero, and curvature/beta refinement checks pass | natural action beta can be mistaken for the normalized beta contract, legacy core beta, a physical Kelvin coefficient, or an alpha calibration | source-lock an independent Phi normalization and physical temperature coefficient, then match this action lane to the dimensional/alpha bridge |

At `(T,mu,Phi)=(0.22,0.35,0.15)` with `epsilon_nc=0.05` and response coupling `0.8`, the reference natural curvature is `-6.643796596856807e-07` and `beta_Phi^nat=-2.4271981641363002e-06`; the refined values are `-6.643888625292461e-07` and `-2.427707354265597e-06`. Relative refinement changes are `1.385159216892113e-05` and `2.0974174874360104e-04`. This is an action-origin lane only; it emits no normalized beta, `e0`, SI map, `alpha_Phi_K`, transport coefficient, TTG prediction, or holdout result.

## Berut Figure 3c Figure-Derived Digitization

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE

WHAT_IS_ACTUALLY_CLOSED: Panel 3c, visible axes and units, three marker-series
identities, ten marker centers, pixel-to-axis transforms, and a digitization-only
uncertainty envelope are recorded. The continuous fit curve and Landauer line are
excluded from the rows.

WHAT_REMAINS_OPEN: This is figure-derived rather than raw numeric data. The
publisher-reported 1 s.d. measurement intervals were not numerically transcribed,
and no permissioned raw table is archived.

DEPENDENCY_UNLOCKED: Berut figure-derived comparison lane only. No Full Topic 13,
Core, Gravity, constitutive transport, calibration, or external-validation
dependency is unlocked.

STATUS: `PASS_SCOPED_BERUT_FIGURE3_DIGITIZATION`

WHAT_CHANGED: `docs/core/artifacts/t13_berut_figure3_digitization.json` and its source package record the official Figure 3c
locator, embedded-raster hash, axis mapping, marker rows, preprocessing, and
non-calibration boundary.

EQUATION_OR_MAPPING: `<Q>_panel_c(tau)` is retained in source units `kT` versus
`tau` in seconds. No SI heat or Phi mapping is emitted.

VERIFICATION: `10` rows; three series; no curve digitization;
no fit; no target or holdout access; no alpha calibration.

CONTROLLING_BLOCKER: `berut_figure3_digitization_is_figure_derived_not_raw_numeric_source`

NEXT_ACTION: Obtain a permitted raw or numeric source package, or obtain explicit
permission to archive the binary and its numeric extraction, then transcribe the
source-reported measurement uncertainty separately.

CLAIM_BOUNDARY: Scoped figure-derived comparison only; not a raw source,
calibration, prediction, UET proof, or external validation.

## T13-111 - Thermodynamic Normal Component

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-111` | `p_n=p_qp`; `n_n=partial_mu p_n`; `s_n=partial_T p_n`; `epsilon_n=-p_n+T*s_n+mu*n_n`; `chi_n=partial_mu n_n`; `Pi_n=(1/3) sum_a integral[d^3k/(2*pi)^3] k^2[-partial_E n_B(E_a)]` | `docs/core/uet_o2_finite_temperature_normal_component.py`; `docs/core/uet_o2_finite_temperature_two_fluid_response.py`; `docs/scripts/audit/audit_topic13_uet_o2_thermodynamic_normal_component.py`; `docs/core/artifacts/t13_uet_o2_thermodynamic_normal_component_audit.json` | natural-unit thermal pressure/charge/entropy/energy densities and static responses; `Phi` remains an effective response variable; no SI `Phi` scale or physical Kubo units are emitted | action-derived tree-condensate plus thermal-quasiparticle EOS and static Doppler response | `CLOSED_FOR_LANE`; branch, finite-value, stability, low-temperature, ontology, and no-fit checks pass | names the finite-temperature thermodynamic normal component without promoting static response to physical flow or retarded Kubo transport | a thermal pressure sector or static susceptibility can be mislabeled as a complete physical two-fluid transport theory | source-lock a state-matched physical normal-flow/retarded Kubo record with units and uncertainty; keep independent SI and `alpha_Phi_K` gates open |

The lane is internal and natural-unit only. It does not derive a dimensional `Phi -> Delta_Tq` map, a physical normal-fluid coefficient, `alpha_Phi_K`, Ding `C_src`, a TTG prediction, or Full Topic 13 closure. Artifact status is `PASS_ACTION_DERIVED_THERMODYNAMIC_NORMAL_COMPONENT_LANE` with zero failed checks; no fit, target data, threshold adjustment, or Xie 2026 holdout access occurred.

## T13-112 - Condensed Relative-Flow Collision Kernel

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-112` | `A_*^2=(Z*mu^2-m_eff^2)/lambda`; `sigma_ab(s_med)=lambda^2/[16*pi*(s_med+m_H^2)]`; `L_rel=Gamma_rel*((1,-1),(-1,1))`; `G_R^rel(omega)=2*D_rel/(2*Gamma_rel-i*omega)` | `docs/core/uet_o2_condensed_relative_flow_collision.py`; `docs/scripts/audit/audit_topic13_uet_o2_condensed_relative_flow_collision.py`; `docs/core/artifacts/t13_uet_o2_condensed_relative_flow_collision_audit.json` | natural units; `s_med,m_H^2` are energy squared, `Gamma_rel` is energy, and the relative response is a natural-unit coefficient; no SI Phi scale is emitted | existing O(2) tree condensate scales plus a declared screened contact-channel and symmetric mode-space relaxation | `CLOSED_FOR_LANE`; positivity, common-flow conservation, retarded interface, KMS/FDT, entropy, and refinement checks pass | a finite natural-unit contact response can be mislabeled as a complete microscopic or physical Kubo transport coefficient | complete condensed microscopic vertices and continuum/renormalization matching, or source-lock a state-matched retarded correlator with units and uncertainty |

The medium-frame invariant is explicit because the finite-density quasiparticle dispersions are not silently treated as vacuum Lorentz-invariant four-momenta. The lane emits no physical Kubo coefficient, SI map, alpha_Phi_K, TTG prediction, or holdout result.

## T13-113 - Continuum Relative-Flow Kubo Lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`
WHAT_IS_ACTUALLY_CLOSED: The screened contact-channel response is evaluated with a compactified radial map over `k in [0,infinity)`. Radial-order, angular-order, and compactification-scale refinements pass the unchanged `1e-2` convergence controller.
WHAT_REMAINS_OPEN: Loop-renormalized condensed vertex, complete scattering channels, physical Kubo units/uncertainty, complete two-fluid tensor, dimensional `Phi` map, independent calibration, Ding-compatible `C_src`, and Full Topic 13.
DEPENDENCY_UNLOCKED: Continuum natural-unit thermal contact-response lane only.
STATUS: `PASS_ACTION_DERIVED_CONTINUUM_RELATIVE_FLOW_KUBO_LANE`
WHAT_CHANGED: Added the continuum integral module, audit, test, equation entry, and gate projection. The integration scale `Lambda` is a quadrature map scale, not a physical cutoff.
EQUATION_OR_MAPPING: `k=Lambda*u/(1-u)` and `dk=Lambda/(1-u)^2 du`; `D_a=(1/3) integral[d^3k/(2*pi)^3] k^2 v_a^2[-partial_E n_a]`; `sigma_ab=lambda^2/[16*pi*(s_med+m_H^2)]`; `L_rel=Gamma_rel*((1,-1),(-1,1))`; `G_R^rel(omega)=2*D_rel/(2*Gamma_rel-i*omega)`.
VERIFICATION: Radial maximum relative change `4.5662793172363093e-07`; angular refinement `2.06194987822215e-06`; scale refinement `1.6133063996982916e-09`; positivity, common-flow conservation, KMS/FDT, entropy, finite-value, no-fit, and holdout checks pass. Focused regression `2 passed`.
CONTROLLING_BLOCKER: `loop_renormalized_condensed_vertex_and_physical_kubo_match_missing`.
NEXT_ACTION: Derive/source-lock the loop-renormalized condensed vertex or a state-matched retarded correlator with units and uncertainty, then rerun physical Kubo admission.
CLAIM_BOUNDARY: Natural-unit action-derived continuum thermal contact-response lane only; not a loop-renormalized physical Kubo coefficient, SI observable, alpha calibration, TTG prediction, external validation, or Full Topic 13 closure.

## T13-114 - Condensed Loop-Renormalized Contact Vertex

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-114` | `B_ab^th=(integral d^3k/(2*pi)^3)*(k/L)^2*(n_a+n_b)/(2 E_a E_b (E_a+E_b))`; `B_ab^R=B_ab^th(Phi)-B_ab^th(Phi_ref)`; `lambda_ab^R=lambda/(1+lambda B_ab^R)`; `G_R^rel(omega)=2*D_rel/(2*Gamma_rel-i*omega)` | `docs/core/uet_o2_condensed_loop_renormalized_vertex.py`; `docs/scripts/audit/audit_topic13_uet_o2_condensed_loop_renormalized_vertex.py`; `docs/core/test/test_topic13_uet_o2_condensed_loop_renormalized_vertex.py`; `docs/core/artifacts/t13_uet_o2_condensed_loop_renormalized_vertex_audit.json` | natural continuum 3+1; bubble and couplings dimensionless after declared `(k/L)^2` normalization; `Gamma_rel` is energy; response is natural-unit only; `Phi` is not temperature; `C` is not mass or charge | existing O(2) condensed quasiparticle dispersion and screened contact channel; internal reference subtraction; no external data, fit, or holdout | `CLOSED_FOR_LANE`; finite bubble, reference condition, positive coupling, order/scale refinement, PSD/conservation, KMS/FDT, and entropy checks pass | closes a loop-renormalized condensed contact-channel and state-matched retarded natural-unit interface without physical Kubo promotion | a channel-specific natural-unit loop can be mislabeled a full condensed 1PI vertex, physical Kubo coefficient, SI conductivity, or `alpha_Phi_K` | source-lock or microscopically match an independent state-matched physical vertex/Kubo record, then complete SK/KMS and all condensed scattering channels |

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`.
WHAT_IS_ACTUALLY_CLOSED: The declared finite thermal loop/contact channel and its state-matched natural retarded response.
WHAT_REMAINS_OPEN: Physical Kubo admission, independent anchor/provenance, complete 1PI/scattering, SI, alpha, Ding `C_src`, and Full Topic 13.
DEPENDENCY_UNLOCKED: Lane only; no downstream dependency unlock.
STATUS: `PASS_ACTION_DERIVED_CONDENSED_LOOP_RENORMALIZED_CONTACT_VERTEX_LANE`.
VERIFICATION: Numerical uncertainty bound `3.500054507989025e-06`; loop-bubble change `9.321205929180344e-13`; loop-coupling change `3.261235996489399e-14`; focused regression `2 passed`.
CONTROLLING_BLOCKER: `physical_Kubo_coefficient_record_missing`.
NEXT_ACTION: Obtain accepted state-matched physical Kubo/vertex provenance and uncertainty.
CLAIM_BOUNDARY: This is not full 1PI, physical Kubo, SI, alpha, TTG, or Full Topic 13 closure.
## 2026-08-20 - State-matched Kubo admission and condensed SK/KMS match (T13-115/T13-116)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_CONDENSED_RELATIVE_FLOW_KUBO_ADMISSION_LANE` and `T13_UET_O2_CONDENSED_SK_KMS_KUBO_MATCH_LANE`.
WHAT_IS_ACTUALLY_CLOSED: One declared condensed relative-flow contact channel now has a machine-readable state-matched natural-unit Kubo record, plus a matched retarded lower-half-plane pole, positive spectral matrix, KMS ratio, FDT identity, zero-frequency Kubo match, and nonnegative entropy witness.
WHAT_REMAINS_OPEN: Full finite-temperature retarded 1PI self-energy, all-channel renormalization, complete two-fluid transport, SI conversion, independent physical vertex anchor, dimensional Phi map, independent alpha_Phi_K, Ding-compatible C_src, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Declared-channel Kubo and SK/KMS/FDT lanes only; `full_core_unlock=false`; no physical global coefficient, Core, Gravity, Galaxy, SI, or external-validation dependency is unlocked.
STATUS: `PASS_KUBO_MATCHED_DECLARED_CONDENSED_RELATIVE_FLOW_CHANNEL` and `PASS_ACTION_DERIVED_CONDENSED_SK_KMS_KUBO_MATCH_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`.
WHAT_CHANGED: Added the state-matched Kubo admission builder/audit and the condensed SK/KMS/Kubo response audit, then synchronized full-gate mappings, closure register, dependency projection, and update records. No fit, synthetic replacement, target residual, or Xie 2026 holdout was used.
EQUATION_OR_MAPPING: `K_rel^natural=lim_(omega->0) Re G_R^rel(omega)=D_rel/Gamma_rel`; `G_R^rel(omega)=2*D_rel/(2*Gamma_rel-i*omega)*P_rel`; `G^K=rho*coth(omega/(2*T))`.
VERIFICATION: Both audits have zero failed checks. Kubo coefficient `2.713283847206443e-05` with quadrature uncertainty `3.500054507989025e-06` is `KUBO_MATCHED` in natural units only. SK/KMS residuals are KMS `0`, FDT `2.1815250606323664e-16`, retarded reality `0`, spectral PSD minimum `0`, and zero-frequency match `0`; focused tests `4 passed`. Wave 1 integrity is `PASS_WITH_BLOCKED_LANES` with no hash errors and holdout access clean.
CONTROLLING_BLOCKER: `full_finite_temperature_retarded_1PI_self_energy_missing`, `independent_physical_condensed_vertex_anchor_missing`, and the full-bridge dimensional/alpha, Ding C_src, EOS/transport/KMS/entropy closure groups.
NEXT_ACTION: Derive the full finite-temperature condensed retarded self-energy and all-channel SK/KMS kernel, or source-lock an independent physical condensed vertex anchor. Keep this coefficient scoped to the declared natural-unit lane and do not promote it to SI or Full Topic 13.
CLAIM_BOUNDARY: Action-derived declared-channel result only; not an external measurement, complete interacting 1PI theory, SI thermal transport, alpha_Phi_K calibration, TTG prediction, external validation, or global UET closure.
DATA_ROLE: `DERIVED_INTERNAL_NATURAL_UNIT`; the admitted coefficient is not a calibration, training, comparison, or holdout record. No external numeric source was consumed by these two lanes.
EVIDENCE_PATHS: `docs/core/uet_o2_condensed_relative_flow_kubo_admission.py`; `docs/core/artifacts/t13_uet_o2_condensed_relative_flow_kubo_admission_audit.json`; `docs/core/uet_o2_condensed_sk_kms_kubo_match.py`; `docs/core/artifacts/t13_uet_o2_condensed_sk_kms_kubo_match_audit.json`.
EVIDENCE_HASHES: Kubo module `92dea65cf85d2fc2054e4f5c0b293712d2ea0b8b0df65ffa5e4b95de9dd2df67`; Kubo audit `5e909ff97aa0476619235460c012313f36b6065e642bbe4f7fba63f36bd8c7f6`; SK/KMS module `ab6fabaca6d2a19f8185535928638ecf4f1581cd2ad89ada78ed89e5341aff72`; SK/KMS audit `d13d59760f9ebe0a3d2471ad984ec95c6729846d08b2b9ce011e2e8eb2fcaf1c`; registry `ae143f9bd06738ae777415b46d39752c8fbb4a96b17f31de94eac3e563a7be44`; full gate `4b69d2f13ef9827f11898edc63b254dd837943b3ccdf4b88f7fe52b2ea0d2415`; register `6d41189d970ba4b17bb889176412fc66ed4b9cbcd02a8520d014ddc61800ddb0`; dependency `83f6351dc2ccee0f3ba80a593c2081ca82e04d0b0b9d5b69ec9ad91754bfff1d`.
## 2026-08-20 - Declared finite-temperature retarded 1PI response grid (T13-117)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_LANE`.
WHAT_IS_ACTUALLY_CLOSED: The audited action-derived 1<->3 and labeled 2<->2 finite-temperature sunset channels are evaluated on one matched timelike invariant grid. The assembled pole-subtracted retarded response has a positive spectral grid, lower-half-plane imaginary part, grid-level KMS/FDT checks, retarded i0 consistency, and PV convergence.
WHAT_REMAINS_OPEN: Complete finite-temperature retarded 1PI self-energy, all sunset cuts, unique physical renormalization, physical Kubo transport, covariant entropy/heat-flux closure, dimensional Phi mapping, independent alpha_Phi_K, Ding C_src, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Declared retarded response-grid lane only; `full_core_unlock=false`; no physical Kubo, SI, alpha, Core, Gravity, Galaxy, or external-validation dependency is unlocked.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.
WHAT_CHANGED: Added the multi-invariant state-matched retarded response builder, focused regression, audit artifact, full-gate mapping, closure-register entry, dependency projection, and wave record. No target data, fit, synthetic replacement data, Landauer shortcut, or Xie 2026 holdout was used.
EQUATION_OR_MAPPING: `Sigma_R,T^declared(s+i0)=Re Sigma_R,T^declared,sub(s)-i*pi*rho_T^declared(s)`; `rho_T^declared=rho_>,13+rho_>,22-rho_<,13-rho_<,22`; `log(rho_>/rho_<)=sqrt(s)/T`; `N_T=rho_T*coth(sqrt(s)/(2*T))`.
VERIFICATION: Audit has zero failed checks on `s={4.75,5.0,5.5}` with threshold `4.5`. Maximum KMS residual `8.881784197001252e-16`; maximum FDT residual `0.003942955405912313`; maximum PV inner/outer residuals `0.0004183177470783957` / `0.00028892386785935357`; retarded i0 residual `6.776263578034403e-21`; focused regression `3 passed`. Wave 1 integrity remains `PASS_WITH_BLOCKED_LANES`, with no hash errors and no holdout consumption.
CONTROLLING_BLOCKER: `complete_finite_temperature_1pi_self_energy_and_all_channel_physical_renormalization_missing`; independent physical vertex/Kubo provenance, dimensional Phi anchor, alpha_Phi_K, Ding C_src, and EOS/transport/KMS/entropy completion remain full-bridge blockers.
NEXT_ACTION: Derive the remaining finite-temperature interacting 1PI channels and an independent physical renormalization/vertex anchor. Keep this grid as a declared natural-unit lane and do not promote it to physical SI transport.
CLAIM_BOUNDARY: Action-derived internal evidence for the declared two-channel response grid only; not a complete interacting 1PI theory, physical Kubo coefficient, SI thermal transport, alpha_Phi_K calibration, TTG prediction, external validation, or global UET closure.
DATA_ROLE: `ACTION_DERIVED_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_NO_HOLDOUT`.
EVIDENCE_HASHES: module `f635e131e00c295cb90bf51607a8c41b392fef4af610682d9c4d3bc99e504885`; audit script `c2c379f776a48d0c4daad099696042e3c205ded0f51dcc7893a959ebe9d2c281`; audit artifact `f22d74b88c82e62bb0dc984bc96b1171bc2b7579d563d693fa3559ac199e3861`; full gate `53f40cd31b9cba7d608aeb5e8a3d48d3dc204302c478c16d4bb165a96f66a9ee`; register `8561401dec879ebc1b3c98f438e0ea774e8a8bacaf9cbe6cacae0ab1b25b985c`; dependency `cc3ef8f07c4e16037d9d232f40487f5de6cd841f9b12ddc8f163541bc7f820fd`.
## T13-118: Finite-Temperature Signed-Cut Kinematic Taxonomy
- `major_result_id`: `T13_UET_O2_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_LANE`
- `closure_level`: `CLOSED_FOR_LANE`
- `equation`: `P0=sigma_1 E_1+sigma_2 E_2+sigma_3 E_3`, with all eight sign assignments enumerated for positive external energy.
- `classification`: one `1<->3` assignment above `sqrt(s)>=3m`; three `2<->2` assignments `-++`, `+-+`, `++-`; one-plus/two-minus and all-negative assignments are forbidden for `P0>0`.
- `multiplicity_boundary`: current scattering implementation is labeled to `++-` only; two kinematic permutations remain outside the current action-level multiplicity contract.
- `units`: natural vacuum 3+1; external energy and mass in energy units; `mass_squared` in energy squared.
- `derivation_class`: action-compatible future-timelike kinematic classification; no fitted coefficient and no external data.
- `observable`: sign-assignment inventory, process-class counts, threshold witness, and labeled-channel gap.
- `verification`: `t13_uet_o2_finite_temperature_signed_cut_coverage_audit.json`, zero failed checks.
- `claim_boundary`: closes taxonomy only; does not close full 1PI, physical renormalization, Kubo, entropy, dimensional `Phi` mapping, independent `alpha_Phi_K`, TTG, or Full Topic 13.
## T13-119: Action-Level Sunset Cut Multiplicity
- `major_result_id`: `T13_UET_O2_FINITE_T_SUNSET_CUT_MULTIPLICITY_LANE`
- `closure_level`: `CLOSED_FOR_LANE`
- `equations`: `S_sunset=1/6`; `N_13=1`; `N_22=3`; `w_13=1/6`; `w_22=3/6=1/2`; `w_final(c,d)=1/(1+delta_cd)` in the separate physical scattering comparator.
- `mapping`: current representative scattering factor `SCATTERING_CHANNEL_SYMMETRY_FACTOR=0.5` equals the graph-summed `2<->2` weight; this is not a proof of physical Kubo normalization.
- `units`: natural vacuum 3+1; weights dimensionless; tensor prefactor has energy-squared units per loop integral.
- `derivation_class`: action-derived graph symmetry and signed-cut permutation count; species-resolved final-state convention kept separate.
- `verification`: `t13_uet_o2_finite_temperature_sunset_cut_multiplicity_audit.json`, zero failed checks.
- `claim_boundary`: closes action-level multiplicity only; full 1PI, physical renormalization, Kubo, entropy, dimensional `Phi`, independent `alpha_Phi_K`, TTG, and Full Topic 13 remain open.
## T13-120: All Positive-Energy On-Shell Cut Spectral Response
- `major_result_id`: `T13_UET_O2_FINITE_T_ALL_ONSHELL_CUT_SPECTRAL_RESPONSE_LANE`
- `closure_level`: `CLOSED_FOR_LANE`
- `equations`: `rho_all=rho_(+++)+rho_(-++)+rho_(+-+)+rho_(++-)`; `rho_(2<->2,all)=(3/6)rho_(++-)`; `Sigma_R=Re Sigma_sub-i*pi*rho_all`; `N=rho_all*coth(sqrt(s)/(2*T))`.
- `grid`: `s={4.75,5.0,5.5}` with threshold `4.5`.
- `units`: natural vacuum 3+1; spectral/self-energy lane remains energy-squared convention.
- `derivation_class`: action-derived signed-cut taxonomy plus graph multiplicity plus state-matched retarded response grid.
- `verification`: `t13_uet_o2_finite_temperature_all_onshell_cut_response_audit.json`, zero failed checks.
- `claim_boundary`: closes on-shell spectral response only; off-shell 1PI, physical renormalization, Kubo, entropy, dimensional `Phi`, independent `alpha_Phi_K`, TTG, and Full Topic 13 remain open.

## T13-121 - Declared-Channel Retarded/Advanced/Keldysh 1PI

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`.
WHAT_IS_ACTUALLY_CLOSED: Numerical real-time component construction for the declared action-derived finite-temperature 1<->3 and representative 2<->2 sunset channels.
WHAT_REMAINS_OPEN: Complete off-shell all-channel 1PI, physical renormalization, physical Kubo, entropy/heat-flux balance, dimensional `Phi`, independent `alpha_Phi_K`, Ding `C_src`, and Full Topic 13.
DEPENDENCY_UNLOCKED: Declared-channel retarded/advanced/Keldysh interface only.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_DECLARED_CHANNEL_RETARDED_ADVANCED_KELDYSH_1PI_LANE`.
WHAT_CHANGED: Added an explicit component convention and numerical residual checks over the matched invariant grid.
EQUATION_OR_MAPPING: `rho=rho_>-rho_<`; `N=rho_>+rho_<`; `Sigma_R=Re Sigma_sub-i*pi*rho`; `Sigma_A=Sigma_R^*`; `Sigma_K=-2*i*pi*N`; `N/rho=coth(sqrt(s)/(2*T))`.
UNITS: Natural vacuum 3+1; `s`, self-energy components, spectral and noise measures use the declared energy-squared lane; `Phi` is not temperature or metric.
DERIVATION_CLASS: Action-derived numerical composition of audited greater/lesser/PV channels; no fitted coefficient and no external source.
OBSERVABLE: Retarded/advanced conjugacy, discontinuity, Keldysh convention, FDT, and convergence residuals.
VERIFICATION: Audit zero failed checks; maximum Keldysh FDT residual `1.1620995061153706e-16`; focused regression `3 passed`.
CONTROLLING_BLOCKER: `complete_off_shell_all_channel_1pi_and_physical_renormalization_anchor_missing`.
NEXT_ACTION: Evaluate the remaining off-shell all-channel object and source-lock an independent physical renormalization condition.
CLAIM_BOUNDARY: Declared natural-unit component lane only; not full 1PI, physical renormalization, transport, SI `Phi` mapping, `alpha_Phi_K`, TTG prediction, or Full Topic 13 closure.
FORMULA_ORIGIN: `rho`, `N`, and the component relations are action-derived real-time definitions over the audited channel measures; FDT is an equilibrium KMS identity in the declared normalization.
VERIFICATION_ROLE: Lane-level numerical audit; no external validation and no holdout access.

## T13-122: Off-Shell Threshold-Crossing 1PI Lane
- `major_result_id`: `T13_UET_O2_FINITE_T_OFFSHELL_THRESHOLD_CROSSING_1PI_LANE`
- `closure_level`: `CLOSED_FOR_LANE`
- `ontology`: `C` remains a collective system-behaviour coordinate; `Phi` remains an effective response variable; `R_gen` remains a derived history trace; `R_obs` remains an observer record.
- `equations`: `s_th=9*m^2`; `rho_13(s)=0` below the three-body threshold and positive above it; `rho_22(s)` is nonzero on selected below-threshold points; `Sigma_R=Re Sigma_sub-i*pi*rho`; `Sigma_A=Sigma_R^*`; `Sigma_K=-2*i*pi*N`; `N/rho=coth(sqrt(s)/(2*T))`.
- `units`: natural vacuum 3+1; `s`, spectral measures, noise measures, and self-energy components use the declared energy-squared lane; no SI `Phi` mapping is asserted.
- `derivation_class`: action-derived equal-mass threshold support, graph-summed `2<->2` scattering response, pole-subtracted PV continuation, and real-time component identities.
- `observable`: below/above-threshold support, PV convergence, retarded/advanced relations, Keldysh component identity, and equilibrium FDT over the crossing grid.
- `verification`: `t13_uet_o2_finite_temperature_offshell_threshold_crossing_1pi_audit.json`, zero failed checks; focused regression `3 passed`.
- `claim_boundary`: closes the declared threshold-crossing natural-unit lane only; it does not close complete all-channel 1PI, physical renormalization, Kubo, entropy, heat-flux, dimensional `Phi`, `alpha_Phi_K`, TTG, or Full Topic 13.
## T13-123: All 2-to-2 Permutation Identity
- `major_result_id`: `T13_UET_O2_FINITE_T_ALL_22_PERMUTATION_IDENTITY_LANE`
- `closure_level`: `CLOSED_FOR_LANE`
- `equations`: `P+k_minus=k_plus,1+k_plus,2`; `k_ref=(k_plus,1,k_plus,2,k_minus)`; `|det J|=1`; `I_22^(++-)=I_22^(+-+)=I_22^(-++)`; `w_single=1/6`; `w_22=3/6=1/2`.
- `ontology`: `C` remains a collective system-behaviour coordinate; `Phi` remains an effective response variable; `R_gen` remains a derived history trace; `R_obs` remains separate observer data.
- `units`: natural vacuum 3+1; invariant, spectral, noise, and self-energy quantities remain on the declared energy-squared lane; no SI `Phi` mapping is asserted.
- `derivation_class`: exact equal-mass dummy-line relabeling with unit Jacobian plus action-level sunset graph weight.
- `observable`: three permutation maps, aggregate response identity, KMS/FDT, and PV convergence.
- `verification`: `t13_uet_o2_finite_temperature_all_22_permutation_identity_audit.json`, zero failed checks; focused regression `3 passed`.
- `claim_boundary`: closes action-level permutation coverage only; complete off-shell 1PI, physical renormalization, transport, entropy, dimensional `Phi`, `alpha_Phi_K`, TTG, and Full Topic 13 remain open.
## T13-124 same-state Cp and density mapping

- Source mapping: `C_p^V = rho*C_p`.
- Conditional uncertainty mapping: `u(C_p^V | rho fixed) = rho*u(C_p)`.
- Constant-volume correction remains `c_v^V = C_p^V - T*alpha_V^2*K_T` and is not evaluated by this lane because matched alpha_V and K_T are not source-locked.
- Units: `C_p` in `J kg^-1 K^-1`, `rho` in `kg m^-3`, `C_p^V` in `J m^-3 K^-1`, `alpha_V` in `K^-1`, and `K_T` in `Pa`.
- Derivation class: source transcription, exact 300 C row matching, standard mass-to-volume identity, and conditional one-input uncertainty propagation. This is not a UET derivation.
- Claim boundary: the comparator does not map `Phi` to kelvin, does not emit `alpha_Phi_K`, and does not close the thermodynamic bridge.
## T13-125 Cp-only source boundary

- Ontology: the package records a standard-material comparator; it does not redefine `C`, `Phi`, `R_gen`, or `R_obs`.
- Quantity: `C_p(T)` is a mass-specific heat capacity, not `c_v` and not a volumetric observable.
- Units: `C_p` uses `J kg^-1 K^-1`; temperature is retained in K with source Celsius coordinates.
- Mapping boundary: `c_v^V = rho*(C_p - T*alpha_V^2*K_T)` is the declared correction, but it is not evaluated because the required same-state inputs are absent.
- Derivation class: source transcription plus uncertainty reconstruction from reported absolute Cp uncertainty; no UET derivation and no Phi calibration.
- Status: `CLOSED_FOR_LANE` only for source identity, row identity, and Cp uncertainty boundary; full thermodynamic bridge remains open.

## T13-126 - IG210 expansion comparator formula contract
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_ZENODO_HITRACE_IG210_ALPHA_L_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: Source transcription of the mean linear expansion coefficient and an explicit, conditional isotropic volume-expansion mapping.
WHAT_REMAINS_OPEN: `K_T`, density, `Cp/Cv`, Ding material equivalence, `C_src`, and `alpha_Phi_K` remain open.
EQUATION_OR_MAPPING: `alpha_l^mean(T;23 C)=mean(Delta_L/L)/(T-23 C)` as source quantity; `alpha_l[K^-1]=alpha_l[10^-6 K^-1]*10^-6`; `alpha_V=3*alpha_l` only under the declared isotropic geometry assumption; `c_p^V-c_v^V=T*alpha_V^2*K_T` remains an open conversion contract.
VERIFICATION: 15 rows have sheet/cell identity and four replicate values; the source model column remains separate; the source reports expanded uncertainty 10 percent at `k=2`, which is retained as a source-level bound rather than relabelled as an independent standard uncertainty.
CONTROLLING_BLOCKER: This is not a matched `alpha_V/K_T` pair and cannot close the volumetric heat-capacity correction.
NEXT_ACTION: Find a same-state `alpha_V` and isothermal `K_T` pair with material-regime mapping and uncertainty, then propagate only within the declared thermodynamic contract.
CLAIM_BOUNDARY: Source comparator and conditional geometry relation only; no UET derivation, `alpha_Phi_K`, TTG prediction, or Full Topic 13 claim.
DATA_ROLE: `EXTERNAL_SOURCE_COMPARATOR_NOT_CALIBRATION`.
EVIDENCE_PATHS: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/zenodo_5799133_ig210_alpha_l_source_package.json`; `docs/core/artifacts/t13_zenodo_ig210_alpha_l_source_audit.json`.
## T13-128 - IG210 thermophysical source formula contract
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_FAROOQUI_IG210_THERMOPHYSICAL_SOURCE`.
WHAT_IS_ACTUALLY_CLOSED: Source-level property rows and uncertainty contracts are auditable without changing the UET ontology.
WHAT_REMAINS_OPEN: The thermodynamic conversion from `C_p` to `C_v` needs a source-matched `K_T`; no UET SI anchor or `alpha_Phi_K` is emitted.
DEPENDENCY_UNLOCKED: Source comparator lane only.
STATUS: `PASS_SCOPED_FAROOQUI_IG210_THERMOPHYSICAL_SOURCE`; full Topic 13 remains blocked.
WHAT_CHANGED: Added a published-source formula and unit audit for IG-210.
EQUATION_OR_MAPPING: `c_v^V = rho*(C_p - T*alpha_V^2*K_T)`; `alpha_V=3*alpha_l` only under isotropic geometry; `kappa=rho*C_p*D` remains source context.
VERIFICATION: Three rows at 500/700/1000 C, units are declared, expanded bounds use `k=2`, and all 15 source checks pass.
CONTROLLING_BLOCKER: Missing same-state `K_T` and independent `alpha_Phi_K`.
NEXT_ACTION: Acquire `K_T` or record a no-go; keep the lane outside calibration and holdout paths.
CLAIM_BOUNDARY: No `C_v`, Ding `C_src`, UET transport derivation, temperature prediction, or Full Topic 13 claim.

## T13-129 IG210 K_T formula boundary
MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for the source-compatibility boundary only.
WHAT_IS_ACTUALLY_CLOSED: The IG210 package supplies source-traceable C_p, density, alpha_l, and conductivity rows; it does not supply the K_T term required to evaluate c_v^V.
WHAT_REMAINS_OPEN: The formula c_v^V = rho*(C_p - T*alpha_V^2*K_T) remains unevaluated for IG210. alpha_V = 3*alpha_l remains a conditional isotropic geometry mapping, not a source-reported universal identity.
DEPENDENCY_UNLOCKED: Formula audit boundary only; no volumetric c_v, UET SI map, calibration, or full bridge dependency is unlocked.
STATUS: PASS_SCOPED_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY_NO_GO; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Added explicit IG210 absence checks for K_T, C_v, and alpha_Phi_K emission to the matched-source audit.
EQUATION_OR_MAPPING: alpha_V has units K^-1; K_T has units Pa; c_v^V has units J m^-3 K^-1. No numeric Cp-to-Cv correction is emitted.
VERIFICATION: All matched-source checks passed; focused regression 2 passed; full gate remains partial; holdout access remains false.
CONTROLLING_BLOCKER: same_state_IG210_K_T_missing.
NEXT_ACTION: Obtain a permitted same-state K_T source with uncertainty or preserve the formula as open.
CLAIM_BOUNDARY: No UET derivation, no K_T inference, no transport coefficient, and no Full Topic 13 closure.
## T13-130 - Covariant action symbolic SI conversion formula boundary
MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE only.
WHAT_IS_ACTUALLY_CLOSED: The dimensional powers and unit labels for the natural-unit to SI conversion are explicit and regression-tested, conditional on E_ref and Phi_scale.
WHAT_REMAINS_OPEN: The physical origin and numeric value of E_ref, covariant field normalization, base Phi -> Phi_E, e0, and alpha_Phi_K remain open.
DEPENDENCY_UNLOCKED: Formula-contract lane only; no physical calibration or Core unlock.
STATUS: PASS_SCOPED_SYMBOLIC_ACTION_SI_CONVERSION_CONTRACT.
WHAT_CHANGED: Added exact-constant loading, symbolic conversion helpers, audit checks, and regression coverage.
EQUATION_OR_MAPPING: u_SI=u_nat*E_ref^4/(hbar*c)^3; C_SI=C_nat*k_B*E_ref^3/(hbar*c)^3; Delta_Tq=(E_ref/k_B)*Delta_theta; Phi_normalized=Phi_covariant/Phi_scale.
VERIFICATION: Audit has zero failed checks; regression 4 passed; no numeric coefficient was fitted or inferred.
CONTROLLING_BLOCKER: energy_reference_and_base_Phi_normalization_provenance_missing.
NEXT_ACTION: Establish coefficient provenance before using the symbolic map to evaluate any SI observable.
CLAIM_BOUNDARY: Unit algebra only; not proof of UET dynamics, thermal transport, or alpha_Phi_K.

## T13-131 - Huberman public PBTE formula boundary

The Huberman source method is retained as comparator context: `g_i` is a mode-specific deviational energy density, `C=sum_i c_i`, and `Delta_T=(1/C)sum_i g_i`. These are source-method relations, not UET derivations and not a numeric `C_src` import.

The Topic 13 source acceptance contract remains `C_src(T)=sum_mu c_mu(T)` with units `J m^-3 K^-1` and `Delta_Tq=Delta_u_ph/C_src`. No unit-closed row, uncertainty, convergence, or `Phi` mapping is emitted by this lane.

## Berut Figure 3 Local Archive (2026-08-20)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE

WHAT_IS_ACTUALLY_CLOSED: The official publisher Figure 3 route was
download-tested. Its remote binary identity is pinned by SHA-256, byte size,
OLE signature, retrieval date, and an explicit four-asset raster inventory.

WHAT_REMAINS_OPEN: No raster is accepted as a numeric row yet. Selected panel,
axis ticks and units, point or curve selection, digitization uncertainty,
preprocessing, and row identity remain open.

DEPENDENCY_UNLOCKED: Berut figure-acquisition route only. No numeric source,
alpha_Phi_K, Full Topic 13, Core, Gravity, or transport dependency is unlocked.

STATUS: PASS_REMOTE_FIGURE3_BINARY_IDENTITY

WHAT_CHANGED: docs/core/artifacts/t13_berut_figure3_remote_binary_identity.json records the official article/download locators,
binary hash e4bab6be849a093b7578bc52ce6df9be95dc25d83d51ecb718b4f798a37d50fa, size
479744 bytes, and embedded raster inventory.
The binary is archived locally at the hash-linked raw path; no raw measurement table is implied.

EQUATION_OR_MAPPING: Figure 3 is a source-surface asset for the Berut
heat-versus-erasure-duration observable; no numeric Delta_Tq or alpha_Phi_K
mapping is emitted.

VERIFICATION: Binary identity and asset inventory checks pass; accepted numeric
rows emitted: 0; no fit, target data, calibration, or Xie 2026 holdout was used.

CONTROLLING_BLOCKER: berut_selected_panel_and_axis_tick_mapping_missing

NEXT_ACTION: Select one quantitative panel, record axis ticks and units, map selected points or curve with declared digitization uncertainty, and archive row identity and preprocessing before source-normalized use.

CLAIM_BOUNDARY: Remote binary identity only. This is not a source-normalized
numeric row, uncertainty result, calibration, prediction, or external validation.

## Berut Source Package Availability Boundary (2026-08-20)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The Berut working copies in the current checkout are
classified as topic-derived summaries, not raw experimental rows. The captured
publisher surface is recorded as a Figure 3/PPT acquisition route, while the
absence of a local raw or separately exposed source-data package is explicit.

WHAT_REMAINS_OPEN: The official Figure 3 binary/hash, selected panel and axis
mapping, numeric transcription, row identity, preprocessing, and uncertainty
package remain open. No Berut numeric row is eligible for calibration.

DEPENDENCY_UNLOCKED: Berut source-acquisition decision only. No Full Topic 13,
Core, Gravity, or constitutive-transport dependency is unlocked.

STATUS: `PASS_SCOPED_BERUT_SOURCE_PACKAGE_BOUNDARY`

WHAT_CHANGED: `docs/core/artifacts/t13_berut_source_package_availability_boundary.json` records the source identity, publisher locator,
current local inventory, source-surface scope, and non-calibration policy.

EQUATION_OR_MAPPING: `E_min = k_B T ln(2)` remains an imported standard
constraint. No numeric `Delta_Tq = alpha_Phi_K * Delta_Phi` mapping is emitted.

VERIFICATION: All source identity, summary-role, no-raw-file, surface-scope,
holdout, no-fit, and no-calibration checks pass; accepted numeric rows emitted:
`0`.

CONTROLLING_BLOCKER: `berut_permissioned_raw_numeric_package_missing`

NEXT_ACTION: Obtain a permissioned raw numeric table or numeric measurement uncertainty for the Berut rows; keep the archived Figure 3c transcription as comparison-only and outside alpha calibration.

CLAIM_BOUNDARY: This is a provenance and acquisition boundary, not a closed
Berut numeric row, uncertainty result, `alpha_Phi_K`, UET bridge, or external
validation.

## T13-145 - Semantic alpha-calibration admission gate

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for the calibration-admission contract; the numeric alpha_Phi_K result remains open.

WHAT_IS_ACTUALLY_CLOSED: Candidate eligibility is evaluated from substantive values within one paired record rather than from field-name presence across an arbitrary JSON tree. The gate requires source identity and locator, matched material/state/geometry, finite base-Phi and SI response amplitudes, units, numeric uncertainty, preprocessing, row identity, a valid source hash, and an independence statement.

WHAT_REMAINS_OPEN: All 11 current candidate packages remain ineligible. No independent paired base-Phi/SI record, numeric alpha_Phi_K, or base-Phi to Phi_E scale was produced.

DEPENDENCY_UNLOCKED: Calibration-admission contract only; no alpha, dimensional map, Full Topic 13, Core, Gravity, or transport dependency is unlocked.

STATUS: PASS_SCOPED_NO_ELIGIBLE_PAIRED_ALPHA_RECORD; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE / PARTIAL.

WHAT_CHANGED: The candidate audit now validates semantic paired records and keeps key-presence diagnostics separate. The full gate, closure register, and dependency projection consume the regenerated candidate artifact.

EQUATION_OR_MAPPING: y_TTG^UET = Delta_Phi(t) / Delta_Phi(0); Delta_Tq = alpha_Phi_K * Delta_Phi; no coefficient is emitted from normalized data, Landauer, or a comparator package.

VERIFICATION: Candidate count is 11 and eligible count is 0; numeric_alpha_Phi_K_emitted=false, holdout_accessed=false, and target_fit_performed=false. The focused regression passed with 10 tests.

CONTROLLING_BLOCKER: independent_paired_base_Phi_amplitude_and_SI_observable_record_missing.

NEXT_ACTION: Obtain a permitted paired base-Phi/SI record or derive a coefficient-provenance-backed dimensional map without reading Xie 2026, then rerun the semantic admission gate before any calibration or prediction.

CLAIM_BOUNDARY: This closes the admission and provenance boundary only. It is not a numeric calibration, temperature prediction, external validation, or Full Topic 13 closure.
## T13-147 - Joint thermal-bridge scale-dependency no-go

MAJOR_RESULT_CLOSURE: `CLOSED_AS_NO_GO` for the current normalized/action scale question; the thermal dimensional bridge remains open.

WHAT_IS_ACTUALLY_CLOSED: Field rescaling of the declared scalar action leaves the action terms and normalized Phi coordinate invariant when the scalar coefficients and field scale transform together. A joint field/energy-density scale family leaves normalized TTG shape unchanged but changes the absolute Kelvin response and the normalized beta correspondence.

WHAT_REMAINS_OPEN: Independent field-energy-temperature scale provenance, paired base-Phi/SI observable evidence, physical beta source provenance, and the base-Phi-to-Delta_u_ph mapping remain missing.

DEPENDENCY_UNLOCKED: None. The result closes a structural identifiability question and does not satisfy the alpha, dimensional observable, EOS, transport, KMS, entropy, or source gates.

STATUS: `PASS_SCOPED_THERMAL_BRIDGE_SCALE_DEPENDENCY_NO_GO`.

WHAT_CHANGED: Added a deterministic field/action and joint-scale witness plus a machine-readable major-result artifact. The full gate places this lane under `dimensional_observable_map`.

EQUATION_OR_MAPPING: `y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)`; `Delta_Tq = alpha_Phi_K * Delta_Phi`; `alpha_Phi_K' = alpha_Phi_K / s_phi`; `beta_T13 = (Phi_scale^2 / e0_scale) beta_Phi^nat`; `Delta_Tq = (e0 / c_v) r_Phi Delta_Phi`.

VERIFICATION: `t13_thermal_bridge_scale_dependency_no_go.json` passed all structural checks; no numeric alpha_Phi_K/e0, target, fit, Landauer inference, threshold tuning, or Xie 2026 access was used. Full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL` with 10 blockers.

CONTROLLING_BLOCKER: `independent_field_energy_and_temperature_scale_map_missing`.

NEXT_ACTION: Seek a permitted source-locked field residue or independent paired Phi/SI observable anchor, then rerun dimensional and alpha admission without using normalized target residuals.

CLAIM_BOUNDARY: Scoped structural no-go only; no physical coefficient, Kelvin prediction, external validation, or Core closure is claimed.

## T13-148 - AIST source-route boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`; no formula or SI coefficient was promoted.
WHAT_IS_ACTUALLY_CLOSED: The AIST TPDS route is catalogued as a possible thermophysical source surface, but its displayed terms do not permit embedding the numeric contents in the public repository. The local artifact stores metadata only and marks the route as non-calibration.
WHAT_REMAINS_OPEN: Numeric `c_v`, density/uncertainty, material-state mapping, Ding `C_src`, and independent `alpha_Phi_K` remain open.
DEPENDENCY_UNLOCKED: None beyond source-route classification.
STATUS: `PASS_SCOPED_AIST_GRAPHITE_SOURCE_ROUTE_BOUNDARY`; full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added a source-route audit and gate lane with explicit no-payload and no-redistribution fields.
EQUATION_OR_MAPPING: Candidate relation `c_v^V(T, material) = rho(T, material) * c_v(T, material)` is recorded with `c_v` in `J kg^-1 K^-1`, `rho` in `kg m^-3`, and `c_v^V` in `J m^-3 K^-1`; it is not evaluated numerically. The UET bridge remains `y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)` and `Delta_Tq = alpha_Phi_K * Delta_Phi`, with alpha uninstantiated.
VERIFICATION: AIST metadata boundary artifact and focused regression passed; no material detail, numeric payload, fit, calibration, or holdout was accessed.
CONTROLLING_BLOCKER: `aist_numeric_payload_not_publicly_redistributable` for this route; global full-bridge blockers are unchanged.
NEXT_ACTION: Seek a permitted redistributable numeric source or a separately controlled private source package; do not relabel AIST metadata as c_v evidence.
CLAIM_BOUNDARY: Source-provenance boundary only; no numeric thermodynamic correction, calibration, prediction, or external validation.
## T13-149 - NIST SRM 3600 heat-capacity comparator boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`; this is a source/material/uncertainty boundary, not physical Topic 13 closure.
WHAT_IS_ACTUALLY_CLOSED: The official NIST SRM 3600 PDF identity, hash, page locators, 20-295 K comparison range, and source-reported approximately +/-2 percent 90 percent-confidence uncertainty boundary are recorded. The paper's glassy-carbon and graphite-powder material identity is kept separate from Ding HOPG PBTE `C_src`.
WHAT_REMAINS_OPEN: Figure 3 supplies no machine-readable rows in the archived paper; row-level standard uncertainty, same-state Ding mapping, volumetric `c_v`, `C_src`, `alpha_Phi_K`, SI map, and physical transport remain open.
DEPENDENCY_UNLOCKED: Comparator lane only; no calibration or downstream dependency unlock.
STATUS: `PASS_SCOPED_NIST_SRM_3600_HEAT_CAPACITY_COMPARATOR_BOUNDARY`.
WHAT_CHANGED: Added a source-boundary artifact and verifier, connected it to the canonical full gate, and preserved the raw PDF as local-only ignored source material.
EQUATION_OR_MAPPING: `c_v^V = rho c_v^m` is a declared standard-physics conversion contract only; no numeric row or UET mapping is emitted.
VERIFICATION: Hash/source-boundary verifier and synchronized focused regression passed; `numeric_rows_emitted=0`, `figure_only_payload=true`, `material_match_to_Ding_TTG=false`, `holdout_accessed=false`.
CONTROLLING_BLOCKER: `figure_only_numeric_payload_and_Ding_material_mapping_missing`.
NEXT_ACTION: Seek a permitted same-state numeric source or separately controlled Ding-compatible PBTE package with uncertainty and convergence; do not use Figure 3 or its approximate uncertainty as `C_src` or alpha calibration.
CLAIM_BOUNDARY: Source-traceable comparator boundary only; not a formula derivation, SI calibration, temperature prediction, external validation, or Full Topic 13 closure.
## T13-150 - Perez-Castaneda HOPG specific-heat source boundary

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for a source-traceable HOPG specific-heat comparator boundary; not CLOSED_FOR_CORE.

WHAT_IS_ACTUALLY_CLOSED: The author-posted paper is hash-locked with DOI/arXiv and page-level locators. The HOPG specimen identity, natural-graphite comparison identity, temperature range, and below-3-percent method-comparison statement are recorded. The published numeric route is figure-only and cannot be promoted to row-level evidence.

WHAT_REMAINS_OPEN: Machine-readable rows, row-level uncertainty, fixed-volume c_v, Ding material/state and PBTE-response mapping, Ding C_src, independent alpha_Phi_K, dimensional Phi mapping, and full EOS/transport/KMS/entropy closure remain open.

DEPENDENCY_UNLOCKED: HOPG source-boundary lane only; no c_v, C_src, alpha, Full Topic 13, Core, Gravity, constitutive transport, or Galaxy dependency is unlocked.

STATUS: PASS_SCOPED_HOPG_SPECIFIC_HEAT_SOURCE_BOUNDARY; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE / PARTIAL.

WHAT_CHANGED: Added the hash-locked author-posted PDF source boundary, verifier, focused test, full-gate source-package projection, closure-register/dependency synchronization, and this formula-audit entry. No figure digitization, synthetic replacement, fit, threshold change, Landauer inference, or Xie 2026 access occurred.

EQUATION_OR_MAPPING: Candidate standard-physics relation is c_p^m(T, material) with candidate volumetric map c_v^V(T, material) = rho(T, material) * c_p^m(T, material) - Cp-to-Cv correction. No numeric rows or correction are emitted. The UET measurement contract remains y_TTG = Delta_Tq(t) / Delta_Tq(0), y_TTG^UET = Delta_Phi(t) / Delta_Phi(0), and Delta_Tq = alpha_Phi_K * Delta_Phi; alpha remains uninstantiated.

VERIFICATION: Raw PDF SHA-256 is f5056e3804275336deca634da84a47fec1e91876ff65ab62a84596a5ad3ebd4a, size 1141942 bytes, 21 pages; numeric_rows_emitted=0; figure_only_payload=true; method_comparison_relative_bound=0.03; row_level_standard_uncertainty_present=false; Ding match=false; focused source/gate/register/dependency regression passed 13 tests. Full gate remains 10 blockers, claim promotion=false, and Xie 2026 remains unconsumed.

CONTROLLING_BLOCKER: figure_only_numeric_payload_and_Ding_PBTE_response_mapping_missing for this lane; the global primary blocker remains the missing independent dimensional/alpha anchor together with the other full-bridge blockers.

NEXT_ACTION: Acquire a permitted machine-readable same-state heat-capacity or Ding PBTE C_src package with row locators, units, row-level uncertainty, preprocessing, convergence, material identity, and hash; do not digitize Figures 6-8 into calibration without a declared digitization and uncertainty contract.

CLAIM_BOUNDARY: Comparator source boundary only; not numeric C_src, not alpha calibration, not a temperature prediction, not external validation, and not Full Topic 13 closure.

EVIDENCE_PATHS: docs/core/artifacts/t13_perez_castaneda_hopg_source_boundary_audit.json; docs/scripts/audit/audit_topic13_perez_castaneda_hopg_boundary.py; docs/core/test/test_topic13_perez_castaneda_hopg_boundary.py; docs/scripts/audit/audit_topic13_full_bridge_gate.py; docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json; docs/core/artifacts/uet_major_result_closure_register.json; docs/core/artifacts/uet_major_result_dependency_unlock_gate.json.

EVIDENCE_HASHES: artifact a7116b76ede94cd71f70d61c488795159ca4cf9e9f9922b9960f9f1166640fdf; verifier 3adcfe4166b7f0729a43daa8d34b8644cc401040c470f8245304049d9842069c; regression a9ccf1c613494af41dc59d0720045f5124141fee424fbbdce8e8dc8c4832ab01; full gate fe00b27f371e78ef4f337ffd5a66e8c6e54bf5fdcc8ef19826cfd44e37f2143c; register a5a2c43cd059db34edc18b85866a7eb9e387bc47ccd4a4234989be69a0d01816; dependency d76237a766620684b46cb7fce270cfe553f6ed81c0ba8715ea542bd84c87a7fe.
## T13-151 - Calorine full-LBTE numerical stability boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`; this is an external full-LBTE numerical boundary, not a UET transport derivation.
WHAT_IS_ACTUALLY_CLOSED: The source-locked force-constant identity, natural-isotope control, full-LBTE solver-method comparison, collision-spectrum sign diagnostic, and adjacent mesh response record are reproducible from the archived local payload hashes.
WHAT_REMAINS_OPEN: `kappa` is not accepted as a UET coefficient. The collision matrix is not positive semidefinite at the high mesh, method-1 response is not converged, and material/state equivalence, source uncertainty, `alpha_Phi_K`, SI `Phi` mapping, Kubo, EOS, KMS, and entropy closure are absent.
DEPENDENCY_UNLOCKED: None beyond the numerical-boundary lane.
STATUS: `WARN_FULL_LBTE_NUMERICAL_STABILITY_OPEN`.
WHAT_CHANGED: Added formula and solver semantics for `pinv_method=0/1` and kept the source mapping separate from UET variables.
EQUATION_OR_MAPPING: `C_src(T) = [sum_q w_q sum_mu c_qmu(T)] / [sum_q w_q V_primitive]`; `Delta_Tq = Delta_u_ph/C_src(T)`; `kappa` is a candidate heat-current response. `C_src` is not UET `C`; `Phi` and `R_gen` are not relabeled.
VERIFICATION: `pinv_method=0` yields negative in-plane `kappa` at 300 K; method `1` ignores negative eigenvalues but the latest mesh change is `0.129379135193`. No fit, calibration, or Xie 2026 holdout access occurred.
CONTROLLING_BLOCKER: `full_lbte_collision_spectrum_positive_semidefinite_missing` and `full_lbte_mesh_convergence_missing`.
NEXT_ACTION: Supply a declared, source-supported collision/transport stability and uncertainty contract before any physical transport comparison.
CLAIM_BOUNDARY: Numerical boundary only; no UET dimensional map, `alpha_Phi_K`, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE: `docs/core/artifacts/t13_calorine_full_lbte_stability_boundary_audit.json` (SHA-256 `8b5de32a8c33b0a646c8e26faf263585d98bcb939df8adb78b1b16f9d832859d`).

## T13-152 - QH-15 Graphite Comparator Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_QH15_GRAPHITE_CV_COMPARATOR_BOUNDARY`; Full Topic 13 remains `PARTIAL`.
WHAT_IS_ACTUALLY_CLOSED: QH-15 source identity, selected raw-entry hashes, `SpecificC` column units, the `1.0e9` SI conversion, separate isopure control, and non-fitting 200/300 K comparison with the Calorine candidate.
WHAT_REMAINS_OPEN: Ding mode-resolved `C_src`, response-contract/material mapping, source-grade uncertainty, independent `alpha_Phi_K`, and full thermodynamic closure.
DEPENDENCY_UNLOCKED: Comparator lane only; no Core, Gravity, transport, Galaxy, or external claim is unlocked.
STATUS: `PASS_SCOPED_QH15_CV_COMPARATOR_BOUNDARY`.
WHAT_CHANGED: Added a source package and verifier that keep macroscopic QH-15 `SpecificC` separate from Ding `C_src` and from the UET `Phi` map.
EQUATION_OR_MAPPING: `C_v^QH15 = SpecificC * 1.0e9 J m^-3 K^-1`; `r_T = (C_v^QH15-C_src^Calorine)/C_src^Calorine`.
VERIFICATION: Source hashes, row schema, unit witness, selected rows, cross-check rows, no-fit policy, no-alpha policy, and Xie holdout non-access pass. The cross-checks are `-0.682889%` at 200 K and `+0.014257%` at 300 K.
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.
NEXT_ACTION: Obtain an authorized Ding numeric package or accepted same-regime PBTE reproduction with source-grade uncertainty; do not use QH-15 to calibrate Phi.
CLAIM_BOUNDARY: Comparator evidence only; not Ding `C_src`, not alpha calibration, not temperature prediction, not external validation, and not Full Topic 13 closure.
EVIDENCE: `docs/core/artifacts/t13_qh15_graphite_transport_boundary_audit.json`.

## T13-153 - Covariant matter-coupling normalization identifiability

MAJOR_RESULT_CLOSURE: `CLOSED_AS_NO_GO` for the declared natural-unit response-matter coupling chart; Full Topic 13 remains `PARTIAL` / `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: The implemented reciprocal interaction `V_int = -epsilon_nc * response_coupling * delta_phi * (chi_1^2 + chi_2^2) / 2` is invariant under `delta_phi_prime=s delta_phi` and `response_coupling_prime=response_coupling/s`. The response force transforms covariantly, the matter force remains invariant in the fixed matter chart, and the normalized coordinate remains unchanged after `Phi_scale_prime=s Phi_scale`.
WHAT_REMAINS_OPEN: A source-locked physical field residue or interaction coefficient, a system-specific SI energy-density contract, the base-Phi-to-Phi_E map, independent `alpha_Phi_K`, and the matter-amplitude-to-density `C` reduction remain open.
DEPENDENCY_UNLOCKED: None. This is an action-coupling identifiability no-go only; it does not unlock the SI thermal bridge, Core curved 3+1, Gravity, transport, or external validation.
STATUS: `PASS_SCOPED_NO_GO_COVARIANT_MATTER_COUPLING_NORMALIZATION`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`; claim promotion remains false.
WHAT_CHANGED: Added a structural action-coupling witness, machine-readable artifact, focused tests, and gate/register/dependency linkage. No target data, fit, Landauer inference, or Xie 2026 holdout access was used.
EQUATION_OR_MAPPING: `[delta_phi]=[chi_A]=1`, `[epsilon_nc]=0`, `[response_coupling]=1`, `[V_int]=4` in natural units; `response_coupling_prime=response_coupling/s`; raw `alpha_base_prime=alpha_base/s` preserves a raw-field product, while normalized `Phi` requires an external `Phi_scale` contract.
VERIFICATION: The action, reciprocal derivatives, natural-unit dimension declaration, prior field-normalization no-go, and deterministic rescaling witness all pass. `numeric_e0_emitted=false`, `numeric_alpha_Phi_K_emitted=false`, `target_data_used=false`, `xie_2026_accessed=false`, and `landauer_used_for_derivation=false`.
CONTROLLING_BLOCKER: `physical_field_normalization_and_interaction_coefficient_provenance_missing`; the full Topic 13 controller remains the missing independent dimensional/alpha anchor together with Ding/source and EOS/transport/KMS/entropy blockers.
NEXT_ACTION: Source-lock a physical response residue or interaction coefficient with canonical matter normalization and SI units/uncertainty, or obtain an independent non-TTG alpha calibration; do not infer the scale from normalized TTG or Xie 2026.
CLAIM_BOUNDARY: This closes only a no-go for the current natural-unit action chart. It does not prove that a future physical normalization is impossible, does not identify `Phi` with `C`, temperature, heat flux, entropy, or `R_gen`, and does not close Topic 13.
EVIDENCE: `docs/core/artifacts/t13_covariant_matter_coupling_normalization_no_go.json`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`; `docs/core/artifacts/uet_major_result_closure_register.json`; `docs/core/artifacts/uet_major_result_dependency_unlock_gate.json`.

## T13-154 - Ding Experimental Heating Input Boundary

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_DING_EXPERIMENTAL_HEATING_INPUT_BOUNDARY; Full Topic 13 remains PARTIAL / BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_IS_ACTUALLY_CLOSED: The Ding 2022 source identity, local full-text hash, method locators, reported pump/probe setup rows, the <3 K surface-temperature upper bound, and the geometric incident-fluence conversion are machine-readable and independently rechecked.
WHAT_REMAINS_OPEN: Absorption fraction, optical penetration depth, thermalized volume, absorbed energy density, numeric Ding C_src(T), base Phi-to-energy mapping, e0, independent alpha_Phi_K, and the remaining thermodynamic bridge closure.
DEPENDENCY_UNLOCKED: Incident TTG setup provenance and geometric fluence lane only; no Ding C_src acceptance, SI Phi anchor, alpha calibration, or Full Topic 13 dependency is unlocked.
STATUS: PASS_SCOPED_DING_EXPERIMENTAL_HEATING_INPUT_BOUNDARY.
WHAT_CHANGED: Added a source package, source-hash audit, typed setup rows, SI unit conversion, focused regression, full-gate source-package projection, closure-register entry, and dependency evidence. No absorbed-energy value, fit, calibration, threshold adjustment, Landauer inference, or Xie 2026 holdout access was introduced.
EQUATION_OR_MAPPING: w=d_1e2/2; A_1e2=pi*w^2; F_incident=E_pump/A_1e2 = 6.189358898018153 J m^-2 for the reported 70 nJ and 120 um 1/e2 diameter. Delta_u_abs=eta_abs*F_incident/l_abs remains conditional on source-locked absorption inputs; Delta_Tq=Delta_u_ph/C_src remains formula-only until numeric C_src is accepted.
VERIFICATION: 21/21 source checks pass; raw text is 41581 bytes with SHA-256 b1b029f2812586647077a7b8506c2f52aeb7261714395907f8f8d20868fe2874; package/audit/full-gate/closure/dependency hashes are recorded below. The current full gate remains BLOCKED_OPEN_T13_FULL_BRIDGE with the same 10 open blocker groups; holdout access remains false.
CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing together with alpha_Phi_K_independent_calibration_missing.
NEXT_ACTION: Obtain an authorized Ding numeric C_src package or accepted same-regime PBTE reproduction with uncertainty and state mapping; separately obtain the independent base-Phi/SI anchor. Do not infer absorbed energy, e0, or alpha from incident fluence or the <3 K bound.
CLAIM_BOUNDARY: This closes only the source/setup and incident-fluence lane. It does not identify absorbed energy density, predict Delta_Tq, derive e0, calibrate alpha_Phi_K, validate UET externally, or close Full Topic 13.
EVIDENCE: package 62e6f6ce403c74e0601b2e05f6be2d2a5728d0237fb5392774713f9ee0a8eccd; audit 6e39bbf42037971dc2b5a1068df14835dd0b4689f26a60fff95bc26810b8b008; full gate 065f734a58d542cc98c1dfdf4ecc2f67768641a05205fce57b5109e6e11c0560; closure register 9a8fe0b9598755e48577d103b38768a0a321e89abbe3597fb499b5e8854c289e; dependency gate 78c8424bb973ecaa20b72b8683e45bac7efff05e7fd21adc348e1a98d5a8c9ec.

## T13-155 - Ding C_src fixed-volume thermodynamic identity

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_DING_C_SRC_FIXED_VOLUME_THERMODYNAMIC_IDENTITY`; Full Topic 13 remains `PARTIAL` / `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: Under a declared fixed-volume mode basis, the Ding PBTE denominator is conditionally identified as the temperature derivative of the phonon thermal-energy density. The Bose-mode kernel, SI unit route, source locators, and separation from UET `C` are machine-readable and numerically checked.
WHAT_REMAINS_OPEN: Numeric Ding `C_src(T)`, accepted same-regime reproduction, material/state and volume identity, anharmonic frequency-temperature dependence, source-grade uncertainty/convergence, base `Phi` to energy, and independent `alpha_Phi_K` remain open.
DEPENDENCY_UNLOCKED: Conditional `C_src` to fixed-volume `c_v` identity only; no numeric Ding source, alpha, bridge, transport, Core, Gravity, or external-validation dependency is unlocked.
STATUS: `PASS_SCOPED_C_SRC_FIXED_VOLUME_IDENTITY`.
WHAT_CHANGED: Added `audit_topic13_csrc_fixed_volume_identity.py`, its artifact and focused regression, then projected the result into the full gate, closure register, and dependency gate. No comparator was relabeled as Ding `C_src`.
EQUATION_OR_MAPPING: `u_ph(T,V)=(1/V) sum_mu[hbar*omega_mu(V)*n_B]`; `C_src(T,V)=(partial u_ph/partial T)_V=(1/V) sum_mu c_mu(T,V)`; for fixed frequencies `c_mu/V=k_B*x_mu^2*exp(x_mu)/(V*(exp(x_mu)-1)^2)`. The source response remains `Delta_Tq=Delta_u_ph/C_src`; `C_p^vol-C_v^vol=T*alpha_V^2*K_T` is a separate correction and is not used to manufacture Ding `C_src`.
VERIFICATION: Source locators and unit/ontology contracts pass; analytic Bose-mode derivative agrees with the central finite-difference witness at relative error `7.995153125698355e-11`; focused Topic 13 regression passed `19` tests; full gate remains blocked with `10` open blockers; Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: `ding_pbte_numeric_C_src_or_accepted_independent_reproduction_missing`; independent `alpha_Phi_K` and the remaining SI/EOS/transport/KMS/entropy blockers remain open.
NEXT_ACTION: Obtain a source-locked Ding-compatible mode or fixed-volume `c_v` record with material/state, volume, uncertainty, and convergence metadata; evaluate it under this identity without fitting alpha or reading the holdout.
CLAIM_BOUNDARY: Conditional standard-physics identity only; no numeric `C_src`, no temperature prediction, no base-Phi calibration, no external validation, and no Full Topic 13 closure.
EVIDENCE: `docs/core/artifacts/t13_csrc_fixed_volume_identity_audit.json` (SHA-256 `155b15ac1184f0309e10db8466925d6ad6483d4321a7703d82ecfb09a086cdd5`); full gate `f0cddb266247c0454ed2f89775a7eefc033d3ce1ef8d84cde574a9e4bfc8df50`; closure register `eb044c3083382b61855baa8ee26ea847a85005c148f5e0b85612a74bfb7b3c0b`; dependency gate `985a9727e59db875b6446096942b07b70375da9ba59cb06cc456e9cd25ef93e2`; verifier/test paths are adjacent.
## T13-162 - Day 2012 preferred thermodynamic assessment boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_DAY2012_PREFERRED_THERMODYNAMIC_ASSESSMENT_BOUNDARY`; Full Topic 13 remains `PARTIAL` / `BLOCKED_OPEN_T13_FULL_BRIDGE`.

WHAT_IS_ACTUALLY_CLOSED: Day 2012 Table 2 is source-locked at its publisher/printed-page locator. The graphite assessment records `B0 = 338 +/- 30 kbar (2 sigma)`, `dB/dT = -0.07 +/- 0.02 kbar K^-1 (2 sigma)`, and the stated volume-expansion function.

WHAT_REMAINS_OPEN: The table reports no uncertainty for the graphite thermal-expansion coefficient/function, does not establish a same-specimen alpha_V/K_T pair, and does not close Ding TTG material-regime mapping. The Cp-to-Cv correction, independent `alpha_Phi_K`, Ding `C_src`, physical Kubo, SI map, and full EOS/transport/KMS/entropy remain open.

DEPENDENCY_UNLOCKED: Day source-compatibility boundary only; no numeric thermodynamic correction, Ding C_src, alpha calibration, Core, Gravity, transport, Galaxy, or external-validation dependency is unlocked.

STATUS: `PASS_SCOPED_DAY2012_THERMODYNAMIC_ASSESSMENT_BOUNDARY_NO_GO`.

WHAT_CHANGED: Added the Day source package, route audit, machine-readable artifact, full-gate projection, closure-register/dependency evidence, and focused regression. No values were combined with another specimen and no correction was emitted.

EQUATION_OR_MAPPING: `V(T)/V0 = 1 + a0*(T - 298) - 20*a0*(sqrt(T) - sqrt(298))`; `K_T(T) = B0 + Bprime*(T - 298)` under the table notation; `c_p^V - c_v^V = T*alpha_V^2*K_T` remains a declared but unevaluated contract.

VERIFICATION: All Day route checks pass; focused integration suite `14 passed`; full gate remains blocked with 9 open blockers; `claim_promotion=false`; Xie 2026 remains unconsumed.

CONTROLLING_BLOCKER: `same_grade_alpha_V_and_K_T_missing` for this route; `alpha_V_source_uncertainty_not_reported` is an explicit route-level sub-blocker.

NEXT_ACTION: Acquire a permitted same-state alpha_V/K_T record with units, uncertainty, row/state identity, and Ding-regime mapping, or retain this no-go while continuing independent Ding/PBTE and Phi/SI acquisition.

CLAIM_BOUNDARY: Source-compatibility evidence only; not a numeric Cp-to-Cv correction, Ding `C_src`, independent `alpha_Phi_K`, TTG prediction, physical transport, external validation, or Full Topic 13 closure.

EVIDENCE: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/day_2012_preferred_thermodynamic_table_source_package.json`; `docs/core/artifacts/t13_day2012_preferred_thermodynamic_table_boundary_audit.json`; `docs/scripts/audit/audit_topic13_day2012_preferred_thermodynamic_table.py`.

## T13-163 - Kim 2018 external Green-Kubo input

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_KIM_2018_GRAPHITE_GREEN_KUBO_EXTERNAL_INPUT; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE / PARTIAL.

WHAT_IS_ACTUALLY_CLOSED: The public source locator, Eq. (2) Green-Kubo relation, Eq. (3) uncertainty locator, 300 K pristine-graphite c-axis and basal-plane rows, convergence metadata, and canonical source-transcription hash are recorded.

WHAT_REMAINS_OPEN: No UET Phi space-response state, base-Phi amplitude, Ding material equivalence, raw correlator payload, or physical UET Kubo promotion is available.

DEPENDENCY_UNLOCKED: External standard-physics transport-input lane only.

STATUS: PASS_SCOPED_SOURCE_LOCKED_EXTERNAL_GREEN_KUBO_INPUT.

WHAT_CHANGED: Added the bounded source package and audit. The record is explicitly external comparator/input evidence, not UET derivation or alpha calibration.

EQUATION_OR_MAPPING: kappa_i(tau) = V/(k_B*T^2) * integral [<J_i(s)J_i(0)>/<J_i(0)J_i(0)>] ds; source rows are 7.9 +/- 0.9 W m^-1 K^-1 for c-axis and 1435 +/- 153 W m^-1 K^-1 for basal plane at 300 K.

VERIFICATION: Audit checks pass; source_payload_sha256=e33f0750db2f5bf16fc24a2cd8e84437f17cd77a3dfba3a5a9e63a2074f930c8; no fit or holdout access.

CONTROLLING_BLOCKER: UET_space_response_and_base_Phi_mapping_missing.

NEXT_ACTION: Find a source-locked UET space-response/Phi map or keep this record as a comparator.

CLAIM_BOUNDARY: Standard-physics external transport input only; not physical UET Kubo, alpha_Phi_K, Ding C_src, or Full Topic 13 closure.

EVIDENCE: package e3282c72a48883b25fc5dcb248ff840cbe7de08a3be2057bf01754c245ca472f; audit 13b2b2c677d2d4d0e1035df99b9b6ae40619040caa976f71baf1d406bb25b208; verifier da42657918ef109ad4130e7fa579c534d3016cfe8b7457d8f14a38d66a78f1f0; full gate 192bf678aa95ccdfcde21e14a476362066b9b2f8b57994ec964da3ca9dd14e8e.

## T13-164 - Ding supplementary content boundary

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE / PARTIAL.

WHAT_IS_ACTUALLY_CLOSED: Page-level content review and hash identity for MOESM1, MOESM2, and MOESM3. The reviewed equations preserve C_src(T) = sum_mu c_mu(T) and Delta_Tq = Delta_u_ph / C_src as source notation only; no numeric mode sum is emitted.

WHAT_REMAINS_OPEN: Numeric Ding C_src, accepted independent reproduction, dimensional base-Phi map, independent alpha_Phi_K, and physical EOS/transport/KMS/entropy closure.

DEPENDENCY_UNLOCKED: Public supplementary content boundary only.

STATUS: PASS_SCOPED_DING_SUPPLEMENTARY_CONTENT_BOUNDARY_NO_NUMERIC_PAYLOAD.

WHAT_CHANGED: Added a source-content review package with page locators, PDF size/hash identity, an audit verifier, and full-gate projection. This is not a derivation or calibration artifact.

EQUATION_OR_MAPPING: C_src(T) = sum_mu c_mu(T); Delta_Tq = Delta_u_ph / C_src; y_TTG = Delta_Tq(t) / Delta_Tq(0); Delta_Tq = alpha_Phi_K * Delta_Phi remains open.

VERIFICATION: All source-content checks pass; the three PDF hashes match the archived files; no figure digitization, fit, threshold change, or holdout access occurred.

CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing.

NEXT_ACTION: Acquire an authorized numeric package or accepted same-regime PBTE reproduction with uncertainty and convergence; do not promote PDF equations or figures to numeric C_src.

CLAIM_BOUNDARY: Source-content boundary only; not numeric C_src, alpha calibration, SI prediction, physical transport, external validation, or Full Topic 13 closure.

EVIDENCE: docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_supplementary_content_review_package.json; docs/core/artifacts/t13_ding_supplementary_content_review_audit.json; docs/scripts/audit/audit_topic13_ding_supplementary_content_review.py.

## Dynamical-Stability Diagnostic Addendum

These formulas diagnose the declared normalized evolution and do not alter the thermal bridge.

| formula_id | relation | units | derivation_class | observable | verification_status | controlling_blocker | claim_boundary |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-CHAOS-TANGENT` | `delta_dot_X=D F[X]delta_X`, `X=(C,Phi,Pi)` | normalized tangent state per normalized time | exact discrete Jacobian action | perturbation growth | tangent JVP and method controls pass | state-dependent sources require an explicit JVP | `R_gen` and `R_obs` are excluded; no new physical law |
| `T13-CHAOS-LAMBDA` | `lambda_i=lim_T log(s_i)/T` | inverse normalized time | standard diagnostic | Lyapunov spectrum and conditional `1/lambda_max` | Fourier/Cattaneo and matter-space pilot pass | SI time/state metric remains open | no physical predictability claim |
| `T13-CHAOS-RESOLUTION` | `lambda_res=max(delta_dt,delta_dx,2 SE_block,delta_method)` | inverse normalized time | preregistered gate | sign-resolved regime class | tangent/shadow and ledger gates pass | accepted open/KMS input missing | chaos candidate is not external validation |
