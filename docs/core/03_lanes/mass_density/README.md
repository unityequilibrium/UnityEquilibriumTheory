# Mass-density support lane

This package is the canonical home for the candidate `C`-to-mass-density
correspondence operators.  It keeps geometry/shape, source amplitude, unit
conversion, and the 3D measurement operator as separate contracts.

The lane is intentionally conservative: the normalized relational coordinate
does not identify a mass-density amplitude by itself.  The one-dimensional and
three-dimensional SI operators require explicit source mass and length scales,
so they remain synthetic/internal contracts until an external measurement map,
uncertainty package, and holdout comparison are available.

## Members

- `mass_density_correspondence.py` — normalized kernel-smoothed density and
  direct `C`-only identifiability diagnostic.
- `mass_density_amplitude.py` — explicit source-amplitude extension of the
  normalized shape lane.
- `mass_density_dimensional.py` — synthetic SI one-dimensional line-density
  conversion.
- `mass_density_3d.py` — synthetic SI three-dimensional density operator.

The former root modules remain compatibility shims while consumers migrate to
this package.  Organization migration does not promote `C` to universal mass,
does not create a galaxy prediction, and does not change the existing blocked
foundation boundary.
