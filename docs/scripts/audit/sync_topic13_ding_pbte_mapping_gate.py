"""Attach the Ding PBTE source mapping and route decision to the Topic 13 gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_ding_pbte_energy_temperature_mapping_audit.json"
PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "ding_2022_pbte_energy_temperature_source_package.json"
)
PDF = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "ding_2022_supplementary_information.pdf"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def append_once(values: list[str], item: str) -> None:
    if item not in values:
        values.append(item)


def main() -> int:
    gate = load(GATE)
    audit = load(AUDIT)
    result = audit["major_result"]
    audit_path = rel(AUDIT)
    branch = gate["verification_status"]["alpha_Phi_K"].setdefault(
        "named_energy_response_branch", {}
    )
    branch["pbte_energy_temperature_source"] = {
        "major_result_id": result["major_result_id"],
        "status": audit["status"],
        "closure_level": result["closure_level"],
        "equation_or_mapping": result["equation_or_mapping"],
        "audit": {"path": audit_path, "sha256": sha256(AUDIT)},
        "source_package": {"path": rel(PACKAGE), "sha256": sha256(PACKAGE)},
        "raw_pdf": {
            "path": rel(PDF),
            "sha256": sha256(PDF),
            "bytes": PDF.stat().st_size,
        },
        "numeric_C_src_status": "OPEN_NOT_PROVIDED",
        "base_Phi_identity": "not asserted",
        "xie_2026_accessed": False,
        "open_blockers": result["open_blockers"],
    }

    closed = gate["major_result"].setdefault("what_is_closed", [])
    append_once(
        closed,
        "Ding 2022 source-backed PBTE energy-density-to-temperature mapping and source-C versus UET-C ontology separation",
    )
    remains = gate["major_result"].setdefault("what_remains_open", [])
    for blocker in result["open_blockers"]:
        append_once(remains, blocker)
    append_once(remains, "uet_material_regime_mapping_to_ding_TTG_not_closed")

    evidence = gate.setdefault("evidence_artifacts", [])
    evidence[:] = [item for item in evidence if item.get("path") != audit_path]
    evidence.append(
        {
            "path": audit_path,
            "sha256": sha256(AUDIT),
            "summary": {
                "status": audit["status"],
                "closure_level": result["closure_level"],
                "numeric_C_src_status": "OPEN",
            },
        }
    )
    gate["data_role"]["ding_pbte_energy_temperature_mapping"] = (
        "DERIVED_STANDARD_PHYSICS_MAPPING; formula source-locked; numeric C_src and UET calibration open"
    )
    alpha = gate["verification_status"]["alpha_Phi_K"]
    alpha["controlling_blocker"] = (
        "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    )
    alpha["conditional_next_controller"] = audit["next_action"]
    alpha["source_acquisition_controller"] = (
        "ding_pbte_numeric_C_src_and_uet_energy_anchor_missing"
    )
    dim_map = gate["verification_status"]["dimensional_observable_map"]
    dim_map["standard_pbte_source_formula_status"] = "CLOSED_FOR_LANE"
    dim_map["standard_pbte_relation"] = "Delta_Tq = sum_mu(g_mu)/C_src"
    dim_map["physical_mapping_ready"] = False
    dim_map["controlling_blocker"] = (
        "base_Phi_to_Delta_u_ph_e0_and_numeric_C_src_missing"
    )
    gate["controlling_blocker"] = (
        "dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing"
    )
    gate["source_acquisition_controller"] = (
        "ding_pbte_numeric_C_src_and_uet_energy_anchor_missing"
    )
    gate["next_action"] = audit["next_action"]
    gate["claim_boundary"] = (
        "Full Topic 13 is not Core-ready. Ding closes the standard PBTE source formula lane, "
        "not numeric C_src(T), e0, base Phi correspondence, alpha_Phi_K, EOS/transport/KMS/entropy, "
        "external validation, or global UET closure."
    )
    gate["claim_promotion"] = False
    GATE.write_text(
        json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": gate["status"],
                "pbte_source_mapping": audit["status"],
                "controlling_blocker": gate["controlling_blocker"],
                "source_acquisition_controller": gate[
                    "source_acquisition_controller"
                ],
                "claim_promotion": gate["claim_promotion"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
