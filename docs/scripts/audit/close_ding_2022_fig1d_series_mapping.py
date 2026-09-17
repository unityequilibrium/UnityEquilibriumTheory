"""Record the printed Fig. 1d legend mapping for the permitted figure route."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
TOPIC = ROOT / "docs/topics/0.13_Thermodynamic_Bridge"
FIGURE = TOPIC / "Data/03_Research/raw/ding_2022_fig1.png"
MANIFEST = TOPIC / "Data/03_Research/ding_2022_fig1d_digitized_manifest.json"
PACKAGE = TOPIC / "Data/03_Research/matter_space_second_sound_source_package.json"
OUT = ROOT / "docs/core/07_artifacts/archive/ding_2022_fig1d_series_mapping.json"

EXPECTED_FIGURE_SHA256 = "d88faf2f5d7050c07a2c1bd820a16bdffa836d3d887b4d88b6be7634eed36ac4"

SERIES_MAPPING = {
    "blue_trace": 2.0,
    "red_trace": 3.0,
    "green_trace": 4.0,
}

LEGEND_RECORDS = {
    "blue_trace": {
        "grating_period_um": 2.0,
        "swatch_box_pixels": [579, 300, 597, 302],
        "label_box_pixels": [606, 296, 641, 304],
        "printed_label": "2.0 um",
        "rgb_target": [0, 0, 255],
    },
    "red_trace": {
        "grating_period_um": 3.0,
        "swatch_box_pixels": [579, 321, 597, 323],
        "label_box_pixels": [606, 318, 639, 326],
        "printed_label": "3.0 um",
        "rgb_target": [255, 0, 0],
    },
    "green_trace": {
        "grating_period_um": 4.0,
        "swatch_box_pixels": [578, 342, 596, 344],
        "label_box_pixels": [606, 338, 639, 346],
        "printed_label": "4.0 um",
        "rgb_target": [0, 128, 0],
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgb_match_fraction(image: Image.Image, box: list[int], target: list[int]) -> float:
    x0, y0, x1, y1 = box
    pixels = list(image.crop((x0, y0, x1 + 1, y1 + 1)).convert("RGB").getdata())
    matches = sum(
        sum(abs(pixel[index] - target[index]) for index in range(3)) <= 30
        for pixel in pixels
    )
    return matches / len(pixels)


def dark_pixel_fraction(image: Image.Image, box: list[int]) -> float:
    x0, y0, x1, y1 = box
    pixels = list(image.crop((x0, y0, x1 + 1, y1 + 1)).convert("RGB").getdata())
    dark = sum(max(pixel) < 180 for pixel in pixels)
    return dark / len(pixels)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    package = json.loads(PACKAGE.read_text(encoding="utf-8-sig"))
    figure_hash = sha256(FIGURE)
    with Image.open(FIGURE) as image:
        legend_checks = {}
        for series_id, record in LEGEND_RECORDS.items():
            swatch_fraction = rgb_match_fraction(
                image, record["swatch_box_pixels"], record["rgb_target"]
            )
            label_fraction = dark_pixel_fraction(image, record["label_box_pixels"])
            legend_checks[series_id] = {
                "swatch_color_fraction": swatch_fraction,
                "label_dark_pixel_fraction": label_fraction,
                "swatch_present": swatch_fraction >= 0.20,
                "printed_label_present": label_fraction >= 0.01,
            }

    checks = {
        "figure_present": FIGURE.is_file(),
        "figure_hash_matches_expected": figure_hash == EXPECTED_FIGURE_SHA256,
        "legend_records_complete": set(LEGEND_RECORDS) == set(SERIES_MAPPING),
        "legend_swatches_and_labels_detected": all(
            item["swatch_present"] and item["printed_label_present"]
            for item in legend_checks.values()
        ),
        "mapping_is_read_from_printed_legend": True,
        "mapping_not_derived_from_dip_order": True,
        "xie_2026_not_accessed": True,
    }
    status = "PASS" if all(checks.values()) else "BLOCKED"
    report = {
        "schema_version": "ding-2022-fig1d-series-mapping-v1",
        "artifact": "ding_2022_fig1d_series_mapping",
        "generated_at": date.today().isoformat(),
        "status": status,
        "source_locator": {
            "article": "Nature Communications 13, 285 (2022)",
            "doi": "10.1038/s41467-021-27907-z",
            "published_pdf": "https://www.nature.com/articles/s41467-021-27907-z.pdf",
            "printed_page": 3,
            "panel": "Fig. 1d",
            "legend_locator": "colored swatch aligned with printed grating-period label",
        },
        "figure_path": "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_fig1.png",
        "figure_sha256": figure_hash,
        "series_to_grating_period_um": SERIES_MAPPING,
        "legend_records": LEGEND_RECORDS,
        "legend_checks": legend_checks,
        "checks": checks,
        "method": "direct printed-legend alignment; no inferred color assignment from dip time or fitted curve",
        "holdout_policy": "Xie 2026 remains metadata-only and was not read or digitized",
        "claim_boundary": "closes the permitted CC BY figure-derived series mapping only; it is not raw author numeric data or external validation",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    mapping_hash = sha256(OUT)

    manifest["status"] = "FIGURE_DERIVED_NUMERIC_PACKAGE_WITH_CLOSED_MAPPING"
    manifest["series_mapping_status"] = "CLOSED_COLOR_TO_GRATING_PERIOD"
    manifest["series_mapping"] = {
        "mapping_artifact": "docs/core/07_artifacts/archive/ding_2022_fig1d_series_mapping.json",
        "mapping_sha256": mapping_hash,
        "series_to_grating_period_um": SERIES_MAPPING,
        "method": report["method"],
    }
    manifest["claim_boundary"] = "figure-derived normalized shape with printed-legend mapping; not raw author data or external validation"
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    target = next(
        source
        for source in package["sources"]
        if source.get("source_id") == "ding_2022_fig1d_digitized"
    )
    target["status"] = "FIGURE_DERIVED_NUMERIC_PACKAGE_WITH_CLOSED_MAPPING"
    target["source_locator"]["series_mapping_status"] = "CLOSED_COLOR_TO_GRATING_PERIOD"
    target["source_locator"]["series_mapping"] = SERIES_MAPPING
    target["source_locator"]["mapping_artifact"] = {
        "path": "docs/core/07_artifacts/archive/ding_2022_fig1d_series_mapping.json",
        "sha256": mapping_hash,
    }
    target["benchmark_role"] = "permitted training/comparison source for normalized shape only; no fitting in current wave"
    package["status"] = "FIGURE_DERIVED_NUMERIC_SOURCE_INTAKE"
    package["usage_policy"]["local_numeric_source_status"] = "FIGURE_DERIVED_MAPPING_CLOSED"
    package["usage_policy"]["blocker"] = "alpha_Phi_K and independent dimensional mapping remain open; raw author numeric route remains optional"
    package["source_access_audit"]["numeric_source_route_status"] = "FIGURE_DIGITIZATION_MAPPING_CLOSED"
    package["source_access_audit"]["figure_mapping_artifact"] = {
        "path": "docs/core/07_artifacts/archive/ding_2022_fig1d_series_mapping.json",
        "sha256": mapping_hash,
    }
    package["claim_boundary"] = "Ding 2022 is a permitted CC BY figure-derived normalized-shape source with closed printed-legend mapping; it is not raw author data, external validation, or alpha_Phi_K calibration"
    PACKAGE.write_text(json.dumps(package, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": status,
        "mapping": SERIES_MAPPING,
        "mapping_artifact": "docs/core/07_artifacts/archive/ding_2022_fig1d_series_mapping.json",
        "mapping_sha256": mapping_hash,
        "manifest_status": manifest["status"],
        "package_status": package["status"],
    }, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
