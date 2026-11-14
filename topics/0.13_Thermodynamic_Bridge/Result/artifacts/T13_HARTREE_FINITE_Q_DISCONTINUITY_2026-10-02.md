# Fixed-Phi Hartree finite-q local discontinuity

MAJOR_RESULT_CLOSURE: `T13_FIXED_PHI_HARTREE_FINITE_Q_LANDAU_DISCONTINUITY` is `CLOSED_FOR_LANE` at the unchanged two witnesses and declared grid. Full Topic13, the active scientific Goal and R1 acceptance are not closed.

WHAT_IS_ACTUALLY_CLOSED: Exact signed-mode finite-q shell thresholds and the analytic on-shell joint density needed to continue the response through its local positive thermal cut. Real boundary values agree with the original all-channel radial cuts and independent forward angular delta roots. Two sampled complex tail paths agree, and the density approaches the previously accepted soft density as q decreases.

WHAT_REMAINS_OPEN: The actual finite-q principal kernel and pole root, certified global cut/domain/contour statements, Hartree approximation/full-action/regulator control, joint Phi/material/source/detector mapping, independent thermal normalization and heat/collision/KMS/entropy transport. Neither the TTG scale nor the original conserved-C causal gate is repaired here.

DEPENDENCY_UNLOCKED: Finite-q principal-kernel and actual pole research in this same named candidate only. No physical/Core/funding dependency unlock.

STATUS: `PASS_SCOPED_FINITE_Q_DISCONTINUITY`; ten audit checks and sixteen new independent tests passed. The linked Topic13/Core/planning suite passed 232 tests in 312.19 seconds, including the new planning regression. This record does not use a soft pole as a computed finite-q pole.

WHAT_CHANGED: Separate finite-q density verifier, tests and artifact; local topic/formula/spec/planning/log handoffs. No predecessor code/artifact or Core-owner file changed. Exact prior head `9b2e45b6be7f66916390db2c9d81d9cf56233892` has all relevant remote CI checks successful.

EQUATION_OR_MAPPING: The incoming signed pole is p_j(k), z=q*v, and the on-shell outgoing pole is ell=p_j+z. For sign_j=+1/-1, the exact collinear lower endpoint obeys sign_j*[E_j(k+sign_j*q)-E_j(k)]=z. The outgoing inverse shell gives r^2(ell), with analytic Jacobian sign_j*d(r^2)/dell/(2*k*q). Integrate the joint numerator over the full tail from this endpoint to infinity with k^2*dk/(4*pi^2). Its real cut is -pi*D(q,v); the later retarded continuation requires B_principal_lower-2*pi*i*D_analytic(q,v), not principal lower alone.

VERIFICATION: Eighteen real q/v points across both witnesses: q=.04/.02/.01 and v=.2/.3/.4, original full radial orders 48/80. Maximum original integrated-cut discrepancy 5.92e-14. Five forward-shell radial samples per witness additionally check all active channels and the angular Jacobian. Complex density at each prior soft pole is evaluated with orders 64/96/128 and horizontal/return-to-real tails; last quadrature difference <=5.42e-16, path difference <=5.58e-17 and exact endpoint residual <=3.73e-16. These are numerical differences, not Hartree remainder or material uncertainty. Artifact [JSON](t13_hartree_finite_q_discontinuity.json), SHA-256 `829138c4e2b5387fda30f911e45fc6aa1b8c9db668fb36f012cfae82f864639a`.

CONTROLLING_BLOCKER: `finite_q_principal_kernel_and_actual_pole_not_computed`, followed by global domain/approximation/joint-Phi/material/transport obligations.

NEXT_ACTION: Compute the same-candidate finite-q principal kernel on fixed quadrature nodes. Verify lower-sheet source-signature reciprocity independently against direct complex-frequency algebra. Combine it with this density and solve actual poles, retaining radial/covariance elimination factors, Ward checks, seeds, refinement and a separate finite-q/soft-limit difference. Do not repeat the unchanged real-cut grid without an evidence-changing question. Keep scientific freeze 7 October and portfolio review 11 October; methods/measurement-design scope is not Full Topic13 completion.

CLAIM_BOUNDARY: Conditional natural-unit fixed-Phi spectral-density result, not finite-q collective pole, physical sound, collision/Kubo/SK-KMS/heat/entropy, SI thermal scale, external validation, novelty certification or global UET closure. No assigned width, target fitting, clipping/filter/padding or physical threshold change. C is not mass/charge; UET Phi is not the O2 field; R_gen remains a derived trace; A is nondynamical. No new Xie numeric read; earlier context exposure remains `REVIEW_REQUIRED`.

## Derivation Scope

The accepted internal modes and masses are unchanged. For each signed
same-branch cut, outgoing energy conservation implies ell=p_j(k)+z.
For a positive mode its endpoint is E(k+q)-E(k)=z; for a negative mode
it is E(k)-E(k-q)=z. The two endpoint solutions differ by exactly q.
This is not the approximate soft endpoint k_soft-sign*q/2: its finite-q
correction is retained and independently tested.

With branch=+1 for low modes and -1 for high modes,

```text
d(ell) = sqrt((a-b)^2/4 + 4*mu^2*ell^2)
r^2(ell) = ell^2 - (a+b)/2 + branch*d(ell)
d(r^2)/dell = 2*ell*(1 + branch*2*mu^2/d(ell))
k_z = (r^2-k^2)/(2*q)
k_transverse^2 = ((k+q)^2-r^2)*(r^2-(k-q)^2)/(4*q^2)
V = (mass basis, -(2*p+z)*J+2*i*mu*I, -2*i*k_z*J)
g_ab = .5*(N(p)-N(ell))*Tr(V_a*R_out*V_b*R_in)
D_ab = sum_j int_{k_endpoint,j}^infinity
       k^2/(4*pi^2)*g_ab*sign_j*d(r^2)/dell/(2*k*q) dk
```

The transverse channel uses its original derivative numerator, not a
relabelled longitudinal coefficient. Equal vacuum halves cancel exactly;
Bose differences use expm1 without discarding the exponentially small
thermal tail. The complex Jacobian is analytic, not abs(complex derivative),
and occupations use signed positive-energy continuation, not abs(complex p).
Natural-unit dimensions are E for q,k,ell,T,mu; dimensionless for v and
the covariance bubble density; E for mixed density; E^2 for current density.

## Admitted Domain

Complex evaluation is local: .19<=Re(v)<=.45 and -.015<=Im(v)<=0,
q<=.04 in the declared natural-unit witnesses. The admitted numerical
evidence is the recorded q/v grid and prior pole references, not every
point in that strip or an arbitrary material. Runtime refuses pair-threshold
overlap and endpoints not bracketed above q/2. Original all-channel cuts
and forward shell counts independently agree on the real grid; they do
not establish a certified global exclusion of every other cut.

Each signed tail starts at its own complex threshold. Horizontal and
return-to-real paths integrate the whole tail to infinity. Reported positive
energy/Bose-domain samples and path agreement support this local calculation;
they are not a proof that the entire swept complex domain is free of singularities.

The largest mixed-density differences from the soft density decrease:
mu=1.05: 5.19e-4, 2.60e-4, 1.30e-4; mu=1.2: 2.46e-4, 1.23e-4, 6.15e-5.
The current-density differences decrease faster at these witnesses, but
no universal q^2 error bound for the entire matrix is inferred. All are
evaluations at the previous soft poles, not newly found finite-q poles.

## Method Attribution

Thermal branch cuts and non-Markovian response are established methods,
not a novelty claim for UET. [Boyanovsky et al., hep-ph/9802370](https://arxiv.org/abs/hep-ph/9802370)
is method context from a different scalar-QED model; its coefficients,
microscopic damping or model conclusions are not imported into this candidate.
The particular finite-q shell and numerator above are derived and checked
from the repository's unchanged kinetic/source operator.

## Reproduction

Run `Code/03_Research/Research_T13_Hartree_Finite_Q_Discontinuity.py`
from the repository using the verified Python runtime, then
`Code/03_Research/test_t13_hartree_finite_q_discontinuity.py` with pytest.
The only explicit text input of the audit is the derived predecessor JSON;
code/protected hashes are verified separately. No numeric source/holdout,
calibration value, new SI conversion, new state or Core equation is introduced.
