# Matter-to-Interaction Forward Mapping

Status: `INTERNAL_CHECKED_COMPARATOR` / `SIMULATION_ONLY`

## Purpose

This package fixes the direction of the first mass-related correspondence without
redefining `C` as mass:

\[
S_m=(\rho_b,\mathcal G,m_A,m_B)
\;\longrightarrow\;
\left(\rho_{\mathrm{obs}},C_{AB}\right)
\;\longrightarrow\;
U_N(C_{AB};m_A,m_B)
\;\longrightarrow\;
\mathbf F_N
\;\longrightarrow\;
\mathbf a_N.
\]

Here `S_m` is an independently declared matter source and `\mathcal G` is the
two-body geometry.  In the current lane, `C_AB` is a dimensionless geometry-only
relational coordinate:

\[
C_{AB}=-\frac{r_{\mathrm{ref}}}{r},
\qquad
U_N=-\frac{Gm_Am_B}{r}=U_0C_{AB}.
\]

The important result is directional.  The source masses control density and
interaction amplitude, while geometry controls the normalized `C` coordinate.  The
forward map is therefore allowed; the inverse shortcut `rho=f(C)` is not identified
by this lane.

## What this does and does not say

- `C` remains an abstract relational coordinate with a lane-specific physical map.
- `m_A` and `m_B` are independent standard counterpart parameters.
- The Gaussian density is a declared synthetic observable definition, not a UET
  derivation or an SI measurement operator.
- The force and acceleration are standard Newtonian comparator relations.
- No additional UET force, mass generation law, or galaxy model is implemented.
- A future extra response must be written as an explicit constitutive law, for
  example `Delta F_U = K[C,rho;theta]`, and must pass a separate F0-F8 wave.

## Verification gates

The deterministic verifier checks:

1. density integrates to the independently supplied source mass;
2. common mass rescaling leaves geometry-only `C` unchanged;
3. density amplitude scales linearly with source mass;
4. pair potential and force amplitude scale as `m_A*m_B`;
5. acceleration of A scales with the companion mass `m_B`;
6. `U(C)` reconstructs the standard pair potential;
7. the extra UET response remains explicitly blocked because no constitutive law
   has been declared.

All quantities are normalized code units.  The result is an internal comparator,
not a mass derivation, dimensional prediction, empirical fit, or galaxy validation.

## Next research question

The next scientifically meaningful question is not “can `C` become mass?” but:

> Given an independently measured matter source, does a separately declared UET
> interaction/response law predict an observable residual beyond the standard
> counterpart, with parameters fixed before holdout testing?

That question is blocked until the constitutive law, units, observable operator,
and uncertainty policy are specified.
