"""Package the permitted Ding Fig. 1d intake as a bounded Topic 13 lane result."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/07_artifacts/provenance/ding_2022_source_mapping_audit.json"
MANIFEST_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_fig1d_digitized_manifest.json"
CSV_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_fig1d_digitized.csv"
FIGURE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_fig1.png"
MAPPING_REL = "docs/core/07_artifacts/archive/ding_2022_fig1d_series_mapping.json"
PACKAGE_REL = "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/matter_space_second_sound_source_package.json"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_ding_fig1d_normalized_source_lane_audit.json"


def load(rel: str) -> dict[str, Any]:
    value = json.loads((ROOT / rel).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def evidence(rel: str, summary: dict[str, Any]) -> dict[str, Any]:
    return {"path": rel, "sha256": sha256(rel), "summary": summary}


def main() -> int:
    audit = load(AUDIT_REL)
    manifest = load(MANIFEST_REL)
    mapping = load(MAPPING_REL)
    package = load(PACKAGE_REL)
    checks = audit.get("checks", {})
    required_checks = {
        "audit_pass": (
            audit.get("status") == "PASS"
            or (
                audit.get("status") == "BLOCKED"
                and checks.get("permitted_figure_numeric_route_ready") is True
                and checks.get("raw_author_numeric_source_present") is False
            )
        ),
        "route_ready": audit.get("normalized_comparison_route_ready") is True,
        "numeric_hash_matches_manifest": checks.get("numeric_hash_matches_manifest") is True,
        "figure_hash_matches_manifest": checks.get("figure_hash_matches_manifest") is True,
        "mapping_hash_matches_manifest": checks.get("mapping_hash_matches_manifest") is True,
        "row_identity_complete": checks.get("row_identity_complete") is True,
        "units_declared": checks.get("units_declared") is True,
        "uncertainty_declared": checks.get("uncertainty_declared") is True,
        "preprocessing_declared": checks.get("preprocessing_declared") is True,
        "license_declared": checks.get("license_declared") is True,
        "figure_route_ready": checks.get("permitted_figure_numeric_route_ready") is True,
        "printed_legend_mapping_closed": checks.get("color_to_period_mapping_closed") is True,
        "holdout_not_accessed": checks.get("holdout_not_accessed") is True,
        "numeric_fitting_disabled": checks.get("numeric_fitting_disabled") is True,
    }
    if not all(required_checks.values()):
        raise SystemExit(f"Ding normalized-source lane is not ready: {required_checks}")

    source = next(
        item for item in package.get("sources", []) if item.get("source_id") == "ding_2022_fig1d_digitized"
    )
    row_count = int(manifest.get("row_count", 0))
    artifact = {
        "schema_version": "t13-ding-fig1d-normalized-source-lane-v1",
        "artifact": "t13_ding_fig1d_normalized_source_lane_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_DING_FIGURE_DERIVED_NORMALIZED_SOURCE_LANE",
        "major_result": {
            "major_result_id": "T13_DING_FIG1D_NORMALIZED_SOURCE_LANE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE",
            "what_is_closed": [
                "permitted CC BY 4.0 Ding 2022 Fig. 1d numeric intake for normalized comparison",
                "printed-legend color-to-grating-period mapping",
                "row-level identity, units, deterministic preprocessing, extraction uncertainty, and input/output hashes",
                "explicit separation of figure-derived normalized rows from raw author PBTE inputs",
            ],
            "equation_or_mapping": {
                "standard_observable": "y_TTG(t;Lambda)=Delta_Tq(t;Lambda)/Delta_Tq(0;Lambda)",
                "digitized_signal": "normalized_signal(pixel_x) from Ding 2022 Fig. 1d",
                "series_mapping": "blue_trace=2.0 um; red_trace=3.0 um; green_trace=4.0 um",
                "uet_candidate_operator": "y_TTG^UET(t;Lambda)=Delta_Phi(t;Lambda)/Delta_Phi(0;Lambda)",
            },
            "units": {
                "time": "ps",
                "grating_period": "um",
                "normalized_signal": "dimensionless",
                "extraction_uncertainty": "normalized-signal half-width from pixel_y_half_width",
                "alpha_Phi_K": "K per normalized base Phi; not provided by this lane",
            },
            "derivation_class": "permitted figure digitization and printed-legend source mapping; not raw author-data reproduction",
            "observable": "Ding 2022 normalized transient thermal-grating response shape",
            "data_role": "FIGURE_DERIVED_NORMALIZED_COMPARISON_NOT_RAW_SOURCE",
            "evidence_artifacts": [
                evidence(AUDIT_REL, {"status": audit.get("status"), "row_count": audit.get("observed_package", {}).get("row_count")}),
                evidence(MANIFEST_REL, {"status": manifest.get("status"), "row_count": row_count}),
                evidence(CSV_REL, {"row_count": row_count, "sha256": manifest.get("output_sha256")}),
                evidence(FIGURE_REL, {"sha256": manifest.get("input_assets", [{}])[0].get("sha256")}),
                evidence(MAPPING_REL, {"status": mapping.get("status"), "series_to_grating_period_um": mapping.get("series_to_grating_period_um")}),
                evidence(PACKAGE_REL, {"source_id": source.get("source_id"), "status": source.get("status")}),
            ],
            "verification_status": "PASS_DING_FIGURE_DERIVED_NORMALIZED_SOURCE_LANE",
            "open_blockers": [
                "raw_author_PBTE_inputs_and_numeric_C_src(T)_not_captured",
                "figure_extraction_uncertainty_is_not_experimental_error_bar",
                "base_Phi_to_Delta_u_ph_mapping_missing",
                "independent_alpha_Phi_K_calibration_missing",
                "Xie_2026_holdout_not_consumed",
            ],
            "dependency_unlocked": "normalized comparison source lane only; no alpha, thermal prediction, Full Topic 13, Core, or Gravity unlock",
            "claim_boundary": "This closes a permitted figure-derived normalized-source lane only. It is not raw author numeric data, a C_src(T) reconstruction, a Phi calibration, an external validation, or a temperature prediction.",
        },
        "verification": {
            "checks": required_checks,
            "row_count": row_count,
            "source_locator": audit.get("source_locator"),
            "preprocessing": manifest.get("preprocessing"),
            "uncertainty_policy": manifest.get("uncertainty_policy"),
            "row_identity": manifest.get("row_identity"),
            "holdout_consumed": False,
            "numeric_fitting_allowed": False,
            "raw_author_numeric_source_present": False,
        },
        "claim_promotion": False,
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "major_result_id": artifact["major_result"]["major_result_id"], "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
