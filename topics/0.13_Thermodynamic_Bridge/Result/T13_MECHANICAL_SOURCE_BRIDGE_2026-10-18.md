# Mechanical source bridge: mass modulation is not an additive coherent drive

Owner: Topic13/Core correspondence. Scope frozen for this wave: the existing flat homogeneous conservative normal-background O(2) branch used by the mechanical nonlinear kernel, proposed graphite coherent-shear identification, no new source/action term. Question: can the existing scalar-response/mass coupling itself supply the independently driven coherent matter trajectory required by the kernel test?

## 1. Reuse and missing pieces

This is not another proof of the field-chart ambiguity, scalar E2g selection rule, optical-order mismatch, or action-class equivalence. Reuse the [observer-aware decision](T13_OBSERVER_DISCRIMINATION_2026-10-17.md), [action-class result](T13_ACTION_DISCRIMINATION_2026-10-18.md), [scalar/shear channels](../../../core/03_lanes/topic13_support/T13_SHEAR_SYMMETRY_CHANNELS.md), [matter-source harmonics](../../../core/03_lanes/topic13_support/T13_MATTER_ACTUATION_HARMONICS.md) and the pinned owner readout derivation at commit `0f17012ffd6ad456c150b10e048efd868ce95588`. The new question is the reverse driven initial-value problem, not the older source chi^2 -> Phi harmonic calculation.

| Bridge item | Classification from existing evidence | What this wave must decide |
| --- | --- | --- |
| Conservative action and reciprocal mass coupling | Derived/implemented conditional model | Use exact current matter force; no parameter replacement |
| Mechanical chi_J=beta*Q and graphite E2g identity | Physical-identification hypothesis, not established by naming | Kinetic chart/irrep/mode profile still require independent material support |
| Propagator-corrected signed Q3/Q1^3, with Q2 competitor correction | Derived conditional readout | Its assumed generalized force J must not be silently identified with the pump |
| Scalar Phi or external mass/strain modulation | Conditional mass/stiffness channel | Does this channel create coherent displacement from the declared normal initial state? |
| Pump polarization/orientation -> additive matter drive | Independent physical input/operator currently missing | Is this merely an unknown scalar gain, or an absent source functional? |
| Detector temporal/nonlinear transfer, phase and joint errors | Calibration/independent-data prerequisite | Not supplied by source algebra or a native cavity fit |
| Numerical physical uncertainty and material coefficients | Unknown for proposed comparison | No fit, threshold or physical score until admission |

## 2. Exact driven normal-branch consequence with nonzero coupling

Write d(t)=Phi(t)-Phi_star. The current [matter implementation](../../../core/02_equations/covariant/uet_covariant_matter.py) has

```text
V(chi,d)=m_chi^2*|chi|^2/2+lambda*|chi|^4/4-epsilon*h*d*|chi|^2/2
Z_chi*chi_ddot+[m_chi^2-epsilon*h*d(t)+lambda*|chi|^2]*chi=0.
```

Here chi is the two-component field, not an admitted physical displacement. Natural dimensions: chi,d,h are E; m_chi^2 is E^2; Z_chi,epsilon,lambda are dimensionless; time is E^-1. Every force term has E^3. The homogeneous flat reduction uses Box chi=-chi_ddot; the negative of the production residual is the left side above.

Take constant Z_chi>0, lambda>0 and any finite continuous prescribed d(t), including a nonzero scalar pulse and nonzero epsilon*h. With chi(t0)=chi_dot(t0)=0, chi=0 solves the equation exactly. The first-order state vector (chi,chi_dot) has a vector field locally Lipschitz in the state, so the zero solution is unique on its interval of existence. This is a dynamical implication of the action, not just a zero-coupling member or a finite numerical trajectory. The reciprocal response source is also zero there, so treating d(t) as prescribed is a permissive input check, not a hidden coherent matter force.

A negative instantaneous quadratic coefficient can make nonzero seeds grow parametrically. It does NOT create a deterministic mean from exactly zero initial data. No claim of global stability or absence of variance/thermal response follows. Spatial boundary injection, nonzero prepared coherent initial data, noise, symmetry-breaking backgrounds and an additive drive are different input/state contracts, not outcomes supplied by this zero-initial-data calculation.

More generally, replacing the scalar mass by a time-dependent finite matrix M(t) still gives zero acceleration at chi=chi_dot=0. Directional stiffness modulation is not by itself an additive force. This observation does not implement such a new matrix term in Core.

### Ensemble and detector caveat

The existing force is odd in chi, whereas its backreaction source is even. Paired initial states (chi,chi_dot) and (-chi,-chi_dot) with the same scalar source have paired trajectories and the same Phi history. A sign-symmetric ensemble consequently has zero coherent first moment, while its even variance may be nonzero and respond. A quadratic detector can report an even signal without a nonzero mean displacement. Reuse the existing quadratic-source averaging result; do not infer zero heat, zero occupation, zero fluctuation or zero detector output from this coherent-channel statement. A physical bath or phase-selecting mechanism is not specified here.

## 3. Why a nonzero background is not an automatic rescue of this kernel

At a constant background d_bar, a static v obeys

```text
[mu^2+lambda*|v|^2]*v=0, mu^2=m_chi^2-epsilon*h*d_bar.
```

For the stable normal branch mu^2>0, lambda>0, v=0 is the only homogeneous static solution. A nonzero stationary v requires mu^2=-lambda*|v|^2<0. Its Hessian has longitudinal eigenvalue 2*lambda*|v|^2 and transverse eigenvalue 0 in the exact O(2) model. Linearizing about that prepared background does give a force proportional to epsilon*h*v*delta_d, but changes the state, symmetry and response expansion. It is not the previously derived zero-background mechanical kernel. This is a boundary calculation, not a new condensed-state/He-4 program or an accepted graphite state.

## 4. The missing quantity is a source operator, not just beta or a fit constant

The owner harmonic derivation uses a BOOKKEEPING generalized matter force J_chi. If a physical source were independently admitted, its equation would read

```text
Z_chi*chi_ddot+[m_chi^2-epsilon*h*d+lambda*|chi|^2]*chi=J_chi.
```

This equation identifies the missing input; it is NOT a new implemented action/source. Existing source-only code and the normal-branch kernel do not derive a functional J_chi[laser field, polarization, sample state, time]. Under the CONDITIONAL chart chi_J=beta*Q, the acceleration drive is J_chi,J/(Z_chi*hbar^2*beta), with units m/s^2. A force in newtons further requires the physical mode-mass/projection contract. No beta, source amplitude or mode mass is assigned here. A scale-free kernel test can avoid an absolute Phi anchor, but cannot avoid specifying which conjugate drive and mode it measures.

For any proposed measured trajectory q(t), defining J_required=Z_chi*q_ddot+[m_chi^2-epsilon*h*d+lambda*|q|^2]*q makes the equation true by construction. That inverse residual is not independently known pump input and cannot validate the equation that defines it. Changing parameter values or improving detector calibration does not supply this absent physical source functional.

The existing shear-symmetry result permits a directional optical bilinear paired to an E2g coordinate in a separate physical source description, but leaves its actual coupling/operator unadmitted. Neither scalar intensity nor the mass-source susceptibility determines it. Adding that optical interaction or selecting a symmetry-broken preparation to make the experiment work would be a new physical hypothesis requiring separate approval, not a quiet calibration step.

An independently measured coherent initial seed is another legitimate input to the EXISTING action and need not require a new bulk term or a nonzero stationary background. Its physical mode and preparation-to-initial-state map must still be admitted and separated from the subsequent compared trajectory. A single free ringdown does not become four independent driven-kernel arguments; the existing owner readout result already records that restriction. Thus this wave does not prove a new interaction is unavoidable. It proves that neither the missing drive nor the prepared initial state is supplied by scalar mass modulation alone.

An input API elsewhere is not this missing operator. The normalized [matter-space implementation](../../../core/02_equations/matter_space/uet_matter_space.py) accepts an external C source in its conserved/relaxational first-order dynamics. The [covariant reduction](../../../core/02_equations/covariant/uet_covariant_reduction.py) explicitly requires a constitutive source and does not derive the full C dynamics from chi. Neither API identifies C with this coherent chi displacement or derives a graphite optical pump force. Their existence was checked; they are not declared absent, rerun as a replacement experiment or silently imported into this kernel.

## 5. Frozen test and admission decision

Restricted hypothesis H0: only the declared scalar/mass modulation, exactly zero homogeneous coherent matter initial data, no directional/boundary/additive source and the admitted linear signed displacement readout. Its exact prediction is zero coherent matter displacement for any allowed scalar waveform. A nonzero coherent response outside independently justified initial/readout/source bounds would reject THAT source/preparation hypothesis, not all UET and not the quadratic thermal channel. This is a conditional zero prediction, not a measured test result.

At zero Q1 the ratio Q3/Q1^3 is undefined: the zero-trajectory result is NOT a statement that the intrinsic quartic kernel is zero. The formal response derivative to a hypothetical conjugate J remains meaningful. What is missing is an independently identified physical experiment applying that J, not another algebraic definition of its response function.

No actual source package currently establishes all those preparation and readout conditions. The known graphite coherent-response examples have directional/source questions already recorded; they cannot be scored against an asserted scalar-only protocol merely because the action lacks the pump operator. Non-rejection would not uniquely identify UET, by the existing comparator result.

Before any nonzero-kernel physical test, minimally supply:

1. an independently supported mode/irrep and kinetic chart in the same material state;
2. the physical conjugate drive or preparation mechanism and its mapping to J_chi (including directional dependence and energy/projection accounting), not inferred from the compared Q trace;
3. same-state controlled-drive harmonic records with calibrated signed phase, transfer/processing and joint error/omission bounds.

Input 2 cannot be derived from the present scalar quadratic interaction: its force vanishes at zero chi for every scalar pulse, whereas a nonzero additive directional drive does not. This exact source-level distinction is why more scalar-only simulations, a Phi amplitude calibration, or a native cavity-noise fit cannot fill the gap. No data or physical residual is scored until the source/mode prerequisites are admitted. No new term is proposed as already accepted.

Scope of this result: completes the driven-source distinction for the declared existing normal branch, not a universal no-go, denial of parametric excitation from seeds, graphite falsification, new SI normalization or Full Topic13/Core closure.

## 6. Full goal decision and separately proposed next research

| Goal requirement | Evidence/decision in this same physical path |
| --- | --- |
| Inventory what is derived, assumed, calibrated, independently needed or unknown | Section 1 names the action/kernel as derived and the graphite mode, physical source and measured transfer/error packet separately unadmitted. Prior results reused, not presented as new proofs |
| Build the equation-input-state-observer-output bridge as far as existing equations allow | Sections 2-4 derive the actual mass-modulation force, zero-initial-state dynamics, background boundary, units and conditional Q acceleration conversion. Physical pump-to-J is not derived; the exact zero-force property shows why a nonzero additive source cannot be obtained just by changing a coefficient |
| Separate restricted model falsifiability from unique UET discrimination | Section 5 states a conditional source/preparation falsifier. Existing action/comparator equivalence remains controlling for uniqueness; no new proof of that equivalence or new physical claim |
| Lock hypothesis, observable, parameter/data roles, uncertainties, computation cap and outcomes | H0 and exact zero prediction fixed for normal branch; no physical data or unknown-error threshold adopted. Six scalar settings and 12 implementation comparisons only, with analytic uniqueness proof rather than a trajectory/grid search |
| Execute physical test only when prerequisites pass | Not executed: physical conjugate source, mode and readout/error packet not admitted. Calling the inverse residual a known drive or importing a normalized C source would violate input independence. No private/holdout or new source search used |

The requested stopping outcome **C** is reached for the selected mechanical-normal/graphite-candidate path: the missing input is an independently justified source FUNCTIONAL or preparation-to-initial-state MAP, together with mode projection, not merely an email, detector gain or more scalar simulation samples. The proof specifies what is absent and why the existing force cannot substitute for it. Bounded existing-data/operator alternatives were reused; no different material was substituted. There is no physical UET acceptance or rejection, and no claim that all possible source extensions fail.

**Proposal only, NOT implemented or accepted:** a next research objective could derive and test an external optical-pump-to-conjugate-matter-force interface for the SAME graphite mode/state from an independently supported material model, retaining polarization, carrier/temporal response, source work and detector projection. Its physical mode identification and source functional would be explicit new hypotheses, not a renamed fit constant or an automatic Core action change. The source mechanism must be justified before choosing an instantaneous Raman or other simplified force model. Comparator and uncertainty treatment would remain mandatory.

Approval is needed before developing that physical source hypothesis or changing the preparation/background as a rescue route. No such term is added in this goal. Alternatively an already derived, independently supported same-state source/operator package can reopen the physical test without a new hypothesis. Absent either input, this round ends with the verified prerequisite rather than producing more tests or acquisition activity.

Reproduction: [producer](../Code/03_Research/Research_T13_Mechanical_Source_Bridge.py), [controls](../Code/03_Research/test_t13_mechanical_source_bridge.py), [calculation contract](../calculation_contracts/mechanical_source_bridge.json), [canonical artifact](../../../core/07_artifacts/topic13/t13_mechanical_source_bridge.json). Exact identities/proof are distinct from finite production-code checks; no physical response calculation is authorized by a passing control.
