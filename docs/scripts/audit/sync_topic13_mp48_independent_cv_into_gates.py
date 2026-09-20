"""Integrate the independently audited mp-48 c_v lane conservatively."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/topic13/t13_mp48_independent_graphite_cv_audit.json"
PACKAGE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "mp48_independent_graphite_cv_source_package.json"
)
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-11.md"
NARROW_DING_BLOCKER = "ding_source_specific_C_src_and_mode_resolved_c_mu_not_available"


def load(rel: str) -> dict[str, Any]:
    with (ROOT / rel).open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {rel}")
    return value


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def replace_recursive(value: Any, old: str, new: str) -> Any:
    if isinstance(value, str):
        return new if value == old else value
    if isinstance(value, list):
        return [replace_recursive(item, old, new) for item in value]
    if isinstance(value, dict):
        return {key: replace_recursive(item, old, new) for key, item in value.items()}
    return value


def append_unique(items: list[Any], value: Any) -> None:
    if value not in items:
        items.append(value)


def evidence(rel: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": rel, "sha256": digest(rel), "summary": summary}


def main() -> int:
    audit = load(AUDIT_REL)
    package = load(PACKAGE_REL)
    if audit.get("status") != "PASS_INDEPENDENT_NUMERIC_CV_WITH_EPISTEMIC_ENVELOPE":
        raise SystemExit(f"mp-48 audit is not passing: {audit.get('status')}")

    today = date.today().isoformat()
    route = {
        "status": "PASS",
        "closure_level": "CLOSED_FOR_LANE",
        "source_status": audit["status"],
        "major_result_id": "T13_MP48_INDEPENDENT_GRAPHITE_CV_REPRODUCTION",
        "data_role": "INDEPENDENT_REPRODUCTION_NOT_CALIBRATION",
        "calibration_consumed": False,
        "target_curve_used": False,
        "holdout_consumed": False,
        "audit": evidence(
            AUDIT_REL,
            {
                "status": audit["status"],
                "closure_level": "CLOSED_FOR_LANE",
                "controlling_blocker": audit["controlling_blocker"],
            },
        ),
        "source_package": evidence(
            PACKAGE_REL,
            {
                "status": package["status"],
                "source_id": package["source"]["source_id"],
                "data_role": package["major_result"]["data_role"],
            },
        ),
        "claim_boundary": package["claim_boundary"],
    }

    full = load(FULL_REL)
    full = replace_recursive(full, "ding_pbte_author_data_or_independent_reproduction_package_missing", NARROW_DING_BLOCKER)
    full["generated_at"] = today
    full["major_result"]["closure_level"] = "PARTIAL"
    append_unique(
        full["major_result"]["what_is_closed"],
        "independent mp-48 harmonic graphite heat-capacity comparator with provenance, volumetric conversion, and epistemic envelope",
    )
    full["major_result"]["what_remains_open"] = [
        item
        for item in full["major_result"]["what_remains_open"]
        if item != "ding_pbte_author_data_or_independent_reproduction_package_missing"
    ]
    append_unique(full["major_result"]["what_remains_open"], NARROW_DING_BLOCKER)
    verification = full.setdefault("verification_status", {})
    verification["independent_graphite_cv_route"] = route
    data_role = full.setdefault("data_role", {})
    data_role["independent_heat_capacity_source"] = "CLOSED_FOR_LANE_COMPARATOR_NOT_CALIBRATION"
    data_role["independent_heat_capacity_audit"] = audit["status"]
    full["source_acquisition_controller"] = (
        "Ding-specific C_src(T), mode-resolved c_mu, uncertainty/convergence, "
        "and the Phi energy anchor remain open; independent mp-48 comparator route is closed for lane"
    )
    full["controlling_blocker"] = "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    full["next_action"] = (
        "Derive or independently source-lock e0 and the base Phi-to-Delta_u_ph correspondence; "
        "then construct an uncertainty-bearing alpha_Phi_K record without reading Xie 2026. "
        "Keep Ding-specific C_src(T) and mp-48 comparator roles separate."
    )
    full.setdefault("evidence_artifacts", [])
    append_unique(
        full["evidence_artifacts"],
        evidence(
            AUDIT_REL,
            {"status": audit["status"], "major_result_id": route["major_result_id"]},
        ),
    )
    append_unique(
        full["evidence_artifacts"],
        evidence(
            PACKAGE_REL,
            {"status": package["status"], "data_role": route["data_role"]},
        ),
    )
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    register["generated_at"] = today
    entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    entry = replace_recursive(entry, "ding_pbte_author_data_or_independent_reproduction_package_missing", NARROW_DING_BLOCKER)
    append_unique(
        entry["what_is_closed"],
        "independent mp-48 harmonic graphite heat-capacity comparator with provenance, volumetric conversion, and epistemic envelope",
    )
    entry["open_blockers"] = [
        item for item in entry["open_blockers"]
        if item != "ding_pbte_author_data_or_independent_reproduction_package_missing"
    ]
    append_unique(entry["open_blockers"], NARROW_DING_BLOCKER)
    entry.setdefault("data_role", {})["independent_heat_capacity_source"] = "CLOSED_FOR_LANE_COMPARATOR_NOT_CALIBRATION"
    append_unique(
        entry["evidence_artifacts"],
        {
            "path": AUDIT_REL,
            "sha256": digest(AUDIT_REL),
            "summary": {"status": audit["status"], "data_role": route["data_role"]},
        },
    )
    append_unique(
        entry["evidence_artifacts"],
        {
            "path": PACKAGE_REL,
            "sha256": digest(PACKAGE_REL),
            "summary": {"status": package["status"], "data_role": route["data_role"]},
        },
    )
    register["next_major_result"] = {
        "major_result_id": "T13_DIMENSIONAL_PHI_ENERGY_ANCHOR",
        "topic": "0.13_Thermodynamic_Bridge",
        "controlling_blocker": "base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing",
        "source_route": "mp-48 independent c_v comparator is available but is not a Phi calibration",
    }
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency["generated_at"] = today
    dependency["topic13_partial_evidence"] = {
        "major_result_id": "T13_FULL_THERMODYNAMIC_BRIDGE",
        "current_level": "PARTIAL",
        "independent_cv_route": "CLOSED_FOR_LANE",
        "full_core_unlock": False,
        "audit": evidence(
            AUDIT_REL,
            {"status": audit["status"], "claim_promotion": False},
        ),
        "reason": "A material c_v comparator does not supply e0, base Phi-to-energy correspondence, alpha_Phi_K, or full thermodynamic closure.",
    }
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    log_marker = "### 2026-08-11 - Independent mp-48 graphite heat-capacity route"
    log_path = ROOT / LOG_REL
    log = log_path.read_text(encoding="utf-8")
    if log_marker not in log:
        log += f"""

{log_marker}

- Scope: acquire and audit an independent numeric harmonic graphite route after the Ding 2022 official OA package was closed as a scoped no-go.
- Added or changed: the mp-48 source package, exact seven-member byte/hash manifest, experimental-volume conversion contract, JANAF comparison envelope, deterministic source audit, Full Topic 13 gate/register/dependency evidence, and this update-log entry.
- Verified with: `PASS_INDEPENDENT_NUMERIC_CV_WITH_EPISTEMIC_ENVELOPE`; all member hashes, mp-48 identity, 10 K grid, representative volumetric c_v rows, comparator residuals, and Xie 2026 non-access checks passed.
- Result closed: `T13_MP48_INDEPENDENT_GRAPHITE_CV_REPRODUCTION` is `CLOSED_FOR_LANE`; the independent c_v comparator route is now available without consuming calibration or holdout data.
- Blocker narrowed: the broad independent-package absence is removed; the remaining source blocker is `{NARROW_DING_BLOCKER}`, while the controlling Topic 13 blocker remains the dimensional Phi-energy anchor and independent alpha.
- Still open: Ding-specific mode-resolved C_src(T), convergence/uncertainty, e0, base Phi-to-Delta_u_ph, independent alpha_Phi_K, temperature-resolved volume, and EOS/transport/KMS/entropy closure.
- Claim impact: no promotion. Full Topic 13 remains `PARTIAL / BLOCKED`; the mp-48 route is comparator-only, not a TTG prediction or UET calibration.
- Next controller: derive or source-lock e0 and base Phi-to-Delta_u_ph independently of TTG residuals and Xie 2026.
"""
        log_path.write_text(log, encoding="utf-8")

    ledger_marker = "## Topic 13 Independent mp-48 Graphite Heat Capacity"
    ledger_path = ROOT / LEDGER_REL
    ledger = ledger_path.read_text(encoding="utf-8") if ledger_path.is_file() else "# 2026-08-11\n"
    if ledger_marker not in ledger:
        ledger += f"""

{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`, `raw-private`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` and linked `docs/core` artifacts
- changed: archived seven mp-48 source members, added the independent c_v package/audit, and synchronized the Topic 13 full gate, major-result register, dependency gate, and update log
- verification: `PASS_INDEPENDENT_NUMERIC_CV_WITH_EPISTEMIC_ENVELOPE`; source hashes, unit conversion, representative rows, comparator envelope, and holdout policy passed
- public-safety status: `partial`; source is provenance-traceable, but archive-level hash was not locally verified and Ding-specific C_src/e0/alpha remain open
- current claim boundary: `T13_MP48_INDEPENDENT_GRAPHITE_CV_REPRODUCTION` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL/BLOCKED`
- uncommitted: scoped Topic 13 source/audit/gate files remain uncommitted; unrelated Topic 0.22/0.25 changes were not edited
- next action: independently close the Phi-energy anchor and alpha route while keeping mp-48 as comparator-only evidence
"""
        ledger_path.write_text(ledger, encoding="utf-8")

    print(json.dumps({
        "status": "PASS_INTEGRATED_PARTIAL_T13",
        "major_result_id": route["major_result_id"],
        "closure_level": "CLOSED_FOR_LANE",
        "full_topic13_status": full["status"],
        "controlling_blocker": full["controlling_blocker"],
        "dependency_unlock": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
