# Graphite preparation versus driven-force admission

Scope: same graphite coherent-shear candidate and existing conservative matter/response equations. This is a conditional preparation/observer design, NOT a physical fit, new Core interaction, or replacement of the driven mechanical kernel by a free-ringdown formula. Reuse [source distinction](T13_MECHANICAL_SOURCE_BRIDGE_2026-10-18.md) and [comparator result](T13_ACTION_DISCRIMINATION_2026-10-18.md); their identities remain recorded in the calculation contract.

## Source evidence (not an independent calibration)

[Gerbig et al., NJP 27 (2025) 053004](https://doi.org/10.1088/1367-2630/adcfbc), [author-hosted published PDF](https://www.uni-kassel.de/fb10/index.php?eID=dumpFile&f=41427&t=f&token=ea89c4f5512c8a20950e373eae706724032d0134), sections 2-4, equations 1-6 and data statement: nine-layer graphite, optical preparation and electron-diffraction readout; a directional carrier-mediated force and displacement-to-intensity map are specified. Force scale, lifetime, orientation, period and damping are obtained together from the response fit. Processing removes an estimated Debye-Waller contribution and includes temporal convolution. Numeric records are author-requested, not a public reusable package in this source. Thus there IS a physical source/readout model, but its fitted force is not independent input for a second test on the same records.

The published PDF resolves corrupted HTML uncertainty digits; no HTML number is imported as a quantitative bound. Equation 6's extracted exponential inside the integral has an ambiguous time-prime; we do not implement or silently repair it. The statement of a finite carrier memory is sufficient for the admission question. [Mishina et al., PRB 62 (2000) 2908](https://doi.org/10.1103/PhysRevB.62.2908), abstract, attributes generation primarily to real excitation with saturation. Consequently an instantaneous purely virtual Raman force is NOT adopted merely from the shear symmetry label.

Two exact-title/identifier repository-locator queries plus a mode-specific query returned no eligible same-state numeric packet. This bounded search is not proof of global absence. No author contact, raw download, curve digitization, or other material substitution was performed.

## Decision between the two interfaces

| Route | What can be reused | What is not established | Decision |
| --- | --- | --- | --- |
| Driven pump-to-conjugate-force | Directional source and measurement architecture in cited experiment | Independent force history, finite-mode UET correspondence, same-state coefficients and joint errors | Not admitted; importing a globally fitted force as input is circular |
| Prefix preparation, then forecast | Existing action accepts nonzero initial data; diffraction can locally resolve both shear coordinates | Complete coupled state, force-tail and damping bounds, observer calibration and eligible split records | Preferred conditional design: no new optical bulk term needed, but physical prerequisites still mandatory |

Preference is based on fewer source-mechanism assumptions, not a claim of currently available data or lower measured error. It forecasts a new transient observable using the SAME dynamical model; it does not produce the old four-frequency kernel or its pole invariants. If retaining that exact observable is essential, the driven route remains the only route of these two that targets it.

## Frozen contract before algebra/code controls

FORMAL question: can a prefix-only preparation contract provide a mathematically non-tautological later-state test, and which state/observer conditions are necessary? H is the existing homogeneous coupled action with a declared collinear matter motion, fixed coefficients and physical map. Comparator is its ordinary-scalar forward-equivalent model; a fit cannot identify UET uniquely. No source or damping term is added.

All measurements would be dimensionless processed Bragg intensities; material displacement conversion and the field chart remain conditional. Coefficients and mapping must be fixed independently or from an explicitly calibration-only prefix before the forecast cutoff. A prefix used to estimate initial conditions is calibration, NOT independent validation. All already viewed figures remain exposed. A future suffix is at most prospectively reserved for a locked analysis, not retroactively blind.

Outcome rule: propagate the entire admissible prefix-state/parameter/error set through the frozen coupled equations and observer. Reject only if no member explains the reserved suffix within the joint error set. Overlap is non-rejection, not proof; an unbounded prerequisite is inconclusive. No actual records, parameter values, cutoff time, physical threshold or numerical integration are selected here. The finite check cap is exact observer/state identities plus explicit failure counterexamples, no parameter search.

## New observer consequence: three intensities give two coordinates plus a closure check

Within the paper's small-displacement linear readout only, write y_i=(I_CP,i-1)/(2*pi), x=sqrt(3)*P_a and z=P_b. Then

```text
y = M (x,z),    M = [[1,1],[0,-2],[-1,1]].
x = (y_1-y_3)/2,
z = (y_1-2*y_2+y_3)/6,
y_1+y_2+y_3 = 0.
```

These are a left inverse and a redundant closure channel, not a nonlinear UET prediction. The orthogonal unweighted residual is (sum(y)/3)*(1,1,1); use a covariance-weighted version only when covariance is supplied. For joint componentwise errors |e_i|<=eta, the exact linear worst-case bounds are |delta x|<=eta, |delta z|<=2*eta/3; no independence assumption is needed. A departure in the closure channel rejects the readout/processing approximation, not automatically the matter equation. The full structure factor and thermal/background effects must bound the approximation before scoring harmonics.

The inversion reconstructs temporally blurred coordinates if each channel shares a linear convolution kernel. It does NOT undo that blur or recover instantaneous velocity. Different kernels, fitted baseline division and nonlinear intensity corrections need a joint operator, not three independent gain adjustments. This operator audit improves the observation part but cannot create missing source/state evidence.

## New preparation consequence: displacement and velocity alone are not the coupled state

Even on a one-direction invariant subspace, the state is (q,q_dot,d,d_dot), where d=Phi-Phi_star. For fixed g=epsilon*h !=0 and no residual matter force,

```text
Z*q_ddot + (m2 + lambda*q^2 - g*d)*q = 0.
d = (m2 + lambda*q^2 + Z*q_ddot/q)/g,
d_dot = (2*lambda*q*q_dot + Z*(q_jerk*q-q_ddot*q_dot)/q^2)/g.
```

The latter two follow by algebra/differentiation and require q!=0. Natural units are q,d:E; time:E^-1; q_ddot:E^3; q_jerk:E^4; g:E. Consequently d:E and d_dot:E^2. With only q and q_dot known, two different d values give different accelerations g*q*delta_d/Z for nonzero q: the two-coordinate initial state is not closed. Even matching d leaves d_dot undetermined by the first acceleration; its contribution appears in the next derivative. At a zero crossing these quotient formulas fail; using an adjacent nonzero prefix interval needs its own observability/error analysis. They are not a global no-observability theorem.

This is a legitimate possible MODEL-CONDITIONED state estimator from a prefix, not an independent measurement of Phi. It can support a later forecast only if parameters were frozen, the inferred full state set is propagated jointly, and the suffix is not reused in inference. By contrast, inferring a new force at every suffix time from its target trajectory makes that same suffix fit tautological. Known residual force requires its subtraction; unknown force makes the estimator ambiguous. Differentiating noisy blurred intensities three times is not admitted by an exact identity. No such differentiation or inversion of measured traces is performed.

In noncollinear motion the transverse state must also be resolved. Material E2g is not automatically the action's internal O(2); collinearity, kinetic projection and field units remain explicit hypotheses, not consequences of seeing two diffraction channels.

An absolute field scale is NOT intrinsically required by this approach. In a fixed material-coordinate/time chart one can instead write Q_ddot+(A+B*Q^2-U)*Q=0, with identifiable coefficient combinations A,B and effective response U, rather than separately identifying every field constant. Then U=A+B*Q^2+Q_ddot/Q and U_dot=2*B*Q*Q_dot+(Q_jerk*Q-Q_ddot*Q_dot)/Q^2. Forecasting still needs an independently justified evolution equation for U, its coefficient combinations and its initial velocity; eliminating the field name or units does not eliminate the hidden dynamic state. No absolute SI Phi calibration is demanded merely to apply the formal test.

## Source memory and observer memory cannot be reset at an arbitrary cutoff

If a residual acceleration has norm <=B(t), its direct velocity contribution over duration T is bounded by integral(B), and the double-integrated direct displacement contribution by integral((T-s)*B(s)). In the full nonlinear coupled system these are not by themselves total trajectory error bounds: state-dependent amplification also needs a stability/variational bound on the declared domain. A force lifetime fitted from the entire trace is not an independent B(t). Nor does a short pump pulse prove all thermal/carrier effects have vanished. Existing conservative equations cannot silently acquire empirical damping; damping must either be quantitatively negligible over a predeclared window or trigger stop D before implementation.

An electron-pulse response kernel convolves both sides of a cutoff. A Gaussian has nonzero tails, so a finite guard interval is not exact statistical independence. One needs a tail bound and state/output range or a joint forward model; temporal covariance and common time-zero/baseline uncertainties must remain coupled across the split. No cutoff based solely on a quoted central lifetime is chosen.

## Current admission and reopening input

Physical forecast NOT RUN. The source model exists, but the inspected public paper does not supply an eligible independent drive or full prefix-state/error packet. A measured material coordinate is not yet chi; a model-conditioned hidden-state inference does not resolve the missing physical correspondence. Published force/lifetime/damping fits and figures cannot substitute for those inputs. The earlier mass-modulation proof is unchanged.

Minimum reopening packet for the preferred route, all in the SAME state/sample/protocol:

1. Independently justified mode/kinetic chart and fixed coefficient combinations sufficient for this forecast (absolute SI Phi need not be required if eliminated consistently).
2. Signed multichannel time records, baseline/thermal correction history, time-zero, temporal transfer and joint uncertainties; usage/exposure status explicit.
3. Prefix-only admissible FULL coupled state set, measured or model-conditioned with uncertainty; unobserved directions constrained, not set to zero silently.
4. Source-tail, heating, damping and approximation bounds over a usable forecast window, including dynamical amplification and observer cross-window leakage.

Outcome C for the present admission decision: exact missing inputs are above and the two mathematical counterexamples explain why a fitted drive or q,q_dot alone cannot replace them. This is not an instruction to wait for one email or rerun indefinitely. A new dissipative/material interaction would require stop D and separate approval; none is implemented. The ordinary comparator remains forward-equivalent within its admitted action class. No physical UET test or Full Topic13 promotion is claimed.

## Goal completion audit

1. Inventory: source evidence and route table distinguish derived readout, fitted source, conditional material map and missing data/bounds.
2. Compare routes: driven and preparation paths assessed in the same graphite mode; exact old kernel not silently equated to ringdown.
3. Primary-source inspection: published PDF sections/equations and data statement inspected, older generation result cross-checked; bounded locator searches recorded, no archive acquired.
4. Freeze: formal hypothesis, units, comparator, data roles, errors, control cap and decision rules above were fixed before controls; no physical calculation admitted.
5. Execution: only new exact observer/state identities checked. Physical prerequisites fail; no target fit, source reconstruction from suffix, or threshold chosen. Final condition C is a prerequisite result, not theory validation.

## Continued material-side audit: finite-layer kinetic projection

The existing [MP48 residue derivation](../../../core/03_lanes/topic13_support/T13_MP48_INTERLAYER_MODE_RESIDUE.md) already derives the mass-centroid kinetic metric and spectral residue. The [MP48 crystal audit](../../../core/03_lanes/topic13_support/T13_MP48_SHEAR_IRREP.md) establishes the SOURCE bulk Gamma doublet's E2g character. These are not missing or redone here. They do not automatically specify a nine-layer sample or equate its normal coordinate to the UET field. The older shape-only status is superseded by that scoped source-irrep result, not by an unperformed new experiment.

[Tan et al., Nature Materials 11 (2012) 294-300](https://doi.org/10.1038/nmat3245), [author PDF](https://www-g.eng.cam.ac.uk/nms/publications/pdf/nmat3245.pdf), page 3 equations 1-2 and the intervening eigenvector expression, gives a free-ended identical-layer nearest-neighbour shear chain. Its highest branch approaches the bulk shear mode. We use its analytic layer profile and mass metric as a conditional material model, NOT its fitted force constant or Raman spectra as independent data for the heated nine-layer preparation.

Predeclared extension: N=9 target, N=2 exact rigid reference, N=3,4 implementation controls. No force constant, observed frequency or pump/readout record fitted. Compare free-chain eigenvector and matrix independently, check translation removal, and calculate the kinetic residue for a NAMED coordinate. Floating tolerance 1e-12 is code roundoff only, not a physical model error. This extension covers a material-side geometry question, not the missing optical operator or UET identity.

Let each layer have mass per area mu, physical in-plane displacement u_j, and define the highest-mode profile and a coordinate Q by

```text
e_j = cos[(N-1)*(2j-1)*pi/(2N)],  u_j=e_j*a,
r_j = +1/n_A on odd layers, -1/n_B on even layers,
Q = r.u = mean(u_odd)-mean(u_even),
M_Q/area = mu*sum(e_j^2)/(r.e)^2.
```

Here a and Q are lengths; mu is kg/m^2. Their conjugate generalized forces are force/area. The force projected onto Q is f_Q=(e.f)/(r.e), where f_j is force per layer area, because sum(f_j*delta u_j)=f_Q*delta Q. A total sample modal mass requires an illuminated mode/area profile; this formula does not supply one.

The rigid odd/even-group approximation with center-of-mass fixed instead gives M_rigid/area=mu*n_A*n_B/N. Cauchy-Schwarz shows eta=(r.e)^2/(sum(r_j^2)*sum(e_j^2))<=1 and M_Q=M_rigid/eta. Equality requires e proportional to r. The N=2 reference is exactly rigid. For a longer free-ended highest mode, surface amplitudes need not equal interior amplitudes; a named coordinate's pole mass is therefore not automatically the two-group reduced mass. This is a layer-profile/projection correction, not renormalization of Phi.

For an arbitrary drive profile, the highest-mode projection can even vanish while nonzero layer forces excite other modes. Total intensity or total deposited momentum cannot replace e.f. This continues the earlier directional-force distinction; it does not assert that every graphite pump has zero projection. Likewise Q as an odd/even centroid is NOT automatically the relative displacement inferred by the paper's four-atom diffraction ansatz. Before applying the earlier three-channel inverse to a finite-layer mode, project the actual structure factor onto e and compare its observer rows, including layer weighting and stacking. Uniform force f_j=constant has e.f=0 for this optical mode, a useful translation-channel check rather than a proposed pump.

The chain's angular-frequency ratio to its bulk limit is cos(pi/(2N)) on this highest branch. It may diagnose the finite-size model but cannot be retuned to the measured post-pump frequency. A frequency mismatch needs material-state/model errors, not an eigenvector relabeling. No full finite-layer crystal irrep is inferred from the chain alone.

Result interpretation: kinematic material mass/projection is more specified than an arbitrary gain, but a material chain is not the action's field-to-material map. Even an accepted M_Q would not determine source polarization/carrier dynamics, nonlinear coefficients, damping, or Phi correspondence. The next decision is whether the finite-layer diffraction projection admits Q with bounded model error; only then assess independent coefficient/state information. No bulk dataset is silently substituted for the nine-layer experiment.

### Conditional finite-layer observer projection (positive partial bridge)

There is an analytic special case that does not require every layer displacement to be rigidly equal. Assume kinematic basal-plane scattering, identical layer form factors, AB stacking with layer factors F_A and F_B=F_A*exp(-i*phi), no depth/probe weighting and small displacement. Sum displacements within each group; first-order scattering depends only on their centroids. For center-of-mass-fixed Q=u_A-u_B, put t=G.Q. The unperturbed amplitude (dividing out F_A) is S_0=n_A+n_B*exp(-i*phi), and its derivative is S'_0=-i*n_A*n_B*(1-exp(-i*phi))/N. Thus

```text
d(I/I0)/dt = 2*n_A*n_B*sin(phi)/(n_A^2+n_B^2+2*n_A*n_B*cos(phi)).
```

For a first-order phase with cos(phi)=-1/2, the ratio to the balanced-group observer coefficient is exactly n_A*n_B/(n_A^2+n_B^2-n_A*n_B): 20/21 for N=9, and one for equal groups. The direction/sign and actual reciprocal phases must still be verified from the sample geometry; no phase or finite-thickness Ewald correction is declared measured here. This provides an explicit conditional map from a finite-layer centroid coordinate to a linear diffraction signal, not just a missing-item list. Under these assumptions the earlier two-coordinate inverse can be rescaled coherently, while its zero-sum closure remains. This correction does NOT repair unknown thermal division, temporal blur, layer attenuation, dynamical scattering or nonlinear harmonics. Outside these assumptions the full layer-resolved observer is required.

The computed N=9 free-chain centroid pole mass is approximately 2.68033 times the layer mass per area, versus 20/9 for the rigid grouped ansatz (ratio about 1.20615). These are model-coordinate ratios, not measured sample masses, a physical discrepancy significance, or a new Phi calibration. Their effect and the 20/21 conditional readout factor show why a force or displacement gain should not be copied unchanged between conventions.

## Continued observer audit: finite-displacement bounds and false cubic signal

Freeze before numerical controls: retain the preceding equal-layer basal AB kinematic observer and highest free-chain profile. Target N=9; N=2 exact reference; N=3,4 cross-checks. Choose dimensionless t=G.Q in {0,+/-0.001,+/-0.01,+/-0.1} ONLY as mathematical controls, not measured displacements or a physical acceptance window. No sampling of a UET trajectory or target tuning. Aim: bound linear-observer error for arbitrary real t and determine whether nonlinear diffraction alone can generate a cubic harmonic from sinusoidal material motion.

Let b_j=e_j/(r.e), c_j=1 on odd layers and exp(-i*phi) on even layers. With D=|sum(c_j)|^2>0 the full conditional observer is

```text
I(t)=|sum_j c_j exp(-i*t*b_j)|^2/D,
K_n=I^(n)(0)=sum_jk c_j conjugate(c_k)*[-i*(b_j-b_k)]^n/D.
```

This is a real intensity despite the complex representation; each ordered pair has a conjugate partner. All layers move; a common translation multiplies the amplitude by a phase and leaves I unchanged. No linearization or mode-frequency approximation is used in this observer formula, but its kinematic scattering, fixed form-factor and mode-profile assumptions remain unvalidated physically.

Taylor's integral remainder and |c_j|=1 give a GLOBAL linear-error envelope, not merely an asymptotic statement:

```text
|I(t)-1-K_1*t| <= B_2*t^2,
B_2 = sum_jk (b_j-b_k)^2/(2*D)
    = [N*sum(b_j^2)-(sum b_j)^2]/D.
```

Similarly, after including terms through cubic,
`|I(t)-1-K_1*t-K_2*t^2/2-K_3*t^3/6| <= B_4*|t|^4`, where `B_4=sum_jk |b_j-b_k|^4/(24*D)`. Both inequalities follow from bounded derivatives of real exponentials for all real arguments, not finite-grid success. They are conditional OBSERVER bounds only, not total physics/measurement errors. Near an extinct baseline D they can become large; normalizing a zero baseline is invalid and must be refused, not clipped.

If an independently established |G.Q|<=A and allowed intensity omission eta are provided, the sufficient admission condition B_2*A^2<=eta can be checked without fitting the output. No A or eta is assigned from the response being tested. The bound also specifies how a nonlinear deviation from the old three-channel zero-sum closure can be an observer effect rather than a failed dynamical equation. Channel bounds must be propagated jointly through the prior left inverse; temporal transfer and thermal correction errors remain additional.

For a perfectly SINUSOIDAL input coordinate t(s)=A*cos(omega*s), the cubic Taylor term contributes cosine amplitude K_3*A^3/24 at 3*omega and K_3*A^3/8 at omega. Thus a nonzero measured third harmonic can arise in the detector even when the MATERIAL trajectory contains no third harmonic at all. At K_1!=0 the small-amplitude raw ratio tends to K_3/(24*K_1^3), not necessarily zero. This is detector-generated effective cubic response, not an intrinsic quartic UET kernel. The bilayer reference has K_3=-K_1 exactly. No measured graphite cubic coefficient is inferred here.

For the exact observer, the cubic-polynomial third-harmonic amplitude is only the leading term: the amplitude error is bounded conservatively by 2*B_4*A^4 using the above uniform remainder and the cosine Fourier coefficient norm. This avoids claiming an uncomputed harmonic series is exact. If a common temporal response is linear/time-invariant, its frequency transfer multiplies each harmonic, so raw ratios also require the relative transfer at omega and 3*omega; cancellation is not automatic. State-dependent/nonlinear detector response requires its own bounds.

Acceptance consequence: subtract or forward-model this SPECIFIED observer nonlinearity with joint parameter/profile errors before testing a mechanical third-harmonic claim. One cannot simply attribute the observed cubic ratio to UET, nor independently tune one cubic correction per channel. The full intensity forward operator may be preferable to noisy inverse differentiation. Its validity for the actual sample, mode mixture, Ewald/depth weighting and damping/source preparation remains the controlling empirical question.

### Which temporal uncertainties cancel, and which do not

There is a useful cancellation, not a requirement to know every clock offset perfectly. For consistent complex harmonic coefficients of the SAME stationary record, a common time shift multiplies Y_n by exp(-i*n*omega*t0). Hence Y_3/Y_1^3 is invariant to that common shift. Separate channel/run shifts, nonstationary finite windows or timing-dependent preparation are not covered by this identity. A constant detector gain G instead leaves a factor G^-2 in the ratio; it does NOT cancel like the phase.

A common normalized linear temporal kernel has harmonic transfer H(n*omega), so the ratio gains H(3*omega)/H(omega)^3. For a hypothetical Gaussian kernel of standard deviation sigma, H=exp[-omega^2*sigma^2/2]; the multiplier is exp[-3*omega^2*sigma^2], not one. This is an analytic conditional transfer calculation, not an assignment of the experiment's fitted resolution or physical uncertainty. The formulas show exactly which calibration combinations are needed, rather than demanding an absolute clock or assuming every instrument effect cancels. Unknown/non-Gaussian transfer still requires the measured operator or bounds. Frequency-varying transfer and cubic observation therefore remain confounders even after the favorable common-clock cancellation.

### A sufficient local inverse domain, without assuming linearity is exact

For three declared reciprocal in-plane rows g_i, define the unblurred two-coordinate observer F_i(Q)=I_i(g_i.Q). Suppose its baseline Jacobian J0 has smallest singular value s>0 and each channel has the above B2_i. On a convex ball |Q|<=R, |I'_i(g_i.Q)-I'_i(0)|<=2*B2_i*|g_i|*R. Consequently the Jacobian drift has operator norm at most L=2*R*sqrt(sum_i B2_i^2*|g_i|^4). For any two points in that ball, integrate along their joining segment and use the triangle inequality to obtain

```text
|F(Q)-F(P)| >= (s-L)*|Q-P|.
```

If L<s, the full nonlinear observer is injective there and inverse state error is at most output-vector error/(s-L) for admissible paired outputs (or twice the measurement radius when comparing two candidate states in the same error ball). This is a sufficient bound, not a necessary amplitude cutoff or an evaluated physical domain. It gives a constructive route beyond the linear inverse once geometry, R and joint errors are independently supplied. It does not invert temporal blur, identify Phi, or prove a globally unique state over multiple diffraction periods. No hypothetical geometry or amplitude is silently declared to be the actual experiment's.

### Candidate discriminating readout: two reciprocal orders, one material trajectory

A bounded extension can separate geometric detector cubic from a true coordinate third harmonic without assigning either one to UET. Freeze two simultaneous same-direction reciprocal orders G and 2G with verified AB phases +2*pi/3 and -2*pi/3, respectively, identical normalized layer weighting, and corrected/common temporal transfer. Complex conjugation then gives K1_second=-K1_first and K3_second=-K3_first for the SAME normalized profile. This is a proposed geometry to admit, not a claim that an eligible (100)/(200) dataset was acquired.

For a coordinate with only odd fundamental and third components, let B be its signed third cosine amplitude and C=(Q^3)_3/6. The quadratic observer term has no odd harmonics. Through cubic order the two measured third amplitudes obey

```text
Y3_first  = K1*B + K3*C,
Y3_second = -2*K1*B - 8*K3*C,
B = (8*Y3_first + Y3_second)/(6*K1),
C = -(2*Y3_first + Y3_second)/(6*K3).
```

The determinant is -6*K1*K3, nonzero on the inspected conditional N=9 observer. Thus two orders add information that repeating the same detector gain does not. For Q=A*cos(theta)+B*cos(3*theta), C=A^3/24+A^2*B/4+B^3/8; no need to drop mixed cubic terms or suppose B=0. A sinusoidal material trajectory then gives inferred B=0 even though each raw channel has a third harmonic. Other material harmonics, even motion, unequal transfer, background and mode mixture require the full operator rather than this two-component formula.

If both channels retain the SAME unknown linear transfer at 3*omega, the inversion returns H(3*omega)*B and H(3*omega)*C, not their unblurred values. Absolute amplitudes need that transfer calibrated; distinguishing zero/nonzero B requires a nonvanishing-transfer bound and noise accounting. Common transfer alone therefore preserves the algebraic separation, not an unblurred material measurement.

### Continued source-geometry and baseline-processing audit

The [primary article](https://arxiv.org/html/2412.16392v2), equations 1-3 and the figure-3 processing discussion, specifies the four-atom basal basis and division by a scaled reference-peak estimate. The reference peak has zero shear response in the SAME small-displacement approximation, not a stated all-orders symmetry theorem. We now check that source geometry and the consequence of a residual reference response; no actual processing bias is asserted.

Predeclared mathematical extension: dimensionless lattice a=1, direct vectors (1,0),(-1/2,sqrt(3)/2), two atoms per layer from equation 1, basal G_hk=2*pi*(h,(h+2*k)/sqrt(3)). Inspect (100),(010),(-110),(200),(110); N=2 source unit-cell reference and N=9 conditional chain. No lattice constant, physical sample orientation, force, target intensity or correction scale fitted. The basis factors are

```text
F_A=1+exp[-2*pi*i*(h+2*k)/3],
F_B=1+exp[-2*pi*i*(2*h+k)/3].
```

For the three first-order peaks, |F_A|=|F_B| and their ratio is a cube root of unity, verifying the earlier equal-layer phase assumption within this ideal basal geometry. The (100)/(200) pair has conjugate phase ratios and doubled G, so its two-order proposal is geometrically possible in the source model. Depending on axis/sign convention, the first phase is -2*pi/3 rather than +2*pi/3; keep the signed K1 and coordinate convention consistently. Using Q=-a*P for the article's choice of moving B layers, the N=2 rows reproduce its displayed linear coefficients. N=9 carries the previously derived common 20/21 factor under the declared finite-layer observer, not a new empirical normalization. These are model-geometry checks, not acquisition of calibrated peaks.

For (110), F_A=F_B=2 and the relative layer phase is zero. The linear derivative vanishes, but the FULL normalized coherent observer has

```text
I_ref''(0) = -2*[N*sum(b_j^2)-(sum b_j)^2]/N^2 < 0
```

for a nonuniform optical mode. It can therefore contain a quadratic coherent signal when G_ref.Q is nonzero. A special displacement perpendicular to that G is an exception; averaging a symmetry star does not in general annihilate the even quadratic contribution. Small experimental amplitude may make this negligible, but a quantitative bound is needed at cubic-precision targets. No conflict with the article's explicitly first-order approximation is inferred.

Suppose, as a conditional processing model, a normalized numerator is 1+a1*q+a2*q^2/2+a3*q^3/6 and its applied divisor contains an unremoved even component 1+b2*q^2/2. Then the divided linear derivative remains a1, its second derivative is a2-b2, and its third is a3-3*a1*b2. Thus reference normalization can alter the apparent cubic readout even for sinusoidal material motion. This algebra is not a claim that the experiment's fitted thermal scaling equals this simplified divisor; actual scaling, heating, timing and shared correlations must be recorded before using it. A calibrated pipeline may remove or bound the effect.

This matters for the proposed two-order discriminant. If BOTH orders share the same unmodeled divisor b2, the reconstructed B acquires a leading bias -b2*(Q^3)_3/2, despite the pure geometric-cubic cancellation. At the instantaneous cubic expansion level, dividing by D(q) multiplies the material-linear vector by 1/D(q), so this residual lies in the same order-scaling direction as material motion. Two reciprocal orders alone cannot distinguish that shared normalization effect from true third motion. Therefore keep/review the undivided reference and numerator records and forward-model their common correction; simply adding one more processed curve is insufficient.

There is still a usable bounded path: if |D-1|<=rho<1 and |N|<=M independently on the domain, |N/D-N|<=M*rho/(1-rho). The same bound controls joint normalization omission before harmonic/state propagation, without setting reference response to zero. If no finite divisor-away-from-zero and correction bound is available, refuse a physical cubic score. This pinpoints a pipeline prerequisite, not a new action term, a reason to tune a cubic coefficient or a proof that UET/that experiment is wrong.

For the narrower inference using ONLY processed third-amplitude channels with uncalibrated common b2, define C=(Q^3)_3/6 and E=b2*C. Every reciprocal order has the form Y3_i=k1_i*m_i*(B-3*E)+k3_i*m_i^3*C through the retained cubic order. The B and E columns are proportional for ANY number of such channels; (delta B,delta C,delta E)=(3*delta,0,delta) leaves every Y3_i unchanged. More processed third-harmonic peaks alone therefore cannot remove this particular ambiguity. This is not a claim about full time records, independent amplitude/preparation constraints, calibrated reference response, or higher-order full-forward inference. Once b2 is fixed/bounded by justified reference/processing evidence, or an independently informative observable is added, that null direction need not remain. This is why undivided reference/correction evidence takes priority over another processed harmonic curve.

### Positive alternative: shared-divisor invariants from three full traces

The previous null result explicitly discards most of the time-record information. A different sufficient packet is possible: preserve simultaneous normalized FULL traces for (100),(010),(-110) and prove their applied correction is the SAME pointwise nonzero divisor D(t). Then Y_i(t)=F_i(P(t))/D(t) gives R1=Y1/Y2=F1/F2 and R3=Y3/Y2=F3/F2 exactly, regardless of the size or nonlinear content of D. It is not necessary to know that applied divisor's waveform to eliminate it. This is a positive alternative to requiring undivided references in every case, not reversal of the processed-third-only null proof.

Freeze the new audit before controls: same ideal N=9 layer observer, N=2 reference; full-record ratios, no isolated Fourier-amplitude substitution. Mathematical P controls (0,0),(0.0001,-0.0002),(-0.0001,0.0002); arbitrary common divisor controls 1/2,1,2. No observed P, physical noise threshold or target fit. Actual common-processing identity, channel gains, exposure/transfer and numeric records remain unadmitted.

At P=0 the ratio Jacobian rows are the source intensity rows v1-v2 and v3-v2. With f=20/21 for the conditional N=9 centroid chart, these rows are 2*pi*f*(sqrt(3),3) and 2*pi*f*(-sqrt(3),3). Their determinant is 24*pi^2*sqrt(3)*f^2>0. The inverse function theorem consequently gives a local two-coordinate inverse for the FULL nonlinear ratio map, not only its Taylor truncation. No globally unique diffraction inverse or physical inverse radius is claimed. This establishes that the shared applied divisor need not destroy state information when all three simultaneous traces are retained.

For the LINEAR observer only, let x=sqrt(3)*P_a,z=P_b. If intensities are 1+2*pi*f*M(x,z), the reconstruction can eliminate even a large arbitrary D exactly: set D_est=3/sum(Y_i), I_est=D_est*Y, then x=(I_est,1-I_est,3)/(4*pi*f) and z=(I_est,1-2*I_est,2+I_est,3)/(12*pi*f). This is an exact algebraic property of the linear observation model, not permission to force nonlinear intensities to sum to three. In the full model the sum differs at second and higher orders; use its ratio forward map and previous remainder bounds instead of imposing that normalization.

For measured ratio a/b with joint bounds |delta a|<=eps_a, |delta b|<=eps_b<|b|, the quotient error is at most (eps_a+|a/b|*eps_b)/(|b|-eps_b). No independence is assumed; a near-zero denominator is refused. Shared timing, interpolation and covariance remain in that joint set. Unknown channel-specific gains or DIFFERENT corrections D_i do not cancel and can restore ambiguity. The article describes a common estimated baseline for its three first-order traces, but preserved numeric records and the exact executable correction history have not been obtained; a prose statement alone does not certify equality to cubic accuracy.

Applied correction and physical exposure must also be distinguished. If the instrument first records Z_i=H[W*F_i] and only then divides all channels by D_est, ratios eliminate D_est exactly, but generally do NOT eliminate the unknown time-varying thermal factor W inside the convolution. Ratio of convolutions is not convolution of a ratio. Under a nonnegative normalized kernel and positive intensities, an independently bounded relative variation |W(s)/W(t)-1|<=rho<1 across its support bounds the ratio distortion relative to H[F1]/H[F2] between (1-rho)/(1+rho) and its reciprocal. Gaussian/infinite support requires a tail term, not an unproved finite-support assumption. No rho is chosen here.

Updated minimum observer input: either an admitted raw/reference correction package OR full simultaneous normalized first-order traces with a verifiable common applied divisor, calibrated relative gains and joint exposure/thermal-transfer bounds. Two-order third-amplitude data alone remains insufficient under the earlier free-divisor assumption. Even successful material-state reconstruction does not identify Phi, the optical source, or the coefficients needed for a UET forecast. Prioritize this more precise existing-record inquiry before requesting new reciprocal orders or adding an action term.

If the two third-amplitude errors (including Taylor omissions) have joint component bounds E1,E2, then |delta B|<=(8*E1+E2)/(6*|K1|), before coefficient/geometry uncertainties. This is conservative without assuming independence. E_i includes 2*B4_i*max|G_i.Q|^4 for the cubic Taylor remainder; independent physical error bounds and actual reciprocal geometry are still missing. Unknown channel-specific gains can destroy the stated cancellation; they may not be fitted separately to force it. The next useful data request is therefore simultaneous normalized first/second-order signed time records with shared timing/processing and weighting information, not merely a larger archive of the same scalar trace. This designs a measurement discriminant; it is not an executed physical experiment or unique UET test.
