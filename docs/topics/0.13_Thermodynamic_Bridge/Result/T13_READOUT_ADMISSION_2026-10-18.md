# Actual Fig3c readout admission: do not invert all processed magnitudes

Owner: Topic13. Class: exploratory physical-data/readout diagnostic, not physical acceptance or a UET test. This advances the [shared-scale protocol](T13_SOURCE_FEEDBACK_PROTOCOL_2026-10-18.md#h-rejecting-a-shared-model-without-knowing-the-absolute-input-scale) from hypothetical requirements to one actual small public member.

## Source and frozen question

The question is whether the published low-power processed magnitude can be directly inverted with the central ideal passive hanger calibration, before any cubic residual or coefficient is fitted. No filtering, rescaling or parameter fitting is allowed in this diagnostic.

The [public archive](https://doi.org/10.5281/zenodo.18954807) supplies the Fig3c Experiment CSV. Only that 39,201-byte member was fully decompressed, with its ZIP CRC32 and SHA-256 checked. Bounded HTTP ranges transferred 99,458 bytes including tail, directory and compressed member. No 377 MB archive copy was downloaded. The [working CSV](../Data/03_Research/dhiman_2026_fig3c_experiment.csv) normalizes CRLF to LF only; upstream bytes can be reconstructed and their hash/CRC reverified. The [manifest](../Data/03_Research/dhiman_2026_fig3c_readout_manifest.json) separates raw-member and normalized-copy identities, CC-BY-4.0 data license, product level, exposure and unresolved corrections. This small data working copy is not a raw complex time trace or a duplicate full archive.

The [main article](https://www.nature.com/articles/s41467-026-73259-x), Fig3 caption and its experiment/model discussion, binds this curve to Set III at low drive. Authors identify a single stable fixed-point regime across the curve, unlike the higher-power Fig3d. Their pulsed method and classification support a stationary candidate; they do not supply the independently quantified per-record averaging/correction uncertainty required by our new test. The [parameter table](https://www.nature.com/articles/s41467-026-73259-x/tables/1?error=cookies_not_supported) lists Set III linewidths kappa_int/(2*pi)=0.68 MHz and kappa_ext/(2*pi)=1.64 MHz. These are independently determined inputs according to the source, but the inspected table has no complete joint uncertainty/deembedding packet. They are used here only as rounded CENTRAL calibration values.

## Conditional domain result on actual records

For the ideal real-deembedded passive hanger,

```text
|t| >= 1-c_p/a = kappa_int/(kappa_int+kappa_ext)
and |t| < 1 for the finite stationary inverse.
```

The central amplitude lower bound is 17/58, about 0.2931; this is NOT an uncertainty-qualified physical limit. Common angular-frequency factors cancel, so no extra 2*pi is applied. Absolute S21 is an amplitude, not its square. The CSV's detuning column is preserved, but its dimensional/normalized-axis conversion is not used in this test and must be resolved before a physical residual.

| Check | Result on all 1,001 rows |
| --- | --- |
| Missing or nonfinite numeric fields | 0 |
| Duplicate detuning keys / exact duplicate rows | 0 / 0 |
| Below central ideal amplitude minimum | 9 |
| Inside central ideal finite-inverse domain | 589 |
| At or above unit magnitude | 403 |
| Rows clipped, dropped or rescaled | 0 |

Recorded amplitude ranges approximately 0.1512 to 1.3560. Every point is retained. The 589 inside-domain rows are NOT automatically admitted: selecting them after seeing compatibility would change the selection policy. The remaining 412 rows show that this processed noisy magnitude plus the central ideal inverse cannot simply be treated as exact stationary observations.

## What this does and does not establish

Outside-domain values do not by themselves imply corrupt data, a failed experiment, negative physical occupation, failed UET, or rejection of the source model. Measurement noise, amplitude normalization/gain, complex mismatch, rounded calibration and averaging can change observed values. No noise distribution, covariance, gain correction or zero systematic error has been inferred from adjacent detunings. Those points sample different expected signals, not declared repeated measurements of one state.

The earlier exact rational gcd controls must NOT be applied directly to these rounded/noisy records. No physical residual, goodness-of-fit, threshold, significance or theory-rejection score was computed. This exposed curve cannot later be relabeled blind holdout. Header-only statements in earlier protocol waves describe their original exposure scope, not this new acquisition; the new packet has its own PHYSICAL_COMPARISON/DIAGNOSTIC contract and artifact.

**Controlling prerequisite now:** a run-matched calibrated readout/processing model with noise and joint calibration/averaging bounds, or a validated processed product already carrying those corrections and uncertainties. Raw phase is not universally necessary, but the ideal magnitude-only shortcut has not been admitted. The source does contain calibration methods and a low-power stationary candidate; the gap is their usable uncertainty/correction packet for this diagnostic, not the mere existence of helium data or lack of any online experiment.

The next useful source check is the calibration/processing and noise record linked to this exact curve. Do not fit an unknown gain to the comparison rows and call it independent calibration; do not acquire large Fourier products to solve this readout uncertainty without a source binding. Native apparatus compatibility would still not resolve the earlier UET/comparator equivalence or supply an SI Phi anchor.

Reproduction: [producer](../Code/03_Research/Research_T13_Readout_Admission.py), [controls](../Code/03_Research/test_t13_readout_admission.py), [contract](../calculation_contracts/readout_admission.json), [canonical diagnostic](../../../core/07_artifacts/topic13/t13_readout_admission.json). Emit/check are offline and deterministic from the small verified CSV and manifest; no repeated network fetch is needed.
