"""Attach the Ding PBTE source formula to the named Topic 13 energy branch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ENERGY = ROOT / "docs/core/07_artifacts/topic13/t13_energy_response_bridge_audit.json"
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
    energy = load(ENERGY)
    audit = load(AUDIT)
    result = audit["major_result"]
    audit_ref = {"path": rel(AUDIT), "sha256": sha256(AUDIT)}
    package_ref = {"path": rel(PACKAGE), "sha256": sha256(PACKAGE)}
    pdf_ref = {
        "path": rel(PDF),
        "sha256": sha256(PDF),
        "bytes": PDF.stat().st_size,
    }
    energy["standard_pbte_source_anchor"] = {
        "major_result_id": result["major_result_id"],
        "status": audit["status"],
        "closure_level": result["closure_level"],
        "equation_or_mapping": result["equation_or_mapping"],
        "audit": audit_ref,
        "source_package": package_ref,
        "raw_pdf": pdf_ref,
        "numeric_C_src_status": "OPEN_NOT_PROVIDED",
        "base_Phi_identity": "not asserted",
        "xie_2026_accessed": False,
    }

    closed = energy["major_result"].setdefault("what_is_closed", [])
    if isinstance(closed, str):
        closed = [closed]
        energy["major_result"]["what_is_closed"] = closed
    append_once(
        closed,
        "Ding 2022 source-backed PBTE mapping Delta_Tq = sum_mu(g_mu)/C_src with explicit source-C versus UET-C separation",
    )
    evidence = energy["major_result"].setdefault("evidence_artifacts", [])
    evidence[:] = [item for item in evidence if item.get("path") != rel(AUDIT)]
    evidence.extend([audit_ref, package_ref, pdf_ref])
    blockers = energy["major_result"].setdefault("open_blockers", [])
    for blocker in result["open_blockers"]:
        append_once(blockers, blocker)
    energy["major_result"]["data_role"] = (
        "source-backed standard PBTE formula plus named-branch algebra; no numeric C_src, "
        "e0, base-Phi calibration, target residual, or holdout data consumed"
    )
    energy["conditional_inputs"]["c_v"] = {
        "status": "OPEN_NUMERIC_DING_C_SRC_AND_THERMODYNAMIC_REGIME",
        "units": "J m^-3 K^-1",
        "source_formula_status": "CLOSED_FOR_LANE",
    }
    energy["controlling_blocker"] = (
        "numeric_C_src_e0_and_base_Phi_to_Delta_u_ph_inputs_not_source_locked"
    )
    energy["next_controller"] = audit["next_action"]
    energy["claim_boundary"] = (
        "The Ding PBTE source formula and named energy-response algebra are closed for their "
        "lanes only. Numeric C_src(T), e0, base Phi correspondence, Full Topic 13, and external "
        "validation remain open."
    )
    ENERGY.write_text(
        json.dumps(energy, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "artifact": rel(ENERGY),
                "source_anchor": audit["status"],
                "controlling_blocker": energy["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
