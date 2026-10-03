# Conditional dynamical composite and current-source matching

MAJOR_RESULT_CLOSURE: `T13_CONDITIONAL_DYNAMIC_COMPOSITE_AND_CURRENT_MATCH`, `CLOSED_FOR_LANE` in a declared leading Gaussian phase theory. This does not close the microscopic background.

WHAT_IS_ACTUALLY_CLOSED: The same Cartesian longitudinal source now has a conditional finite-frequency continuum and a retarded time kernel. Pair creation and thermal scattering are derived separately. Independent frequency, momentum, spectrum and time calculations return the previous static IR coefficient. A contact-completed Gaussian current-source Hessian obeys its Ward identity.

WHAT_REMAINS_OPEN: Renormalized amplitude and joint Phi equilibrium, interacting/vacuum matching, controlled microscopic error, material/source/detector inputs, finite-temperature normal component and microscopic SK/KMS/transport. A spectrum in the phase approximation is not an admitted physical response.

DEPENDENCY_UNLOCKED: Same-lane frequency-protocol and measurement design only. Recorded Core composition and physical funding/full-Topic13 gates are unchanged.

STATUS: `PASS_CONDITIONAL_PHASE_DYNAMIC_RESPONSE` in the [artifact](t13_polar_dynamic_composite.json). The artifact's checks, not this note's prose, determine its diagnostic state.

WHAT_CHANGED: Added one dynamic-composite verifier, sixteen tests, this derivation and a generated artifact; linked the result to the current research plans. Original Gaussian stationarity and failed direct tree-stiffness lift remain intact.

EQUATION_OR_MAPPING:

## 1. Source, action and scope

Continue the [same-field polar result](T13_POLAR_STATIC_IR_OBSERVABLE_2026-10-01.md), with the original Cartesian longitudinal probe coupling to

```text
varphi_l = A+h-A*theta^2/2+...; O_l,composite = -A*theta^2/2, x=A^2.
S_phase = rho_s/2 * integral [(grad theta)^2 + (partial_tau theta)^2/c^2].
G_theta(i nu,k) = c^2/[rho_s*(nu^2+c^2*k^2)].
chi_composite(i Omega,q) = x/2 * T sum_n integral_k G_theta(nu,k) G_theta(nu+Omega,k+q).
```

The Wick factor is two; the observable vertex is `-A/2`. There is no new fundamental field. Phi is fixed, C is not Noether charge or mass, and R_gen/R_obs are not dynamical states. The Gaussian phase action is conditional: its coefficients still require a consistent renormalized background before material admission.

Only the leading composite contribution is computed here. The h response and
amplitude/phase mixing can supply additional regular and pole contributions;
they are not silently included in this formula. Away from the ideal threshold
the composite IR contribution grows as 1/q at fixed z/(cq), but a uniform
near-pole full-response matching still requires those other terms.

For coefficient matching, retain the previous tree witnesses without selecting the one that looks better:
`x=Z*r/lambda`, `rho_s=Z*x`, `c^2=r/(r+2mu^2)`.
T=0.22, Phi=0.15, Z=lambda=1 and mu=1.05/1.20 are unchanged.

Natural units: q, frequency, T and mu carry E; x and rho_s carry E^2; theta and c are dimensionless. Frequency susceptibility carries E^-2, time response E^-1 and time E^-1. The source J_l carries E^3. This is not Phi-to-K calibration or a He-II second-sound prediction.

## 2. Independent frequency sum

For e=c*k, f=c*ell, S=e+f and D=e-f, the thermal part of the frequency sum is

```text
B_T(e,f,z) = (n_e+n_f)*S/[2 e f (S^2-z^2)]
           + (n_f-n_e)*D/[2 e f (D^2-z^2)].
```

The vacuum pair term has the additional numerator one. At D=0 and static z=0 the second term is `n_e*(1+n_e)/(2e^2 T)`; dropping it loses the scattering response. The code evaluates the Bose divided difference with expm1 and its exact coincident limit, without a fitted small-gap threshold.

Direct sums at external harmonics zero and one use 128/256 terms and an independently derived nu^-4 tail. Subtract the analytic vacuum frequency integral at the same external harmonic. These direct sums match the spectral expression to the preregistered 1e-7 relative criterion.

## 3. Real-axis spectrum from the on-shell triangle

Write a=c*q. The three-dimensional integration measure becomes

```text
integral d^3k/(2pi)^3 = 1/(4pi^2 q c^4) integral e de f df,
|e-f| <= a <= e+f.
```

The positive-frequency absorptive susceptibility in the linear Gaussian continuum is

```text
Im chi^R(q,omega) = x/(16pi rho_s^2 q) * [
  a/2 * Theta(omega-a)
  + T log((1-exp(-(omega+a)/(2T)))/(1-exp(-abs(omega-a)/(2T)))) ].
```

For 0<omega<a there is thermal scattering; above a there is pair creation plus its thermal occupation correction. Both thermal pieces are obtained independently by integrating n(e) from `abs(omega-a)/2` to `(omega+a)/2`. At omega=a the ideal linear Gaussian spectrum diverges logarithmically. It is integrable; the code refuses an exact-threshold point instead of assigning a width or clipping it.

The vacuum spectral continuum is finite, but its all-frequency static dispersion is UV divergent and needs subtraction/matching. Only the thermal difference is used for the convergent numerical dispersion integral. Its quantum all-momentum linear extension is a mathematical cross-check, not evidence that high-momentum microscopic modes are correctly described.

## 4. Conditional classical IR response and time kernel

When external omega,cq are small compared with T, the leading thermal spectrum is

```text
Im chi_cl^R = B log((omega+a)/abs(omega-a)),
B=x*T/(16pi rho_s^2 q).
chi_cl^R(q,z) = i B log((z+a)/(z-a)), Im z>0.
chi_cl^R(q,0) = pi B = x*T/(16rho_s^2 q).
chi_cl^R(q,t) = Theta(t)*2B*sin(a*t)/t.
```

The logarithm branch is analytic in the upper half-plane. Its inverse time transform has retarded support and a 1/t oscillatory tail; it is not a single exponential relaxation. Two imaginary-frequency protocols yield different effective Debye relaxation times, explicitly excluding a frequency-independent single-pole representation of this conditional continuum. This does not prohibit other microscopic damping mechanisms or modes.

An independent classical pair/scattering integral uses S>=a and -a<=D<=a. Analytically integrating one variable gives two convergent one-dimensional integrals, evaluated without reusing the closed logarithm. A separate damped time transform agrees as well. These checks do not prove that the original full conserved-C branch passes its finite-cone leakage gate.

The thermal spectral dispersion is evaluated at q=.005,.0025,.00125 with fixed z/(cq). Both static and dynamic differences from the classical asymptote decrease. At the smallest q the static differences are about 0.12%/0.19% and dynamic differences 0.15%/0.24% for the two witnesses. These are comparisons within the declared linear Gaussian extension, not estimates of the error of the microscopic theory.

In fact T/[c*sqrt(2r)] is about 2.18 and 0.636. The first witness especially cannot justify extending the low-energy phase spectrum across the whole thermal distribution. Leading IR matching survives this warning, but the complete quantum thermal response is not admitted as material physics. The next wave must control matching to the existing full action, not hide this domain gap.

## 5. Current contact and Gaussian detailed balance

At vanishing Cartesian symmetry-breaking probe, introduce Euclidean gauge source a_mu, Q=(nu,q) and W=diag(rho_s/c^2,rho_s,rho_s,rho_s). Eliminating the phase gives

```text
Pi = W - (W Q)(W Q)^T/(Q^T W Q),
Q^T Pi = 0.
```

An independent source-action Hessian agrees with Pi. Removing the local W contact term violates the Ward identity. This is a Gaussian current-source identity, not a microscopic Kubo or normal-component calculation.

Full Gaussian greater/lesser on-shell weights obey detailed balance. For a pair they are `(1+n_e)(1+n_f)` and `n_e*n_f`; for e>f scattering they are `n_f*(1+n_e)` and `n_e*(1+n_f)`. Their ratio supplies exp(-omega/T), and their half-sum obeys the symmetric FDT with the full commutator. Do not apply that full-correlator FDT to the thermal difference alone or report this check as complete microscopic SK/KMS matching.

The spectrum's continuum absorption can arise from composite phase correlations even though these Gaussian phase modes have no collision width. Absorption/dephasing is not a viscosity, heat conductivity, entropy-current closure or fitted damping rate.

## 6. Method attribution and next decision

[Dupuis](https://arxiv.org/html/1011.3324v2) provides amplitude-direction and IR context for different model classes. [Podolsky, Auerbach and Arovas](https://arxiv.org/abs/1108.5207) emphasizes that longitudinal and scalar responses are different observables. The finite-T normalizations, phase-space derivation and checks above are explicit conditional calculations for this declared lane; these references are not imported TTG/He-II measurements or a novelty certification.

VERIFICATION: Sixteen dynamic tests, including direct Matsubara versus spectral sums, pair/scattering phase space, classical loop versus logarithm, time transform, static/dynamic refinement, contact/source Hessian, detailed balance, unit scaling, threshold refusal, T0 limits and audit-read allowlist. Related earlier tests and evidence hashes must also pass before integration. No source rows or numeric holdout are read; prior Xie context-exposure review remains open.

CONTROLLING_BLOCKER: `renormalized_stationary_background_and_dynamic_matching_remainder_not_closed`.

NEXT_ACTION: Match the leading phase/composite result to a source-complete renormalized/interacting background and the full-action dynamic current. Establish the matching remainder and material source/detector inputs before accepting a physical prediction. Keep the original failure baseline; do not change x/rho_s/c using the target response.

CLAIM_BOUNDARY: Conditional dynamical source response and measurement-design progress only. No physical Kubo, independent thermal prediction, exact finite-T state, full causal-branch repair, global UET closure or physical funding-gate unlock follows.
