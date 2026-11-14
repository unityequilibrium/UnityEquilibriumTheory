# Topic 13: experimental population-source route

MAJOR_RESULT_CLOSURE: PARTIAL. A permitted experimental archive and its processing route are identified; quantitative mode populations and Phi coupling are not closed.

WHAT_IS_ACTUALLY_CLOSED: The Zenodo metadata establishes open CC-BY-4.0 access and published archive checksums. The author notebook is pinned to a commit and inspected as JSON, not executed. Acquisition integrity is controlled by the generated audit, not this prose.

WHAT_REMAINS_OPEN: Safe numeric payload decoding, measured units, uncertainties/row identities, detector-to-mode inversion, invisible modes, same-state sample mapping and independent Phi coupling.

DEPENDENCY_UNLOCKED: Payload inspection and detector-mapping research only.

STATUS: Consult `artifacts/t13_ued_source_acquisition_audit.json` for completed download/hash state. Presence of the metadata alone is not numeric acquisition.

WHAT_CHANGED: Added a checksum/central-directory audit and tests that do not deserialize pickle, execute notebooks or extract archive paths. Raw data and the inspected notebook stay local-only.

EQUATION_OR_MAPPING: The author workflow uses pump-on/off diffraction images against delay, with reciprocal-space calibration. These are not yet n_j(q,t), heat flux or temperature. A further forward/inverse scattering model is needed before energy can be summed over occupations.

VERIFICATION: The two focused tests check streaming hashes and listing opaque archive members without decoding or extraction. Real archive byte count and published MD5 must match before generating a completed acquisition record. The audit records SHA-256, member sizes/CRC metadata and notebook cell identities. Listing CRC values is not a CRC check of decompressed members.

CONTROLLING_BLOCKER: safe_numeric_decoding_and_detector_to_mode_mapping_missing.

NEXT_ACTION: Inspect the processed members with a restricted, reviewed data-only conversion route; never call unrestricted pickle.load or pandas.read_pickle on downloaded data. Preserve pump-on/off pairing, delay units, reciprocal calibration, preprocessing and sample identity. Then test inverse-map rank, observable coverage and propagated covariance before estimating relaxation.

CLAIM_BOUNDARY: No physical mode population, lifetime, Kubo coefficient, alpha_Phi_K or TTG prediction is emitted. Dataset acquisition is not calibration. Coherent-amplitude dephasing is not automatically population/energy relaxation. No source is used as a replacement for locked Xie data.

## Source decisions

[Barantani and Claude dataset, Zenodo 14760926](https://zenodo.org/records/14760926)
provides a processed UED archive and associated processing references. The API
reports CC-BY-4.0 and publication date 2025-01-29. The processed archive is
271,920,160 bytes. The full API capture, not a search-result date, controls this
record's identity. It is a comparison candidate, not a TTG source.

[Author processing repository](https://github.com/remiclaude/UED_processing/tree/7f7036bfda28f9330f19b40e57f4edf464b67d64)
loads gzip-compressed pandas records with image pairs and delay, then applies
reciprocal calibration. A code redistribution license has not been established;
the downloaded notebook is kept local and is not executed.

[Kremeyer et al., arXiv:2310.18793](https://arxiv.org/abs/2310.18793), section VII,
provides the most direct full-scattering-matrix TG/UEDS modeling connection, but
states that supporting data are available from the corresponding author on
reasonable request. This is a simulation/data-request route, not an acquired
experimental numeric population source. No request has been sent on the user's behalf.

[Rene de Cotret et al., arXiv:1908.02795](https://arxiv.org/abs/1908.02795)
provides a branch-population inversion framework. Its [001] geometry leaves
out-of-plane modes invisible; the text also discloses a positive *population
change* constraint used for robustness. Do not transfer that constraint to an
oscillating thermal grating: a negative deviation can coexist with positive
absolute occupation. Detector null directions require extra information, not
zero-filled populations or a claim of complete energy accounting.

## Extraction acceptance

Before calling the new archive a mode-occupation source, require numeric row
identity, source units and uncertainty; a documented map from detector coordinates
to phonon wavevectors; structure factors and full-rank evidence for every claimed
resolved branch; and an explicit account of unresolved modes. Export only reviewed
data arrays into a non-executable format. Do not fit a relaxation time to a picture
or use one scalar decay rate as a complete collision operator.
