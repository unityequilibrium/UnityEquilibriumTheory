# Topic 10-13: entropy sources and reference-coordinate contract

Date: 2026-09-30. Role: SOURCE_CANDIDATE_AND_STANDARD_REFERENCE_ONLY.
Physical controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.

## Source progress and lineage

[Source/contract package](Data/03_Research/he4_entropy_source_and_reference_contract.json)
preserves six entropy tokens from [Donnelly-Barenghi 1998](https://srd.nist.gov/jpcrdreprint/1.556028.pdf),
Tables 8.3 and 8.5, printed pages 1244-1245 (PDF pages 29-30). Full pages
1243-1245 were rendered and inspected, including units and Section 8 notes.
These are recommended spline values, not six new raw experiments.

Table 8.3 is a fountain-pressure branch; Table 8.5 is integrated from the
recommended heat capacity. Section 8 note (8) specifies the integral from
0 K, giving an explicit zero-temperature integration convention for Table 8.5.
This does not establish the entropy reference of TN1334 or convert its edition.

The [primary fountain-pressure paper](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.29.4951)
is Singsaas-Ahlers, published 1 May 1984; the review bibliography's 1983
date differs. Publisher metadata, not that bibliography year, controls identity.
Its abstract describes fountain measurements; full protocol and thesis tables
have not been acquired. A different measurement family helps source design,
but independence of the eventual sound target is not established: entropy
also participates in sound-derived superfluid-density inference.

Source precision/accuracy statements are not assigned as row standard deviations
or covariance. The Table 8.5 entropy shares heat-capacity ancestry; it cannot
independently validate that same calorimetry. The SVP path still lacks transverse
fixed-pressure/volume EOS identification.

## F0-F4: ontology, units and derivation before code

This extends only the standard ideal two-fluid comparator in
[TWO_FLUID_STATE_EOS_REFERENCE.md](TWO_FLUID_STATE_EOS_REFERENCE.md).
Material specific entropy s has units J/(kg K), entropy density sigma=rho*s
has J/(m^3 K), and a is a constant specific-entropy reference offset.
It is a coordinate change, not a fitted physical parameter. No UET field is
identified with material entropy, temperature, mass or superfluid phase.

Let starred quantities use s_star=s+a:
~~~text
sigma_star = sigma + a*rho
e_star(rho,sigma_star) = e(rho,sigma_star-a*rho)
T_star=T; mu_star=mu-a*T; p_star=p
A_star=A-2*a*B+a^2*D; B_star=B-a*D; D_star=D
~~~
Here A=e_rhorho, B=e_rhosigma, D=e_sigmasigma and mu is chemical potential
per mass. The unit products a*B and a^2*D match A; a*D matches B; a*T matches
mu. This is a chain-rule derivation from the declared reference EOS, not
microscopic UET origin or physical He-II admission.

For z=(delta_rho,delta_sigma,j,delta_v_s), z_star=L*z with L[1,0]=a
and unit diagonal. Its linearized operator and quadratic availability obey
M_star=L*M*L_inverse, H_star=L_inverse_transpose*H*L_inverse.
The same physical model keeps its characteristic speeds and availability.

A direct flux/force assembly must transform BOTH constitutive relations:
~~~text
sigma_star_t = -div(sigma*v_n+a*j)
             = -div(sigma_star*v_n-a*rho_s*(v_n-v_s))
v_s_t = -grad(delta_mu_star+a*delta_T)
~~~
The coefficients in these fluxes are frozen uniform rest-state values. The
identity j-rho*v_n=-rho_s*(v_n-v_s) uses the original mass current.
Pressure is rho*delta_mu_star+sigma_star*delta_T. At nonlinear order,
additional work/state/transport questions require a separate derivation.

Simply inserting shifted entropy/Hessian into the UNMODIFIED standard
sigma_star*v_n and mu_star equations defines a different model.
It can still have positive quadratic availability and reciprocal flux;
an energy-only PASS therefore does not check entropy-reference correspondence.
The usual entropy-speed term involving s^2 cannot accept an arbitrary
industrial relative entropy without these transport/force changes or an
evidenced conversion back to the physical entropy convention.

[NIST REFPROP 9 manual](https://www.nist.gov/document/refprop9pdf), Section 7.2,
allows thermodynamic reference-state choices. That fact is a convention warning,
not evidence for the TN1334 edition's chosen zero or a measured numerical offset.

## Locked checks and non-acceptance comparison

Before first execution: reuse unchanged normalized base rho=1,rho_s=0.6,
sigma=0.8,T=1,A=9,B=-0.2,D=1.4; offsets [-0.3,0,0.4,1.0];
identity tolerance 1e-10, negative-control floor 1e-8; periodic grid 32.
Compare independently assembled transformed flux/force with matrix similarity,
congruence/work, Gibbs pressure, heat capacities and characteristic roots.
Check explicit local periodic entropy/phase flux balances. Nonzero shifts must
detect omitted entropy correction, omitted phase-force correction and both
omitted; test that the both-omitted model can pass its own work check.
No trajectory, physical speed, calibrated entropy offset or parameter fit runs.
Keep any failure before changing a rule, input or control.

Convert J/(g K) to J/(kg K) by 1000. Compare six source values to prior TN1334
only at matching NOMINAL printed temperatures. Report central differences;
do not accept/reject a physical EOS, infer a constant offset, interpolate
between temperature scales, or use printing resolution as physical uncertainty.
T90 versus TN1334's EPT-76-based adjustment and physical row covariance remain
unresolved. No temperature-error propagation or fitted-reference conversion is
performed.

## Next controlling work

Table 8.5's own integration convention is now explicit. The remaining source
controller is he4_entropy_integration_anchor_found_but_TN1334_reference_transfer_covariance_and_independence_open.
Acquire selected-edition reference evidence or choose a source with an explicit
reference; reconstruct exact calibration/response ancestry and a primary
state/frequency/geometry response protocol. Keep original material requirements
null, Topic 13 constants frozen, J04/J05/J06 unexecuted and all Core gates unchanged.
