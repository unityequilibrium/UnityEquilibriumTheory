"""Generate the source-backed thermal observable-map readiness artifact."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

from core.core_paths import canonical_existing_path
from docs.core.thermal_source_observable_map import (  # noqa: E402
    NORMALIZED_TTG_OBSERVABLE,
    THERMAL_SOURCE_MAP_SCHEMA_VERSION,
    normalized_ttg_signal,
    quasi_temperature_difference_from_phi,
    ttg_wave_speed,
    ttg_wavevector,
    ttg_propagation_length,
)


TOPIC = ROOT / "topics" / "0.13_Thermodynamic_Bridge"
SOURCE_PACKAGE_PATH = TOPIC / "Data" / "03_Research" / "matter_space_second_sound_source_package.json"
SOURCE_REVIEW_PATH = TOPIC / "Data" / "03_Research" / "matter_space_thermal_source_review.json"
OUTPUT_PATH = TOPIC / "Result" / "artifacts" / "matter_space_thermal_observable_map_readiness.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(canonical_existing_path(path).read_bytes()).hexdigest()


def _local_numeric_exists(source: dict) -> bool:
    local_path = source.get("local_raw_path")
    if not local_path:
        return False
    candidate = TOPIC / local_path
    return canonical_existing_path(candidate).is_file()


def build_artifact() -> dict:
    source_package = json.loads(canonical_existing_path(SOURCE_PACKAGE_PATH).read_text(encoding="utf-8"))
    source_review = json.loads(canonical_existing_path(SOURCE_REVIEW_PATH).read_text(encoding="utf-8"))
    sources = source_package.get("sources", [])
    source_rows = []
    for source in sources:
        source_rows.append(
            {
                "source_id": source.get("source_id"),
                "external_identity_complete": bool(source.get("doi") and source.get("url")),
                "reported_units_present": bool(source.get("reported_unit_context")),
                "local_numeric_path": source.get("local_raw_path"),
                "local_numeric_present": _local_numeric_exists(source),
                "benchmark_role": source.get("benchmark_role"),
                "source_status": source.get("status"),
            }
        )

    normalized_example = normalized_ttg_signal(0.25, -0.25, 0.5)
    dimensional_example = quasi_temperature_difference_from_phi(0.25, -0.25, 4.0)
    wave_speed_example = ttg_wave_speed(2.0e-6, 1.0e-9)
    wavevector_example = ttg_wavevector(2.0e-6)
    propagation_length_example = ttg_propagation_length(2.0e-6, -2.0 ** -1.0)
    all_identity_complete = all(row["external_identity_complete"] for row in source_rows)
    local_numeric_ready = any(row["local_numeric_present"] for row in source_rows)
    holdout_consumed = bool(source_review.get("holdout_consumed"))
    gates = {
        "source_identity_and_unit_context_present": all_identity_complete,
        "standard_normalized_ttg_operator_defined": True,
        "standard_ttg_diagnostic_relations_defined": True,
        "normalized_phi_operator_is_explicit": normalized_example == 1.0,
        "dimensional_phi_to_quasi_temperature_scale_defined": False,
        "local_numeric_source_package_present": local_numeric_ready,
        "heat_flux_observable_map_closed": False,
        "entropy_production_observable_map_closed": False,
        "holdout_data_not_consumed": not holdout_consumed,
        "no_parameter_fitting": not bool(source_review.get("numeric_fitting_allowed")),
    }
    status = (
        "PASS_WITH_BLOCKED_DIMENSIONAL_AND_DATA_LANES"
        if all(
            gates[name]
            for name in (
                "source_identity_and_unit_context_present",
                "standard_normalized_ttg_operator_defined",
                "standard_ttg_diagnostic_relations_defined",
                "normalized_phi_operator_is_explicit",
                "holdout_data_not_consumed",
                "no_parameter_fitting",
            )
        )
        else "FAIL"
    )
    return {
        "schema_version": THERMAL_SOURCE_MAP_SCHEMA_VERSION,
        "artifact": "matter_space_thermal_observable_map_readiness",
        "audit_status": status,
        "mapping_status": "NORMALIZED_TTG_OPERATOR_DEFINED_DIMENSIONAL_UET_MAPPING_BLOCKED",
        "claim_status": "DEFINITION_ONLY / SIMULATION_ONLY",
        "evidence_class": "SOURCE_BACKED_OBSERVABLE_DEFINITION_WITH_BLOCKED_EXTERNAL_NUMERIC_INTAKE",
        "unit_lane": {
            "normalized_ttg_signal": "dimensionless",
            "quasi_temperature": "K only after independent calibration",
            "heat_flux": "W/m^2 not active",
            "entropy_production": "W/(K*m^3) not active",
        },
        "input_identity": {
            "source_package_path": str(SOURCE_PACKAGE_PATH.relative_to(ROOT.parent)).replace("\\", "/"),
            "source_package_sha256": _sha256(SOURCE_PACKAGE_PATH),
            "source_review_path": str(SOURCE_REVIEW_PATH.relative_to(ROOT.parent)).replace("\\", "/"),
            "source_review_sha256": _sha256(SOURCE_REVIEW_PATH),
        },
        "source_rows": source_rows,
        "measurement_operator": {
            "observable_id": "TTG-QTEMP-001",
            "name": NORMALIZED_TTG_OBSERVABLE,
            "standard_definition": "y_TTG(t;Lambda)=Delta_Tq(t;Lambda)/Delta_Tq(0;Lambda)",
            "UET_candidate_definition": "y_TTG(t;Lambda)=Delta_Phi(t;Lambda)/Delta_Phi(0;Lambda)",
            "dimensional_bridge": "Delta_Tq=alpha_Phi_K*Delta_Phi",
            "alpha_Phi_K_status": "OPEN_CALIBRATION_DEPENDENT",
            "raw_signal_status": "SOURCE_DATA_DECLARED_FOR_2026_HOLDOUT_BUT_NOT_LOCALLY_ARCHIVED",
            "heat_flux_status": "NOT_DIRECTLY_MEASURED_IN_TTG_OPERATOR",
            "entropy_status": "DERIVED_ONLY_AFTER_Tq_AND_q_UNITS_ARE_CLOSED",
        },
        "standard_reference_relations": {
            "wave_speed": "v_TTG=Lambda/(2*t_d)",
            "wave_speed_example_m_per_s": wave_speed_example,
            "wavevector": "q_TTG=2*pi/Lambda",
            "wavevector_example_m_inv": wavevector_example,
            "propagation_length": "l_p=Lambda/(-2*ln(-DeltaT_d))",
            "propagation_length_example_m": propagation_length_example,
            "fourier_flux": "q=-k*grad(Tq)",
            "entropy_production": "sigma=q^2/(k*Tq^2)",
        },
        "sanity_examples": {
            "normalized_signal_from_phi": normalized_example,
            "dimensional_temperature_difference_example_K": dimensional_example,
            "dimensional_example_is_not_a_calibration": True,
        },
        "gates": gates,
        "blockers": [
            "no locally archived numeric source package with row-level locator, preprocessing, uncertainty, and hash",
            "alpha_Phi_K has no derivation or source-locked calibration",
            "heat flux and entropy production are not direct TTG observables",
            "2026 source remains a locked holdout and cannot tune parameters",
        ],
        "next_required_artifact": "licensed local source-data package plus preregistered normalized TTG comparison; dimensional alpha_Phi_K remains a separate calibration gate",
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT_PATH.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(artifact, indent=2, ensure_ascii=False))
    return 0 if artifact["audit_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
