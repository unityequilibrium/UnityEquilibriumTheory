"""Integrate the bounded Georgia Tech graphite comparator into Topic 13 records."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_gatech_standard_transport_comparator_audit.json"
SOURCE_AUDIT_REL = "docs/core/07_artifacts/topic13/t13_gatech_graphite_source_audit.json"
PACKAGE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "gatech_gen3csp_graphite_source_package.json"
)
RAW_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "gen3csp_graphite.xlsx"
)
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
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
    audit = load(AUDIT_REL)
    if audit.get("status") != "PASS_STANDARD_GRAPHITE_TRANSPORT_COMPARATOR_CONDITIONAL":
        raise SystemExit(f"standard comparator audit is not passing: {audit.get('status')}")

    today = date.today().isoformat()
    major = audit["major_result"]
    blocker = "standard_comparator_is_not_a_UET_Phi_transport_coefficient_or_Ding_C_src"
    audit_evidence = evidence(AUDIT_REL, {
        "status": audit["status"],
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_core_unlock": False,
    })
    source_evidence = evidence(SOURCE_AUDIT_REL, {
        "status": load(SOURCE_AUDIT_REL)["status"],
        "data_role": "INDEPENDENT_MATERIAL_COMPARATOR_NOT_UET_CALIBRATION",
    })
    package_evidence = evidence(PACKAGE_REL, {
        "source_id": audit["source_identity"]["source_id"],
        "row_identity": audit["source_identity"]["row_identity"],
        "data_role": audit["source_identity"]["source_data_role"],
    })
    raw_evidence = {
        "path": RAW_REL,
        "sha256": digest(RAW_REL),
        "summary": {"row_identity": audit["source_identity"]["row_identity"]},
    }

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(
        full_major.setdefault("what_is_closed", []),
        "conditional standard graphite transport comparator with separate source-reported and propagated uncertainty envelopes",
    )
    append_unique(
        full_major.setdefault("what_remains_open", []),
        "standard graphite comparator density uncertainty and c_p-to-c_v regime remain conditional",
    )
    append_unique(full_major.setdefault("what_remains_open", []), blocker)
    transport = full["verification_status"]["eos_transport_kms_entropy"]
    transport["standard_graphite_transport_comparator"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "source_identity": audit["source_identity"],
        "derived_comparator": audit["derived_comparator"],
        "uncertainty_contract": audit["uncertainty_contract"],
        "synthetic_controls_physical": False,
        "alpha_Phi_K_emitted": False,
        "audit": audit_evidence,
        "source_audit": source_evidence,
        "source_package": package_evidence,
        "raw_source": raw_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    full.setdefault("evidence_artifacts", [])
    for item in (audit_evidence, source_evidence, package_evidence, raw_evidence):
        append_unique(full["evidence_artifacts"], item)
    full.setdefault("data_role", {})["standard_graphite_transport_comparator"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["next_action"] = (
        "Acquire a state-matched physical Kubo coefficient and independent base-Phi SI anchor; "
        "keep the graphite comparator conditional and rerun the full bridge only after EOS, transport, KMS, and entropy evidence are source-locked."
    )
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
    record["evidence_artifacts"] = [audit_evidence, source_evidence, package_evidence, raw_evidence]
    record["verification_status"] = audit["status"]
    register["entries"] = [
        item for item in register.get("entries", [])
        if item.get("major_result_id") != major["major_result_id"]
    ] + [record]
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(
        full_entry.setdefault("what_is_closed", []),
        "conditional standard graphite transport comparator with explicit source and propagation uncertainty separation",
    )
    append_unique(
        full_entry.setdefault("open_blockers", []),
        "standard graphite comparator is not a UET Phi transport coefficient or Ding C_src",
    )
    append_unique(full_entry.setdefault("evidence_artifacts", []), audit_evidence)
    for item in full_entry["evidence_artifacts"]:
        if item.get("path") == FULL_REL:
            item["sha256"] = digest(FULL_REL)
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["standard_graphite_transport_comparator"] = audit_evidence
    partial["standard_graphite_transport_comparator_source"] = {
        "source_audit": source_evidence,
        "source_package": package_evidence,
        "raw_source": raw_evidence,
    }
    partial["standard_graphite_transport_comparator_controller"] = blocker
    partial["standard_graphite_transport_comparator_data_role"] = major["data_role"]
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Standard Graphite Transport Comparator (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-024` | `c_p^vol = c_p^mass rho_assumed`; `k = D c_p^vol`; `sigma_k` is reported and first-order propagated separately | `{AUDIT_REL}`; `{PACKAGE_REL}`; `{RAW_REL}` | `c_p^mass` = J kg^-1 K^-1; `rho` = kg m^-3; `c_p^vol` = J m^-3 K^-1; `D` = m^2 s^-1; `k` = W m^-1 K^-1 | source-backed comparator algebra with assumed density; no UET derivation | comparator gate passes conditionally; density and c_p-to-c_v regime remain open | confirms source row, units, raw hash, reconstructed k, uncertainty separation, synthetic-control boundary, and holdout isolation | comparator could be mislabeled as UET Phi transport or Ding C_src | source-lock density/c_v regime or acquire a state-matched UET Kubo coefficient and base-Phi SI anchor |

The source-reported and first-order propagated `sigma_k` values are retained as
separate envelopes because source covariance and provider aggregation are not
locked. This comparator does not emit `Phi`, `alpha_Phi_K`, `C_src`, or a TTG
prediction.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Standard Graphite Transport Comparator"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: A conditional, source-backed graphite comparator at
`573.15 K` is reproducible from the archived row. The reconstructed
`k = 74.0939625200673 W m^-1 K^-1`; source-reported and first-order propagated
uncertainty envelopes are both retained and explicitly separated.

WHAT_REMAINS_OPEN: Density uncertainty, the `c_p` to `c_v` regime correction,
UET `Phi` transport, Ding `C_src`, and the base-Phi SI anchor remain open.

DEPENDENCY_UNLOCKED: Standard-material comparator lane only. No Full Topic 13,
Core curved 3+1, Gravity, or constitutive transport dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` and its source/hash evidence are linked into the
Topic 13 full gate, major-result register, dependency gate, formula audit, and
current-state report.

EQUATION_OR_MAPPING:

```text
c_p^vol = c_p^mass * rho_assumed
k = D * c_p^vol
sigma_k(source-reported) != forced_equal_to sigma_k(first-order propagated)
```

VERIFICATION: Source row identity, unit conversions, raw hash, reconstructed
conductivity, finite uncertainty envelopes, synthetic-control separation, and
no-holdout/no-alpha-fit policy all pass.

CONTROLLING_BLOCKER: `{blocker}`

NEXT_ACTION: Acquire a state-matched physical Kubo coefficient and an
independent base-Phi SI anchor; do not relabel this standard comparator as UET
transport evidence.

CLAIM_BOUNDARY: This is a conditional standard-material comparator only. It is
not Ding PBTE `C_src`, not UET constitutive transport, not `alpha_Phi_K`, not a
TTG prediction, and not external validation.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Standard graphite transport comparator"
    log_content = f"""{log_marker}

- Scope: close the standard-fluid/material comparator lane without treating it as UET constitutive transport.
- Added or changed: `{AUDIT_REL}`, source-row/hash linkage, comparator integration in the full gate/register/dependency gate, formula audit, and current-state report.
- Verified with: `{audit["status"]}`; `k = 74.0939625200673 W m^-1 K^-1` is reconstructed from `D * c_p * rho_assumed`, while source-reported and propagated uncertainty envelopes remain separate.
- Result closed: `T13_GATECH_STANDARD_TRANSPORT_COMPARATOR` is `CLOSED_FOR_LANE`.
- Blocker narrowed: the comparator boundary is explicit as `{blocker}`; density uncertainty and the `c_p` to `c_v` regime remain conditional.
- Still open: independent base-Phi SI anchor, `alpha_Phi_K`, Ding `C_src`, physical Kubo coefficient, finite-temperature normal component, full KMS/entropy completion, and full Topic 13 closure.
- Next controller: acquire accepted physical transport and base-Phi evidence; keep Fourier/Cattaneo and graphite outputs as comparator controls only.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
"""
    append_marker(LOG_REL, log_marker, log_content)

    ledger_marker = "## Topic 13 Standard Graphite Transport Comparator"
    ledger_content = f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked comparator artifacts
- changed: added the conditional standard graphite transport comparator and synchronized Topic 13 gate, register, dependency gate, formula audit, report, and update log
- verification: `{audit["status"]}`; source row/hash and reconstructed `k` pass, uncertainty envelopes are separate, and no Phi calibration or Xie 2026 access occurred
- public-safety status: `partial`; comparator is not UET transport evidence
- current claim boundary: `T13_GATECH_STANDARD_TRANSPORT_COMPARATOR` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated Topic 0.22/0.25 changes were not edited
- next action: acquire state-matched physical Kubo evidence and independent base-Phi SI calibration
"""
    append_marker(LEDGER_REL, ledger_marker, ledger_content)

    print(json.dumps({
        "status": "PASS_INTEGRATED_STANDARD_GRAPHITE_TRANSPORT_COMPARATOR",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "controlling_blocker": full["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
