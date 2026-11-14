# Finite-momentum thermal 1PI and infrared boundary

MAJOR_RESULT_CLOSURE: `T13_FINITE_MOMENTUM_THERMAL_1PI_AND_INFRARED_BOUNDARY`, `CLOSED_FOR_LANE` for the fixed-Phi thermal one-loop difference, contingent on the linked artifact checks.

WHAT_IS_ACTUALLY_CLOSED: The two-by-two finite-external-momentum bubble and upper-half-plane frequency continuation are computed from the existing Cartesian vertices. The static phase-gradient limit agrees with the independently derived current. The full radial bubble approaches a derived `1/q` infrared term, with no discarded zero mode or filter.

WHAT_REMAINS_OPEN: Uniform infrared treatment, matched current vertices at finite frequency, the real-axis limit, joint Phi equilibrium, vacuum/material matching, normal component, independent measurements and a controlled remainder. A finite complex-frequency matrix is not a transport coefficient.

DEPENDENCY_UNLOCKED: Infrared/response completion design in the same lane only. No physical funding gate, Core composition gate, Gravity or full Topic13 unlock.

STATUS: See [machine-readable artifact](t13_finite_momentum_thermal_1pi.json); this note does not supersede its checks.

WHAT_CHANGED: Added a finite-q/frequency verifier, independent tests, artifact and derivation. The original failed tree lift, exact Gaussian stationarity boundary and zero-momentum Ward artifact remain unchanged. The initial dynamic quadrature failed; a logarithmic integration coordinate fixed the soft-mode resolution with the same equations and acceptance threshold.

EQUATION_OR_MAPPING:

## 1. State and normalization

Hold the existing effective response Phi fixed at 0.15. Use the prior natural-unit witnesses T=0.22, mu=1.05/1.20, Z=lambda=1 and r=0.1085/0.446. These are not admitted He-II states. Here Z is the kinetic normalization, not a frequency, and x=A^2=Z*r/lambda is the tree condensate amplitude squared. Cartesian sigma/pi perturbations are the existing O(2) matter coordinates, not Phi, C, R_gen or a newly introduced physical field.

All T, mu, q, k, frequency and A carry E; r, the loop inverse and current stiffness carry E^2. The vertices carry E and pole residues E^-1. No SI mapping is supplied by this calculation. Lambda=1 is not certified weak coupling.

## 2. Matrix propagator and actual vertices

With complex frequency w and a tree background:

```text
K_R(w,k) = [[k^2+2r-w^2,  2i mu w],
            [-2i mu w,    k^2-w^2]]
D(w,k) = (w^2-k^2)(w^2-k^2-2r)-4mu^2 w^2
G_R(w,k) = adj(K_R)/D = sum_p R_p(k)/(w-p)
p = +/- E_low, +/- E_high
R_p = adj(K_R(p,k))/[4p(p^2-k^2-r-2mu^2)]
g=lambda/Z
V_sigma=2gA diag(3,1); V_pi=2gA [[0,1],[1,0]]
```

At w=i nu this is exactly the prior Euclidean matrix, including its off-diagonal signs. The residues are checked against direct matrix inversion, not only against D. The stable product E_low^2*E_high^2=k^2(k^2+2r) avoids gapless-root subtraction error.

## 3. Thermal bubble and continuation

For ell=|k+q| define delta_n(p)=sign(p)*n_B(|p|). The thermal frequency sum minus its zero-temperature integral is

```text
B_ab(w,q) = -1/(2Z) int d^3k/(2pi)^3 sum_(p,u)
            Tr[R_p(k) V_a R_u(ell) V_b]
            *[-(delta_n(p)-delta_n(u))/(w+p-u)].
```

Static coincident poles use the continuous divided-difference limit n_B(E)*(1+n_B(E))/T, not zero. At nonzero imaginary part the real pole differences have no external-frequency singular denominator. This gives an upper-half-plane analytic thermal contribution. At imaginary external frequency 0 and 2pi*T, a separately implemented direct matrix Matsubara sum minus a numerical vacuum-frequency integral checks every matrix entry. Only the derived nu^-4 tail is restored in that frequency check.

The nonzero-frequency sigma/pi mixing is antisymmetric, not symmetric at the same frequency. No averaging is used to erase it. Retarded reality is checked as B(-w*)=B(w)*. Values at w=0.15+0.1i do not supply a real-axis decay width: the imaginary part 0.1 is an evaluation point, not a phenomenological damping input.

## 4. Exact static zero-mode extraction

At internal frequency zero, G_sigma=1/(k^2+2r), G_pi=1/k^2. Let m=sqrt(2r). The all-momentum convolution is

```text
J_ab(q)=int d^3k/(2pi)^3 /[(k^2+a^2)((k+q)^2+b^2)]
       = atan(q/(a+b))/(4pi q)
J_00(q)=1/(8q)
B_sigma,n0(q)=-2g^2*x*T/Z*[9J_mm(q)+J_00(q)]
B_pi,n0(q)=-4g^2*x*T/Z*J_m0(q).
```

An independent Feynman-parameter integral verifies J. Numerically integrate B_thermal minus its exact zero-Matsubara integrand, then add these analytic integrals back. This is an identity, not removing an infrared degree of freedom. The remainder has a power-law ultraviolet tail, so it is integrated to infinity, not terminated at a thermal cutoff. Radial compactification and mapping-scale variation test the all-momentum integration.

Dynamic integration instead uses ell as the angular coordinate, with d(cos theta)=ell*dell/(k*q), then log(ell) to resolve the soft occupation factors. This changes the integration coordinates only. Both versions split the radial integration at k=q; no padding, clipping, mass regulator or nonlocal physical filter is introduced.

## 5. Static-current agreement and formal inverse

Use the already computed one-loop amplitude shift, delta_x=-2Omega_G,x/lambda. The transverse tadpole plus this shift cancels B_pi(0), without a new counterterm:

```text
Gamma_pi(w,q)/Z = q^2-w^2+B_pi(w,q)-B_pi(0)
Gamma_sigma(w,q)/Z = q^2+2r-w^2-4Omega_G,x/Z+B_sigma(w,q)
Gamma_sigma_pi/Z = 2i mu w+B_sigma_pi(w,q)
delta_Z_pi(q)=[B_pi(0,q)-B_pi(0,0)]/q^2
f(q)=Z*(x+delta_x)+Z*x*delta_Z_pi(q)
```

As q decreases, delta_Z_pi matches `(f_held-Z*x)/(Z*x)` from the independent moving-background calculation. At q=0.02, f is 0.0915708223 and 0.4371772631, versus prior currents 0.0915737194 and 0.4371787549. The finite-q deviations are about 3.2e-5 and 3.4e-6 relative; they are not physical uncertainty estimates.

The displayed inverse is an order-matched 1PI expression. It is not inverted into a Dyson-resummed stable propagator, and zeros are not advertised as admitted second-sound poles.

## 6. Why bare amplitude perturbation cannot be continued uniformly

The massless zero mode gives

```text
B_sigma(0,q) ~ -lambda*r*T/(4Z^2*q)
|B_sigma,IR|/(2r) ~ lambda*T/(8Z^2*q)
q_IR=lambda*T/(8Z^2).
```

Full-bubble q refinement at 0.005/0.0025 reproduces the leading coefficient, not only the isolated zero-mode answer. With the fixed witnesses q_IR=0.0275; at q=0.02 the leading correction/tree ratio is 1.375. The unresummed radial inverse becomes negative there. This is an explicit failure of uniform small-correction reasoning, not evidence for physical material instability or a no-go of the full action. Above q_IR, the leading ratio alone is not a rigorous truncation error bound.

The phase-gradient coefficient remains finite in this diagnostic. Therefore the bare amplitude-Hessian divergence must not be relabeled as a divergence of physical second sound or temperature response.

VERIFICATION: 55 focused/related tests pass, including eleven new tests. They check residue matrices, independent finite-frequency sums, coincident Bose limits, exact zero-mode convolution, full infrared refinement, energy-unit and coupling scaling, T=0, static-current agreement, complex-frequency reality and evidence hashes. Static radial/angular orders are 96/48, 144/72, 216/108; dynamic absolute refinement tolerance remains 1e-6. The first linear-cosine dynamic estimate failed and the log-ell coordinate resolved it, without threshold relaxation. Numerical convergence is not control of the loop expansion.

CONTROLLING_BLOCKER: `nonuniform_IR_loop_expansion_and_real_axis_response_not_closed`.

NEXT_ACTION: Test an amplitude-direction/hydrodynamic treatment of the Goldstone composite contribution against this derived 1/q coefficient and finite static current. Require the Cartesian-to-polar observable/Jacobian and current Ward contract, not a hand-added mass or Padé denominator. Then address the real-axis limit and joint Phi/material response. Keep source acquisition independent of this derivation.

CLAIM_BOUNDARY: Natural-unit fixed-Phi thermal one-loop response only. No independent He-II/graphite prediction, exact finite-T equilibrium, physical Kubo coefficient, SI calibration, finite-cone proof or global UET closure. No target fit, holdout read or Core gate overwrite.

## Method context and novelty restraint

[Brauner 2006](https://arxiv.org/abs/hep-ph/0607102) computes propagator/effective-potential loop corrections in a different SU(2)xU(1) model. It is method context, not an identification of that model with this lane.

[Dupuis 2011, sections II.1-II.2](https://arxiv.org/html/1011.3324v2) describes longitudinal Goldstone infrared behavior and an amplitude-direction treatment of the classical O(N) model; the boson sections concern a different, nonrelativistic zero-temperature system. Those results motivate the next calculation but do not establish UET resummation or material admission.

[Brunetti, Fredenhagen and Pinamonti](https://arxiv.org/abs/1911.01829) supplies another relativistic finite-temperature construction using thermal masses and perturbative agreement. That scheme is not implemented here. No cited paper substitutes for the verifier, and reproducing standard loop methods does not establish research novelty by itself.
