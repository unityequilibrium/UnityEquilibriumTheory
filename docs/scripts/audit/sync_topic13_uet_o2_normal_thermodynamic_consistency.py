"""Integrate the normal-branch thermodynamic-consistency result conservatively."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_normal_thermodynamic_consistency_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-12.md"


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def evidence(relative: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": relative, "sha256": digest(relative), "summary": summary}


def append_unique(items: list[Any], value: Any) -> None:
    if value not in items:
        items.append(value)


def append_marker(relative: str, marker: str, content: str) -> None:
    path = ROOT / relative
    current = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
    if marker not in current:
        path.write_text(current.rstrip() + "\n\n" + content.strip() + "\n", encoding="utf-8")


def main() -> int:
    audit = load(AUDIT_REL)
    if audit.get("status") != "PASS_ACTION_DERIVED_NORMAL_THERMODYNAMIC_CONSISTENCY":
        raise SystemExit(f"normal consistency audit is not passing: {audit.get('status')}")

    today = date.today().isoformat()
    major = audit["major_result"]
    audit_evidence = evidence(
        AUDIT_REL,
        {
            "status": audit["status"],
            "major_result_id": major["major_result_id"],
            "closure_level": major["closure_level"],
            "full_core_unlock": False,
        },
    )

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(
        full_major.setdefault("what_is_closed", []),
        "grid-level thermodynamic consistency, Maxwell reciprocity, and Gibbs-Duhem checks for the action-derived O(2) normal lane",
    )
    append_unique(
        full_major.setdefault("what_is_closed", []),
        "normal-branch positivity and domain checks across the declared deterministic state grid",
    )
    append_unique(
        full_major.setdefault("what_remains_open", []),
        "normal-branch consistency does not close vacuum renormalization, condensate/two-fluid physics, physical transport, or SI Phi mapping",
    )
    transport = full.setdefault("verification_status", {}).setdefault(
        "eos_transport_kms_entropy", {}
    )
    transport["uet_o2_normal_thermodynamic_consistency"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "grid": audit["grid"],
        "metrics": audit["metrics"],
        "checks": audit["checks"],
        "audit": audit_evidence,
        "full_core_unlock": False,
        "controlling_blocker": audit["controlling_blocker"],
        "claim_boundary": major["claim_boundary"],
    }
    append_unique(full.setdefault("evidence_artifacts", []), audit_evidence)
    full.setdefault("data_role", {})["uet_o2_normal_thermodynamic_consistency"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["next_action"] = "Keep the internally consistent normal lane bounded; close vacuum/interaction and condensate/two-fluid sectors, then source physical Kubo coefficients and an independent base-Phi SI anchor."
    full["claim_promotion"] = False
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    record = {
        key: major[key]
        for key in (
            "major_result_id",
            "topic",
            "closure_level",
            "what_is_closed",
            "equation_or_mapping",
            "units",
            "derivation_class",
            "observable",
            "data_role",
            "verification_status",
            "open_blockers",
            "dependency_unlocked",
            "claim_boundary",
        )
    }
    record["evidence_artifacts"] = [audit_evidence]
    record["verification_status"] = audit["status"]
    register["entries"] = [
        item
        for item in register.get("entries", [])
        if item.get("major_result_id") != major["major_result_id"]
    ] + [record]
    full_entry = next(
        item for item in register["entries"]
        if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE"
    )
    append_unique(
        full_entry.setdefault("what_is_closed", []),
        "grid-level thermodynamic consistency and reciprocity checks for the action-derived O(2) normal lane",
    )
    append_unique(
        full_entry.setdefault("open_blockers", []),
        audit["controlling_blocker"],
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
    partial["uet_o2_normal_thermodynamic_consistency"] = audit_evidence
    partial["uet_o2_normal_thermodynamic_consistency_controller"] = audit["controlling_blocker"]
    partial["uet_o2_normal_thermodynamic_consistency_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## O(2) Normal-Lane Thermodynamic Consistency (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-030` | `n=partial_mu p`; `s=partial_T p`; `epsilon=-p+T*s+mu*n`; `partial_Phi n=partial_mu(partial_Phi p)`; `partial_Phi s=partial_T(partial_Phi p)` | `{AUDIT_REL}`; `docs/core/02_equations/o2/uet_o2_one_loop_normal_branch.py` | natural-unit thermodynamic densities and natural response-field derivative | action-derived thermal determinant; no external coefficient or fit | grid-level derivative, reciprocity, positivity, and Gibbs-Duhem checks pass; vacuum/condensate/transport/SI remain open | verifies internal consistency of the declared normal branch without target data | a local derivative pass can be overstated as a full finite-temperature UET closure | close renormalized/interacting and condensate/two-fluid sectors, then match physical Kubo and SI observables |

This result is a consistency closure for the normal-background lane only. It
does not derive a physical Kubo coefficient, `alpha_Phi_K`, an SI observable,
or a full finite-temperature UET EOS.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## O(2) Normal-Lane Thermodynamic Consistency"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The action-derived one-loop normal branch is internally
consistent across a deterministic grid: pressure derivatives recover charge,
entropy, and the Phi response derivative; cross-derivative reciprocity and
Gibbs-Duhem identities pass; positivity and the normal-domain condition pass.

WHAT_REMAINS_OPEN: Vacuum renormalization, interacting finite-temperature
self-energy, condensate/Goldstone/normal two-fluid completion, physical Kubo
coefficients, SK/KMS microscopic matching, the SI Phi map, and `alpha_Phi_K`
remain open.

DEPENDENCY_UNLOCKED: Normal-lane thermodynamic consistency only. No physical
EOS, transport, SI, Full Topic 13, Core, or Gravity dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` evaluates the declared normal determinant over
{audit["grid"]["point_count"]} state points with fixed quadrature/cutoff policy,
finite-difference derivative checks, Maxwell reciprocity, positivity, and
Gibbs-Duhem identities. The result is linked into the full gate, register,
dependency gate, formula audit, update log, and ledger.

EQUATION_OR_MAPPING:

```text
n = partial_mu p
s = partial_T p
epsilon = -p + T*s + mu*n
partial_Phi n = partial_mu(partial_Phi p)
partial_Phi s = partial_T(partial_Phi p)
```

VERIFICATION: Maximum derivative error is `{max(audit["metrics"][key] for key in ("dp_dmu", "dp_dT", "dp_dPhi")):.3e}`;
maximum Maxwell error is `{max(audit["metrics"][key] for key in ("maxwell_mu_phi", "maxwell_T_phi")):.3e}`;
and all declared positivity, branch, ontology, and holdout checks pass. No
parameter fitting, target curve, Xie 2026 data, alpha, or SI coefficient was
used.

CONTROLLING_BLOCKER: `{audit["controlling_blocker"]}` for this derived lane;
the Full Topic 13 controller remains `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`.

NEXT_ACTION: Keep this lane fixed as an internal consistency baseline; close
the vacuum/interaction and condensate/two-fluid sectors, then obtain physical
Kubo evidence and an independent base-Phi SI anchor.

CLAIM_BOUNDARY: This is not a renormalized finite-temperature UET theory, a
physical transport result, an SI calibration, external validation, or Full
Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - O(2) normal-lane thermodynamic consistency"
    log_content = f"""{log_marker}

- Scope: test action-derived one-loop normal thermodynamic consistency over a fixed state grid.
- Added or changed: `{AUDIT_REL}`, the full-gate lane mapping, register/dependency evidence, formula audit, current report, update log, and ledger entry.
- Verified with: `{audit["status"]}`; pressure derivatives, Maxwell reciprocity, Gibbs-Duhem identities, positivity, normal-domain, ontology, and holdout checks.
- Result closed: `T13_UET_O2_NORMAL_THERMODYNAMIC_CONSISTENCY` is `CLOSED_FOR_LANE`.
- Blocker narrowed: internal normal-lane consistency is no longer the controller; `{audit["controlling_blocker"]}` controls the remaining one-loop physics boundary.
- Still open: renormalization, interacting finite-T response, condensate/two-fluid sector, physical Kubo, SI Phi map, alpha, and Full Topic 13 closure.
- Next controller: close the remaining physical finite-temperature and SI/source evidence without promoting this internal lane.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
"""
    append_marker(LOG_REL, log_marker, log_content)

    ledger_marker = "## Topic 13 O(2) Normal-Lane Thermodynamic Consistency"
    ledger_content = f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` O(2) normal thermal branch and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added grid-level thermodynamic consistency audit and synchronized the Topic 13 full gate, register, dependency gate, formula audit, report, and update log
- verification: `{audit["status"]}`; {audit["grid"]["point_count"]} deterministic states, no fit, no target, no holdout
- public-safety status: `partial`; this is an internal natural-unit consistency result, not physical transport or SI calibration
- current claim boundary: `T13_UET_O2_NORMAL_THERMODYNAMIC_CONSISTENCY` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated Topic 0.22/0.25 changes were not edited
- next action: close renormalization/interacting and condensate/two-fluid physics, then source physical Kubo and base-Phi SI evidence
"""
    append_marker(LEDGER_REL, ledger_marker, ledger_content)

    print(
        json.dumps(
            {
                "status": "PASS_INTEGRATED_NORMAL_THERMODYNAMIC_CONSISTENCY",
                "major_result_id": major["major_result_id"],
                "closure_level": major["closure_level"],
                "full_topic13_status": full["status"],
                "full_core_unlock": False,
                "controlling_blocker": full["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
