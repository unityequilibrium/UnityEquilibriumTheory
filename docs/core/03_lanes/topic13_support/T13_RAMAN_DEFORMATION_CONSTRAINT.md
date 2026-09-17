# Topic 13: source-backed Raman mass-deformation constraint

## What is gained

This replaces a wholly unspecified material deformation source with a measured
constraint on its hydrostatic projection, conditional on identifying a material
mode. It does not equate a Raman doublet with the UET matter doublet.

[Hanfland, Beister and Syassen (1989)](https://doi.org/10.1103/PhysRevB.39.12598)
report graphite Raman frequencies and pressure derivatives in Table II, and
axial moduli in Table I. The extracted package preserves row identity, errors,
PDF hash and locators. These are room-temperature pressure-fit quantities,
not state-matched TTG calibration. The low-mode pressure slope is extrapolated
from the reported fit, and the a-axis modulus has a fixed linear fit form.
Raw copyrighted PDF remains local-only; only extracted numeric facts are staged.

## Exact spectral conversion and conditional source map

Let nu be the Raman wavenumber, not angular frequency. With nu in cm^-1:

```text
E_mode=h*c*100*nu
Omega_mode=2*pi*c*100*nu
x_mode=E_mode^2=(hbar*Omega_mode)^2
delta0=d ln(nu)/dP
d x_mode/dP=2*x_mode*delta0
```

h,c,k_B are exact SI definitions, not fit parameters
([BIPM](https://www.bipm.org/en/measurement-units/si-defining-constants)).
delta0 from the source is per GPa and must be divided by 1e9 for per Pa.
This avoids both a missing cm-to-m factor and an erroneous extra 2*pi.

Only IF x_mode is matched to the canonical UET matter curvature in the same
state does its strain derivative supply the physical D needed by the source
ansatz. Spectroscopy fixes an eigenfrequency; it does not fix the full kinetic
residue, density of states, h-to-Phi coupling, or Phi normalization Z.

For a scalar mode shift preserving basal-plane hexagonal symmetry, put
D_xx=D_yy=D_ab and D_zz=D_c. Hydrostatic pressure produces
eps_xx=eps_yy=-P/B_a and eps_zz=-P/B_c to first order, so

```text
[-2/B_a, -1/B_c] . [D_ab/x_mode, D_c/x_mode] = 2*delta0
```

This is one equation for TWO coefficients. Its null direction is proportional
to (1/B_c,-2/B_a). No individual D component, uncertainty ellipse or preferred
solution is identified by these data alone. Measuring two Raman modes does
not fix the problem: each mode has its own two unknown deformation coefficients.
Their joint system has rank two for four unknowns, not rank two for two.
Shear splitting of a doublet requires a matrix-valued source; the scalar
projection above does not establish an exact O(2) charge symmetry.

An independent fixed-in-plane c-axis strain experiment supplies
g_c=d ln(nu)/d eps_zz, giving D_c/x_mode=2*g_c. That additional row can close
the two-coefficient scalar projection at a matched state. It does not itself
fix Phi normalization, pump coupling or thermodynamic integration over q.

## Uncertainty without invented independence

The package records parenthetic source errors, with confidence level and
covariance unspecified. Evaluate the monotone positive spectral expressions
at all endpoint corners to obtain sensitivity envelopes. These are NOT
statistical confidence intervals or certified systematic-error bounds.
The uncertainty in the constraint row follows reciprocal axial moduli; it
does not shrink the exact tensor nullspace to a finite component error bar.
The abstract also reports absolute pressure slopes with broader errors than
those implied by Table II, particularly for the high mode. Both were visually
checked. Keep the two conversions separate, and report the union sensitivity
envelope rather than choosing the narrower one. This source precision
discrepancy is unresolved, not interpreted as an extra independent measurement.

## Which mode merits follow-up

The measured low-frequency interlayer mode and high-frequency intralayer mode
should not be conflated. As a SCREENING calculation only, freeze each source
frequency and evaluate the single harmonic-oscillator heat-capacity ratio

```text
z=E_mode/(k_B*T)
c_osc/k_B=z^2*exp(-z)/(1-exp(-z))^2
```

at 100,200,300 K. This distinguishes thermally accessible gap scales, not the
heat capacity of a whole phonon branch or the graphite sample. A Gamma-point
mode has no finite Brillouin-zone measure by itself. No low-temperature
frequency shift, dispersion, group velocity or collision lifetime is inferred.
The low gap is a promising candidate for mode-identification work, not a
demonstration that this mode carries TTG second sound.

[Sun et al. (2017)](https://arxiv.org/abs/1704.04202) provide a separate DFT
route for interlayer strain dependence. Their Eq. (3) power-law convention
uses exponent -3*gamma; it cannot be copied as -gamma. Fit errors from those
calculations are not experimental or total model uncertainties. Their results
are a prospective cross-check, NOT merged numerically with the 1989 experiment.

## Acceptance and next research

Verify the original local PDF hash, source row hashes, table-derived units,
independent angular-frequency and finite-difference derivatives, rank/nullspace,
endpoint envelopes and thermal limits. Do not read any TTG holdout or fit data.
Return physical D and alpha as absent, not fitted placeholders. Preserve the
full-topic gates and separate O(2)/He-4 status.

Next: obtain a same-state independent strain direction and mode-resolved
dispersion/residue. Use those to decide whether the low interlayer doublet can
support a material effective branch at all before identifying chi, constructing
its thermodynamic measure, or connecting the optical pump to Phi and entropy.
