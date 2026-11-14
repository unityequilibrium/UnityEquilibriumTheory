# Physical route decision after dual-channel identifiability

Owner: Topic13. Scope: select and evaluate one real protocol through native equations, source/readout capability, calibration and error requirements. This is not closure of Full Topic13, an experiment, or a UET validation claim.

## Route decision

Select the U-shaped two-electrode/two-direction MEMS route over the inspected arch, base-excited beam and 3:1 ringdown alternatives. Its published native operator is concrete enough to identify specific admission failures. Current materials do **not** support a locked physical UET prediction or an accepted reduction to the old source-free auxiliary kernel. The alternative finish condition is a source-backed route limitation and a precise missing packet, not another generic “need data.”

Inputs are curated in the [source reference](../Data/03_Research/physical_route_admission_sources.json). The [prior two-channel derivation](T13_DUAL_CHANNEL_IDENTIFIABILITY_2026-10-17.md) is reused unchanged. New calculations below diagnose the sourced native model only; no measured response curve is fitted or scored.

## Source evidence and choice

Selected primary reference: [Rocha and Younis 2022](https://www.nature.com/articles/s41598-022-14657-1), Eqs. (1)-(2), experimental methods and Figs. 1/3/6/7. It supplies E1/E2 actuation, two-direction video readout, state-dependent electrostatic forcing and inertial terms. Geometry is adjusted to frequency data; parameters are not independent UET predictions. Supplement S1 is a model table; S7/S8 discuss small inertial sensitivity in their tested IR setting. Published plots are not an admitted phase-record/error package.

Alternative [Asadi et al. 2021](https://www.nature.com/articles/s41378-020-00230-1), Experimental process/Fig. 8: base shaker plus one-point vibrometry; the observation point limits modal-amplitude interpretation. Its source participation/readout normalization is not an admitted independent-control package. This does not prove a single-drive dynamic protocol impossible.

Alternative [Ramini et al. 2016](https://www.nature.com/articles/srep34717), Devices/Electrothermal frequency shifting: useful tunability, but changing thermal bias changes the state. The earlier source/readout gaps remain; no unchanged search or fit is repeated.

Alternative [Chen et al. 2017](https://www.nature.com/articles/ncomms15523), Transient characterization/methods/data statement: 3:1 transfer and a torsional/third-harmonic optical ambiguity at IR, with requested rather than acquired data. It is not substituted for the 2:1 protocol.

Selection is a hard-capability decision (two inputs, two output directions, native operator available), not a numerical ranking or claim all alternatives are exhausted globally. One auxiliary drive is not intrinsically required when independently informative dynamics or self-nonlinearity constraints exist; two sensors alone do not establish identifiability.

## Actual acquired source and inspection limits

The publisher's [supplementary DOCX](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41598-022-14657-1/MediaObjects/41598_2022_14657_MOESM1_ESM.docx) was read in memory: 6,336,789 bytes, SHA-256 `e8052811a90517d3bc3d3b264cb74598f90ecd23d40697e7b794b92196d265f4`. No raw-file duplicate is retained. Plain Table S1 and relevant discussion were extracted. S16/S18 exist as equation images; the available WMF renderer overlapped glyphs, so their normalization was not signed off. Do not report this execution/readability limitation as absent physics or absent source definitions.

Main-article equations are readable and independently show the extra native terms. Supplement text reports little delta1/delta2 sensitivity for its 54 V DC / 0.5 V AC IR case. That is relevant favorable model evidence and must not be hidden; it is not a supplied bound on experimental uncertainty at arbitrary conditions. No claim is made that inertia necessarily dominates this IR test.

## Native source is not a pure sine or a source-free auxiliary channel

For the published squared-voltage operator at a FIXED coordinate u,

```text
(Vdc+Vac*cos(theta))^2
 = Vdc^2+Vac^2/2 + 2*Vdc*Vac*cos(theta) + Vac^2*cos(2theta)/2.
```

This algebra is exact. At the reported nominal 54 V / 0.5 V cosine-amplitude convention, second/fundamental coefficient ratio is 1/432. This is not a measured total force fraction: moving `(1-u)^-2` mixes harmonics, and actual source calibration/uncertainty is still needed. At Vdc=0, fixed-coordinate force has DC and 2*voltage-frequency terms, not a fundamental voltage-frequency term. Generator frequency, force frequency and mechanical response frequency must be traced separately; this is not an allegation that the authors used the wrong convention.

For |u|<=A<1, the exact geometric factor lies between `(1+A)^-2` and `(1-A)^-2`. A justified measured A and source transfer can bound an omission; none is chosen from a target fit here. Gap singularities cannot be clipped away.

The reported high-mode-drive IR experiment directly forces the higher coordinate. It is not the old low-mode experiment with an unforced auxiliary response. The dual-channel full-source framework may describe a different protocol, but cannot silently reuse the source-free three-harmonic inversion.

## State reconstruction from the sourced model

The following is a declared source-MODEL diagnostic, not a reconstruction of measured data. Configure E1 DC/AC zero and E2 DC=54 V with AC=0 to isolate a candidate baseline. Actual experimental E1 settings, driven mean shifts and sensor offsets must be independently supplied before a comparison.

With primary x0=0, the native equilibrium residual for y0 is

```text
f(y0)=wn2^2*y0+k32*y0^3-beta2*Vdc2^2/(1-y0)^2.
```

Using Table S1 values, bracket the small branch on [0,1/4]. On this interval,
`f'(y)>=wn2^2-2*beta2*Vdc2^2/(3/4)^3>0`. The endpoint signs plus this lower derivative bound certify one root ON THAT BRANCH; no claim is made about other equilibria. Forty-eight exact rational bisections enclose it within 2^-50 in native displacement units. A 32-step enclosure is checked to contain the refined interval.

Local auxiliary mass and stiffness are

```text
M2=1+delta2*y0^2
K2=wn2^2+3*k32*y0^2-2*beta2*Vdc2^2/(1-y0)^3
local w2^2=K2/M2; local w1^2=1+alpha1*y0.
```

The producer uses conservative interval endpoints for these positive quantities. Their dimensionless frequency-squared intervals differ from the zero-bias operator. Consequently the zero-bias table frequency cannot simply be frozen while treating DC tuning as amplitude-only input. This is a source-model consequence; geometry fitted upstream and absent parameter covariance forbid calling its digits an independent physical prediction. No SI clock or modal mass conversion is inferred from an unreadable equation image.

## Inertial and source terms need a declared domain

For u=A*cos(Omega*t), direct differentiation gives

```text
u*u_dot^2+u^2*u_ddot = -A^3*Omega^2*(cos(theta)+cos(3theta))/2.
```

Thus that term can contribute a frequency-dependent cubic response; it is not automatically the constant contact term of the previous lossless pole family. The identity does not prove its experimental size. A full native forward model or an output-unit omission bound is needed in the chosen domain, respecting the supplement's favorable sensitivity evidence where applicable. No inertial/damping term is added to UET to rescue a fit.

Likewise alpha1 and alpha2 in dimensionless equations cannot be tested by setting alpha1=2*alpha2 directly. The prior reciprocal condition is mass/coordinate/gain weighted. Native mass/profile normalization and measurement-point conversion must be verified first.

## Admission packet and frozen decision

| Dependency | Evidence now | Exact addition needed before a physical score |
| --- | --- | --- |
| Native protocol | Two inputs/output directions, complete displayed force equations | Both electrode waveforms/biases, equilibrium branch, timing and state identities |
| UET correspondence | Shared interaction order only | Finite-mode/material projection with units, source/readout operators and quantitative treatment of extra terms |
| Generalized coordinates | Equation coordinates and measurement targets differ | Verified S16/S18 plus point-A/point-B mode/profile map and independently supported modal masses |
| Calibration | Upstream geometry adjusted to frequencies | Separate calibration records, relative gains, electrode-to-modal force transfer and joint uncertainties; no retuning on reserved outputs |
| Observations | Published amplitude curves, no admitted numeric-record locator | Eligible signed complex/phase/time records or a justified sufficient observable, processing lineage and usage terms |
| Errors | Model sensitivity discussion, not full acceptance budget | Output-unit joint bounds for source, detector, timing, bias, damping and omissions; no invented independence or universal 10% error |
| Test separation | Shapes/figures already seen in this research | Honest exposure record, calibration partition and a separately locked comparison; no “restored blind” label |

Four bounded exact-title/DOI/repository locator queries found no qualifying numeric package in this pass. Irrelevant U-shaped electromagnetic sources were not adopted. This is not an exhaustive proof of absence or permission to contact authors. A manufacturer resolution spec alone cannot supply the run-specific budget.

**Decision:** `SELECTED_NATIVE_MIMO_ROUTE_NOT_ADMITTED_FOR_UET_TEST`. Do not score curves as UET predictions, fit a new material map or call model reproduction external validation. The native route is technically relevant, but the missing packet and field-to-material correspondence control the decision. A valid future acceptance rule would propagate the full predeclared source/parameter/observer set to reserved observables and reject only disjoint prediction/measurement sets. Those sets cannot be numerically locked with the present calibration/uncertainty inputs; no threshold is invented.

### Which dependency to address first

Do not acquire a large response archive merely to fit the shared interaction. First supply a named UET-to-material projection and a predeclared relation not freely retuned on the comparison records. If UET and the ordinary comparator yield the same complete forward operator, initial conditions, source and readout on this domain, this protocol cannot distinguish them: the same well-posed initial-value problem has the same output. More precise sensors do not remove that equivalence. This is a conditional limitation, not a proof that every UET extension or every experiment is equivalent.

If such a distinguishing relation exists, the next dependency is the independent calibration packet in the table, followed by locked joint uncertainty propagation and reserved observations. A response disagreement would then reject the specified model-plus-mapping under its declared conditions, not every possible UET formulation. Agreement with a flexible fitted mechanical operator would support only that operator's adequacy, not UET uniquely. No new relation, calibration or uncertainty bound has been invented to make the route pass.

## Evidence and reproducibility

[Producer](../Code/03_Research/Research_T13_Physical_Route_Admission.py), [tests](../Code/03_Research/test_t13_physical_route_admission.py), [contract](../calculation_contracts/physical_route_admission.json), [generated route decision](../../../core/07_artifacts/topic13/t13_physical_route_admission.json).

Use the producer's `--check` for offline, read-only reproduction; `--emit` changes only the one small canonical output. Optional `--verify-supplement` reads the public reference in memory, checks its binary hash and Table S1 transcription, and stores no raw file. The native diagnostic is SYNTHETIC/source-model scope, with no measured-response comparison and no scientific gate promotion.
