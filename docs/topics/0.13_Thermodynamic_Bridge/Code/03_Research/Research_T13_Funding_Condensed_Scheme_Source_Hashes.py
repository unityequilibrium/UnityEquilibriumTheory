"""Refresh the source-byte links of the bounded condensed-scheme decision."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
OUTPUT = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "t13_funding_condensed_scheme_selection_2026-09-28.json"
)


def refresh_source_hashes() -> dict:
    decision = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if decision["full_core_unlock"] or decision["g1_physical_unlock"] or decision["g2_science_unlock"]:
        raise ValueError("A source-hash refresh cannot promote the route decision")
    decision["source_hashes"] = {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in decision["source_hashes"]
    }
    return decision


if __name__ == "__main__":
    OUTPUT.write_bytes((json.dumps(refresh_source_hashes(), indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(OUTPUT)
