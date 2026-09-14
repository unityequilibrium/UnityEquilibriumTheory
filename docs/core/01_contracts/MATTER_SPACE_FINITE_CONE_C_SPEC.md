# Matter-Space Finite-Cone C Candidate

## Status

matter_space_finite_cone_c_v1 is an opt-in normalized candidate lane. It is
not the conserved-C baseline, a mass-density identity, a covariant completion,
or an empirical validation.

The current conserved-C lane remains the phase/order comparator. Its changing-C
finite-cone claim is blocked because the conserved gradient term produces an
unbounded high-k characteristic speed.

## Ontology

- C_telegraph_candidate: non-conserved collective system-behaviour/order coordinate.
- C_rate: dC/dt, the response rate of this realization.
- Phi_response: effective space/system response.
- Pi: dPhi/dt.
- R_gen: derived trace computed after the physical step.
- R_obs: detector/observer record, not accepted by this operator.

C is not universally mass, density, charge, force, or energy. A mapping to
rho or n must be declared in a separate lane.

## Candidate equations

\[
\tau_C \partial_t^2 C+\partial_t C=-M_C\mu_C+J_C
\]

\[
\partial_t\Phi=\Pi,\qquad
\tau_\Phi\partial_t\Pi+\Pi=-M_\Phi\mu_\Phi+J_\Phi
\]

\[
\mu_C=a_CC+b_CC^3-\kappa_C\nabla^2C-gC\Phi
\]

\[
\mu_\Phi=a_\Phi\Phi+b_\Phi\Phi^3-\kappa_\Phi\nabla^2\Phi-\frac{g}{2}C^2
\]

The principal candidate speeds are:

\[
v_C=\sqrt{\frac{M_C\kappa_C}{\tau_C}},
\qquad
v_\Phi=\sqrt{\frac{M_\Phi\kappa_\Phi}{\tau_\Phi}}.
\]

The normalized extended energy is:

\[
\mathcal E
=
\Omega+
\frac{\tau_C}{2M_C}\int(\partial_t C)^2dx+
\frac{\tau_\Phi}{2M_\Phi}\int\Pi^2dx.
\]

For the source-free continuum candidate:

\[
\frac{d\mathcal E}{dt}
=
-\int\left[
\frac{(\partial_t C)^2}{M_C}
+
\frac{\Pi^2}{M_\Phi}
\right]dx
\leq0.
\]

The discrete Heun implementation reports ledger residual and does not clip
fields or pad the causal cone.

## Comparators

The conserved branch remains:

\[
\partial_t C=M_C\nabla^2\mu_C+J_C.
\]

A conserved Cattaneo current remains a negative control:

\[
\partial_tC+\nabla\cdot j=0,\qquad
\tau_C\partial_tj+j=-M_C\nabla\mu_C.
\]

With positive kappa_C, its high-k group speed is unbounded unless an
independent UV/nonlocal regularization is derived. It must not be merged with
the finite-cone non-conserved lane.

## Gates

The candidate may advance only after:

- functional directional derivative residual passes the registry threshold;
- ledger closure and non-negative dissipation pass;
- no clipping, hidden stabilization, or parameter fitting is used;
- finite principal speeds are below the declared normalized limit;
- numerical pre-arrival leakage is measured without cone padding;
- normalized-to-dimensional and observable mapping is created;
- physical-data and holdout gates are completed.

Current artifact status is BLOCKED because numerical compact support is not yet
closed. The current allowed claim is:

> candidate normalized finite-cone collective-response lane.

Forbidden claims include C = mass, R_gen as substance, Phi as metric,
and finite speed as proof of photon/neutrino or antimatter conversion.