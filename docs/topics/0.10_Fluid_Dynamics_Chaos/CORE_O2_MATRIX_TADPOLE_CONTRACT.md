# SD04 finite-density matrix tadpole and auxiliary stationarity contract

Date: 2026-10-13. Topic10 secondary shared Core/Topic13 derivation.
Role: PREREGISTERED_CONDITIONAL_STATE_PREREQUISITE_ONLY.
Prior: [SD03](MATERIAL_FRAME_EOS_HANDOFF.md).

## Question and acceptance

Can SD01's changed gHF approximation reuse normal scalar tadpoles/subtraction,
or does finite-density mixing require its own matrix and stationary-source chain?
Derive kernel/residues, IR/UV behavior and auxiliary stationarity. Accept only
exact analytic identities plus locked independent integrand checks and negatives.
No state root, momentum-integrated thermal EOS, physical scheme selection,
new material benchmark or gate promotion. Retain first execution before repairs.
Stop after this discriminating derivation, not another benchmark expansion.

The [published Core handoff](../../core/03_lanes/topic13_support/CORE_HE4_SAME_STATE_HANDOFF_2026-10-04.md)
and its [artifact](../../core/07_artifacts/topic13/core_he4_same_state_correspondence_2026_10_04.json)
keep same-state atomic current, action/measure, mu reference and low-T remainder
open. Main PR34 is incorporated unchanged; SD01-SD03 remain draft dependencies.
The 1.7K calibration is not transferred to low-T states. This derivation supplies
natural-unit state prerequisites only, not those missing physical inputs.

## Kernel and equal-time matrix

Use SD01 notation x=rho^2,Y=M^2,D=delta M^2 (each E2); mu,k,omega,T have E1,
lambda is dimensionless, Q_ab:E2. D is splitting, not a counterterm; Q_ab and
diagram-functional Phi are distinct from UET Q/Phi. Fix homogeneous zero
superflow and condensate phase. At symmetric coincident frequency integration
Q12 vanishes, but G12 and its dynamic/source variations need not vanish.
Let A=k^2+Y+D-mu^2, B=k^2+Y-D-mu^2, omega_n=2*pi*n*T:

    K=[[omega^2+A,-2mu*omega],[2mu*omega,omega^2+B]]
    det K=(omega^2+A)*(omega^2+B)+4mu^2*omega^2
    R=sqrt(4mu^2*(k^2+Y)+D^2)
    eH/L^2=k^2+Y+mu^2 +/- R; Delta=eH^2-eL^2=2R>0
    wH11=(eH^2-B)/Delta; wL11=(B-eL^2)/Delta
    wH22=(eH^2-A)/Delta; wL22=(A-eL^2)/Delta
    Qii=int d^3k/(2pi)^3 sum_j wij*coth(ej/(2T))/(2ej)

H/L mean upper/lower, not the paper's e-label convention. For k>0 the declared
stable rest domain is Y-mu^2>=abs(D), with positive nondegenerate poles.
Evaluate eL^2=A*B/eH^2 when needed to avoid cancellation. Invalid/degenerate
numeric interface inputs are rejected; degeneracy requires a separate limit.
I_plus=Q11+Q22,I_minus=Q11-Q22. For D>0 the unsubtracted thermal I_minus
integrand is negative because nB(e)/e decreases with e; renormalized I_minus
need not share that sign. Dropping mixing changes modes and residues.
On Y=mu^2+D,D>0, eL^2=D/(D+2mu^2)*k^2+O(k^4); eH(0)^2=2D+4mu^2.
The lower-pole thermal radial Q22 integrand tends to T; the Q11 contribution
tends to zero, before the measure factor 1/(2pi^2). These 3D tadpoles are IR
integrable; source/transport derivative integrals are not thereby certified.

## One-loop derivative and subtraction, not full 2PI renormalization

L=int[ell+T*sum_j log(1-exp(-ej/T))], ell=(eH+eL)/2, at a fixed common
regulator. Off-shell 2L_Y=I_plus,2L_D=I_minus. At zero superflow:

    ell=k+Y/(2k)-(Y^2+D^2)/(8k^3)+O(k^-5)
    E0=sqrt(k^2+Y0), Y0>0 fixed independently of T,mu
    ell_R=ell-E0-(Y-Y0)/(2E0)+((Y-Y0)^2+D^2)/(8E0^3)

ell_R is O(k^-5); tadpole subtractions must be its derivatives. Omitting D^2
leaves a logarithmic divergence. The divergent coefficients have no explicit
mu, but Y,D may depend on medium. The finite-mu vacuum difference must remain.
A moving Y0 adds source derivatives. This is a one-loop finite subtraction
candidate, not full modified 2PI counterterm/source or superflow/metric analysis;
normal/paper Hartree counterterms are not imported. No physical Y0 is chosen.

## Auxiliary stationarity before imposing Ward

With U=(m_squared-mu^2)*x/2+lambda*x^2/4, AY=Y-m_squared-2lambda*x,
AD=D-lambda*x, define at a common finite regulator (or conditionally for a
same-source finite L and justified corresponding modified functional):

    Omega_g=U+L-AY^2/(8lambda)+AD^2/(4lambda)
    =L-(Y-m_squared)^2/(8lambda)+D^2/(4lambda)+x*(Y-D-mu^2)/2.

The changed traceless sign follows SD01, not old Hartree. This is an auxiliary
stationary representation, not a minimum in all its variables. For x>0 its
unrestricted gradients give AY=2lambda*I_plus,AD=-lambda*I_minus and
Omega_x=(Y-D-mu^2)/2=0. After variation, restrict Y=mu^2+D:

    D=mu^2-m_squared-2lambda*(I_plus+I_minus)=mu^2-m_squared-4lambda*Q11
    x=D/lambda+I_minus.

Restricted Omega loses x; recovering x from the unrestricted gap equation is
mandatory. Arbitrary x is not a stationary witness. Existence/uniqueness,
positive D/x, full stability and regulator/reference control remain untested.
At fixed Y,D,x, Omega_mu=L_mu-mu*x, so stationary n=mu*x-L_mu.
The reduced source derivative agrees only after gap equations and x recovery;
SD02's implicit Hessian and SD03's material map remain separate obligations.

## Locked independent controls and claim ceiling

Synthetic integrand point k=1,Y=5,D=1,mu=1,T=1/5; gapless IR control mu=1,D=2,
T=1/5,k=1e-8; UV controls k=1000/2000,Y0=3,60 decimal digits. Numerical steps/
tolerances are in the frozen contract. They check implementation, not new states.
Exact SymPy checks include dropped mixing, Hartree-sign, scalar-only subtraction,
moving reference and early-Ward/arbitrary-x negatives. Independent direct
frequency integrals, trace-log finite differences, high-precision UV/IR and
fresh-source/scope guards are tested. No fitting or threshold relaxation.
All ten method gates, sixteen false admissions and null physical scales remain.
Controller: finite_density_gHF_integral_state_renormalization_and_external_source_vertex_not_admitted.

[Alford et al.](https://arxiv.org/pdf/1310.5953), v2 rest kernel and appendix A2/A3/
Table I: selected matrix/vacuum conventions only, not original stationarity or
counterterm transfer. [Gapless HF](https://arxiv.org/pdf/hep-ph/0506157), v2
9-18/III: phenomenological functional already normalized in SD01. No figures,
material calibration, full-paper replication or physical response is produced.
