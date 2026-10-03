# Source-responsive finite-q/frequency Hartree field operator

MAJOR_RESULT_CLOSURE: `T13_FIXED_PHI_HARTREE_EXTERNAL_FIELD_RESPONSE` is `CLOSED_FOR_LANE` in `t13.candidate.fixed_phi_hartree_ms_finite_potential_v1`, under its declared zero-momentum subtraction. This does not close the physical response or the entire research Goal.

WHAT_IS_ACTUALLY_CLOSED: An actual three-channel vacuum-plus-thermal bubble, covariance response equation and external Cartesian-field inverse are computed. Absolute loop subtraction agrees with subtraction anchored to the previous finite tadpoles. Static radial curvature recovers the reoptimized potential; transverse curvature vanishes without changing the nonzero internal mass. Finite-q upper-half-plane frequency values are not merely arbitrary matrix probes.

WHAT_REMAINS_OPEN: Gauge-current vertices and contacts, real-axis spectrum and controlled IR/truncation matching, full covariant regulator/RG/action input, joint Phi/global state, independent material/source/detector admission, normal component, microscopic SK/KMS and transport.

DEPENDENCY_UNLOCKED: Same-candidate gauge-current and spectral work only. No Core-composition rewrite, physical funding G1/G2, full Topic13 or Gravity unlock.

STATUS: `PASS_SUBTRACTED_HARTREE_EXTERNAL_FIELD_RESPONSE`; [JSON](t13_hartree_external_response.json).

WHAT_CHANGED: Added an external-response verifier, eighteen tests and this derivation. Uses the two previous stationary witnesses and their declared trial renormalized coefficients, not a new fit or massless internal replacement.

EQUATION_OR_MAPPING:

## 1. Full covariance and source derivative

Let varphi=(v,0), s=v^2, u=lambda/Z^2 and M=diag(a+mu^2,b+mu^2). All fields here are the existing O(2) Cartesian fields, **not UET Phi**. Phi is held fixed at its preceding value. The 2PI functional in method references is not UET Phi either. C stays a collective coordinate; R_gen is not a state or propagator.

Use symmetric orthonormal matrices E0=I/sqrt(2), E1=diag(1,-1)/sqrt(2), E2=[[0,1],[1,0]]/sqrt(2). The full symmetric covariance response includes its offdiagonal E2 channel; it cannot be replaced by only the two diagonal gap equations.

```text
K=diag(4u,2u,2u).
W=sqrt(2s)*[[1,0],[1,0],[0,1]]; L=K*W.
deltaM=L*deltavarphi+K*deltaI; deltaI=J_F(Q)*deltaM.
Gamma_external(Q)=G_internal^-1(Q)+L^T*J_F(Q)*(I-K*J_F(Q))^-1*L/2.
G_internal^-1(Q)=[[q^2+a-z^2,2i*mu*z],[-2i*mu*z,q^2+b-z^2]].
```

These follow by differentiating the invariant Hartree gap with respect to the mean field and re-solving its covariance response. They do not arise by identifying internal propagators with external observables. The inverse exists on the calculated grid; this does not establish its global pole structure or stability for all Q.

## 2. Same-counterterm source equation

The homogeneous field identity from the predecessor extends algebraically to `E_field=(M-mu^2*I)*varphi-2u*s*varphi`. Its derivative gives

```text
V(Q)=[K^-1-J_F(Q)]^-1.
Gamma_external=G_internal^-1-diag(6us,2us)+W^T*V(Q)*W/2.
```

Since L=KW and W^T*K*W/2=diag(6us,2us), this equals the previous formula. For the same invariant bare kernel K_b and `J_b=J_F+D*I`, `K_b^-1-J_b=K^-1-J_F`; the source response is counterterm-independent in this declared decomposition. Checks now insert computed bubbles, not arbitrary complex matrices. This does not by itself construct a full regulator at nonuniform superflow or admit the action's RG/material coefficients.

## 3. Actual vacuum and thermal loop

For Q=(z,q), the covariance kernel is the Matsubara convolution `J_ab(Q)=-T*sum_n integral_k Tr[Ea*G(nu+omega,k+q)*Eb*G(nu,k)]`, analytically continued for Im(z)>0. Four internal poles come from the predecessor's stable a,b spectrum. The full pole occupation is sign(p)*(n(abs(p))+1/2), so vacuum is retained even at T=0. Coincident static poles use the exact Bose divided-difference limit, not an artificial width.

At large four-momentum, G=I/P^2+O(P^-3). The leading bubble is proportional to `-Tr(Ea*Eb)/P^4=-delta_ab/P^4`; its logarithmic divergence is independent of external Q. After the frequency integral, the leading radial integrand is `-delta_ab/(4k^3)` before the spatial measure. The subtraction therefore uses the same channel-identity logarithm as the tadpole derivative.

The finite scheme is computed in two ways:

```text
J_F(Q)=J_F(0)+integral[J_raw(Q)-J_raw(0)].
J_F(Q)=integral_k[J_raw(Q)+I/(4*(k^2+M0^2)^(3/2))]
       +I*log(M0^2/Qren^2)/(16pi^2).
```

Qren is the predecessor's renormalization reference, not frequency Q or an SI scale. The first uses its finite tadpole derivatives. The second directly integrates the full loop with an auxiliary mass subtraction. Neither has a physical UV cutoff. Compact momentum coordinates integrate to infinity; angular averaging removes odd routing terms. Symmetric k+/-q/2 and one-sided k,k+q routes agree for the convergent difference. This establishes the tested rest-frame prescription, not an arbitrary curved/superflow regulator proof.

At Q=0 the diagonal block is a basis rotation of partial(I_sigma,I_pi)/partial(a,b); the E2 entry is `(I_sigma-I_pi)/(a-b)`, from rotating the same covariance. Absolute loop integration independently recovers all entries. Consequently the external angular mass cancels internal b through covariance response. No b=0 constraint is imposed, and this is not a proof that the earlier physical IR composite continuum disappears.

An independent T=mu=0 equal-mass four-dimensional reference is

```text
J_F(Q)=I/(16pi^2)*[log(m^2/Qren^2)
                  +integral_0^1 dx log(1+x*(1-x)*(q^2-z^2)/m^2)].
```

All log arguments are dimensionless. Unit contracts: T,mu,q,z,v,Qren,M0 have E; s,a,b,M,Gamma have E^2; J_F,K,u are dimensionless; W,L have E. Rescaling all energies and both reference masses leaves J_F invariant. Fixed-Phi potential normalization may depend on m(Phi) and is still retained for future joint dynamics.

## 4. Verification and boundary

Preregistered grids: q=.02,.08,.16 for static response; q=.08 at z=.15+.1i and first Matsubara frequency; radial/angular orders (64,32),(96,48),(144,72). Thresholds are point-frequency absolute 1e-7, quadrature/routing 1e-5, static radial relative 2e-5 and Ward/source algebra absolute 1e-9. These do not replace the original causal leakage threshold 1e-6.

VERIFICATION: Eighteen tests cover orthonormal tensor channels, pole reconstruction, degenerate unmixed limit, nonzero vacuum, independent matrix frequency sums, four-dimensional vacuum reference, absolute versus difference subtraction, routing, small static q, independently differentiated source vertices, static potential/Ward, actual-bubble counterterms, retarded reality/parity, units, invalid-domain refusal, evidence hashes and declared artifact reads. Maximum matrix-frequency disagreement is 2.14e-13; absolute-subtraction disagreement 4.29e-10; static radial relative discrepancy 2.39e-10; static Ward residual 3.65e-13. These numerical discrepancies are not physical error bars or a truncation estimate.

Artifact SHA-256: `5078cc2b3c8a8d679542046aa41992f0263b93665297111d4a7864baa96eae36`.

[van Hees and Knoll](https://arxiv.org/pdf/hep-ph/0203008), III, gives established external-effective-action/Bethe-Salpeter method context; [Fejos](https://arxiv.org/abs/1410.1337) retains symmetry-preserving regulator obligations. This is a reconstructed standard-method application, not evidence of UET novelty or a material source. No numeric experimental or holdout input is read by this verifier. Prior Xie context exposure remains review-required.

CONTROLLING_BLOCKER: `gauge_current_real_axis_and_regulator_material_matching_not_closed`.

NEXT_ACTION: Couple the same action and counterterms to an explicit gauge/current source, derive its contact/vertex Ward identity, and define the real-axis spectral prescription with controlled error. Then close RG/action, joint Phi and independent material/source/detector admission. Do not rerun this field bubble without a new question.

CLAIM_BOUNDARY: A computed external Cartesian-field response of one fixed-Phi Hartree candidate in an explicit subtraction. Not a temperature trace, physical He-II/graphite prediction, complete gauge-current Ward proof, full covariant/RG match, real-axis spectrum, microscopic KMS/collision transport, finite-cone repair or global UET closure.
