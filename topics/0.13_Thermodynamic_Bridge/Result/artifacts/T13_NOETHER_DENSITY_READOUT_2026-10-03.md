# Same-Action Noether Density Readout And Calibration Boundary

MAJOR_RESULT_CLOSURE: T13_NOETHER_DENSITY_READOUT_AND_CALIBRATION_BOUNDARY,
CLOSED_FOR_LANE. Not Full Topic13, G2-G4, R1-R5 or Core-owner acceptance.

WHAT_IS_ACTUALLY_CLOSED: The declared tree action fixes conserved density
source/contact and its projection onto three tree modes. Independent
state-space and spectral calculations check that readout. Constructive
restricted families show which detector/unit inputs remain unidentified,
and a conditional inverse shows how independent inputs remove them.

WHAT_REMAINS_OPEN: Atomic-number-current/state/SI identification, permitted
numeric rows, independent gain and joint resolution, approximation and
interaction control, physical heat/entropy/transport/KMS and alpha_Phi_K.

DEPENDENCY_UNLOCKED: Same-state density measurement/information-gap
research only; no physical/Core/Gravity unlock or owner-gate change.

STATUS: PASS_SCOPED_NOETHER_DENSITY_READOUT. Derived internal evidence,
not physical data admission or a novelty/continuum proof.

WHAT_CHANGED: Topic-local calculation, tests, registry, derived artifact
and protocol screen; linked conditional measurement card and canonical
handoff. Old source-work FAIL and remainder evidence remain unchanged.

EQUATION_OR_MAPPING: delta_n=s*a0+sqrt(s)*(2mu*sigma+dot_pi_phase);
chi_nn=s+j_minus D^-1 j_plus=sum_j Rnn_j/(E_j^2-z^2). Conditional detector
intensity is G_inst*Z_N^2 times resolution-convolved S_Noether, not Phi.

VERIFICATION: Ten scientific checks pass on mu1.05/1.2, q.002/.01/.04
and z=.02i/.05i/.03+.02i. Direct/state-space discrepancy <=1.910e-12;
density and mixed spectral discrepancies <=9.757e-13 and2.920e-12;
charge Ward error <=2.941e-15. The independent-scale inverse recovers all
four constructive kinetic witnesses with relative error <=4.220e-15.
These are numerical identity errors, not experimental uncertainties.
Tests additionally check central charge/uncertainty derivatives, the
contact omission, coordinate covariance, dark decoupled Phi, rejected
inputs, hashes and audit-time Path read allowlist. No original causal rerun.

CONTROLLING_BLOCKER: Noether_to_atomic_density_SI_state_resolution_and_independent_gain_not_admitted.

NEXT_ACTION: Verify the particle-current and same-state action-unit map;
seek permitted primary low-q rows and independent gain/resolution covariance.
As a separate derived question, test whether the next dispersion coefficient
lifts the retained-q3 family with controlled approximation, rather than
assuming U is the only possible additional measurement. Keep physical
heat-source and nonlinear parent obligations separate.

CLAIM_BOUNDARY: Tree Noether readout only; no assigned damping, fitted
scale, quantum Phi loop, KMS structure-factor admission, independent alpha,
physical UET validation or global claim promotion. C is not this charge;
pi_phase is not UET Pi. R_gen/R_obs are not dynamical states. Original
conserved-C FAIL/1e-6 threshold and prior Xie exposure REVIEW_REQUIRED stay.

## Evidence Identity

[Derived artifact](t13_noether_density_readout.json): SHA-256
`2b6688dab3cb55c623fa5c1a43320ef28d65fe82e95b27d6ea1731f9c632ac12`.
[Local registry](../../Data/03_Research/t13_noether_density_readout_registry.json)
and [protocol screen](../../Data/03_Research/t13_density_spectroscopy_protocol_screen.json)
are hashed by the artifact; no Core registry edit.
[Predecessor](t13_gaussian_work_remainder.json):
`0bff6697f0c94f749cbaf2134c3e78ae36de40c66783a7303e8c5f5aadf307b1`.
The earlier density and later unit-family subprotocols were declared before
their respective first audits, not retrospectively before one common run.
The final inverse-family check adds verification without changing thresholds.

## Source, Contact And Conservation

Use the existing rest, h0=0 action and fluctuation order (sigma,pi_phase,Phi).
Let v=sqrt(s), D=V_q-z^2 K+z L, L_sigma,pi=2i mu and
L_pi,sigma=-2i mu. The external chemical-potential drive a0=delta_mu
does not add a state. Its quadratic source terms are

```text
L_source = a0*v*(2mu*sigma+dot_pi_phase) + s*a0^2/2
delta_n = s*a0 + v*(2mu*sigma+dot_pi_phase)
delta_J = -v*grad(pi_phase)
j_plus  = v*(2mu,+iz,0)       Euler source after integration by parts
j_minus = v*(2mu,-iz,0)       density detector
chi_nn = s+j_minus*D^-1*j_plus
chi_nh = j_minus*D^-1*e_Phi
```

The phase equation gives -iz*delta_n+iq*delta_J=0 including the seagull.
At q=0 and nonzero z, chi_nn=chi_nh=0: total charge of the closed system
cannot change. Omitting s incorrectly gives -s, an order-one failure.
This dynamic limit is not grand-canonical static compressibility. The
active (sigma,Phi) static Hessian instead gives

```text
chi_nn(static,q->0) = s+2mu^2/u_eff = P_tree,mumu = d(mu*s)/dmu
```

Independent central differences check the last equality; the two native
susceptibilities are2.34482928366 and3.36983269945, in E^2, not helium SI.
Units: a0:E, n/J:E^3, chi_nn:E^2, h:E^3, Phi:E and chi_nh:E^0.

## What A Density Detector Sees

For positive-energy, signed-normalized same-action mode u_j,

```text
d_j = v*(2mu,-iE_j,0)*u_j = -i*v*q^2*u_pi,j/E_j
Rnn_j = |d_j|^2 >= 0
chi_nn = sum_j Rnn_j/(E_j^2-z^2)
R_nPhi,j = Re(d_j*conjugate(u_Phi,j))
chi_nh = sum_j R_nPhi,j/(E_j^2-z^2)
sum_j Rnn_j = s*q^2
```

The last line is tree completeness in this action, not an admitted physical
helium f-sum rule. The acoustic strength starts as s*q^2; heavier density
strength starts at order q^4. Density spectroscopy sees projected modes,
not the raw Phi-Phi response. At gamma=0 the neutral Phi source is dark.
No extra quantum heavy-mode population or vacuum fill is introduced.

Under the existing Phi coordinate change Phi'=a*Phi, gamma'=gamma/a,
response mass/kinetic'=old/a^2, quartic'=old/a^4 and h'=h/a, chi_nn is
invariant while the h-response column is covariant. This is coordinate
redundancy, not a physical no-go or a measured temperature normalization.

## Restricted Calibration Families And Their Inverses

The [measurement card](T13_DENSITY_SPECTROSCOPY_MEASUREMENT_CARD_2026-10-03.md)
separates two ambiguities. With other inputs known, intensity determines
only G_inst*Z_N^2. The family (G,Z_N)->(G/a^2,a Z_N) preserves it. Log
Jacobian (1,2) has rank1; independent gain adds rank2 and permits a positive
conditional inverse. This is not the minimum measurement set for full UET.

For dispersion through q^3 with native static inputs fixed but action SI
scales open, write physical energy(Q)=A_Q Q+B_Q Q^3+uncontrolled higher terms:

```text
A_Q=E_unit*c/Q_unit
B_Q=E_unit*eta/Q_unit^3
eta=eta_base*(1+s*I_kinetic)
I_kinetic=gamma^2*epsilon*response_kinetic/V_curvature^2
U_unit=E_unit*Q_unit^3     declared volumetric action convention
```

The convention requires action normalization to be established, not merely
calibrated detector axes. A_Q:J*m, B_Q:J*m^3, E_unit:J per native E,
Q_unit:m^-1 per native E, U_unit:J*m^-3 per native E^4; eta/I:E^-2.
The positive constructive family E_unit'=a E_unit, Q_unit'=a Q_unit,
I'=[a^2(1+s I)-1]/s preserves A_Q/B_Q and native pressure, but U'=a^4 U.
It does NOT preserve q^5/full dispersion or already locked physical EOS.
If independent same-state physical U is admitted, this family is excluded.

For parameters (log E_unit,log Q_unit,I) and outputs(log A_Q,log B_Q),
k=s/(1+s I)>0:

```text
J = [[1,-1,0],[1,-3,k]]; null=(1,1,2/k); rank=2
independent log U row=(1,3,0); determinant=-4k; augmented rank=3
Q_unit=(c*U/A_Q)^(1/4); E_unit=A_Q*Q_unit/c
eta=B_Q*c^(3/2)*U^(1/2)*A_Q^(-3/2)
I=(eta/eta_base-1)/s
```

The inverse is conditional on positive declared inputs and the retained
approximation. Negative inferred I rejects the positive-kinetic class;
it is not clipped. Zero SVP pressure or arbitrary vacuum offset cannot
automatically provide U. The full-covariance uncertainty gradient is given
in the card; no practical precision or controlled q^5 error is claimed.
