# Actual Finite-q Landau-sheet Phase Poles - 2026-10-02

MAJOR_RESULT_CLOSURE: `T13_FIXED_PHI_HARTREE_FINITE_Q_LANDAU_POLES` is `CLOSED_FOR_LANE` in `t13.candidate.fixed_phi_hartree_ms_finite_potential_v1`. This closes the actual finite-q principal-kernel/pole question on six declared points, not Full Topic13, R1, or the active research Goal.

WHAT_IS_ACTUALLY_CLOSED: Fixed-grid principal loops with complex Cauchy subtraction; independently checked lower-sheet source reciprocity and vacuum reference; actual complex phase zeros at both unchanged fixed-Phi witnesses and q=.04/.02/.01. Roots refine, survive alternative seeds/grids/tail paths, have nonzero local derivatives and approach the accepted soft poles without substituting them.

WHAT_REMAINS_OPEN: Certified global complex domain/stability; Hartree approximation remainder and full regulator/RG/action matching; joint UET Phi stationarity; independently admitted material/state/source/detector and thermal scale; physical collision/Kubo/SK-KMS/heat/entropy transport. The original conserved-C causal branch and failed Gaussian/tree baselines remain unchanged.

DEPENDENCY_UNLOCKED: Same-candidate validity-domain, approximation/action and joint-Phi research only. No physical, funding, Gravity or full-Core dependency is unlocked; the separate Core-owner composition is neither overwritten nor promoted.

STATUS: `PASS_SCOPED_FINITE_Q_POLES`.

WHAT_CHANGED: Separate [verifier](../../Code/03_Research/Research_T13_Hartree_Finite_Q_Poles.py), 22 tests and [artifact](t13_hartree_finite_q_poles.json). The [density-only predecessor](T13_HARTREE_FINITE_Q_DISCONTINUITY_2026-10-02.md) retains its original flags; this successor supplies the missing principal kernel and actual root. No older code, input, mass, coupling, subtraction/contact convention or Core-owner file was changed.

EQUATION_OR_MAPPING:

```text
B_L(q,z) = B_principal_lower(q,z) - 2*pi*i*D(q,z/q)
Gamma_phase = Gamma_pp - Gamma_pr*Gamma_rp/Gamma_rr
Gamma_phase(q,z_pole) = 0
det_full = det(I-K_cov*J)*det(Gamma_field)
```

These are the same source-responsive covariance/field equations as the predecessor. The O(2) phase variable is not clamped UET Phi. q,z,k,T,mu have natural units E; v=z/q is dimensionless; bubble, mixed and current loops have units 1, E and E^2 respectively; Gamma_field has E^2; det_full has E^4 and det_full/q^2 has E^2. The block-rescaling test checks this algebra, not full-loop RG invariance or an SI map.

For each fixed radial node and outgoing signed shell, retain the original source-frequency polynomial and use the analytic identity

```text
integral_lo^hi g(ell,z)/(p+z-ell) dell
 = integral_lo^hi [g(ell,z)-g(p+z,z)]/(p+z-ell) dell
   + g(p+z,z)*log((p+z-lo)/(p+z-hi)).
```

The same-mode thermal numerator is subtracted at the complex Cauchy point, not a real fitted surrogate. Other smooth-channel reference points remain fixed real midpoints. Retain all polynomial contacts, covariance reoptimization, vacuum subtraction and the derived spatial surface contact. Nodes are fixed before the root search with split rays (.19,.2,.3,.4,.45); they do not track a trial root. The radial map covers 0<=k<infinity.

The time insertion has an anti-Hermitian part whereas real-energy internal residues are Hermitian. With S=diag(-1,1,1,1), checked source reciprocity is

```text
B_lower = B_upper(z*)^dagger
Y_lower = reverse_upper(z*)^dagger * S
reverse_lower = S * Y_upper(z*)^dagger
Pi_lower = S * Pi_upper(z*)^dagger * S.
```

Unsplit angular Matsubara moments at both signs of Im(z), and direct lower Cauchy integration, check this independently. Ordinary conjugation without S fails the negative control. No predecessor upper-half-plane validator was bypassed or patched.

The equal-mass vacuum reference uses centered shell coordinates eta=ell-m, h=k*q/midE and A=p+z-m, avoiding large-k^2 subtraction in longitudinal vertices. Its moments are

```text
I_n(A,h) = 2*h^(n+1)/A * sum_{j>=0, n+j even} (h/A)^j/(n+j+1).
```

For mass_ref=1 and local q<=.04, |v|<=sqrt(.45^2+.015^2), h<=q and |A|>=2-q*|v| imply |h/A|<.0203. Sixteen parity terms are retained, with runtime guard |h/A|<.05. For r=|h/A| and j0=n mod 2, the omitted tail is bounded by

```text
2*|h|^(n+1)/|A| * r^(j0+32)
  / [(n+j0+33)*(1-r^2)].
```

This bounds only the vacuum angular-series remainder, not full radial quadrature, Hartree truncation or continuum physics. The analytic reference agrees with the unchanged vacuum angular method at k=.02,.2,1,20,150.

VERIFICATION: Fifteen artifact checks pass; the 22 new tests pass in 16.43 seconds. Pole orders are (radial,angular)=(64,24),(96,32),(128,40); alternative rays are (.21,.25,.35,.43). The old soft pole is only a starting seed; two independent seeds (.2-.01i,.4-.005i) yield the same roots. The lower-sheet strip is .19<=Re(v)<=.45, -.015<=Im(v)<=0, not a global contour theorem.

| mu | q | finest v=z_pole/q | distance to accepted soft pole |
| --- | --- | --- | --- |
| 1.05 | .04 | .2196361937093543-.006925360530202967i | 7.3353634010e-4 |
| 1.05 | .02 | .21908731503236417-.006957708916569762i | 1.8370526328e-4 |
| 1.05 | .01 | .2189496581410602-.006965845740257696i | 4.5808104967e-5 |
| 1.20 | .04 | .3744673022848205-.00342832238578826i | 2.3695287489e-4 |
| 1.20 | .02 | .3742896767725501-.0034344714956961583i | 5.9220958587e-5 |
| 1.20 | .01 | .3742450877980379-.0034360101793141093i | 1.4605447636e-5 |

Maximum final pole refinement is 3.284e-7; seed disagreement 9.423e-13; alternate-grid disagreement 8.527e-10. Maximum root residual is 2.521e-12 against 1e-8; alternate density-tail residual also passes. Final original upper-reference loop discrepancy <=5.608e-7; maximum phase/current Ward discrepancy 1.614e-5 against inherited 1e-3; local Cauchy-Riemann discrepancy <=1.675e-6. Minimum derivative modulus 5.2938. Radial/covariance factors and minimum singular values remain nonzero; the uneliminated determinant also vanishes. The wrong principal-lower sheet does not give the retarded pole. Decreasing pole differences do not establish uniform q^2 error or a Hartree remainder; these numerical differences are not physical uncertainty.

The full linked Topic13/Core/planning regression subsequently passes 256 tests
in 342.61 seconds, including the two new planning-boundary tests. This is
internal verification of the declared scope, not external replication.

Artifact SHA-256: `7a16d7203b2347984d3a6f5dd8e4025730b049bce3e474b52ff103a8cfbb380a`.
Density predecessor SHA-256: `829138c4e2b5387fda30f911e45fc6aa1b8c9db668fb36f012cfae82f864639a`.
The Windows runtime reports longdouble_bits=64 and clongdouble_itemsize=16; extended precision is not assumed. Protected Core/dependency and prior failure hashes agree. The audit reads only the derived predecessor, not empirical/holdout rows.

CONTROLLING_BLOCKER: `global_domain_Hartree_remainder_joint_Phi_material_transport_not_closed`.

NEXT_ACTION: Specify the validity domain and regulator/action/approximation obligations of this candidate before joint Phi or material transport admission. Account for the potential normalization that can depend on m(Phi); do not drop it in joint variations. Separate missing proof/input from numerical convergence. No unchanged root-grid rerun. Portfolio preparation uses this bounded methods result and a measurement-design aim; science freeze remains 7 October, review 11 October, and the full Goal remains active.

CLAIM_BOUNDARY: Local fixed-Phi collisionless collective poles, not microscopic particle lifetime, material sound, heat coefficient, SI alpha, external validation, novelty certification or global UET closure. No fit/width/mass repair, clipping/filter/cone padding/threshold change, new numeric Xie read or Core-owner edit. Prior Xie exposure remains `REVIEW_REQUIRED`, not pristine blinding. A momentum-independent Hartree internal self-energy does not supply particle lifetimes; collective cut absorption is different ([primary Hartree context](https://arxiv.org/pdf/1410.1337)). Regulator/UV-domain questions must be derived in this prescription, not imported from a different NLO scheme ([primary comparison context](https://arxiv.org/pdf/1404.4426)). These sources are methodological context, not UET coefficients, thermal calibration or proof of this result.
