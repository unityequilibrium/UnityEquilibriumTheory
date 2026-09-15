"""Repair Topic 13 partial evidence after a dependency-gate rebuild.

The downstream unlock verifier owns dependency decisions, but it must not
discard the Topic 13 evidence ledger that links lane-level results to the
blocked full result. This repair also normalizes legacy summary fields while
preserving the more specific controller in a detail field.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
UNLOCK_SCRIPT_REL = "docs/scripts/audit/audit_major_result_dependency_unlock.py"

ROUTES = (
    ("phi_energy_anchor_no_go", "docs/core/07_artifacts/topic13/t13_phi_energy_anchor_identifiability_no_go.json", "PASS_SCOPED_NO_GO_NORMALIZED_PHI_ENERGY_ANCHOR"),
    ("covariant_action_si_anchor_route", "docs/core/07_artifacts/topic13/t13_covariant_action_si_anchor_route_audit.json", "PASS_NATURAL_UNIT_ROUTE_IDENTIFIED_SI_MAPPING_BLOCKED"),
    ("covariant_field_normalization_no_go", "docs/core/07_artifacts/topic13/t13_covariant_field_normalization_identifiability_no_go.json", "PASS_SCOPED_NO_GO_COVARIANT_FIELD_NORMALIZATION"),
    ("causal_branch_selection", "docs/core/07_artifacts/topic13/t13_causal_branch_selection_audit.json", "PASS_CLOSED_AS_NO_GO_WITH_NAMED_COUPLED_BRANCH"),
    ("beta_symbol_separation_noncircularity_no_go", "docs/core/07_artifacts/topic13/t13_beta_symbol_separation_noncircularity_audit.json", "PASS_SCOPED_NO_GO_BETA_SYMBOL_IDENTIFICATION"),
    ("thermal_response_beta_contract", "docs/core/07_artifacts/topic13/t13_thermal_response_beta_contract_audit.json", "PASS_NAMED_FINITE_TEMPERATURE_BETA_CONTRACT"),
    ("collective_response_eos_stability_contract", "docs/core/07_artifacts/topic13/t13_collective_response_eos_stability_audit.json", "PASS_NAMED_COLLECTIVE_RESPONSE_EOS_STABILITY_CONTRACT"),
    ("phi_e_reference_normalization", "docs/core/07_artifacts/topic13/t13_phi_e_reference_normalization_audit.json", "PASS_NAMED_PHI_E_REFERENCE_NORMALIZATION"),
    ("base_phi_independent_calibration_requirement", "docs/core/07_artifacts/topic13/t13_base_phi_independent_calibration_requirement.json", "PASS_OPEN_CALIBRATION_REQUIREMENT"),
)


def load(rel: str) -> dict[str, Any]:
    value = json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def evidence(rel: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": rel, "sha256": digest(rel), "summary": summary}


def repair_dependency() -> None:
    dependency = load(DEPENDENCY_REL)
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial.setdefault("major_result_id", "T13_FULL_THERMODYNAMIC_BRIDGE")
    partial.setdefault("current_level", "PARTIAL")
    partial.setdefault("independent_cv_route", "CLOSED_FOR_LANE")
    partial["full_core_unlock"] = False
    partial.setdefault(
        "reason",
        "Lane-level results are linked for auditability but do not supply a base-Phi SI anchor, alpha_Phi_K, or full thermodynamic closure.",
    )
    for key, rel, status in ROUTES:
        summary: dict[str, Any] = {"status": status, "full_core_unlock": False}
        if key == "causal_branch_selection":
            summary["baseline_replaced"] = False
        partial[key] = evidence(rel, summary)
    partial["base_phi_calibration_controller"] = "independent_paired_base_Phi_amplitude_and_SI_observable_record_missing"
    partial["register_sha256"] = digest(REGISTER_REL)
    dependency["generated_at"] = date.today().isoformat()
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def repair_register_and_full_controller() -> None:
    full = load(FULL_REL)
    full["source_acquisition_controller"] = "ding_pbte_author_data_or_independent_reproduction_package_missing"
    full["source_acquisition_controller_detail"] = (
        "Ding-specific C_src(T), mode-resolved c_mu, uncertainty/convergence, and the Phi energy anchor remain open; "
        "the independent mp-48 c_v route is comparator-only and closed for lane."
    )
    (ROOT / FULL_REL).write_text(json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    register = load(REGISTER_REL)
    next_value = register.get("next_major_result")
    if isinstance(next_value, dict):
        register["next_major_result_detail"] = next_value
    register["next_major_result"] = "T13_FULL_THERMODYNAMIC_BRIDGE"
    full_entry = next(item for item in register["entries"] if item.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE")
    for item in full_entry.get("evidence_artifacts", []):
        if item.get("path") == FULL_REL:
            item["sha256"] = digest(FULL_REL)
    register["generated_at"] = date.today().isoformat()
    (ROOT / REGISTER_REL).write_text(json.dumps(register, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    dependency = load(DEPENDENCY_REL)
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    dependency.setdefault("topic13_partial_evidence", {})["register_sha256"] = digest(REGISTER_REL)
    (ROOT / DEPENDENCY_REL).write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def patch_unlock_verifier() -> bool:
    path = ROOT / UNLOCK_SCRIPT_REL
    text = path.read_text(encoding="utf-8-sig")
    if "Preserve lane-level Topic 13 evidence" in text:
        return False
    needle = '    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\\n", encoding="utf-8")\n'
    insertion = (
        '    # Preserve lane-level Topic 13 evidence when this downstream-only verifier reruns.\n'
        '    previous = json.loads(OUT.read_text(encoding="utf-8-sig")) if OUT.is_file() else {}\n'
        '    if "topic13_partial_evidence" in previous:\n'
        '        artifact["topic13_partial_evidence"] = previous["topic13_partial_evidence"]\n'
        '    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\\n", encoding="utf-8")\n'
    )
    if needle not in text:
        raise SystemExit("dependency unlock write point not found")
    path.write_text(text.replace(needle, insertion, 1), encoding="utf-8")
    return True


def main() -> int:
    patched = patch_unlock_verifier()
    repair_register_and_full_controller()
    repair_dependency()
    print(json.dumps({
        "status": "PASS_REPAIRED_TOPIC13_DEPENDENCY_METADATA",
        "unlock_verifier_patched": patched,
        "partial_routes": len(ROUTES),
        "full_core_unlock": False,
        "source_acquisition_controller": "ding_pbte_author_data_or_independent_reproduction_package_missing",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
