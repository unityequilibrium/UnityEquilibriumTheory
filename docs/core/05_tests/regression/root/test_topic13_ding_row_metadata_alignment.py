from __future__ import annotations
from docs.core.core_paths import repo_root

import csv
import json
from pathlib import Path


ROOT = repo_root()
CSV = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_fig1d_digitized.csv"
MANIFEST = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_fig1d_digitized_manifest.json"


def test_ding_rows_match_closed_mapping_without_becoming_raw_source() -> None:
    with CSV.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    assert len(rows) == 432
    assert {row["series_mapping_status"] for row in rows} == {"CLOSED_COLOR_TO_GRATING_PERIOD"}
    assert {row["source_locator"] for row in rows} == {
        "Nature Communications 13, 285 (2022), Fig. 1d; printed-legend mapping artifact"
    }
    assert manifest["row_metadata_alignment"]["numeric_values_changed"] is False
    assert manifest["row_metadata_alignment"]["data_role"] == "FIGURE_DERIVED_NORMALIZED_COMPARISON_NOT_RAW_SOURCE"
