# O(2) gapless Hartree-Fock functional candidate and method comparison

Date:2026-10-02. Conditional source algebra, not solved tadpoles/EOS or method admission.
Prior: [method/source audit](CORE_O2_INTERACTING_METHOD_ADMISSION.md).
Overall/selected physical controllers remain unchanged.

## Source comparison and decision

| Route | Source scope actually reviewed | Research decision |
| --- | --- | --- |
| Original finite-density Hartree | Alford1310.5953v2 II, previous conditional residual audit | Retain stationary background comparator; internal Goldstone gap is not a physical gapless-mode admission |
| Alford gapless replacement | Same source II.3/pressure | Comparison only; original stationarity/pressure cannot be inherited |
| Symmetry-improved CJT | Pilaftsis/Teresi1305.3221v2 selected3/6; Brown2016 author abstract only | Distinct constrained scheme; finite-density and dynamic-source consistency need their own derivation |
| Stationary 2PI plus external vertices | van Hees/Knollhep-ph0203008v3 III/V/VI selected passages | External source-response route for auditing; internal/external propagators remain distinct |
| Gapless Phi-derivable Hartree-Fock | Ivanov/Riek/van Hees/Knollhep-ph0506157v2 II/III/VI selected passages | Next conditional finite-density functional candidate; phenomenological modification is explicit |
| Large-N/strict perturbative comparator | 0203008v3 V.C plus old Gaussian approximation boundary | Alternative comparison; no N=2 error or selected low-T regime certification |

[Gapless HF source](https://arxiv.org/pdf/hep-ph/0506157), equations9-18,
modifies the functional by an invariant tadpole term while retaining its mean-field
equation. Its correction is phenomenological. Finite-T scale dependence and
limiting-temperature branches persist. Selected sections were reviewed, not all
proofs or figures replicated. The paper's renormalization scale mu is not our
chemical potential mu; no quoted sigma/pion calibration is imported.

[External-vertex source](https://arxiv.org/pdf/hep-ph/0203008), v3 equations19-31,
constructs response from a stationary 2PI background. Its external Goldstone
property does not remove artifacts inherited from internally gapped lines.
Feedback of external lines defines a changed scheme, not a free repair.
This source guides a separate response obligation for our candidate.

The two papers' Phi functionals mean diagram/approximation functionals, not UET
Phi_fixed=.15 or a physical temperature. All material/transport claims stay open.

## Conditional O(2) normalization and polynomial variation

Canonical real doublet phi has unitsE1; Q_ab is the symmetric coincident tadpole
matrix, unitsE2; Q is not an independently sampled physical state. This
Q_ab tadpole is unrelated to the vector-state Q=Dt Phi. The mean
doublet phi is also distinct from UET Phi. Lambda here
is the existing canonical quartic coupling. Source lambda_paper/N=lambda_here,
so at N=2 lambda_paper=2lambda_here. Classical potential is
(m_squared-mu_charge^2)*phi^2/2+lambda_here*(phi^2)^2/4.
Chemical potential has unitsE1 and remains the same selected1.28.

For symmetric Q=[[a,c],[c,b]], define
V2_H=lambda/4*((tr Q)^2+2tr(Q^2)).
The source modification after normalization is
DeltaV2=-lambda/2*(2tr(Q^2)-(tr Q)^2).
Thus V2_g=lambda/4*(3(tr Q)^2-2tr(Q^2)).
Both have unitsE4. They are proposed approximation-functional terms; the new
term is not newly derived from the unmodified microscopic diagram expansion.

Use the source definition delta V2=(1/2)tr(Sigma delta Q). Independent diagonal
variation gives Sigma_11=2partial_a V2, Sigma_22=2partial_b V2, whereas the
single symmetric off-diagonal coordinate gives Sigma_12=partial_c V2.
Consequently Sigma_H=lambda*((tr Q)I+2Q) and
Sigma_g=lambda*(3(tr Q)I-2Q). Losing the off-diagonal factor or using the paper
coupling without its N normalization changes the source equations.

Let d=m_squared-mu_charge^2, x=phi^T phi. At fixed Q the shared mean-field
residual is h=(d+lambda*x+lambda*tr Q)*phi+2lambda*Q*phi, unitsE3.
The static internal gHF inverse block is
K_g=(d+lambda*x)I+2lambda*phi phi^T+Sigma_g, unitsE2.
For J=[[0,-1],[1,0]], direct 2x2 multiplication gives K_g Jphi=Jh
for arbitrary symmetric Q and phi. This is an off-shell polynomial identity.
At a nonzero stationary mean field h=0, it gives a static zero mode K_g Jphi=0,
conditional on using this modified self-energy and mean-field equation together.

With phi=(rho,0), I_plus=a+b,I_minus=a-b, the shared h/rho is
d+lambda*rho^2+lambda*(2I_plus+I_minus).
Modified Dyson parameters are
Y=m_squared+2lambda*rho^2+2lambda*I_plus,
D=lambda*rho^2-lambda*I_minus.
The original Hartree sign was D=lambda*rho^2+lambda*I_minus.
Hence Y-D-mu_charge^2=h/rho for the modified functional. The prior residual
identity remains algebraically valid but its original three stationary equations
are not the new functional's equations. No old artifact or failed witness changes.

Use the same synthetic rational I_plus1/20,I_minus=-1/100,0,1/100,mu128/100,
m_squared1,lambda1/100 for conditional comparison; no temperature integral.
The old stationary x is shared, but D changes. Drop DeltaV2 or halve its normalized
coefficient as negatives. Use off-shell Q/phi with c nonzero and exact rational
rotation R=[[3/5,-4/5],[4/5,3/5]] to test covariance; no fitted numbers.

## External response and thermodynamic derivatives still required

Write Gamma[phi,G;A,g] for the proposed source-varied 2PI action, and
G_star[phi;A,g] for a differentiable solution Gamma_G=0. Chain differentiation,
where the pair-space Hessian is invertible on a declared admissible domain, gives
H_ext=Gamma_phiphi-Gamma_phiG*(Gamma_GG)^(-1)*Gamma_Gphi.
This is a conditional derivation. Frozen-G field curvature, internal G^-1 and
the source-varied H_ext are three different objects. A global static zero mode
does not supply the frequency-dependent local Ward or stress/heat vertex.

For thermodynamics eliminate the full stationary state y (mean field and G) in
Omega(y;theta), theta=(T,mu_charge). Fix the global phase or restrict to its
quotient before asserting Hessian invertibility. Then p=-Omega_star,
p_theta=-Omega_theta and
p_thetatheta=-Omega_thetatheta+Omega_thetay*(Omega_yy)^(-1)*Omega_ytheta.
All terms need the same measure, sources and counterterms; a Legendre identity
defined from output densities alone is not an independent derivative check.
For V4 density and state variable y_i of unitsE^d_i, Hessian block ij has
unitsE^(4-d_i-d_j); both Schur terms have identical units. Functional kernels
also require explicit coordinate/measure factors before numerical use.

Core's current two-channel ladder and finite-grid Bethe-Salpeter interfaces
are normal-branch projected collision resolvents. Their kernel gamma_ref I-L
is not delta Sigma_g/dG. Their declared exclusions prohibit importing them as
the condensed field-theoretic vertex. Original Core definitions stay untouched.

## Prelocked audit and next controller

Exact Fraction polynomial derivatives through symmetric +/-steps must reproduce
both self-energies, off-shell Ward/covariance identities, unit scale2 and negative
controls. Check nonzero off-diagonal tadpoles and three original/modified
stationary witnesses. Algebra has no sampling tolerance. Source/contract/card/
registry and prior156-check input hashes must match before running.

No condensed integral state, counterterms, stability/pressure derivative, external
Bethe-Salpeter vertex, retarded positivity, interaction-width/transport, material
frame/SI or Topic13 protocol is computed. All ten physical method obligations
remain NOT_STARTED, even when this proposed functional algebra passes.

Next method controller:
finite_density_gHF_integral_state_renormalization_and_external_source_vertex_not_admitted.
First derive the full finite-mu matrix tadpole/state and subtraction/source
contract for this changed functional; compare stable branches and implicit
derivatives. Derive its own delta Sigma/dG external response before assigning
Goldstone lines or rates to transport. Old tree collision/current/source artifacts
remain historical comparators, not dressed-state evidence.
