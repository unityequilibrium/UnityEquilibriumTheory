"""Validate a received Ding PBTE payload without fitting or reading holdout data.

The repository currently has a request contract but no received author payload.
This verifier keeps that boundary explicit: a missing payload is BLOCKED, an
invalid payload is FAIL, and only a row-complete payload can pass the source
acceptance contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PAYLOAD = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/received/"
    "ding_2022_pbte_numeric_payload.json"
)
DEFAULT_OUTPUT = ROOT / "docs/core/artifacts/t13_ding_pbte_payload_acceptance_audit.json"
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
REL_TOL = 1.0e-10



def _display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)

def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.fullmatch(value))


def _relative_match(left: float, right: float) -> bool:
    scale = max(abs(left), abs(right), 1.0e-30)
    return abs(left - right) <= REL_TOL * scale


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("payload must be a JSON object")
    return value


def _source_hashes_pass(payload: dict[str, Any]) -> bool:
    records = payload.get("source_hashes")
    if not isinstance(records, list) or not records:
        return False
    for record in records:
        if not isinstance(record, dict):
            return False
        if not _nonempty_text(record.get("path")) or not _sha256(record.get("sha256")):
            return False
    return True


def _holdout_policy_pass(payload: dict[str, Any]) -> bool:
    policy = payload.get("holdout_non_access_statement")
    if not isinstance(policy, dict):
        return False
    required_false = (
        "xie_2026_accessed",
        "target_curve_used",
        "alpha_fit_used",
        "parameter_fitting_performed",
        "post_inspection_tuning",
    )
    return all(policy.get(key) is False for key in required_false)


def _uncertainty_contract_pass(payload: dict[str, Any]) -> bool:
    record = payload.get("uncertainty_or_convergence")
    if not isinstance(record, dict):
        return False
    if not _nonempty_text(record.get("method")):
        return False
    if record.get("accepted") is not True:
        return False
    has_uncertainty = any(
        _nonempty_text(record.get(key))
        for key in ("source_standard_uncertainty", "convergence_envelope", "sensitivity_envelope")
    )
    return has_uncertainty


def _rows_pass(payload: dict[str, Any]) -> tuple[bool, list[str], dict[str, Any]]:
    mode_rows = payload.get("mode_rows")
    c_src_rows = payload.get("c_src_rows")
    temperature_grid = payload.get("temperature_grid_K")
    if not isinstance(mode_rows, list) or not mode_rows:
        return False, ["mode_rows_missing"], {}
    if not isinstance(c_src_rows, list) or not c_src_rows:
        return False, ["c_src_rows_missing"], {}
    if not isinstance(temperature_grid, list) or not temperature_grid:
        return False, ["temperature_grid_missing"], {}
    if not all(_finite(value) and float(value) > 0.0 for value in temperature_grid):
        return False, ["temperature_grid_not_positive_finite"], {}
    grid = [float(value) for value in temperature_grid]
    if len(set(grid)) != len(grid):
        return False, ["temperature_grid_not_unique"], {}

    mode_by_temperature: dict[float, list[dict[str, Any]]] = {temperature: [] for temperature in grid}
    seen_mode_rows: set[str] = set()
    failures: list[str] = []
    for row in mode_rows:
        if not isinstance(row, dict):
            failures.append("mode_row_not_object")
            continue
        row_id = row.get("row_id")
        row_key = str(row_id)
        temperature = row.get("temperature_K")
        mode_index = row.get("mode_index")
        c_mu = row.get("c_mu_J_per_m3_K")
        weight = row.get("weight", 1.0)
        if not _nonempty_text(row_id) or row_key in seen_mode_rows:
            failures.append("mode_row_identity_missing_or_duplicate")
        seen_mode_rows.add(row_key)
        if not _finite(temperature) or float(temperature) not in mode_by_temperature:
            failures.append("mode_row_temperature_not_in_grid")
            continue
        if not isinstance(mode_index, (int, str)) or isinstance(mode_index, bool):
            failures.append("mode_index_missing")
        mode_numeric_valid = True
        if not _finite(c_mu) or float(c_mu) < 0.0:
            failures.append("mode_heat_capacity_not_nonnegative_finite")
            mode_numeric_valid = False
        if not _finite(weight) or float(weight) <= 0.0:
            failures.append("mode_weight_not_positive_finite")
            mode_numeric_valid = False
        if mode_numeric_valid:
            mode_by_temperature[float(temperature)].append(row)

    c_src_by_temperature: dict[float, dict[str, Any]] = {}
    seen_c_src_rows: set[str] = set()
    for row in c_src_rows:
        if not isinstance(row, dict):
            failures.append("c_src_row_not_object")
            continue
        row_id = row.get("row_id")
        row_key = str(row_id)
        temperature = row.get("temperature_K")
        c_src = row.get("C_src_J_per_m3_K")
        if not _nonempty_text(row_id) or row_key in seen_c_src_rows:
            failures.append("c_src_row_identity_missing_or_duplicate")
        seen_c_src_rows.add(row_key)
        if not _finite(temperature) or float(temperature) not in mode_by_temperature:
            failures.append("c_src_row_temperature_not_in_grid")
            continue
        if not _finite(c_src) or float(c_src) < 0.0:
            failures.append("c_src_not_nonnegative_finite")
        uncertainty = row.get("uncertainty_standard_J_per_m3_K")
        if uncertainty is not None and (not _finite(uncertainty) or float(uncertainty) < 0.0):
            failures.append("c_src_uncertainty_not_nonnegative_finite")
        c_src_by_temperature[float(temperature)] = row

    if set(c_src_by_temperature) != set(grid):
        failures.append("c_src_temperature_coverage_incomplete")

    recomputed: dict[str, float] = {}
    for temperature in grid:
        rows = mode_by_temperature[temperature]
        if not rows:
            failures.append("mode_temperature_coverage_incomplete")
            continue
        expected = sum(float(row["weight"]) * float(row["c_mu_J_per_m3_K"]) for row in rows)
        row = c_src_by_temperature.get(temperature)
        if row is not None and _finite(row.get("C_src_J_per_m3_K")):
            reported = float(row["C_src_J_per_m3_K"])
            if not _relative_match(expected, reported):
                failures.append(f"c_src_recompute_mismatch_{temperature:g}K")
            recomputed[f"{temperature:g}"] = expected

    return not failures, sorted(set(failures)), {"recomputed_C_src_J_per_m3_K": recomputed}


def audit_payload(payload_path: Path, output_path: Path | None = None) -> dict[str, Any]:
    if not payload_path.exists():
        report: dict[str, Any] = {
            "schema_version": "t13-ding-pbte-payload-acceptance-audit-v1",
            "artifact": "t13_ding_pbte_payload_acceptance_audit",
            "generated_at": date.today().isoformat(),
            "status": "BLOCKED_DING_PBTE_PAYLOAD_NOT_RECEIVED",
            "payload_path": _display_path(payload_path),
            "payload_present": False,
            "checks": {"payload_present": False, "holdout_accessed": False},
            "controlling_blocker": "author_data_or_independent_reproduction_payload_not_received",
            "next_controller": "Receive a permitted payload, hash every source file, then rerun this verifier before full-gate integration.",
            "claim_boundary": "No Ding C_src, alpha_Phi_K, prediction, or external validation is emitted.",
        }
    else:
        payload = _load_json(payload_path)
        required_fields = (
            "source_identity",
            "source_locator_or_author_file_name",
            "material_state_and_geometry",
            "quantity_definition",
            "units",
            "temperature_grid_K",
            "mode_rows",
            "c_src_rows",
            "preprocessing",
            "uncertainty_or_convergence",
            "source_hashes",
            "permission_or_terms",
            "independence_statement",
            "holdout_non_access_statement",
        )
        field_checks = {field: field in payload for field in required_fields}
        checks: dict[str, bool] = {
            "payload_present": True,
            "schema_version_present": _nonempty_text(payload.get("schema_version")),
            "data_role_declared": payload.get("data_role") in {
                "SOURCE_LOCKED_EXTERNAL_INPUT",
                "INDEPENDENT_REPRODUCTION_INPUT",
            },
            "required_fields_present": all(field_checks.values()),
            "source_identity_nonempty": bool(payload.get("source_identity")),
            "source_locator_nonempty": _nonempty_text(payload.get("source_locator_or_author_file_name")),
            "material_state_nonempty": bool(payload.get("material_state_and_geometry")),
            "quantity_definition_nonempty": bool(payload.get("quantity_definition")),
            "units_declared": bool(payload.get("units")),
            "preprocessing_nonempty": bool(payload.get("preprocessing")),
            "permission_nonempty": bool(payload.get("permission_or_terms")),
            "independence_nonempty": bool(payload.get("independence_statement")),
            "source_hashes_valid": _source_hashes_pass(payload),
            "uncertainty_or_convergence_accepted": _uncertainty_contract_pass(payload),
            "holdout_policy_pass": _holdout_policy_pass(payload),
        }
        rows_pass, row_failures, row_summary = _rows_pass(payload)
        checks["mode_and_c_src_rows_recompute"] = rows_pass
        failures = [key for key, value in checks.items() if not value]
        failures.extend(row_failures)
        report = {
            "schema_version": "t13-ding-pbte-payload-acceptance-audit-v1",
            "artifact": "t13_ding_pbte_payload_acceptance_audit",
            "generated_at": date.today().isoformat(),
            "status": "PASS_DING_PBTE_PAYLOAD_ACCEPTANCE" if not failures else "FAIL_DING_PBTE_PAYLOAD_ACCEPTANCE",
            "payload_path": _display_path(payload_path),
            "payload_present": True,
            "payload_sha256": hashlib.sha256(payload_path.read_bytes()).hexdigest(),
            "checks": checks,
            "field_checks": field_checks,
            "row_summary": row_summary,
            "row_failures": sorted(set(row_failures)),
            "failed_checks": sorted(set(failures)),
            "holdout_accessed": not checks["holdout_policy_pass"],
            "numeric_C_src_accepted": not failures,
            "numeric_alpha_Phi_K_emitted": False,
            "controlling_blocker": None if not failures else "ding_pbte_payload_acceptance_contract_failed",
            "next_controller": "Integrate only this accepted source into the full gate; keep base-Phi calibration and Xie holdout gates independent." if not failures else "Repair the payload contract and rerun without using target residuals or Xie 2026.",
            "claim_boundary": "Accepted Ding PBTE source input only; this verifier does not derive or emit alpha_Phi_K, a base-Phi SI map, TTG prediction, or Full Topic 13 closure." if not failures else "No Ding PBTE source acceptance is emitted.",
        }

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", type=Path, default=DEFAULT_PAYLOAD)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload_path = args.payload if args.payload.is_absolute() else ROOT / args.payload
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    report = audit_payload(payload_path, output_path)
    print(json.dumps({
        "status": report["status"],
        "payload_present": report["payload_present"],
        "failed_checks": report.get("failed_checks", []),
        "artifact": str(output_path.relative_to(ROOT)).replace("\\", "/"),
    }, indent=2))
    return 0 if report["status"].startswith("PASS") or report["status"].startswith("BLOCKED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
