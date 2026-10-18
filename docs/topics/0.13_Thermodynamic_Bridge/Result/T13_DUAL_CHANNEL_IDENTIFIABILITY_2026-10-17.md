# Two channels: when independent control adds a prediction

Status: FORMAL_CONDITIONAL, not a physical material correspondence or UET validation.
Owner: Topic13. Question/controller: independent two-channel parameter identification vs passive slaving and unknown gains. Prior [screen](../MEASUREMENT_REQUIREMENTS_AND_TESTBED_SCREEN_2026-10-17.md) and [single-channel result](T13_OBSERVER_DISCRIMINATION_2026-10-17.md) are reused, not rerun.

## Frozen scope and finite verification

Compare one generic two-coordinate conservative interaction to the inherited local scalar/matter monomial; do not alter Core or call a beam coordinate Phi. Derive exact equivalence/identification conditions, then check one rational fixture with two calibration controls and one reserved synthetic control, plus degeneracy/domain controls. No trajectories, parameter search, measured rows, network acquisition or physical tolerances. Formal completion requires both a constructive negative example and a positive independent-control inverse; numerical rank alone is insufficient.

## What matches the existing action, and what does not

Canonical [uet_covariant_matter.py](../../../core/02_equations/covariant/uet_covariant_matter.py), `interaction_energy_density` and `reciprocal_interaction_derivatives`, defines the existing natural-unit interaction as `-epsilon*h*delta_phi*(chi_1^2+chi_2^2)/2`. Restricted to the inherited one-component, normal-background lane this has the q-squared-times-response structure. The known matter and response self-potentials, kinetic normalizations, spatial terms and full field interpretation remain part of the parent model.

The ordinary two-mode comparator in [the source screen](../MEASUREMENT_REQUIREMENTS_AND_TESTBED_SCREEN_2026-10-17.md) has the same possible monomial order. This does NOT supply a finite-mode projection, mode mass Gram, SI conversion, damping reduction, source matching, detector matching or bounds on omitted terms. In particular its dissipative driven resonance model is not automatically the conservative UET lane. No numerical equality between its coupling and epsilon*h is admitted.

For the conditional analysis only, define physical-coordinate comparator variables q,r [m], positive modal masses mq,mr [kg], and

```text
V_int = kappa*q^2*r
q_ddot + wq^2*q + lambda*q^3 + alpha*q*r = Fq/mq
r_ddot + wr^2*r + beta*q^2 = Fr/mr
alpha = 2*kappa/mq; beta = kappa/mr.
```

This follows by differentiating this explicitly stated comparator potential, not adding a UET term. [kappa]=kg m^-1 s^-2, [alpha]=[beta]=m^-1 s^-2, [lambda]=m^-2 s^-2. A physical reduction would need independent omission bounds for auxiliary self-nonlinearity, other modes and damping; none are established here. Frequency squares are in s^-2; this static control design is not a new four-frequency kernel experiment.

## Gain-aware observation equations

After independently established equilibrium offsets, phase/time alignment and a justified instantaneous real linear readout, let y=Gq*q and z=Gr*r, with nonzero signed gains. Define independently calibrated source readouts sq=Gq*Fq/mq and sr=Gr*Fr/mr, then

```text
Rq = sq-y_ddot-wq^2*y = ell*y^3 + a*y*z
Rr = sr-z_ddot-wr^2*z = b*y^2
ell=lambda/Gq^2; a=alpha/Gr; b=beta*Gr/Gq^2.
```

Rq/Rr cannot be constructed by fitting arbitrary unmeasured forces to the target. Source-to-readout acceleration transfer must be independently calibrated, possibly directly in instrument units, rather than assumed from an unknown absolute displacement gain. Backgrounds, finite bandwidth, clock drift and complex frequency-dependent phase require their own operator treatment and uncertainty; this scalar algebra does not remove them.

For output units [y]=U, [z]=V: [ell]=U^-2 s^-2, [a]=V^-1 s^-2, [b]=V U^-2 s^-2, [Rq]=U s^-2 and [Rr]=V s^-2. The instrument coefficients are not SI Phi amplitudes or predicted constants.

## Negative result: two passive static channels can still be insufficient

With Fr=0, static stable auxiliary response wr^2>0 gives

```text
z = -b*y^2/wr^2
Rq = (ell-a*b/wr^2)*y^3.
```

Even if z is measured and b inferred, replacing `a -> a+t` and `ell -> ell+t*b/wr^2` leaves BOTH channels and the full static source-response curve unchanged for every y. Thus passive static dual readout cannot independently test the two couplings and self-nonlinearity when ell is unknown. This is a constructive global ambiguity, not a count of unknowns. It applies to this passive-static protocol, not every dynamic dual-channel experiment.

Assuming reciprocity to solve for a would allow inference conditional on that assumption, but would not independently test reciprocity with the same data. An independently known ell or informative transient/frequency response could remove the particular collinearity too; this result does not exclude those protocols.

## Positive result: independent auxiliary control can break that ambiguity

For two calibration conditions with independently known source residuals, rows `(y_i^3, y_i*z_i)` must have determinant

```text
Delta = y1^3*y2*z2 - y2^3*y1*z1 != 0.
```

Cramer's rule then uniquely fixes ell and a, and a nonzero-y auxiliary residual fixes b=Rr/y^2. One design is to hold the same nonzero y while using an independently characterized auxiliary force to establish two different z values. That is an added experimental capability, NOT a capability proven available in the screened arch device. In dynamics, well-conditioned independent regressors could serve the same role; unknown forces or omitted dynamics would invalidate the inverse.

Freeze ell,a,b after these separate calibration conditions. A third source/control point is then an overidentifying prediction; do not refit at that point. The verifier's third point is generated from the same comparator and is a synthetic method check, not independent experimental validation. Finite-noise implementation must bound source/readout/derivative errors and distance from Delta=0; an exact nonzero determinant is not a claimed laboratory precision.

## What is needed to test reciprocal coupling independently

The common potential imposes mq*alpha=2*mr*beta. In observed coefficients this becomes

```text
mq*a*(Gr/Gq)^2 - 2*mr*b = 0.
```

Independent modal masses and relative gain Gr/Gq suffice for this particular check; separate absolute gains are not required. Their calibration must not be chosen from the a/b values under test. For nonzero same-sign a,b, an unconstrained relative gain can always satisfy the relation by choosing `(Gr/Gq)^2=2*mr*b/(mq*a)`. Thus two sensors with unknown relative gain do not establish reciprocal physics. Under this declared real constant-gain positive-mass model, opposite signs cannot be rescued by a real relative gain; a zero/nonzero pair is also incompatible with a single nonzero coupling. Complex transfer, lag, omitted force terms or uncertain signs must first be resolved before applying these restrictions physically.

This is a conservative two-mode consistency condition, also predicted by ordinary mechanics with the same interaction. Passing it cannot distinguish a universal Phi field from an ordinary material mode. Calibrated parameter combinations may still make a useful testable effective model; claiming a new mechanism requires an independently constrained additional difference, not a new fitted term.

## Decision and next prerequisite

The alternative platform is **conditionally useful for an effective-model test** if independent auxiliary control or an equivalent independent constraint, calibrated source transfer, modal masses/relative detector gain, material/operator matching and an error budget are supplied. Passive two-channel equilibrium measurements alone are not enough. No inspected package has been admitted as supplying all these prerequisites.

Stop the automatic progression to data fitting here: no physical action-to-material map or complete independent-control record has been established. Do not build a device, contact authors, download the 3:1 archive, rerun old fits or enlarge the UET action automatically. The new concrete input is a named same-state two-channel protocol with independent source/relative-gain/mass calibration and either noncollinear controls or independently known self-nonlinearity, followed by an operator review. Alternatively a separately authorized theory wave must produce a distinguishing relation already constrained by the theory.

## Reproduction and evidence

- [Contract](../calculation_contracts/dual_channel_identifiability.json)
- [Exact producer](../Code/03_Research/Research_T13_Dual_Channel_Identifiability.py)
- [Regression controls](../Code/03_Research/test_t13_dual_channel_identifiability.py)
- [Generated decision](../../../core/07_artifacts/topic13/t13_dual_channel_identifiability.json)

Run `python -B -m unittest discover -s docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research -p test_t13_dual_channel_identifiability.py -v`, then the producer with `--check`. Only `--emit` writes the one compact canonical record. Exact rational arithmetic eliminates roundoff for these controls, not model or measurement error. The calculation contract remains INCOMPLETE for physical correspondence; no physics gate is promoted.
