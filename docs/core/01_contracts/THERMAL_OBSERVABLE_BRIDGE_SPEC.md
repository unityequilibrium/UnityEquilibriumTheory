# Thermal Observable Bridge for Relational C

Status: `SIMULATION_ONLY` / `INTERNAL_DIAGNOSTIC` / `BLOCKED_OPEN_MAPPING`

## Purpose

This wave tests the missing physical correspondence between a relational path
`C(t,x)` and a thermal observable. It does not identify `C` with temperature or
heat flux. Instead, it declares a temporary synthetic map:

\[
T_{\mathrm{norm}}(t,x)=T_0+\alpha_T C(t,x),
\]

and evaluates standard comparator quantities:

\[
q_F=-k\nabla T,
\qquad
\dot s_F=\frac{q_F^2}{kT^2}\geq0,
\]

alongside the Cattaneo control

\[
\tau_q\partial_tq+q=-k\nabla T.
\]

The gain `alpha_T` is deliberately not inferred from C. It is an open
correspondence parameter. Changing it while holding `C` fixed is a constructive
test that blocks a universal direct `C -> T` identity.

## What is measured in this diagnostic

- `C_path_work`: normalized Rayleigh-type path cost from the prior diagnostic;
- `fourier_entropy_proxy`: integrated standard Fourier entropy-production proxy;
- `cattaneo_entropy_proxy`: the same local proxy applied to delayed Cattaneo flux;
- minimum temperature and source-sign checks;
- numerical Cattaneo-versus-analytic reference residual.

The Cattaneo entropy quantity is explicitly called a proxy here. A complete
nonequilibrium entropy current for a delayed heat flux requires an extended
thermodynamic construction and is not silently asserted by `q^2/(kT^2)` alone.

## Interpretation

If the same `C` path gives the same path cost but different thermal entropy
proxies when `alpha_T` changes, then `C` alone does not identify the thermal
observable amplitude. A physical claim needs an independently derived or
externally measured map for `alpha_T`, plus units, uncertainty, preprocessing,
and holdout policy.

This is a bridge diagnostic, not a derivation of UET thermodynamics, not an SI
prediction, and not external validation of the 0.13 thermal pilot.
