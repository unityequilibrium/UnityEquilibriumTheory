"""Shared helpers for the Research Standard v2 checks (docs/STANDARD.md)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
STANDARD_DIR = Path("docs/standard")
SCHEMA_PATH = STANDARD_DIR / "schema.json"
CLAIMS_PATH = STANDARD_DIR / "claims.json"
DATA_MANIFEST_PATH = STANDARD_DIR / "data_manifest.json"
TESTS_DIR = STANDARD_DIR / "tests"
RESULTS_DIR = STANDARD_DIR / "results"
THEORY_CARD_PATH = Path("docs/core/theory_card.json")

LEVEL_ORDER = {
    "L0_SPECULATIVE": 0,
    "L1_CONSISTENT": 1,
    "L2_CONFRONTED": 2,
    "L3_REPLICATED": 3,
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def record_files(root: Path, directory: Path) -> list[Path]:
    folder = root / directory
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.glob("*.json") if p.is_file())
