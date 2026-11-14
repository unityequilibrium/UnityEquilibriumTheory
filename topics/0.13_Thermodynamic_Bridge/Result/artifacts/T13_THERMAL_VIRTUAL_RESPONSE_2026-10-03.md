# Virtual tree response closes the static matching gap without fitted contact

MAJOR_RESULT_CLOSURE: `T13_THERMAL_VIRTUAL_SOURCE_STATIC_COMPLETION_AND_DYNAMIC_COVARIANCE`, `CLOSED_FOR_LANE` in a named acoustic-thermal-insertion extension. Full Topic13/R1/Goal remain open.

WHAT_IS_ACTUALLY_CLOSED: The origin of the predecessor's acoustic cut-only static gap: mixed virtual tree propagation and the action-derived contact/background term supply the missing response. An explicit q=0 complex-frequency source correction also agrees independently with real-time covariance evolution.

WHAT_REMAINS_OPEN: Finite-q source response and population relaxation, vacuum/full interacting thermal matching, approximation control and independent material/source/readout/temperature/uncertainty; physical normal/heat/Kubo/SK-KMS.

DEPENDENCY_UNLOCKED: Finite-q source and population-relaxation research only. No physical/Core/Gravity/owner-composition admission.

STATUS: `PASS_SCOPED_THERMAL_VIRTUAL_RESPONSE`. [Artifact](t13_thermal_virtual_response.json), SHA-256 `a05474ba7a9fdf0005df0c67f2d4a2ff1dbc5432016a1988ccd22730e70e70b0`.

WHAT_CHANGED: Separate [calculation](../../Code/03_Research/Research_T13_Thermal_Virtual_Response.py), tests and [two-entry registry](../../Data/03_Research/t13_thermal_virtual_response_registry.json). Parent action and [static-curvature predecessor](T13_THERMAL_SOURCE_CURVATURE_2026-10-03.md) are unchanged. New branch `t13.candidate.acoustic_thermal_insertion_tree_virtual_response_v1` explicitly declares an acoustic thermal population with virtual classical tree propagation. It is not retroactive all-mode quantum admission of the old phase-EFT branch.

EQUATION_OR_MAPPING:

## 1. Prescription and exact tree spectral resolution

Use the same rest-frame quadratic parent, cubic and quartic potential
derivatives, with Fourier convention exp(-izt):

```text
D(z,p)=V0+p^2 K-z^2 K+z L
K=diag(1,1,epsilon Z_Phi)
L_sigma,phase=2i mu; L_phase,sigma=-2i mu
G(z,p)=D(z,p)^-1
G=sum_j [u_j u_j^dag/(E_j-z)+u_j^* u_j^T/(E_j+z)]/(2E_j)
-u_j^dag D_E(E_j)u_j=2E_j
```

The heavy energies/polarizations are computed from a quadratic companion
eigenproblem and checked against the direct inverse. They have no assigned
thermal occupations or vacuum determinant here. They are virtual response
of the same classical tree parent to the acoustic thermal covariance.
This new prescription is explicit; neither the old acoustic-only cuts nor
its historical static mismatch is overwritten or reclassified.

Fields are radial/phase/Phi fluctuations and their velocities for a
covariance diagnostic, not C, UET Pi, R_gen or R_obs. h remains the original
external action source, not heat injection or a calibrated detector.

## 2. Static completion follows from virtual pair and number transitions

Along the fixed-mu stationary family let A=D_h and A2=D_hh, as derived in
the predecessor. For acoustic a and a nonacoustic tree mode j define
N_aj=u_a^dag A u_j and P_aj=u_a^T A u_j. At fixed momentum:

```text
pair/n=abs(P_aa)^2/(4E_a^3)
mixed_j/n=[abs(P_aj)^2/(E_a+E_j)+abs(N_aj)^2/(E_j-E_a)]/(2E_a E_j)
contact/n=u_a^dag A2 u_a/(2E_a)
pair/n+sum_j mixed_j/n-contact/n=-E_a,hh
chi_static=integral [n(1+n) E_a,h^2/T+pair+mixed-contact]
```

All terms are independently generated from potential derivatives and tree
pole polarizations. The static target is used only as a verification, not
as an input to define or adjust contact. The identity is checked against
gyroscopic eigenvalue variation and recomputed pressure finite differences.
Virtual modes remain relevant even when their thermal populations are
omitted: a thermally occupied acoustic mode can couple virtually to them.
An exponentially small heavy occupation is not a license to discard this
response. Missing heavy occupation is an explicit approximation obligation.

At divisor256 the integrated static decomposition is:

| mu | mixed lower | mixed upper | contact (subtracted) | completed chi |
| --- | --- | --- | --- | --- |
| 1.05 | 2.60445e-14 | 1.74689e-12 | -2.16756e-14 | 4.90685914e-11 |
| 1.2 | 8.08787e-11 | 6.42613e-12 | -5.88386e-11 | 2.20087753e-10 |

Population/pair terms remain those of the predecessor. Including the
displayed virtual/contact terms resolves its 3.65%/66.4% cut-only matching
gap on these witnesses. Four integrated target discrepancies are below
1.2e-15. These are normalized candidate susceptibilities, not SI material
data or a total physical error bound.

## 3. Contact and background shift come from the action, not a residual

For one acoustic thermal insertion per momentum, with n omitted below:

```text
f_i=u_a^dag T_i u_a/(2E_a)
delta_x=-V0_active^-1 f_active           [phase gauge fixed]
S_ij=u_a^dag Q_ij u_a/(2E_a)
M_ij=S_ij+T_ijk delta_x_k
d(z)=D(z,0)^-1 e_Phi
delta_chi(z,0)=integral n d(-z)^T [B(z)-M] d(z)
B_ij(z)=[u_a^dag T_i G(E_a+z)T_j u_a
         +u_a^dag T_j G(E_a-z)T_i u_a]/(2E_a)
```

delta_x is the thermal one-loop background shift, not a fitted source
offset. The term T delta_x changes the tree source response at the same
loop order; S is the quartic seagull. The scalar transpose d(-z)^T is
required for analytic frequency dependence, not a modulus square at a
complex frequency. D(-z)^T=D(z), B(-z)^T=B(z), and source response obeys
the real-field conjugation condition. No contact is obtained from the
predecessor's residual, and no pole width is assigned. Non-real frequencies
are evaluation points of the response, not phenomenological damping.

## 4. Independent real-time covariance calculation

Let y=(x,dot_x), B_gyro=iL and

```text
dot_y=A_tree y
A_tree=[[0,1],[-K^-1(V0+p^2 K),-K^-1 B_gyro]]
w_a=(u_a,-iE_a u_a)
Cov_th/n=Re(w_a w_a^dag)/E_a
delta_A_j=[[0,0],[-K^-1 T_j,0]]
(-iz-L_A)delta_Cov_j=delta_A_j Cov+Cov delta_A_j^T
L_A Cov=A_tree Cov+Cov A_tree^T
B_ij=-Tr(T_i delta_Cov_j,xx)/2
```

The second method solves a 36-component linear covariance equation. It
does not use the spectral bubble or static E_hh. The initial covariance
has only the declared acoustic Bose thermal difference. Real-time
population relaxation/collisions are absent; this is not a transport model.
Full matrix and externally dressed scalar responses agree with the direct
propagator/spectral calculation. Maximum scalar discrepancy is 1.461e-9
against the preregistered 1e-7 independent-covariance gate.

## 5. The two static limits are physically different ensembles

At q=0 and z nonzero, the phase equation implies
2mu d_sigma-iz d_phase=0: homogeneous source response conserves charge.
Its tree zero-frequency limit is

```text
chi_q0,dynamic=1/[V_PhiPhi-V_sigmaPhi^2/(V_sigmasigma+4mu^2)]
chi_fixed_mu,static=1/[V_PhiPhi-V_sigmaPhi^2/V_sigmasigma]
```

The respective values are19.9110 versus20.2186 at mu1.05 and18.3788 versus
18.6158 at mu1.2. They are not equal (normalized differences1.54%/1.29%).
Grand-canonical static population variance therefore cannot simply be
added as a homogeneous dynamical response. Finite-q limits and a declared
population-relaxation/transport prescription are the next obligations.
This distinguishes an ensemble/limit issue from failed static matching.

## 6. Retained first failure and finite numerical scope

[First failure](t13_thermal_virtual_response_first_failure.json), SHA-256
`1b67bdac27a4a1aa6f52f9fa06164fc6545ac92cab2b4e1fc83ab17c064e0e0c`,
failed only a contact-projection comparison at mu1.05,p.005. Direct
binary64 contraction of large seagull/background terms lost relative
precision (2.385e-9 against the fixed1e-9 identity gate). The same action
contact is now evaluated independently with 50-digit arithmetic, rebuilding
the 2x2 Hessian and T/Q from the declared input values. No parameter, step,
grid or gate changes. Raw error remains in the accepted artifact; the
precise projection discrepancy is below1.3e-12. This does not turn
binary64 polarizations or action inputs into independently precise data.
First-failure code/test hashes are historical, not current rerun certificates.

VERIFICATION: Seven checks; mu1.05/1.2, p.005/.02/.04, T=c*dispersion_scale/256 and /512, orders24/48/96, tails32/40 and z=.02i/.05i/.1i/.03+.02i fixed before first audit. Independent modes/inverse/covariance, pressure FD, source charge/reality/reciprocity, static ensemble, zero-T/decoupling/coordinate/invalid-domain and protected-hash/runtime-read controls. Dynamic finest quadrature discrepancy6.158e-10 and finite-tail difference6.700e-11. Finite grids/tails do not establish a global analytic, approximation or physical uncertainty bound. Final linked test count is recorded in UPDATE_LOG.

CONTROLLING_BLOCKER: `finite_q_source_transport_and_complete_interacting_thermal_matching_open`.

NEXT_ACTION: Extend the explicit covariance/source prescription to finite q and verify the equilibrium versus collisionless limit, without inventing relaxation or transport inputs. Account for vacuum/full interacting thermal consistency and approximation control; in parallel require independent material/source/detector/scale/uncertainty for measurement. Preserve7/11 October and full Goal/R1-R5 criteria.

CLAIM_BOUNDARY: Named one-acoustic thermal-insertion Gaussian response only. Not full interacting EOS/sunset/vacuum, heavy quantum-Phi admission, global causal/retarded stability, physical heat/Kubo/SK-KMS/calibration, original conserved-C repair or Full Topic13/UET/Core promotion. No holdout numeric read; prior exposure remains REVIEW_REQUIRED. No fitting, clipping/padding/filter, threshold/ontology/owner changes. [Andersen's review](https://arxiv.org/abs/cond-mat/0305138) supplies context on distinct Bose-gas thermal approximations and perturbative control, not this candidate's material coefficients or external validation.
