"""Integrate the scoped Berut Figure 3c digitization result without promotion."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_berut_figure3_digitization.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
MANIFEST_REL = "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-17.md"


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def append_unique(values: list[Any], value: Any) -> None:
    if value not in values:
        values.append(value)


def append_marker(relative: str, marker: str, content: str) -> None:
    path = ROOT / relative
    current = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
    if marker not in current:
        path.write_text(current.rstrip() + "\n\n" + content.strip() + "\n", encoding="utf-8")


def main() -> int:
    audit = load(AUDIT_REL)
    major = audit["major_result"]
    if audit.get("status") != "PASS_SCOPED_BERUT_FIGURE3_DIGITIZATION":
        raise SystemExit(f"unexpected Berut digitization status: {audit.get('status')}")
    audit_evidence = {
        "path": AUDIT_REL,
        "sha256": digest(AUDIT_REL),
        "summary": {
            "status": audit["status"],
            "major_result_id": major["major_result_id"],
            "closure_level": major["closure_level"],
            "row_count": audit["row_count"],
            "data_role": major["data_role"],
            "full_core_unlock": False,
        },
    }
    today = date.today().isoformat()

    full = load(FULL_REL)
    full["generated_at"] = today
    append_unique(full["major_result"].setdefault("what_is_closed", []), "Berut Figure 3c figure-derived marker transcription boundary")
    for blocker in major["open_blockers"]:
        append_unique(full["major_result"].setdefault("what_remains_open", []), blocker)
    full.setdefault("verification_status", {}).setdefault("source_package", {})["berut_figure3_digitization"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "row_count": audit["row_count"],
        "series_counts": audit["series_counts"],
        "source_locator": audit["source_locator"],
        "audit": audit_evidence,
        "full_core_unlock": False,
        "controlling_blocker": audit["controlling_blocker"],
        "claim_boundary": major["claim_boundary"],
    }
    append_unique(full.setdefault("evidence_artifacts", []), audit_evidence)
    full.setdefault("data_role", {})["berut_figure3_digitization"] = major["data_role"]
    full["claim_promotion"] = False
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    record = {key: major[key] for key in (
        "major_result_id", "topic", "closure_level", "what_is_closed",
        "equation_or_mapping", "units", "derivation_class", "observable",
        "data_role", "verification_status", "open_blockers",
        "dependency_unlocked", "claim_boundary",
    )}
    record["evidence_artifacts"] = [audit_evidence]
    register["entries"] = [
        item for item in register.get("entries", [])
        if item.get("major_result_id") != major["major_result_id"]
    ] + [record]
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry.setdefault("what_is_closed", []), "Berut Figure 3c figure-derived marker transcription boundary")
    for blocker in major["open_blockers"]:
        append_unique(full_entry.setdefault("open_blockers", []), blocker)
    append_unique(full_entry.setdefault("evidence_artifacts", []), audit_evidence)
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["berut_figure3_digitization"] = audit_evidence
    partial["berut_figure3_digitization_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    marker = "## Berut Figure 3c Figure-Derived Digitization"
    section = f"""{marker}

MAJOR_RESULT_CLOSURE: {major["closure_level"]}

WHAT_IS_ACTUALLY_CLOSED: Panel 3c, visible axes and units, three marker-series
identities, ten marker centers, pixel-to-axis transforms, and a digitization-only
uncertainty envelope are recorded. The continuous fit curve and Landauer line are
excluded from the rows.

WHAT_REMAINS_OPEN: This is figure-derived rather than raw numeric data. The
publisher-reported 1 s.d. measurement intervals were not numerically transcribed,
and no permissioned raw table is archived.

DEPENDENCY_UNLOCKED: Berut figure-derived comparison lane only. No Full Topic 13,
Core, Gravity, constitutive transport, calibration, or external-validation
dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` and its source package record the official Figure 3c
locator, embedded-raster hash, axis mapping, marker rows, preprocessing, and
non-calibration boundary.

EQUATION_OR_MAPPING: `<Q>_panel_c(tau)` is retained in source units `kT` versus
`tau` in seconds. No SI heat or Phi mapping is emitted.

VERIFICATION: `{audit["row_count"]}` rows; three series; no curve digitization;
no fit; no target or holdout access; no alpha calibration.

CONTROLLING_BLOCKER: `{audit["controlling_blocker"]}`

NEXT_ACTION: Obtain a permitted raw or numeric source package, or obtain explicit
permission to archive the binary and its numeric extraction, then transcribe the
source-reported measurement uncertainty separately.

CLAIM_BOUNDARY: Scoped figure-derived comparison only; not a raw source,
calibration, prediction, UET proof, or external validation.
"""
    append_marker(REPORT_REL, marker, section)
    append_marker(FORMULA_REL, marker, section)
    append_marker(LOG_REL, "### 2026-08-17 - Berut Figure 3c figure-derived digitization", f"""### 2026-08-17 - Berut Figure 3c figure-derived digitization

- Scope: map the hash-pinned publisher Figure 3c raster into a transparent comparison-only marker table.
- Changed: `{AUDIT_REL}`, the digitization source package, full-gate source lane, closure register, dependency evidence, report, formula audit, manifest, update log, and ledger.
- Verified: `{audit["status"]}`; `{audit["row_count"]}` marker rows, explicit axes/units, three series, no fit, no target/holdout access, and no calibration.
- Result closed: `T13_BERUT_FIGURE3_DIGITIZATION` is `CLOSED_FOR_LANE`.
- Blocker narrowed: the selected-panel/axis/marker mapping is no longer open; raw numeric provenance and source-reported error-bar transcription remain open.
- Still open: Berut raw/permissioned numeric source, source-grade uncertainty, Topic 13 dimensional anchor, calibration, EOS/transport/KMS/entropy closure, and Full Topic 13 promotion.
- Claim impact: no promotion; the result is figure-derived comparison only.
""")
    append_marker(MANIFEST_REL, marker, f"""{marker}

The official publisher Figure 3c route is represented by a hash-pinned embedded
raster identity and a ten-row, figure-derived marker table. The rows use `tau` in
seconds and `<Q>` in `kT`; they are not raw experimental data and are not eligible
for calibration. See `{AUDIT_REL}`.
""")
    append_marker(LEDGER_REL, "## Topic 13 Berut Figure 3c Figure-Derived Digitization", f"""## Topic 13 Berut Figure 3c Figure-Derived Digitization

- area id: `research-core` (secondary: `data-provenance`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` Berut Figure 3c source lane
- changed: added hash-pinned panel/axis/marker digitization artifact and synchronized the source lane, closure register, dependency gate, report, formula audit, manifest, and update log
- verification: `{audit["status"]}`; `{audit["row_count"]}` rows, no fit, no target/holdout access, no calibration
- public-safety status: `partial`; figure-derived comparison is recorded but raw source and source-reported uncertainty remain open
- current claim boundary: `T13_BERUT_FIGURE3_DIGITIZATION` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- next action: obtain permissioned raw/numeric rows and close measurement-uncertainty provenance without using this lane for calibration
""")
    print(json.dumps({
        "status": "PASS_INTEGRATED_BERUT_FIGURE3_DIGITIZATION",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_core_unlock": False,
        "row_count": audit["row_count"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
