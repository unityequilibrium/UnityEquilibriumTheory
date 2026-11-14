"""Keep energy-throughput history separate from literal fuel-energy-density claims."""

from __future__ import annotations

from economic_hardening_common import (
    ARTIFACT_DIR,
    SOURCE_MANIFEST,
    as_float,
    load_json,
    read_csv,
    source_path,
    utc_now,
    write_json,
)


ARTIFACT = ARTIFACT_DIR / "0_25_energy_density_audit.json"


def historical_transition(path) -> dict:
    if path is None:
        return {"status": "BLOCKED", "blocker": "EIA historical 1776-1945 annual export is absent."}
    rows = []
    for raw in read_csv(path):
        year = as_float(raw.get("Year"))
        wood = as_float(raw.get("wood_quadrillion_btu"))
        coal = as_float(raw.get("coal_quadrillion_btu"))
        petroleum = as_float(raw.get("petroleum_quadrillion_btu"))
        if None in {year, wood, coal, petroleum}:
            continue
        total = wood + coal + petroleum
        if total <= 0:
            continue
        rows.append({"year": int(year), "total": total, "wood_share": wood / total, "fossil_share": (coal + petroleum) / total})
    if len(rows) < 3:
        return {"status": "INSUFFICIENT_ROWS", "n": len(rows), "blocker": "Historical source file did not contain the declared comparable energy columns."}
    return {
        "status": "DESCRIPTIVE_COMPLETE",
        "n": len(rows),
        "first_year": rows[0]["year"],
        "last_year": rows[-1]["year"],
        "first_fossil_share": rows[0]["fossil_share"],
        "last_fossil_share": rows[-1]["fossil_share"],
        "first_total_quadrillion_btu": rows[0]["total"],
        "last_total_quadrillion_btu": rows[-1]["total"],
        "interpretation": "This is a descriptive source-mix and energy-throughput transition. It is not a literal energy-density estimate and not a macroeconomic causal test.",
    }


def current_energy_input(path) -> dict:
    if path is None:
        return {"status": "BLOCKED", "blocker": "EIA primary-energy annual export is absent."}
    years = []
    for raw in read_csv(path):
        year = as_float(raw.get("Year"))
        energy = as_float(raw.get("primary_energy_quadrillion_btu"))
        if year is not None and energy is not None and energy > 0:
            years.append((int(year), energy))
    return {"status": "READY_FOR_PANEL" if years else "INSUFFICIENT_ROWS", "n": len(years), "first_year": years[0][0] if years else None, "last_year": years[-1][0] if years else None}


def main() -> int:
    manifest = load_json(SOURCE_MANIFEST)
    history = historical_transition(source_path(manifest, "eia_energy_history"))
    primary = current_energy_input(source_path(manifest, "eia_primary_energy"))
    literal_gate = {
        "gate": "energy_density_definition_gate",
        "status": "BLOCKED",
        "controller_reason": "The available source plan measures energy consumption, not comparable energy density across wood, coal, petroleum, nuclear, and renewable sources.",
        "required_before_literal_claim": ["source-locked heating-value table", "common physical basis such as MJ/kg", "declared treatment or exclusion of nuclear, hydro, wind, and solar", "unit conversion audit"],
        "blocked_claims": ["energy-density leap proved", "literal fuel-density mechanism validated", "energy transition causally explains resource growth"],
    }
    artifact = {
        "schema_version": "1.0",
        "topic": "0.25_Strategy_Power_Economics",
        "status": "WARN" if history.get("status") == "BLOCKED" or primary.get("status") == "BLOCKED" else "DESCRIPTIVE_COMPLETE",
        "generated_at_utc": utc_now(),
        "historical_energy_transition": history,
        "postwar_primary_energy_input": primary,
        "energy_density_definition_gate": literal_gate,
        "claim_boundary": "The lane may describe a source-locked energy transition. It cannot prove a literal energy-density leap or a UET macroeconomic mechanism.",
    }
    write_json(ARTIFACT, artifact)
    print(f"Energy-density audit: {artifact['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
