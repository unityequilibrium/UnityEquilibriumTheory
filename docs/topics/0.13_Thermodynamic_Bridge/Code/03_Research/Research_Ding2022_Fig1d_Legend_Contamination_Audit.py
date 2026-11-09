"""Test whether the archived Fig. 1d blue-mask jumps come from its legend."""

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
PIXEL_AUDIT = TOPIC / "Result/artifacts/ding_2022_fig1d_pixel_quality_audit.json"
OUTPUT = TOPIC / "Result/artifacts/ding_2022_fig1d_legend_contamination_audit.json"

# Manually located around the blue swatch/line in the printed legend, not a
# fitted region. This alternative is read-only and never replaces the source CSV.
LEGEND_ROI = {"x_min": 560, "x_max": 597, "y_min": 296, "y_max": 307}
NORMALIZED_RANGE = 1.2


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_digitizer() -> Any:
    spec = importlib.util.spec_from_file_location("ding_figure_digitizer", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load digitizer: {SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_blue_csv() -> dict[int, dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as handle:
        rows = csv.DictReader(handle)
        return {
            int(row["pixel_x"]): row
            for row in rows
            if row["series_id"] == "blue_trace"
        }


def extract_blue(
    rgb: np.ndarray,
    digitizer: Any,
    bounds: dict[str, int],
    exclude_legend: bool,
) -> list[dict[str, float | int]]:
    left, right = bounds["left"], bounds["right"]
    top, bottom = bounds["top"], bounds["bottom"]
    x0, x1 = left + 12, right - 10
    y0, y1 = top + 8, bottom - 10
    mask = digitizer.colour_mask(rgb, "blue_trace")
    rows: list[dict[str, float | int]] = []

    for pixel_x in range(x0, x1 + 1):
        ys = np.flatnonzero(mask[y0:y1 + 1, pixel_x]) + y0
        if exclude_legend:
            in_legend = (
                (pixel_x >= LEGEND_ROI["x_min"])
                & (pixel_x <= LEGEND_ROI["x_max"])
                & (ys >= LEGEND_ROI["y_min"])
                & (ys <= LEGEND_ROI["y_max"])
            )
            ys = ys[~in_legend]
        if ys.size == 0:
            continue

        pixel_y = float(np.median(ys))
        rows.append(
            {
                "pixel_x": pixel_x,
                "pixel_y": pixel_y,
                "time_ps": (pixel_x - left) / (right - left) * 1200.0,
                "normalized_signal": 1.0 - (pixel_y - top) / (bottom - top) * NORMALIZED_RANGE,
            }
        )
    return rows


def large_adjacent_steps(
    rows: list[dict[str, float | int]], threshold: float
) -> list[dict[str, float | int]]:
    steps: list[dict[str, float | int]] = []
    for first, second in zip(rows, rows[1:]):
        if int(second["pixel_x"]) - int(first["pixel_x"]) != 1:
            continue
        step = abs(float(second["normalized_signal"]) - float(first["normalized_signal"]))
        if step >= threshold:
            steps.append(
                {
                    "pixel_x_from": int(first["pixel_x"]),
                    "pixel_x_to": int(second["pixel_x"]),
                    "absolute_step": step,
                }
            )
    return steps


def build_audit() -> dict[str, Any]:
    digitizer = load_digitizer()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    previous_audit = json.loads(PIXEL_AUDIT.read_text(encoding="utf-8-sig"))
    rgb = np.asarray(Image.open(PNG).convert("RGB"))
    bounds = manifest["axes_box_pixels"]
    uncertainty = float(manifest["uncertainty_policy"]["normalized_signal_half_width"])
    pairwise_bound = 2.0 * uncertainty
    gross_threshold = 10.0 * pairwise_bound

    baseline = extract_blue(rgb, digitizer, bounds, exclude_legend=False)
    challenger = extract_blue(rgb, digitizer, bounds, exclude_legend=True)
    stored = read_blue_csv()
    source_mask = digitizer.colour_mask(rgb, "blue_trace")
    roi_blue_pixels = int(
        np.count_nonzero(
            source_mask[
                LEGEND_ROI["y_min"] : LEGEND_ROI["y_max"] + 1,
                LEGEND_ROI["x_min"] : LEGEND_ROI["x_max"] + 1,
            ]
        )
    )

    replay_matches = len(baseline) == len(stored)
    for row in baseline:
        actual = stored.get(int(row["pixel_x"]))
        if actual is None or any(
            abs(float(actual[key]) - float(row[key])) > tolerance
            for key, tolerance in (("pixel_y", 1e-12), ("normalized_signal", 1e-8))
        ):
            replay_matches = False
            break

    baseline_steps = large_adjacent_steps(baseline, gross_threshold)
    challenger_steps = large_adjacent_steps(challenger, gross_threshold)
    baseline_by_x = {int(row["pixel_x"]): row for row in baseline}
    challenger_by_x = {int(row["pixel_x"]): row for row in challenger}
    removed_columns = sorted(set(baseline_by_x) - set(challenger_by_x))
    reassigned_columns = [
        {
            "pixel_x": x,
            "baseline_pixel_y": baseline_by_x[x]["pixel_y"],
            "challenger_pixel_y": challenger_by_x[x]["pixel_y"],
        }
        for x in sorted(set(baseline_by_x) & set(challenger_by_x))
        if baseline_by_x[x]["pixel_y"] != challenger_by_x[x]["pixel_y"]
    ]

    hashes = {
        "source_png_sha256": sha256(PNG),
        "source_csv_sha256": sha256(CSV_PATH),
        "source_manifest_sha256": sha256(MANIFEST),
        "source_digitizer_sha256": sha256(SOURCE),
        "prior_pixel_audit_sha256": sha256(PIXEL_AUDIT),
    }
    checks = {
        "source_png_hash_matches_manifest": hashes["source_png_sha256"]
        == manifest["input_assets"][0]["sha256"],
        "source_csv_hash_matches_manifest": hashes["source_csv_sha256"]
        == manifest["output_sha256"],
        "baseline_replay_matches_stored_blue_rows": replay_matches,
        "baseline_jump_count_matches_prior_audit": len(baseline_steps)
        == previous_audit["verification"]["series"]["blue_trace"]["gross_discontinuity_count"],
        "legend_roi_contains_expected_blue_pixels": roi_blue_pixels == 30,
        "challenger_has_no_large_adjacent_jump": len(challenger_steps) == 0,
    }
    status = (
        "PASS_LEGEND_CONTAMINATION_DIAGNOSTIC_ONLY"
        if all(checks.values())
        else "FAIL_SOURCE_OR_REPLAY_CONSISTENCY"
    )

    return {
        "schema_version": "t13-ding-fig1d-legend-audit-v1",
        "artifact": "ding_2022_fig1d_legend_contamination_audit",
        "generated_on": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_DING_FIG1D_BLUE_LEGEND_CONTAMINATION",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "PARTIAL",
            "what_is_closed": [
                "all 10 prior large adjacent blue-mask jumps disappear in a separate challenger extraction after exclusion of the visually located blue legend swatch/line",
                "the declared diagnostic threshold and source image are unchanged",
            ],
            "equation_or_mapping": {
                "axis_map": "time_ps=(pixel_x-left)/(right-left)*1200",
                "signal_map": "normalized_signal=1-(pixel_y-top)/(bottom-top)*1.2",
                "baseline_extractor": "median blue-mask y pixel per x column",
                "challenger_only_change": "exclude blue-mask pixels inside the manually inspected legend ROI; do not interpolate missing columns",
            },
            "units": {
                "pixel_x": "pixel",
                "pixel_y": "pixel",
                "time": "ps",
                "normalized_signal": "dimensionless",
            },
            "derivation_class": "read-only source-pixel extraction sensitivity audit",
            "observable": "Ding 2022 Fig. 1d blue figure-derived normalized response mask",
            "data_role": "FIGURE_DERIVED_NORMALIZED_COMPARISON_NOT_RAW_SOURCE",
            "evidence_artifacts": [
                "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/ding_2022_fig1d_pixel_quality_audit.json",
                "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_fig1d_digitized_manifest.json",
                "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_fig1.png",
            ],
            "verification_status": status,
            "open_blockers": [
                "the published figure combines measured points and simulated curves; the blue mask has not separated these roles",
                "the challenger trace is not raw author data and is not qualified for dip-time or velocity inference",
                "authorized raw response rows, graphite Phi normalization, independent alpha_Phi_K, and physical transport remain open",
            ],
            "dependency_unlocked": "No physical dependency; permits a separate marker-versus-curve extraction study only",
            "claim_boundary": "The prior pixel jumps are attributable to legend contamination under this figure-mask diagnostic. This does not identify a physical discontinuity or validate UET.",
        },
        "verification": {
            "checks": checks,
            "input_hashes": hashes,
            "legend_roi_pixels": LEGEND_ROI,
            "legend_roi_selection": "manually inspected against the archived Fig. 1d raster after the prior audit flagged the same columns; post hoc sensitivity check, not preregistered",
            "uncertainty_and_threshold": {
                "single_row_normalized_half_width": uncertainty,
                "pairwise_bound": pairwise_bound,
                "gross_jump_triage_threshold": gross_threshold,
                "threshold_changed": False,
            },
            "baseline": {
                "blue_row_count": len(baseline),
                "large_adjacent_jump_count": len(baseline_steps),
                "large_adjacent_jumps": baseline_steps,
            },
            "challenger": {
                "blue_row_count": len(challenger),
                "large_adjacent_jump_count": len(challenger_steps),
                "large_adjacent_jumps": challenger_steps,
                "legend_blue_pixels_excluded": roi_blue_pixels,
                "columns_without_nonlegend_blue_pixel": removed_columns,
                "columns_with_changed_median": reassigned_columns,
                "interpolation_or_smoothing": False,
                "fit_or_parameter_tuning": False,
                "written_over_source_csv": False,
            },
            "measured_points_separated_from_simulation": False,
            "dip_time_or_velocity_inferred": False,
            "holdout_accessed": False,
            "source_data_modified": False,
            "claim_promotion": False,
        },
    }


def main() -> int:
    artifact = build_audit()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": artifact["status"],
                "path": str(OUTPUT),
                "checks": artifact["verification"]["checks"],
                "baseline_large_jumps": artifact["verification"]["baseline"]["large_adjacent_jump_count"],
                "challenger_large_jumps": artifact["verification"]["challenger"]["large_adjacent_jump_count"],
            },
            indent=2,
        )
    )
    return 0 if artifact["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
