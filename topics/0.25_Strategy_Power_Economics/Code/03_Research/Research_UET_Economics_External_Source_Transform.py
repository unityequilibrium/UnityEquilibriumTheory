"""Acquire and normalize the non-FRED primary sources for Topic 0.25.

The script keeps provider raw files in the shared external cache, creates only
declared research subsets, and writes a transformation manifest that ties every
normalized value back to its source table and hash.
"""

from __future__ import annotations

import argparse
import csv
import math
import shutil
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from economic_hardening_common import RAW_ROOT, RESEARCH_DATA, relative, sha256, utc_now, write_csv, write_json


BEA_SECTION_1 = "https://apps.bea.gov/national/FixedAssets/Release/xls/Section1All_xls.xlsx"
BEA_SECTION_2 = "https://apps.bea.gov/national/FixedAssets/Release/xls/Section2All_xls.xlsx"
EIA_TABLE_1_3 = "https://www.eia.gov/totalenergy/data/browser/csv.php?tbl=T01.03&freq=A"
EPI_PAGE = "https://data.epi.org/productivity/productivity_levels/line/year/national/real_dollars_per_hour_2024/productivity_pay?dateString=2024-01-01&highlightedLines=compensation_productivity_pay&highlightedLines=productivity_productivity_pay&timeEnd=2024-01-01&timeStart=1948-01-01"
NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PACKAGE = "http://schemas.openxmlformats.org/package/2006/relationships"


def download(url: str, path: Path, referer: str | None = None) -> None:
    headers = {"User-Agent": "UET-Topic-0.25-Research/1.0"}
    if referer:
        headers["Referer"] = referer
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=90) as response:
        path.write_bytes(response.read())


def column_index(reference: str) -> int:
    letters = "".join(character for character in reference if character.isalpha())
    output = 0
    for letter in letters:
        output = output * 26 + ord(letter.upper()) - ord("A") + 1
    return output


def shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join(node.text or "" for node in item.iter(f"{{{NS_MAIN}}}t")) for item in root.findall(f"{{{NS_MAIN}}}si")]


def workbook_sheets(path: Path) -> dict[str, list[dict[int, str]]]:
    with zipfile.ZipFile(path) as archive:
        strings = shared_strings(archive)
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in relationships.findall(f"{{{NS_PACKAGE}}}Relationship")}
        result = {}
        for sheet in workbook.find(f"{{{NS_MAIN}}}sheets").findall(f"{{{NS_MAIN}}}sheet"):
            relation = sheet.attrib[f"{{{NS_REL}}}id"]
            target = "xl/" + targets[relation].lstrip("/")
            root = ET.fromstring(archive.read(target))
            rows = []
            for row in root.findall(f".//{{{NS_MAIN}}}sheetData/{{{NS_MAIN}}}row"):
                values = {}
                for cell in row.findall(f"{{{NS_MAIN}}}c"):
                    raw = cell.find(f"{{{NS_MAIN}}}v")
                    value = raw.text if raw is not None else ""
                    if cell.attrib.get("t") == "s" and value:
                        value = strings[int(value)]
                    values[column_index(cell.attrib["r"])] = value
                rows.append(values)
            result[sheet.attrib["name"]] = rows
        return result


def bea_series(workbook: dict[str, list[dict[int, str]]], sheet_name: str, code: str) -> dict[int, float]:
    rows = workbook[sheet_name]
    header = next(row for row in rows if row.get(1) == "Line")
    years = {column: int(value) for column, value in header.items() if column >= 4 and value.isdigit()}
    row = next(row for row in rows if row.get(3) == code)
    result = {}
    for column, year in years.items():
        try:
            result[year] = float(row[column])
        except (KeyError, ValueError):
            continue
    return result


def build_bea(section1: Path, section2: Path, target: Path) -> dict:
    book1 = workbook_sheets(section1)
    book2 = workbook_sheets(section2)
    equipment = bea_series(book1, "FAAt102-A", "kcntotl1eq00")
    structures = bea_series(book1, "FAAt102-A", "kcntotl1st00")
    government = bea_series(book1, "FAAt102-A", "kcgtotl1es00")
    ip_investment = bea_series(book2, "FAAt208-A", "icntotl1ip00")
    rows = []
    for year in range(1959, 2025):
        if any(year not in series or series[year] <= 0 for series in [equipment, structures, government, ip_investment]):
            continue
        rows.append(
            {
                "Year": year,
                "ip_product_quantity_index_2017_100": ip_investment[year],
                "private_tangible_fixed_assets_quantity_index_2017_100": math.sqrt(equipment[year] * structures[year]),
                "government_fixed_assets_quantity_index_2017_100": government[year],
            }
        )
    write_csv(target, rows, list(rows[0]) if rows else ["Year", "ip_product_quantity_index_2017_100", "private_tangible_fixed_assets_quantity_index_2017_100", "government_fixed_assets_quantity_index_2017_100"])
    return {
        "normalized_path": relative(target),
        "normalized_sha256": sha256(target),
        "coverage": [rows[0]["Year"], rows[-1]["Year"]] if rows else None,
        "selected_series": {
            "ip_product_quantity_index_2017_100": "BEA Fixed Assets Table 2.8, code icntotl1ip00: chain-type quantity index for investment in nonresidential intellectual property products (2017=100)",
            "private_tangible_fixed_assets_quantity_index_2017_100": "geometric composite of BEA Fixed Assets Table 1.2 codes kcntotl1eq00 (nonresidential equipment) and kcntotl1st00 (nonresidential structures), both chain-type quantity indexes (2017=100)",
            "government_fixed_assets_quantity_index_2017_100": "BEA Fixed Assets Table 1.2, code kcgtotl1es00: chain-type quantity index for government fixed assets (2017=100)",
        },
    }


def build_eia(source: Path, target: Path) -> dict:
    rows = []
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("MSN") != "TETCBUS" or not row.get("YYYYMM", "").endswith("13"):
                continue
            year = int(row["YYYYMM"][:4])
            if 1959 <= year <= 2024:
                rows.append({"Year": year, "primary_energy_quadrillion_btu": float(row["Value"])})
    rows.sort(key=lambda row: row["Year"])
    write_csv(target, rows, ["Year", "primary_energy_quadrillion_btu"])
    return {
        "normalized_path": relative(target),
        "normalized_sha256": sha256(target),
        "coverage": [rows[0]["Year"], rows[-1]["Year"]] if rows else None,
        "selected_series": {"primary_energy_quadrillion_btu": "EIA Monthly Energy Review Table 1.3 annual observation: TETCBUS, Total Primary Energy Consumption, Quadrillion Btu"},
    }


def build_epi(source: Path, target: Path) -> dict:
    raw_rows = []
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if len(fields) != 3 or fields[0] != "date":
            raise ValueError("EPI export must be the provider-generated three-column annual chart CSV.")
        for row in reader:
            raw_rows.append((int(row[fields[0]][:4]), float(row[fields[1]]), float(row[fields[2]])))
    by_year = {year: (productivity, compensation) for year, productivity, compensation in raw_rows}
    if 1979 not in by_year:
        raise ValueError("EPI export does not include 1979, the declared base year.")
    base_productivity, base_compensation = by_year[1979]
    rows = [
        {
            "Year": year,
            "net_productivity_index": 100.0 * productivity / base_productivity,
            "epi_compensation_index": 100.0 * compensation / base_compensation,
        }
        for year, productivity, compensation in raw_rows
        if 1948 <= year <= 2024
    ]
    write_csv(target, rows, ["Year", "net_productivity_index", "epi_compensation_index"])
    return {
        "normalized_path": relative(target),
        "normalized_sha256": sha256(target),
        "coverage": [rows[0]["Year"], rows[-1]["Year"]] if rows else None,
        "selected_series": {"net_productivity_index": fields[1], "epi_compensation_index": fields[2]},
        "base_year": 1979,
    }


def raw_record(path: Path, url: str, role: str) -> dict:
    return {"path": relative(path), "sha256": sha256(path), "bytes": path.stat().st_size, "source_url": url, "role": role}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vintage", default="2026-07-12")
    parser.add_argument("--refresh-official", action="store_true", help="Download the BEA and EIA provider files.")
    parser.add_argument("--epi-csv", type=Path, required=True, help="Provider-generated EPI chart CSV downloaded through the EPI Data Library.")
    args = parser.parse_args()
    bea_dir = RAW_ROOT / "bea" / args.vintage
    eia_dir = RAW_ROOT / "eia" / args.vintage
    epi_dir = RAW_ROOT / "epi" / args.vintage
    section1 = bea_dir / "Section1All_xls.xlsx"
    section2 = bea_dir / "Section2All_xls.xlsx"
    eia_raw = eia_dir / "EIA_Table_1_3_annual.csv"
    epi_raw = epi_dir / "EPI_productivity_pay_levels_provider_export.csv"
    if args.refresh_official:
        download(BEA_SECTION_1, section1)
        download(BEA_SECTION_2, section2)
        download(EIA_TABLE_1_3, eia_raw, referer="https://www.eia.gov/totalenergy/data/browser/?tbl=T01.03")
    if not args.epi_csv.exists():
        raise FileNotFoundError(f"EPI source export not found: {args.epi_csv}")
    epi_raw.parent.mkdir(parents=True, exist_ok=True)
    if args.epi_csv.resolve() != epi_raw.resolve():
        shutil.copyfile(args.epi_csv, epi_raw)
    for path in [section1, section2, eia_raw, epi_raw]:
        if not path.exists():
            raise FileNotFoundError(f"Required raw source is absent: {path}")
    bea = build_bea(section1, section2, bea_dir / "bea_fixed_assets_annual.csv")
    eia = build_eia(eia_raw, eia_dir / "eia_primary_energy_annual.csv")
    epi = build_epi(epi_raw, epi_dir / "epi_productivity_pay.csv")
    manifest = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "generated_at_utc": utc_now(),
        "vintage": args.vintage,
        "raw_sources": [
            raw_record(section1, BEA_SECTION_1, "BEA Fixed Assets Table 1.2 extraction"),
            raw_record(section2, BEA_SECTION_2, "BEA Fixed Assets Table 2.8 extraction"),
            raw_record(eia_raw, EIA_TABLE_1_3, "EIA Table 1.3 annual TETCBUS extraction"),
            raw_record(epi_raw, EPI_PAGE, "EPI Data Library provider-generated chart CSV"),
        ],
        "normalized_outputs": {"bea_fixed_assets": bea, "eia_primary_energy": eia, "epi_productivity_pay": epi},
        "claim_boundary": "The manifest documents source extraction and normalization only. It does not establish an economic mechanism, causal effect, or policy result.",
    }
    write_json(RESEARCH_DATA / "uet_us_economics_transform_manifest.json", manifest)
    print("UET 0.25 external source transform")
    print(f"  BEA normalized coverage: {bea['coverage']}")
    print(f"  EIA normalized coverage: {eia['coverage']}")
    print(f"  EPI normalized coverage: {epi['coverage']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
