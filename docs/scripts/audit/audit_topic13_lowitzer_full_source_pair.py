"""Verify the source-locked Lowitzer graphite alpha_V/K_T pair boundary."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PACKAGE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "lowitzer_2006_graphite_pvt_full_source_package.json"
)
OUT_REL = "docs/core/artifacts/t13_lowitzer_graphite_pvt_full_source_pair_audit.json"


def load(relative: str) -> dict:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    package = load(PACKAGE_REL)
    source = package["source"]
    pair = package["pair_contract"]
    rows = package["source_rows"]
    witness = package["derived_correction_witness"]
    raw_rel = source["local_raw_path"]
    raw_path = ROOT / raw_rel

    primary = next(row for row in rows if row["row_id"] == witness["row_id"])
    alpha = primary["alpha_V_K_inv"]
    alpha_uncertainty = primary["alpha_V_uncertainty_K_inv"]
    k_t_pa = primary["K_T_GPa"] * 1.0e9
    k_t_uncertainty_pa = primary["K_T_uncertainty_GPa"] * 1.0e9
    temperature = primary["temperature_K"]
    correction = temperature * alpha**2 * k_t_pa
    relative_uncertainty = math.sqrt(
        (2.0 * alpha_uncertainty / alpha) ** 2
        + (k_t_uncertainty_pa / k_t_pa) ** 2
    )
    correction_uncertainty = correction * relative_uncertainty

    checks = {
        "package_status_is_source_locked": package["status"].startswith("SOURCE_LOCKED"),
        "source_locator_and_doi_present": bool(source.get("source_locator")) and bool(source.get("doi")),
        "local_payload_present": raw_path.is_file(),
        "local_payload_hash_matches": raw_path.is_file()
        and sha256(raw_path) == source["local_raw_sha256"],
        "local_payload_size_matches": raw_path.is_file()
        and raw_path.stat().st_size == source["local_raw_size_bytes"],
        "full_text_state_is_declared": source["payload_state"] == "FULL_TEXT_ARCHIVED",
        "four_source_rows_present": len(rows) == 4,
        "rows_have_temperature_units_and_locators": all(
            row["temperature_K"] == 300.0
            and row["alpha_V_K_inv"] > 0.0
            and row["K_T_GPa"] > 0.0
            and row["source_locator"]
            for row in rows
        ),
        "same_study_sample_and_temperature_pair": pair["same_study_pair_present"]
        and pair["same_sample_pair_present"]
        and pair["same_temperature_point_present"],
        "source_uncertainty_is_present": pair["source_grade_uncertainty_available"]
        and all(
            row["alpha_V_uncertainty_K_inv"] is not None
            and row["K_T_uncertainty_GPa"] is not None
            for row in rows
        ),
        "correction_witness_reproduces": math.isclose(
            correction, witness["delta_c_p_minus_c_v_J_m3_K"], rel_tol=0.0, abs_tol=1.0e-9
        ),
        "uncertainty_witness_reproduces": math.isclose(
            correction_uncertainty,
            witness["delta_c_p_minus_c_v_uncertainty_J_m3_K"],
            rel_tol=0.0,
            abs_tol=0.02,
        ),
        "no_c_v_or_ding_csrc_emitted": pair["same_state_c_p_or_c_v_present"] is False
        and pair["numeric_c_p_to_c_v_correction_emitted"] is False
        and pair["numeric_Ding_C_src_emitted"] is False,
        "ding_mapping_remains_open": pair["Ding_material_regime_mapping_closed"] is False,
        "alpha_not_calibration": witness["accepted_for_alpha_Phi_K"] is False,
        "holdout_is_unread": all(
            value is False
            for value in package["holdout_policy"].values()
            if isinstance(value, bool)
            and value
            in {
                package["holdout_policy"]["xie_2026_accessed"],
                package["holdout_policy"]["xie_2026_source_data_consumed"],
                package["holdout_policy"]["target_curve_used"],
                package["holdout_policy"]["alpha_fit_used"],
                package["holdout_policy"]["used_for_calibration"],
            }
        ),
    }
    # The compact boolean expression above deliberately checks the named
    # policy fields explicitly; unrelated future policy metadata is ignored.
    checks["holdout_is_unread"] = not any(
        package["holdout_policy"].get(key, False)
        for key in (
            "xie_2026_accessed",
            "xie_2026_source_data_consumed",
            "target_curve_used",
            "alpha_fit_used",
            "used_for_calibration",
        )
    )

    status = (
        "PASS_SCOPED_SOURCE_LOCKED_LOWITZER_ALPHA_V_K_T_PAIR"
        if all(checks.values())
        else "FAIL_LOWITZER_ALPHA_V_K_T_PAIR_AUDIT"
    )
    report = {
        "schema_version": "t13-lowitzer-graphite-pvt-full-source-pair-audit-v1",
        "artifact": "t13_lowitzer_graphite_pvt_full_source_pair_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_LOWITZER_GRAPHITE_ALPHA_V_K_T_FULL_SOURCE_PAIR",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if status.startswith("PASS") else "OPEN",
            "what_is_closed": "A same-study, same-sample, 300 K alpha_V/K_T pair with source-reported uncertainty is hash-verified.",
            "what_remains_open": [
                "material_regime_mapping_to_TTG_not_closed",
                "c_v_source_uncertainty_not_closed",
                "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
                "alpha_Phi_K_independent_calibration_missing",
            ],
            "equation_or_mapping": "c_p^V - c_v^V = T * alpha_V^2 * K_T",
            "units": {
                "alpha_V": "K^-1",
                "K_T": "Pa",
                "correction_term": "J m^-3 K^-1",
            },
            "derivation_class": "source-locked primary-paper transcription plus standard thermodynamic identity",
            "observable": "graphite Cp-to-Cv correction term",
            "data_role": "EXTERNAL_INPUT_THERMODYNAMIC_CORRECTION_COMPARATOR_NOT_DING_CALIBRATION",
            "evidence_artifacts": [
                {"path": PACKAGE_REL, "sha256": sha256(ROOT / PACKAGE_REL)},
                {"path": raw_rel, "sha256": source["local_raw_sha256"]},
            ],
            "verification_status": status,
            "controlling_blocker": "material_regime_mapping_to_TTG_not_closed",
            "claim_boundary": "The pair closes only the source-grade alpha_V/K_T correction-input lane. It does not close c_v, Ding C_src, Phi SI scale, alpha_Phi_K, UET transport, or Full Topic 13.",
        },
        "source": {
            "source_id": source["source_id"],
            "local_raw_path": raw_rel,
            "local_raw_sha256": source["local_raw_sha256"],
            "source_locators": source["source_locators"],
            "material_state": package["material_state"],
        },
        "pair": {
            "same_study": pair["same_study_pair_present"],
            "same_sample": pair["same_sample_pair_present"],
            "same_temperature": pair["same_temperature_point_present"],
            "alpha_V_K_inv": alpha,
            "alpha_V_uncertainty_K_inv": alpha_uncertainty,
            "K_T_Pa": k_t_pa,
            "K_T_uncertainty_Pa": k_t_uncertainty_pa,
            "temperature_K": temperature,
        },
        "derived_correction_witness": {
            "value_J_m3_K": correction,
            "uncertainty_J_m3_K": correction_uncertainty,
            "source_recorded_value_J_m3_K": witness["delta_c_p_minus_c_v_J_m3_K"],
            "source_recorded_uncertainty_J_m3_K": witness["delta_c_p_minus_c_v_uncertainty_J_m3_K"],
            "no_c_v_value_emitted": True,
            "no_Ding_C_src_emitted": True,
        },
        "checks": checks,
        "holdout_policy": package["holdout_policy"],
        "claim_boundary": "This source-pair result is a comparator/correction input only. Its material and response contract are not silently substituted for Ding TTG.",
    }
    out = ROOT / OUT_REL
    out.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": OUT_REL, "failed_checks": [key for key, value in checks.items() if not value]}, indent=2))
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
