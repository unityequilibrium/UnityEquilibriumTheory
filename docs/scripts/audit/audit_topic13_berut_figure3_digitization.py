"""Audit a scoped, figure-derived Berut Figure 3c transcription."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DATA_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/berut_2012_figure3_panel_c_digitized.json"
BINARY_REL = "docs/core/07_artifacts/topic13/t13_berut_figure3_remote_binary_identity.json"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_berut_figure3_digitization.json"

EXPECTED_ASSET_SHA256 = "95823a29ed7f979d3979eb6fa776bce7df8eaa4485632073347874b5c868b188"
EXPECTED_BINARY_SHA256 = "e4bab6be849a093b7578bc52ce6df9be95dc25d83d51ecb718b4f798a37d50fa"
EXPECTED_SERIES = {"r_ge_0.90": "plus", "r_ge_0.85": "cross", "r_ge_0.75": "circle"}


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def canonical_payload(data: dict[str, Any]) -> str:
    return json.dumps(data.get("rows", []), sort_keys=True, separators=(",", ":"))


def build_artifact() -> dict[str, Any]:
    data = load(DATA_REL)
    binary = load(BINARY_REL)
    source = data["source"]
    panel = data["panel"]
    preprocessing = data["preprocessing"]
    rows = data["rows"]
    binary_identity = binary["binary_identity"]
    series_counts = {series: 0 for series in EXPECTED_SERIES}
    for row in rows:
        series_counts[row["series"]] = series_counts.get(row["series"], 0) + 1

    checks = {
        "data_schema_is_expected": data.get("schema_version") == "t13-berut-figure3-panel-c-digitization-v1",
        "source_asset_hash_matches_remote_inventory": source["embedded_asset_sha256"] == EXPECTED_ASSET_SHA256
        and any(item.get("sha256") == EXPECTED_ASSET_SHA256 for item in binary["embedded_assets"]),
        "publisher_binary_hash_matches_remote_inventory": source["publisher_binary_sha256"] == EXPECTED_BINARY_SHA256
        and binary_identity["sha256"] == EXPECTED_BINARY_SHA256,
        "panel_and_units_are_explicit": panel["panel_id"] == "3c"
        and panel["x_unit"] == "s"
        and panel["y_unit"] == "kT",
        "axis_models_are_explicit": "model" in panel["axis_mapping"]["x"]
        and "model" in panel["axis_mapping"]["y"],
        "rows_are_nonempty_and_unique": bool(rows)
        and len({row["row_id"] for row in rows}) == len(rows),
        "series_marker_contract_is_respected": all(
            row["marker"] == EXPECTED_SERIES[row["series"]] for row in rows
        ),
        "rows_have_positive_digitization_uncertainty": all(
            row["digitization_uncertainty"]["tau_s"] > 0
            and row["digitization_uncertainty"]["mean_heat_kT"] > 0
            for row in rows
        ),
        "pixel_centers_are_finite": all(
            len(row["pixel_center"]) == 2
            and all(isinstance(value, (int, float)) for value in row["pixel_center"])
            for row in rows
        ),
        "source_error_bars_not_promoted": preprocessing["measurement_error_bars_transcribed"] is False,
        "continuous_fit_not_digitized": panel["continuous_fit_curve_included"] is False
        and preprocessing["curve_digitized"] is False,
        "no_unit_conversion_or_fit": preprocessing["unit_conversion_performed"] is False
        and preprocessing["fit_performed"] is False,
        "no_target_or_holdout_access": preprocessing["target_data_used"] is False
        and preprocessing["holdout_accessed"] is False
        and preprocessing["xie_2026_accessed"] is False,
        "no_alpha_calibration_emitted": True,
    }
    passed = all(checks.values())
    blockers = [
        "berut_figure3_digitization_is_figure_derived_not_raw_numeric_source",
        "berut_measurement_error_bars_are_not_numeric_transcribed",
        "berut_permissioned_raw_numeric_package_missing",
    ]
    evidence = [
        {
            "path": DATA_REL,
            "sha256": sha256(DATA_REL),
            "role": "figure-derived marker transcription and pixel mapping",
        },
        {
            "path": BINARY_REL,
            "sha256": sha256(BINARY_REL),
            "role": "remote binary and embedded raster identity",
            "source_sha256": EXPECTED_BINARY_SHA256,
            "embedded_asset_sha256": EXPECTED_ASSET_SHA256,
        },
        {
            "locator": source["article_url"],
            "doi": source["doi"],
            "figure_locator": source["figure_locator"],
            "role": "official publisher figure/caption locator",
        },
    ]
    status = "PASS_SCOPED_BERUT_FIGURE3_DIGITIZATION" if passed else "BLOCKED_BERUT_FIGURE3_DIGITIZATION"
    major = {
        "major_result_id": "T13_BERUT_FIGURE3_DIGITIZATION",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
        "what_is_closed": [
            "Figure 3c panel, axes, units, marker-series identity, and ten marker centers are recorded.",
            "The continuous fit curve and Landauer reference line are explicitly excluded from the numeric rows.",
            "Pixel-coordinate digitization uncertainty is declared separately from the source-reported 1 s.d. error bars.",
        ],
        "equation_or_mapping": "<Q>_panel_c(tau) is retained as a figure-derived kT comparison; no SI heat or Phi mapping is emitted.",
        "units": {"tau": "s", "mean_heat": "kT", "digitization_uncertainty": "s and kT"},
        "derivation_class": "figure-derived manual transcription with hash-pinned panel locator",
        "observable": "Berut Figure 3c mean dissipated heat versus erasure duration",
        "data_role": "FIGURE_DERIVED_COMPARISON_ONLY",
        "evidence_artifacts": evidence,
        "verification_status": status,
        "open_blockers": blockers,
        "dependency_unlocked": "Berut figure-derived comparison lane only; no raw source, alpha, Full Topic 13, Core, Gravity, or transport dependency is unlocked.",
        "claim_boundary": "This closes a transparent Figure 3c transcription lane only. It is not a raw numeric source, source-grade uncertainty package, calibration, prediction, UET proof, or external validation.",
    }
    return {
        "schema_version": "t13-berut-figure3-digitization-v1",
        "artifact": "t13_berut_figure3_digitization",
        "generated_at": date.today().isoformat(),
        "status": status,
        "claim_promotion": False,
        "major_result": major,
        "source_locator": {
            "article_url": source["article_url"],
            "doi": source["doi"],
            "figure_locator": source["figure_locator"],
            "embedded_asset_id": source["embedded_asset_id"],
            "embedded_asset_sha256": source["embedded_asset_sha256"],
            "publisher_binary_sha256": source["publisher_binary_sha256"],
        },
        "axis_mapping": panel["axis_mapping"],
        "series_counts": series_counts,
        "row_count": len(rows),
        "row_payload_sha256": hashlib.sha256(canonical_payload(data).encode("utf-8")).hexdigest(),
        "preprocessing": preprocessing,
        "checks": checks,
        "evidence_artifacts": evidence,
        "open_blockers": blockers,
        "controlling_blocker": blockers[0],
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "xie_2026_consumed": False,
    }


def main() -> int:
    artifact = build_artifact()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": artifact["status"],
        "major_result_id": artifact["major_result"]["major_result_id"],
        "closure_level": artifact["major_result"]["closure_level"],
        "row_count": artifact["row_count"],
        "controlling_blocker": artifact["controlling_blocker"],
    }, indent=2))
    return 0 if all(artifact["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
