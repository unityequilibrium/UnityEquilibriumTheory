# Thermal Parameter Provenance and No-Fit Protocol

## Purpose

This protocol defines what “lock the parameters before comparison” means in the
matter–space thermal lane. It is a provenance and preregistration rule. It does
not mean that unknown parameters may be fitted and then presented as being
derived by UET.

The controlling distinction is:

```text
equation-derived value
    != independently measured input
    != fitted/calibrated value
```

Only the first class can support a parameter-free UET prediction. The second
class supports a conditional comparison. The third class is exploratory
calibration unless it is separated from the test data and reported as such.

## Three parameter classes

### A. Derived by the UET model

A value is `DERIVED` only when it follows from the declared UET equations,
constants, boundary/initial conditions, and a closed unit contract. Examples
include a relation such as

\[
v_\Phi^2 = \frac{M_\Phi\kappa_\Phi}{\tau_\Phi}
\]

provided that the coefficients on the right-hand side are themselves derived
or independently fixed without using the target observations.

The equation can derive a relation without deriving its numerical coefficient.
An unresolved coefficient remains `OPEN`; it must not be silently assigned a
value and called a prediction.

### B. Supplied by an independent source

A value is `EXTERNAL_INPUT` when it is measured, tabulated, or calculated by an
independent method before the UET comparison. The source, units, uncertainty,
locator, preprocessing, and hash must be recorded.

This is scientifically valid input, but the resulting comparison is
conditional on that source. It is not evidence that UET derived the value.

For the graphite TTG lane, grating period, sample temperature, isotope
composition, heat capacity, and independently established material transport
properties may belong to this class when their provenance is complete.

### C. Chosen from the target observations

A value is `FITTED` or `CALIBRATED` when it is selected by minimizing residuals
against the same observations used to judge the model. This is allowed only in
an explicitly labelled exploratory/calibration run. It cannot be used as a
parameter-free prediction or external validation.

Using an observed dip time or observed wave speed to choose \(\tau_\Phi\),
\(M_\Phi\), or \(\kappa_\Phi\) is calibration, even if the choice is made by
matching an algebraic relation rather than by a formal optimizer.

## What “lock before comparison” means

Before a target curve is inspected for model agreement, the run must record:

1. the equation version and unit lane;
2. every coefficient and its provenance class;
3. the derivation or source locator for each non-open value;
4. the initial/boundary conditions and numerical grid;
5. the parameter grid, if the theory leaves a coefficient open;
6. a configuration hash or equivalent immutable run identity.

After this record is created, the target curve may be used for comparison, but
its residual may not be used to select a preferred value in the same claim
run. If a value is changed, the run becomes a new calibration or sensitivity
run and its claim status is downgraded accordingly.

“Locked” therefore means “frozen for this preregistered run”, not “proven by
the data” and not “fitted forever”.

## Current UET thermal lane

The normalized TTG operator can be tested without a Kelvin conversion:

\[
y_{\mathrm{TTG}}(t;\Lambda)
 = \frac{\Delta T_q(t;\Lambda)}{\Delta T_q(0;\Lambda)}.
\]

Under a separately declared linear-response hypothesis,

\[
\Delta T_q = \alpha_{\Phi,K}\,\Delta\Phi,
\qquad
y_{\mathrm{TTG}}^{\mathrm{UET}}
 = \frac{\Delta\Phi(t;\Lambda)}{\Delta\Phi(0;\Lambda)}.
\]

The scale \(\alpha_{\Phi,K}\) cancels in the normalized ratio, but the
proportionality hypothesis does not become derived merely because the scale
cancels. It must be treated as a linearized observable-map assumption until a
thermal closure derives it.

The current normalized UET equation does not contain a Kelvin scale, a heat
capacity, or a temperature-dependent free-energy closure. Consequently:

- the normalized response shape is an eligible `SIMULATION_ONLY` or
  `STRUCTURAL_COMPARISON` target;
- \(\alpha_{\Phi,K}\) is `OPEN`, not fitted in the core lane;
- heat flux and entropy production remain downstream mappings;
- a dimensional agreement in kelvin, W/m², or W/(K·m³) is not currently a UET
  prediction.

## Allowed research paths

### Path 1 — No-fit structural test

Use only equation-derived relations and a preregistered parameter grid. Report
the full grid and sensitivity, not the best curve. The test may ask whether the
equation produces the required causal/damped/oscillatory structure and scaling.

### Path 2 — Independent-input comparison

Use source-locked material properties and initial conditions from an independent
measurement or established calculation. Report the comparison as conditional
on those inputs. Do not claim that UET derived them.

### Path 3 — Calibration study

Fit a declared subset of coefficients to a training subset, then evaluate on a
held-out subset. This is useful for model identification, but it is not the
parameter-free UET test. The holdout must remain untouched while calibration is
performed.

The 2026 graphite source remains a holdout in the current workstream. It must
not be used to choose UET coefficients. The 2022 source remains unavailable as
a local numeric package until its data and provenance are obtained.

## Next controlling derivation

The next equation-level task is not to estimate \(\alpha_{\Phi,K}\) from TTG.
It is to decide whether UET can derive a thermal closure of the form

\[
f=f(C,\Phi,T),
\qquad
s=-\frac{\partial f}{\partial T},
\qquad
e=f+Ts,
\]

with a declared dimensional scale and a measurement operator for \(T_q\).
If that closure cannot be derived from the UET action or an explicitly
independent constitutive input, the dimensional map remains blocked and the
normalized lane must remain the highest allowed claim level.

## Claim boundary

The current status is:

```text
normalized TTG operator       DEFINED
no-fit structural comparison  ALLOWED
Kelvin calibration             OPEN / BLOCKED
heat-flux mapping              BLOCKED
entropy-production mapping     BLOCKED
parameter-free empirical claim NOT ESTABLISHED
```

