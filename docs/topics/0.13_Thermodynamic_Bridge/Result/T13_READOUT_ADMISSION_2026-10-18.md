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

## Can one global gain correction alone repair the domain mismatch?

The authors' [arXiv v2 methods](https://arxiv.org/html/2510.01775v2#S3.SS1), section III.1, explicitly describe complex circle fitting with gain, phase/delay and impedance mismatch. This is an author preprint, not a newly verified copy of the final supplement: its version/section numbering is kept distinct. It supports the existence of a calibration method, not an exact-curve gain/mismatch/noise packet for our CSV. The illustrative calibration working point differs from Set III. No preprint parameter or quality-factor identity is substituted into the final-version rate ratio. The mean-field simulation's omission of explicit noise is not evidence that measured readout noise vanishes.

Test a deliberately permissive envelope, not an independent calibration:

```text
m_i=g*t_i+e_i, g>0, l<=t_i<=1, |e_i|<=eta
l=17/58; m_min=min(m_i); m_max=max(m_i).
```

The upper endpoint is the CLOSED envelope; finite stationary inversion is stricter. Each t_i is allowed to vary independently, ignoring detuning and stability constraints. Thus failure of this permissive envelope rules out a noiseless constant-gain-only explanation of the central ideal range; success would not establish a cavity model.

At eta=0 a common gain requires m_max<=g<=m_min/l. Actual endpoints require simultaneously g>=1.3560284 and g<=0.5158183. No such gain exists. A simple constant normalization factor alone cannot repair all rows under this central real-port assumption. No gain correction was applied.

For a uniform residual allowance, the necessary conditions are eta>=m_max-g, eta>=g*l-m_min and eta>=0. Multiplying the first by l and adding the second eliminates g. The optimistic minimax envelope is

```text
eta_star=max(0,(l*m_max-m_min)/(1+l)).
```

When positive, equality is attained by the envelope optimizer g_star=(m_max+m_min)/(1+l), balancing both endpoint violations. This is an algebraic lower bound over a relaxed range, NOT a fitted physical gain or a noise estimate. Here eta_star is about 0.1904476 in the REPORTED amplitude units; a locked unit gain instead needs an envelope of at least 0.3560284. Neither number is a standard deviation, confidence interval, measured noise floor or accepted error budget. No row was changed and no target-fit gain was adopted as calibration.

Alternatively, a noiseless global gain could satisfy the relaxed range only if the actual lower ratio l were at most m_min/m_max, about 0.1114933. This is a required calibration change for that particular explanation, not an assertion that the independently published central ratio is wrong. Uncertainty or complex mismatch may change the real admissible range. Without an independently supported lower bound on that ratio, the central-domain diagnosis cannot be upgraded to rejection. If a valid lower bound l_0 is available, the same monotone formula at l_0 gives a conservative necessary envelope; it still requires an independently justified readout/noise model before statistical use.

**Narrowed decision:** do not spend another wave searching for one scalar normalization that makes this curve exact. The next useful packet must address noise and/or frequency-dependent or complex readout corrections and their joint calibration uncertainty. Arbitrary frequency-dependent gain fitted to every target would erase the test rather than provide calibration. This result rejects only the noiseless constant-gain repair of the conditional central range, not the source's nonlinear model or UET.

## Scope checkpoint: the native readout diagnostic is not the UET discriminator

The [approved observer-aware design](../RESEARCH_DESIGN_OBSERVABLE_DISCRIMINATION_2026-10-17.md) concerns the inherited mechanical nonlinear kernel, with a same-state material/operator mapping and signed harmonic readout. A native cavity S21 magnitude is not that kernel. The [action-class result](T13_ACTION_DISCRIMINATION_2026-10-18.md) also demonstrates why fitting a shared scalar comparator cannot identify a uniquely UET mechanism.

There are therefore TWO distinct dependencies: the native diagnostic needs an admitted measurement-error/correction packet; the UET research question additionally needs the material/source/kernel correspondence or an independent distinguishing constraint. Solving the former does not solve the latter. This wave closes the constant-gain-only repair question; do not expand it into an unlimited native-apparatus benchmark. Return to the original kernel's remaining correspondence/feasibility decision before further cavity data acquisition. This is not a declaration that every UET hypothesis is untestable.

Reproduction: [producer](../Code/03_Research/Research_T13_Readout_Admission.py), [controls](../Code/03_Research/test_t13_readout_admission.py), [contract](../calculation_contracts/readout_admission.json), [canonical diagnostic](../../../core/07_artifacts/topic13/t13_readout_admission.json). Emit/check are offline and deterministic from the small verified CSV and manifest; no repeated network fetch is needed.
