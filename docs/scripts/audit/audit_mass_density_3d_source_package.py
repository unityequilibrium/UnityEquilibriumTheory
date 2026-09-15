"""Audit the external 3D density source-package boundary.

The audit intentionally accepts a metadata-only candidate while blocking any
physical C-to-mass or galaxy-data claim until a local source table, selection
function, mass realization, uncertainty propagation, and holdout protocol are
present.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "docs/data/external/astronomy/gaia_edr3_gcns/2026-08-08/source_manifest.json"
OPERATOR_PATH = ROOT / "docs/core/07_artifacts/verification/mass_density_3d_contract_verification.json"
QUERY_MANIFEST_PATH = ROOT / "docs/data/external/astronomy/gaia_edr3_gcns/2026-08-08/query_and_holdout_manifest.json"
OUTPUT_PATH = ROOT / "docs/core/07_artifacts/provenance/mass_density_3d_external_source_package.json"


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
    operator = _load(OPERATOR_PATH)
    query_manifest = _load(QUERY_MANIFEST_PATH)
    identity = manifest.get("source_identity", {})
    units = manifest.get("unit_contract", {})
    selection = manifest.get("selection_function", {})
    mass = manifest.get("mass_calibration", {})
    uncertainty = manifest.get("uncertainty", {})
    holdout = manifest.get("holdout_policy", {})
    fit_policy = manifest.get("fit_policy", {})

    gates = {
        "source_identity_complete": bool(
            manifest.get("source_id")
            and identity.get("paper_doi")
            and identity.get("paper_url")
            and identity.get("archive_url")
        ),
        "source_scope_declares_3d_structure_not_mass_density": bool(
            manifest.get("data_scope", {}).get("not_directly_supplied_as_target")
        ),
        "local_raw_path_and_hash_are_explicitly_missing": (
            "local_raw_path" in manifest
            and "local_raw_sha256" in manifest
            and manifest.get("local_raw_path") is None
            and manifest.get("local_raw_sha256") is None
            and manifest.get("source_data_status") == "NOT_ARCHIVED"
        ),
        "units_are_declared_without_silent_mass_conversion": bool(
            units.get("parallax_source_unit")
            and units.get("distance_runtime_unit")
            and units.get("position_runtime_unit")
            and units.get("source_mass_unit") == "not_closed_by_catalogue_package"
            and units.get("target_density_unit") == "kg/m^3"
        ),
        "preprocessing_worklist_is_explicit": bool(
            manifest.get("preprocessing", {}).get("required_steps")
        ),
        "selection_function_remains_open": selection.get("status") == "OPEN",
        "mass_calibration_remains_open": mass.get("status") == "OPEN",
        "uncertainty_remains_open": uncertainty.get("status") == "OPEN",
        "holdout_policy_is_locked_before_comparison": (
            holdout.get("status") == "LOCK_BEFORE_EXTERNAL_COMPARISON"
            and holdout.get("holdout_not_consumed") is True
        ),
        "fit_and_parameter_tuning_are_blocked": (
            fit_policy.get("numeric_fitting_allowed") is False
            and fit_policy.get("parameter_tuning_allowed") is False
        ),
        "synthetic_operator_does_not_promote_physical_map": (
            operator.get("audit_status") == "PASS_WITH_BLOCKED_EXTERNAL_3D_MAPPING"
            and operator.get("claim_status") == "SIMULATION_ONLY"
        ),
        "query_and_holdout_manifest_is_present_and_blocked": (
            query_manifest.get("status") == "QUERY_AND_HOLDOUT_MANIFEST_ONLY"
            and query_manifest.get("fit_policy", {}).get("numeric_fitting_allowed") is False
            and query_manifest.get("holdout_split", {}).get("holdout_consumed") is False
        ),
    }
    structural_keys = (
        "source_identity_complete",
        "source_scope_declares_3d_structure_not_mass_density",
        "local_raw_path_and_hash_are_explicitly_missing",
        "units_are_declared_without_silent_mass_conversion",
        "preprocessing_worklist_is_explicit",
        "selection_function_remains_open",
        "mass_calibration_remains_open",
        "uncertainty_remains_open",
        "holdout_policy_is_locked_before_comparison",
        "fit_and_parameter_tuning_are_blocked",
        "synthetic_operator_does_not_promote_physical_map",
        "query_and_holdout_manifest_is_present_and_blocked",
    )
    audit_status = (
        "PASS_WITH_BLOCKED_EXTERNAL_SOURCE_PACKAGE"
        if all(gates[key] for key in structural_keys)
        else "FAIL"
    )
    return {
        "schema_version": "1.0",
        "artifact": "mass_density_3d_external_source_package",
        "audit_status": audit_status,
        "claim_status": "SOURCE_CANDIDATE_METADATA_ONLY",
        "evidence_class": "EXTERNAL_IDENTITY_WITHOUT_LOCAL_NUMERIC_ARCHIVE",
        "source_manifest": {
            "path": _relative(MANIFEST_PATH),
            "sha256": _sha256(MANIFEST_PATH),
            "source_id": manifest.get("source_id"),
            "status": manifest.get("status"),
            "source_data_status": manifest.get("source_data_status"),
        },
        "query_manifest": {
            "path": _relative(QUERY_MANIFEST_PATH),
            "sha256": _sha256(QUERY_MANIFEST_PATH),
            "status": query_manifest.get("status"),
            "holdout_consumed": query_manifest.get("holdout_split", {}).get("holdout_consumed"),
        },
        "operator_dependency": {
            "path": _relative(OPERATOR_PATH),
            "sha256": _sha256(OPERATOR_PATH),
            "status": operator.get("audit_status"),
            "claim_status": operator.get("claim_status"),
        },
        "research_finding": {
            "candidate": "Gaia EDR3/GCNS can supply a 3D stellar-structure coordinate source after distance treatment.",
            "non_equivalence": "a 3D catalogue of observed stellar sources is not automatically a volume-mass density field",
            "required_chain": "parallax -> distance/coordinates -> selection-corrected source field -> stellar-mass realization -> rho_3D",
            "UET_consequence": "the source can test an explicit C-to-shape/amplitude observable map, but cannot define C as mass by itself",
        },
        "unit_and_observable_boundary": {
            "source_coordinates": "mas -> pc -> m after declared distance treatment",
            "target_observable": "rho_3D in kg/m^3",
            "measurement_operator": "O[C_phase, geometry, rho_hat, A_m, L_xyz] -> rho_3D",
            "C_to_shape_status": "OPEN",
            "amplitude_status": "OPEN_SOURCE_OR_CALIBRATION_DEPENDENT",
        },
        "gates": gates,
        "blockers": [
            "no local raw/extracted Gaia table or dataset hash",
            "query/holdout manifest is preregistered but no numeric intake has occurred",
            "selection/completeness and distance treatment are not frozen",
            "catalogue source counts do not close total baryonic mass calibration",
            "uncertainty propagation to volume density is open",
            "no calibration/holdout source split is available",
        ],
        "forbidden_uses": [
            "fit C directly to Gaia source counts and call it mass density",
            "use the metadata-only candidate as galaxy rotation validation",
            "promote the synthetic 3D operator to a physical mass derivation",
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
