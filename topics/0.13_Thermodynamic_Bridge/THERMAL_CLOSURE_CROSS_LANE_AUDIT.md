# Thermal Closure Cross-Lane Audit

## Finding

The repository does contain temperature-dependent coefficient formulas, but
none currently closes the thermal map for the matter–space response variable
\(\Phi\).

The important distinction is:

```text
a_C(T) for a phase-transition/order-parameter comparator
    !=
a_Phi(T) for the matter-space response
```

Moving the first relation into the second lane would be a new modeling
assumption, not a derivation from the current UET equation.

## Existing temperature-dependent relation

Topic `0.11_Phase_Transitions` uses the normalized comparator

\[
a_C(T)=a_0\frac{T-T_c}{T_c}
\]

in its synthetic Ginzburg–Landau/TDGL scaling scripts. The local implementation
uses normalized \(T_c=1\), dimensionless coefficients, and a phase/order
variable in the `C` lane. Its purpose is a phase-transition benchmark and
diagnostic, not a Kelvin-valued thermal closure for \(\Phi\).

This relation can be used for a controlled normalized comparator only if the
lane is named explicitly:

```text
normalized C/order-parameter comparator
```

It cannot currently be promoted to:

```text
derived temperature dependence of the space-response field Phi
```

## Existing O(2) lane

The finite-density O(2) EOS is a tree-level, natural-unit, zero-temperature
condensate derivation. Its contract explicitly records:

- finite-temperature normal component: `NOT_DERIVED`;
- transport coefficients: `NOT_DERIVED_FROM_CONSERVATIVE_ACTION`;
- gradient coefficient: `OPEN_GRADIENT_EFT_MATCHING`.

Therefore the O(2) work does not currently supply the missing \(a_\Phi(T)\),
heat capacity, or dimensional \(\Phi\)-to-temperature map.

## Existing dimensionless temperature proxy

Topic `0.13` also contains a local relation derived from a topic entropy proxy,

\[
T_{\mathrm{proxy}}=\frac{1}{\ln(1+N/E)}.
\]

This is useful for the engine's normalized equilibration diagnostics. It is not
Kelvin temperature, is not derived from the matter–space functional, and has no
accepted map to \(\Phi\), \(C\), \(\Pi\), or the TTG quasi-temperature.

## Cross-lane decision matrix

| Existing relation | Native variable | Unit lane | Derivation class | Can supply \(a_\Phi(T)\)? |
| :-- | :-- | :-- | :-- | :-- |
| \(a_0(T-T_c)/T_c\) | phase/order field \(C\) | normalized | standard GL comparator in synthetic 0.11 lane | no; comparator only |
| O(2) \(p(\mu,\Phi)\) | Noether charge condensate | natural units | tree-level equilibrium EOS | no; finite-T layer deferred |
| \(1/\ln(1+N/E)\) | engine proxy variables \(E,N\) | dimensionless | derivative of topic entropy proxy | no; no \(\Phi\) map |
| proposed \(a_\Phi(T)\) | space-response \(\Phi\) | not closed | conditional closure only | open |

## What can be reused safely

The 0.11 law can be used as a deliberately labelled normalized sensitivity
case:

\[
a_\Phi^{\mathrm{cmp}}(\hat T)=a_0(\hat T-1),
\qquad \hat T=T/T_c,
\]

but its status must remain `COMPARATOR_ONLY`. It can test whether the
linearized matter–space equation responds sensibly when a temperature-like
control is supplied. It cannot establish that the physical space response has
that temperature dependence.

For a true UET closure, the next relation must instead be obtained from an
action, an equation of state, or an independently source-locked constitutive
law that explicitly connects \(T\) to \(\Phi\) or to the physical energy/entropy
variables.

## Controlling conclusion

The previous blocker becomes more precise:

```text
temperature-dependent formulas exist in adjacent lanes,
but no accepted cross-lane correspondence derives a_Phi(T)
for the matter-space response.
```

The normalized TTG structural lane can proceed with the 0.11 relation only as
a declared comparator. The dimensional thermal lane remains blocked, and no
parameter-free UET prediction is created by reusing the comparator.

