"""Audit the permitted Ding 2022 figure-derived numeric intake."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
PACKAGE = TOPIC / "Data/03_Research/matter_space_second_sound_source_package.json"
MANIFEST = TOPIC / "Data/03_Research/ding_2022_fig1d_digitized_manifest.json"
CSV_PATH = TOPIC / "Data/03_Research/ding_2022_fig1d_digitized.csv"
FIGURE = TOPIC / "Data/03_Research/raw/ding_2022_fig1.png"
MAPPING = ROOT / "docs/core/07_artifacts/archive/ding_2022_fig1d_series_mapping.json"
HOLDOUT_AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_xie_2026_holdout_access_audit.json"
OUT = ROOT / "docs/core/07_artifacts/provenance/ding_2022_source_mapping_audit.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _dip_times(rows: list[dict[str, str]]) -> dict[str, float]:
    grouped: dict[str, list[tuple[float, float]]] = {}
    for row in rows:
        grouped.setdefault(row["series_id"], []).append(
            (float(row["normalized_signal"]), float(row["time_ps"]))
        )
    return {
        series: float(min(values, key=lambda item: item[0])[1])
        for series, values in grouped.items()
    }


def _permutation_diagnostic(dip_times: dict[str, float]) -> dict[str, Any]:
    colors = sorted(dip_times)
    periods = (2.0, 3.0, 4.0)
    candidates = []
    monotonic = []
    for assignment in itertools.permutations(periods):
        color_to_period = dict(zip(colors, assignment))
        speed_by_period = {
            period: color_to_period[color] * 1000.0 / (2.0 * dip_times[color])
            for color in colors
            for period in (color_to_period[color],)
        }
        record = {
            "color_to_period_um": color_to_period,
            "estimated_speed_km_per_s": speed_by_period,
            "uses_published_monotonicity_probe_only": True,
        }
        candidates.append(record)
        if (
            speed_by_period[2.0] > speed_by_period[3.0]
            and speed_by_period[3.0] > speed_by_period[4.0]
        ):
            monotonic.append(record)
    return {
        "dip_time_ps_by_series": dip_times,
        "published_periods_um": list(periods),
        "candidate_assignment_count": len(candidates),
        "monotonic_assignment_count": len(monotonic),
        "diagnostic_use": (
            "not used to assign colors; the direct printed-legend mapping artifact is "
            "the controlling source record"
        ),
        "candidates": candidates,
    }


def build_report() -> dict[str, Any]:
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    mapping = json.loads(MAPPING.read_text(encoding="utf-8-sig"))
    holdout_audit = json.loads(HOLDOUT_AUDIT.read_text(encoding="utf-8-sig"))
    holdout_controls = holdout_audit.get("audit", {})
    rows = _load_rows()
    target = next(
        source
        for source in package["sources"]
        if source.get("source_id") == "ding_2022_fig1d_digitized"
    )
    fields = set(rows[0]) if rows else set()
    mapping_ref = manifest.get("series_mapping", {})
    expected_mapping = {"blue_trace": 2.0, "red_trace": 3.0, "green_trace": 4.0}
    checks = {
        "numeric_file_present": CSV_PATH.is_file(),
        "figure_asset_present": FIGURE.is_file(),
        "mapping_artifact_present": MAPPING.is_file(),
        "figure_hash_matches_manifest": FIGURE.is_file()
        and sha256(FIGURE) == manifest["input_assets"][0]["sha256"],
        "numeric_hash_matches_manifest": CSV_PATH.is_file()
        and sha256(CSV_PATH) == manifest["output_sha256"],
        "mapping_hash_matches_manifest": MAPPING.is_file()
        and sha256(MAPPING) == mapping_ref.get("mapping_sha256"),
        "mapping_artifact_pass": mapping.get("status") == "PASS",
        "mapping_values_match_manifest": mapping.get("series_to_grating_period_um")
        == manifest.get("series_mapping", {}).get("series_to_grating_period_um")
        == expected_mapping,
        "row_identity_complete": {
            "source_id",
            "series_id",
            "row_id",
            "pixel_x",
        }.issubset(fields),
        "units_declared": {"time_ps", "normalized_signal"}.issubset(fields),
        "uncertainty_declared": "extraction_uncertainty" in fields,
        "preprocessing_declared": bool(manifest.get("preprocessing")),
        "license_declared": "CC BY 4.0" in target.get("license_or_terms", ""),
        "raw_author_numeric_source_present": target.get("upstream_data_availability")
        == "author_numeric_data_captured",
        "permitted_figure_numeric_route_ready": all(
            [
                "CC BY 4.0" in target.get("license_or_terms", ""),
                manifest.get("series_mapping_status")
                == "CLOSED_COLOR_TO_GRATING_PERIOD",
                mapping.get("status") == "PASS",
            ]
        ),
        "color_to_period_mapping_closed": manifest.get("series_mapping_status")
        == "CLOSED_COLOR_TO_GRATING_PERIOD",
        # Compatibility field: the canonical distinction between metadata
        # observation and source-data consumption lives in the holdout audit.
        "holdout_not_accessed": holdout_controls.get("numeric_payload_consumed") is False,
        "holdout_metadata_only_observed": holdout_controls.get("metadata_only_observed") is True,
        "holdout_source_data_consumed": holdout_controls.get("source_data_payload_observed") is True,
        "holdout_source_data_unconsumed": holdout_controls.get("source_data_payload_observed") is False,
        "holdout_audit_pass": holdout_audit.get("status") == "PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY",
        "numeric_fitting_disabled": package["usage_policy"]["numeric_fitting_allowed"] is False,
    }
    required_checks = [
        key
        for key in checks
        if key
        not in {
            "raw_author_numeric_source_present",
            "holdout_source_data_consumed",
        }
    ]
    status = "PASS" if all(checks[key] for key in required_checks) else "BLOCKED"
    # The figure route is valid for normalized comparison only. It is not the
    # raw PBTE/C_src package required by the full Topic 13 source gate.
    source_ready = checks["raw_author_numeric_source_present"]
    dip_diagnostic = _permutation_diagnostic(_dip_times(rows))
    return {
        "schema_version": "ding-2022-source-mapping-audit-v2",
        "artifact": "ding_2022_source_mapping_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "source_id": "ding_2022_fig1d_digitized",
        "source_locator": "Nature Communications 13, 285 (2022), Fig. 1d",
        "source_route_ready_for_full_closure": source_ready,
        "normalized_comparison_route_ready": checks[
            "permitted_figure_numeric_route_ready"
        ],
        "source_policy": {
            "permitted_figure_asset": "CC BY 4.0 article figure asset",
            "raw_author_data_status": (
                "not captured; publisher article states supporting data are "
                "available on reasonable request"
            ),
            "figure_digitization_role": "permitted training/comparison candidate for normalized shape only",
            "calibration_role": "prohibited until independent alpha_Phi_K is closed",
            "mapping_source": "printed Fig. 1d legend, not dip-order inference",
        },
        "checks": checks,
        "observed_package": {
            "row_count": len(rows),
            "series_ids": sorted({row["series_id"] for row in rows}),
            "manifest_series_mapping_status": manifest.get("series_mapping_status"),
            "mapping_artifact_sha256": sha256(MAPPING) if MAPPING.is_file() else None,
            "figure_sha256": sha256(FIGURE) if FIGURE.is_file() else None,
            "numeric_sha256": sha256(CSV_PATH) if CSV_PATH.is_file() else None,
        },
        "mapping_diagnostic": dip_diagnostic,
        "evidence_inputs": {
            "package": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json",
            "manifest": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_fig1d_digitized_manifest.json",
            "mapping_artifact": "docs/core/07_artifacts/archive/ding_2022_fig1d_series_mapping.json",
            "numeric_file": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_fig1d_digitized.csv",
            "figure_asset": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_fig1.png",
            "published_pdf": "https://www.nature.com/articles/s41467-021-27907-z.pdf",
        },
        "controlling_blocker": (
            "ding_2022_figure_series_mapping_unresolved_or_raw_source_permission_missing"
            if status != "PASS"
            else None
        ),
        "claim_boundary": (
            "The figure-derived rows have a permitted CC BY route and a closed printed-legend "
            "series mapping, but are not raw author data. No external validation or alpha_Phi_K "
            "calibration is promoted."
        ),
        "next_controller": (
            "derive or independently calibrate alpha_Phi_K using training/calibration data only; "
            "do not read or tune on Xie 2026"
            if status == "PASS"
            else "capture a permitted numeric route or close the explicit printed-legend mapping"
        ),
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "controlling_blocker": report["controlling_blocker"],
        "source_route_ready_for_full_closure": report["source_route_ready_for_full_closure"],
        "checks": report["checks"],
        "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
