# Topic 13: reciprocal material/response dynamics

CANDIDATE local quadratic material extension, not an accepted core equation.
This follows the conditional G/r source matching, not a graphite calibration.
The older prescribed-Phi comparator is preserved unchanged.

## Declared thermodynamic and kinetic origin

At fixed reference T>0 use compatible strain eps=B(n)v, q>0, b=B^T beta,
h=B^T G, A=B^T K B. Introduce the explicit free-energy increment

```text
f2=v.A.v/2-theta*b.v-c*theta^2/(2T)
   +phi*h.v+a_q*phi^2/2-r*phi*theta
a_q=a+kappa_phi*q^2
ds=b.v+c*theta/T+r*phi
```

phi is a displacement of the existing response variable, Pi=phi_dot, not a
new substance. Material v,w and optional flux J are declared material states,
not relabelings of C or R_gen. Neither trace appears in the state vector.
All coefficients here are declared TOTAL coefficients of this local lane.
Adding thermal increments to measured material coefficients automatically
would risk double counting and is not implemented.

Use positive kinetic density rho*w.w/(2q^2)+z*Pi^2/2, z>0, and the forces
obtained by differentiating f2 at fixed theta. Linear heat balance is T*ds_dot
=Q-q*J. Damping gamma>=0 and Fourier/Cattaneo k,tau are EXTERNAL constitutive
inputs, not a microscopic SK/KMS match. The reciprocal equations are

```text
v_dot=w
(rho/q^2)*w_dot=-A*v+b*theta-h*phi
c*theta_dot=-T*b.w-T*r*Pi-q*J+Q
phi_dot=Pi
z*Pi_dot=-a_q*phi-h.v+r*theta-gamma*Pi+f
tau*J_dot+J=k*q*theta           (tau>0)
J=k*q*theta                    (tau=0)
```

Q is deposited heat, f a generalized response force. Neither is inferred from
a TTG curve. The initial theta is T*(ds0-b.v0-r*phi0)/c; preparation is still
independent input. The matching calculation supplies CONDITIONAL G/r jointly;
physical pump-to-(ds0,phi0,Pi0,Q,f) is not supplied by this dynamics.

## Positive availability and reciprocal cancellation

The quadratic availability (internal energy minus reference T times entropy)
is f2+theta*ds plus kinetics and a Cattaneo flux storage term:

```text
W=rho*w.w/(2q^2)+v.A.v/2+c*theta^2/(2T)
  +z*Pi^2/2+a_q*phi^2/2+phi*h.v+tau*J^2/(2T*k)
W_dot=theta*Q/T+Pi*f-gamma*Pi^2-J^2/(T*k)   (tau>0)
W_dot=theta*Q/T+Pi*f-gamma*Pi^2-k*q^2*theta^2/T (tau=0)
```

Both b and r cross terms cancel exactly. Removing either r backreaction alone
leaves an unaccounted +/-r*theta*Pi term. There is no r cross term in W because
the Legendre transform cancels it, not because the entropy coupling is absent.
Positive definiteness requires A>0 and a_q-h.A^-1.h>0, besides positive c,rho,z,T
and positive k,tau for the Cattaneo state. An unstable Schur block is rejected,
not repaired by clipping. This is a sufficient modal stability domain, not a
continuum causal-cone theorem. Undamped transverse modes can remain marginal.

The nonnegative quadratic dissipation divided by T is an entropy-production
budget. For Cattaneo the extended entropy includes -tau*J^2/(2*k*T^2).
The linear single-mode system does NOT evolve the second-order uniform heating
or all generated harmonics. Consequently this is a quadratic availability and
linear entropy contract, not a nonlinear total SI first-law closure.

## Independent response elimination

For zero initial conditions and Laplace s, set D=A+rho*s^2*I/q^2 and
H=b.D^-1.h-r. Eliminate mechanical strain and Cattaneo flux:

```text
U=c*s+k*q^2/(1+tau*s)+T*s*b.D^-1.b
V=z*s^2+gamma*s+a_q-h.D^-1.h
[ U   -T*s*H ] [theta] = [Q]
[ H      V   ] [ phi ]   [f]
```

This 2x2 elimination must independently agree with the full state resolvent.
Poles of an eliminated subblock raise an error; no numerical pole padding.
For zero coupling h=r=0 it reduces to the old material dynamics plus an
independent response oscillator. At k=gamma=0 W is conserved. For k>0 a
constant response force gives zero DC temperature in the zero-heat steady
state, not the constrained no-conduction isentropic temperature ratio.

## Units and failure boundary

Natural energy dimensions: v dimensionless; w,theta,phi E; Pi E^2; J,rho,A E^4;
b,h,c E^3; r,a,q^2,k E^2; z,kappa_phi dimensionless; gamma,q,T E;
tau E^-1; f E^3; Q E^5. W E^4 and W_dot E^5. Phi-normalization rescaling
phi'=s_phi*phi requires h,r,f divided by s_phi and a,z,kappa_phi,gamma divided
by s_phi^2; observable theta and W must be invariant.

The underlying physical mass deformation D, field normalization Z, vacuum
subtraction/material identity, dissipation provenance, pump preparation,
detector geometry and uncertainty remain open. No source curve or holdout is
an input. This extends a conditional material ansatz, not the conserved-C
branch, accepted covariant UET action, microscopic KMS or physical heat tensor.
Full graphite/TTG remains blocked; the independently recorded O(2)/He-4 status
is unchanged and not revalidated by this result.
