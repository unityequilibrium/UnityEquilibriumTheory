# Thermal No-Fit Linearized Dispersion

## Scope

This note derives the first structural prediction of the matter–space response
equation without fitting a thermal curve. It uses the equation coefficients as
declared model inputs and does not assign a Kelvin scale to \(\Phi\).

The result is therefore a normalized, conditional prediction of response
shape, damping, and causal propagation—not a derivation of thermal conductivity
or an empirical validation.

## Expansion point

Take a homogeneous matter background \(C=C_0\) and a homogeneous space-response
equilibrium \(\Phi=\Phi_0\), where

\[
a_\Phi\Phi_0+b_\Phi\Phi_0^3-\frac{g}{2}C_0^2=0.
\]

Write

\[
\Phi=\Phi_0+\delta\Phi,
\qquad
\Pi=\partial_t\delta\Phi.
\]

For a closed lane with no external space drive and to first order in
\(\delta\Phi\), the matter–space equation gives

\[
\tau_\Phi\partial_t^2\delta\Phi+
\partial_t\delta\Phi+
M_\Phi a_{\mathrm{eff}}\delta\Phi-
M_\Phi\kappa_\Phi\nabla^2\delta\Phi=0,
\]

with

\[
a_{\mathrm{eff}}=a_\Phi+3b_\Phi\Phi_0^2.
\]

The coupling \(g\) determines the expansion point through \(\Phi_0\). It does
not create a direct trace-feedback term in this derivation.

## Dispersion relation

For the convention

\[
\delta\Phi\propto e^{i(\mathbf{k}\cdot\mathbf{x}-\omega t)},
\]

the roots satisfy

\[
\tau_\Phi\omega^2+i\omega-
M_\Phi\left(a_{\mathrm{eff}}+\kappa_\Phi k^2\right)=0.
\]

Therefore,

\[
\omega_\pm=
-\frac{i}{2\tau_\Phi}
\pm
\sqrt{
\frac{M_\Phi(a_{\mathrm{eff}}+\kappa_\Phi k^2)}{\tau_\Phi}
 -\frac{1}{4\tau_\Phi^2}}
.
\]

The response is oscillatory only when

\[
4\tau_\Phi M_\Phi
\left(a_{\mathrm{eff}}+\kappa_\Phi k^2\right)>1.
\]

The damping rate in this minimal model is

\[
\Gamma_\Phi=\frac{1}{2\tau_\Phi}.
\]

In the high-wave-number/front-propagation limit, the characteristic speed is

\[
v_{\mathrm{front}}=
\sqrt{\frac{M_\Phi\kappa_\Phi}{\tau_\Phi}}.
\]

This is the equation-derived causal-speed relation. It is not a measured value
and it is not a fitted value. A numerical comparison can use it only after the
coefficient provenance is declared.

## TTG-compatible normalized target

For a grating period \(\Lambda\), the standard spatial wave number is

\[
k=\frac{2\pi}{\Lambda}.
\]

Under the separately stated small-signal map

\[
\Delta T_q=\alpha_{\Phi,K}\Delta\Phi,
\]

the normalized candidate is

\[
y_{\mathrm{TTG}}^{\mathrm{UET}}(t;\Lambda)=
\frac{\Delta\Phi(t;\Lambda)}{\Delta\Phi(0;\Lambda)}.
\]

The unknown scale \(\alpha_{\Phi,K}\) cancels from this ratio. The linear
observable-map assumption does not become a first-principles derivation merely
because the scale cancels; amplitude, heat flux, and entropy still require a
dimensional closure.

## What this does and does not predict

This derivation supplies equation-level structural tests:

- whether a damped oscillatory mode exists;
- how the oscillation threshold depends on \(k\);
- how the damping time depends on \(\tau_\Phi\);
- the causal front-speed relation;
- the dependence of the response on grating period through \(k=2\pi/\Lambda\).

It does not yet supply:

- a numerical value of \(\alpha_{\Phi,K}\);
- a Kelvin-valued temperature signal;
- heat flux \(q\) or conductivity \(k_T\);
- entropy production in SI units;
- a fitted or externally validated UET coefficient set.

## No-fit decision rule

For a prediction run, coefficients must come from the equation derivation or an
independent source before the target curve is inspected. If a coefficient is
unknown, use a preregistered range and report the complete sensitivity envelope.
Selecting the range member that best reproduces the target is a calibration
run, not a no-fit prediction.

## Falsification/repair signals

The structural lane must be reduced or rejected if, after coefficient
provenance and numerical convergence are closed:

- the measured normalized response requires a mode outside the derived
  oscillatory condition;
- the observed arrival scaling cannot be reconciled with the derived causal
  speed without target-data calibration;
- the signal is explained only by adding trace feedback, despite the physical
  dynamics being defined without \(R\);
- the apparent agreement disappears under a preregistered parameter envelope.

