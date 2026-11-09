# Ding PBTE Data Request Draft

Status: `DRAFT_NOT_SENT`

This draft is prepared from the Topic 13 source-request manifest. It must not be
sent without project authorization. It does not request, access, or use the
locked Xie 2026 holdout.

To: Keith A. Nelson; Gang Chen
Subject: Request for reproducibility data for graphite TTG/PBTE study

Dear Professor Nelson and Professor Chen,

I am preparing a reproducibility package for the thermal-response bridge in our
internal research project. I am writing regarding:

Z. Ding, K. Chen, B. Song et al., "Observation of second sound in graphite over
200 K," Nature Communications 13, 285 (2022), DOI: 10.1038/s41467-021-27907-z.

If possible, could you share the numerical inputs or outputs used for the
published graphite PBTE/TTG calculations, together with permission terms for
research reuse? The minimum useful package would contain the following.

1. Material and geometry

- Natural-graphite specimen identity, isotope and defect state, morphology, and
  the geometry/state used for the calculation.
- Relaxed lattice vectors, atomic coordinates, unit-cell volume, and the volume
  convention.
- TTG temperature grid, grating periods, boundary assumptions, and scattering
  settings.

2. First-principles and PBTE inputs

- VASP version, PAW dataset identifiers, exchange-correlation/vdW settings,
  cutoff and convergence settings.
- Second- and third-order force constants, or the original Phonopy and
  thirdorder/ShengBTE input/output files.
- ShengBTE CONTROL files and the 16 x 16 x 8 calculation outputs, including
  isotope and boundary-scattering assumptions.

3. Numeric mode and response data

- Mode-resolved frequencies, eigenvectors, group velocities, mode heat
  capacities c_mu(T), mode indices, and Brillouin-zone weights.
- Aggregate C_src(T) = sum_mu c_mu(T), with units J m^-3 K^-1 and the
  temperature grid.
- Mesh/supercell convergence results and an uncertainty or sensitivity
  envelope.
- Machine-readable TTG response inputs/outputs sufficient to regenerate the
  published temperature response, plus a data dictionary and preprocessing
  description.

For every delivered file, a filename, checksum, source identity, preprocessing
description, row identity, and permission/terms statement would be very helpful.
If the exact 2022 payload is not available, a pointer to a permitted
same-regime PBTE reproduction would also be useful, provided its material state
and uncertainty are documented separately from the 2022 specimen.

We will keep all source data separate from calibration and holdout data. We will
not infer a Phi-to-temperature coefficient from a normalized TTG curve, and we
will not use any locked holdout data for fitting or tuning.

Thank you for considering this request.

Best regards,

[Name]
[Affiliation]
[Contact]
