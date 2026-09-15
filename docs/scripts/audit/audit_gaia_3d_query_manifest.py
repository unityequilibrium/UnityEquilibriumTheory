"""Audit the preregistered Gaia 3D query/holdout contract.

This verifier confirms that the query and split policy are explicit before data
intake. It intentionally remains blocked for numeric or physical claims until
the returned table is archived, hashed, and passed through selection, distance,
and uncertainty audits.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "docs/data/external/astronomy/gaia_edr3_gcns/2026-08-08/query_and_holdout_manifest.json"
SOURCE_PATH = ROOT / "docs/data/external/astronomy/gaia_edr3_gcns/2026-08-08/source_manifest.json"
OUTPUT_PATH = ROOT / "docs/core/07_artifacts/provenance/gaia_3d_query_manifest_verification.json"


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def build_artifact() -> dict[str, Any]:
    manifest = _load(MANIFEST_PATH)
    source = _load(SOURCE_PATH)
    tables = {row.get("table") for row in manifest.get("candidate_tables", [])}
    fields = {(row.get("table"), row.get("field")) for row in manifest.get("requested_fields", [])}
    bias = manifest.get("parallax_bias_policy", {})
    distance = manifest.get("distance_policy", {})
    selection = manifest.get("selection_policy", {})
    split = manifest.get("holdout_split", {})
    local = manifest.get("local_data", {})
    fit = manifest.get("fit_policy", {})

    gates = {
        "source_identity_and_upstream_manifest_present": bool(
            manifest.get("source_id")
            and manifest.get("source_identity", {}).get("gaia_archive_url")
            and source.get("source_id") == manifest.get("source_id")
        ),
        "primary_table_and_identity_fields_declared": (
            "gaiadr3.gaia_source" in tables
            and ("gaiadr3.gaia_source", "source_id") in fields
        ),
        "distance_fields_and_units_declared": all(
            ("gaiadr3.gaia_source", field) in fields
            for field in ("ra", "dec", "parallax", "parallax_error")
        ),
        "parallax_bias_policy_is_not_silent": (
            bias.get("single_constant_correction_allowed") is False
            and bias.get("documented_global_reference_bias_mas") == -0.017
            and len(bias.get("required_correction_inputs", [])) == 3
            and bias.get("raw_and_corrected_columns_required") is True
        ),
        "distance_estimator_policy_is_explicit": (
            distance.get("status") == "PRE_REGISTERED_POLICY_REQUIRED"
            and "reciprocal parallax" in distance.get("forbidden_default", "")
            and len(distance.get("required_record", [])) >= 4
        ),
        "mass_density_non_equivalence_is_declared": (
            manifest.get("coordinate_and_density_policy", {}).get("source_counts_are_not_mass_density") is True
            and manifest.get("coordinate_and_density_policy", {}).get("mass_realization_status") == "OPEN"
        ),
        "selection_gate_is_open_before_intake": (
            selection.get("status") == "OPEN_BEFORE_DATA_INTAKE"
            and len(selection.get("required_items", [])) >= 4
        ),
        "calibration_holdout_split_is_disjoint_and_unconsumed": (
            split.get("status") == "LOCKED_BEFORE_DATA_INTAKE"
            and split.get("holdout_consumed") is False
            and split.get("calibration_condition") != split.get("holdout_condition")
        ),
        "fit_and_tuning_are_blocked": (
            fit.get("numeric_fitting_allowed") is False
            and fit.get("parameter_tuning_allowed") is False
            and fit.get("C_to_shape_mapping_fitted_from_holdout") is False
        ),
        "raw_data_absence_is_explicit": (
            local.get("status") == "NOT_ARCHIVED"
            and local.get("raw_local_path") is None
            and local.get("raw_dataset_sha256") is None
        ),
    }
    keys = tuple(gates)
    return {
        "schema_version": "1.0",
        "artifact": "gaia_3d_query_manifest_verification",
        "audit_status": "PASS_WITH_BLOCKED_DATA_INTAKE" if all(gates[key] for key in keys) else "FAIL",
        "claim_status": "PREREGISTERED_QUERY_AND_HOLDOUT_ONLY",
        "evidence_class": "EXTERNAL_SOURCE_IDENTITY_WITHOUT_NUMERIC_ARCHIVE",
        "manifest": {
            "path": _relative(MANIFEST_PATH),
            "sha256": _sha256(MANIFEST_PATH),
            "status": manifest.get("status"),
            "source_id": manifest.get("source_id"),
        },
        "source_manifest": {
            "path": _relative(SOURCE_PATH),
            "sha256": _sha256(SOURCE_PATH),
            "source_data_status": source.get("source_data_status"),
        },
        "locked_design": {
            "primary_table": "gaiadr3.gaia_source",
            "requested_field_count": len(manifest.get("requested_fields", [])),
            "parallax_bias_reference_mas": bias.get("documented_global_reference_bias_mas"),
            "distance_policy": distance.get("status"),
            "selection_policy": selection.get("status"),
            "holdout_rule": split.get("rule"),
            "holdout_consumed": split.get("holdout_consumed"),
        },
        "gates": gates,
        "blockers": [
            "query has not been executed and no local raw table/hash exists",
            "distance estimator and parallax correction implementation remain open",
            "selection/completeness and mass realization remain open",
            "uncertainty propagation and physical rho_3D calibration remain open",
        ],
        "forbidden_uses": [
            "use source counts as rho_3D without mass realization",
            "apply -0.017 mas as a universal correction without covariate policy",
            "use holdout rows for calibration or parameter tuning",
            "call the query manifest external validation",
        ],
        "next_controller": manifest.get("next_controller"),
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT_PATH.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, ensure_ascii=False))
    return 0 if artifact["audit_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
