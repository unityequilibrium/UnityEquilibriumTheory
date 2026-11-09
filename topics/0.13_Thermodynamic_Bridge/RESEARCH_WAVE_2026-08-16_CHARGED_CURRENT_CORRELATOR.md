# Topic 13 Research Wave: Charged Current Correlator

MAJOR_RESULT_CLOSURE:
T13_UET_O2_CHARGED_CURRENT_CORRELATOR_LANE = CLOSED_FOR_LANE

WHAT_IS_ACTUALLY_CLOSED:
- The charged quasiparticle source is fixed as `b_Jx(s,k,n) = q_s (p_x/E_s) sqrt(w_s)`.
- The source is projected against the declared charge and four-momentum conserved subspace.
- A finite-cutoff retarded current-current response is evaluated from the action-derived conservative collision operator.
- The local contact-SK coupling is matched to the charged transition-kernel normalization.
- Charged KMS/FDT ratios and a positive entropy-production witness are verified.

WHAT_REMAINS_OPEN:
- The continuum limit of the collocation/interpolation construction.
- A loop-renormalized finite-temperature off-shell retarded self-energy.
- A microscopic current vertex and physical Kubo coefficient match.
- Finite-temperature two-fluid completion and covariant entropy-current/heat-flux balance.
- The dimensional Phi-to-thermal map, independent alpha calibration, and Ding-compatible C_src source.

DEPENDENCY_UNLOCKED:
The result unlocks only a named charged finite-cutoff current-correlator/KMS interface. It does not unlock physical transport, SI mapping, Core curved 3+1, Gravity, or Full Topic 13.

STATUS:
PASS_ACTION_MATCHED_CHARGED_CURRENT_CORRELATOR_LANE

WHAT_CHANGED:
Added `uet_o2_charged_current_correlator.py`, its verifier, focused tests, a machine-readable artifact, and an equation-registry addendum. The full-gate integration records this as a lane closure while retaining the physical transport blockers.

EQUATION_OR_MAPPING:
```text
b_Jx(s,k,n) = q_s (p_x/E_s) sqrt(w_s)
G_R^JxJx(omega) = b_Jx,perp^T (L_cont - i omega I)^(-1) b_Jx,perp
rho_JJ(omega) = 2 Im G_R^JxJx(omega)
G^>/G^< = exp(beta_th omega)
N_JJ = rho_JJ coth(beta_th omega/2)
sigma_J = b_Jx,perp^T L_cont b_Jx,perp / T >= 0
```

VERIFICATION:
- `docs/core/07_artifacts/topic13/t13_uet_o2_charged_current_correlator_audit.json`: `PASS_ACTION_MATCHED_CHARGED_CURRENT_CORRELATOR_LANE`; no failed checks.
- KMS maximum relative residual: `1.6337129034990842e-16`.
- FDT maximum relative residual: `1.5143303520891009e-16`.
- Focused regression: `9 passed`.
- No parameter fitting, target data, or Xie 2026 holdout access.

CONTROLLING_BLOCKER:
`loop_renormalized_off_shell_self_energy_and_microscopic_current_vertex_match_missing`, with `continuum_limit_missing` retained separately.

NEXT_ACTION:
Derive the charged finite-temperature off-shell retarded self-energy and its current vertex from the same SK/KMS action, then test whether the finite-cutoff correlator has a controlled continuum limit before any physical Kubo admission.

CLAIM_BOUNDARY:
This is an action-matched finite-cutoff natural-unit interface only. It is not a microscopic off-shell proof, a physical Kubo coefficient, an SI observable, an alpha calibration, a TTG prediction, or Full Topic 13 closure.
