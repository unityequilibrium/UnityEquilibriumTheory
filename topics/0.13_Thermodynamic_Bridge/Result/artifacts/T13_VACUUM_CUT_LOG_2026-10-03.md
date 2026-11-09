# Vacuum phase cut, logarithmic response and the local matching boundary

MAJOR_RESULT_CLOSURE: `T13_VACUUM_PHASE_CUT_LOG_AND_LOCAL_MATCHING_BOUNDARY`, `CLOSED_FOR_LANE`. Not Full Topic13, R1-R5 or scientific Goal completion.

WHAT_IS_ACTUALLY_CLOSED: The formal leading-order linear-phase two-phonon vacuum cut, its real logarithmic equivalence class and independent four-subtracted dispersion reconstruction. A constructive local family has the same cut but different real response. The restricted degree-six fixed-convention matching matrix has rank four; leading on-shell samples have rank one, not four independently observable physical coefficients.

WHAT_REMAINS_OPEN: State-dependent microscopic Wilson and source/contact matching, internal-curvature near-shell finite real part, complete thermal sunset/mixed pressure and source/entropy derivatives, finite-T normal/heat/Kubo/SK-KMS/entropy transport, independent material/source/readout/scale and practical measurement feasibility.

DEPENDENCY_UNLOCKED: Local Wilson and thermal-sunset research only. No physical/Core/Gravity unlock; Core-owner composition and the original failed conserved-C branch are unchanged.

STATUS: `PASS_SCOPED_VACUUM_CUT_LOG`. [Artifact](t13_vacuum_cut_log.json) SHA-256 `449b4df1741ebd0b4c3fa5f69cda1f97b6f014ebd5cfc603e97352bed2e41e17`.

WHAT_CHANGED: Separate [verifier](../../Code/03_Research/Research_T13_Vacuum_Cut_Log.py), focused tests and [topic-local registry](../../Data/03_Research/t13_vacuum_cut_log_registry.json). The [interaction predecessor](T13_LOW_T_INTERACTIONS_2026-10-02.md) and tree-EFT evidence remain byte-identical. No coefficient is fitted and no damping width is assigned.

EQUATION_OR_MAPPING:

## 1. Declared scope and exact cut

Use the existing tree-matched classical-Phi phase EFT, not the old Hartree
prescription. Canonical phase is not UET Pi; its self-energy Sigma is not Phi.
K=cq, z=omega^2 and acoustic s_a=z-K^2 are not the radial amplitude squared.
Sigma has E^2, g_t/g_s E^-2, z/K^2 E^2 and the renormalization scale mu_R E.
C, R_gen and R_obs are absent from this phase-only fluctuation state.

For barred=g_s/c^2, G=g_t+barred, the earlier canonical cubic vertex on two
massless internal lines can be written

```text
V = 6 G omega E_p E_r - 2 barred omega s_a
E_p=(omega+K cos(theta))/2; E_r=(omega-K cos(theta))/2
a=(3G/2-2 barred)z+2 barred K^2; b=3G K^2/2
F(z,K^2)=z[a^2-2ab/3+b^2/5]
Im Sigma_R=-sign(omega) F(z,K^2)/(32pi c^3), z>K^2
Im Sigma_R=0, z<K^2
```

The factor follows from the identical-boson cut, -1/4 times the two-body
phase-space integral of V^2. Its angular measure is dcos(theta)/(16pi c^3).
An independent original-spatial-vertex integral uses
p in [(omega/c-q)/2,(omega/c+q)/2], r=omega/c-p and the actual angular root,
without clipping. It agrees for both states, three q and three frequency
ratios. Energy conservation holds at each root. Threshold value itself is
not assigned: a strictly linear internal dispersion needs a near-shell
prescription. This is not a finite-cone proof for the original conserved-C.

An independently expanded expression is

```text
F=z[(6G^2/5)z^2+(3G^2/5-4G barred)z s_a
    +(9G^2/20-2G barred+4 barred^2)s_a^2]
```

## 2. Real logarithm and independent dispersion reconstruction

Analytic continuation z=(omega+i0)^2 gives the nonlocal part

```text
Sigma_nonlocal=F(z,K^2)/(32pi^2 c^3) * log((K^2-z)/mu_R^2)
Sigma_R(-omega,q)=conjugate(Sigma_R(omega,q))
```

The upper-half-frequency limit reproduces the negative positive-frequency
cut. For reference z0=-K^2, subtract the Taylor polynomial of degree three:

```text
Sigma_4sub(z)=(z-z0)^4/pi * integral from K^2 to infinity
 Im Sigma(sqrt(nu),q) / [(nu-z0)^4 (nu-z)] dnu
```

Independent complex Cauchy quadrature agrees with the analytic logarithm
minus its four Taylor terms; the largest relative disagreement is
4.016e-12. Four subtractions suffice for the generic cubic-in-z spectral
polynomial; special coupling cancellations can lower the required count.
Integration to infinity defines this formal subtracted linear loop, not
physical validity of the low-energy EFT to infinite energy. UV completion
and finite subtraction/matching inputs are not measured by this integral.

Changing mu_R by a factor f changes only a local polynomial,
Delta Sigma_nonlocal=-2 log(f) F/(32pi^2 c^3), compensated by the opposite
counterterm. This checks running, not the finite Wilson coefficient.

## 3. Connection to the earlier decay and its limit

Approach the cut from z>K^2. The optical-theorem pole rate
gamma=-Im Sigma/(2omega) tends to the earlier convex-branch leading rate,

```text
gamma/q^5 = 3 G^2 c^2/(160pi)
Re Delta omega_linear = (gamma/q^5)/pi * q^5
                       * log(abs(K^2-z)/mu_R^2) near threshold
```

| mu E | gamma/q^5 E^-4 | coefficient of q^5 log(argument) E^-4 |
| --- | --- | --- |
| 1.05 | .0108344696153 | .00344871879010 |
| 1.20 | .00131422468447 | .000418330709734 |

The last column is the coefficient of the displayed dimensionless log,
not a universal coefficient of log(q). How K^2-z approaches zero matters.
Putting only an external curved pole into the linear internal loop does
not compute internal-curvature resummation or its finite on-shell constant.
The dilute-Bose control recovers pole width 3q^5/(640pi m n), half the
occupation decay; its coefficients are not imported into UET.

## 4. What matching must supply

One allowed order-reduced low-q local example is Sigma_local=ell6 q^6.
The declared ell6=(-.5,0,.5) E^-4 family has unchanged imaginary part and
different conditional real shifts ell6 q^6/(2cq), with positive sampled
frequency squared and correction below the preregistered low-q margin.
It is not a microscopic/global-stability proof or an added physical state.

At this derivative order in a fixed canonical/source convention, consider

```text
Sigma6=a6 z^3+b6 z^2 K^2+c6 z K^4+d6 K^6
```

At fixed nonzero K, four distinct ratios z/K^2=(-1,0,.5,2) produce a
Vandermonde-type matrix of rank four, determinant 6.75 and condition number
30.17. Synthetic algebraic reconstruction error is 2.776e-17; this is not
a calibration result. The leading on-shell line z=K^2 sees only
a6+b6+c6+d6 (rank one). For example z^2(z-K^2) vanishes there but changes
off-shell response. Some such directions are equation-of-motion/field-
redefinition redundant; source/contact terms must transform consistently.
Thus neither four independent physical parameters nor four minimum lab
measurements are inferred. This fixes an explicit mathematical matching
interface while leaving physical source/operator admission open.

The lower-order kinetic/sound-speed and tree dispersive inputs are held in
the declared tree convention here. Full-parent vacuum matching can also
renormalize them and their source/current vertices. The rank statement for
degree six neither fixes those lower-order conditions nor proves that the
whole microscopic response has only four missing coefficients.

Required next input is a declared microscopic parent/renormalization and
source-matching prescription, or independent matched response information
in a specified state. An arbitrary subtraction scheme can define a
conditional model but cannot manufacture a material prediction. Separate
the on-shell physical combination from convention-dependent off-shell
terms before designing measurements. Missing input is not global no-go.

VERIFICATION: Nine artifact checks and focused tests; original grids/gates retained, with new matching ratios declared before their computation. Independent original-vertex phase space, expanded polynomial, four-subtracted Cauchy, scale running, upper-half-frequency/reality, known Bose limit, Phi-coordinate invariance, free/spacelike/invalid-input and runtime file-allowlist checks. Hash/protected evidence checked; linked test counts are recorded in UPDATE_LOG. No experimental data, holdout or model trial was used.

CONTROLLING_BLOCKER: `state_dependent_local_Wilson_and_thermal_sunset_matching_open`.

NEXT_ACTION: Declare same-parent source/renormalization matching conditions and compute internal-curvature real response plus thermal sunset/mixed pressure with source/entropy consistency. Quantify the remaining approximation terms before uncertainty or heat-transport claims. Independently assess material/readout feasibility. Preserve 7 October science freeze, 11 October portfolio review and the five later review dates.

CLAIM_BOUNDARY: Formal LO linear-phase cut/log modulo local matching and a restricted information boundary only. Not full quantum EOS, a controlled total remainder, physical normal/heat/Kubo/SK-KMS/entropy transport, independent Kelvin alpha, material/TTG prediction, external validation or Full Topic13/Core. Original conserved-C remains blocked at 1e-6; no fit, assigned width, mass repair, clipping/filter/padding, threshold/ontology change or new numeric Xie access. Prior exposure stays REVIEW_REQUIRED, owner composition unchanged and all physical/full-Core/global flags false.

Primary method controls: [Escobedo and Manuel, Sections III-V](https://arxiv.org/html/1004.2567v2) discuss loop/near-shell EFT sensitivity; [Derezinski, Li and Napiorkowski](https://www.fuw.edu.pl/~derezins/damping_publ.pdf) distinguish Beliaev pole rate and UV real-part issues. Their nonrelativistic coefficients are not used as matching input for this relativistic-X candidate.
