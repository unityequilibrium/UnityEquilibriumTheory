# Source feedback: an apparent cubic can exist with a linear spring

Owner: Topic13. Class: FORMAL protocol/counterexample and source-header admission, not a UET validation. Reuses the [action-class result](T13_ACTION_DISCRIMINATION_2026-10-18.md): its static law requires the PREPARED invariant source, not arbitrary incident power. This pass asks whether an actual controlled-source/readout protocol can support that law without circular inference.

## Decision fixed before calculation

Test three possibilities: (1) source feedback alone makes the apparent cubic, requiring input reconstruction before any score; (2) that counterexample exists only at unstable fixed points, so cannot undermine a stable-state test; (3) a calibrated scattering observable can recover the internal source without extra physical assumptions. Derive the source operator and stability certificate, then inspect actual public data headers before deciding whether to acquire numerical rows. No target fits, trajectories, new Core term or automatic author contact.

## A. A concrete candidate with public provenance

[Dhiman et al. 2026](https://www.nature.com/articles/s41467-026-73259-x), Eqs. 1-3 and data/code statements, supplies a cavity-mechanical Hamiltonian, different transfer operators for stationary and oscillating states, and [processed figure data](https://doi.org/10.5281/zenodo.18954807). Its actual device has cavity Kerr; the zero-Kerr construction below is an ordinary comparator, NOT a claimed fit to that experiment. The paper distinguishes processed public figure data from raw records available upon request. This is not another claim that no online data exist.

The [curated reference](../Data/03_Research/source_feedback_protocol_references.json) records immutable source hashes, code commit, archive identity and inspected member headers. The archive is 377,463,133 bytes; it was NOT downloaded. Bounded HTTP ranges inspected 95 directory entries and only three header lines from each of two CSVs. A ZIP tail/prefix includes compressed bytes; none were decoded as scientific numeric rows. No full-member CRC or whole-archive checksum was certified.

Actual Fig3c experimental/simulation headers say `sep=,` and `detuning Delta,S21 absolute`, while the general README advertises semicolons. A future parser must honor member-level metadata, separate experiment from simulation, and resolve units from the figure/operating-state record. Do not infer displacement, intracavity occupation, phase or uncertainty columns that are not present. This is a header-only finding, not an exhaustive inventory of every member. No article figure already inspected becomes a blind holdout by changing its filename.

The publisher's supplementary PDF was acquired in memory (13,389,457 bytes; SHA-256 `342392fb5ca94bdba5a6b5c6a3b41688aa866f0dec1ea78878f5dfcb6d760538`), with calibration-method text inspected on pages 1-5 of 18. Notes 1-2 describe circle fitting including gain/phase/delay and impedance mismatch, sideband/EMIT coupling checks, and attenuation calibration. The methods are present; they are not an absent prerequisite. Their same-state application, branch identity and joint error coverage for this different static test are not thereby established. No PDF copy or figure is retained; data/code licensing is distinct from the article's NC-ND license.

## B. Internal occupation is not incident power

Define an ordinary optomechanical comparator with cavity resonance `omega_c(x)=omega_c0-G*x`, constant G>0, mechanical mass m>0, stiffness k>0 and optional Duffing beta>=0. The interaction energy is `-hbar*G*n*x`. The positive-force orientation is a declared coordinate convention; it need not equal the author's mechanical-coordinate sign. With `Delta=omega_L-omega_c0`, cavity amplitude half-linewidth a=kappa/2>0 and input coupling rate r>0,

```text
F_m(x)=k*x+beta*x^3
n(x)=r*P/[hbar*omega_L*(a^2+(Delta+G*x)^2)]
F_m(x)=hbar*G*n(x).
```

These are stationary mean-field equations with single-mode linear cavity response; they require corrections when Kerr, heating, frequency-dependent G, other modes or self-oscillation matter. Eliminating n gives

```text
q=(G*r/omega_L)*P
q=(k*x+beta*x^3)*(a^2+(Delta+G*x)^2).
```

The exact polynomial coefficients of x through x^5 are

```text
[k*(a^2+Delta^2), 2*k*Delta*G,
 k*G^2+beta*(a^2+Delta^2), 2*beta*Delta*G, beta*G^2].
```

At Delta=0 and beta=0, `q=k*a^2*x+k*G^2*x^3`: a positive cubic in incident source despite a strictly LINEAR mechanical restoring force. Using q as the prepared invariant u in the prior source-law test would assign intrinsic nonlinearity to the wrong component. With correctly reconstructed n, the same example instead has `hbar*G*n=k*x`. The example demonstrates physical source feedback, not an observer metadata change magically altering the source.

Units: k [kg/s^2], beta [kg/(m^2*s^2)], G [s^-1/m], r,a,Delta [s^-1], P [J/s], n dimensionless. Then hbar*G*n is a force, q has force/time^2, and every polynomial term has that same unit. New test constants below are dimensionless controls, not calibrated apparatus values.

## C. The counterexample can be linearly stable

Do not certify stability from a monotone static curve alone. Retain cavity quadratures and mechanical velocity with dynamics

```text
x_dot=v
v_dot=-Gamma*v-w^2*x+c*n, c=hbar*G/m
alpha_dot=[-a+i*(Delta+G*x)]*alpha+E, n=|alpha|^2.
```

At a fixed point, the exact linearized response is
`delta_n/delta_x=-2*G*n*delta/[(s+a)^2+delta^2]`, where delta=Delta+G*x. Hence the characteristic polynomial is

```text
[(s+a)^2+delta^2]*(s^2+Gamma*s+w^2)+2*c*G*n*delta.
A1=Gamma+2*a
A2=w^2+2*a*Gamma+a^2+delta^2
A3=2*a*w^2+Gamma*(a^2+delta^2)
A4=w^2*(a^2+delta^2)+2*c*G*n*delta.
```

Take the explicit dimensionless family a=3/4, Gamma=10, w^2=c=G=1, Delta=beta=0. At every fixed point x>=0, n=x and E^2=x*(9/16+x^2). With t=x^2>=0,

```text
A1=23/2; A2=265/16+t; A3=57/8+10*t; A4=9/16+3*t
H2=A1*A2-A3=5867/32+3*t/2
H3=A3*H2-A1^2*A4=315375/256+11579*t/8+15*t^2.
```

Every coefficient and Hurwitz determinant is strictly positive. The quartic Routh first column is `1,A1,H2/A1,H3/H2,A4`, so all local eigenvalues have negative real parts by the [Routh criterion](https://ocw.mit.edu/courses/2-004-dynamics-and-control-ii-spring-2008/e098a44ee402a52174eb0f205c5d542f_lecture_25.pdf). This proves LOCAL linear stability for the entire declared mathematical branch, not global attraction or validity of a real cavity model at arbitrarily large displacements. No eigenvalue sweep or long transient simulation is needed. The polynomial identity is checked independently against the exact 4x4 Jacobian determinant at rational fixed points; finite controls supplement the all-t>=0 sign certificate.

## D. What absolute scattering can and cannot reconstruct

Use the publication's hanger-style stationary port convention, not a different one-sided cavity prefactor. Set c_p=kappa_ext/2 with 0<c_p<=a and

```text
t21=1-c_p/(a-i*delta), R=|t21|^2
D=a^2+delta^2=c_p*(2*a-c_p)/(1-R)
E^2=c_p*n_in
n=n_in*(1-R)/(2*a-c_p).
```

Therefore an independently calibrated ABSOLUTE magnitude R, device-input flux n_in, port coupling and linewidth can determine the stationary internal occupation WITHOUT optical phase. Do not overstate magnitude-only data as universally useless. Domain checks are essential: 0<=R<1, D>=a^2, known calibration/operating state and stationary single-pole transfer. The quoted CSV is `S21 absolute`, so R is its SQUARE, not the magnitude itself. R=1 or c_p=0 does not provide this finite inverse; incompatible measurements cannot be rescued by clipping. An R interval touching 1 leaves the detuning enclosure unbounded, even though some occupation bounds can remain finite.

Magnitude alone gives `delta=+/-sqrt(D-a^2)`. If a displacement is inferred from `delta=Delta+K*n+G*x`, there are generally two candidate x values. Choosing the branch by assuming the mechanical law under test would be circular. Independently calibrated complex t21 instead gives `c_p/(1-t21)=a-i*delta`; a separately supported branch/continuity record can also resolve the ambiguity. Actual nonlinear or oscillating states need the appropriate full transfer operator; the paper explicitly supplies a different sideband-summed expression there. A manufacturer's resolution or fitted line-shape curve alone is not the joint uncertainty packet.

### The actual circle-fit mismatch must be assessed

The simple magnitude inverse above requires a REAL port coefficient after deembedding. In the more general calibrated notch form `t=1-c_m*exp(i*phi)/(a-i*delta)`, even known mismatch phi changes the result:

```text
R=1+[c_m^2-2*c_m*a*cos(phi)+2*c_m*delta*sin(phi)]/(a^2+delta^2).
(1-R)*delta^2+2*c_m*sin(phi)*delta
 +(1-R)*a^2-2*c_m*a*cos(phi)+c_m^2=0.
```

For a=1, c_m=1/2, cos(phi)=3/5, sin(phi)=4/5 and R=13/20, the candidate detunings are 0 and -16/7. With the SAME independently known intracavity drive intensity E^2=1, their candidate occupations are 1 and 49/305. Thus a known complex mismatch can leave occupation ambiguous too, not only displacement. Here c_m is the circle-fit coefficient magnitude, not automatically the physical input-coupling rate; E^2 requires its own calibration. These are abstract transfer controls, not measured parameters. Additional physical-domain or phase/branch evidence may exclude a candidate, but cannot be supplied by assuming the constitutive relation being tested. Retain the candidate set or resolve it independently rather than applying the ideal inverse to arbitrary normalized |S21|.

## E. Protocol decision and useful next test

The public processed archive is a concrete and licensed source of scattering data, but the inspected Fig3c columns are NOT admitted as the static prepared-source/displacement pair. Do not run a cubic fit on these columns or call them UET validation. Header/source inspection, not numerical response exposure, is sufficient to reject that shortcut.

Two legitimate paths remain:

1. For an **effective constitutive test**, reconstruct internal occupation and an independent displacement from a calibrated stationary complex transfer or justified branch record. Bound Kerr, photothermal, geometric and time-dependent corrections jointly. Freeze the source/readout/calibration policy and separate data roles before a reserved input is scored with the existing cubic prediction-set rule.
2. For an **instrument/operator benchmark**, use the public processed curves with the native nonlinear cavity model and keep the objective limited to source/readout reproduction. That may validate implementation or apparatus modeling, not supply a new UET-specific relationship. No long author simulation is launched merely because code exists.

The first path needs same-state absolute input/port/linewidth, displacement/branch and uncertainty records. The second is a different scientific question; do not quietly substitute it for theory testing. Earlier action-class equivalence still controls unique UET claims. This result closes the source-feedback false-positive question and makes the next observation packet specific; it does not close Full Topic13 or prove a real material's cubic response.

## F. Follow-up: what the candidate phase/time/calibration products contain

Fifteen additional candidate member headers were inspected using 129,878 range bytes, with the same directory identity and no numeric response rows decoded. Together with the earlier two Fig3c members, this is 17 selected schemas, not an exhaustive assertion about every archive payload.

| Candidate group | Header evidence | Admitted role and restriction |
| --- | --- | --- |
| Fig9 continuous/pulsed b/c | `freq` and absolute S21; pulsed up/down columns | Frequency sweeps, not time or complex-phase records merely because the filename says pulsed |
| Fig6 | Frequency, S_ww data and S_ww fit | Calibration spectrum and model fit distinguished; the fitted column is not a second experiment |
| Fig7 a/b | Frequency, absolute S21 and its fit | Calibration magnitude products; no explicit paired real/imaginary record in these headers |
| Fig8f | Parameters, n_c and P_d dBm from n_c | Derived calibration product; not an independent n-versus-power validation pair |
| Fig11 a/b | First-author and comparison metrics | Literature/comparison-table role, not a new same-state detector trace |
| Fig12 a/b | Frequency, Fourier of beta_r / alpha | State-spectrum products. Header alone does not admit measured-versus-simulated origin, complex-value representation, transform normalization/window or pairing to a physical source |
| Fig14/15/16 selected members | Fixed-point/stability columns, duplicate-solution/imaginary-root comments | Model-root products as declared, not independently measured branch stability; folder/embedded figure labels differ and require explicit binding |

The two Fig12 members would expand to 412,966,875 and 419,426,184 bytes. Their spectra may be useful for their own declared analysis, but loading them is not justified merely to look for an experimental time-domain quadrature record. No claim is made that a properly identified full complex Fourier record could never reconstruct a waveform; that would additionally require its sampling, transform/window, preparation and source lineage.

### Why a derived calibration column cannot independently confirm its own formula

If a published pipeline calculates P_est=F(n_est,calibration), then P_est-F(n_est,calibration)=0 by construction. At fixed calibration the pair's Jacobian with respect to n_est is the single column `(1,F')`; it supplies no second independent measured quantity. This does not make calibration invalid. It means the derived pair cannot be reused as an independent validation of the conversion equation. Generator settings, separately calibrated line attenuation and their joint errors could provide the missing external constraint, but must be traced as such rather than inferred from this residual being zero. The source's Notes 1-2 calibration methods remain useful evidence; no claim is made that the original authors performed a circular validation.

**Minimum next product for unique state reconstruction:** a state-identified experimental complex transmission record (or a documented independent branch equivalent), paired device-input source settings, the corresponding transfer calibration/deembedding record, and a joint uncertainty/omission description. Separate calibration rows from candidate comparison rows. The current selected schemas do not admit this packet. This is not proof that no such record exists elsewhere, nor authorization to request it by email. Do not substitute computed fixed points or spectra of an unadmitted state for experimental phase data. The necessary-condition test below can sometimes reject a model WITHOUT unique state reconstruction, so missing phase must not be made a blanket prohibition on every diagnostic.

## G. A phase-free necessary-condition test is possible

Supplementary Note 6.1, Eqs. (18)-(21), fixes the stationary native hypothesis

```text
K_eff=K+2*g0^2*Omega_m/(Omega_m^2+Gamma_m^2/4)
delta=Delta+K_eff*n.
```

K, g0, Omega_m and Gamma_m must be locked from the independent calibration role, not fitted to the comparison rows. This is a standard native model relation, not a new UET coefficient prediction or a mapping of the cavity mode to the covariant matter field. The ideal real-port magnitude inverse in section D constructs n_R and delta_R^2 independently of this mechanical relation. Therefore every admitted stationary observation must satisfy

```text
F(R,Delta,n_in;calibration)=(Delta+K_eff*n_R)^2-delta_R^2=0.
```

F has angular-frequency-squared units. It does NOT choose the hidden detuning sign from the model and then call that choice independent validation. With a predeclared joint calibration/measurement/omission set, exclusion of zero from the possible F values rejects this specified stationary source/readout hypothesis. Inclusion of zero is merely non-rejection: the unmeasured sign, model class and other candidate branches are not verified. Multiple rows must share the SAME admitted calibration parameters; separately retuning each row is forbidden. Per-row inclusion is not proof that one common parameter tuple explains all rows.

At Delta=0, the necessary condition is insensitive to the sign of K_eff. At known nonzero detuning,
`F(K_eff)-F(-K_eff)=4*Delta*K_eff*n_R`. Thus an independently calibrated detuned control can distinguish these restricted sign hypotheses without measuring phase, when the projected joint-error sets separate and the stationary domain is independently justified. The exact controls use one on-resonance and one detuned setting; they are not measured acceptance or a prescription to ignore dynamical instability. This is an information-bearing protocol change, not a request to run a larger arbitrary parameter grid.

### Retaining complex mismatch instead of setting it to zero

For known complex circle coefficient c_m*exp(i*phi), known drive intensity I=E^2 and R=|t|^2, keep n>=0 latent and require BOTH

```text
F_n=n*[a^2+(Delta+K_eff*n)^2]-I=0
G_n=I*(R-1)-n*[c_m^2-2*c_m*a*cos(phi)+2*c_m*Delta*sin(phi)]
    -2*c_m*K_eff*sin(phi)*n^2=0.
```

These two polynomial constraints eliminate phase as an independently required record, not the physical effect of mismatch. Failure of every nonnegative n and every common admitted calibration tuple is a valid rejection condition; selecting a convenient n and proclaiming a measured occupation is not. No global uncertainty-feasibility solver or physical numerical threshold is claimed by the finite controls. For actual oscillating data use the sideband/time-dependent native operator instead: the stationary cubic condition is outside its domain.

**Revised next dependency:** raw phase is useful but not logically necessary for this projected falsifier. What is necessary is a matched independent source/transfer calibration, a justified stationary-data role, and bounded joint errors. If those are available from public calibration products, a necessary-condition diagnostic can proceed on magnitude data; if not, do not invent real-port deembedding or reuse model-derived power as independent input. Even a successful native-model comparison would not overcome the earlier UET/comparator equivalence result.

## H. Rejecting a shared model without knowing the absolute input scale

Absolute flux calibration is necessary for a physical occupation or separate K_eff measurement, but not for every model-class rejection. Suppose the stationary, real-deembedded transfer has independently known shared a and c_p. Let p_i>0 be a known RELATIVE PHOTON-FLUX setting and n_in,i=C*p_i with one unknown C>0 shared across the admitted records. Linear relative power needs its known photon-energy/frequency conversion before being called p_i; dBm is not a linear p_i. Frequency-dependent attenuation, gain, linewidth or operating-state drift must be bounded, not silently assigned the same C/a/c_p.

From the transfer independently construct

```text
d_i=c_p*(2*a-c_p)/(1-R_i)-a^2 >= 0
X_i=p_i*(1-R_i)
b=K_eff*C/(2*a-c_p)
q_i(b)=X_i^2*b^2+2*Delta_i*X_i*b+Delta_i^2-d_i.
```

Every admitted stationary row of this restricted family must have q_i(b)=0 for ONE common real b. With dimensionless relative flux p_i, b has angular-frequency units and q_i has angular-frequency-squared units. The C-to-K_eff transformation C->lambda*C, K_eff->K_eff/lambda (lambda>0) leaves every q_i unchanged. Consequently, a surviving b cannot identify either physical quantity separately. Additional independent information is needed for those quantities, not necessarily to reject the shared forward-model family.

For exact rational controls, compute the monic polynomial gcd of all q_i. A constant nonzero gcd excludes every common complex root, hence every common real b. A linear gcd has one real candidate; a quadratic additionally requires a nonnegative discriminant. Identically zero constraints give no information, not validation. The verifier explicitly supports degree <=2 only. This is an exact algebraic diagnostic; equality/gcd of rounded measured CSV values is NOT a valid physical rejection rule. For actual measurements use admitted joint error/omission sets and ask whether ANY one common tuple survives. No global interval feasibility implementation or confidence threshold is claimed here.

Two exact controls expose the information gained by sharing parameters:

- q_1=b^2-1 (on resonance) and q_2=b^2+b-2 (detuned) have gcd b-1. The first sign ambiguity is removed without measuring phase or separately calibrating C.
- q_1=b^2-1 and q_3=4*b^2-1 each admit real candidates alone, but their common gcd is 1. No common b exists. Refitting each row would conceal this incompatibility.

These controls are in the same abstract real-port domain as section G, not measured records or evidence for a new UET coefficient. This restricted native-model route can therefore investigate common-parameter compatibility before requiring an absolute source anchor. Real-port deembedding, relative-input lineage, stationarity and joint errors remain necessary. The complex-mismatch operator in section G cannot be replaced by this shortcut when its real-port conditions are unestablished.

### The actual time-averaging operator is not innocuous

The source's pulsed protocol (main text, pulsed-measurement section and Fig.3) records complex S21(t), waits within a 1.4 s pulse and averages the final 2 ms, with 0.8 s equilibration between pulses. This is evidence for its acquisition/processing method, not independent proof that every plotted point is a static fixed point. The paper deliberately includes self-oscillating regions and uses a different operator there.

In general, |mean(t)|^2 differs from mean(|t|^2); their difference is the nonnegative temporal variance. For t=1/2+i/2 and 1/2-i/2, the former is 1/4 and the latter is 1/2. A magnitude column from an averaged complex carrier cannot be inverted as a sequence of instantaneous stationary magnitudes without a justified state/averaging bound. This is an observer/processing effect; it does not create or remove the source backaction in sections B-C. A model-predicted stable root alone is not an independent measured stationarity check, and post-hoc removal of disagreeing rows is not an admissible selection policy.

**Narrower next prerequisite:** establish relative-flux and real-port calibration lineage and an independently justified stationary selection/error policy for a shared-scale diagnostic. An absolute C/K_eff split and unique phase reconstruction are optional additional identification tasks, not blanket prerequisites for all rejection tests. No measured score is admitted in this wave. The earlier action-class limitation on unique UET claims remains unchanged.

Reproduction: [producer](../Code/03_Research/Research_T13_Source_Feedback.py), [controls](../Code/03_Research/test_t13_source_feedback.py), [contract](../calculation_contracts/source_feedback.json), [canonical output](../../../core/07_artifacts/topic13/t13_source_feedback.json). The curated header/reference file is the input; no numerical experimental row or copied archive is needed for these formal results.
