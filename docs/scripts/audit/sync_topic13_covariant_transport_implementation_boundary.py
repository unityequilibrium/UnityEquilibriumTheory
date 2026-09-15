"""Integrate the bounded covariant transport implementation result."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_covariant_transport_implementation_boundary_audit.json"
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
    if audit.get("status") != "PASS_CLOSED_TRANSPORT_IMPLEMENTATION_BOUNDARY":
        raise SystemExit(f"transport boundary audit is not passing: {audit.get('status')}")
    today = date.today().isoformat()
    major = audit["major_result"]
    blocker = "physical_Kubo_coefficient_record_missing"
    audit_evidence = evidence(AUDIT_REL, {
        "status": audit["status"],
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_core_unlock": False,
    })

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(full_major.setdefault("what_is_closed", []), "covariant transport implementation scope and coefficient-admission boundary")
    append_unique(full_major.setdefault("what_remains_open", []), "current transport implementation is T=0/natural-unit and does not supply finite-temperature physical transport")
    append_unique(full_major.setdefault("what_remains_open", []), "covariant transport implementation boundary does not supply a physical Kubo coefficient")
    transport = full["verification_status"]["eos_transport_kms_entropy"]
    transport["covariant_transport_implementation_boundary"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "implementation_lane": "natural_units",
        "temperature_scope": "T_ZERO_PURE_SUPERFLUID_ONLY",
        "normal_component": "OPEN_NOT_DERIVED",
        "physical_coefficient_evidence": "BLOCKED_NOT_PROVIDED",
        "synthetic_controls_physical": False,
        "si_lane": "BLOCKED",
        "curved_3p1_solver": "NOT_IMPLEMENTED",
        "trace_input": False,
        "trace_backreaction": False,
        "audit": audit_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    append_unique(full.setdefault("evidence_artifacts", []), audit_evidence)
    full.setdefault("data_role", {})["covariant_transport_implementation_boundary"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["next_action"] = "Acquire a state-matched physical Kubo coefficient and independent base-Phi SI anchor; separately derive finite-temperature normal response before claiming full constitutive transport."
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
    record["verification_status"] = audit["status"]
    register["entries"] = [item for item in register.get("entries", []) if item.get("major_result_id") != major["major_result_id"]] + [record]
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry.setdefault("what_is_closed", []), "covariant transport implementation boundary is explicit and verified")
    append_unique(full_entry.setdefault("open_blockers", []), "physical Kubo coefficient, finite-temperature normal component, SI transport, and curved 3+1 solver remain outside the implementation")
    append_unique(full_entry.setdefault("evidence_artifacts", []), audit_evidence)
    for item in full_entry["evidence_artifacts"]:
        if item.get("path") == FULL_REL:
            item["sha256"] = digest(FULL_REL)
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["covariant_transport_implementation_boundary"] = audit_evidence
    partial["covariant_transport_implementation_controller"] = blocker
    partial["covariant_transport_implementation_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Covariant Transport Implementation Boundary (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-025` | `P=P(X,Phi)`; `N^mu=(Zq/lambda)xi^mu`; `T^mu_nu=f_s xi^mu xi^nu+p g^mu_nu`; `KuboRecord -> coefficient` only when matched evidence passes | `docs/core/uet_covariant_superfluid_transport.py`; `docs/core/07_artifacts/archive/covariant_superfluid_transport_contract.json`; `{AUDIT_REL}` | implementation lane = natural units; frame = Landau; T=0 ideal sector; physical coefficient units must be source-declared | tree-level O(2) action for ideal sector; dissipative values require external/microscopic match | implementation boundary closes; physical coefficient, finite-T normal component, SI lane, and curved 3+1 remain open | prevents synthetic controls, natural-unit defaults, or T=0 ideal formulas from being promoted to physical full transport | a T=0/natural-unit interface can be mislabeled as finite-temperature SI constitutive closure | acquire state-matched Kubo record, derive normal component, and construct SI observable map |

The audit intentionally closes only the implementation boundary. It does not
emit a physical transport coefficient or use `R_gen` as transport state.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Covariant Transport Implementation Boundary"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The current implementation is explicitly bounded to a
natural-unit Landau-frame `T=0` pure-superfluid ideal sector plus a minimal
longitudinal Kubo interface. Ideal covariance, entropy positivity, causal
control, and missing-provenance blocking are verified.

WHAT_REMAINS_OPEN: No physical Kubo coefficient is supplied. The finite-
temperature normal component, full transport tensor, SI lane, and curved 3+1
solver are not implemented.

DEPENDENCY_UNLOCKED: Implementation-boundary result only. No physical transport,
Full Topic 13, Core curved 3+1, or Gravity dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` hashes the transport implementation, contract,
verification artifact, and tests, then links the boundary into the full gate,
register, dependency gate, formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
P = P(X, Phi)
N^mu = (Z*q/lambda) xi^mu
T^mu_nu = f_s xi^mu xi^nu + p g^mu_nu
KuboCoefficientRecord -> coefficient only when matched evidence passes
sigma = X_A L^(AB) X_B >= 0
```

VERIFICATION: Source markers and tests confirm T=0 rejection, no-default
coefficient admission, natural-unit/SI boundary, synthetic-control opt-in,
trace isolation, ideal covariance, entropy sign, causal speed, and blocked
physical provenance.

CONTROLLING_BLOCKER: `{blocker}`

NEXT_ACTION: Acquire one state-matched physical Kubo coefficient and derive the
finite-temperature normal sector and SI Phi observable map independently.

CLAIM_BOUNDARY: This is an implementation-scope result only. It is not a
microscopic Kubo match, finite-temperature two-fluid derivation, SI transport
result, external validation, or Full Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Covariant transport implementation boundary"
    log_content = f"""{log_marker}

- Scope: audit what the current covariant transport implementation actually supports before attempting physical finite-temperature closure.
- Added or changed: `{AUDIT_REL}`, source/test hashes, full-gate transport boundary, major-result register entry, dependency evidence, formula audit, report, and ledger.
- Verified with: `{audit["status"]}`; ideal covariance, entropy sign, causal control, T=0 rejection, no-default Kubo admission, and trace isolation all agree with the implementation.
- Result closed: `T13_COVARIANT_TRANSPORT_IMPLEMENTATION_BOUNDARY` is `CLOSED_FOR_LANE`.
- Blocker narrowed: physical transport input is explicitly `{blocker}`; finite-temperature normal response and SI/curved extensions are separate blockers.
- Still open: state-matched physical coefficient, finite-temperature normal component, full tensor, SI Phi map, curved 3+1 transport, alpha_Phi_K, and full Topic 13 closure.
- Next controller: source-lock one physical coefficient and independently derive the normal sector/SI map; do not promote synthetic controls.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
"""
    append_marker(LOG_REL, log_marker, log_content)

    ledger_marker = "## Topic 13 Covariant Transport Implementation Boundary"
    ledger_content = f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` covariant transport and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added the implementation-boundary audit and synchronized Topic 13 full gate, register, dependency gate, formula audit, report, update log, and ledger
- verification: `{audit["status"]}`; T=0/natural-unit scope, no-default coefficient admission, entropy/causal controls, and trace isolation are explicit
- public-safety status: `partial`; no physical coefficient or finite-temperature claim emitted
- current claim boundary: `T13_COVARIANT_TRANSPORT_IMPLEMENTATION_BOUNDARY` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated Topic 0.22/0.25 changes were not edited
- next action: acquire physical Kubo evidence and derive finite-temperature normal response plus SI Phi mapping
"""
    append_marker(LEDGER_REL, ledger_marker, ledger_content)

    print(json.dumps({
        "status": "PASS_INTEGRATED_TRANSPORT_IMPLEMENTATION_BOUNDARY",
        "major_result_id": major["major_result_id"],
        "closure_level": major["closure_level"],
        "full_topic13_status": full["status"],
        "full_core_unlock": False,
        "controlling_blocker": full["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
