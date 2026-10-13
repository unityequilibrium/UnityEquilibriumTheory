# SD02 conditional stationary source-response contract

Date: 2026-10-05. Owner: Topic 10 shared Core/Topic13 derivation.
Role: PREREGISTERED_CONDITIONAL_DERIVATION; not state/vertex/material admission.
Prior: [SD01 handoff](CORE_O2_GAPLESS_FUNCTIONAL_HANDOFF.md).

## Decision and stopping rule

Derive the gHF coincident-tadpole response tensor and same-stationary-functional
source Hessian, with an exact synthetic discriminating calculation for frozen
versus relaxed state. Link the existing Topic13 source-curvature obligation
without importing its tree/acoustic result as an interacting gHF vertex.
Completion means exact variation, Schur/envelope/coordinate identities and
negative-domain controls pass with locked inputs. A failed identity stops the
wave. No thermal integral, new benchmark lane, numerical gHF state/vertex,
material measurement or physical gate promotion is authorized in this wave.

## New gHF-specific response tensor

SD01 fixes Sigma_g=lambda*(3 tr(Q) I-2Q), whereas
Sigma_H=lambda*(tr(Q) I+2Q). For symmetric variations define T by

    delta Sigma_ab = sum_cd T_abcd delta Q_cd
    T_g,abcd = lambda*(3 delta_ab delta_cd-delta_ac delta_bd-delta_ad delta_bc)
    T_H,abcd = lambda*(delta_ab delta_cd+delta_ac delta_bd+delta_ad delta_bc).

The sum includes both off-diagonal entries. This full-index convention avoids
using the single-coordinate c Hessian with the wrong pair-space factor.
In O(2), T_g has eigenvalue 4lambda on trace matrices and -2lambda on the
two-dimensional traceless symmetric sector; T_H gives 4lambda and +2lambda.
This is a changed approximation kernel even where trace response agrees.
The negative bare traceless eigenvalue is not proof of an unstable state:
full Gamma_GG also contains trace-log/propagator terms and counterterms.
T has dimension E^0 because Sigma:E^2 and Q:E^2. It is neither a collision
rate matrix nor the solved Bethe-Salpeter/external vertex. For a local coincident
Q(x)=G(x,x), distribution/contour/measure and renormalization factors must be
specified before calling it delta Sigma(x)/delta G(y,z) in a full scheme.

## Same-source stationarity and response

Let F(y,s) be a differentiable functional with F_y=0 on a declared branch,
full state y=(mean field, propagator) and external sources s. Restrict to an
admissible phase-fixed/quotient domain on which A=F_yy is invertible. Then

    y_s = -A^(-1) F_ys
    F_star,s = F_s
    F_star,ss = F_ss - F_sy A^(-1) F_ys.

First derivatives use the envelope rule; second derivatives generally need
the state response. For density Omega, p=-Omega_star, n=p_mu, entropy=p_T,
and chi_p=-Omega_ss+Omega_sy Omega_yy^(-1) Omega_ys. These definitions require
the same ensemble, sources, regulator, measures and counterterms. They do not
prove stationarity of an actual interacting state. If Omega_y is nonzero,
the first path derivative additionally contains Omega_y y_s.

For Gamma at fixed mean field, eliminate only G: H_ext=Gamma_phiphi-
Gamma_phiG Gamma_GG^(-1) Gamma_Gphi. For equilibrium source susceptibility,
eliminate all admissible state variables. These are different reductions;
frozen-G curvature and internal G^-1 are not automatically either response.
A singular full Hessian cannot be inverted; deleting a phase direction works
only when the source and mixed blocks respect that quotient. Positive A makes
the pressure relaxation correction positive semidefinite; invertibility alone
does not imply that positivity. A branch switch/critical zero mode requires
separate treatment and does not inherit smooth Maxwell derivatives.

For a stationary generating functional W with a declared background-source
convention, define j=(1/sqrt(abs(g))) delta W/delta A and
T=2/sqrt(abs(g)) delta W/delta g. Their first variations obey the same envelope
rule and their responses require the Schur block and explicit contact/measure
variations. This is a conditional definition, not calculated j or T. Signs and
Euclidean-to-real-time continuation must be fixed in the actual action; W is
not silently identified with the thermodynamic density Omega. Charge mu is
only a declared temporal-source convention, not an SI atom chemical potential.
Gauge/diffeomorphism covariance of the complete regulated source functional
and state is still required before local Ward conservation can be claimed.

## Synthetic exact comparator, not a material benchmark

Prelock one quadratic functional
F=y^T A y/2+y^T B s+s^T D s/2+l^T y+q^T s+constant.
Use the contract's rational A/B/D/l/q/source point and two exact steps. Direct
stationary substitution, central first/mixed second differences and independent
coordinate transforms test the conditional formulas without fit or tolerance.
Prelock three symmetric tadpole variations, the SD01 coupling and scale 2.
Required negatives: frozen curvature when B is nonzero, original Hartree tensor
on a traceless variation, doubled symmetric off-diagonal factor, singular state
inverse, inadmissible phase-source coupling, falsely inferred positivity from
an indefinite A, omitted nonstationary path term and a moving integration bound.
The moving-bound example integral_0^s k^2 dk=s^3/3 shows why fixed-domain
pressure derivatives cannot omit boundary terms on a source-dependent domain.

All these calculations are rational algebra controls. They do not expand the
material benchmark program or certify any actual susceptibility sign/accuracy.
Density source/state variables have declared dimension E in the fixture,
A/B/D dimension E^2, l/q E^3 and F E^4. Coordinate transformations must
transform source gains and Hessians together; they supply no physical gain.

## Reuse and limits of existing Topic13 work

[Tree thermal source curvature](../0.13_Thermodynamic_Bridge/Result/artifacts/T13_THERMAL_SOURCE_CURVATURE_2026-10-03.md)
separates stationary-background, polarization and energy curvature from the
population term in the acoustic thermal pressure Hessian. Its retained artifact
reports PASS_SCOPED_THERMAL_SOURCE_CURVATURE with dynamic contact/virtual-mode/
full-thermal matching open. [Pair-source work](../0.13_Thermodynamic_Bridge/Result/artifacts/T13_ACOUSTIC_SOURCE_PAIR_2026-10-03.md)
uses the same parent source and distinguishes its tree Schur response from
full acoustic/contact/real/thermal matching. These are inspected pinned records,
not rerun or imported numeric evidence in SD02. Their +h Phi source with h:E^3
and chi:E^-2 is distinct from the fixture's dimension-E source and from charge
mu:E. Their parent, quantum-mode admission, source/state and approximation must
be reconciled before composition; source gains and response units cannot be
identified from similar symbols. No Topic13 original action or gate changes.

## Sources and unchanged controlling boundary

[van Hees/Knoll](https://arxiv.org/pdf/hep-ph/0203008), v3 selected section III
and equations 28-31, distinguishes internal lines and scheme-specific external
vertices; signs/contours are not imported by analogy.
[Gapless HF](https://arxiv.org/pdf/hep-ph/0506157), v2 selected section II,
provides the phenomenological functional normalized in SD01. Tensor and
stationary chain calculations here are our conditional derivations.
Full papers/renormalized dynamic solutions are not reproduced.

Method controller remains
finite_density_gHF_integral_state_renormalization_and_external_source_vertex_not_admitted.
All ten method gates and physical J04/J05/J06 remain NOT_STARTED. SD03 requires
the material heat/frame/Legendre/SI and Topic13 EOS/covariance/independent protocol
handoff; no new benchmark expansion. Full J00-J09 scope remains open.
