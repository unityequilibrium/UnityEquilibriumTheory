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
