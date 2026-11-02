# SD03 result: material heat/frame and fixed-pressure EOS handoff

Date: 2026-10-05. Owner: Topic10 shared Core/Topic13 secondary derivation.
Status: COMPLETED_SCOPED_DERIVATION_ONLY; material and physical gates still open.
[Preregistered card](MATERIAL_FRAME_EOS_HANDOFF_CONTRACT.md),
[contract](Data/03_Research/fluid_material_frame_eos_handoff_contract.json),
[local registry](Data/03_Research/fluid_material_frame_eos_handoff_registry.json),
[verifier](Code/03_Research/Research_Fluid_Material_Frame_EOS_Handoff.py),
[160-check result](Result/artifacts/fluid_material_frame_eos_handoff.json).

## What changed scientifically

SD03 connects the stationary source Hessian to the physical questions the
secondary Topic10 derivations must eventually answer. It does not solve the
finite-density state or establish a material mapping.

For n=p_mu>0, S=p_T, w=epsilon+p=T*S+mu*n and h=w/n, the linear isotropic-rest
frame heat subtraction is q=j_E-h*j_N. The rotating-generator flux identified
by the earlier tree Ward audit is j_G=j_E-mu*j_N=q+T*(S/n)*j_N.
A linear frame shift changes j_N by -n*delta v and j_E by -w*delta v;
q is invariant but j_G is not. They coincide only in the appropriate zero-particle-
flux frame (or other explicitly degenerate condition), not as a universal identity.
The normal-lane Core Landau/Eckart entropy identity already implements this
structure; SD03 connects its declared scope to the condensed/material gaps.
It does not rerun or extend the normal collision lane.

For the same fully stationary p(T,mu), fixed pressure gives mu_T=-S/n and

    c_p,particle = T/n * [p_TT-2(S/n)*p_Tmu+(S/n)^2*p_mumu].

The exact pressure fixture gives n=9/8, S=3/4, c_p=40/81; the fixed-mu specific
entropy path instead gives 10/27. A pressure path slope 1/7 gives 800/1701,
with correction -40/1701. These are synthetic counterexamples to substituting
fixed-mu or an SVP path into fixed-pressure c_p. Exact second-order pressure
jets and independent rational tangent/Richardson calculations agree. They do
not give a material EOS, speed or physical heat capacity.

An entropy-reference shift S'=S+a*n and mu'=mu-a*T transforms the source
Hessian together; c_p, Gibbs enthalpy and invariant heat remain unchanged.
Using the shifted entropy with the old Hessian fails. This complements the
existing material entropy-coordinate flux/force contract, without inventing an
entropy reference for TN1334. Table8.5's integration-from-zero convention remains
known; transfer to TN1334 and covariance/ancestry remain unresolved.

SI derivative conversion requires pressure, energy/source, temperature, particle
and velocity/measure maps. From pSI=P0*pbar, TK=Theta0*Tbar and
mu_atom=E0*mubar follow nSI=P0/E0*pbar_mu and SSI=P0/Theta0*pbar_T.
The mass-specific c_p factor is E0/(m_atom*Theta0), and heat-flux subtraction
transforms consistently with the velocity scale. A common Bose energy convention
additionally requires E0=k_B*Theta0. A Kelvin gain or e0 alone cannot admit this
whole interface. Rational scaling numbers test algebra only; every physical
scale/charge-per-atom/material covariance field remains null. Existing Topic13
calibration constants and their source bounds are not altered or rematched.

## Existing two-fluid result and covariance are retained at their scope

The [standard material comparator](TWO_FLUID_STATE_EOS_REFERENCE.md) already
contains the full coupled sound quartic and the conditions for a reduced
counterflow branch. SD03 does not compute another sound benchmark. Its exact
heat-flux consequence is q_mass=T*Sigma*(rho_s/rho)*(v_n-v_s) under that
standard linear constitutive convention. Condensate fraction alone is not rho_s.

For the restricted formula c2^2=(r/(1-r))*T*s_mass^2/c_p, logarithmic sensitivity
is g=[1/(r*(1-r)),1/T,2/s_mass,-1/c_p]. First-order relative speed variance is
(g^T Cov*g)/4, with the full joint covariance. A synthetic positive covariance
fixture demonstrates that discarding cross terms changes this budget. This is
not a measured uncertainty, a nonlinear error bound or a certificate of the
reduced branch. The covariance fixture is a separate algebra control, not an
EOS-derived He-II state; its coincident rational numbers imply no particle-to-mass map.
The existing imported EFT domain failure and full pressure/relative-flow/current
admission blockers stay unchanged.

## Retained failure and exact repair

The [first verifier](Result/previews/material_frame_eos_first_verifier.py.txt)
and [first result](Result/previews/fluid_material_frame_eos_first_failure.json)
are retained byte-for-byte:154/156, failing both entropy-current reference shifts.
The initial comparison added a*j_N to the full entropy current but used only
the charge perturbation j_N. Its background velocity was nonzero, so it omitted
a*n*u. The corrected target is J_S'=J_S+a*J_N,total, with
J_N,total=n*u+j_N. This is a total-versus-perturbation caller/target distinction;
the source transform, EOS, current equations, fixtures and locked thresholds did
not change. The two missing-convection negatives now explicitly detect the old
error. Two archive guards plus those negatives give160/160 and112 input hashes.
No failure is discarded, fitted away or renamed into a pass.

Four focused regressions pass (pytest2.36s): independent fixed-pressure tangent/
pressure expansion and entropy quotient, total-current/frame/reference identity,
independent sound-formula covariance derivative/unit factor, and source/archive/
false-scope rejection. No physical numerical model or benchmark was executed.

## Concrete admission handoff

| Required decision | Existing controller/evidence | Current boundary and required evidence |
| --- | --- | --- |
| Same state and source functional | SD02 snapshot/method gates | Regulated finite-density gHF state, counterterms and full source/pair-space vertex still absent; static algebra does not admit them |
| Charge-to-atom/mass mapping | Existing material input requirements: phase_and_UET_correspondence | Value null; derive source normalization, signed-charge versus total-atom relation, measure, density and mass current before using rho=m_atom*n |
| Heat/enthalpy and frame | heat_frame_SI_mapping method gate; Core normal-lane frame contract | Gate NOT_STARTED for condensed/material lane; derive same-state n,w,j_E,j_N and matched experimental zero-flow condition |
| Fixed-pressure EOS | [EOS source card](HE4_FIXED_CONSTRAINT_EOS_SOURCE_CARD.md); requirements c_p/kappa_T/alpha_p/SVP slope | Candidates exist but material values stay null; source-lock held variables, edition/T scale, pressure transfer, uncertainties and covariance |
| Entropy convention | [Entropy source/reference contract](HE4_ENTROPY_SOURCE_AND_REFERENCE_CONTRACT.md) | Table8.5 zero-T integration known; TN1334 transfer and source lineage unresolved; transform flux/force/source Hessian consistently |
| SI and statistical normalization | Topic13 frozen e0/theta_T package; SD03 physical_scales | Physical scales null; establish full pressure/source/atom/velocity map and common thermal-energy convention; no rematching |
| Normal density/relative flow and sound regime | Existing two-fluid comparator and Topic13 conditional operator | No UET material rho_s or normal component admitted; retain full quartic/domain failure, local-equilibrium and frequency/wavelength constraints |
| Covariance and independence | Existing requirements response_protocol_and_covariance | Unknown values/errors remain null; acquire joint covariance or conservative labeled bounds without treating print precision or shared ancestry as independent noise |
| Primary response/probe | [He4 protocol card](../0.13_Thermodynamic_Bridge/HE4_SECOND_SOUND_PROTOCOL_CARD.md) | State, pressure/T90 path, frequency, mode geometry, flow and complex response/error convention needed; compiled viewed rows are not blind/independent targets |
| Dissipation and external claims | Existing dissipative_tensor requirement and J06/J09 | Normal shear alone cannot specify thermal/bulk/mutual-friction response; no conductivity/attenuation/independent-validation claim |

These are handoffs to existing controllers, not new competing gate records.
Graphite TTG/independent alpha/C_src and the full J00-J09 obligations are not
closed or replaced by this He4 interface. Core's C/Phi/Pi/R are not relabeled as
mass/temperature/entropy or an independent reservoir.

All SD01-SD03 handoffs are now completed only at their conditional derivation
scope. Topic10 stays secondary and new benchmark expansion remains deferred.
The next scientific controller remains
finite_density_gHF_integral_state_renormalization_and_external_source_vertex_not_admitted.
Selected useful-current-error/interacting-Noether-heat/frame and overall
vector-origin/material-frame controllers remain unchanged. All ten method gates
and physical J04/J05/J06 remain NOT_STARTED; sixteen admissions false. Full
Topic10 research and the joint physical program remain open. This completed
handoff is ready for the next shared Core/Topic13 state/source decision.

## Provenance and claim boundary

All new files belong to the existing Topic10 Code/Data/Result/document namespaces;
three candidates are registered locally with ontology, units, assumptions,
source/verifier/artifact, failure modes and NOT_ADMITTED observables. Original
Core/Topic13 sources and central registries/gates are unchanged. Five additional
predecessor files matched HEAD after CRLF-only checkout normalization. No central
Core audit rerun or repaired foundation/link gate is claimed; inherited blockers
remain. No raw/private or new material input is published.

[Pitaevskii/Stringari](https://arxiv.org/pdf/1510.01306), selected section1.2,
provides the standard two-fluid and sound-regime reference;
[Hu et al.](https://arxiv.org/pdf/1001.0772), selected sectionsII/III,
distinguishes response probes. SD03's source/ensemble/frame/unit chain is a
conditional derivation, not replication of full papers or independent material evidence.
