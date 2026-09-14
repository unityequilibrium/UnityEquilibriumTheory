# Topic 13: interlayer mode shape and material displacement residue

This is a source-derived harmonic material diagnostic. It does not identify
the UET matter doublet or Phi with a phonon by matching a frequency.

## Source and declared screening

The old MP48 payload stores frequencies and mode capacities, not eigenvectors.
Reconstruct eigenvectors from the existing source-locked second-order force
constants and primitive structure. Do not refit, rescale the cell, symmetrize
the force constants again, or shift an eigenfrequency to the Raman value.
Use the source frequency conversion factor; expose the installed Phonopy
factor separately. Retain signed roundoff acoustic frequencies.

Predeclared diagnostic path: Gamma and fractional q along (1,0,0) and (0,0,1)
with coordinates +/-0.005, +/-0.01, +/-0.02. Select the two modes of largest
relative-layer shear projection, NOT the closest frequencies to Raman.
Require at least 0.98 minimum eigenvalue of the two-mode overlap matrix and
1e-5 THz isolation from other modes on this path for a resolved diagnostic.
These are new mode-identification tolerances, not changes to causal or TTG gates.
No claim about the whole Brillouin zone follows from these short paths.

## Physical coordinate and mass metric

Let the two layers contain masses M_A and M_B. Define their mass centroids
and relative in-plane displacement s=u_A-u_B, with reduced mass

```text
mu=M_A*M_B/(M_A+M_B)
s_a=sum_(i in A) m_i*u_ia/M_A - sum_(i in B) m_i*u_ia/M_B
Q_i=sqrt(m_i)*u_i
R_ai=+sqrt(m_i)/M_A in layer A, -sqrt(m_i)/M_B in layer B
B=sqrt(mu)*R^T; B^T*B=I_2; P_s=B*B^T
```

The in-plane basis is orthogonal to the layer normal. Uniform translations
are orthogonal to B in mass-weighted space. For rigid layer motion with fixed
overall center of mass the kinetic energy is mu*|s_dot|^2/2. This kinematic
mass is not the normalization of Phi. The dataset atomic masses and
[CODATA atomic mass constant](https://physics.nist.gov/cuu/pdf/wall_2022.pdf)
supply the unit conversion; unknown sample isotope composition is not thereby
closed.

## Eigenvectors and degenerate subspaces

[Phonopy's dynamical-matrix convention](https://phonopy.github.io/phonopy/formulation.html)
uses mass-weighted eigenvectors and an intracell phase. Move them to a fixed
cell-periodic displacement basis with exp(2*pi*i*q.r_i) before comparing layer
centroids away from Gamma. The two-mode projector, not individual eigenvector
components, is invariant under arbitrary phases or rotations within a
degenerate doublet. Record B^dagger*P_pair*B and its two eigenvalues. Do not
infer exact rigidity when overlap is merely near one.

## Displacement-force response, not Phi response

At Gamma let Omega^2 be the full mass-weighted dynamical matrix in angular
frequency squared. An external generalized force f conjugate to s gives

```text
chi_s(z)=R*(z^2*I+Omega^2)^-1*R^T
        =sum_n (R*e_n)*(R*e_n)^dagger/(z^2+Omega_n^2)
Z_pair=R*P_pair*R^T=(B^T*P_pair*B)/mu
```

z is Laplace frequency with positive real part for the numerical check.
Z_pair has units kg^-1; chi_s has units m/N=s^2/kg. In an exactly rigid
isolated doublet Z_pair=I/mu. Its inverse is a conditional pole effective mass
matrix, not total sample mass, canonical UET kinetic residue or a heat-current
Kubo coefficient. Higher-mode weight is retained in the full resolvent.

## Verification and boundaries

Compare the full resolvent to an independently summed spectrum. Check the
Gamma matrix against the existing direct force-constant assembly, eigenpair
residuals, mass metric, degeneracy/gauge invariance, rotations, atom permutations,
q-to-minus-q spectra and the short-path overlap. Hash the source files and
all consumed evidence. Keep old heat-capacity payloads and whole-topic gates
unchanged. There is no TTG/holdout or calibration input.

The Raman gap comparison is a separate physical correspondence check. A
frequency outside the source-reported experimental interval is a mismatch,
not a numerical-method failure and not permission to retune force constants.
Harmonic source state, cell dimensions and temperature differ from the Raman
experiment; no statistical significance is assigned without a model-error
budget. Shape identification alone does not close that mismatch.

Next: identify the source-state origin of the interlayer frequency discrepancy
and obtain independent strained force constants/eigenvectors. A momentum
derivative is not a strain derivative. Full dispersion, mode occupation,
scattering/heat flux, pump coupling and the UET matter/Phi map remain separate.
