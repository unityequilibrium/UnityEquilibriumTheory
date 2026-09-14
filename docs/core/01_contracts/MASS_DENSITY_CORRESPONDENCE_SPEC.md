# C-to-Mass-Density Correspondence Gate

Status: `BLOCKED_DIRECT_C_ONLY` / `SIMULATION_ONLY`

This package tests whether the current geometry-only relational coordinate `C` can be mapped
uniquely to a mass-density observable. It is an identifiability gate, not a galaxy model and not
a derivation of mass.

## Question

Can a map of the form

$$
\rho(x)=f(C(x))
$$

be used as the physical meaning of `C` in the current relational two-body lane?

The test must first hold geometry and interaction coordinate fixed while changing the standard
mass parameters. If the density changes, `C` alone does not identify density amplitude.

## Locked synthetic construction

For the same two-body positions and reference separation, the relational baseline uses

$$
C_{AB}=-\frac{r_0}{r}.
$$

The observable mass density is constructed separately from point masses with a declared Gaussian
kernel:

$$
\rho(x)=m_A W_\epsilon(x-x_A)+m_B W_\epsilon(x-x_B),
$$

$$
W_\epsilon(z)=\frac{1}{\sqrt{2\pi}\epsilon}
\exp\left(-\frac{z^2}{2\epsilon^2}\right).
$$

This has a normalized code-unit density of mass per coordinate length. It is not SI density.

Construct two configurations with identical geometry but

$$
m'_A=2m_A,\qquad m'_B=2m_B.
$$

Then

$$
C'_{AB}=C_{AB},
\qquad
\rho'(x)=2\rho(x).
$$

The same `C` value therefore corresponds to different density amplitudes. A direct universal
mapping `rho=f(C)` fails this identifiability test.

## What remains possible

The result does not prove that no mass-density lane can ever exist. It narrows the viable form to
an augmented mapping such as

$$
\rho(x)=A_m\,\widehat\rho\bigl(C,\text{geometry},\text{matter source};\theta\bigr),
$$

where `A_m` or an equivalent matter/amplitude state is declared separately. That is a
constitutive ansatz until its origin, units, observable operator, and parameters are derived or
externally constrained.

## Gates

The verifier must pass these structural checks:

- same geometry gives the same `C`;
- the density integral recovers the declared total mass within the kernel/grid tolerance;
- mass rescaling changes density linearly;
- normalized density shape is unchanged under common mass rescaling;
- direct `C`-only non-identifiability is detected rather than hidden;
- no parameter fitting or external data is used.

The intended result is `PASS_WITH_BLOCKED_MAPPING`: the test itself is valid, but the direct
physical mapping is blocked.

## Consequence for galaxy research

Do not yet fit rotation curves with `C` as baryonic mass density. The next required lane must
declare at least:

1. whether the matter amplitude is an independent field or source;
2. the dimensional map to `rho_b(x,t)`;
3. the gravitational/force operator that consumes `rho_b`;
4. the observable operator for the measured curve;
5. uncertainty, parameter lock, and holdout policy.

Implementation: [mass_density_correspondence.py](./mass_density_correspondence.py)

Audit: `docs/scripts/audit/audit_mass_density_correspondence.py`


## External 3D source-package decision (2026-08-08)

Gaia EDR3/GCNS is registered as a metadata-only candidate because it can provide a
three-dimensional stellar-structure source after distance treatment, but a catalogue of
observed sources is not itself a volume-mass density field. The required chain is:

```text
parallax -> distance/coordinates -> selection-corrected source field
-> stellar-mass realization -> rho_3D
```

The source package therefore keeps `local_raw_path`, `local_raw_sha256`, selection, mass
calibration, uncertainty, and holdout fields explicit. No fit is permitted until those fields
are closed. See [gaia_edr3_gcns source manifest](../data/external/astronomy/gaia_edr3_gcns/2026-08-08/source_manifest.json)
and [mass_density_3d_external_source_package.json](artifacts/mass_density_3d_external_source_package.json).

This narrows the problem: the remaining obstacle is not merely a missing algebraic rewrite of
`rho_3D`; it is the physical measurement and calibration chain needed to decide whether the
collective coordinate `C` predicts a density shape or amplitude.
