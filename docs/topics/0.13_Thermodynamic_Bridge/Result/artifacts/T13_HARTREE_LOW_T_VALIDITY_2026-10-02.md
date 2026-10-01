# Joint Hartree low-temperature thermodynamic admission boundary

MAJOR_RESULT_CLOSURE: `T13_JOINT_HARTREE_LOW_T_THERMODYNAMIC_COMPATIBILITY_BOUNDARY`, `CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED: Conditional asymptotic compatibility of the unchanged classical-Phi/Hartree prescription. Its positive-gap internal trace-log cannot simultaneously be admitted as complete low-T thermodynamics of the external linear gapless bosonic mode at the two witnesses. Its stationary entropy envelope is consistent, not a failed temperature derivative.

WHAT_REMAINS_OPEN: Consistent gapless thermal approximation or justified restricted validity; global spectrum/regulator/RG/Hartree remainder, independent material/source/readout/temperature inputs and physical heat/collision/Kubo/SK-KMS/entropy transport. Full Topic13/R1/Goal, novelty and measurement design remain unaccepted.

DEPENDENCY_UNLOCKED: Approximation/validity and independent-input research only. No physical/Core/Gravity unlock or overwrite of the Core owner's composition.

STATUS: `PASS_SCOPED_LOW_T_EXCLUSION`; physical low-T EOS admission is `BLOCKED_ASYMPTOTIC_SPECTRUM_THERMODYNAMICS_MISMATCH`. [Artifact](t13_hartree_low_T_validity.json) SHA-256 `6b6d5db3086439ce68703accacc04733dee8efb5535e85067b5c9941628c7f39`.

WHAT_CHANGED: Separate verifier/sixteen tests; actual zero-T stationary states, source coefficients, independent Bose entropy and fully reoptimized envelope. No old mass, potential, propagator or pole changed. Grid/gates fixed after exploratory zero-T/entropy checks; not an external-data preregistration.

EQUATION_OR_MAPPING:

## Internal positive gap

Keep original action trial inputs and Phi-dependent normalization. Let
A=a+b+4*mu^2 and D(k)=(a-b)^2+8*mu^2*(a+b)+16*mu^4+16*mu^2*k^2.

```text
E_-(k)^2=k^2+(a+b)/2+2*mu^2-sqrt(D(k))/2
Delta^2=2*a*b/(A+sqrt(A^2-4*a*b))>0 for a,b>0
h=1-4*mu^2/sqrt(D(0))>0
E_-(k)=Delta+k^2/(2*M_eff)+O(k^4), M_eff=Delta/h
```

The exact unmixed equal-mass mu=0,a=b limit gives h=1, not a cutoff repair.
Original gap identities a=2*u*s and b=2*u*(I_p-I_s) still hold.

| mu (E) | s (E^2) | b (E^2) | Phi (E) | Internal Delta (E) |
| --- | --- | --- | --- | --- |
| 1.05 | .129914154415 | .003322480632 | .047087374835 | .013591836739 |
| 1.20 | .461675943267 | .003532277093 | .176594006102 | .022085891974 |

Static amplitude/Phi blocks are locally positive and the scaled four-equation
Jacobian is nonsingular numerically. These are trial-input witnesses, not
material states, a certified interval proof or global minimum.

## Entropy envelope and asymptotic boundary

Differentiating the insertion/double-bubble terms gives tadpole-derivative
coefficients -R_a/2 and -R_b/2, where R_a,R_b are the mass residuals:

```text
-partial_T Omega = s_internal + (R_a*partial_T I_s+R_b*partial_T I_p)/2
-d_T Omega_joint_stationary = s_internal
s_internal=integral d^3k/(2*pi)^3 sum_j[(E_j/T)*n_B(E_j)-ln(1-exp(-E_j/T))]
```

Classical Phi has no explicit thermal trace-log; its implicit derivative
also vanishes from the stationary envelope. Fixed-mu/action potential
differences with all matter/Phi coordinates reoptimized recover the entropy
at T=.02/.01 E; worst final relative disagreement 4.100e-5 (gate 1e-3).

Assume a smooth noncritical stationary branch approaches these positive-gap
zero-T states with nonsingular stationary Jacobian. The quadratic minimum
then gives the leading Boltzmann approximation

```text
s_H ~ (M_eff*T/(2*pi))^(3/2)*exp(-Delta/T)*(Delta/T+5/2)
s_H/T^3 -> 0
```

Dispersion corrections vanish as T decreases. Thermal tadpoles and locally
implicit changes of a,b,Phi are exponentially small, so they do not change
this to a T^3 law. This conditional argument excludes critical/gap-closing
states and other approximation branches; it is not a continuum/global proof.

Separately, joint source-relaxed external response has positive zero-T chi
and rho, with c^2=rho/chi. Upper-plane q=.008/.004/.002 E and
z=i*(.2 or .4)*q check (rho+v_imag^2*chi)/s. Static phase inverse is
<=9.398e-11 E^2; finest quadratic disagreement <=9.608e-6. This is local
derivative evidence, not all-frequency or causal proof. If admitted as one
physical equilibrium linear bosonic excitation, ordinary mode counting gives

```text
s_ph/T^3=2*pi^2/(45*c^3)>0
```

This integral is independently checked as a comparator, never added to
Omega. Natural c=.235343000241/.377042932979 is not measured He-II sound.
At T=Delta/64, stable adaptive integration gives s_H/T^3=
2.674007281e-23/6.926675271e-24, with improving quadratic Boltzmann relative
differences .028529/.029584. The exclusion follows from the conditional
asymptotic structure, not an empirical small-ratio threshold.

The new integral factors out its Boltzmann scale and uses log1p(-exp(-x)).
The legacy entropy agrees for Delta/T<=16 but loses about 1.5 percent at
Delta/T=64 when its tiny free-energy logarithm rounds to zero. This is
disclosed numerical precision loss, not physics; no predecessor is modified.
Independent stable integration controls the deep-T evidence.

Thus source/envelope consistency does not establish asymptotic thermal
completeness. The old source-response result remains valid in its bounded
scope; this result does not establish any nonzero-T physical validity window.

The internal/external Ward distinction is method context in
[van Hees and Knoll](https://arxiv.org/abs/hep-ph/0203008); their 2PI Phi
functional is not UET Phi. [Alford et al., Sec. II.3](https://arxiv.org/html/1310.5953v2)
discuss Hartree's Goldstone issue and explicitly modify stationarity in
their treatment; that modification is not imported. Their
[low-T calculation](https://arxiv.org/html/1212.0670v3) gives phonon thermal
pressure under its own weak-coupling assumptions, not UET calibration.
Reproducing a known approximation issue does not establish novelty.

VERIFICATION: Fourteen artifact checks and sixteen focused tests passed. Zero-T orders/splits 128/20,192/40,256/64; seeds .8/1.2; source orders 96/144/192; Delta/T=2,4,8,16,32,64; envelope steps .02/.01/.005; two imaginary velocities and three q. Dispersion differences, equal-mass/gapless Bose controls, natural units, off-shell entropy identity, adaptive refinement, state/source/protected hashes and claim/read/report controls pass. An exact equal-mass test exposed the missing d=0 limit, fixed analytically without threshold change; a provenance path typo was fixed before final generation. Linked regressions are recorded in UPDATE_LOG.

CONTROLLING_BLOCKER: `gapless_equilibrium_thermal_prescription_not_derived`.

NEXT_ACTION: Derive a same-action consistent low-T approximation or justified restricted validity. A proposed loop-ordered Goldstone EFT route must distinguish its stationary expansion from old Hartree, quantify control at the trial coupling and avoid double counting; it is not yet implemented or accepted. Do not set old b to zero or append phonon free energy by hand. Independent source/readout/thermal input remains required; 7 October freeze/11 October portfolio review unchanged.

| Route to investigate | Decisive calculation | What would not close it |
| --- | --- | --- |
| Same-action loop-ordered low-T EFT (first proposed route) | Eliminate amplitude/classical Phi consistently at each order; derive phase source/pressure and its thermal determinant in that new approximation; check entropy/current derivatives, stability, units and an explicit control domain | Reusing old Hartree masses, appending its external phonon determinant or assuming u=1 is controlled without estimating enhanced/omitted terms |
| Justified restricted Hartree domain | Bound the actual omitted thermal contribution against a declared observable margin with separately admitted inputs | A positive root, gap/T crossing or choosing a warmer interval until a plot agrees |
| Constrained/symmetry-improved resummation (alternative, not selected) | Derive the new stationary/source action and check both equilibrium and driven linear-response solvability | Imposing b=0 on old equations or assuming a Ward constraint alone fixes dynamics |

[Pilaftsis and Teresi](https://arxiv.org/abs/1305.3221) supply an O(2)
symmetry-improved equilibrium construction, but
[Brown, Whittingham and Kosov](https://arxiv.org/abs/1603.03425) find
linear-response pathologies for their constrained formalism. This makes
the alternative a new research obligation, not a ready-made UET repair.
The first route is a proposed order-consistent calculation, not yet a
controlled material result; none of these routes creates independent
alpha_Phi_K, source rows or physical Kubo input.

CLAIM_BOUNDARY: Conditional local admission exclusion at two trial-input states, not global UET no-go, exact continuum proof, new thermal model, physical material/heat/Kubo/collision/KMS/entropy, SI alpha, external validation or Full Topic13/Core. Old response and Core-owner composition intact. C is not signed O(2) charge/mass; Phi remains response; R_gen/R_obs not dynamics. No fit, mass/phonon repair, clipping/filter/padding, threshold change or new numeric Xie access. Original conserved-C failure BLOCKED at 1e-6; prior Xie exposure REVIEW_REQUIRED.
