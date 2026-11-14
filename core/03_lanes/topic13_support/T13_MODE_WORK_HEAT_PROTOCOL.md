# Mode energy is not automatically heat

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for the conditional independent-harmonic-mode protocol distinction.

WHAT_IS_ACTUALLY_CLOSED: Work from changing gaps is separated from heat carried by changing occupations. Equilibrium isothermal and isentropic limits and frozen-occupation evolution are different. A spectrum at one control value does not identify its derivative with respect to Phi.

WHAT_REMAINS_OPEN: Physical gap-to-Phi derivative, normalization, prepared occupations, relaxation/bath dynamics, full dispersion/measure and same-state material correspondence.

DEPENDENCY_UNLOCKED: Protocol-aware thermal-map design only; no physical dependency gate.

STATUS: PASS_CONDITIONAL_HARMONIC_PROTOCOLS.

WHAT_CHANGED: Added a standard harmonic comparator, nine tests, a candidate registry and an illustration using the source Gamma pair. No bath rate or physical source coefficient is invented.

EQUATION_OR_MAPPING: Let epsilon_i>0 be gaps in J, w_i fixed dimensionless mode weights, n_i Bose occupations, and C_i their heat capacities. Positive work and heat enter the subsystem. For a declared external control lambda with gap derivative f_i:

```text
U = sum_i w_i*epsilon_i*(n_i+1/2)
dU = sum_i w_i*[(n_i+1/2)*d_epsilon_i + epsilon_i*dn_i]
W_lambda = sum_i w_i*(n_i+1/2)*f_i
Q_lambda|T = -T*sum_i w_i*C_i*f_i/epsilon_i
U_lambda|T = W_lambda + Q_lambda|T
S_lambda|T = Q_lambda|T/T
T_lambda|S = T*sum_i w_i*C_i*f_i/epsilon_i / sum_i w_i*C_i
```

VERIFICATION: Nine independent tests check energy/entropy central derivatives, isentropic cancellation, uniform scaling, nonuniform frozen-mode temperature incompatibility, source-derivative non-identifiability and invalid-mode rejection. No negative mode is clipped. The illustration checks existing source hashes and reads no TTG/holdout data.

CONTROLLING_BLOCKER: physical_gap_source_derivative_and_relaxation_protocol_missing.

NEXT_ACTION: Obtain the source response f_i and the occupation/bath equation independently. Require source power, thermalization and heat transport to balance. If f_i cannot be obtained, retain an explicitly parameterized response rather than emitting alpha. Do not substitute a strain derivative for a Phi derivative without its own physical map.

CLAIM_BOUNDARY: Canonical harmonic equilibrium or quantum-adiabatic frozen populations only. Rapid quenches, coherences, squeezing, interacting baths, changing mode weights/volume and anharmonic transport are excluded. This is not SK/KMS closure, material calorimetry or Full Topic 13 readiness. He-4 and full-topic artifacts remain unchanged.

## Meaning of the protocols

At fixed bath temperature, raising a gap does positive work but can release heat;
the resulting energy change cannot all be labeled heating. At fixed occupations,
gap changes do work without population heat. This assumes adiabatic following,
not an arbitrary fast frequency change. If every gap scales by the same factor,
the unchanged occupations admit a common temperature rescaled by that factor.
With unequal fractional gap changes they generally do not: a single inferred
temperature requires internal equilibration and the corresponding dynamics.

The isentropic formula assumes a reversible internally equilibrated state. For
an arbitrary nonequilibrium population it is not a thermometer. A stationary
isothermal experiment instead has dT/dlambda=0 by its imposed bath condition.

The existing candidate mass source `x_i=epsilon_i^2=x_i0-eta_i*Phi` would give
`f_i=-eta_i/(2*epsilon_i)` only after SI normalization and material correspondence.
This algebra does not determine eta_i. Multiplying all eta_i by two leaves the
unperturbed spectrum and heat capacity unchanged but doubles the isentropic gain.
Spectroscopy of the unperturbed material alone therefore cannot calibrate Phi.

## Illustration boundary

The generated example uses the two MP48 Gamma gaps and a dimensionless *synthetic*
common log-gap control, so f_i=epsilon_i by definition. Unit weights count two
oscillators; they are not a crystal heat-capacity measure. The resulting 200 K
temperature tangent is a scaling identity, not an observed temperature rise.
Zero-point energy is retained in work/internal energy and drops out of entropy
and heat capacity. No UET vacuum subtraction or total material energy is closed.

[Deffner and Lutz](https://arxiv.org/abs/0711.3914) treat work for time-dependent
harmonic frequencies, distinguishing adiabatic and nonadiabatic processes.
This comparator uses only the equilibrium/adiabatic limit, not their full work
distribution. Evidence: `artifacts/t13_mode_work_heat_audit.json`.
