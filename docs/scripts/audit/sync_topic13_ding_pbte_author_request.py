"""Integrate the bounded Ding PBTE author-request result without promoting claims."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "ding_2022_pbte_author_request_manifest.json"
)
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_ding_pbte_author_request_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
ENERGY_REL = "docs/core/07_artifacts/topic13/t13_energy_response_bridge_audit.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-12.md"


def load(rel: str) -> dict[str, Any]:
    value = json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def evidence(rel: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": rel, "sha256": digest(rel), "summary": summary}


def append_unique(items: list[Any], value: Any) -> None:
    if value not in items:
        items.append(value)


def append_marker(rel: str, marker: str, content: str) -> None:
    path = ROOT / rel
    current = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
    if marker not in current:
        path.write_text(current.rstrip() + "\n\n" + content.strip() + "\n", encoding="utf-8")


def main() -> int:
    manifest = load(MANIFEST_REL)
    audit = load(AUDIT_REL)
    if audit.get("status") != "PASS_REQUEST_SCHEMA_OPEN_EXTERNAL_RESPONSE":
        raise SystemExit(f"request audit is not passing: {audit.get('status')}")

    today = date.today().isoformat()
    major = manifest["major_result"]
    blocker = "author_data_or_independent_reproduction_payload_not_received"
    request_evidence = evidence(
        AUDIT_REL,
        {
            "status": audit["status"],
            "major_result_id": major["major_result_id"],
            "request_state": manifest["status"],
            "full_core_unlock": False,
        },
    )
    manifest_evidence = evidence(
        MANIFEST_REL,
        {
            "status": manifest["status"],
            "major_result_id": major["major_result_id"],
            "data_role": major["data_role"],
        },
    )

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(
        full_major.setdefault("what_is_closed", []),
        "Ding PBTE corresponding-author request package with bounded payload, provenance, and acceptance contract",
    )
    append_unique(full_major.setdefault("what_remains_open", []), blocker)
    full["verification_status"]["alpha_Phi_K"]["named_energy_response_branch"][
        "pbte_author_request_package"
    ] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "request_state": manifest["status"],
        "manifest": manifest_evidence,
        "audit": request_evidence,
        "sent": False,
        "response_received": False,
        "numeric_C_src_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "target_curve_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    full.setdefault("evidence_artifacts", [])
    append_unique(full["evidence_artifacts"], request_evidence)
    append_unique(full["evidence_artifacts"], manifest_evidence)
    full["data_role"]["ding_pbte_author_request"] = "REQUEST_SPECIFICATION_NOT_SOURCE_DATA"
    full["source_acquisition_controller"] = "ding_pbte_author_data_or_independent_reproduction_package_missing"
    full["source_acquisition_controller_detail"] = (
        "A bounded author-request package is ready but not sent; no external payload has been received. "
        "Independent mp-48 c_v remains comparator-only."
    )
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["next_action"] = (
        "If authorized, send the prepared Ding PBTE request and record the sent-message hash; "
        "otherwise continue independent base-Phi/e0 derivation without inferring C_src from TTG residuals."
    )
    full["claim_promotion"] = False
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    energy = load(ENERGY_REL)
    energy["generated_at"] = today
    # Preserve the legacy route field for existing consumers; expose the
    # machine-readable request state in the adjacent package record.
    energy["pbte_numeric_input_availability"]["author_request_route"] = "OPEN_NOT_EXECUTED"
    energy["pbte_numeric_input_availability"]["author_request_package"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "request_state": manifest["status"],
        "manifest": manifest_evidence,
        "audit": request_evidence,
        "numeric_C_src_status": "OPEN_NOT_RECEIVED",
        "numeric_alpha_Phi_K_emitted": False,
        "xie_2026_accessed": False,
    }
    energy["next_controller"] = (
        "If authorized, send the bounded author request and audit any returned payload; "
        "keep numeric C_src and the base-Phi energy anchor open until source acceptance."
    )
    (ROOT / ENERGY_REL).write_text(json.dumps(energy, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    record = {key: major[key] for key in (
        "major_result_id", "topic", "closure_level", "what_is_closed",
        "equation_or_mapping", "units", "derivation_class", "observable",
        "data_role", "verification_status", "open_blockers",
        "dependency_unlocked", "claim_boundary",
    )}
    record["evidence_artifacts"] = [request_evidence, manifest_evidence]
    record["verification_status"] = audit["status"]
    register["entries"] = [
        item for item in register.get("entries", [])
        if item.get("major_result_id") != major["major_result_id"]
    ] + [record]
    register["next_major_result"] = register.get("next_major_result", "T13_FULL_THERMODYNAMIC_BRIDGE")
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["ding_pbte_author_request_package"] = request_evidence
    partial["ding_pbte_author_request_manifest"] = manifest_evidence
    partial["author_request_state"] = manifest["status"]
    partial["author_request_controller"] = blocker
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Ding PBTE Author-Request Acquisition Contract (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-022` | `C_src(T) = sum_mu c_mu(T)`; `Delta_Tq = Delta_u_ph/C_src`; `Phi_E = Delta_u_ph/e0` | `{MANIFEST_REL}`; `{AUDIT_REL}` | `c_mu,C_src` = J m^-3 K^-1; `Delta_u_ph,e0` = J m^-3; `Phi_E` = dimensionless | published Ding notation plus a request specification; no numeric input supplied | request contract only, no derivation/calibration | checks that the external acquisition route is bounded and auditable before source acceptance | request can be mistaken for received data or independent alpha calibration | if authorized, send the request; hash and audit any returned payload before changing state |

The request package is not a data source. It does not identify base `Phi` with
`Phi_E`, does not emit `C_src`, `e0`, or `alpha_Phi_K`, and does not read Xie
2026.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Ding PBTE Author-Request Controller"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: A bounded corresponding-author request package now
lists the missing Ding PBTE payload, units, row identity, provenance,
uncertainty/convergence, hashes, permission terms, and acceptance tests.

WHAT_REMAINS_OPEN: The request is `REQUEST_PACKAGE_READY_NOT_SENT`. No author
payload, numeric `C_src(T)`, mode-resolved `c_mu(T)`, `e0`, base-`Phi` energy
map, or `alpha_Phi_K` has been received or emitted.

DEPENDENCY_UNLOCKED: Source-acquisition readiness only. Full Topic 13, Core
curved 3+1, Gravity, and transport remain blocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{MANIFEST_REL}` and `{AUDIT_REL}` are linked to the full gate,
energy bridge, register, dependency gate, formula audit, and update log.

EQUATION_OR_MAPPING:

```text
C_src(T) = sum_mu c_mu(T)
Delta_Tq = Delta_u_ph / C_src
Phi_E = Delta_u_ph / e0
```

VERIFICATION: The local OA package remains a scoped no-go for numeric Ding
inputs. The request audit passes all schema, provenance, unit, and holdout
checks; `sent=false`, `response_received=false`, and no target curve was used.

CONTROLLING_BLOCKER: `{blocker}`

NEXT_ACTION: If the project owner authorizes external contact, send the prepared
request and record the sent-message hash. On response, hash and audit every
file before accepting any numeric `C_src` row.

CLAIM_BOUNDARY: This is a request specification, not a sent request, source
package, calibration, fit, prediction, external validation, or Full Topic 13
closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Ding PBTE author-request package"
    log_content = f"""{log_marker}

- Scope: convert the captured Ding OA numeric-input no-go into a bounded external acquisition route.
- Added or changed: `{MANIFEST_REL}`, `{AUDIT_REL}`, request-wave sync, formula-audit record, Full Topic 13 gate/register/dependency evidence, and current-state report.
- Verified with: `{audit["status"]}`; requested payload groups, units, row identity, provenance, uncertainty/convergence, hashes, permission terms, and holdout restrictions are present.
- Result closed: `T13_DING_PBTE_AUTHOR_REQUEST_PACKAGE` is `CLOSED_FOR_LANE`; the request is ready but not sent.
- Blocker narrowed: the route is no longer unspecified; the external state remains `{blocker}`.
- Still open: numeric Ding `C_src(T)`, mode-resolved `c_mu(T)`, e0, base-Phi energy mapping, alpha_Phi_K, and full EOS/transport/KMS/entropy closure.
- Next controller: send only with project authorization; never infer numeric C_src from normalized TTG data and never read Xie 2026.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
"""
    append_marker(LOG_REL, log_marker, log_content)

    ledger_marker = "## Topic 13 Ding PBTE Author-Request Package"
    ledger_content = f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` artifacts
- changed: added the bounded author-request manifest/audit and synchronized Topic 13 full-gate, energy bridge, register, dependency gate, formula audit, and update log
- verification: `{audit["status"]}`; request state is `{manifest["status"]}`, with no external payload or holdout access
- public-safety status: `partial`; this is a request specification, not a received source package
- current claim boundary: `T13_DING_PBTE_AUTHOR_REQUEST_PACKAGE` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated Topic 0.22/0.25 changes were not edited
- next action: obtain authorization before sending; then record sent-message hash or continue independent base-Phi/e0 derivation
"""
    append_marker(LEDGER_REL, ledger_marker, ledger_content)

    print(json.dumps({
        "status": "PASS_INTEGRATED_DING_AUTHOR_REQUEST_PACKAGE",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "request_state": manifest["status"],
        "full_topic13_status": full["status"],
        "controlling_blocker": full["controlling_blocker"],
        "dependency_unlock": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
