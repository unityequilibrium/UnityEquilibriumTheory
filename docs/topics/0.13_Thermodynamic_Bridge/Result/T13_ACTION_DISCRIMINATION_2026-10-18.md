# Action-level discrimination: what is testable, and what is not unique to UET

Owner: Topic13/Core correspondence review. Class: FORMAL CONDITIONAL, not physical validation. Parent: the unchanged [dual-channel result](T13_DUAL_CHANNEL_IDENTIFIABILITY_2026-10-17.md) and [physical-route decision](T13_PHYSICAL_ROUTE_ADMISSION_2026-10-18.md).

## Question fixed before calculation

Determine whether the existing conservative scalar/O(2) action imposes a relation outside an ordinary scalar-mediator comparator, and whether alternative existing lanes evade that limitation. If its coefficient image is the full comparator class, changing instruments cannot uniquely identify the theory label. Nevertheless derive a falsifiable restricted-model relation rather than equating non-uniqueness with untestability. Do not add a coupling, choose constants from target responses, rerun old harmonic inverses, or treat the default configuration as measured physics.

The primary calculation is an exact field/coefficient transformation. A nontrivial leftover relation would supply a distinguishing candidate; a surjective map supplies an explicit model-class counterexample. A second calculation eliminates the existing static response: its sign/shape constraints could reject the specified constitutive model even if they cannot identify UET uniquely. These outcomes are not interchangeable.

## Authoritative scope and symbols

Use [covariant response](../../../core/02_equations/covariant/uet_covariant_response.py), `conservative_lagrangian_scalar`, and [covariant matter](../../../core/02_equations/covariant/uet_covariant_matter.py), `coupled_matter_lagrangian_scalar`, as implemented, not an inferred future action. Write e=epsilon_nc, d=Phi-Phi_*, Zp=response_kinetic, Zc=matter_kinetic, mp2=response_mass_sq, mc2=matter_mass_sq, lp=response_quartic, lc=matter_quartic, xi=curvature_coupling, h=response_coupling. chi^2 means chi_1^2+chi_2^2, not a conserved density. The density is

```text
L = (1+e*xi*d^2)*(R-2*Lambda)/(2*kappa)
    -e*Zp*(grad d)^2/2 - Zc*sum(grad chi_A)^2/2
    -e*rho -e*mp2*d^2/2 -e*lp*d^4/4
    -mc2*chi^2/2 -lc*(chi^2)^2/4 +e*h*d*chi^2/2.
```

Natural units only: d,chi have mass dimension 1; Zp,Zc,e,lp,lc dimension 0; mp2,mc2 dimension 2; h dimension 1; xi,kappa dimension -2; rho dimension 4. Source code accepts e>=0, Zp,Zc>0, mp2>=0, lp,lc>0, h>=0, any mc2, and only the domain with positive curvature factor. All are configuration inputs, not independently measured or derived numerical constants. This audit does not cover every historical equation in the repository or silently identify the normalized dissipative lane with this action.

## A. Exact coefficient image, including curvature

For e>0 define constant invertible field coordinates

```text
p=sqrt(e*Zp), c=sqrt(Zc), psi=p*d, eta_A=c*chi_A.
M2=mp2/Zp; m2=mc2/Zc
ls=lp/(e*Zp^2); lm=lc/Zc^2
g=sqrt(e)*h/(sqrt(Zp)*Zc); X=xi/Zp; r0=e*rho.
```

Direct substitution, with the metric unchanged, gives exactly

```text
L = (1+X*psi^2)*(R-2*Lambda)/(2*kappa)
    -(grad psi)^2/2 -sum(grad eta_A)^2/2
    -r0-M2*psi^2/2-ls*psi^4/4
    -m2*eta^2/2-lm*(eta^2)^2/4+g*psi*eta^2/2.
```

This is a constructive canonical scalar/O(2) mediator comparator, with the SAME restricted polynomial content and sign/domain rules. It is not the Standard Model or every conceivable ordinary model. No gravity or nonminimal-curvature term was thrown away. The Jacobian is a nonzero constant: functional derivatives transform as E_d=p*E_psi and E_chi=c*E_eta, so corresponding on-shell solutions and consistently transformed initial/boundary/source data coincide. This classical statement does not assert a quantization or renormalization theorem.

**Surjectivity:** choose e=Zp=Zc=1 and identify mp2=M2, mc2=m2, lp=ls, lc=lm, h=g, xi=X, rho=r0 for ANY comparator coefficient tuple in the admitted domain. Thus the action's current independent coefficients impose no additional numerical relation among this comparator's coefficients. Its missing polynomial operators and O(2) symmetry remain testable restrictions relative to a larger model; they are not unique UET predictions. Negative g can also be reversed by the response field orientation, but no sign-flip extension is needed for the stated image.

At e=0 this chart is singular and must NOT be used. The original action instead loses its response sector and interaction, retaining the original matter and gravitational terms. Taking e->0 while holding the canonical couplings fixed is not the same experiment as holding the original coefficients fixed. No regular epsilon-limit claim is introduced.

## B. Observer and zero-signal counterexamples

For any admitted observation functional O[d,chi,g_mu_nu; detector], define the comparator functional by composing the inverse field map. Both then produce the same record for corresponding solutions and identical detector dynamics. This is equivalence of the complete assumed forward descriptions, not permission to fit an arbitrary detector or manufacture a material map. An independently established detector coupling different between the descriptions would break the premise and must be tested explicitly.

Consequently a reciprocal two-mode interaction, a scalar pole, O(2) current conservation or a causal response can distinguish a RESTRICTED null without uniquely identifying UET. The prior passive-control ambiguity and finite-error weak-pole limitation are reused unchanged.

There is also an exact allowed no-signal member: e>0, h=xi=rho=0, with d and its initial derivative zero. Then the response equation is satisfied with d=0, its stress vanishes, and the matter/metric sector is the corresponding ordinary scalar-matter problem. The configuration permits h=0 and does not impose an independently physical lower bound. Absence of an extra response therefore cannot reject the entire free-parameter family. This does not protect a separately locked nonzero-coupling model from falsification.

## C. A falsifiable relation already in the action

Use the declared homogeneous, static, flat, zero-Lambda, zero-external-response-source sector. Hold the matter invariant s=eta^2>=0 at specified prepared values. This is a restricted boundary/preparation protocol, not a claim that a real beam displacement is eta or that the full matter equations need no preparation force. The response energy is

```text
V(psi,s)=M2*psi^2/2+ls*psi^4/4 +m2*s/2+lm*s^2/4-g*psi*s/2.
stationarity: M2*psi+ls*psi^3=g*s/2.
```

If a nonzero but constant curvature background is retained, its response coefficient is instead `M2_local=M2-X*(R-2*Lambda)/kappa`. The cubic form survives but the nonnegative-coefficient domain must be checked again; positive original mp2 alone does not guarantee M2_local>=0. The flat/zero-Lambda control is an explicitly selected mathematical sector, not an assertion that curvature corrections vanish in a real laboratory. A real protocol must retain them or justify their output-unit bound.

For M2>=0, ls>0, g>0 this has a unique nonnegative minimizer at each s>=0 (strictly increasing cubic; at M2=s=0 the derivative vanishes at zero but uniqueness remains). At D=M2+3*ls*psi^2>0, implicit differentiation gives

```text
dpsi/ds=g/(2*D)
d^2 V_eff/ds^2=lm/2-g^2/(4*D) <= lm/2
d^3 V_eff/ds^3=3*g^3*ls*psi/(4*D^3) >= 0.
```

The negative Schur-complement correction is mandatory for this stable static elimination. It does not establish positive full matter stability, an entropy law, finite-temperature dynamics or numerical values for a material. With M2>0 the small-s effective quartic is lm-g^2/(2*M2). For M2=0 the small-s Taylor formula is invalid: psi=(g*s/(2*ls))^(1/3) and the response contribution is `-3/4*(g/2)^(4/3)*ls^(-1/3)*s^(4/3)`. Do not hide this boundary with a mass floor.

### Gain-aware source-controlled test, not another passive two-channel fit

If independently established zero offsets and common positive linear gains give z=Gpsi*psi and u=Gs*s, the source law becomes

```text
u=A*z+B*z^3,
A=2*Gs*M2/(g*Gpsi) >= 0,
B=2*Gs*ls/(g*Gpsi^3) > 0.
```

Two DISTINCT positive calibration z values identify A and B by the straight line `u/z=A+B*z^2`. Given a separately locked held-out source u3>=0, solve the monotone cubic for its unique z3>=0 with A,B frozen. This is an output prediction in instrument units without requiring separate absolute field normalizations. It is not a first-principles amplitude prediction: A,B are openly calibrated combinations. Nonlinear readout, unknown offsets, uncontrolled response source, spatial gradients, time dependence, curvature or varying state invalidate this simple operator unless modeled or bounded. g=0 cannot use this inverse.

Here u is an independently reconstructed proxy for the prepared matter invariant s, NOT an arbitrary laser power, electrode voltage or applied response force. The preparation-to-s transfer is part of the physical admission requirement. If [z]=U and [u]=V, then [A]=V/U and [B]=V/U^3; the pointwise cubic residual has unit V. In natural units [s]=E^2, [D]=E^2, [dpsi/ds]=E^-1, [V_eff'']=1 and [V_eff''']=E^-2. Neither this field coordinate convention nor the calibration fixes an absolute SI Phi anchor.

For finite bounded errors, the preregistered prediction is a SET: all z>=0 satisfying u=A*z+B*z^3 for (A,B) in the independently admitted joint calibration set and u in the held-out source interval. Reject this specific model/protocol only if that prediction set and the independently reconstructed measurement set are disjoint. Otherwise report inconclusive. No physical error budget or confidence level is invented here; point estimates and exact control tests do not substitute for those sets. The native MEMS auxiliary-drive experiment has an extra source and is not automatically this protocol.

This law and softening are also predictions of the explicit ordinary scalar comparator. Passing them supports a specified effective constitutive law, not a uniquely UET ontology. Their value is an actual falsifier after protocol admission, rather than an unfalsifiable theory label.

## D. Alternatives examined before stopping the uniqueness question

| Existing route | Action/operator consequence | What it can discriminate | Why it does not evade the present limitation |
| --- | --- | --- | --- |
| Full conservative covariant action | Exact canonical image above, including X*psi^2*R | Particular scalar/curvature parameter hypotheses vs restricted nulls | No residual extra coefficient identity in this parameterization; no claim about unknown future action |
| Two-mode MEMS/pole | Prior reciprocal/pole relations and native-source audit | Contact-only/passive nulls under independently admitted transfer | Ordinary coupled modes share them; native extra forcing prevents silently reusing a source-free kernel |
| Static full quartic response | Cubic source law and Schur softening above | Locked affine-only or wrong-sign/wrong-shape constitutive models | Ordinary mediator gives exactly the same relation; material/source/readout preparation still must match |
| Normalized matter-space | Existing Omega and constant mobilities give C_t=M_C*lap(mu_C) (or -M_C*mu_C), tau*Phi_tt+Phi_t=-M_Phi*mu_Phi+J | Particular gradient-flow/inertial phase-field approximations | Construct an ordinary order-parameter comparator with the SAME Omega and mobility laws; C is not thereby identified with covariant chi or SI mass |
| Trace/observer extension | R_gen is a retarded postprocessing functional with no feedback in this lane | Wrong source/readout operator under fixed calibration | Applying the same postprocessor to identical state trajectories gives identical records; cannot add new dynamics by renaming a record |
| O(2) thermodynamics | Existing tree-level potential and global rotation symmetry | Particular EOS/transport approximations once their domain is admitted | Same canonical O(2) action gives the same tree-level relation; neither finite-temperature closure nor He-4 identity follows from the symmetry |
| Existing linear open-system controls | Physical exponential memory, specified covariance and local SK inverse kernel | Markov-only, wrong-memory or non-KMS restricted models after coefficient/measurement admission | These constitutive operators admit an explicit ordinary linear-filter/damped-oscillator comparator; coefficients are not unique measured UET constants |

The normalized comparator is constructed at the level of the existing discrete free energy, finite-difference operators, sources and update convention, so it need not assume a new continuum theorem or a reduction from the covariant lane. This is not a global statement about all UET topics, particles, cosmology, every dissipative extension or future physical identifications. A new cross-system parameter lock or non-equivalent source/observer interaction would require fresh review rather than being ruled out by this proof.

### Physical memory must not be confused with postprocessing

The [covariant open-system control](../../../core/02_equations/covariant/uet_covariant_open_system.py) uses `K(t)=theta(t)*diag(exp(-t/tau)/tau)*L`, `x_dot=-K*f+source`, and a discrete history quadrature. Thus memory DOES feed the state evolution. An ordinary linear auxiliary filter `tau*z_dot+z=L*f` has the same retarded convolution for matched history/initial memory (the implemented coupled sectors require a common tau when L has off-diagonal terms). Constructing the same discrete convolution and Euler update gives identical current-code rates. This is not an assertion that an arbitrary continuum approximation equals the discrete quadrature.

Its declared classical covariance is `N(t)=T*(K(|t|)+K(|t|)^T)`; an ordinary linear bath control can be specified with that SAME covariance. Equality of this two-point object is not a proof of equality of all stochastic trajectories or higher cumulants, and the current deterministic evolution function does not sample a noise process. The [formal local SK/KMS lane](../../../core/02_equations/o2/uet_o2_open_system_sk_kms.py) specifies `K_R=kappa-chi*omega^2-i*gamma*omega`, the inverse operator of a damped oscillator, with formal FDT noise; it does not derive its physical Kubo values. Full interacting microscopic/open-sector equivalence is NOT established by this limited linear comparison. No allegedly new prediction is extracted from simply renaming this kernel, and no physical memory term is deleted from the comparison.

Literature context only: [Oncala and Petraki, 1808.04854v3](https://arxiv.org/abs/1808.04854v3), section 3, discusses ordinary scalar-mediator couplings; [Cavaterra, Grasselli and Wu, 1310.0965](https://arxiv.org/abs/1310.0965) discusses inertial/viscous phase-field dynamics. Neither is claimed to be an exact material realization of UET. The exact comparator and the equivalence proof here are explicit constructions, not conclusions inferred from those papers.

## Decision and next research requirement

The inspected existing action is falsifiable as a specified effective model but does not, with its present free coefficients and corresponding observation map, supply a unique discriminator against the constructed ordinary scalar comparator. The complete coefficient map and allowed zero-signal member establish this limitation without waiting for an email or a laboratory dataset. This is more specific than merely saying a material map is missing.

Do not launch a MEMS fit to settle a distinction the forward equations do not contain. For a practical test of the EXISTING model, next admit a physical system implementing the static cubic-source protocol or the prior independently controlled two-mode protocol, with joint calibration/omission bounds; then lock instrument-unit prediction sets before scoring reserved records. For a UNIQUE theory test, first supply an already justified cross-system coefficient relation, physical identification or source/detector coupling not shared by the comparator. None is derived by changing variable names, fixing benchmark defaults or adding an unexplained term. This report does not invent one.

Reproduction: [producer](../Code/03_Research/Research_T13_Action_Discrimination.py), [tests](../Code/03_Research/test_t13_action_discrimination.py), [contract](../calculation_contracts/action_discrimination.json), [canonical generated decision](../../../core/07_artifacts/topic13/t13_action_discrimination.json). Exact finite controls check the implementations and counterexamples; the all-field argument is the substitution and surjectivity proof above. No physical response rows, new action implementation, unchanged old verifier reruns, author contact, large data or push.
