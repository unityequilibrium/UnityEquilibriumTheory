# Formula Audit: 0.10 Fluid Dynamics and Chaos

## Scope

This registry covers the current primary benchmark gate and the formulas that directly
support it: the embedded simplified Navier-Stokes comparator, the UET master-equation update,
the UET 2D fluid mobility bridge, the stress-test stability check, and the speedup metric.
Many exploratory fluid scripts exist, but they are not promoted here unless a verifier
artifact ties them to data, thresholds, and units.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `FD-NS-DIFFUSION` | `u <- u + dt * nu * Laplacian(u)` and same for `v` | `Proof_Turbulence_Benchmarks.SimplifiedNSSolver.step` | `u`, `v` dimensionless velocity arrays in embedded benchmark; `dt` solver time units; `nu` dimensionless benchmark diffusivity; `dx`, `dy` unit-square spacing | `benchmark_anchor`; embedded simplified comparator | `checked local comparator formula` | primary speed baseline | Comparator is not a full CFD solver; speedup can overstate practical CFD advantage if treated as external validation. | Add external CFD validation cases and compare against a documented solver/version. |
| `FD-NS-POISSON-JACOBI` | `p_ij <- 0.25*(p_E+p_W+p_N+p_S)` repeated 20 times | `Proof_Turbulence_Benchmarks.SimplifiedNSSolver.step` | `p` dimensionless pressure-like array | `benchmark_anchor` | `checked local comparator formula` | primary speed baseline cost driver | Fixed 20 Jacobi sweeps are an implementation choice and can bias speed comparison. | Record solver tolerance/sweep sensitivity and competitor solver variants. |
| `FD-UET-MASTER-STEP` | `C,I <- UETMasterEquation.step(C, dt, dx, I)` | `Proof_Turbulence_Benchmarks.time_uet_once`; `docs/core/uet_master_equation.py` | `C`, `I` dimensionless fields; `dt` solver time units; `dx=1/grid_size` | `topic_derived_relation` from core UET master equation | `checked local implementation relation` | candidate solver under primary benchmark | If master-equation internals change, speed/stability result may change without topic docs noticing. | Hash core master-equation file in artifact and add formula-level regression tests. |
| `FD-UET-FLUID-LAPLACIAN` | `Laplacian(C) = d2C/dx2 + d2C/dy2` by central differences | `Engine_UET_2D.compute_laplacian` | `C` dimensionless in benchmark; `dx`, `dy` grid spacing | `standard numerical identity` | `identity / checked local implementation` | engine formula registry, not primary artifact gate | Unit-square benchmark may hide physical-unit behavior. | Add physical-unit benchmark with declared density, viscosity, Reynolds number, and boundary conditions. |
| `FD-UET-MOBILITY` | `u = -M * grad_x(C)`, `v = -M * grad_y(C)` | `Engine_UET_2D.step` | `u`, `v` velocity-like arrays; `M` mobility scale; `grad(C)` per length | `heuristic_bridge` via `FLUID_MOBILITY_BRIDGE / mu / rho` when physical properties are used | `heuristic bridge` | engine diagnostic and future physical benchmark path | Mobility bridge can be mistaken for a validated physical constitutive law. | Source-lock physical fluids and validate velocity/pressure fields against external cases. |
| `FD-PHYSICAL-KAPPA` | `kappa = min(mu/rho, stability_limit)`; `stability_limit = 0.4/(dt*(1/dx^2+1/dy^2))` | `Engine_UET_2D._derive_uet_parameters` | `mu` Pa s; `rho` kg m^-3; `mu/rho` m^2 s^-1; `stability_limit` numerical diffusion bound | `source_locked_physics_relation` for kinematic viscosity plus numerical stability cap | `checked local implementation relation` | future physical-unit gate | Stability cap can silently move from physical viscosity to numerical constraint. | Artifact should record whether cap is active for each physical run. |
| `FD-STABILITY-GATE` | `stable = all(isfinite(C_stress))` after stress update | `Proof_Turbulence_Benchmarks.run_benchmarks` | Boolean gate over dimensionless stress field; stress seed `1e6` benchmark amplitude | `benchmark_anchor` | `checked local benchmark gate` | primary stability gate | Finite output does not prove boundedness or smoothness for arbitrary initial data. | Add norm growth metrics and repeated stress amplitudes; separate theorem work from benchmark work. |
| `FD-SPEEDUP` | `speedup = median(t_NS_trials) / median(t_UET_trials)` | `Proof_Turbulence_Benchmarks.run_benchmarks` | runtimes in seconds; speedup dimensionless | `topic_derived_metric` | `metric definition` | primary PASS/FAIL metric; threshold `> 2.0` | Environment jitter or comparator choice can shift the pass result. | Record hardware/runtime metadata and repeated runs across grid sizes. |

## Current Artifact Link

- Primary command: `python docs/topics/0.10_Fluid_Dynamics_Chaos/Code/02_Proof/Proof_Turbulence_Benchmarks.py`
- Artifact: `Result/artifacts/fluid_benchmark_validation.json`
- Current gate: speedup greater than `2.0` and finite stress-test output.
- Claim boundary: internal implementation benchmark only.

## Current Formula Boundary

- The benchmark gate can support speed/stability wording for the embedded comparator and
  configuration.
- It cannot support external CFD accuracy, arbitrary-turbulence generalization, or
  Millennium-problem closure.
- Paper-facing claims require external validation datasets, physical-unit Reynolds-number
  cases, and theorem-target assumptions separated from implementation benchmarks.

## Chaos Diagnostic Formula Addendum

Chaos diagnostic formulas remain separate from the speed gate and constitutive-transport claims.

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `FD-CHAOS-TANGENT` | `delta_x[n+1] = D F(x[n]) delta_x[n]` | `docs/core/uet_dynamical_stability.py` | tangent state in the declared normalized lane | analytic Jacobian of the declared evolution | checked against central finite difference | primary Benettin/QR estimator | numerical instability or an undeclared source JVP is treated as physical sensitivity | admit state-dependent sources only with an explicit JVP |
| `FD-CHAOS-SPECTRUM` | `lambda_i = lim_T log(s_i)/T` | same module and `Research_Chaos_Method_Validation.py` | inverse normalized time; logistic exponent per iteration | standard dynamical-systems diagnostic | validated on linear, logistic, and Lorenz controls | diagnostic method gate | Lyapunov exponent is confused with the free-energy Lyapunov function | retain the terminology and evidence-class separation |
| `FD-CHAOS-RESOLUTION` | `lambda_res = max(delta_dt, delta_dx, 2 SE_block, delta_method)` | same module | same inverse-time lane as `lambda` | preregistered diagnostic gate | checked implementation contract | sign-resolution gate | arbitrary epsilon or one unconverged run controls the classification | add topic-specific spatial/statistical budgets |
