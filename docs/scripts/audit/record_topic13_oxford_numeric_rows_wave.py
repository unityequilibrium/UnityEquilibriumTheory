from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
CSV_GZ = TOPIC / "Data/03_Research/oxford_tgs_figure1_numeric_rows.csv.gz"
MANIFEST = TOPIC / "Data/03_Research/oxford_tgs_figure1_numeric_rows_manifest.json"
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_oxford_tgs_numeric_rows_audit.json"
FULL = TOPIC / "Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY = ROOT / "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_once(path: Path, marker: str, content: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in text:
        return
    separator = "" if not text or text.endswith("\n\n") else "\n"
    path.write_text(text + separator + content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    csv_hash = digest(CSV_GZ)
    manifest_hash = digest(MANIFEST)
    audit_hash = digest(AUDIT)
    full_hash = digest(FULL)
    register_hash = digest(REGISTER)
    dependency_hash = digest(DEPENDENCY)
    report = f"""### 2026-08-13 - Oxford TGS Figure 1 numeric-row comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_OXFORD_TGS_NUMERIC_ROWS_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: The archived MATLAB v7.3 Figure 1 source is extracted at the source-selected map point (`ph=39.0`, `pv=3.95`) as 10 trace identities with 2002 samples per trace. The source time/intensity labels and `yy1 - yy` operation are preserved without fitting.
WHAT_REMAINS_OPEN: The source does not declare the selected material and temperature, gives intensity rather than a unitful thermal observable, and does not provide Ding PBTE `C_src`, volumetric `c_v`, or a base-Phi amplitude.
DEPENDENCY_UNLOCKED: Oxford numeric comparator lane only; no Ding source, `c_v`, `alpha_Phi_K`, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_OXFORD_TGS_NUMERIC_ROWS_SOURCE_LOCKED_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added compressed numeric rows `{csv_hash}`, extraction manifest `{manifest_hash}`, numeric-row audit `{audit_hash}`, full-gate projection `{full_hash}`, and register/dependency synchronization `{register_hash}` / `{dependency_hash}`.
EQUATION_OR_MAPPING: `y_source(t) = yy1(t) - yy(t)`; source fit remains outside this artifact. No `c_v`, Ding `C_src`, `Delta_Tq=alpha_Phi_K*Delta_Phi`, or alpha value is emitted.
VERIFICATION: HDF5 shape/transpose contract, raw source hash, 20,020 row count, unique trace/sample identity, finite values, monotone time, exact subtraction, no fit, no target access, and Xie 2026 holdout isolation pass.
CONTROLLING_BLOCKER: `material_temperature_and_physical_thermal_mapping_missing`; full gate remains controlled by Ding `C_src`, independent `alpha_Phi_K`, dimensional Phi anchor, bridge/beta, EOS/transport/KMS/entropy, and source-grade `c_v` requirements.
NEXT_ACTION: Retain the extracted rows as a comparator and continue with a permitted source that supplies physical heat capacity or an independent base-Phi/SI anchor; do not relabel Oxford intensity as temperature.
CLAIM_BOUNDARY: Source-locked Oxford TGS numeric-row comparator only. It is not Ding validation, UET transport validation, alpha calibration, external validation, or Full Topic 13 closure.
"""
    append_once(TOPIC / "FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "Oxford TGS Figure 1 numeric-row comparator lane", report)
    append_once(TOPIC / "UPDATE_LOG.md", "2026-08-13 - Oxford TGS Figure 1 numeric-row comparator lane", report)
    manifest_report = f"""## Oxford TGS Figure 1 Numeric Rows (2026-08-13)

Numeric rows: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/oxford_tgs_figure1_numeric_rows.csv.gz` (`{csv_hash}`; 20,020 rows).
Extraction manifest: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/oxford_tgs_figure1_numeric_rows_manifest.json` (`{manifest_hash}`).
Audit: `docs/core/07_artifacts/topic13/t13_oxford_tgs_numeric_rows_audit.json` (`{audit_hash}`).

The rows preserve the Oxford source's Figure 1 time/intensity data and its
`yy1 - yy` subtraction at the selected map point. They are a comparison-only
source. Material/temperature identity, physical thermal units, Ding `C_src`,
and base-Phi calibration remain open.
"""
    append_once(TOPIC / "DATA_MANIFEST.md", "## Oxford TGS Figure 1 Numeric Rows (2026-08-13)", manifest_report)
    ledger = ROOT / "WORK_LEDGER/2026/2026-08-13.md"
    ledger_report = f"""## Topic 13 Oxford TGS numeric-row comparator wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: Oxford compressed numeric rows and manifest; extractor/audit/test; full-gate projection; major-result register/dependency sync; report/update log/manifest
- verifier: `PASS_OXFORD_TGS_NUMERIC_ROWS_SOURCE_LOCKED_COMPARATOR`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: 20,020 source-locked rows closed for comparator lane; no physical thermal or Phi calibration promotion
- hashes: rows `{csv_hash}`; manifest `{manifest_hash}`; audit `{audit_hash}`; full `{full_hash}`; register `{register_hash}`; dependency `{dependency_hash}`
- remains: material/temperature mapping, Ding `C_src`, unitful `c_v`, base-Phi SI anchor, independent alpha, bridge/beta, transport, KMS, entropy, and dissipative balance
- next action: pursue permitted physical thermal source or independent base-Phi/SI anchor without target fitting or Xie 2026 access
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""
    append_once(ledger, "## Topic 13 Oxford TGS numeric-row comparator wave", ledger_report)
    print("recorded Oxford TGS numeric-row comparator wave")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
