# Research Wave: C_src Mesh-Tail Extension (2026-08-23)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE
WHAT_IS_ACTUALLY_CLOSED: The source-locked Calorine candidate now includes a fifth q-mesh run at `12x12x6`, using the same `4x4x2` force-constant state as the archived `4x4x2`, `6x6x3`, `8x8x4`, and `10x10x5` runs. The latest `10x10x5 -> 12x12x6` C_src tail is quantified.
WHAT_REMAINS_OPEN: Ding-compatible material/state mapping, source-grade uncertainty, accepted Ding `C_src`, independent `alpha_Phi_K`, the dimensional Phi map, physical transport/KMS/entropy closure, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: C_src numerical mesh-tail evidence only; no Ding, alpha, physical transport, Core, Gravity, or Galaxy dependency unlock.
STATUS: PASS_SCOPED_C_SRC_THERMODYNAMIC_TRANSPORT_DECOMPOSITION; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Added the `12x12x6` persistent PBTE summary and HDF5 output, regenerated the Calorine source package and audit, and refreshed the C_src-versus-transport decomposition plus full-gate/closure/dependency projections.
EQUATION_OR_MAPPING: `C_src(T,V) = (partial u_ph / partial T)_V = V^-1 sum_mu c_mu(T,V)`; `Delta_Tq = Delta_u_ph / C_src`; `Delta_Tq = alpha_Phi_K * Delta_Phi` remains uncalibrated. The latest C_src tail is `0.0010655423065807136`; the latest in-plane RTA kappa tail is `0.128511188152267`.
VERIFICATION: The new run uses the existing hash-locked force constants, reports `C_src` in `J m^-3 K^-1`, passes the candidate mesh preflight, and records no fit, target tuning, alpha calibration, threshold change, or Xie 2026 holdout access.
CONTROLLING_BLOCKER: `ding_C_src_mode_state_and_source_grade_uncertainty_missing` for the decomposition lane; globally `alpha_Phi_K_independent_calibration_missing` and Ding-compatible C_src acceptance remain independent controllers.
NEXT_ACTION: Obtain an authorized Ding numeric package or accepted same-regime PBTE reproduction with source-grade uncertainty and material/state mapping; keep the RTA comparator outside the Phi calibration path.
CLAIM_BOUNDARY: This closes only a numerical convergence sub-lane for an independent Calorine candidate. It is not Ding-regime validation, not a source-grade uncertainty estimate, not an alpha calibration, not a TTG prediction, not external validation, and not Full Topic 13 closure.
