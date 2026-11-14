"""Create a provisional, deterministic digitization of Ding 2022 Fig. 1d.

This is an evidence-intake step only. It does not fit Phi, estimate alpha_Phi_K,
read the Xie holdout, or claim that a figure trace is raw source data.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[5]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
RAW = TOPIC / "Data/03_Research/raw/ding_2022_fig1.png"
CSV_PATH = TOPIC / "Data/03_Research/ding_2022_fig1d_digitized.csv"
MANIFEST_PATH = TOPIC / "Data/03_Research/ding_2022_fig1d_digitized_manifest.json"
PACKAGE_PATH = TOPIC / "Data/03_Research/matter_space_second_sound_source_package.json"
REVIEW_PATH = TOPIC / "Data/03_Research/matter_space_thermal_source_review.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def colour_mask(rgb: np.ndarray, series_id: str) -> np.ndarray:
    red, green, blue = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    if series_id == "red_trace":
        return (red > 170) & (green < 150) & (blue < 150) & ((red - green) > 45)
    if series_id == "green_trace":
        return (green > 125) & (red < 170) & (blue < 170) & ((green - red) > 20)
    if series_id == "blue_trace":
        return (blue > 125) & (red < 170) & (green < 180) & ((blue - red) > 20)
    raise ValueError(series_id)


def extract_series(rgb: np.ndarray, series_id: str) -> list[dict[str, Any]]:
    # Coordinates are the declared axes box for Figure 1d in the downloaded
    # 685x798 PNG. The inner margin excludes panel labels and tick text.
    left, right, top, bottom = 379, 668, 271, 481
    x0, x1 = left + 12, right - 10
    y0, y1 = top + 8, bottom - 10
    mask = colour_mask(rgb, series_id)
    rows: list[dict[str, Any]] = []
    for pixel_x in range(x0, x1 + 1):
        ys = np.flatnonzero(mask[y0:y1 + 1, pixel_x]) + y0
        if ys.size == 0:
            continue
        pixel_y = float(np.median(ys))
        time_ps = (pixel_x - left) / (right - left) * 1200.0
        normalized_signal = 1.0 - (pixel_y - top) / (bottom - top) * 1.2
        rows.append(
            {
                "source_id": "ding_2022_fig1d_digitized",
                "series_id": series_id,
                "row_id": f"{series_id}:{pixel_x}",
                "pixel_x": pixel_x,
                "pixel_y": pixel_y,
                "time_ps": round(float(time_ps), 6),
                "normalized_signal": round(float(normalized_signal), 8),
                "extraction_uncertainty": 2.0 / (bottom - top) * 1.2,
                "source_locator": "Nature Communications 13, 285 (2022), Fig. 1d; color mapping remains open",
                "series_mapping_status": "OPEN_COLOR_TO_GRATING_PERIOD",
            }
        )
    return rows


def update_source_records(manifest: dict[str, Any]) -> None:
    package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8-sig"))
    review = json.loads(REVIEW_PATH.read_text(encoding="utf-8-sig"))
    numeric_record = {
        "source_id": "ding_2022_fig1d_digitized",
        "title": "Provisional digitization of Ding 2022 Figure 1d",
        "parent_source_id": "ding_2022_graphite_over_200K",
        "doi": "10.1038/s41467-021-27907-z",
        "url": "https://www.nature.com/articles/s41467-021-27907-z",
        "license_or_terms": "CC BY 4.0 article; figure asset used for a labelled provisional digitization",
        "upstream_data_availability": "open_access_figure_asset_not_raw_author_table",
        "original_filename": "ding_2022_fig1.png",
        "local_raw_path": "Data/03_Research/ding_2022_fig1d_digitized.csv",
        "local_numeric_path": "Data/03_Research/ding_2022_fig1d_digitized.csv",
        "local_record_path": "Data/03_Research/ding_2022_fig1d_digitized_manifest.json",
        "preprocessing": "deterministic RGB color-mask digitization of the declared Fig. 1d axes box; one median pixel per x column; no interpolation beyond pixel-column sampling",
        "source_locator": {
            "figure": "Fig. 1d",
            "axes_box_pixels": {"left": 379, "right": 668, "top": 271, "bottom": 481},
            "axis_ranges": {"time_ps": [0.0, 1200.0], "normalized_signal": [-0.2, 1.0]},
            "series_mapping_status": "OPEN_COLOR_TO_GRATING_PERIOD",
        },
        "reported_observable_family": "normalized transient thermal-grating temperature-response trace",
        "reported_unit_context": ["time ps", "normalized signal dimensionless", "figure temperature-response context K"],
        "extraction_uncertainty": {
            "pixel_y_half_width": 2.0,
            "normalized_signal_half_width": manifest["uncertainty_policy"]["normalized_signal_half_width"],
            "status": "provisional_figure_digitization_uncertainty_not_experimental_error_bar",
        },
        "row_identity": {"key": "source_id + series_id + pixel_x", "row_count": manifest["row_count"]},
        "benchmark_role": "training_source_candidate_for_normalized_shape_only; no fitting in current wave",
        "status": "PROVISIONAL_DIGITIZED_NUMERIC_PACKAGE",
        "input_assets": manifest["input_assets"],
        "output_hash": manifest["output_sha256"],
    }
    package["status"] = "PROVISIONAL_NUMERIC_SOURCE_INTAKE"
    usage = dict(package.get("usage_policy", {}))
    usage.update(
        {
            "numeric_fitting_allowed": False,
            "observable_map_status": "NORMALIZED_DEFINED_DIMENSIONAL_BLOCKED",
            "local_numeric_source_status": "PROVISIONAL_DIGITIZED_FIGURE_PACKAGE",
            "blocker": "figure-derived normalized intake is not raw author data; alpha_Phi_K and independent dimensional mapping remain open",
        }
    )
    package["usage_policy"] = usage
    sources = [source for source in package.get("sources", []) if source.get("source_id") != numeric_record["source_id"]]
    sources.insert(1, numeric_record)
    package["sources"] = sources
    access = dict(package.get("source_access_audit", {}))
    access.update(
        {
            "direct_numeric_download_route_captured": "figure_asset_route_captured",
            "local_numeric_archive": True,
            "numeric_source_route_status": "PROVISIONAL_FIGURE_DIGITIZATION",
            "figure_digitization_manifest": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_fig1d_digitized_manifest.json",
            "holdout_policy": "metadata-only until normalized operator and parameter policy are frozen",
        }
    )
    package["source_access_audit"] = access
    package["claim_boundary"] = "Ding 2022 figure digitization is provisional normalized-shape intake; no external numeric validation, dimensional prediction, or holdout access"
    PACKAGE_PATH.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    review_sources = [source for source in review.get("sources", []) if source.get("source_id") != numeric_record["source_id"]]
    review_sources.insert(
        1,
        {
            "source_id": numeric_record["source_id"],
            "doi": numeric_record["doi"],
            "url": numeric_record["url"],
            "source_locator": ["Fig. 1d", "axes box and axis ranges recorded in digitization manifest"],
            "external_numeric_status": "figure_asset_digitized_locally_provisional",
            "local_numeric_path": numeric_record["local_raw_path"],
            "local_numeric_hash": manifest["output_sha256"],
            "preprocessing": numeric_record["preprocessing"],
            "units_reviewed": ["ps", "dimensionless normalized signal"],
            "uncertainty": numeric_record["extraction_uncertainty"],
            "row_identity": numeric_record["row_identity"],
            "benchmark_role": numeric_record["benchmark_role"],
            "status": numeric_record["status"],
        },
    )
    review["sources"] = review_sources
    review["local_numeric_archive"] = True
    review["source_access_audit"]["local_numeric_archive"] = True
    review["source_access_audit"]["numeric_source_route_status"] = "PROVISIONAL_FIGURE_DIGITIZATION"
    review["source_access_audit"]["figure_digitization_manifest"] = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_fig1d_digitized_manifest.json"
    review["claim_boundary"] = "Ding figure digitization is provisional intake only; Xie 2026 remains metadata-only locked holdout"
    REVIEW_PATH.write_text(json.dumps(review, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    if not RAW.is_file():
        raise FileNotFoundError(RAW)
    image = Image.open(RAW).convert("RGB")
    rgb = np.asarray(image)
    rows = [row for series_id in ("red_trace", "green_trace", "blue_trace") for row in extract_series(rgb, series_id)]
    if len(rows) < 100 or len({row["series_id"] for row in rows}) < 2:
        raise RuntimeError("figure digitization found too few trace pixels")
    fieldnames = list(rows[0])
    CSV_PATH.write_text("", encoding="utf-8")
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "schema_version": "1.0",
        "artifact": "ding_2022_fig1d_digitized_manifest",
        "generated_on": date.today().isoformat(),
        "status": "PROVISIONAL_DIGITIZED_NUMERIC_PACKAGE",
        "input_assets": [{"path": "Data/03_Research/raw/ding_2022_fig1.png", "sha256": sha256(RAW), "license_context": "CC BY 4.0 article figure asset"}],
        "output_path": str(CSV_PATH.relative_to(TOPIC)).replace("\\", "/"),
        "output_sha256": sha256(CSV_PATH),
        "row_count": len(rows),
        "series": sorted({row["series_id"] for row in rows}),
        "source_locator": "Nature Communications 13, 285 (2022), Fig. 1d",
        "axes_box_pixels": {"left": 379, "right": 668, "top": 271, "bottom": 481},
        "axis_ranges": {"time_ps": [0.0, 1200.0], "normalized_signal": [-0.2, 1.0]},
        "preprocessing": "RGB color-mask selection, median y per pixel column, direct affine axis conversion; no smoothing or fitting",
        "uncertainty_policy": {"pixel_y_half_width": 2.0, "normalized_signal_half_width": 2.0 / 210.0 * 1.2, "not_experimental_error_bar": True},
        "row_identity": "source_id + series_id + pixel_x",
        "series_mapping_status": "OPEN_COLOR_TO_GRATING_PERIOD",
        "holdout_policy": "No Xie 2026 bytes, curves, or figures were read or digitized.",
        "claim_boundary": "provisional figure-derived normalized shape intake; not raw source data and not external validation",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    update_source_records(manifest)
    print(json.dumps({"status": manifest["status"], "row_count": len(rows), "csv_sha256": manifest["output_sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
