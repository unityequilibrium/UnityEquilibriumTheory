"""Test Card T021 prediction method: lighting technology succession, stage 1 of test D (topic 0.25).

Layer 3 with several resources (AI translation of the author's statement of 2026-11-17): a technology that
replaces another and survives should not need more of every resource per unit of service. Stage 1 needs no
exchange rate between resources: it only asks whether any historical successor was worse in ALL resources.

Resources per 1,000 lumen-hours (Nordhaus 1997, Tables 1.3 and 1.6):
    energy  E = 1 / (lumens per watt)          at the device, as tabulated
    time    T = hours of work per 1,000 lumen-hours (labor price of light)

Each pair below is fixed before the run: incumbent row -> successor row, the successor taken at its first
appearance in the table and the incumbent at the closest row at or before that date (same experiment when
Silliman 1855 measured both). Within-family improvements are not pairs.

Classification of a pair with relative tolerance tol = 0.05 on each resource:
    DOMINATES   successor better in one resource and not worse in the other
    TRADE_OFF   successor better in one resource, worse in the other
    WORSE_BOTH  successor worse in both
    TIE         no difference beyond tol in either
PASS if no pair is WORSE_BOTH. FAILED if one or more pairs are WORSE_BOTH.
Reported, not deciding: the counts of each class; for pairs where the successor is electric, the break-even
power-plant efficiency eta* = (incumbent lm/W) / (electric lm/W) below which the successor would use more
primary energy; for each TRADE_OFF pair, the first later successor-family row that dominates the incumbent's row.

Do not run against the data before the card is APPROVED by the author.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/data/external/economics/lighting/nordhaus1997_lighting.csv"
MANIFEST = ROOT / "docs/standard/data_manifest.json"
CARD = ROOT / "docs/standard/tests/T021.json"
DATA_ID = "NORDHAUS1997_LIGHTING"
TOL = 0.05
BTU_WH = 0.29307107  # 1 Btu in watt-hours

# (incumbent row_id, successor row_id, label). Fixed before the run; AI choice from Nordhaus Table 1.1 and text.
PAIRS = [
    ("babylonian_lamp", "candle_tallow_1800", "sesame-oil lamp -> tallow candle"),
    ("candle_tallow_1830", "lamp_whale_oil", "tallow candle -> whale-oil lamp"),
    ("candle_tallow_1800", "gas_early_1827", "tallow candle -> town gas"),
    ("lamp_sperm_oil_1855", "kerosene_silliman_1855", "sperm/whale-oil lamp -> kerosene (Silliman 1855)"),
    ("kerosene_1880", "electric_edison_1883", "kerosene -> Edison electric"),
    ("gas_early_1880", "electric_edison_1883", "town gas -> Edison electric"),
    ("electric_1990", "electric_cfl_1992", "incandescent -> compact fluorescent"),
]


def classify(e_old: float, t_old: float, e_new: float, t_new: float, tol: float = TOL) -> str:
    """Compare resource use per unit service (lower is better) with a relative tolerance."""
    def sign(old: float, new: float) -> int:
        if new < old * (1.0 - tol):
            return 1  # better
        if new > old * (1.0 + tol):
            return -1  # worse
        return 0
    se, st = sign(e_old, e_new), sign(t_old, t_new)
    if se == -1 and st == -1:
        return "WORSE_BOTH"
    if (se == 1 and st == -1) or (se == -1 and st == 1):
        return "TRADE_OFF"
    if se == 1 or st == 1:
        return "DOMINATES"
    return "TIE"


def load_rows(path: Path = DATA) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return {r["row_id"]: r for r in csv.DictReader(fh)}


def resources(row: dict[str, str]) -> tuple[float, float]:
    """Energy (W per lumen, i.e. Wh per lumen-hour) and labor hours per 1,000 lumen-hours."""
    return 1.0 / float(row["lumens_per_watt"]), float(row["labor_hours_per_1000lmh"])


def _sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def run() -> dict:
    card = json.loads(CARD.read_text(encoding="utf-8"))
    if card["status"] not in ("APPROVED", "CLOSED"):
        raise SystemExit("T021 is not APPROVED by the author; refusing to run against the data.")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = manifest["entries"] if isinstance(manifest, dict) else manifest
    entry = next(e for e in entries if e["data_id"] == DATA_ID)
    if _sha256_lf(DATA) != entry["sha256"]:
        raise SystemExit("data file does not match the manifest hash")
    rows = load_rows()
    out = []
    for old_id, new_id, label in PAIRS:
        e0, t0 = resources(rows[old_id])
        e1, t1 = resources(rows[new_id])
        cls = classify(e0, t0, e1, t1)
        item = {"pair": label, "class": cls, "energy_ratio_new_over_old": round(e1 / e0, 4),
                "labor_ratio_new_over_old": round(t1 / t0, 4)}
        if rows[new_id]["family"] == "electric lamp":
            item["eta_star_plant_efficiency"] = round(float(rows[old_id]["lumens_per_watt"])
                                                      / float(rows[new_id]["lumens_per_watt"]), 4)
        if cls == "TRADE_OFF":
            fam, y0 = rows[new_id]["family"], float(rows[new_id]["year"])
            later = sorted((float(r["year"]), rid) for rid, r in rows.items()
                           if r["family"] == fam and r["year"] and float(r["year"]) >= y0
                           and r["labor_hours_per_1000lmh"])
            item["first_dominating_successor_row"] = next(
                (rid for _, rid in later if classify(e0, t0, *resources(rows[rid])) == "DOMINATES"), None)
        out.append(item)
    counts = {c: sum(1 for i in out if i["class"] == c) for c in ("DOMINATES", "TRADE_OFF", "WORSE_BOTH", "TIE")}
    return {"pairs": out, "counts": counts, "outcome": "FAIL" if counts["WORSE_BOTH"] else "PASS"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
