"""Audit the He-4 SVP equilibrium physical-anchor source package."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.he4_svp_reference import (  # noqa: E402
    SOURCE_DOI,
    SOURCE_SNAPSHOT_BYTES,
    SOURCE_SNAPSHOT_SHA256,
    SOURCE_URL,
    T_LAMBDA_K,
    calibration_grid,
)


PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "he4_svp_o2_physical_anchor_source_package.json"
)
MODULE = ROOT / "docs/core/he4_svp_reference.py"
OUT = ROOT / "docs/core/artifacts/t13_he4_svp_physical_anchor_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(left: float, right: float) -> bool:
    return math.isclose(float(left), float(right), rel_tol=1.0e-12, abs_tol=1.0e-12)


def main() -> int:
    package = load(PACKAGE)
    expected_rows = calibration_grid()
    reported_rows = package.get("rows", [])
    reported_by_id = {row.get("row_id"): row for row in reported_rows}
    expected_by_id = {row["row_id"]: row for row in expected_rows}
    fields = (
        "temperature_K",
        "total_density_kg_m3",
        "superfluid_density_kg_m3",
        "normal_density_kg_m3",
        "superfluid_fraction",
    )
    row_residuals = {
        row_id: {
            field: abs(float(reported_by_id[row_id][field]) - float(expected[field]))
            for field in fields
        }
        for row_id, expected in expected_by_id.items()
        if row_id in reported_by_id
    }
    checks = {
        "source_doi_matches_transcription": package["source"]["doi"] == SOURCE_DOI,
        "source_url_matches_transcription": package["source"]["interactive_locator"] == SOURCE_URL,
        "source_snapshot_hash_matches": package["source"]["interactive_snapshot_sha256"] == SOURCE_SNAPSHOT_SHA256,
        "source_snapshot_bytes_match": package["source"]["interactive_snapshot_bytes"] == SOURCE_SNAPSHOT_BYTES,
        "lambda_temperature_matches": close(package["material_state"]["lambda_temperature_K"], T_LAMBDA_K),
        "row_ids_are_unique": len(reported_by_id) == len(reported_rows),
        "preregistered_grid_complete": set(reported_by_id) == set(expected_by_id),
        "rows_recompute_from_source_transcription": bool(row_residuals)
        and max(value for row in row_residuals.values() for value in row.values()) <= 1.0e-12,
        "density_ledger_closes": all(
            close(row["total_density_kg_m3"], row["superfluid_density_kg_m3"] + row["normal_density_kg_m3"])
            for row in reported_rows
        ),
        "fractions_are_physical": all(0.0 < float(row["superfluid_fraction"]) < 1.0 for row in reported_rows),
        "temperature_grid_excludes_lambda_endpoint": all(float(row["temperature_K"]) < T_LAMBDA_K for row in reported_rows),
        "mapping_remains_open": package["observable_contract"]["mapping_status"] == "OPEN_INDEPENDENT_FIELD_NORMALIZATION",
        "uncertainty_gap_is_explicit": package["uncertainty_contract"]["status"] == "OPEN_PROPERTY_LEVEL_SOURCE_UNCERTAINTY_EXTRACTION",
        "no_numeric_uncertainty_consumed": package["uncertainty_contract"]["numeric_uncertainty_consumed"] is False,
        "holdout_not_accessed": package["holdout_policy"]["xie_2026_accessed"] is False,
        "target_not_used": package["holdout_policy"]["target_curve_used"] is False,
        "no_fit_or_tuning": package["holdout_policy"]["fit_or_tuning_used"] is False,
        "no_threshold_adjustment": package["holdout_policy"]["threshold_adjustment_used"] is False,
    }
    status = "PASS_HE4_EQUILIBRIUM_SOURCE_ANCHOR_UNCERTAINTY_OPEN" if all(checks.values()) else "FAIL_HE4_SOURCE_AUDIT"
    report = {
        "schema_version": "t13-he4-svp-physical-anchor-audit-v1",
        "artifact": "t13_he4_svp_physical_anchor_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_HE4_SVP_O2_PHYSICAL_ANCHOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
            "what_is_closed": "A source-locked He-4 SVP equilibrium grid for total density, superfluid density, normal density, and superfluid fraction, with deterministic row identity and no holdout access.",
            "equation_or_mapping": "rho_n = rho - rho_s; candidate only: Delta(rho_s/rho) = Z_Phi Delta_Phi",
            "units": package["units"],
            "derivation_class": "SOURCE_TRANSCRIPTION_AND_EQUILIBRIUM_IDENTITY",
            "observable": "rho, rho_s, rho_n, and rho_s/rho at He-4 SVP",
            "data_role": "CALIBRATION_REFERENCE_CANDIDATE_NOT_TARGET_DATA",
            "evidence_artifacts": [
                {"path": str(PACKAGE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(PACKAGE)},
                {"path": str(MODULE.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(MODULE)},
            ],
            "verification_status": status,
            "open_blockers": [
                "property_level_source_uncertainty_not_yet_extracted",
                "independent_Z_Phi_field_normalization_missing",
                "SI_energy_and_length_scale_mapping_missing",
                "physical_transport_coefficient_not_closed",
            ],
            "dependency_unlocked": "He-4/O(2) physical calibration lane may proceed to field-normalization and SI-scale design; no Core-ready promotion yet.",
            "claim_boundary": package["claim_boundary"],
        },
        "source_identity": package["source"],
        "material_state": package["material_state"],
        "rows": reported_rows,
        "row_recompute_absolute_residuals": row_residuals,
        "checks": checks,
        "controlling_blocker": "independent_Z_Phi_and_property_uncertainty_missing",
        "next_controller": "Source-lock property-level uncertainty, then preregister a thermodynamic field-normalization condition for Z_Phi without TTG or Xie 2026 target access.",
        "claim_boundary": package["claim_boundary"],
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/")}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
