"""
Extract source-locked AME2020 binding-energy data for topic 0.5.

This script now writes two layers:
- a table-wide parsed JSON for every nuclide with readable BE/A
- the historical validation subset used by the strict 0.5 verifier
"""

from __future__ import annotations

# BEGIN UET REPO ROOT BOOTSTRAP
import sys as _uet_sys
from pathlib import Path as _UETPath

_UET_REPO_ROOT = None
_UET_HERE = _UETPath(__file__).resolve()
for _UET_CANDIDATE in (_UET_HERE.parent, *_UET_HERE.parents):
    if (_UET_CANDIDATE / "docs" / "core" / "core_paths.py").is_file():
        _UET_REPO_ROOT = _UET_CANDIDATE
        break
if _UET_REPO_ROOT is None:
    raise RuntimeError("cannot locate repository root from the tooling script")
if str(_UET_REPO_ROOT) not in _uet_sys.path:
    _uet_sys.path.insert(0, str(_UET_REPO_ROOT))
# END UET REPO ROOT BOOTSTRAP

import json
import re
import sys
from pathlib import Path


def _bootstrap():
    curr = Path(__file__).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    return None


ROOT = _bootstrap()
if not ROOT:
    print("CRITICAL: UET docs root not found!")
    sys.exit(1)


from docs import ROOT_PATH


root_path = ROOT_PATH
ame_path = root_path / "docs" / "data" / "external" / "particle_physics" / "ame2020" / "mass_1.mas20"
output_path = (
    root_path
    / "docs"
    / "topics"
    / "0.5_Nuclear_Binding_Hadrons"
    / "Data"
    / "03_Research"
    / "Data_AME2020_Binding_RawSubset.json"
)
full_output_path = (
    root_path
    / "docs"
    / "topics"
    / "0.5_Nuclear_Binding_Hadrons"
    / "Data"
    / "03_Research"
    / "Data_AME2020_Binding_FullParsed.json"
)
manifest_output_path = (
    root_path
    / "docs"
    / "topics"
    / "0.5_Nuclear_Binding_Hadrons"
    / "Data"
    / "03_Research"
    / "Data_AME2020_Benchmark_Manifest.json"
)

TARGETS = {
    ("H", 2, 1): "H2",
    ("He", 4, 2): "He4",
    ("C", 12, 6): "C12",
    ("O", 16, 8): "O16",
    ("Fe", 56, 26): "Fe56",
    ("Ni", 62, 28): "Ni62",
    ("U", 238, 92): "U238",
}

LINE_RE = re.compile(
    r"^\s*[01 ]?\s*(-?\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([A-Za-z]{1,3})\s*(\S*)?\s+"
    r"([0-9#.*-]+)\s+([0-9#.*a-]+)\s+([0-9#.*-]+)\s+([0-9#.*a-]+)"
)


def parse_float(token: str) -> float | None:
    token = token.strip()
    if not token or "*" in token:
        return None
    token = token.replace("#", "")
    token = token.replace("a", "")
    return float(token)


def main() -> int:
    if not ame_path.exists():
        raise FileNotFoundError(f"AME2020 raw file not found: {ame_path}")

    full_data: dict[str, dict] = {}
    extracted: dict[str, dict] = {}
    source_lines: dict[str, int] = {}
    line_texts: dict[str, str] = {}
    skipped_no_binding = 0

    for lineno, line in enumerate(ame_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        match = LINE_RE.match(line)
        if not match:
            continue
        _nz, n, z, a, element, origin, mass_excess, mass_unc, be_per_a, be_per_a_unc = match.groups()
        a_int = int(a)
        z_int = int(z)
        n_int = int(n)
        be_per_a_keV = parse_float(be_per_a)
        if be_per_a_keV is None:
            skipped_no_binding += 1
            continue
        be_total_keV = be_per_a_keV * int(a) if be_per_a_keV is not None else None
        table_label = f"{element}{a_int}"
        row = {
            "A": a_int,
            "Z": z_int,
            "N": n_int,
            "element": element,
            "origin_flag": origin or "",
            "mass_excess_keV": parse_float(mass_excess),
            "mass_excess_unc_keV": parse_float(mass_unc),
            "binding_energy_per_nucleon_keV": be_per_a_keV,
            "binding_energy_per_nucleon_unc_keV": parse_float(be_per_a_unc),
            "BE_keV": be_total_keV,
            "line_number": lineno,
        }
        full_data[f"{table_label}_Z{z_int}_N{n_int}"] = row

        key = (element, a_int, z_int)
        if key not in TARGETS:
            continue
        label = TARGETS[key]
        extracted[label] = row
        source_lines[label] = lineno
        line_texts[label] = line.rstrip()

    missing = sorted(set(TARGETS.values()) - set(extracted.keys()))
    if missing:
        raise RuntimeError(f"Failed to extract AME2020 targets: {missing}")

    full_payload = {
        "source": "AME2020 raw ASCII table",
        "doi": "10.1088/1674-1137/abddaf",
        "source_file": str(ame_path.relative_to(root_path)),
        "format_note": "Table-wide parsed layer for every AME2020 mass_1.mas20 row with readable binding energy per nucleon.",
        "parsed_table_count": len(full_data),
        "skipped_no_binding_count": skipped_no_binding,
        "data": full_data,
    }
    full_output_path.write_text(json.dumps(full_payload, indent=2, sort_keys=True), encoding="utf-8")

    subset_payload = {
        "source": "AME2020 raw ASCII table",
        "doi": "10.1088/1674-1137/abddaf",
        "source_file": str(ame_path.relative_to(root_path)),
        "format_note": "Parsed from mass_1.mas20 raw AME2020 table using fixed benchmark isotopes for topic 0.5.",
        "data": extracted,
        "provenance": {
            "line_numbers": source_lines,
            "raw_lines": line_texts,
        },
    }
    output_path.write_text(json.dumps(subset_payload, indent=2, sort_keys=True), encoding="utf-8")

    manifest_payload = {
        "source": "AME2020 raw ASCII table",
        "source_file": str(ame_path.relative_to(root_path)),
        "full_parsed_table": str(full_output_path.relative_to(root_path)),
        "validation_subset": str(output_path.relative_to(root_path)),
        "parsed_table_count": len(full_data),
        "validation_subset_count": len(extracted),
        "heavy_nucleus_gate": "A >= 16 and relative error < 15%",
        "light_nucleus_policy": "A < 16 remains diagnostic/excluded from the heavy-nucleus pass gate.",
        "validation_subset_labels": sorted(extracted.keys()),
        "skipped_no_binding_count": skipped_no_binding,
    }
    manifest_output_path.write_text(json.dumps(manifest_payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Wrote table-wide AME2020 parsed data to {full_output_path}")
    print(f"Wrote raw-derived AME2020 subset to {output_path}")
    print(f"Wrote AME2020 benchmark manifest to {manifest_output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
