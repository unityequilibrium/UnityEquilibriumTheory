## Entries

### 2026-07-20 - Trace ontology and core-alignment checkpoint

- Scope: `docs/core` trace candidate and compatibility adapter.
- Wave type: artifact pass and claim-boundary pass.
- Added or changed: `TraceKernelConfig`, `UETStepResult`, non-negative
  `sigma_C`, finite-support retarded trace functional, normalized ledger
  proxies, and `spacetime_trace_v1`.
- Files touched: `uet_trace.py`, `uet_master_equation.py`,
  `uet_base_solver.py`, `uet_parameters.py`, trace artifacts and tests.
- Verified with: `.venv\Scripts\python.exe -m pytest docs/core/test/test_spacetime_trace.py docs/core/test/test_spatial_coupling.py -q --disable-warnings --maxfail=1` and `Research_Spacetime_Trace.py`.
- Result: 10 trace tests and 24 combined targeted regression tests pass;
  Cattaneo artifact remains `SIMULATION_ONLY`.
- Blocker narrowed: `I_trace` is now an explicit history functional in the
  trace lane and is not accepted as an independent field state.
- Still open: SI units/ledger closure and a source-backed observable map.
- Next controller: separate physical space-response state from the derived
  trace before any mechanism claim is broadened.
- Claim impact: wording narrowed; no external-validation or dark-matter
  replacement claim.
- Workflow linkage: first checkpoint before the matter-space hardening waves.
