# Topic 0.4 update log

## 2026-11-15 — Saved-result reporting regression (software only)
- Added two tests for the original `analyze_failures` decision helper and the saved McMillan result; the producer, benchmark and data-writing paths are not executed.
- Criterion provenance: the existing helper uses average error <=20 percent and requires every row's existing `within_20_percent` flag; its scientific basis is not newly validated here.
- The saved record retains `run_status=PASS` and `model_gate_status=FAIL`; the shared runner copies the latter into a separate legacy readout, not the v2 registry.
- Scope is partial: reporting/helper checks do not admit the benchmark, input provenance or other Topic paths. `--topic 0.4` returns 2 for this explicit coverage gap, not a whole-Topic pass.
- No equation, parameter, scientific artifact, source hash or evidence level changed; no new physical comparison performed.
