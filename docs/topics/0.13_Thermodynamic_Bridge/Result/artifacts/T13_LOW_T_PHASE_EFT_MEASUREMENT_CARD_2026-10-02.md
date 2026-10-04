# Conditional dispersion measurement: independent kinetic information

MAJOR_RESULT_CLOSURE: Measurement design component of `T13_TREE_MATCHED_LOW_T_PHASE_THERMODYNAMIC_PRESCRIPTION`, `CLOSED_FOR_LANE` only in the declared single-unknown natural-unit class.

WHAT_IS_ACTUALLY_CLOSED: Tree rest EOS and leading T4 phonon pressure do not determine the invariant kinetic response combination. One resolved q-cubed acoustic dispersion coefficient is locally sufficient in the restricted class with all other inputs fixed. This is a constructive/analytic design, not acquired measurement data.

WHAT_REMAINS_OPEN: Material/state admission, independent action coefficients/normalization/temperature scale, source/detector and covariance, q5/interaction/Wilson errors and actual instrument feasibility. Global/full-parameter minimum measurement count and funding scientific acceptance remain open.

DEPENDENCY_UNLOCKED: Independent source/request-packet and theory error-budget research only. No empirical/full-Core unlock.

STATUS: CONDITIONAL_NATURAL_UNIT_MEASUREMENT_DESIGN_NOT_LAB_FEASIBILITY.

WHAT_CHANGED: A specific additional observable replaces a generic request for more data. [Evidence](t13_low_T_phase_eft.json) SHA-256 `050aceb4f94f3534929d8c59c75da4dda8efe16ce7aec250a34f6f8b5868dcb7`; this card uses its declared kinetic and coordinate controls.

EQUATION_OR_MAPPING:

## Question and model class

Can the same static calibration and leading thermal pressure determine the
first dispersive correction of the phase response? In this tree-matched
class, no: Z_Phi is absent from P0(X,h) and A4 but present in eta.

```text
eta_base=(1-c^2)^2/[2c*(A0+4mu^2)]
eta=eta_base*(1+s*I_kinetic)
I_kinetic=gamma^2*epsilon*Z_Phi/(V'')^2
I_kinetic=(eta/eta_base-1)/s
```

Static/leading-T4 sensitivity to this single unknown has rank zero.
Adding eta has rank one because partial_I eta=s*eta_base>0 on the condensed
stable branch. This is an analytic scalar inverse, not an SVD claim about
all UET parameters. If normalized gamma,V'',s are separately known and
gamma is nonzero, Z_Phi can then be inferred. If gamma=0, eta contains no
information about Z_Phi. Pure Phi coordinate rescaling preserves eta and
I_kinetic; it is not the physical ambiguity.

## Observable, source and readout

Proposed observable: real acoustic frequency omega(q) at independently
known wavevector, in the admitted low-T/rest-frame stable state. A
source-coupled phase/current response must establish which measured peak
is the same mode; a generic TTG transient is not automatically this
observable. Use several q values to separate c, eta and the q5 remainder,
not one peak with an assumed exact c. The numerical q grid in the verifier
is not an instrument specification or permissioned experimental source.

Role of future data: independent kinetic CALIBRATION, not a holdout score.
Lock coefficient estimates and covariance before any separate prediction.
No Xie 2026 or previously exposed He-II rows are used or designated blind.

## Precision and uncertainty

For a prescribed desired normalized Z_Phi uncertainty, with all other
inputs independently fixed,

```text
sigma_eta <= abs(partial_Z_Phi eta)*desired_sigma_Z_Phi
partial_Z_Phi eta=eta_base*s*gamma^2*epsilon/(V'')^2
```

The slopes in the two trial states are .001548446965/.001871119131 E^-2
per dimensionless Z_Phi. These are derived sensitivities, not achievable
measurement precision. Propagate the full covariance of mu, source/phase
normalization, gamma, V'', s, c and eta plus detector/frequency/q and
controlled theory remainders. Unknown correlations must remain unknown or
bounded, not be replaced by fictitious independent Gaussian errors.

The tested .5 versus 2 kinetic witnesses differ by 1.5 times those slopes.
At q=.002 E the leading fractional frequency difference is only about
4.4e-8/3.1e-8 in the two natural trial states. This warns that an apparently
invertible coefficient may be hard to measure; no claim of lab practicality
or physical SI precision is made. A source/detector/material owner must
check resolvable q range, damping, background modes and signal/noise before
contacting an instrument facility or budgeting a measurement.

The T6 pressure coefficient is an alternative source of the same dispersive
information, but only with independent temperature/unit and nuisance-input
calibration and controlled subleading terms. Measuring a tiny T6 residual
does not identify the coefficient simply because a fitted curve looks good.

## Required input packet before empirical work

| Item | Required evidence | Present status |
| --- | --- | --- |
| Material/state and normal rest frame | Matching to this EFT, admitted source/thermal protocol | OPEN |
| Other action/normalization inputs | Independent values and covariance, not target-fit | TRIAL INPUTS ONLY |
| Dispersion source/detector | Current/phase coupling, readout transfer and peak identity | OPEN |
| Numeric rows and rights | Primary locator, row identity, units, preprocessing, uncertainty and hash | NOT ACQUIRED |
| Theory precision | q5, Wilson/vacuum and interaction remainder at selected state | OPEN |
| Instrument/time/cost | Human-reviewed feasibility and actual quote/access | UNKNOWN |

VERIFICATION: Constructive .5/1/2 kinetic family keeps P0/c/A4 fixed, changes eta, preserves positive-energy parent checks. Coordinate .5/2 rescaling leaves observables invariant. Independent polynomial/first-order parent, inverse coefficient and gamma=0 controls are in the EFT regression suite. No data acquisition or empirical precision audit ran.

CONTROLLING_BLOCKER: physical_source_detector_and_remainder_for_dispersion_measurement_not_admitted.

NEXT_ACTION: Complete the EFT error budget first and screen one protocol/material against these requirements. Request only missing calibration/readout/uncertainty evidence; don't infer a physical kinetic value or Kelvin scale from the trial witnesses.

CLAIM_BOUNDARY: Locally sufficient extra information for one invariant kinetic combination in a specified natural-unit EFT. Not a global identifiability proof, minimum measurements for Full UET, demonstrated instrument feasibility, independent alpha_Phi_K, TTG source package, material prediction or external validation. No holdout fitting/access, normalization relabel or physical/Core unlock.
