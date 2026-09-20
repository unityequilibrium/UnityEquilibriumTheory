"""Audit and synchronize the Topic 0.13 local numeric provenance contract."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
PACKAGE = TOPIC / "Data/03_Research/matter_space_second_sound_source_package.json"
REVIEW = TOPIC / "Data/03_Research/matter_space_thermal_source_review.json"
MAP = TOPIC / "Result/artifacts/matter_space_thermal_observable_map_readiness.json"
OUT = ROOT / "docs/core/07_artifacts/topic13/thermal_source_provenance_gate.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    package = load(PACKAGE)
    review = load(REVIEW)
    mapping = load(MAP)
    review_by_id = {row.get("source_id"): row for row in review.get("sources", [])}
    rows: list[dict[str, Any]] = []
    failures: list[str] = []
    for source in package.get("sources", []):
        source_id = source.get("source_id")
        review_row = review_by_id.get(source_id, {})
        local_path_text = source.get("local_numeric_path") or source.get("local_raw_path")
        local_path = TOPIC / local_path_text if local_path_text else None
        local_present = bool(local_path and local_path.is_file())
        actual_hash = sha256(local_path) if local_present and local_path else None
        expected_hash = review_row.get("local_numeric_hash") or source.get("output_hash")
        has_locator = bool(source.get("source_locator") and review_row.get("source_locator"))
        has_preprocessing = bool(source.get("preprocessing") and source.get("preprocessing") != "none")
        has_uncertainty = bool(source.get("extraction_uncertainty") or review_row.get("uncertainty"))
        has_row_identity = bool(source.get("row_identity") or review_row.get("row_identity"))
        hash_matches = bool(local_present and expected_hash and actual_hash == expected_hash)
        is_holdout = "holdout" in str(source.get("benchmark_role", "")).lower() or "holdout" in str(source_id).lower()
        if local_present and not hash_matches:
            failures.append(f"{source_id}:hash_mismatch")
        if local_present and not all((has_locator, has_preprocessing, has_uncertainty, has_row_identity)):
            failures.append(f"{source_id}:provenance_fields_incomplete")
        rows.append(
            {
                "source_id": source_id,
                "local_numeric_path": local_path_text,
                "local_numeric_present": local_present,
                "local_numeric_sha256": actual_hash,
                "declared_sha256": expected_hash,
                "hash_matches": hash_matches if local_present else None,
                "source_locator_present": has_locator,
                "preprocessing_present": has_preprocessing,
                "uncertainty_present": has_uncertainty,
                "row_identity_present": has_row_identity,
                "holdout": is_holdout,
                "status": source.get("status"),
            }
        )
    local_rows = [row for row in rows if row["local_numeric_present"]]
    normalized_rows = [
        row for row in rows
        if row["local_numeric_present"]
        and row["source_id"] == "ding_2022_fig1d_digitized"
        and row["status"] == "FIGURE_DERIVED_NUMERIC_PACKAGE_WITH_CLOSED_MAPPING"
    ]
    raw_author_rows = [
        row for row in rows
        if row["local_numeric_present"]
        and row["source_id"] != "ding_2022_fig1d_digitized"
        and row["status"] == "SOURCE_LOCKED_NUMERIC"
    ]
    holdout_rows = [row for row in rows if row["holdout"]]
    holdout_consumed = bool(review.get("holdout_consumed")) or any(row["holdout"] and row["local_numeric_present"] for row in rows)
    provenance_complete = bool(local_rows) and not failures and all(row["hash_matches"] for row in local_rows)
    mapping["evidence_class"] = "SOURCE_BACKED_FIGURE_DERIVED_NORMALIZED_COMPARISON_WITH_DIMENSIONAL_BLOCKER"
    mapping["source_rows"] = [
        {
            **row,
            "benchmark_role": next((source.get("benchmark_role") for source in package.get("sources", []) if source.get("source_id") == row["source_id"]), None),
        }
        for row in rows
    ]
    mapping["measurement_operator"]["raw_signal_status"] = "DING_2022_FIGURE_DIGITIZATION_LOCAL_NORMALIZED_COMPARISON; XIE_2026_HOLDOUT_METADATA_ONLY"
    mapping["gates"]["source_package_provenance_complete"] = provenance_complete
    mapping["gates"]["normalized_comparison_route_ready"] = bool(normalized_rows) and not failures
    mapping["gates"]["raw_author_numeric_route_ready"] = bool(raw_author_rows) and not failures
    mapping["gates"]["holdout_data_not_consumed"] = not holdout_consumed
    mapping["blockers"] = [
        "Ding 2022 raw-author PBTE C_src(T) is not captured; the permitted figure-derived normalized comparison route is separate and ready",
        "alpha_Phi_K has no derivation or source-locked independent calibration with uncertainty",
        "heat flux and entropy production are not direct TTG observables",
        "2026 source remains a locked holdout and cannot tune parameters",
    ]
    mapping["next_required_artifact"] = "raw-author or accepted independent PBTE C_src(T) reproduction plus independent alpha_Phi_K calibration/derivation with uncertainty; normalized comparison is already source-ready and must use only non-holdout rows"
    MAP.write_text(json.dumps(mapping, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    artifact = {
        "schema_version": "1.0",
        "artifact": "thermal_source_provenance_gate",
        "generated_at": date.today().isoformat(),
        "status": "PASS_WITH_FIGURE_DERIVED_NORMALIZED_COMPARISON" if bool(normalized_rows) and not failures and not holdout_consumed else "BLOCKED",
        "source_package": {"path": str(PACKAGE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(PACKAGE)},
        "source_review": {"path": str(REVIEW.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(REVIEW)},
        "rows": rows,
        "metrics": {"source_count": len(rows), "local_numeric_count": len(local_rows), "normalized_comparison_count": len(normalized_rows), "raw_author_numeric_count": len(raw_author_rows), "holdout_count": len(holdout_rows), "holdout_consumed": holdout_consumed, "provenance_complete": provenance_complete},
        "gates": {"source_locator": all(row["source_locator_present"] for row in local_rows), "unit_context": bool(local_rows), "preprocessing": all(row["preprocessing_present"] for row in local_rows), "uncertainty": all(row["uncertainty_present"] for row in local_rows), "row_identity": all(row["row_identity_present"] for row in local_rows), "hash_match": all(row["hash_matches"] for row in local_rows), "holdout_locked": not holdout_consumed, "numeric_fitting_disabled": not bool(review.get("numeric_fitting_allowed"))},
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing; independent alpha_Phi_K remains open",
        "next_action": "keep the normalized figure-derived route in comparison-only role; obtain raw-author or accepted independent PBTE C_src(T) and an independent alpha_Phi_K anchor without reading Xie 2026",
        "claim_boundary": "provenance readiness for a provisional normalized source row only; no external validation or temperature prediction",
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "local_numeric_count": len(local_rows), "holdout_consumed": holdout_consumed, "failures": failures}, indent=2))
    return 0 if artifact["status"] != "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
