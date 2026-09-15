"""Integrate the formal Topic 13 SK/KMS/entropy lane without promoting it."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/07_artifacts/topic13/t13_sk_kms_entropy_contract_audit.json"
MODULE_REL = "docs/core/thermal_sk_kms_entropy_contract.py"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
FORMULA_REL = "docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md"
REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-11.md"


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
    action = load(ACTION_REL)
    if action.get("status") != "PASS_NAMED_SK_KMS_ENTROPY_INTERFACE_CONTRACT":
        raise SystemExit(f"SK/KMS/entropy audit is not passing: {action.get('status')}")
    today = date.today().isoformat()
    major = action["major_result"]
    blocker = action["controlling_blocker"]

    full = load(FULL_REL)
    full["generated_at"] = today
    append_unique(full["major_result"]["what_is_closed"], "formal local SK/KMS response-noise, entropy-current, and exchange-balance interface")
    for item in action["major_result"]["open_blockers"]:
        append_unique(full["major_result"]["what_remains_open"], item)
    transport_gate = full.setdefault("verification_status", {}).setdefault("eos_transport_kms_entropy", {})
    transport_gate["named_sk_kms_entropy_interface"] = {
        "status": action["status"],
        "closure_level": "CLOSED_FOR_LANE",
        "physical_coefficient_evidence": "BLOCKED_NOT_PROVIDED",
        "finite_temperature_completion": "BLOCKED",
        "full_SK_KMS_completion": "INTERFACE_ONLY_NOT_FULL_MATCH",
        "audit": evidence(ACTION_REL, {"status": action["status"], "major_result_id": major["major_result_id"]}),
        "claim_boundary": action["claim_boundary"],
    }
    full.setdefault("verification_status", {})["sk_kms_entropy_interface"] = {
        "status": action["status"],
        "closure_level": "CLOSED_FOR_LANE",
        "numeric_transport_coefficients_emitted": False,
        "parameter_fitting_performed": False,
        "source_rows_consumed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "audit": evidence(ACTION_REL, {"status": action["status"], "data_role": major["data_role"]}),
        "controlling_blocker": blocker,
        "claim_boundary": action["claim_boundary"],
    }
    append_unique(full.setdefault("evidence_artifacts", []), evidence(ACTION_REL, {"status": action["status"], "data_role": major["data_role"]}))
    full["claim_promotion"] = False
    full["next_action"] = (
        "Keep the formal SK/KMS/entropy interface as a lane contract; source-lock or microscopically match physical Kubo coefficients, "
        "complete the finite-temperature normal component and curved 3+1 transport, and independently close the base-Phi SI anchor."
    )
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    append_unique(full_entry["what_is_closed"], "formal local SK/KMS response-noise, entropy-current, and exchange-balance interface")
    for item in action["major_result"]["open_blockers"]:
        append_unique(full_entry["open_blockers"], item)
    append_unique(full_entry["evidence_artifacts"], evidence(ACTION_REL, {"status": action["status"], "major_result_id": major["major_result_id"]}))
    for item in full_entry["evidence_artifacts"]:
        if item.get("path") == FULL_REL:
            item["sha256"] = digest(FULL_REL)
    entry = next((item for item in register["entries"] if item.get("major_result_id") == major["major_result_id"]), None)
    record = {key: major[key] for key in ("major_result_id", "topic", "closure_level", "what_is_closed", "equation_or_mapping", "units", "derivation_class", "observable", "data_role", "evidence_artifacts", "verification_status", "open_blockers", "dependency_unlocked", "claim_boundary")}
    record["evidence_artifacts"] = [evidence(ACTION_REL, {"status": action["status"]})]
    if entry is None:
        register["entries"].append(record)
    else:
        entry.clear()
        entry.update(record)
    register["next_major_result"] = "T13_FULL_THERMODYNAMIC_BRIDGE"
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["sk_kms_entropy_interface"] = evidence(ACTION_REL, {"status": action["status"], "full_core_unlock": False, "closure_level": "CLOSED_FOR_LANE"})
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    formula_marker = "## Formal SK/KMS and Entropy Interface (2026-08-11)"
    formula_content = f"""{formula_marker}

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T13-021` | `S_SK = integral [Phi_a D_R Phi_r + i Phi_a N Phi_a/2]`; `N(omega)=coth(beta_th omega/2)*2 Im D_R`; `J_S^mu=s u^mu+q^mu/T`; `nabla_mu J_S^mu >= 0` under PSD `L` | `{MODULE_REL}`; `{ACTION_REL}` | `Phi_r,Phi_a` = dimensionless contour response copies; `beta_th` = J^-1; `q` = W m^-2; `T` = K; `kappa` = W m^-1 K^-1; `J_S` = W m^-2 K^-1 | standard KMS/Onsager interface plus declared UET lane notation; no physical coefficient supplied | formal lane contract and algebraic positivity witness; not microscopic derivation | separates SK/KMS structure, entropy positivity, and exchange-current balance from physical Kubo matching | formal positivity can be mistaken for physical transport closure or a base-Phi SI map | source-lock or microscopically match coefficients, complete finite-temperature normal sector and curved 3+1, then rerun with physical units and provenance |

The contract keeps `beta_th` distinct from `beta_T13` and `beta_core`. `Phi_a`
is a contour-difference response copy, not a new physical field. `R_gen` is
absent and has no backreaction. The witness closes only the formal lane.
"""
    append_marker(FORMULA_REL, formula_marker, formula_content)

    report_marker = "## Formal SK/KMS and Entropy Interface"
    report_content = f"""{report_marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: Topic 13 now has a named local SK response/noise
interface, KMS relation, entropy-current form, Onsager positivity witness, and
exchange-current balance that does not give `R_gen` backreaction.

WHAT_REMAINS_OPEN: Physical Kubo coefficient provenance, finite-temperature
normal component, curved 3+1 transport, base-Phi SI normalization, and external
transport validation remain open.

DEPENDENCY_UNLOCKED: Formal lane only. No full transport, Full Topic 13, Core,
Gravity, or external-claim dependency is unlocked.

STATUS: `{action['status']}`

WHAT_CHANGED: `{ACTION_REL}` and `{MODULE_REL}` were added and linked into the
full gate, major-result register, dependency gate, formula audit, and update log.

EQUATION_OR_MAPPING:

```text
S_SK = integral [Phi_a D_R Phi_r + i Phi_a N Phi_a/2]
N(omega) = coth(beta_th omega/2) * 2 Im D_R(omega)
J_S^mu = s u^mu + q^mu/T
nabla_mu T_matter^(mu nu) = Q^nu
nabla_mu T_UET^(mu nu) = -Q^nu
```

VERIFICATION: The KMS noise witness is nonnegative for a positive retarded
spectral term, and the declared Onsager witness is symmetric positive
semidefinite. No source rows, fit, target, Xie 2026 holdout, or numeric physical
transport coefficient was used.

CONTROLLING_BLOCKER: `{blocker}`

NEXT_ACTION: Source-lock or microscopically match state-specific Kubo
coefficients, complete finite-temperature and curved transport, and keep this
formal witness separate from physical validation.

CLAIM_BOUNDARY: This is a formal candidate interface, not microscopic SK/KMS
matching, physical entropy-production validation, SI Phi calibration, or global
UET closure.
"""
    append_marker(REPORT_REL, report_marker, report_content)

    log_marker = "### 2026-08-11 - Formal SK/KMS and entropy interface"
    log_content = f"""{log_marker}

- Scope: add the Topic 13 formal SK/KMS, entropy-current, positivity, and exchange-balance interface without claiming physical transport closure.
- Wave type: artifact pass / formula-audit pass.
- Added or changed: `{MODULE_REL}`, `{ACTION_REL}`, integration sync, formula record, report section, dependency evidence, and regression tests.
- Verified with: `{action['status']}`; KMS noise and Onsager entropy witnesses pass while physical coefficient evidence remains blocked.
- Result: `T13_SK_KMS_ENTROPY_INTERFACE_CONTRACT` is `CLOSED_FOR_LANE`.
- Blocker narrowed: the formal structure is separated from the remaining `physical_Kubo_coefficient_provenance_missing` blocker.
- Still open: physical Kubo matching, finite-temperature normal component, curved 3+1 transport, base-Phi SI anchor, and external validation.
- Next controller: source-lock/microscopically match coefficients and complete the missing physical dependencies.
- Claim impact: no promotion; the formal interface does not unlock full Topic 13 or downstream gravity.
"""
    append_marker(LOG_REL, log_marker, log_content)

    ledger_marker = "## Topic 13 Formal SK KMS Entropy Interface"
    ledger_content = f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` transport contracts
- changed: added the formal SK/KMS/entropy module, audit artifact, gate/register/dependency integration, formula entry, and tests
- verification: `{action['status']}`; KMS noise and Onsager positivity witnesses pass with no source rows or physical coefficient values
- public-safety status: `partial`; formal lane is closed for lane, physical transport and finite-temperature completion remain blocked
- current claim boundary: `T13_SK_KMS_ENTROPY_INTERFACE_CONTRACT` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated user changes were not edited
- next action: source-lock/microscopically match Kubo coefficients and complete finite-temperature/curved transport
"""
    append_marker(LEDGER_REL, ledger_marker, ledger_content)

    print(json.dumps({
        "status": "PASS_INTEGRATED_T13_SK_KMS_ENTROPY_INTERFACE",
        "major_result_id": major["major_result_id"],
        "closure_level": "CLOSED_FOR_LANE",
        "full_topic13_status": full["status"],
        "full_gate_sha256": digest(FULL_REL),
        "register_sha256": digest(REGISTER_REL),
        "dependency_unlock": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
