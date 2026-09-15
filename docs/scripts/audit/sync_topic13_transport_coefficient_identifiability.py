"""Integrate the scoped conservative-action Kubo identifiability no-go."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_transport_coefficient_identifiability_no_go.json"
MODULE_REL = "docs/core/uet_transport_coefficient_identifiability.py"
TRANSPORT_REL = "docs/core/uet_covariant_superfluid_transport.py"
SK_REL = "docs/core/thermal_sk_kms_entropy_contract.py"
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
    expected = "PASS_SCOPED_NO_GO_CONSERVATIVE_ACTION_KUBO_IDENTIFIABILITY"
    if audit.get("status") != expected:
        raise SystemExit(f"transport identifiability audit is not passing: {audit.get('status')}")

    today = date.today().isoformat()
    major = audit["major_result"]
    blocker = audit["controlling_blocker"]
    audit_evidence = evidence(
        AUDIT_REL,
        {
            "status": audit["status"],
            "major_result_id": major["major_result_id"],
            "closure_level": major["closure_level"],
            "full_core_unlock": False,
        },
    )
    module_evidence = evidence(
        MODULE_REL,
        {"role": "scoped conservative-action Kubo identifiability no-go", "data_role": major["data_role"]},
    )
    transport_evidence = evidence(
        TRANSPORT_REL,
        {"role": "ideal action and Kubo admission contract"},
    )
    sk_evidence = evidence(
        SK_REL,
        {"role": "formal SK/KMS/entropy interface and physical-coefficient boundary"},
    )
    all_evidence = [audit_evidence, module_evidence, transport_evidence, sk_evidence]

    full = load(FULL_REL)
    full["generated_at"] = today
    full_major = full["major_result"]
    append_unique(
        full_major.setdefault("what_is_closed", []),
        "scoped no-go showing the current conservative single-copy action does not identify a unique physical Kubo/Onsager dissipative sector",
    )
    append_unique(
        full_major.setdefault("what_remains_open", []),
        "physical Kubo values still require a state-matched source or microscopic open-system/SK derivation",
    )
    transport = full.setdefault("verification_status", {}).setdefault(
        "eos_transport_kms_entropy", {}
    )
    transport["transport_coefficient_identifiability_no_go"] = {
        "major_result_id": major["major_result_id"],
        "status": audit["status"],
        "closure_level": major["closure_level"],
        "data_role": major["data_role"],
        "witnesses": audit["witnesses"],
        "audit": audit_evidence,
        "implementation": module_evidence,
        "transport_contract": transport_evidence,
        "sk_kms_contract": sk_evidence,
        "controlling_blocker": blocker,
        "claim_boundary": major["claim_boundary"],
    }
    for item in all_evidence:
        append_unique(full.setdefault("evidence_artifacts", []), item)
    full.setdefault("data_role", {})["transport_coefficient_identifiability_no_go"] = major["data_role"]
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["claim_promotion"] = False
    full["next_action"] = "Treat the Kubo no-go as closed for the current conservative action; acquire a state-matched physical Kubo record or derive an open-system/SK collision-noise kernel, while independently closing the Phi SI anchor and alpha."
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
    record["evidence_artifacts"] = all_evidence
    record["verification_status"] = audit["status"]
    register["entries"] = [
        item
        for item in register.get("entries", [])
        if item.get("major_result_id") != major["major_result_id"]
    ] + [record]
    full_entry = next(
        item
        for item in register["entries"]
        if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE"
    )
    append_unique(
        full_entry.setdefault("what_is_closed", []),
        "scoped conservative-action Kubo/Onsager identifiability no-go",
    )
    append_unique(full_entry.setdefault("open_blockers", []), blocker)
    append_unique(full_entry.setdefault("evidence_artifacts", []), audit_evidence)
    register["claim_promotion"] = False
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["transport_coefficient_identifiability_no_go"] = audit_evidence
    partial["transport_coefficient_identifiability_no_go_controller"] = blocker
    partial["transport_coefficient_identifiability_no_go_full_core_unlock"] = False
    partial["full_core_unlock"] = False
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Conservative-Action Kubo Identifiability Boundary (2026-08-12)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-034` | `S_cons[Phi,chi] -> P(X,Phi), N_ideal^mu, T_ideal^munu`; `J_diss^A=-L^(AB)X_B`; `nabla_mu J_S^mu=X_A L^(AB) X_B>=0` | `{AUDIT_REL}`; `{MODULE_REL}`; `{TRANSPORT_REL}`; `{SK_REL}` | ideal sector = natural action units; dissipative coefficients require source-declared units and state matching; SI map remains open | conservative action fixes ideal sector; dissipative witnesses are internal underdetermined completions, not physical values | scoped structural no-go passes: two distinct PSD/positive-relaxation witnesses satisfy the formal entropy contract while differing in response | shows that entropy positivity/formal SK interface cannot identify a unique physical Kubo coefficient from the current action | a synthetic Onsager matrix or formal positivity witness could be mistaken for physical transport evidence | add a matched retarded correlator/source record or a declared microscopic open-system/SK collision-noise derivation |

The lane uses no source rows, target curve, fit, `alpha_Phi_K`, or Xie 2026 holdout. It preserves the declared meanings of `C`, `Phi`, `R_gen`, and `R_obs`.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Conservative-Action Kubo Identifiability Boundary"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_AS_NO_GO`

WHAT_IS_ACTUALLY_CLOSED: The current single-copy conservative O(2) action
determines the ideal pressure/current/stress sector but does not determine a
unique dissipative Onsager/Kubo sector. Two distinct positive-semidefinite
matrices with positive relaxation times satisfy the formal entropy interface
while producing different dissipative responses. The result is a scoped
no-go for the current action, not a rejection of a future open-system UET
extension.

WHAT_REMAINS_OPEN: A physical coefficient still requires a state-matched
retarded correlator or a microscopic SK/open-system collision-noise derivation,
with units, temperature, chemical potential, Phi state, locator, source
identity, hash, and evidence status. Finite-temperature normal response, SI
transport, curved 3+1 transport, the Phi SI anchor, and `alpha_Phi_K` remain
open.

DEPENDENCY_UNLOCKED: Structural Kubo identifiability boundary only. No
physical transport, Full Topic 13, Core, Gravity, constitutive transport, or
external-validation dependency is unlocked.

STATUS: `{audit["status"]}`

WHAT_CHANGED: `{AUDIT_REL}` and `{MODULE_REL}` add two explicit PSD transport
witnesses and an action-level identifiability audit; this sync links them into
the full gate, closure register, dependency graph, formula audit, current
report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
S_cons[Phi,chi] -> ideal P(X,Phi), N_ideal^mu, T_ideal^munu
J_diss^A = -L^(AB) X_B, tau_A > 0
nabla_mu J_S^mu = X_A L^(AB) X_B >= 0
```

VERIFICATION: `{audit["status"]}`; the two witnesses are distinct, positive
semidefinite, and have positive relaxation times. The transport implementation
requires external or microscopic matching and emits no default physical
coefficient. Formal SK/KMS/entropy positivity is kept separate from physical
transport evidence. No fit, source row, or Xie 2026 holdout is used.

CONTROLLING_BLOCKER: `{blocker}` for the transport lane. The full Topic 13
controller remains `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`.

NEXT_ACTION: Acquire one state-matched physical Kubo record or derive a
microscopic open-system/SK collision-noise kernel. In parallel, obtain the
independent base-Phi SI anchor and `alpha_Phi_K` route; do not substitute the
internal witnesses as physical values.

CLAIM_BOUNDARY: This is a scoped structural identifiability no-go for the
current conservative action. It is not a physical transport measurement,
microscopic Kubo match, finite-temperature two-fluid closure, SI calibration,
external validation, or Full Topic 13 closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-12 - Conservative-action Kubo identifiability boundary"
    append_marker(
        LOG_REL,
        log_marker,
        f"""{log_marker}

- Scope: test whether the current conservative single-copy O(2) action identifies a unique physical dissipative/Kubo sector.
- Added or changed: `{MODULE_REL}`, `{AUDIT_REL}`, lane-key repair, full-gate/register/dependency integration, formula audit, current report, and ledger.
- Verified with: `{audit["status"]}`; two distinct PSD Onsager witnesses, positive relaxation times, transport admission boundary, and ontology/holdout checks pass.
- Result closed: `T13_TRANSPORT_COEFFICIENT_IDENTIFIABILITY_NO_GO` is `CLOSED_AS_NO_GO`.
- Blocker narrowed: entropy positivity and the formal SK/KMS interface do not identify a physical Kubo coefficient from the current action.
- Still open: state-matched physical Kubo evidence or microscopic open-system derivation, finite-T normal component, SI transport, curved 3+1 transport, SI Phi map, alpha, and Full Topic 13 closure.
- Next controller: acquire/derive the missing physical Kubo input; never promote the internal witnesses to measured coefficients.
- Claim impact: no promotion; Full Topic 13 remains `PARTIAL / BLOCKED`.
""",
    )

    ledger_marker = "## Topic 13 Conservative-Action Kubo Identifiability Boundary"
    append_marker(
        LEDGER_REL,
        ledger_marker,
        f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` transport identifiability lane and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added scoped conservative-action Kubo no-go and synchronized full gate, closure register, dependency evidence, formula audit, report, and update log
- verification: `{audit["status"]}`; distinct PSD witnesses, positive relaxation, admission boundary, and ontology/holdout checks pass
- public-safety status: `partial`; no physical coefficient or transport validation is claimed
- current claim boundary: `T13_TRANSPORT_COEFFICIENT_IDENTIFIABILITY_NO_GO` is `CLOSED_AS_NO_GO`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: acquire a state-matched physical Kubo record or derive the missing open-system/SK kernel
""",
    )

    print(
        json.dumps(
            {
                "status": "PASS_INTEGRATED_T13_TRANSPORT_COEFFICIENT_IDENTIFIABILITY_NO_GO",
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
