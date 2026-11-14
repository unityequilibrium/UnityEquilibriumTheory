# Method

- Engine: `Code/01_Engine/Engine_Mass_Gap.py`
- Proof script: `Code/02_Proof/Proof_Mass_Gap.py`
- Research script: `Code/03_Research/Research_Mass_Gap.py`

Method boundary:

- The current repository workflow includes a parameter sweep against a selected lattice-QCD
  target and is therefore calibration-aware.

## Research Workflow

1. Load the source-lock manifest and the topic working copy of the lattice-QCD glueball spectrum.
2. Select the scalar `0++` benchmark row and convert the reference uncertainty from `m r0`
   units to MeV using the metadata convention in the dataset.
3. Sweep `alpha` across the configured negative-curvature interval.
4. Convert the engine gap proxy to MeV using the configured `scale_gev`.
5. Select the minimum-error calibration point and write the artifact with hashes,
   residuals, uncertainty thresholds, and claim boundary.

## Current Scientific Role

The method tests whether the implemented curvature-gap mechanism can be calibrated to
one cited lattice glueball scale. It is useful as a focused bridge between the UET mass
generation idea and non-Abelian benchmark data, but it does not yet test spectral ratios,
continuum-limit behavior, gauge-invariant operator construction, or a general existence
argument.
