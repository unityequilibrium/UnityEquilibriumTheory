# Thermal Closure Derivation Audit

## Question

Can the current matter–space equation derive a temperature, heat capacity, or
entropy-production map by itself?

## Result

Not yet. The current `matter_space_coupled_v1` functional is a normalized
effective functional

\[
\widehat\Omega(C,\Phi)
\]

with no explicit temperature argument and no declared dimensional energy-density
scale. It therefore derives chemical-potential-like variational drives and an
effective dissipation ledger, but it does not yet derive a physical Helmholtz
free energy.

If one naively promotes the current normalized functional to a physical
Helmholtz density with temperature-independent coefficients, then

\[
s=-\left(\frac{\partial f}{\partial T}\right)_{C,\Phi}=0.
\]

That is not a usable thermal theory. This is a diagnostic of missing closure,
not a reason to reinterpret the normalized ledger as entropy.

## Minimal conditional thermal closure

The smallest extension that can support a thermodynamic derivative is

\[
f_{\mathrm{th}}(C,\Phi,T)
=
e_0\,\widehat f\bigl(C,\Phi;\vartheta_1(T),\ldots,\vartheta_r(T)\bigr),
\]

where:

- \(e_0\) is a dimensional free-energy-density scale;
- \(\vartheta_i(T)\) are explicitly temperature-dependent coefficients;
- the unit and volume convention for \(e_0\) must be declared;
- the coefficient functions must be derived or independently source-locked;
- assigning \(\vartheta_i(T)\) from the target TTG curve is calibration, not
  derivation.

Under this closure,

\[
s(C,\Phi,T)
=
-e_0\sum_i
\frac{\partial\widehat f}{\partial\vartheta_i}
\frac{d\vartheta_i}{dT}.
\]

The current normalized equation does not provide \(e_0\) or the functions
\(\vartheta_i(T)\). They therefore remain open until an additional physical
closure is supplied.

## Local-equilibrium map from the space-response equation

For the minimal matter–space potential, let only \(a_\Phi\) depend on
temperature:

\[
a_\Phi=a_\Phi(T).
\]

For homogeneous fixed \(C=C_0\), local equilibrium satisfies

\[
F_\Phi(T,\Phi)
=a_\Phi(T)\Phi+b_\Phi\Phi^3-
\frac{g}{2}C_0^2=0.
\]

At a regular equilibrium \((T_0,\Phi_0)\), implicit differentiation gives

\[
\left(a_\Phi(T_0)+3b_\Phi\Phi_0^2\right)\delta\Phi
+a_\Phi'(T_0)\Phi_0\,\delta T=0,
\]

so the conditional local-equilibrium response is

\[
\delta T
=
\alpha_{\Phi,K}^{\mathrm{eq}}\,\delta\Phi,
\qquad
\alpha_{\Phi,K}^{\mathrm{eq}}
=-
\frac{a_\Phi(T_0)+3b_\Phi\Phi_0^2}
{a_\Phi'(T_0)\Phi_0}.
\]

If \(C\) is also perturbed, the first-order relation becomes

\[
\delta T
=-
\frac{
\left(a_\Phi+3b_\Phi\Phi_0^2\right)\delta\Phi
-gC_0\delta C
}
{a_\Phi'(T_0)\Phi_0}.
\]

These expressions are useful because they show exactly what would be needed to
derive `alpha_Phi_K`. They are not a completed UET prediction: they require
the new temperature-dependent coefficient \(a_\Phi(T)\), its derivative, a
regular nonzero \(\Phi_0\), and a physical unit contract.

## Singular and limiting cases

The local-equilibrium map must be blocked or replaced when:

- \(a_\Phi'(T_0)=0\): the equation has no first-order temperature response;
- \(\Phi_0=0\): the displayed inverse map is singular and a higher-order or
  different observable map is required;
- \(a_\Phi+3b_\Phi\Phi_0^2\leq0\): the local branch is not a stable minimum;
- the perturbation is outside the local-equilibrium regime: TTG dynamics then
  require a nonequilibrium kinetic/transport closure, not this algebraic map.

## What the current ledger means

The current ledger contains a normalized effective-energy change and a
non-negative dissipation density. It can support statements such as

\[
\frac{d\mathcal E}{dt}\leq0
\]

for the declared closed normalized lane. It does not by itself establish

\[
\dot{s}_{\mathrm{prod}}=\frac{\sigma}{T}
\]

because both the physical energy scale and the temperature field are still
missing. Thus `sigma` is currently an effective dissipation observable, not SI
entropy production.

## Decision

The current equation can proceed on the normalized structural lane. The
dimensional thermal lane remains blocked until one of the following is supplied:

1. a UET derivation of \(e_0\) and the temperature dependence of the functional;
2. an independent, source-locked constitutive closure for those quantities;
3. a clearly labelled calibration study separated from prediction and holdout
   evaluation.

No `alpha_Phi_K` value is fitted or inserted by this audit.

