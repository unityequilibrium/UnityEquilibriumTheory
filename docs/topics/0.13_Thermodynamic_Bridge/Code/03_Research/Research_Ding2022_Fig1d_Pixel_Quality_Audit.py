"""Audit row-level localization in the existing Ding Fig. 1d digitization."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[5]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
SOURCE = TOPIC / "Code/03_Research/Research_Ding2022_Figure_Digitization.py"
PNG = TOPIC / "Data/03_Research/raw/ding_2022_fig1.png"
CSV_PATH = TOPIC / "Data/03_Research/ding_2022_fig1d_digitized.csv"
MANIFEST = TOPIC / "Data/03_Research/ding_2022_fig1d_digitized_manifest.json"
OUTPUT = TOPIC / "Result/artifacts/ding_2022_fig1d_pixel_quality_audit.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_source_digitizer() -> Any:
    spec = importlib.util.spec_from_file_location("ding_figure_digitizer", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load digitizer: {SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contiguous_clusters(values: list[int]) -> list[dict[str, int]]:
    clusters: list[list[int]] = []
    for value in sorted(values):
        if not clusters or value > clusters[-1][-1] + 1:
            clusters.append([value])
        else:
            clusters[-1].append(value)
    return [
        {"y_min": group[0], "y_max": group[-1], "pixel_count": len(group)}
        for group in clusters
    ]


def _compress_ranges(values: list[int]) -> list[list[int]]:
    if not values:
        return []
    ordered = sorted(set(values))
    ranges: list[list[int]] = []
    start = previous = ordered[0]
    for value in ordered[1:]:
        if value > previous + 1:
            ranges.append([start, previous])
            start = value
        previous = value
    ranges.append([start, previous])
    return ranges


def _read_csv() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _column_audit(rgb: np.ndarray, digitizer: Any, series_id: str, bounds: dict[str, int]) -> dict[str, Any]:
    mask = digitizer.colour_mask(rgb, series_id)
    x0, x1 = bounds["left"] + 12, bounds["right"] - 10
    y0, y1 = bounds["top"] + 8, bounds["bottom"] - 10
    ambiguous: list[dict[str, Any]] = []
    multi_component_x: list[int] = []

    for pixel_x in range(x0, x1 + 1):
        ys = (np.flatnonzero(mask[y0 : y1 + 1, pixel_x]) + y0).tolist()
        if not ys:
            continue
        clusters = contiguous_clusters([int(y) for y in ys])
        if len(clusters) < 2:
            continue
        multi_component_x.append(pixel_x)
        median_y = float(np.median(ys))
        containing = [
            cluster
            for cluster in clusters
            if cluster["y_min"] <= median_y <= cluster["y_max"]
        ]
        median_count = containing[0]["pixel_count"] if containing else 0
        dominant_count = max(cluster["pixel_count"] for cluster in clusters)
        dominant_separation = max(
            abs(median_y - (cluster["y_min"] + cluster["y_max"]) / 2)
            for cluster in clusters
            if cluster["pixel_count"] == dominant_count
        )
        # Flag medians that fall between components or select a smaller
        # component far from the dominant pixel cluster.
        if median_count == 0 or (
            median_count < dominant_count and dominant_separation >= 10
        ):
            ambiguous.append(
                {
                    "pixel_x": pixel_x,
                    "median_y": median_y,
                    "median_component_pixel_count": median_count,
                    "largest_component_pixel_count": dominant_count,
                    "clusters": clusters,
                }
            )

    return {
        "multi_component_column_count": len(multi_component_x),
        "multi_component_pixel_x_ranges": _compress_ranges(multi_component_x),
        "ambiguous_median_count": len(ambiguous),
        "ambiguous_medians": ambiguous,
    }


def _row_audit(rows: list[dict[str, str]], pairwise_bound: float, gross_threshold: float) -> dict[str, Any]:
    by_series: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_series.setdefault(row["series_id"], []).append(row)

    result: dict[str, Any] = {}
    for series_id, series_rows in sorted(by_series.items()):
        series_rows.sort(key=lambda row: int(row["pixel_x"]))
        gaps: list[dict[str, int]] = []
        transitions: list[dict[str, Any]] = []
        for first, second in zip(series_rows, series_rows[1:]):
            x0, x1 = int(first["pixel_x"]), int(second["pixel_x"])
            dx = x1 - x0
            if dx > 1:
                gaps.append({"pixel_x_from": x0, "pixel_x_to": x1, "missing_columns": dx - 1})
            if dx != 1:
                continue
            delta = float(second["normalized_signal"]) - float(first["normalized_signal"])
            if abs(delta) >= gross_threshold:
                transitions.append(
                    {
                        "pixel_x_from": x0,
                        "pixel_x_to": x1,
                        "time_ps_from": float(first["time_ps"]),
                        "time_ps_to": float(second["time_ps"]),
                        "normalized_signal_from": float(first["normalized_signal"]),
                        "normalized_signal_to": float(second["normalized_signal"]),
                        "absolute_step": abs(delta),
                        "step_over_pairwise_uncertainty_bound": abs(delta) / pairwise_bound,
                    }
                )
        all_steps = [
            abs(float(second["normalized_signal"]) - float(first["normalized_signal"]))
            for first, second in zip(series_rows, series_rows[1:])
            if int(second["pixel_x"]) - int(first["pixel_x"]) == 1
        ]
        result[series_id] = {
            "row_count": len(series_rows),
            "adjacent_pair_count": len(all_steps),
            "pixel_gaps": gaps,
            "max_adjacent_absolute_step": max(all_steps, default=None),
            "gross_discontinuity_count": len(transitions),
            "gross_discontinuities": transitions,
        }
    return result


def build_audit() -> dict[str, Any]:
    digitizer = load_source_digitizer()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    rows = _read_csv()
    rgb = np.asarray(Image.open(PNG).convert("RGB"))
    bounds = manifest["axes_box_pixels"]
    uncertainty = float(manifest["uncertainty_policy"]["normalized_signal_half_width"])
    pairwise_bound = 2.0 * uncertainty
    gross_threshold = 10.0 * pairwise_bound

    expected_rows = [
        row
        for series_id in ("red_trace", "green_trace", "blue_trace")
        for row in digitizer.extract_series(rgb, series_id)
    ]
    existing_by_key = {(r["series_id"], int(r["pixel_x"])): r for r in rows}
    replay_matches = len(expected_rows) == len(rows)
    for expected in expected_rows:
        actual = existing_by_key.get((expected["series_id"], int(expected["pixel_x"])))
        if actual is None:
            replay_matches = False
            break
        if any(actual[key] != str(expected[key]) for key in ("source_id", "series_id", "row_id", "pixel_x")):
            replay_matches = False
            break
        if any(
            abs(float(actual[key]) - float(expected[key])) > tolerance
            for key, tolerance in (
                ("pixel_y", 1e-12),
                ("time_ps", 1e-6),
                ("normalized_signal", 1e-8),
                ("extraction_uncertainty", 1e-12),
            )
        ):
            replay_matches = False
            break

    row_summary = _row_audit(rows, pairwise_bound, gross_threshold)
    pixel_summary = {
        series_id: _column_audit(rgb, digitizer, series_id, bounds)
        for series_id in ("red_trace", "green_trace", "blue_trace")
    }
    blue_jumps = row_summary["blue_trace"]["gross_discontinuities"]
    blue_ambiguous = pixel_summary["blue_trace"]["ambiguous_medians"]
    blue_affected_x = [
        int(record[key])
        for record in blue_jumps
        for key in ("pixel_x_from", "pixel_x_to")
    ]
    blue_affected_x.extend(record["pixel_x"] for record in blue_ambiguous)
    blue_region = [min(blue_affected_x), max(blue_affected_x)] if blue_affected_x else None
    left, right = bounds["left"], bounds["right"]
    time_range = None
    if blue_region:
        time_range = [
            (x - left) / (right - left) * 1200.0
            for x in blue_region
        ]

    input_hashes = {
        "source_png_sha256": sha256(PNG),
        "source_csv_sha256": sha256(CSV_PATH),
        "source_manifest_sha256": sha256(MANIFEST),
        "digitizer_script_sha256": sha256(SOURCE),
    }
    checks = {
        "source_png_hash_matches_manifest": input_hashes["source_png_sha256"]
        == manifest["input_assets"][0]["sha256"],
        "source_csv_hash_matches_manifest": input_hashes["source_csv_sha256"]
        == manifest["output_sha256"],
        "csv_row_count_matches_manifest": len(rows) == int(manifest["row_count"]),
        "pixel_digitization_replay_matches_existing_csv": replay_matches,
        "blue_trace_has_no_gross_discontinuity": len(blue_jumps) == 0,
    }
    status = (
        "PASS_SOURCE_IDENTITY_AND_REPLAY_WITH_LOCALIZED_PIXEL_MASK_WARNING"
        if all(value for key, value in checks.items() if key != "blue_trace_has_no_gross_discontinuity")
        and blue_jumps
        else "PASS_SOURCE_IDENTITY_AND_REPLAY"
        if all(checks.values())
        else "FAIL_SOURCE_IDENTITY_OR_REPLAY"
    )
    return {
        "schema_version": "t13-ding-fig1d-pixel-quality-v1",
        "artifact": "ding_2022_fig1d_pixel_quality_audit",
        "generated_on": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_DING_FIG1D_LOCALIZED_PIXEL_MASK_QUALITY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "PARTIAL",
            "what_is_closed": [
                "pixel-level replay of the existing deterministic Fig. 1d extraction against its archived PNG and CSV",
                "localized identification of large blue-mask discontinuities and competing pixel components",
            ],
            "equation_or_mapping": {
                "axis_map": "time_ps=(pixel_x-left)/(right-left)*1200",
                "signal_map": "normalized_signal=1-(pixel_y-top)/(bottom-top)*1.2",
                "extractor": "median selected y pixel per x column",
                "TTG_observable": "y_TTG=Delta_Tq(t)/Delta_Tq(0); dimensionless digitized trace only",
            },
            "units": {
                "pixel_x": "pixel",
                "pixel_y": "pixel",
                "time": "ps",
                "normalized_signal": "dimensionless",
            },
            "derivation_class": "read-only source-pixel replay and numerical quality diagnostic",
            "observable": "Ding 2022 Fig. 1d figure-derived normalized response traces",
            "data_role": "FIGURE_DERIVED_NORMALIZED_COMPARISON_NOT_RAW_SOURCE",
            "evidence_artifacts": [
                "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_fig1d_digitized.csv",
                "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_fig1d_digitized_manifest.json",
                "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_fig1.png",
            ],
            "verification_status": status,
            "open_blockers": [
                "the blue-trace region containing gross mask discontinuities is not qualified for derivative, dip-time, or velocity inference",
                "pixel-derived uncertainty remains an extraction bound, not experimental uncertainty",
                "raw author numeric response, graphite Phi normalization, independent alpha_Phi_K, and physical transport remain separate blockers",
            ],
            "dependency_unlocked": "localized exclusion boundary for derivative-like use only; no source-lane promotion, alpha, TTG prediction, Core, or Full Topic 13 unlock",
            "claim_boundary": "This is a digitization quality finding, not evidence of physical discontinuity or validation of UET. No CSV values were changed.",
        },
        "verification": {
            "checks": checks,
            "input_hashes": input_hashes,
            "uncertainty_policy": {
                "single_row_normalized_half_width": uncertainty,
                "pairwise_worst_case_bound": pairwise_bound,
                "gross_jump_triage_threshold": gross_threshold,
                "gross_jump_threshold_definition": "10 times the sum of two declared pixel-extraction half-widths; diagnostic triage only, not an acceptance gate",
            },
            "series": row_summary,
            "pixel_components": pixel_summary,
            "blue_trace_suspect_pixel_x_range": blue_region,
            "blue_trace_suspect_time_ps_range": time_range,
            "holdout_accessed": False,
            "source_data_modified": False,
            "source_lane_status_changed": False,
            "claim_promotion": False,
        },
    }


def main() -> int:
    artifact = build_audit()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": artifact["status"], "path": str(OUTPUT), "checks": artifact["verification"]["checks"]}, indent=2))
    return 0 if artifact["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
