# Infrared trial quadrature: near-collinear floating-point geometry repair

Date: 2026-10-01. Numerical geometry evaluation only, not a new interaction.
The first infrared execution stopped with a non-interior rounded triangle:
124/126 checks, no complete state. Its exact verifier/output are archived.
Orders96/192/384 and all source/refinement tolerances remain unchanged.

## Exact triangle identities
Let k,p>0, q be the curved on-shell daughter and d=q-(k-p)>0.
Heron factors are d,2k+d,2(k-p)+d,2p-d, all momentum dimensionE.
p_z=p-d*(2(k-p)+d)/(2k), p_transverse=sqrt(product factors)/(2k).
Place the soft P directly, then Q=K-P. This avoids subtracting large z components
to recover a soft P and avoids canceling p+q-k to recover an extremely small d.
These are identities for the original geometry, not added angular corrections.

If the rounded d is <=128*machine_epsilon*k, recompute ONLY d with Decimal
precision60 from the same rationalized tree energy and inverse:
B=r+2mu^2 with the binary-float r/mu inputs promoted to Decimal.
The original float B's consistency residual is separately bounded.
Exact binary inputs are used, no material/source parameters are changed.
No triangle clipping, momentum floor, scattering width, population regulator
or event deletion. Every factor must still be strictly positive.
The tiny high-precision d is used only for Cartesian geometry; original
floating q/E/measure occupations and source values remain unchanged and their
independent energy/geometry/detailed-balance checks still apply.

## Audit boundary
Record all high-precision event counts and full old/current function AST hashes.
The full function syntax now differs transparently because geometry changed.
Require identical AST for the physical collision tail from group velocity
through vertex, decay measure, Bose factors and gain/loss matrix accumulation,
and compare unchanged EVEN/SOFT G/Q/source/R at order192 against the immutable
previous artifact at1e-8. Preserve the first exact-source hash and output.

This repairs finite-precision geometry only. It does not improve physical
dispersion, add a channel or prove continuum collision-form domain convergence.
No parameter or1% numerical-response acceptance target is relaxed.
