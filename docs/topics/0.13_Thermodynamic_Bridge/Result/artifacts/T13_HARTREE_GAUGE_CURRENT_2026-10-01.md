# Source-complete rest-frame Hartree current response

MAJOR_RESULT_CLOSURE: `T13_FIXED_PHI_HARTREE_SOURCE_COMPLETE_CURRENT` is `CLOSED_FOR_LANE` in `t13.candidate.fixed_phi_hartree_ms_finite_potential_v1` under a declared vacuum-source contact convention. The full research Goal remains active.

WHAT_IS_ACTUALLY_CLOSED: Actual mixed covariance/source and four-component rest-frame current loops, source-covariance and mean-field reoptimization, seagull and UV surface contacts, nonzero-Q Ward transversality, and an independent uniform-density thermodynamic-envelope check.

WHAT_REMAINS_OPEN: Real-axis spectrum and controlled IR/truncation error, full nonuniform covariant regulator/RG/action matching, joint Phi and material/source/detector admission, normal component, heat current, microscopic SK/KMS/collision transport and independent measurement.

DEPENDENCY_UNLOCKED: Same-candidate spectral/joint-state research only. No change to physical funding G1/G2, recorded Core composition, Full Topic13 or Gravity gates.

STATUS: `PASS_REST_FRAME_HARTREE_SOURCE_CURRENT`; [JSON](t13_hartree_gauge_current.json), SHA-256 `b74428070c559faa3c7caa7ab8efd0258f9f692073b7e736c62a8d44bc8ac971`.

WHAT_CHANGED: Added current-source verifier and independent tests, using the previous trial renormalized inputs and stationary witnesses unchanged. The ultraviolet surface correction is derived before Ward testing, not adjusted to make a residual vanish.

EQUATION_OR_MAPPING:

## 1. Source ontology and kinetic vertices

Canonical varphi=(v,0), s=v^2, u=lambda/Z^2 and M=diag(a+mu^2,b+mu^2) retain the preceding conventions. UET Phi is fixed, not varphi or a gauge field. C is still a collective coordinate; R_gen remains derived and R_obs stays outside physical dynamics.

Let J=[[0,-1],[1,0]], D_alpha=partial_alpha+A_alpha J, and K=-D^2+M. A is a **nondynamical source** for the existing O(2) Noether current; this introduces neither a new UET state nor a physical gauge particle. The source normalization is the chosen O(2) representation, not a C-to-charge identity. Background A_0=i mu, A_i=0 reproduces the preceding Euclidean internal matrix.

For internal P=(nu,k), external Q_E=(omega,q), the forward and reverse kinetic insertions are

```text
V_alpha(P+Q,P)=-i(2P_alpha+Q_alpha)J+2 Abar_alpha I.
delta^2 K/(delta A_alpha delta A_beta)=2 delta_alpha_beta I.
i Q_E dot V=K(P+Q)J-JK(P)-[M,J].
```

The classical seagull is s delta_alpha_beta. The loop seagull is Tr(I_cov) delta_alpha_beta. Omitting either source contact is not an acceptable current-current response.

## 2. Actual mixed and current loops

Use the predecessor's internal propagators, without setting the internal b to zero. With E_c the three symmetric orthonormal covariance matrices:

```text
Y_calpha=-T sum_n integral_k Tr[E_c G(P+Q) V_alpha G(P)].
Ybar_alphac=-T sum_n integral_k Tr[V_alpha G(P+Q) E_c G(P)].
N_alphabeta=-T/2 sum_n integral_k Tr[V_alpha G(P+Q) V_beta G(P)].
```

The reverse insertion is computed by its own matrix ordering, not assumed to be Y transpose. For x=i nu and z=i omega, V_0=-(2x+z)J+2i mu I. Spatial vertices are linear in momentum. After pole decomposition, the full vacuum-plus-thermal moments are

```text
N(p)=sign(p)*(n(abs(p))+1/2).
S0=-[N(p)-N(ell)]/(z+p-ell).
S1=p*S0-N(ell).
S2=p^2*S0-(p+ell-z)*N(ell).
```

At coincident static poles use the Bose divided difference, not a width. Polynomial division gives an extra sum of 1 in S2, but it cancels after summing residues because sum_p R_p=0; it is not silently dropped from a nonzero contact. Direct matrix Matsubara sums independently test these moments. Azimuthal integration gives two identical transverse components; this is a homogeneous isotropic rest-frame tensor, not arbitrary-flow covariance.

## 3. Vacuum source contact and the UV boundary

The current loop plus seagull has a source F_A^2 logarithm in addition to the previously matched mass/quartic terms. Its finite convention must be declared. The independent four-dimensional equal-mass vacuum reference is

```text
Pi_ref=(Q_E^2 I-Q_E Q_E^T)*c_ref.
c_ref=-integral_0^1 dx (1-2x)^2 log[(M0^2+x(1-x)Q_E^2)/Qren^2]/(16 pi^2).
```

Subtract the reference **current bubble and seagull together**, integrate their difference, then add this 4D reference. A frequency-first spatial integral still has an integration-by-parts surface. At large k,

```text
k^3 Tr[integral(dnu/2pi) G]=k^2-Tr(M)/4+O(k^-2).
surface_3D=-[Tr(M)-2 M0^2]/(24 pi^2).
```

The covariant total-derivative convention removes that residual by adding the opposite spatial contact, with no temporal counterpart. Its coefficient depends only on the analytically derived mass trace, not q, temperature, fitting or measured Ward residuals. Boundary convergence, independent 4D vacuum, auxiliary-mass independence and momentum-routing checks test the prescription. Without this correction Ward residuals remain about 1.5e-4 and 6.1e-4 at q=.08; this is a retained negative control, not a threshold change.

At Qren=1 choose the finite F_A^2 coefficient to be zero **as a subtraction convention**, not a microscopic/material input. Scale variation adds `(Q_E^2 I-Q_E Q_E^T) log(Qren'/Qren)/(24 pi^2)`. A compensating source contact is needed; this calculation does not establish full UET RG matching or authorize changing the action's physical coefficients.

## 4. Reoptimized response and Ward checks

For the same K_H=diag(4u,2u,2u), L=K_H W and J_F(Q) calculated previously:

```text
deltaI=(I-J_F K_H)^-1*(J_F L deltavarphi+Y deltaA).
Gamma_phiA=T_phiA+L^T*(I-J_F K_H)^-1*Y/2.
Gamma_Aphi=T_Aphi+Ybar*(I-K_H J_F)^-1*L/2.
Gamma_AA=s I+loop_AA+Ybar*K_H*(I-J_F K_H)^-1*Y/2.
Pi=Gamma_AA-Gamma_Aphi*Gamma_phiphi^-1*Gamma_phiA.
```

Here T_phiA,alpha=-i Q_E,alpha Jv+2 Abar_alpha v, with T_Aphi(Q)=T_phiA(-Q)^T. The last line reoptimizes the mean field as well as the covariance; the internal propagator is not the physical response. The already derived bare/finite identity `[K_b^-1-J_b]^-1=[K_H^-1-J_F]^-1` now uses computed Y and N, not arbitrary matrix probes.

Inversion and Ward checks on this grid do not establish global collective-pole stability, well-posedness or an error bound on the Hartree truncation. Those remain part of spectral and approximation admission, not consequences of transversality.

With i Q_E=(z,iq,0,0), directly test Gamma_phiA iQ=Gamma_phiphi Jv, Gamma_AA iQ=Gamma_Aphi Jv and Pi iQ=iQ^T Pi=0. No transverse projector is applied to the numerical tensor. The covariance check independently uses `Y iQ=-[J,I_cov]_basis-J_F[M,J]_basis`.

At uniform static Q the Goldstone field direction is singular, so do not invent a pseudoinverse. The density source decouples from that direction; eliminate only the radial field and compare the resulting density susceptibility with `-d^2 Fbar/dmu^2` at fixed physical action mass, re-solving the stationary background. The current stiffness at uniform spatial source is an equilibrium candidate quantity, not yet a complete two-fluid constitutive coefficient.

VERIFICATION: Matrix sums, independent 4D vacuum, boundary asymptotics, routing/reference/grid refinement, bare/finite source replay, Ward/reality, action-vertex differences, derivative refinement, units and source-read allowlists. Maximum Ward residual on the declared grid is 2.17e-9; source density matches the potential derivative to relative 1.95e-8 or better. These are numerical discrepancies, not physical uncertainties. At mu=1.05/1.20 the derived fixed-Phi susceptibilities are 2.37144091/3.22737211 and uniform stiffnesses 0.11823723/0.45404297, in canonical E^2 units.

CONTROLLING_BLOCKER: `real_axis_regulator_joint_Phi_material_and_transport_matching_not_closed`.

NEXT_ACTION: Derive real-axis/spectral and controlled-error treatment, then full regulator/action and joint-Phi/material admission. Preserve the computed current and failed predecessor branches; no repeated current-generation wave without a new question.

CLAIM_BOUNDARY: One fixed-Phi Hartree candidate's rest-frame source/current Hessian in an explicit vacuum contact convention. Not physical heat flux, Kubo damping, complete microscopic SK/KMS, full covariant/RG construction, He-II/graphite validation or global UET closure. No parameter fit, clipping, artificial phase mass/filter, causal-threshold change or numeric holdout read; prior Xie context exposure remains REVIEW_REQUIRED.

## Method Context

The distinction between internal self-consistent propagators and external source vertices follows the established [van Hees-Knoll external-effective-action method](https://arxiv.org/pdf/hep-ph/0203008), sections II-III. Regulator symmetry/translation obligations remain, as discussed by [Fejos](https://arxiv.org/pdf/1410.1337). These references are method provenance, not evidence of UET novelty; their 2PI Phi-functional is not UET Phi. The explicit rest-frame loops, surface and independent comparisons above are the local candidate calculation.
