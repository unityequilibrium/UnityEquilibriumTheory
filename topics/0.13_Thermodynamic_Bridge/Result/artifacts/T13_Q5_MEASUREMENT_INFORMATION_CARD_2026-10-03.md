# Q5 Measurement Information And Precision Supplement

MAJOR_RESULT_CLOSURE: Restricted q5 information component CLOSED_FOR_LANE;
physical measurement design/validation remain OPEN.

WHAT_IS_ACTUALLY_CLOSED: An alternative to independent U exists: with the
other native coefficients known, q5 unit-free information uniquely identifies
positive kinetic I and then the energy/momentum scales. No physical data used.

WHAT_REMAINS_OPEN: Native coefficient/state/current admission, measured q5,
joint resolution and full covariance, practical estimator and physical
interaction/finite-T validity. Gain and Phi-to-temperature stay separate.

DEPENDENCY_UNLOCKED: One conditional higher-dispersion information route;
not full Topic13, G4, R1-R5 or Core acceptance.

STATUS: DERIVED_CONDITIONAL_INFORMATION_NOT_PHYSICAL_MEASUREMENT.

WHAT_CHANGED: The [q3 card](T13_DENSITY_SPECTROSCOPY_MEASUREMENT_CARD_2026-10-03.md)
is extended, not contradicted. Its U route is sufficient but not uniquely
necessary for the restricted class when q5 can be resolved independently.

EQUATION_OR_MAPPING: r=A_Q*C_Q/B_Q^2=r0-D*(I/(1+sI))^2, with the
positive-class inverse and exact tree envelope in the
[derivation](T13_Q5_DISPERSION_INFORMATION_2026-10-03.md).

VERIFICATION: Eight scientific checks pass; local relative inverse condition
numbers246.476/26.218 in the two declared states. A finite-q proxy still
biases I by1.477%/0.04187% at q.005. These are derived witnesses, not data.

CONTROLLING_BLOCKER: physical_q5_resolution_native_input_covariance_material_map_and_interaction_error_open.

NEXT_ACTION: Derive a multi-q estimator and its joint covariance/tree bias
envelope; determine which q-window and independent input package could
resolve I before seeking a physical comparison. Do not fit the holdout.

CLAIM_BOUNDARY: Other native inputs are fixed only conditionally. No full
minimum-measurement theorem, laboratory precision/feasibility, gain,
temperature, KMS or physical material admission. C/Pi/R_gen/R_obs untouched,
Xie numeric paths unread and exposure REVIEW_REQUIRED. Original dates/gates stay.

## What A Measurement Must Resolve

Let kappa=|r/(I*dr/dI)|. If native inputs were exact, a local1% I target
would require relative r uncertainty below approximately4.057e-5 or3.814e-4
for the two witnesses. This is an illustrative sensitivity requirement,
not achievable precision, an uncertainty estimate or a new acceptance gate.
Native parameter, background and resolution errors can dominate it.

For log-inputs(A_Q,B_Q,-C_Q,-r0,D,s), f=1+sI and J_I=-f^3/(2DI),

```text
g=(J_I*r, -2J_I*r, J_I*r, -J_I*r0, -I*f/2, s*I^2)
Var(I)=g^T*Sigma_log*g plus separately controlled physical/theory errors
```

Logs use reference ratios. Native inputs share an action/state and cannot
be treated as independent by default. Numerical inverse accuracy does not
measure this covariance. Detector gain remains an amplitude ambiguity
even if dispersion coefficients are known.

The finite-q proxy (E(q)-c*q-eta*q^3)/q^5 is not the asymptotic coefficient.
For mu1.05 its I biases at q.02/.01/.005 are27.06%/6.043%/1.477%; for
mu1.2 they are0.6717%/0.1676%/0.04187%. Thus the finest first-state proxy
already misses an illustrative1% target without any measurement noise.
Reducing q lowers expansion bias but also weakens q5 signal. A defensible
window needs the estimator, correlated noise and resolution, not a smaller
q chosen merely to pass a simulation threshold.

## Evidence And Portfolio Boundary

Artifact SHA-256:
`c4b23308c1ffdc45215cdba8d1fb0e3ba8b44c861d8c2c402bec22b3055a6485`.
Zero numeric rows admitted. The existing conditional low-T neutron route
still requires source ancestry/rights, same-state particle-current and
axis/resolution mapping; no transfer from existing1.7K calibration.
This supplement does not accept G2-G4/full Goal or establish novelty.
Preserve7 October freeze/11 October portfolio review and later review dates.
