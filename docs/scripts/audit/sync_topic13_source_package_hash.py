"""Refresh Wave 1 provenance links after a Topic 13 source-package change."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "docs/core/07_artifacts/archive/uet_research_room_wave1_contract.json"
PACKAGE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    package_path = PACKAGE.relative_to(ROOT).as_posix()
    topic = contract["rooms"]["topic_0_13"]
    topic["data_role"] = (
        "permitted Ding 2022 CC BY figure-derived normalized-shape source; "
        "raw author numeric route remains optional; Xie 2026 locked holdout"
    )
    topic["verification_status"] = "SOURCE_ROUTE_PASS_ALPHA_OPEN"
    topic["controlling_blocker"] = "alpha_Phi_K_independent_calibration_missing"
    topic["claim_boundary"] = (
        "permitted figure-derived source route and normalized internal controls; "
        "not raw author data, temperature prediction, external validation, or global closure"
    )
    topic["next_action"] = (
        "derive or independently calibrate alpha_Phi_K with uncertainty using "
        "training/calibration data only; do not read or tune on Xie 2026"
    )
    for evidence in topic.get("evidence", []):
        if evidence.get("path") == package_path:
            evidence["sha256"] = sha256(PACKAGE)
            evidence["summary"] = {
                "status": package.get("status"),
                "numeric_source_route_status": package.get("source_access_audit", {}).get(
                    "numeric_source_route_status"
                ),
                "raw_author_numeric_source": False,
                "figure_mapping_closed": True,
            }
    blockers = contract.get("integration_blockers", [])
    contract["integration_blockers"] = [
        (
            "full original conserved-C candidate remains blocked; named coupled C/Phi lane "
            "passes the locked normalized causal checks"
            if item == "core full coupled pre-arrival leakage remains above the locked 1e-6 threshold"
            else item
        )
        for item in blockers
        if item != "TTG source rows are provisional digitized intake, not raw author data"
    ]
    contract["integration_blockers"].append(
        "alpha_Phi_K has no independent derivation or calibration with uncertainty"
    ) if "alpha_Phi_K has no independent derivation or calibration with uncertainty" not in contract["integration_blockers"] else None
    contract["generated_at"] = date.today().isoformat()
    CONTRACT.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact": str(CONTRACT.relative_to(ROOT)).replace("\\", "/"),
        "package_sha256": sha256(PACKAGE),
        "topic13_controller": topic["controlling_blocker"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
