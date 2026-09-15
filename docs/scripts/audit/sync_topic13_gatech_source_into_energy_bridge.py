"""Attach the source-locked c_p anchor to the named energy-response audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ENERGY = ROOT / "docs/core/07_artifacts/topic13/t13_energy_response_bridge_audit.json"
SOURCE_AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_gatech_graphite_source_audit.json"
SOURCE_PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "gatech_gen3csp_graphite_source_package.json"
)
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/gen3csp_graphite.xlsx"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_once(values: list[str], item: str) -> None:
    if item not in values:
        values.append(item)


def main() -> int:
    energy = json.loads(ENERGY.read_text(encoding="utf-8-sig"))
    source = json.loads(SOURCE_AUDIT.read_text(encoding="utf-8-sig"))
    source_path = rel(SOURCE_AUDIT)
    package_path = rel(SOURCE_PACKAGE)
    raw_path = rel(RAW)
    source_digest = sha256(SOURCE_AUDIT)
    package_digest = sha256(SOURCE_PACKAGE)
    raw_digest = sha256(RAW)

    energy["source_anchor"] = {
        "status": source["status"],
        "major_result_id": source["major_result"]["major_result_id"],
        "source_audit": {"path": source_path, "sha256": source_digest},
        "source_package": {"path": package_path, "sha256": package_digest},
        "raw_workbook": {"path": raw_path, "sha256": raw_digest},
        "temperature_K": source["row_identity"]["temperature_K"],
        "cp_mass_specific_J_per_g_K": source["reported_values"]["average_specific_heat_J_per_g_K"],
        "uncertainty_95pct_J_per_g_K": source["reported_values"]["uncertainty_95pct_J_per_g_K"],
        "c_v_status": "OPEN",
        "consumed_for_calibration": False,
    }
    major_result = energy.setdefault("major_result", {})
    what_is_closed = major_result.get("what_is_closed", [])
    if isinstance(what_is_closed, str):
        what_is_closed = [what_is_closed]
    append_once(what_is_closed, "independent Georgia Tech c_p row and 95% confidence source anchor")
    major_result["what_is_closed"] = what_is_closed
    open_blockers = major_result.setdefault("open_blockers", [])
    for blocker in source["major_result"]["open_blockers"]:
        append_once(open_blockers, blocker)
    evidence = major_result.setdefault("evidence_artifacts", [])
    evidence[:] = [
        item for item in evidence if item.get("path") not in {source_path, package_path, raw_path}
    ]
    evidence.extend(
        [
            {"path": source_path, "sha256": source_digest, "summary": {"status": source["status"]}},
            {"path": package_path, "sha256": package_digest, "summary": {"status": "RAW_ARCHIVED_CP_95CI_CV_OPEN"}},
            {"path": raw_path, "sha256": raw_digest, "summary": {"bytes": RAW.stat().st_size}},
        ]
    )
    energy["source_package"]["independent_c_p_anchor"] = {
        "path": source_path,
        "sha256": source_digest,
        "status": source["status"],
    }
    energy["next_controller"] = (
        "source-lock volumetric c_v or close Cp-to-cv plus density uncertainty; "
        "independently derive or calibrate e0 and prove base Phi-to-Phi_E without TTG target residuals or Xie 2026"
    )
    ENERGY.write_text(json.dumps(energy, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"energy_audit": rel(ENERGY), "source_status": source["status"], "source_sha256": source_digest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
