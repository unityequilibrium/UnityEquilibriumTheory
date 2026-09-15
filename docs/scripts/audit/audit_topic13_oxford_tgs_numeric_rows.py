"""Audit the source-locked Oxford TGS Figure 1 numeric-row extraction."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research"
MANIFEST = BASE / "oxford_tgs_figure1_numeric_rows_manifest.json"
CSV_GZ = BASE / "oxford_tgs_figure1_numeric_rows.csv.gz"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_oxford_tgs_numeric_rows_audit.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    manifest = load_json(MANIFEST)
    checks: dict[str, bool] = {}
    rows: list[dict[str, str]] = []
    checks["manifest_status_is_source_locked"] = (
        manifest.get("status") == "NUMERIC_ROWS_SOURCE_LOCKED_COMPARATOR"
    )
    checks["csv_present"] = CSV_GZ.is_file()
    checks["manifest_output_path_matches"] = (
        manifest["extraction"]["output_path"]
        == CSV_GZ.relative_to(ROOT).as_posix()
    )
    actual_hash = sha256(CSV_GZ) if CSV_GZ.is_file() else None
    checks["csv_hash_matches_manifest"] = (
        actual_hash == manifest["extraction"]["output_sha256"]
    )
    checks["raw_mat_hash_matches"] = bool(manifest["source"]["raw_mat_hash_match"])
    checks["row_count_is_expected"] = (
        manifest["extraction"]["row_count"]
        == manifest["extraction"]["trace_count"]
        * manifest["extraction"]["sample_count_per_trace"]
    )

    fieldnames = [
        "horizontal_index_1based",
        "vertical_index_1based",
        "trace_index_1based",
        "sample_index_1based",
        "ph_source_value",
        "pv_source_value",
        "xx_time_s",
        "xx1_time_s",
        "yy_signal_au",
        "yy1_signal_au",
        "y_delta_yy1_minus_yy_au",
    ]
    if CSV_GZ.is_file():
        with gzip.open(CSV_GZ, "rt", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            checks["csv_header_matches_contract"] = reader.fieldnames == fieldnames
            for row in reader:
                rows.append(row)
    else:
        checks["csv_header_matches_contract"] = False

    expected_rows = manifest["extraction"]["row_count"]
    checks["csv_row_count_matches_manifest"] = len(rows) == expected_rows
    keys = {
        (
            int(row["trace_index_1based"]),
            int(row["sample_index_1based"]),
        )
        for row in rows
    }
    checks["row_identity_is_unique"] = len(keys) == len(rows)
    checks["rows_are_finite"] = all(
        math.isfinite(float(row[field]))
        for row in rows
        for field in fieldnames[4:]
    )
    checks["source_subtraction_is_exact"] = all(
        math.isclose(
            float(row["y_delta_yy1_minus_yy_au"]),
            float(row["yy1_signal_au"]) - float(row["yy_signal_au"]),
            rel_tol=0.0,
            abs_tol=1e-15,
        )
        for row in rows
    )
    checks["xx_and_xx1_are_equal"] = all(
        math.isclose(
            float(row["xx_time_s"]),
            float(row["xx1_time_s"]),
            rel_tol=0.0,
            abs_tol=1e-20,
        )
        for row in rows
    )
    checks["selected_map_identity_is_preserved"] = all(
        int(row["horizontal_index_1based"])
        == manifest["extraction"]["selected_horizontal_index_1based"]
        and int(row["vertical_index_1based"])
        == manifest["extraction"]["selected_vertical_index_1based"]
        for row in rows
    )
    checks["time_is_strictly_increasing_per_trace"] = True
    for trace in range(1, manifest["extraction"]["trace_count"] + 1):
        trace_rows = [row for row in rows if int(row["trace_index_1based"]) == trace]
        times = [float(row["xx_time_s"]) for row in trace_rows]
        if any(right <= left for left, right in zip(times, times[1:])):
            checks["time_is_strictly_increasing_per_trace"] = False
            break
    checks["row_level_uncertainty_not_invented"] = not manifest[
        "uncertainty_boundary"
    ]["row_level_uncertainty_emitted"]
    checks["thermal_diffusivity_not_emitted"] = not manifest[
        "uncertainty_boundary"
    ]["thermal_diffusivity_emitted"]
    checks["no_fit_or_target_used"] = (
        manifest["holdout_policy"]["target_curve_used"] is False
        and manifest["holdout_policy"]["ding_target_curve_used"] is False
        and manifest["uncertainty_boundary"]["fit_performed_by_extractor"] is False
    )
    checks["xie_holdout_not_accessed"] = (
        manifest["holdout_policy"]["xie_2026_accessed"] is False
    )
    checks["alpha_not_emitted"] = (
        manifest["holdout_policy"]["numeric_alpha_Phi_K_emitted"] is False
    )

    status = (
        "PASS_OXFORD_TGS_NUMERIC_ROWS_SOURCE_LOCKED_COMPARATOR"
        if all(checks.values())
        else "FAIL_OXFORD_TGS_NUMERIC_ROWS_AUDIT"
    )
    artifact = {
        "schema_version": "t13-oxford-tgs-numeric-rows-audit-v1",
        "artifact": "t13_oxford_tgs_numeric_rows_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "claim_promotion": False,
        "major_result": {
            "major_result_id": "T13_OXFORD_TGS_NUMERIC_ROWS_COMPARATOR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": [
                "source-locked extraction of the selected Figure 1 map point",
                "10 trace identities and 2002 source samples per trace",
                "source time and intensity units preserved as labeled",
                "yy1 minus yy subtraction preserved as the source-defined signal operation",
                "raw extraction separated from fitting, thermal diffusivity, Ding C_src, and Phi calibration",
            ],
            "equation_or_mapping": (
                "y_source(t) = yy1(t) - yy(t); source fit remains outside this artifact"
            ),
            "units": manifest["units"],
            "derivation_class": "external source numeric-row extraction; no UET derivation",
            "observable": "Oxford Figure 1 transient-grating intensity trace",
            "data_role": manifest["data_role"],
            "evidence_artifacts": [
                {
                    "path": MANIFEST.relative_to(ROOT).as_posix(),
                    "sha256": sha256(MANIFEST),
                },
                {
                    "path": CSV_GZ.relative_to(ROOT).as_posix(),
                    "sha256": actual_hash,
                },
                {"path": OUT.relative_to(ROOT).as_posix()},
            ],
            "verification_status": status,
            "open_blockers": [
                "material_and_temperature_regime_mapping_to_Ding_TTG_not_closed",
                "Ding_specific_PBTE_C_src_not_provided",
                "row_level_uncertainty_for_a_physical_thermal_observable_not_available",
                "base_Phi_to_SI_energy_map_and_independent_alpha_Phi_K_missing",
                "EOS_transport_KMS_entropy_and_dissipative_balance_remain_open",
            ],
            "dependency_unlocked": (
                "Oxford TGS numeric comparator lane only; no Ding C_src, c_v, "
                "alpha_Phi_K, Full Topic 13, Core, Gravity, or external-validation unlock"
            ),
            "claim_boundary": manifest["claim_boundary"],
        },
        "source": manifest["source"],
        "extraction": manifest["extraction"],
        "checks": checks,
        "numeric_rows_emitted": len(rows),
        "numeric_alpha_Phi_K_emitted": False,
        "parameter_fitting_performed": False,
        "target_data_used": False,
        "xie_2026_accessed": False,
        "controlling_blocker": "material_temperature_and_physical_thermal_mapping_missing",
        "next_action": (
            "Retain the rows as a source comparator; do not infer c_v, C_src, "
            "thermal diffusivity, or alpha_Phi_K without a declared source mapping."
        ),
        "claim_boundary": manifest["claim_boundary"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "closure_level": artifact["major_result"]["closure_level"],
                "failed_checks": [key for key, value in checks.items() if not value],
                "numeric_rows_emitted": len(rows),
                "controlling_blocker": artifact["controlling_blocker"],
            },
            indent=2,
        )
    )
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
