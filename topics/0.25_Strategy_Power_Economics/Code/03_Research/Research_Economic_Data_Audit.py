"""Topic 0.25 verification: economic data and market time-series audit."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path


def bootstrap_repo() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("Repository root with docs/core was not found.")


ROOT = bootstrap_repo()
TOPIC = ROOT / "docs" / "topics" / "0.25_Strategy_Power_Economics"
DATA = TOPIC / "Data"
ARTIFACT = TOPIC / "Result" / "artifacts" / "0_25_strategy_power_economics_verification.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yahoo_close(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        next(reader, None)  # ticker row
        next(reader, None)  # Date placeholder row
        close_index = header.index("Close")
        for raw in reader:
            if not raw or len(raw) <= close_index:
                continue
            try:
                close = float(raw[close_index])
            except ValueError:
                continue
            if math.isfinite(close) and close > 0:
                rows.append({"date": raw[0], "close": close})
    return rows


def returns(closes: list[float]) -> list[float]:
    return [math.log(b / a) for a, b in zip(closes, closes[1:]) if a > 0 and b > 0]


def pearson(a: list[float], b: list[float]) -> float | None:
    n = min(len(a), len(b))
    if n < 3:
        return None
    x = a[-n:]
    y = b[-n:]
    mx = sum(x) / n
    my = sum(y) / n
    vx = sum((v - mx) ** 2 for v in x)
    vy = sum((v - my) ** 2 for v in y)
    if vx <= 0 or vy <= 0:
        return None
    return sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / math.sqrt(vx * vy)


def series_metrics(name: str, path: Path) -> dict:
    rows = load_yahoo_close(path)
    closes = [row["close"] for row in rows]
    rets = returns(closes)
    annualized_volatility = statistics.pstdev(rets) * math.sqrt(252) if len(rets) > 1 else None
    total_return = closes[-1] / closes[0] - 1.0 if len(closes) > 1 else None
    return {
        "name": name,
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(path),
        "row_count": len(rows),
        "first_date": rows[0]["date"] if rows else None,
        "last_date": rows[-1]["date"] if rows else None,
        "first_close": closes[0] if closes else None,
        "last_close": closes[-1] if closes else None,
        "total_return": total_return,
        "annualized_volatility": annualized_volatility,
        "returns": rets,
    }


def economy_metrics(path: Path) -> dict:
    data = load_json(path)
    economies = data.get("Economies", {})
    gini_values = [float(item["Gini"]) for item in economies.values() if "Gini" in item]
    gdp_values = [float(item["GDP_PPP_USD"]) for item in economies.values() if "GDP_PPP_USD" in item]
    pop_values = [float(item["Population"]) for item in economies.values() if "Population" in item]
    return {
        "source": data.get("Source", "unspecified"),
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256(path),
        "economy_count": len(economies),
        "gini_min": min(gini_values) if gini_values else None,
        "gini_max": max(gini_values) if gini_values else None,
        "gdp_ppp_total_usd": sum(gdp_values),
        "population_total": sum(pop_values),
        "world_total": economies.get("World_Total", {}),
    }


def main() -> int:
    series = [
        series_metrics("SP500", DATA / "03_Research" / "SP500_yahoo_real.csv"),
        series_metrics("Gold", DATA / "03_Research" / "Gold_yahoo_real.csv"),
        series_metrics("Bitcoin", DATA / "03_Research" / "Bitcoin_yahoo_real.csv"),
    ]
    economy = economy_metrics(DATA / "Global_Economy_2024.json")
    snapshot_path = DATA / "03_Research" / "daily_economic_snapshot.json"
    snapshot = load_json(snapshot_path)

    sp500 = next(item for item in series if item["name"] == "SP500")
    gold = next(item for item in series if item["name"] == "Gold")
    bitcoin = next(item for item in series if item["name"] == "Bitcoin")

    correlations = {
        "sp500_gold_return_corr": pearson(sp500["returns"], gold["returns"]),
        "sp500_bitcoin_return_corr": pearson(sp500["returns"], bitcoin["returns"]),
        "gold_bitcoin_return_corr": pearson(gold["returns"], bitcoin["returns"]),
    }

    thresholds = {
        "min_rows_per_market_series": 2500,
        "gini_range_min": 0.0,
        "gini_range_max": 100.0,
        "require_snapshot_source_url": True,
        "require_economy_source_url_or_doi": True,
    }

    checks = {
        "market_rows_ok": all(item["row_count"] >= thresholds["min_rows_per_market_series"] for item in series),
        "gini_range_ok": economy["gini_min"] is not None
        and economy["gini_max"] is not None
        and economy["gini_min"] >= thresholds["gini_range_min"]
        and economy["gini_max"] <= thresholds["gini_range_max"],
        "snapshot_has_source_url": "url" in snapshot or "URL" in snapshot or "doi" in snapshot or "DOI" in snapshot,
        "economy_has_source_url": "url" in economy["source"].lower() or "doi" in economy["source"].lower(),
    }

    blockers = []
    if not checks["market_rows_ok"]:
        blockers.append("At least one market time series is too short for the provisional history-length gate.")
    if not checks["gini_range_ok"]:
        blockers.append("Global economy Gini values fall outside the declared 0-100 unit convention.")
    if not checks["snapshot_has_source_url"]:
        blockers.append("daily_economic_snapshot.json has no upstream URL/DOI; source is a local gateway label.")
    if not checks["economy_has_source_url"]:
        blockers.append("Global_Economy_2024.json names World Bank/IMF references but does not record a URL/DOI.")

    status = "PASS" if all(checks.values()) else "WARN"

    for item in series:
        item.pop("returns", None)

    artifact = {
        "schema_version": "1.1",
        "topic": "0.25_Strategy_Power_Economics",
        "status": status,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "command": "python docs/topics/0.25_Strategy_Power_Economics/Code/03_Research/Research_Economic_Data_Audit.py",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "claim_class": "C - internal economic data integrity and market diagnostics benchmark",
        "formula_ids": [
            "EC25-LOG-RETURN",
            "EC25-ANNUALIZED-VOLATILITY",
            "EC25-RETURN-CORRELATION",
            "EC25-GINI-SANITY",
        ],
        "inputs": [
            {key: item[key] for key in ("name", "path", "sha256", "row_count", "first_date", "last_date")}
            for item in series
        ]
        + [
            {
                "name": "Global_Economy_2024",
                "path": economy["path"],
                "sha256": economy["sha256"],
                "source": economy["source"],
            },
            {
                "name": "daily_economic_snapshot",
                "path": str(snapshot_path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(snapshot_path),
                "source": snapshot.get("source", "unspecified"),
                "timestamp": snapshot.get("timestamp"),
            },
        ],
        "threshold": thresholds,
        "checks": checks,
        "blockers": blockers,
        "market_metrics": series,
        "economy_metrics": economy,
        "correlations": correlations,
        "snapshot": snapshot,
        "limitations": [
            "This artifact validates local data integrity and descriptive market/economy diagnostics only.",
            "It does not prove strategic superiority, social stabilization, Nash-equilibrium improvement, or policy causality.",
            "Upstream provenance for the economy and daily snapshot data remains below archival standard.",
        ],
    }

    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")

    print("UET 0.25 economic data audit")
    print(f"  status: {status}")
    for item in series:
        print(
            f"  {item['name']}: rows={item['row_count']}, range={item['first_date']}..{item['last_date']}, "
            f"vol={item['annualized_volatility']:.4f}"
        )
    print(f"  gini range: {economy['gini_min']}..{economy['gini_max']}")
    print(f"  artifact: {ARTIFACT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
