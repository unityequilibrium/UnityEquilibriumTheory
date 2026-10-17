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

Reproduction: [producer](../Code/03_Research/Research_T13_Source_Feedback.py), [controls](../Code/03_Research/test_t13_source_feedback.py), [contract](../calculation_contracts/source_feedback.json), [canonical output](../../../core/07_artifacts/topic13/t13_source_feedback.json). The curated header/reference file is the input; no numerical experimental row or copied archive is needed for these formal results.
