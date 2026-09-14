# Topic 13 raw acquisition structure

MAJOR_RESULT_CLOSURE: PARTIAL; raw source acquisition and table structure established, not physical calibration.

WHAT_IS_ACTUALLY_CLOSED: Zenodo 14760926 raw-sorted archive (139286365 bytes) and README match publisher size/MD5; SHA256 identities are recorded. Three gzip tables were decoded through the inert reader without executing serialized globals. All members were consumed to CRC-checked EOF. There are 38 rows each in 400nm cut1/cut2 and 32 in 800nm, each with two 512x512 ON/OFF arrays and 22 source columns. The 400nm cuts align exactly in stage/delay coordinates and none of their 38 image pairs is identical.

WHAT_REMAINS_OPEN: Separate cuts are not established independent repeated acquisitions. Each row exposes one ON and one OFF image, without an explicit per-frame axis. Source `nimages=2` does not establish how images were aggregated or an effective sample size. Detector gain/count semantics, acquisition independence, source sensor calibration and Phi coupling remain open.

DEPENDENCY_UNLOCKED: Source-specific acquisition reconstruction and cut-to-cut sensitivity analysis only. No physical dependency unlock.

STATUS: ROWS_DECODED_REPEAT_INDEPENDENCE_OPEN.

WHAT_CHANGED: Raw archive verifier/test and structure verifier/tests; generated [acquisition artifact](../../artifacts/t13_ued_raw_archive_audit.json) and [row structure artifact](../../artifacts/t13_ued_raw_structure_audit.json). Artifacts retain file/hash chains and row identities. Acquisition artifact intentionally describes only archive inventory; downstream structure artifact records completed payload/CRC inspection.

EQUATION_OR_MAPPING: Detector records and instrument metadata only; no new UET equation. Source PHI_DEG/PHI_RAW are instrument columns, not UET Phi. Source Delay_ps is not the pump-relative time axis; its larger numeric values do not extend the processed observation window.

VERIFICATION: Nine tests across raw acquisition, raw structure and inert reader; successful decoding of all three external tables; foundation audit PASS while foundation remains BLOCKED. No holdout path used by these scripts.

CONTROLLING_BLOCKER: Acquisition/aggregation semantics and measured covariance; independent Phi calibration remains separate. Temperature_B ranges are 301.3754005-301.3774160 (cut1), 301.2832997-301.2852862 (cut2), and 300.8997234-300.9008443 (800nm), in unverified source sensor units. Temperature_A is zero throughout; this is not evidence of zero physical temperature. No range is an uncertainty interval.

NEXT_ACTION: Inspect pinned upstream acquisition/sorting code for cut identity, frame aggregation, exposure normalization and sensor provenance before estimating covariance. Compare cuts as sensitivity evidence without claiming independent repeated trials. Do not infer Poisson statistics from integer-looking image values or bootstrap correlated detector pixels as independent shots.

CLAIM_BOUNDARY: CC-BY-4.0 source; raw files remain ignored local-only. No physical thermometry, noise covariance, heat inference, alpha, TTG validation or Full Topic 13 closure. No external unpickling, holdout fitting or threshold changes. Full-core unlock and claim promotion remain false.
