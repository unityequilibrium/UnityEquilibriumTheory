"""Synchronize the Topic 13 beta-symbol no-go into closure records and reports."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/07_artifacts/topic13/t13_beta_symbol_separation_noncircularity_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-11.md"
CURRENT_REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"


def load(rel: str) -> dict[str, Any]:
    value = json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def append_unique(items: list[Any], value: Any) -> None:
    if value not in items:
        items.append(value)


def evidence(rel: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": rel, "sha256": digest(rel), "summary": summary}


def write_current_report(full: dict[str, Any], action: dict[str, Any]) -> None:
    report = f"""# Topic 0.13 Current Full-Bridge State

Machine-readable authority: `{FULL_REL}`.

MAJOR_RESULT_CLOSURE: `{full['major_result']['closure_level']}`

WHAT_IS_ACTUALLY_CLOSED: Topic 13 has closed the normalized TTG/Phi
measurement operators, the source/energy mapping lanes recorded in the full
gate, the causal branch selection result, the covariant field-normalization
no-go, and the beta-symbol separation no-go. The last result establishes that
Landauer inverse temperature, the legacy normalized core coupling, and the
hyperbolic comparator coefficient cannot be merged into a derived UET thermal
coefficient by name.

WHAT_REMAINS_OPEN: Physical field normalization or an independent
`alpha_Phi_K` calibration; a declared `beta_UET` action term with units and
finite-temperature provenance; the non-circular UET bridge; EOS, covariant
transport, SK/KMS, entropy current, dissipative balance, and physical
heat-flux/entropy observable mappings.

DEPENDENCY_UNLOCKED: Lane-level ambiguity is closed only. No Core curved 3+1,
Gravity/GR, full constitutive transport, Galaxy, external validation, or
global UET claim is unlocked.

STATUS: `{full['status']}`

WHAT_CHANGED: `{action['major_result']['major_result_id']}` is
`CLOSED_FOR_LANE`. The pre-existing legacy phrase `UET beta prediction` is
recorded as non-accepted wording rather than silently accepted as a derivation.

EQUATION_OR_MAPPING:

```text
beta_th = 1 / (k_B T)
E_L = k_B T ln(2) = ln(2) / beta_th
beta_core = normalized dimensionless coupling
v_aux^2 = gamma_gradient / beta_wave

y_TTG = Delta_Tq(t) / Delta_Tq(0)
y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)
Delta_Tq = alpha_Phi_K * Delta_Phi
```

VERIFICATION: The beta audit confirms the standard Landauer identity while
showing that changing `beta_core` or `beta_wave` leaves it unchanged. The
selected causal branch contains no `beta` alias; the normalized thermal
functional still has no explicit temperature argument, SI free-energy scale,
or source-backed temperature-dependent coefficient functions. No parameter
fit, source row, target data, or Xie 2026 holdout was used.

CONTROLLING_BLOCKER: `{full['controlling_blocker']}`.
The beta-specific controller is
`declared_beta_UET_action_term_units_and_finite_temperature_derivation_missing`.

NEXT_ACTION: Define one `beta_UET` inside a declared finite-temperature
functional/action with units, independent coefficient provenance, and an SI
observable contract. In parallel, source-lock a physical field amplitude or
independent `alpha_Phi_K` calibration. Only then can the EOS/transport/KMS/
entropy closure be tested without circular use of Landauer.

CLAIM_BOUNDARY: UET remains a candidate effective theory. `C` remains a
collective coordinate, `Phi` an effective response, and `R_gen` a derived
history trace. This report claims neither a UET beta derivation nor a thermal
prediction, external validation, full Topic 13 closure, or downstream unlock.
"""
    (ROOT / CURRENT_REPORT_REL).write_text(report, encoding="utf-8")


def main() -> int:
    action = load(ACTION_REL)
    expected = "PASS_SCOPED_NO_GO_BETA_SYMBOL_IDENTIFICATION"
    if action.get("status") != expected:
        raise SystemExit(f"beta-symbol audit is not passing: {action.get('status')}")

    today = date.today().isoformat()
    full = load(FULL_REL)
    full["generated_at"] = today
    append_unique(
        full["major_result"]["what_is_closed"],
        "beta symbol roles are separated; Landauer inverse temperature cannot identify a normalized core or comparator coefficient as a UET thermal bridge beta",
    )
    append_unique(
        full["major_result"]["what_remains_open"],
        "declared_beta_UET_action_term_units_and_finite_temperature_derivation_missing",
    )
    full.setdefault("verification_status", {})[
        "beta_symbol_separation_noncircularity_no_go"
    ] = {
        "status": "PASS_SCOPED_NO_GO",
        "closure_level": "CLOSED_FOR_LANE",
        "numeric_beta_UET_emitted": False,
        "numeric_e0_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "source_rows_consumed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "audit": evidence(
            ACTION_REL,
            {
                "status": action["status"],
                "major_result_id": action["major_result"]["major_result_id"],
            },
        ),
        "controlling_blocker": action["controlling_blocker"],
        "claim_boundary": action["claim_boundary"],
    }
    append_unique(
        full.setdefault("evidence_artifacts", []),
        evidence(
            ACTION_REL,
            {"status": action["status"], "data_role": action["major_result"]["data_role"]},
        ),
    )
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    full_entry = next(
        item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE"
    )
    append_unique(
        full_entry["what_is_closed"],
        "beta symbol roles are separated; Landauer inverse temperature cannot identify a normalized core or comparator coefficient as a UET thermal bridge beta",
    )
    append_unique(full_entry["open_blockers"], action["controlling_blocker"])
    append_unique(
        full_entry["evidence_artifacts"],
        evidence(
            ACTION_REL,
            {"status": action["status"], "major_result_id": action["major_result"]["major_result_id"]},
        ),
    )
    for item in full_entry["evidence_artifacts"]:
        if item.get("path") == FULL_REL:
            item["sha256"] = digest(FULL_REL)

    entry = next(
        (
            item
            for item in register["entries"]
            if item.get("major_result_id") == action["major_result"]["major_result_id"]
        ),
        None,
    )
    if entry is None:
        register["entries"].append(
            {
                "major_result_id": action["major_result"]["major_result_id"],
                "topic": action["major_result"]["topic"],
                "closure_level": action["major_result"]["closure_level"],
                "what_is_closed": action["major_result"]["what_is_closed"],
                "equation_or_mapping": action["major_result"]["equation_or_mapping"],
                "units": action["major_result"]["units"],
                "derivation_class": action["major_result"]["derivation_class"],
                "observable": action["major_result"]["observable"],
                "data_role": action["major_result"]["data_role"],
                "evidence_artifacts": [evidence(ACTION_REL, {"status": action["status"]})],
                "verification_status": action["status"],
                "open_blockers": action["major_result"]["open_blockers"],
                "dependency_unlocked": action["major_result"]["dependency_unlocked"],
                "claim_boundary": action["major_result"]["claim_boundary"],
            }
        )
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["beta_symbol_separation_noncircularity_no_go"] = evidence(
        ACTION_REL, {"status": action["status"], "full_core_unlock": False}
    )
    partial["reason"] = (
        "Lane-level no-gos make physical normalization and non-circular thermal-coefficient requirements explicit; "
        "they do not supply beta_UET, e0, alpha_Phi_K, EOS, transport, KMS, entropy, or full thermodynamic closure."
    )
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    write_current_report(full, action)

    log_marker = "### 2026-08-11 - Beta-symbol separation and non-circularity no-go"
    log_path = ROOT / LOG_REL
    log = log_path.read_text(encoding="utf-8-sig")
    if log_marker not in log:
        log += f"""

{log_marker}

- Scope: determine whether Landauer inverse temperature, the legacy core coupling, or the hyperbolic comparator coefficient can close the Topic 13 beta/thermal bridge.
- Added or changed: a formula record, a machine-readable symbol-separation/no-go artifact, focused regression checks, full-gate/register/dependency synchronization, and an updated current-state report.
- Verified with: `{action['status']}`; the standard Landauer identity is algebraically correct but leaves distinct normalized coefficients free, the selected causal branch has no beta alias, and the current thermal functional lacks the finite-temperature/SI inputs required for beta_UET.
- Result closed: `{action['major_result']['major_result_id']}` is `CLOSED_FOR_LANE`; the legacy printed phrase `UET beta prediction` is not accepted as a derivation.
- Still open: a declared beta_UET action term and units, finite-temperature coefficient provenance independent of Landauer, SI observable contract, physical Phi normalization or independent alpha, and the full EOS/transport/KMS/entropy closure.
- Claim impact: no promotion. The Full Topic 13 gate remains `PARTIAL/BLOCKED`; no numeric beta, e0, alpha, source calibration, target data, or holdout use occurred.
"""
        log_path.write_text(log, encoding="utf-8")

    ledger_path = ROOT / LEDGER_REL
    ledger = ledger_path.read_text(encoding="utf-8-sig") if ledger_path.is_file() else "# 2026-08-11\n"
    ledger_marker = "## Topic 13 Beta Symbol Separation"
    if ledger_marker not in ledger:
        ledger += f"""

{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` coefficient artifacts
- changed: added a beta-symbol separation/no-go, formula record, focused tests, current-state report, and synchronized closure records
- verification: `{action['status']}`; Landauer identity, unit-role separation, selected-branch alias exclusion, thermal-input requirements, and no-data-use boundary are checked
- public-safety status: `partial`; no UET beta, SI mapping, temperature prediction, source calibration, or holdout result was emitted
- current claim boundary: beta-symbol separation no-go `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: declare beta_UET with finite-temperature action/units/provenance and an SI observable contract, while independently closing physical Phi normalization or alpha calibration
"""
        ledger_path.write_text(ledger, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "PASS_INTEGRATED_T13_BETA_SYMBOL_SEPARATION_NO_GO",
                "major_result_id": action["major_result"]["major_result_id"],
                "closure_level": "CLOSED_FOR_LANE",
                "full_topic13_status": full["status"],
                "full_gate_sha256": digest(FULL_REL),
                "register_sha256": digest(REGISTER_REL),
                "dependency_unlock": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
