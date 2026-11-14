# Limitations

- The current repository comparison uses published values and topic scripts rather than a
  complete observational pipeline.
- The dark-energy problem retains documented failure cases inside the topic.
- Internal agreement with selected H0 references does not establish broad cosmological
  adequacy.
- The generic Landauer-derived solver beta is not the same quantity as the Hubble-frame
  coupling. Using the generic beta for the H0 frame comparison fails the benchmark.
- The current H0 benchmark uses `sqrt(alpha_em)` as a no-fitting frame coupling. This still
  leaves open proof work: the redshift transition law, BAO/SN/CMB consistency, uncertainty
  propagation, and full observational-pipeline replication are not yet closed.
- Source records and hashes are now present for the scalar H0 comparison, but this is still
  not equivalent to mirroring full upstream observational datasets.
- The central `ALPHA_EM` constant is truncated relative to latest CODATA precision; this is
  acceptable for the current scalar benchmark but should be tightened before paper-grade
  constant provenance.
