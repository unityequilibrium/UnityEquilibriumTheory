"""Synchronize the named Topic 13 collective-response EOS lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/07_artifacts/topic13/t13_collective_response_eos_stability_audit.json"
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

WHAT_IS_ACTUALLY_CLOSED: Topic 13 has lane-level causal selection, covariant
field-normalization and beta-symbol no-gos, a named finite-temperature
`beta_T13` functional, and a named collective-response EOS with explicit
derivatives, reciprocity, and local stability conditions. The results close
formula and ontology ambiguity, not physical material coefficients.

WHAT_REMAINS_OPEN: Source-backed finite-temperature coefficients, physical
Phi normalization and SI energy-density anchor, correspondence to core or
covariant coefficients, independent `alpha_Phi_K`, physical EOS observables,
covariant transport, SK/KMS, entropy production, and dissipative balance.

DEPENDENCY_UNLOCKED: A normalized response-EOS interface for later internal
derivations only. No Core-ready, Gravity/GR, transport, Galaxy, external-
validation, or global claim is unlocked.

STATUS: `{full['status']}`

WHAT_CHANGED: `{action['major_result']['major_result_id']}` is
`CLOSED_FOR_LANE`. `C` remains a collective coordinate and `Phi` an effective
response; the named `mu_C` and `mu_Phi` are normalized derivatives, not
measured chemical potentials or a charge EOS.

EQUATION_OR_MAPPING:

```text
f_hat = a_C C^2 / 2 + b_C C^4 / 4 + a_Phi(T) Phi^2 / 2
      + b_Phi Phi^4 / 4 - g C^2 Phi / 2
mu_C = a_C C + b_C C^3 - g C Phi
mu_Phi = a_Phi(T) Phi + b_Phi Phi^3 - g C^2 / 2
H_CPhi = H_PhiC = -g C
local stability: H_CC > 0, H_PhiPhi > 0, det(H) > 0
```

VERIFICATION: Analytic first and second derivatives match a synthetic finite-
difference witness; the Hessian is reciprocal and positive definite at the
declared witness point. The functional does not use a Landauer identity, no
fit, source row, target, or Xie 2026 holdout.

CONTROLLING_BLOCKER: `{full['controlling_blocker']}`. The EOS-lane controller
is `source_backed_finite_temperature_EOS_coefficient_provenance_and_physical_Phi_SI_anchor_missing`.

NEXT_ACTION: Source-lock coefficient provenance and the Phi/e0 SI observable
anchor independently of TTG target fitting. Then extend this named lane to
covariant transport, SK/KMS, entropy production, and dissipative balance.

CLAIM_BOUNDARY: UET remains a candidate effective theory. No physical charge
EOS, mass/particle/information-field identification, transport coefficient,
entropy-production law, external validation, full Topic 13 closure, or
downstream unlock is claimed.
"""
    (ROOT / CURRENT_REPORT_REL).write_text(report, encoding="utf-8")


def main() -> int:
    action = load(ACTION_REL)
    expected = "PASS_NAMED_COLLECTIVE_RESPONSE_EOS_STABILITY_CONTRACT"
    if action.get("status") != expected:
        raise SystemExit(f"collective-response EOS audit is not passing: {action.get('status')}")
    today = date.today().isoformat()
    full = load(FULL_REL)
    full["generated_at"] = today
    append_unique(full["major_result"]["what_is_closed"], "named collective-response finite-temperature EOS derivatives, reciprocity, and local stability contract")
    append_unique(full["major_result"]["what_remains_open"], "source_backed_finite_temperature_EOS_coefficient_provenance_and_physical_Phi_SI_anchor_missing")
    eos = full.setdefault("verification_status", {}).setdefault("eos_transport_kms_entropy", {})
    eos["named_collective_response_eos_status"] = "CLOSED_FOR_LANE"
    eos["named_collective_response_eos_physical_provenance"] = "BLOCKED"
    eos["named_collective_response_eos_audit"] = evidence(ACTION_REL, {"status": action["status"], "major_result_id": action["major_result"]["major_result_id"]})
    eos["controlling_blocker_detail"] = action["controlling_blocker"]
    full["verification_status"]["collective_response_eos_stability_contract"] = {
        "status": action["status"],
        "closure_level": "CLOSED_FOR_LANE",
        "numeric_coefficients_emitted": False,
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
    append_unique(full_entry["what_is_closed"], "named collective-response finite-temperature EOS derivatives, reciprocity, and local stability contract")
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
    partial["collective_response_eos_stability_contract"] = evidence(ACTION_REL, {"status": action["status"], "full_core_unlock": False})
    partial["reason"] = "Topic 13 has lane-level causal, field-normalization, beta, and collective-response EOS contracts; none supplies physical coefficient provenance, an SI Phi anchor, alpha_Phi_K, transport, KMS, entropy production, or full closure."
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    write_current_report(full, action)

    log_marker = "### 2026-08-11 - Named collective-response EOS and stability contract"
    log_path = ROOT / LOG_REL
    log = log_path.read_text(encoding="utf-8-sig")
    if log_marker not in log:
        log += f"""

{log_marker}

- Scope: close the formula-level finite-temperature EOS, reciprocity, and stability interface without changing Topic 13 ontology.
- Added or changed: `thermal_collective_response_eos.py`, formula record, derivative/stability audit, major-result record, full-gate/register/dependency synchronization, current-state report, and regression tests.
- Verified with: `{action['status']}`; first/second derivatives match finite differences, mixed derivatives are reciprocal, and the declared synthetic witness is locally stable. No Landauer identity, source row, fit, target, or holdout is consumed.
- Result closed: `{action['major_result']['major_result_id']}` is `CLOSED_FOR_LANE`; the named lane has a concrete response-EOS interface.
- Still open: physical coefficient provenance and Phi/e0 SI anchor, physical EOS observables, alpha calibration, covariant transport, SK/KMS, entropy production, and dissipative balance.
- Claim impact: no promotion. The Full Topic 13 gate remains `PARTIAL/BLOCKED`; `C` is not called charge/mass and `Phi` is not called information/temperature/heat flux.
"""
        log_path.write_text(log, encoding="utf-8")

    ledger_path = ROOT / LEDGER_REL
    ledger = ledger_path.read_text(encoding="utf-8-sig") if ledger_path.is_file() else "# 2026-08-11\n"
    ledger_marker = "## Topic 13 Named Collective-Response EOS Contract"
    if ledger_marker not in ledger:
        ledger += f"""

{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` named EOS contract
- changed: declared the collective-response EOS/stability lane, added formula/audit/tests/current report, and synchronized closure records
- verification: `{action['status']}`; finite-difference derivatives, reciprocity, stability, ontology, and no-data-use boundaries are checked
- public-safety status: `partial`; this is a normalized candidate EOS without physical coefficient provenance or observable calibration
- current claim boundary: collective-response EOS contract `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: source-lock finite-temperature coefficients and Phi/e0 SI anchor, then close covariant transport, SK/KMS, entropy production, and dissipative balance
"""
        ledger_path.write_text(ledger, encoding="utf-8")

    print(json.dumps({"status": "PASS_INTEGRATED_T13_COLLECTIVE_RESPONSE_EOS_STABILITY_CONTRACT", "major_result_id": action["major_result"]["major_result_id"], "closure_level": "CLOSED_FOR_LANE", "full_topic13_status": full["status"], "full_gate_sha256": digest(FULL_REL), "register_sha256": digest(REGISTER_REL), "dependency_unlock": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
