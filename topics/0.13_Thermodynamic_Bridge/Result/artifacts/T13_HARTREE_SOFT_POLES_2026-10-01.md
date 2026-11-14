# Local Landau-sheet pole of the fixed-Phi collisionless response

MAJOR_RESULT_CLOSURE: `T13_FIXED_PHI_HARTREE_LOCAL_LANDAU_POLE` is controlled by the [machine-readable audit](t13_hartree_soft_poles.json), not this note or elapsed research time. It does not complete the full active Goal.

WHAT_IS_ACTUALLY_CLOSED: Local continuation of the same-candidate positive-cut spectral density gives a simple complex phase pole at both unchanged fixed-Phi witnesses. Two root seeds, three quadrature orders, different real radial grids and two complex-tail contours agree. Denominator checks distinguish it from a radial/covariance elimination singularity. Numerical winding is separate from certified zero counting.

WHAT_REMAINS_OPEN: Certified global complex domain and finite-q poles; Hartree truncation and full regulator/RG/action; joint Phi and independent material/source/detector; physical normal/heat/collision/KMS/entropy transport and independent measurement input.

DEPENDENCY_UNLOCKED: Same-candidate validity and joint-Phi research only. No physical, funding R1 or Core promotion. The Core owner's bounded O(2)/He-4 composition is unchanged.

STATUS: Consult `verification_status`, checks and hashes in the audit. The result is local and collisionless, not a measured thermal mode.

The regenerated audit is `PASS_SCOPED_LOCAL_LANDAU_POLE`, `CLOSED_FOR_LANE`,
SHA-256 `20f1f5ec4d44e8778d541e57f8e38573edf661c3f30d0ee45eed8559155c238d`.

WHAT_CHANGED: A separate successor of the [soft-ray kernel](T13_HARTREE_SOFT_COLLECTIVE_2026-10-01.md) derives the discontinuity and solves the complex inverse itself. No assigned width or fitted Lorentzian replaces the original cut. Predecessor scripts/artifacts are preserved.

EQUATION_OR_MAPPING:

## 1. Continue the spectral density, not an arbitrary logarithm branch

Use signed internal pole p_j, residue R_j and velocity w_j=dp_j/dk. In
joint order (three mass insertions, time, longitudinal), n counts
longitudinal insertions. The original radial measure is in W:

```text
W_ab,j(k) = -[N'(p_j)/2] Tr(V_a R_j V_b R_j) k^2/(2*pi^2),
N'(p_j) = -n(E_j)[1+n(E_j)]/T,
A_n(v,w) = (1/2) int_-1^1 dc c^n*w*c/(v-w*c+i0).
```

For real positive v on the cut, the angular discontinuity is

```text
Im A_n(v,w) = -pi*v^(n+1)/(2*abs(w)*w^n), abs(v)<abs(w),
D_ab(v) = sum_j int_{abs(w_j)>v} dk W_ab,j(k)*v^(n+1)/(2*abs(w_j)*w_j^n),
B_ab(v+i0)-B_ab(v-i0) = -2*pi*i*D_ab(v).
```

Mixed time-source matrices are not elementwise-real responses. Their jump
uses the predecessor's time signature S=diag(-1,1,1,1), not `Im` of every
entry. Bubble/mixed/reverse/current jumps are independently checked against
the original angular evaluator at v=.2,.3,.4 for both witnesses. Preserve
the factor-two mass unpacking. Transverse weights use
v/(2*abs(w))-v^3/(2*abs(w)*w^2).

Continuation of the upper retarded function through this positive cut is

```text
B_L(v) = B_principal_lower(v)-2*pi*i*D_analytic(v), Im(v)<0.
```

Static vacuum/seagull/source-contact anchors have no new discontinuity in
this thermal correction. Simply using the principal lower logarithm is
NOT the continuation: that negative control fails to vanish at the pole.

## 2. Complex thresholds follow the same internal dispersion

Continue each unique real root k_branch of w_positive(k)=v. The determinant
and its positive energies are unchanged:

```text
d(k)=(a-b)^2+8*mu^2*(a+b)+16*mu^4+16*mu^2*k^2,
E_high^2=k^2+(a+b)/2+2*mu^2+sqrt(d)/2,
E_low^2=(k^2+a)*(k^2+b)/E_high^2,
w_high,low=k/E_high,low * [1 +/- 4*mu^2/sqrt(d)].
```

Use the branch originating at positive real k, not abs(complex(E)) in the
Bose function. In D_analytic, abs(w_signed) continues as w_positive while
the signed w^n retains its parity. Defining velocity-root residuals are
checked; the lower endpoint is not a tuned radial cutoff. Two paths run
from this complex endpoint to infinity:

```text
k(x)=k_branch+scale*x/(1-x),                         0<x<1,
k_alt(x)=k_branch+scale*x/(1-x)-i*Im(k_branch)*x.
```

The second returns to the real axis at infinity. Original principal loops
still cover real k from zero to infinity; only the analytic density tail
has a complex endpoint. Sampled positive-energy parts, Bose denominators
and path agreement are local checks, NOT an interval-certified exclusion
of every complex-k singularity along a global homotopy.

Lower evaluation is restricted to .1<=Re(v)<=.6, -.025<=Im(v)<0 and positive
T,mu,a,b,s,u at the two declared fixed-Phi witnesses. No negative-cut pole
is independently computed.

## 3. Solve the complex inverse and retain elimination factors

The predecessor's radial-only source Ward map gives

```text
K_phase(v)=-l^T*Gamma_AA_radial(v)*l/s, l=(v,i,0,0),
K_phase(v_pole)=0,
G_phase(q,z) ~ 1/[q^2*K_phase(z/q)]  [conditional soft model].
```

K'_phase is nonzero and agrees under horizontal/vertical differences; the
local inverse residue in v is 1/K'_phase. This is a simple pole, not a zero
of only Re(K). In the soft model z=q*v_pole, the imaginary term scales with
q, not a collisional diffusion q^2 coefficient. Uniform finite-q pole
control/remainder is not established; no material attenuation is emitted.

Retain the Schur denominators to expose false phase poles:

```text
D_cov=det(I-K_cov*J),
D_full_soft=D_cov*Gamma_radial*K_phase.
```

This leading source-equation determinant follows from the block system
(I-K_cov*J,-L; L^T*J/2,D_internal), not a new full UET action or positive
energy functional. Radial/covariance factors are nonzero at the pole;
their winding and boundary moduli are tested separately.

## 4. Bounded numerical winding is not global stability

Preregister counterclockwise rectangles:

```text
upper: Re(v) in [-1.5,1.5], Im(v) in [.002,.5],
local lower: Re(v) in [.12,.58], Im(v) in [-.02,-.0005].
```

Nested 64/128/256/512 samples per edge give winding zero on the upper and
one on the local lower rectangle for both phase/uneliminated numerators.
Denominator windings are zero; finest phase increments are below pi/2.
This is a sampled zeros-minus-poles diagnostic, not a certified exact
count. Between-sample intervals, the excluded upper near-real strip,
other parameters/sheets/ranges and finite-q poles are not covered. No
global candidate or continuum stability theorem follows.

## 5. Units, provenance and research meaning

v,w,1/K'_phase are dimensionless; k,z,T,mu have E; a,b,s have E^2. Bubble
density is dimensionless, mixed density E, current density E^2 and
D_full_soft E^2. Thermal-density energy scaling is independently checked;
this is not full renormalization-scale invariance or SI normalization.

O(2) phase/Cartesian fields are distinct from clamped UET Phi. C remains a
collective coordinate, not charge/mass. R_gen is not a state; R_obs and
nondynamical A are excluded. No empirical rows, fitted width/parameters,
clipping/filter/noise, threshold changes or Core-owner edits enter. The
audit's sole numeric text input is its derived predecessor. Prior Xie
context exposure remains REVIEW_REQUIRED, not pristine-blind eligibility.

VERIFICATION: The JSON contains complete pole/order/seed/path records, original-cut and independently refined upper-integral checks, local Cauchy-Riemann/derivatives, real-boundary approach, denominator/nested winding checks, protected hashes and eleven report fields. A 128-point original unsplit upper reference was insufficient; 256/512 refinement resolves it without relaxing the 1e-9 comparison. Numerical differences are not physical uncertainty or a Hartree remainder.

| mu | Re(v_pole) | Im(v_pole) | last pole refinement | abs(K'_phase) |
| --- | --- | --- | --- | --- |
| 1.05 | .218903931302 | -.006968573129 | 1.40e-16 | 8.887937490 |
| 1.20 | .374230491486 | -.003436526694 | 4.04e-15 | 5.295905189 |

Original-cut disagreement <=1.81e-15 and independently refined upper
integral disagreement <=7.68e-16. Pole grid/contour/second-seed differences
are below 2e-15; local Cauchy-Riemann disagreement <=3.62e-9. The incorrect
principal lower sheet has inverse residual .123883 and .0364155 at these
retarded poles. Finest upper phase increments <=.896 and lower <=.298
radians; denominator moduli stay nonzero. Real-boundary errors decrease
with eta but are finite (.00145 to .00771 at eta=.0005), not set to zero.
Nineteen new pole tests pass. The earlier failed upper-reference test was
resolved by refining the original unsplit integral, not changing tolerance.
The linked Topic13/Core/planning suite passes 215 tests in 319.54 seconds.
Original failures and Core closure/dependency gates keep their protected
hashes; no predecessor code is changed.

CONTROLLING_BLOCKER: `global_domain_truncation_joint_Phi_material_transport_not_closed`.

NEXT_ACTION: Close global-domain/finite-q and approximation/action obligations, then jointly responsive Phi and material/source/heat-current input. Do not regenerate unchanged roots or choose a relaxation time. Full Goal and original portfolio/model dates remain unchanged.

Immediate next question: does the unchanged finite-q retarded operator have
a continued pole approaching this soft root at q=.04,.02,.01? Derive the
finite-q spectral discontinuity/thresholds from actual loops; substitution
of q*v_pole or a selected width is not that calculation. Separate numerical
q/refinement, Hartree approximation and physical uncertainty. Declare a
candidate validity band rather than assume an effective theory valid at
every momentum/coupling. Unresolved continuation is not a global no-go.
This is a next-action specification, not a completed calculation.

CLAIM_BOUNDARY: Local analytically continued collisionless soft pole of a fixed-Phi Hartree candidate. Not certified global stability, finite-q pole control, microscopic collision rate, measured sound, physical Kubo/SK-KMS/heat/entropy, independent validation or Full Topic13/global UET closure.

## Method Context

[Aitchison, Metikas and Lee](https://arxiv.org/pdf/cond-mat/9905008), sections
6-7, discuss thermal Landau response and approximate lower-half-plane poles
in a different BCS model. Their approximate quadratic/Breit-Wigner
replacement and pole values are NOT used here. The candidate-specific
discontinuity and complex threshold calculation above supply this result.
Established methodology does not establish novelty or physical validity.
