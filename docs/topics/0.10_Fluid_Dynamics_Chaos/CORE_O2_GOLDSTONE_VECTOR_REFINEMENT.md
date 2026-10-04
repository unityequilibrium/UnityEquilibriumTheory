# Stable Goldstone vector-basis and soft-current refinement

Date: 2026-10-01. Research-core, J01/J02 selected kinetic reference.
Physical controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.
Measured controller before this wave: finite_basis_and_cutoff_current_response_not_converged.
This numerical-method card/contract/registry is recorded before execution.

## Unchanged scientific target
Keep the exact selected cubic event measure, curved tree energies, exploratory
mu=1.28, lambda=.01, T=.002/.004, source-frame constraint and 1% refinement
targets from [the Galerkin card](CORE_O2_GOLDSTONE_GALERKIN_DERIVATION.md).
No fitted collision width, new material, changed interaction or physical gate.
Old raw-polynomial PASS and FAILED basis/cutoff targets remain unchanged.

Refine the vector block that controls the constrained kinetic energy-current.
The prior scalar conservation block remains separately evidenced, not rerun
or silently replaced by this vector refinement. No physical heat-current mapping,
interacting self-energy/additional channels or continuum-gap proof is supplied.

## Shared radial Hilbert space
Write each vector feature F_j(k)=A_j(k)*hat{k}.
For one Cartesian component,
G_jl=integral dk k^2/(6pi^2)*N(1+N)*A_j A_l.
Let G00=integral w*k^2, w=k^2*dk*N(1+N)/(6pi^2), and A0=k.
Use the actual quadrature-weighted inner product; never force Gram=identity.
All A have units E, G E^5, Q E^6, finite rate E, R E^4 and basis-time E^-1.

Family EVEN reproduces the original span A=k*polynomial(k^2/K^2).
Start A0=k and generate each trial by x*A_prev, x=k^2/K^2.
Family SOFT adds bounded angular profiles:
A0=k, first trial A=T, later trials x*A_prev with x=k/K.
Its span contains radial powers0..N-1 with momentum as the first vector.
A~constant at k->0 is not smooth as a vector at the single point k=0,
but its Bose Hilbert norm is finite: w approaches a constant at small k.
This is an admissible variational enrichment, not a claim that the true
distribution has this asymptotic shape or that matter phase/Phi is discontinuous.
No kinetic point at k=0 is sampled.

In both families use full two-pass weighted modified Stieltjes orthogonalization:
trial minus all previous inner-product components, including the second pass.
Normalize each residual to norm G00 with positive beta.
Record all projection/normalization coefficients. Evaluate the SAME recurrence
on every off-grid event leg, without interpolation or event-dependent fitting.
This preserves momentum as A0 and changes neither the collision kernel nor Q.
The exact EVEN order5 coordinate transformation independently checks old raw
G/Q/source and response against the unchanged previous implementation.

## Event form and constrained response
Reuse current rationalized energy/inverse-root functions and the identical-
daughter cubic gain/loss measure. Isotropically integrate
Delta F=A(k)*hatk-A(p)*hatp-A(q)*hatq for the SAME radial functions.
Raw momentum invariant, Gram positivity/conditioning, PSD/null rank,
Bose balance/normalization and event geometry are checked before source reduction.
Source J_i=k_i*a(k), zero-momentum frame and reduced Q-i*omega*G resolvents
remain as in the prior card. Execute linear-current zero separately.

Larger bases are principal subspaces of one shared bank at each cutoff/order.
Check nested variational R growth and basis-independent source/physical units.
SOFT order35 includes EVEN order17's highest radial degree33; its response
cannot be lower than EVEN order17 under the same event integral.
Finite-basis rank or a source-weighted time does not imply a continuum spectral gap.

## Predeclared refinements and independent controls
Gauss parent/daughter orders96/144/192.
Cutoff factors40/50/60 times T/c, retain maximum E_cut/radial_gap<=.1.
Record k_cut/gap as a separate diagnostic; this is still a leading-vertex
approximation, not matched higher-derivative or material transport.
EVEN orders5/9/13/17; SOFT orders5/9/17/25/35.
No new state/coupling or relaxed old acceptance threshold.

Targets: last-order, last-cutoff, last-basis and cross-family current response
differences<=1%, separately; source-representation squared error<=1%.
Structural tolerance1e-8, event1e-9, relative spectral tolerance1e-9,
same-span correspondence1e-8. Retain failed targets and first source/output
if any numerical repair is needed. No absolute eigenvalue cutoff/clipping.

Record enough matrix, recurrence, source and spectrum data to reconstruct the
variational response. Compare coordinate/raw implementation at order5; test
whole-action scale2. Diagnose whether remaining controller is basis, cutoff,
cross-family or physical-current/interacting admission without promoting it.
Next: any failed refinement/soft-current or continuum response obligation,
then matched physical condensate/charge heat current, full interacting thermal
state/channels, nonlinear/live response and material/SI/independent sources.

## Source role
The kinetic current/conservation/polynomial variational correspondence remains
the selected arXiv1407.7431v2 equations10-23 in the prior card. Weighted
orthogonalization and the enriched radial trial space are topic-local numerical
methods, not a new core equation or a transferred neutron-star conductivity.
