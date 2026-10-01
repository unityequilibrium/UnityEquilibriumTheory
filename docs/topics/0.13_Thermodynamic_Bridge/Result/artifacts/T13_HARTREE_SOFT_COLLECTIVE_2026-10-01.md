# Thermal ray limit and the collective phase question

MAJOR_RESULT_CLOSURE: `T13_FIXED_PHI_HARTREE_COLLISIONLESS_SOFT_PHASE_RESPONSE` is `CLOSED_FOR_LANE`. This is a same-candidate infrared calculation, not a replacement goal or Full Topic13 acceptance.

WHAT_IS_ACTUALLY_CLOSED: The equal-branch thermal ray kernel, its radial-source/phase Ward mapping and independent full finite-q verification. At both witnesses the derived dynamical kernel differs from the static polynomial and has absorption at the reactive zero; the equilibrium ratio does not answer the undamped-mode question.

WHAT_REMAINS_OPEN: Collective complex poles and global validity domain; Hartree truncation, covariant regulator/RG/action input; joint Phi and material/source/detector admission; normal component, heat current, collision transport, SK/KMS/entropy and independent measurement input.

DEPENDENCY_UNLOCKED: No physical or Core unlock. Only same-candidate collective-pole research can use the derived kernel after verification. The Core owner's bounded O(2)/He-4 composition is unchanged.

STATUS: `PASS_SCOPED_COLLISIONLESS_SOFT_RESPONSE`; [audit](t13_hartree_soft_collective.json) SHA-256 `a7e58a3f9dcdefd032d12e8e6d11d626655d0b2614c367374b90bef3cb620fb4`.

WHAT_CHANGED: A separate soft-ray evaluator integrates the original thermal pole derivative and exact retarded angular moments. It retains the stationary witnesses, static contacts and source reoptimization of the [real-axis predecessor](T13_HARTREE_REAL_AXIS_2026-10-01.md). No original evaluator or artifact is overwritten.

EQUATION_OR_MAPPING:

## 1. Why a static susceptibility does not answer the mode question

The same fixed-Phi candidate gives a static source susceptibility chi and spatial stiffness rho. The quantity sqrt(rho/chi) is dimensionless in its natural-unit lane. It is not automatically a physical sound speed: using it assumes that the soft phase kernel is the local polynomial rho*q^2-chi*z^2. At finite T the retarded thermal loop can depend on z/q even as both z and q vanish.

Let p_j(k) be an unchanged signed internal pole, R_j its residue, and

```text
N(p)=sign(p)*[n(abs(p))+1/2],
N'(p)=-n(abs(p))*[1+n(abs(p))]/T,
w_j=dp_j/dk, z=v*q.
```

For the equal incoming/outgoing branch, ell=p+w*c*q+O(q^2). The original Matsubara divided difference then tends to

```text
-(N(p)-N(ell))/(z+p-ell) -> N'(p)*w*c/(v-w*c+i0).
```

At v=0 this is -N'(p); at nonzero v it is different. Unequal branches have their ordinary static limit. N' is zero at T=0, so this correction is thermal, not a new vacuum mass, width or field. Positive unchanged internal masses make the radial thermal integrals finite; they are not interpreted as a physical Goldstone mass or a cure of the earlier massless/composite continuum.

## 2. Exact angular moments, including absorption

Define m_n=1/(n+1) for even n and zero for odd n. With real signed w,

```text
I_0(v,w)=(1/2w)*log[(v+w)/(v-w)]  [retarded branch],
I_n=(v*I_(n-1)-m_(n-1))/w,
A_n(v,w)=v*I_n-m_n, n=0,1,2.
A_n(0,w)=-m_n.
```

For real v strictly within |v|<|w|, Im I_0=-pi/(2|w|); the higher imaginary moments follow from the recurrence. No finite eta is chosen for the output. The exact endpoints |v|=|w| are logarithmic radial integration splits, not removed intervals. For |w/v|<=1/8 use the absolutely convergent identity A_n=sum_(j>=1)(w/v)^j*m_(n+j); 32 terms control arithmetic cancellation, not a physical approximation of the cut. An independent Cauchy-weight integration checks the original angular numerator.

In joint source order (three mass insertions, time, longitudinal), write the longitudinal insertion as c times its base -2ikJ, where J is the existing O(2) rotation. The time insertion at leading q is -2pJ+2i*mu*I. If n counts longitudinal insertions in a matrix element, the correction to the joint loop is

```text
delta B_ab = -1/2 sum_j int_0^infinity dk*k^2/(2*pi^2)
             * N'(p_j)*Tr[V_a R_j V_b R_j]
             * [A_n(v,w_j)-A_n(0,w_j)].
```

The transverse entry uses the corresponding A_0-A_2 angular average. Joint mass entries are unpacked with the predecessor's factor two. Vacuum/source seagulls and the surviving frequency-moment contact remain in the static anchor; there is no new or fitted contact in the thermal difference. The radial domain is the entire zero-to-infinity interval, with coordinate splits at the velocity roots. No clipping, cutoff, filter or cone padding is used.

## 3. The phase inverse comes from the radial-only source Hessian

Use the same covariance Bethe-Salpeter and mean-field equations. First eliminate the radial mean field only:

```text
Gamma_AA_radial = Gamma_AA-Gamma_A_radial*Gamma_radial_radial^-1*Gamma_radial_A,
Gamma_phase = Gamma_pi_pi-Gamma_pi_radial*Gamma_radial_radial^-1*Gamma_radial_pi.
```

The source Ward identities with Q=(z,iq,0,0) give

```text
s*Gamma_phase = -Q^T*Gamma_AA_radial*Q,
K_phase(v)=lim_(q->0) Gamma_phase(q,vq)/q^2
          = -l^T*Gamma_AA_radial(v)*l/s, l=(v,i,0,0).
```

This is a transpose in the declared Euclidean-source convention, not a Hermitian-conjugate contraction. Do not insert the fully on-shell current Pi here: eliminating the phase as well makes its Ward contraction zero and loses the collective inverse. No uniform phase pseudoinverse, imposed zero mass or Ward projection is used.

K_phase(0)=rho/s. Replacing K_phase(v) by (rho-chi*v^2)/s discards the derived thermal ray contribution. The full finite-q phase Schur complement and its independent radial-current contraction are checked against this limit at q=.04,.02,.01 and v=.1,.3,.6,1.2 at both previous witnesses.

## 4. A reactive zero is not an undamped pole

The declared bracket v in (.1,.6) is used to solve Re K_phase(v)=0, not to fit a target or choose a candidate. If Im K_phase remains nonzero, that real-frequency point is not a zero of the complex inverse and must not be called an undamped collective mode. The numerical record includes the imaginary part, quadrature refinement and an independent finite-q inverse at the reactive zero.

This absorption is collisionless thermal phase-space response. No collisional relaxation rate, physical sound velocity, attenuation length, heat conductivity or entropy-production law is emitted. A complex collective pole requires a controlled continuation through the cut; replacing the cut by an assigned width is not that calculation. A positive or negative reactive coefficient alone is not a global stability test.

## 5. Units, ontology and source scope

v,w,A_n and K_phase are dimensionless; p,k,q,z,T,mu,A have E; s,a,b have E^2; N' has E^-1; R has E^-1. The mass bubble has no units, mixed loops have E and the source Hessian has E^2. The canonical O(2) field varphi is not UET Phi. C is the original collective coordinate, not this phase coefficient or a canonical charge; R_gen is still a derived trace, and R_obs/A are not physical state variables. No SI alpha_Phi_K or detector scale follows from this limit.

The evaluator reads the committed real-axis artifact, not empirical or holdout rows. Prior Xie context exposure remains REVIEW_REQUIRED. Original failures, physical funding gates and the full-topic acceptance matrix are unchanged.

VERIFICATION: Fourteen artifact checks pass. Independent angular Cauchy disagreement is below 6e-15; last soft-loop refinement <=1.29e-9; scaled field/current Ward disagreement <=5.89e-5; finite-q phase quadrature refinement <=3.22e-5. The full finite-q results approach the derived limit on all eight rays, but their remaining corrections at q=.01 range from 1.10e-5 to 6.01e-3: these are not the quadrature error or a certified Hartree remainder. Unit, domain, signed-velocity, cold/static and evidence-lineage tests are linked in the verifier package. No physical uncertainty is assigned.

| mu | static sqrt(rho/chi), not a mode speed | ray at Re inverse=0 | Im phase coefficient there | last root quadrature difference |
| --- | --- | --- | --- | --- |
| 1.05 | 0.22329087 | 0.21937248 | -0.06212778 | 1.71e-11 |
| 1.20 | 0.37508005 | 0.37428752 | -0.01820733 | 9.87e-12 |

All entries are natural-unit diagnostics. The real-frequency inverse is not zero because its imaginary part is nonzero. Full finite-q evaluation at the respective ray has residual correction 3.92e-4 and 7.35e-5 at q=.01; this is retained, not clipped or tuned away. The full linked Topic13/Core/planning suite passed 195 tests in 319.54 seconds, including seventeen new soft-response tests. The first audit's final protected-path indexing typo was corrected and the entire audit rerun; no scientific threshold changed.

CONTROLLING_BLOCKER: `collective_pole_domain_truncation_joint_Phi_material_transport_not_closed`.

NEXT_ACTION: Analyze collective complex poles and stability within an explicit candidate validity domain using this nonlocal kernel; close approximation/regulator/action and joint-Phi/material/heat-current obligations separately. Do not substitute the static susceptibility ratio or another rerun of the old ten points.

CLAIM_BOUNDARY: Conditional fixed-Phi Hartree collisionless infrared response only. Not hydrodynamic first/second sound, material He-II/graphite prediction, physical collision/Kubo/SK-KMS/entropy transport, global stability or Full Topic13/global UET closure.

## Method Context

[Aitchison, Metikas and Lee](https://arxiv.org/pdf/cond-mat/9905008), introduction and sections 6-7, discuss nonlocal thermal Landau terms and the distinction between a static derivative expansion and a dynamical phase response in a different BCS model. [Boyanovsky et al.](https://arxiv.org/pdf/hep-ph/9802370), section IV, give established pair/scattering branch-cut methodology in scalar QED. These are method context, not imported material coefficients, proof of this candidate or evidence of novelty. The local same-action residue and source calculations are what the verifier tests.
