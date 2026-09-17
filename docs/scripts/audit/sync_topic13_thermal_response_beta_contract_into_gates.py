"""Synchronize the named Topic 13 finite-temperature beta contract."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/07_artifacts/topic13/t13_thermal_response_beta_contract_audit.json"
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

WHAT_IS_ACTUALLY_CLOSED: Topic 13 now has lane-level causal selection,
covariant field-normalization and beta-symbol no-gos, plus a named finite-
temperature response functional where `beta_T13` has a declared action term,
units, and entropy derivative. This avoids a Landauer shortcut without
claiming the coefficient is physically derived.

WHAT_REMAINS_OPEN: Source-backed `a_Phi(T)`/`beta_T13` provenance, physical
Phi normalization and SI energy-density anchor, correspondence to a core or
covariant coefficient, independent `alpha_Phi_K`, finite-temperature EOS,
covariant transport, SK/KMS, entropy production, and dissipative balance.

DEPENDENCY_UNLOCKED: A formula/unit interface for later EOS and entropy work
only. No Core-ready, Gravity/GR, transport, Galaxy, external-validation, or
global claim is unlocked.

STATUS: `{full['status']}`

WHAT_CHANGED: `{action['major_result']['major_result_id']}` is
`CLOSED_FOR_LANE`. The legacy `beta_core` remains a separate normalized
coupling; it is not identified with `beta_T13`, `Phi`, or a physical thermal
coefficient.

EQUATION_OR_MAPPING:

```text
f_hat_T13(C, Phi, T) = a_Phi(T) Phi^2 / 2 + b_Phi Phi^4 / 4 - g C^2 Phi / 2
beta_T13 = T0 * (da_Phi / dT)|T0
a_Phi(T) = a_Phi(T0) + beta_T13 * (T - T0) / T0
s = -partial_T(e0 f_hat_T13) = -e0 Phi^2 beta_T13 / (2 T0)

y_TTG = Delta_Tq(t) / Delta_Tq(0)
y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)
Delta_Tq = alpha_Phi_K * Delta_Phi
```

VERIFICATION: Analytic and finite-difference entropy derivatives agree on a
synthetic unit witness. `T0` is K, `da_Phi/dT` is K^-1, and `e0` is an
external J m^-3 input. No Landauer term, fit, source row, target, or Xie 2026
holdout was used.

CONTROLLING_BLOCKER: `{full['controlling_blocker']}`. The beta-lane controller
is `beta_T13_source_backed_temperature_coefficient_provenance_and_physical_Phi_SI_anchor_missing`.

NEXT_ACTION: Source-lock a material-relevant temperature coefficient path and
the Phi/e0 SI anchor independently of TTG target fitting. Then test finite-
temperature EOS, transport, SK/KMS, entropy production, and dissipative
balance under this named lane.

CLAIM_BOUNDARY: UET remains a candidate effective theory. `C` remains a
collective coordinate, `Phi` an effective response, and `R_gen` a derived
history trace. No UET-wide beta, Kelvin prediction, physical entropy-
production law, external validation, full Topic 13 closure, or downstream
unlock is claimed.
"""
    (ROOT / CURRENT_REPORT_REL).write_text(report, encoding="utf-8")


def main() -> int:
    action = load(ACTION_REL)
    expected = "PASS_NAMED_FINITE_TEMPERATURE_BETA_CONTRACT"
    if action.get("status") != expected:
        raise SystemExit(f"thermal response beta contract is not passing: {action.get('status')}")
    today = date.today().isoformat()
    full = load(FULL_REL)
    full["generated_at"] = today
    append_unique(full["major_result"]["what_is_closed"], "named beta_T13 finite-temperature response-functional formula and unit contract, independent of Landauer identity reuse")
    append_unique(full["major_result"]["what_remains_open"], "beta_T13_source_backed_temperature_coefficient_provenance_and_physical_Phi_SI_anchor_missing")
    bridge = full.setdefault("verification_status", {}).setdefault("non_circular_bridge", {})
    bridge["beta_T13_contract_status"] = "CLOSED_FOR_LANE"
    bridge["beta_T13_contract_physical_provenance"] = "BLOCKED"
    bridge["beta_T13_contract_audit"] = evidence(ACTION_REL, {"status": action["status"], "major_result_id": action["major_result"]["major_result_id"]})
    bridge["controlling_blocker_detail"] = action["controlling_blocker"]
    full["verification_status"]["thermal_response_beta_contract"] = {
        "status": action["status"],
        "closure_level": "CLOSED_FOR_LANE",
        "numeric_beta_T13_emitted": False,
        "numeric_e0_emitted": False,
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "source_rows_consumed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "audit": evidence(ACTION_REL, {"status": action["status"], "major_result_id": action["major_result"]["major_result_id"]}),
        "controlling_blocker": action["controlling_blocker"],
        "claim_boundary": action["claim_boundary"],
    }
    append_unique(full.setdefault("evidence_artifacts", []), evidence(ACTION_REL, {"status": action["status"], "data_role": action["major_result"]["data_role"]}))
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry["what_is_closed"], "named beta_T13 finite-temperature response-functional formula and unit contract, independent of Landauer identity reuse")
    append_unique(full_entry["open_blockers"], action["controlling_blocker"])
    append_unique(full_entry["evidence_artifacts"], evidence(ACTION_REL, {"status": action["status"], "major_result_id": action["major_result"]["major_result_id"]}))
    for item in full_entry["evidence_artifacts"]:
        if item.get("path") == FULL_REL:
            item["sha256"] = digest(FULL_REL)
    entry = next((item for item in register["entries"] if item.get("major_result_id") == action["major_result"]["major_result_id"]), None)
    if entry is None:
        register["entries"].append({
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
        })
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["thermal_response_beta_contract"] = evidence(ACTION_REL, {"status": action["status"], "full_core_unlock": False})
    partial["reason"] = "Topic 13 has explicit causal, field-normalization, symbol-separation, and beta-functional lane contracts; none supplies source-backed coefficients, an SI Phi anchor, alpha_Phi_K, EOS, transport, KMS, entropy production, or full closure."
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    write_current_report(full, action)

    log_marker = "### 2026-08-11 - Named finite-temperature beta_T13 contract"
    log_path = ROOT / LOG_REL
    log = log_path.read_text(encoding="utf-8-sig")
    if log_marker not in log:
        log += f"""

{log_marker}

- Scope: give the Topic 13 thermal response a non-Landauer beta definition with an explicit finite-temperature functional, units, and derivative boundary.
- Added or changed: `thermal_response_beta_contract.py`, formula record, structural/finite-difference audit, major-result record, full-gate/register/dependency synchronization, current-state report, and regression tests.
- Verified with: `{action['status']}`; beta_T13 recovers from the declared stiffness slope and the analytic entropy derivative matches a synthetic finite difference. The contract does not identify beta_T13 with beta_th, beta_core, beta_wave, Phi as an SI field, or R_gen.
- Result closed: `{action['major_result']['major_result_id']}` is `CLOSED_FOR_LANE`; action-term and unit ambiguity is closed for the named candidate lane.
- Still open: source-backed coefficient provenance, physical Phi/e0 SI anchor, correspondence to a core or covariant coefficient, alpha calibration, finite-temperature EOS/transport/SK-KMS/entropy production, and dissipative balance.
- Claim impact: no promotion. The Full Topic 13 gate remains `PARTIAL/BLOCKED`; no numeric beta/e0/alpha, source calibration, target fit, or holdout access occurred.
"""
        log_path.write_text(log, encoding="utf-8")

    ledger_path = ROOT / LEDGER_REL
    ledger = ledger_path.read_text(encoding="utf-8-sig") if ledger_path.is_file() else "# 2026-08-11\n"
    ledger_marker = "## Topic 13 Named Finite-Temperature beta_T13 Contract"
    if ledger_marker not in ledger:
        ledger += f"""

{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` thermal-response contract
- changed: declared the beta_T13 finite-temperature lane, added formula/audit/tests/current report, and synchronized closure records
- verification: `{action['status']}`; derivative, units, beta recovery, beta-symbol separations, and no-data-use boundary are checked
- public-safety status: `partial`; beta_T13 is a candidate formula coefficient with no source-backed value or physical calibration
- current claim boundary: beta_T13 contract `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: source-lock temperature-coefficient provenance plus Phi/e0 SI anchor, then test EOS/transport/KMS/entropy/dissipation in the named lane
"""
        ledger_path.write_text(ledger, encoding="utf-8")

    print(json.dumps({"status": "PASS_INTEGRATED_T13_THERMAL_RESPONSE_BETA_CONTRACT", "major_result_id": action["major_result"]["major_result_id"], "closure_level": "CLOSED_FOR_LANE", "full_topic13_status": full["status"], "full_gate_sha256": digest(FULL_REL), "register_sha256": digest(REGISTER_REL), "dependency_unlock": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
