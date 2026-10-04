# Condensed interacting method admission: normal Hartree is not a branch bridge

Date:2026-10-02. Source/branch/algebra audit; no condensed state computation.
Prior: [leading mean density](CORE_O2_DENSITY_BACKREACTION.md).
Overall physical controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.
Selected controller remains useful_certified_current_error_and_interacting_Noether_heat_frame_material_correspondence_open.

## Local reuse before new implementation

Core already has thermal normal self-energy, normal Hartree thermodynamics and
renormalized normal Hartree modules. They supply reusable numerical conventions,
stationary normal thermodynamic bookkeeping and a declared subtraction scheme.
Their state flags exclude condensate/two-fluid/Kubo/SI contributions. Current
original source definitions will be executed at the same selected T=.002/.004,
mu1.28,mass_squared1,lambda.01 and a separate prelocked normal control T=.2,mu.3.
A rejected normal gap is branch-specific, not a no-go for condensed solutions.
Neither old normal closure labels nor a returned dressed mass admit our condensate.

## Primary method comparison and counterevidence

[Alford et al. 1310.5953v2](https://arxiv.org/html/1310.5953v2), II.1-III and
equations13-14/18/23/27, supplies the finite-density condensed 2PI/Hartree
comparison. Its gapless modification sacrifices original stationarity and
uses a different pressure evaluated at the constrained point. Source derivatives
must retain implicit state dependence. Sunset omission and critical-region
accuracy are additional obligations; no paper thermal solution is reproduced.

[Pilaftsis and Teresi 1305.3221v2](https://arxiv.org/html/1305.3221v2), sections3/6,
replaces a field extremum condition by a Ward constraint and discusses pressure/
thermodynamic consistency. This is a distinct method, not the Alford modification
or an automatic finite-density/superflow implementation for UET.
[Brown et al. 2016 author record](https://researchonline.jcu.edu.au/44119/)
reports linear-response pathologies of the studied symmetry-improved O(N)
construction. Only its abstract/metadata were accessible here; arXiv1603.03425v2
full-text fetch failed. This motivates an independent dynamical-source gate;
it is not a no-go for every gapless or conserving method.

## Exact conditional residual algebra

At zero superflow let x=rho^2, Y=M^2, D=delta M^2 and I_plus/minus be tadpole
sum/difference. Lambda is dimensionless; x,Y,D,I_plus,I_minus have unitsE2.
For the three source-transcribed Hartree equations define
R_rho=Y+D-mu^2-2lambda*x,
R_Y=Y-m^2-2lambda*x-2lambda*I_plus,
R_D=D-lambda*x-lambda*I_minus,
R_G=Y-D-mu^2.
Hence R_G=R_rho-2R_D-2lambda*I_minus. Original stationarity implies
R_G=-2lambda*I_minus; it does not imply zero Goldstone inverse propagator.
The zero-energy determinant is (Y+D-mu^2)*(Y-D-mu^2), unitsE4.

If source equations23 enforce D=lambda*x=Y-mu^2 and preserve R_Y=0,
then R_rho=R_G=R_Y=0 but R_D=-lambda*I_minus. Except I_minus=0, the original
three residuals and this gapless replacement cannot all vanish. This is an
exact algebraic consequence conditional on these equations, not a UET/EOS
solution, universal no-go or computation of tadpole integrals.

Fraction witnesses use mu128/100,m_squared1,lambda1/100,I_plus1/20 and
I_minus=-1/100,0,1/100. These are synthetic algebra controls in natural units,
not inferred physical thermal inputs. Both tadpole components are nonnegative.
Changing a coefficient provides a nonzero negative control; scale2 distinguishes
residualE2 from determinantE4. No witness changes the old collision state.

## Prelocked runtime and method gate

Execute original source definitions with closed response Phi.15,Z1,mass_squared1,
lambda.01. Both normal solvers at selected states and Gauss64/128/256 must reject
with their exact declared normal-branch exception. A separate normal control
T.2,mu.3 must return normal-only states with gap/functional residual<=1e-8,
Legendre relative error<=1e-8 and last-order mass/pressure refinement<=1%.
Source extraction is verbatim; any quadrature memoization retains original values.
The normal solver cutoff belongs to that solver; it is not the old60T/c_s domain.

Before a condensed implementation can be admitted, require separate evidence for:
condensed stationary/constrained action and state; full matrix Dyson equations;
Goldstone/source Ward; declared counterterms/scheme; correct pressure and implicit
thermodynamic derivatives; source-varied dynamic vertices/causal response;
collision/dissipation correspondence; approximation regime/sunset control;
material heat/frame/SI mapping; Topic13 EOS/independent protocol.
All remain NOT_STARTED here. Closing a normal lane or satisfying one constraint
does not satisfy this matrix. No formal/interval/material/physical J04/J05/J06
or useful continuum error certificate is produced.

Next narrower method blocker:
condensed_twoPI_stationarity_Goldstone_and_source_response_contract_not_admitted.
Compare candidate conserving/gapless schemes on these same separate obligations
before selecting a numerical condensed solver; preserve old source/results/gates.
