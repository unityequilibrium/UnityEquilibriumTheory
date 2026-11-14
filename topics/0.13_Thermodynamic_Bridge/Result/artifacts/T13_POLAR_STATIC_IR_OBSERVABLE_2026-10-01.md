# Same-action polar static IR observable and source matching

MAJOR_RESULT_CLOSURE: `T13_POLAR_STATIC_IR_OBSERVABLE_MATCH`, `CLOSED_FOR_LANE` for coordinate/source identities and a conditional leading static Goldstone observable. This is not full microscopic infrared resummation.

WHAT_IS_ACTUALLY_CLOSED: The existing Cartesian O(2) field can be rewritten in amplitude-phase coordinates without changing its action or sources. The Jacobian is necessary. Completing the offshell Cartesian source restores the same Gaussian determinant and thermal derivative. The nonlinear Cartesian longitudinal observable reproduces the previous loop's infrared coefficient while giving a positive conditional susceptibility.

WHAT_REMAINS_OPEN: Renormalized order parameter and joint Phi equilibrium, vacuum/interacting matching, a controlled hydrodynamic remainder, finite-frequency composite/current response and independent physical inputs. Positive conditional susceptibility is not proof that an exact finite-T background exists.

DEPENDENCY_UNLOCKED: Same-action static infrared/observable matching design only. Physical funding gates, recorded Core composition and full Topic13 remain unchanged.

STATUS: `PASS_CONDITIONAL_POLAR_STATIC_IR_OBSERVABLE` in the [artifact](t13_polar_static_ir_observable.json). Its checks control this note.

WHAT_CHANGED: Added the polar action/source verifier, thirteen tests and this derivation. The preceding finite-q loop artifact and original Gaussian stationarity/failed tree-lift results are not overwritten.

EQUATION_OR_MAPPING:

## 1. Coordinates, probe and units

For the existing O(2) matter field, write

```text
varphi=(rho*cos(theta), rho*sin(theta)), rho=A+h>0
x=A^2=Z*r/lambda; r=mu^2-m_eff(Phi)^2/Z
U(rho)=-Z*r*rho^2/2+lambda*rho^4/4.
```

These are not new state variables or a relabeling of Phi/C. Phi remains fixed. R_gen remains a derived trace and R_obs is not inserted in the action. J_l,J_t below are auxiliary Cartesian probes defining the generating functional, not accepted experimental driving inputs.

Rho,h,A,T,mu,q have units E; theta is dimensionless; r,x and phase stiffness have units E^2. Cartesian source J has E^3, susceptibility d(varphi)/dJ has E^-2 and the Cartesian-to-polar Jacobian has E. All examples retain T=0.22, Phi=0.15, Z=lambda=1 and the previously fixed mu/r witnesses. There is no material or SI admission.

## 2. Exact action and measure identity

At fixed Phi the Euclidean Cartesian action density used by the previous Gaussian kernel becomes

```text
L_E=Z/2*[(partial rho)^2+rho^2*(partial theta)^2]
    +i Z mu rho^2 partial_tau theta + U(rho)
    -rho*(J_l*cos(theta)+J_t*sin(theta)).
```

The chemical term and both Cartesian sources are preserved. Direct evaluation at finite fields/derivatives checks the full identity, not just the dispersion.

The measure is `dvarphi_1*dvarphi_2=rho*drho*dtheta`. In h and eta=A*theta it is `(rho/A)*dh*deta`. A source-dependent two-dimensional Gaussian integral in Cartesian coordinates agrees with a separately integrated polar measure; omitting rho gives a different result. That finite-dimensional check is in dimensionless test coordinates and is not a continuum counterterm calculation. A common lattice/regulator supplies a local `-sum log(rho)` term; it cannot be silently discarded.

## 3. Why the zero polar angle Hessian is not a stationary-state certificate

For a constant rho and no source, the exact angular potential is constant even offshell. The Hessian chain rule is

```text
U'_rho=rho*(-Z*r+lambda*rho^2)
H_cart,tt=-Z*r+lambda*rho^2
H_polar,theta_theta=rho^2*H_cart,tt-rho*U'_rho=0.
```

At rho=1.1*A the radial tadpole is nonzero in both fixed witnesses. Thus a massless polar phase cannot, by itself, cure the prior nonstationary-background problem. Simply using the linear Jacobian pullback while dropping the gradient-chain term is also incorrect offshell.

## 4. Source-complete offshell Gaussian and measure cancellation

To generate the Cartesian effective action at an offshell background, the classical Cartesian Legendre source is `J_l=U'_rho`, `J_t=0`. In the polar action its quadratic angular term is `+J_l*rho*theta^2/2`. Consequently

```text
H_polar = [[Z*(nu^2+k^2-r)+3lambda*rho^2, -2Z*mu*rho*nu],
           [2Z*mu*rho*nu, Z*rho^2*(nu^2+k^2)+J_l*rho]]
H_polar = diag(1,rho)^T * H_cartesian * diag(1,rho)
det(H_polar)=rho^2*det(H_cartesian)
(1/2)log det(H_polar)-log(rho)=(1/2)log det(H_cartesian).
```

This holds mode by mode in a common regulator before an ultraviolet integration. It is coordinate-measure matching of the Gaussian term, not a solution of vacuum renormalization or the interacting theory.

The displayed logarithms denote dimensionless reference-normalized quantities:
rho/E_ref, H_cart/E_ref^2 and diag(E_ref^-1,E_ref^-2)*H_polar*diag(E_ref^-1,E_ref^-2).
E_ref=1 is a natural-unit convention, not an SI energy calibration. Changing
that reference preserves the determinant identity and all source derivatives.

At the tree boundary the correct thermal derivative is still

```text
Omega_x=lambda/(2Z)*(3I_sigma+I_pi)>0.
```

Dropping the offshell Cartesian source incorrectly drops `lambda*I_pi/(2Z)` from this derivative. Source-completed logdet finite differences reproduce the original matrix derivative. The prior Gaussian stationarity blocker survives the change of coordinates. This explicitly rules out a coordinate-only shortcut, not all interacting completions.

## 5. Tree dynamic kernel and spatial current

At the tree stationary amplitude, eta=A*theta is the original transverse field to first order. Integrating the quadratic amplitude gives

```text
K_theta,eff=Z*x*[nu^2+k^2+4mu^2*nu^2/(nu^2+k^2+2r)]
rho_s_tree=Z*x
low_energy_time_coefficient=rho_s_tree*(1+2mu^2/r)
c_tree^2=r/(r+2mu^2).
```

The Schur complement and exact tree spectrum agree. This is the scalar lane's tree mode, not physical second sound or a finite-T transport closure.

With an auxiliary spatial connection a, the static density is `rho_s*(grad(theta)-a)^2/2`. Its current is `j_i=-dF/da_i=rho_s*(partial_i theta-a_i)`. At zero Cartesian source, phase variation yields div(j)=0. With the Cartesian probes, div(j)=rho*(J_l*sin(theta)-J_t*cos(theta)). The torque is independently checked by action differentiation; the source term must not be omitted from a Ward comparison.

## 6. Reconstruct the original longitudinal observable

Amplitude modulus and Cartesian longitudinal field are different observables:

```text
varphi_l=A+h-A*theta^2/2+...
G_theta,static_equal_time(k)=T/(rho_s*k^2)
J_00(q)=int d^3k/(2pi)^3/[k^2*(k+q)^2]=1/(8q)
chi_l(q)=chi_h(q)+x*T/(2rho_s^2)*J_00(q)
chi_h_tree(q)=1/[Z*(q^2+2r)]
chi_l(q)=1/[Z*(q^2+2r)]+x*T/(16rho_s^2*q).
```

The factor two is the connected Wick contraction of theta^2; one beta=1/T converts a static equal-time covariance to susceptibility. A separately implemented Gaussian source/logdet derivative checks this normalization to about 5.6e-8 relative. The result is not obtained by picking a denominator to avoid a negative inverse.

Define the longitudinal inverse by its source susceptibility: `Gamma_l/Z=1/(Z*chi_l)`. If the composite term is small, expanding this definition with rho_s=Z*x gives

```text
delta(Gamma_l/Z) ~ -(2r)^2*Z*x*T/(16rho_s^2*q)
                = -lambda*r*T/(4Z^2*q).
```

It is exactly the coefficient independently calculated in the preceding finite-q microscopic bubble. At smaller q the composite susceptibility dominates instead: it is positive and diverges as 1/q, while its inverse is positive and approaches zero linearly. Expanding the inverse in that regime is invalid and produces the negative bare value. This is a conditional explanation of that failure, not a proof of physical instability.

The radial modulus susceptibility alone lacks this composite term. It must not be substituted for the original Cartesian observable or for temperature/EOS response. At q=0.0025, the tree-matched conditional inverse is 0.0180834/0.0743334, despite the bare inverse expansion being negative; these numbers are not material predictions or full-loop estimates.

## 7. Matching limitations

The IR form assumes an ordered long-wavelength state with positive stiffness and q much less than sqrt(2r). Exact IR coefficients require the renormalized order parameter and stiffness, not necessarily the tree amplitude. Inserting the previously derived formal current into rho_s produces a conditional template, not a new microscopic resummation; it is recorded separately and is not selected by target agreement.

No uniform error bound, renormalized amplitude, joint Phi stationarity, vacuum matching or real-frequency composite kernel is established. This does not undo the exact-Gaussian no-go or close G1/G2.

VERIFICATION: Full source/chemical action identity, Jacobian integral and omission witness, offshell Hessian chain rule, source-complete Gaussian/logdet derivative, tree Schur/spectrum, static source-current/torque, independent Gaussian source versus Wick normalization, prior loop coefficient, unit/T0 limits, positive conditional IR behavior and protected hashes are checked by thirteen new tests. The full related suite result is recorded in the update log. No artificial mass, IR filter, clipping, target fit or numeric holdout access occurs.

CONTROLLING_BLOCKER: `microscopic_polar_background_and_dynamical_observable_matching_not_closed`.

NEXT_ACTION: Construct a source-complete renormalized/interacting background or show its scoped obstruction, preserving this common-regulator/source identity. Derive the finite-frequency composite observable/current response and quantify matching error before a real-axis/material comparison. Keep the independent source/protocol work separate.

CLAIM_BOUNDARY: Same-action identities plus a conditional leading static IR observable, not exact finite-T equilibrium, microscopic resummation, temperature prediction, physical Kubo, He-II/graphite validation or global closure. Prior Xie exposure remains review-required; no pristine blinding is asserted.

## Method attribution

[Dupuis 2011, section II.2, equations 30-39](https://arxiv.org/html/1011.3324v2) supplies the standard amplitude-direction method and distinction between modulus and Cartesian longitudinal correlations. Here the chemical/source terms, Z/T normalization, prior-loop coefficient and offshell source/measure equivalence are checked for the declared lane. This method is established physics, not evidence of UET novelty or material validity.
