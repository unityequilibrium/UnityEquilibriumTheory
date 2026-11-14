# Topic 13 Research Wave: Causal Branch Selection

MAJOR_RESULT_CLOSURE:
`T13_CAUSAL_THERMAL_BRANCH_SELECTION` is `CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED:
- The original conserved-`C` local-gradient Cattaneo equation is retained as a scoped no-go: positive `kappa_C` gives unbounded high-`k` group speed in that declared class.
- The named conserved flux-telegraph `C` branch and its coupled causal `C/Phi` branch pass the locked compact-support, arrival, convergence, mass, energy-ledger, no-clipping, no-padding, and no-fit gates.
- The original full candidate remains a failure with pre-arrival leakage `0.017639381271029236`, above the unchanged `1e-6` threshold.

WHAT_REMAINS_OPEN:
- The selected branch is still normalized. It has no `Phi -> Delta_Tq`, `e0`, or `alpha_Phi_K` map.
- Numeric TTG source closure, non-circular bridge and `beta`, EOS, finite-temperature transport, SK/KMS, entropy current, and dissipative balance remain open.
- The failed conserved-gradient equation stays blocked. The selected branch is not retroactively substituted for it.

DEPENDENCY_UNLOCKED:
Normalized causal-branch input only. No SI thermal, Core curved 3+1, Gravity, transport, or external-validation dependency is unlocked.

STATUS:
`PASS_CLOSED_AS_NO_GO_WITH_NAMED_COUPLED_BRANCH` for causal-branch selection; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` and `PARTIAL`.

WHAT_CHANGED:
Collected the existing no-go, flux-telegraph, and coupled `C/Phi` evidence into one major-result decision. The decision repairs an obsolete flux-branch note that still listed coupled integration as unfinished.

EQUATION_OR_MAPPING:

```text
blocked baseline:
tau_C C_tt + C_t = M_C Laplacian(a_C C - kappa_C Laplacian(C)), kappa_C > 0

selected C/Phi lane:
C_t + partial_x J_C = 0
tau_C J_C_t + J_C = -M_C partial_x(mu_C), kappa_C = 0
tau_Phi Phi_tt + Phi_t + M_Phi mu_Phi = 0
V_CPhi = -coupling_g C^2 Phi / 2
```

The selected lane passes `prearrival_leakage_fraction <= 1e-6`, with nonzero `C` and `Phi` arrival targets and a normalized combined-energy residual `<= 1e-6`.

VERIFICATION:

```powershell
.venv\Scripts\python.exe docs\scripts\audit\audit_topic13_causal_branch_selection.py
.venv\Scripts\python.exe docs\scripts\audit\sync_topic13_causal_branch_selection_into_gates.py
.venv\Scripts\python.exe -m pytest docs/core/test/test_topic13_causal_branch_selection.py docs/core/test/test_topic13_causal_branch_selection_integration.py -q
```

CONTROLLING_BLOCKER:
`selected_causal_branch_is_normalized_and_dimensional_thermal_bridge_remains_open`.

NEXT_ACTION:
Use the selected named branch only as the normalized causal input while independently deriving a physical `Phi` scale or obtaining independent `alpha_Phi_K`, and while closing source and thermodynamic-bridge requirements. Do not relabel the failed baseline as passing.

CLAIM_BOUNDARY:
This is a named internal causal-branch selection. It does not mean `C` is a universal mass/density, `Phi` is temperature or heat flux, `R_gen` is a dynamic substance, the baseline was repaired, or Topic 13/UET is closed.
