# Same-action thermal source curvature and static matching target

MAJOR_RESULT_CLOSURE: `T13_THERMAL_STATIC_SOURCE_CURVATURE_MATCHING_TARGET`, `CLOSED_FOR_LANE`. Full Topic13/R1/Goal remain open.

WHAT_IS_ACTUALLY_CLOSED: Source derivatives of the tree acoustic energy, the thermal acoustic determinant's source Hessian and a derived static matching target beyond its acoustic pair/population cuts. Background/seagull, kinematic and virtual-polarization contributions are separately calculated.

WHAT_REMAINS_OPEN: Actual dynamic source-contact/virtual-mode and dispersive/local real matching, all-mode quantum/heavy admission, complete thermal sunset/mixed pressure/source/entropy, physical normal/heat/Kubo/SK-KMS and material/readout/scale/uncertainty.

DEPENDENCY_UNLOCKED: Source/contact and virtual-mode matching research only, not physical/Core/Gravity or owner-composition admission.

STATUS: `PASS_SCOPED_THERMAL_SOURCE_CURVATURE`. [Artifact](t13_thermal_source_curvature.json), SHA-256 `b5955d1e8425795da7658ab161dadb6c649e1e03be1ecb113a7b2e3e29bf061e`.

WHAT_CHANGED: Separate [verifier](../../Code/03_Research/Research_T13_Thermal_Source_Curvature.py), tests and [two-entry registry](../../Data/03_Research/t13_thermal_source_curvature_registry.json). The [Landau predecessor](T13_ACOUSTIC_SOURCE_LANDAU_2026-10-03.md), all previous artifacts and original action are unchanged. [First failure](t13_thermal_source_curvature_first_failure.json), SHA-256 `c5a15a30b3b9a2e14218d5b85fdb6e4266db3f7652bf72c7de5438aab9cfe585`, is a historical pre-repair diagnostic, not a current-source rerun certificate.

EQUATION_OR_MAPPING:

## 1. Differentiate the declared stationary source path

Fix mu and T, with the original +h Phi source. For stationary Cartesian
coordinates x0=(r,0,Phi), r=sqrt(s), differentiate the same potential:

```text
V0 x_h=e_Phi                    [radial/response block only]
V0 x_hh=-T_ijk x_h,j x_h,k
D_h,ij=T_ijk x_h,k
D_hh,ij=Q_ijkl x_h,k x_h,l+T_ijk x_hh,k
```

T and Q are the third/fourth potential derivatives, not temperature or new
coefficients. Q_sigma4=Q_phase4=6u, Q_sigma2phase2=2u per permutation,
Q_Phi4=6 epsilon lambda_Phi. The phase direction is gauge-fixed, not
inverted at zero momentum. The active Hessian is positive at the witnesses.
The exact stationary identity u*r^2=X-m0^2+gamma(Phi-Phi_ref) implies
D_h,phase,phase=D_hh,phase,phase=0. It is a derivative along the existing
stationary family, not a mass-repair prescription or new state definition.

Independent h+/-step stationary states check x_h/x_hh and D_h/D_hh.
Source h has E^3, x_h and E_h E^-2, E_hh E^-5; pressure E^4 and chi E^-2.
This natural energy lane is not alpha_Phi_K or SI heat. C, UET Pi, R_gen
and R_obs are not part of the fluctuation/source vector.

## 2. Gyroscopic eigenvalue variation retains polarization response

For the same tree matrix D(E,p)=V0+(p^2-E^2)K+E L and normalized acoustic
polarization u, the predecessor symplectic residue ensures
-u^dagger D_E u=2E. Therefore

```text
E_h=u^dagger D_h u/(2E)
A=D_h+E_h D_E
u_h=-D_perp^-1 A u
E_hh=[u^dagger(D_hh-2 E_h^2 K)u+2 Re(u^dagger A u_h)]/(2E)
```

D_perp inverse excludes the isolated acoustic nullvector. Adding a parallel
normalization/gauge derivative to u_h leaves the expression unchanged
because u^dagger A u=0. This is virtual variation of tree eigenvectors,
not a new prescription for quantum-heavy intermediate-state loops.
The three displayed contributions are background/seagull, kinematic and
virtual polarization. Freezing polarization or the stationary background
acceleration would omit terms from the same-parent source variation.
Independent recomputed tree energies at three h steps check both derivatives.

## 3. Static pressure requires energy curvature, not only populations

The admitted acoustic thermal-difference prescription is

```text
P_th(h)=-T integral d^3p/(2pi)^3 log(1-exp[-E(p,h)/T])
Delta_Phi_th=P_th,h=-integral n E_h
chi_th=P_th,hh=integral [n(1+n) E_h^2/T-n E_hh]
             =chi_population+chi_energy_curvature
```

Only the tree acoustic thermal determinant is included. This is one-loop
thermal-difference source response, not interacting two-loop pressure,
vacuum Wilson matching or all-mode thermodynamic closure. Background
variation follows the tree stationary path, consistently with that order.

The zero-frequency-then-zero-q intrabranch Landau bubble uses
x_h^T V_L(p,p)=u^dagger D_h u=2E E_h. Its static contribution is
chi_population=integral [-n'(E)] E_h^2. This limit does not imply a
nonzero Landau cut at q=0 and omega>0 or commuting static/dynamic limits.

For the two-acoustic pair matrix at q=0, use the static external x_h,
not frequency-dependent source dressing at its tree poles:

```text
delta_R_pair(omega,0)=p^2 n(E)/(16pi E^2 v) V_pair V_pair^dagger
omega=2E(p)
chi_pair_static=2/pi integral d_omega x_h^T delta_R_pair x_h/omega
               =integral d^3p/(2pi)^3 n |u^T D_h u|^2/(4E^3)
required static supplement = chi_pair_static-chi_energy_curvature
```

The last quantity is an obligation to be explained by the actual
source/contact/virtual completion. It is not set as an adjustable contact
coefficient and does not determine frequency dependence from a static
number. The acoustic cut-only truncation is not the full parent response.

At mu=1.05, dropping energy curvature misses about22.93% of chi_th;
including pair instead still differs by3.65-3.66%. At mu=1.2 the respective
fractions are73.11-73.13% and66.38-66.40%. These are normalized diagnostic
fractions at the two declared T grids, not material errors or a global no-go.
All three computed curvature contributions are nonzero. In particular
virtual-polarization response is substantial; extra acoustic damping runs
alone cannot fill this equilibrium matching obligation.

## 4. Numerical cancellation and honest error boundaries

The first audit passed independent source/pressure derivatives but failed
the pointwise vertex identity at tiny p: raw T contraction followed by
x_h projection cancels O(1) phase terms to recover an O(p^2) result.
Binary64 relative errors reached7.551e-4 although integrated quadrature
was already below1.1e-15. The repair contracts D_h after exact stationary
phase cancellation; raw errors remain exposed (up to1.013e-3 in the final
pair/Landau diagnostic). Stable identities are below1.4e-15, with
independent finite-h kernel/state checks. No momentum node, derivative
step, threshold, action parameter or causal boundary changed.

Pressure finite differences use a common fixed p interval and c0 at the
reference state, not an h-dependent integration boundary. Orders24/48/96
and tails32/40 test numerical stability; they are not an infinite-tail,
truncation or physical uncertainty bound. Phi'=a Phi, h'=h/a leaves
P_th invariant and transforms chi by a^2; it supplies no material readout.

VERIFICATION: Six artifact checks, two mu states, T=c*dispersion_scale/256 and /512, momenta.005/.02/.04, source steps1e-4/5e-5/2.5e-5 and fixed grids/gates. Max first-step pressure Hessian discrepancy2.612e-5, finest derivative steps also reported; thermal tail difference4.336e-10 and quadrature below1.1e-15. Tests include independent states/energy/kernel/pressure, curvature decomposition, visible raw cancellation, zero-T/decoupled/coordinate/invalid-domain, protected hashes and audit-time Path read allowlist. Final linked count in UPDATE_LOG. No external validation/model trial or pristine-blinding certificate.

CONTROLLING_BLOCKER: `dynamic_source_contact_virtual_mode_and_full_thermal_matching_open`.

NEXT_ACTION: Derive the actual dynamic source/virtual-mode/contact completion so the static limit returns this independently computed pressure target; do not assign the residual as a constant or fit a pole. Then full real/thermal sunset/source/entropy consistency and independent material/readout/scale. Preserve original7/11 October and Goal/R1-R5 rules.

CLAIM_BOUNDARY: Thermal acoustic static source Hessian and a quantified matching obligation only. Not full retarded real/contact matching, quantum-heavy/all-mode admission, interacting EOS, SK/KMS/Kubo/physical transport, Kelvin/material prediction, original conserved-C repair or Full Topic13/UET/Core promotion. No fit/clipping/padding/filter/threshold/ontology/owner change or Xie numeric read; prior exposure REVIEW_REQUIRED. [Andersen's Bose-gas review](https://arxiv.org/abs/cond-mat/0305138) provides thermal-loop/approximation context, not material coefficients, validation or a controlled expansion parameter for this candidate.
