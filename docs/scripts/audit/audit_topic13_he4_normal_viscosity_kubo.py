"""Audit the physical He-4 normal-component shear Kubo record."""

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

from docs.core.he4_normal_viscosity_kubo import physical_transport_record  # noqa: E402
from docs.core.topic13_closure_record_contract import validate_physical_transport_record  # noqa: E402


PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "he4_svp_normal_viscosity_kubo_source_package.json"
)
MODULE = ROOT / "docs/core/he4_normal_viscosity_kubo.py"
CALIBRATION = ROOT / "docs/core/artifacts/t13_he4_o2_response_calibration_audit.json"
SI_BETA = ROOT / "docs/core/artifacts/t13_he4_o2_si_beta_mapping_audit.json"
HEAT_ENTROPY = ROOT / "docs/core/artifacts/t13_uet_o2_covariant_entropy_heat_flux_balance_audit.json"
OUT = ROOT / "docs/core/artifacts/t13_he4_normal_viscosity_kubo_audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    package = load(PACKAGE)
    calibration = load(CALIBRATION)
    si_beta = load(SI_BETA)
    heat_entropy = load(HEAT_ENTROPY)
    record = physical_transport_record()
    validation = validate_physical_transport_record(record)
    coefficient = package["coefficient"]
    rows = coefficient["envelope_rows"]
    envelope = max(
        abs(float(row["viscosity_Pa_s"]) - float(coefficient["recommended_value_Pa_s"]))
        for row in rows
    )
    checks = {
        "closure_record_validator_passes": validation["status"] == "PASS_PHYSICAL_TRANSPORT_RECORD",
        "source_package_is_external_input": package["data_role"] == "EXTERNAL_INPUT",
        "recommended_value_matches_record": math.isclose(float(coefficient["recommended_value_Pa_s"]), float(record["value"]), rel_tol=0.0, abs_tol=0.0),
        "uncertainty_recomputes_from_local_envelope": math.isclose(envelope, float(record["uncertainty"]), rel_tol=1e-12, abs_tol=1e-20),
        "lower_coefficient_bound_is_positive": float(record["value"]) - float(record["uncertainty"]) > 0.0,
        "temperature_matches_alpha_state": record["state"]["temperature_K"] == calibration["record"]["temperature_K"],
        "response_coordinate_matches_alpha_state": math.isclose(record["state"]["space_response"], calibration["record"]["superfluid_fraction_reference"], rel_tol=0.0, abs_tol=0.0),
        "si_dimensional_lane_is_closed": si_beta["status"] == "PASS_HE4_SI_SCALE_AND_NORMALIZED_BETA",
        "formal_heat_entropy_lane_is_closed": heat_entropy["status"] == "PASS_ACTION_DERIVED_COVARIANT_ENTROPY_HEAT_FLUX_BALANCE_LANE",
        "physical_channel_is_shear_not_fake_heat_conductivity": "shear" in record["hydrodynamic_frame"].lower() and "not a bulk fourier heat conductivity" in package["claim_boundary"].lower(),
        "kms_fdt_is_pass": record["kms_fdt"]["status"] == "PASS",
        "entropy_mapping_is_pass": record["entropy_mapping"]["status"] == "PASS",
        "source_hash_matches_package": record["source_hash"] == sha256(PACKAGE),
        "xie_holdout_is_unread": record["holdout_policy"]["xie_2026_accessed"] is False,
        "no_target_curve": record["holdout_policy"]["target_curve_used"] is False,
        "no_fit_or_tuning": record["holdout_policy"]["fit_or_tuning_used"] is False,
    }
    passed = all(checks.values())
    status = "PASS_HE4_PHYSICAL_SHEAR_KUBO_TRANSPORT" if passed else "FAIL_HE4_PHYSICAL_SHEAR_KUBO_TRANSPORT"
    evidence_paths = [PACKAGE, MODULE, CALIBRATION, SI_BETA, HEAT_ENTROPY]
    report = {
        "schema_version": "t13-he4-normal-viscosity-kubo-audit-v1",
        "artifact": "t13_he4_normal_viscosity_kubo_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": {
            "major_result_id": "T13_HE4_PHYSICAL_SHEAR_KUBO_TRANSPORT",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if passed else "OPEN",
            "what_is_closed": "One source-locked SI shear-viscosity coefficient for the He II normal component at the calibrated 1.7 K SVP state, with a conservative local source envelope, stress Kubo relation, KMS/FDT noise interface, and nonnegative viscous entropy-production map.",
            "equation_or_mapping": {
                "kubo": record["correlator_locator"],
                "kms_fdt": record["kms_fdt"]["relation"],
                "entropy": record["entropy_mapping"]["relation"],
            },
            "units": {"eta": "Pa s", "temperature": "K", "space_response": "rho_s/rho"},
            "derivation_class": "SOURCE_LOCKED_EXTERNAL_INPUT_PLUS_STANDARD_GREEN_KUBO_KMS_ENTROPY_MAPPING",
            "observable": "normal-component shear viscosity of He II at 1.7 K and SVP",
            "data_role": "EXTERNAL_INPUT_NOT_UET_PREDICTION",
            "evidence_artifacts": [
                {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(path)}
                for path in evidence_paths
            ],
            "verification_status": status,
            "open_blockers": [],
            "dependency_unlocked": "Physical dissipative-coefficient input for the flat Topic 13 Core composition; no external validation or global UET unlock by itself.",
            "claim_boundary": package["claim_boundary"],
        },
        "record": record,
        "record_validation": validation,
        "uncertainty_recomputation": {
            "local_envelope_Pa_s": envelope,
            "relative_bound": envelope / float(record["value"]),
            "interpretation": coefficient["source_caution"],
        },
        "checks": checks,
        "controlling_blocker": None if passed else "physical_transport_record_failed",
        "next_controller": "Compose this physical shear channel with the already-passed formal heat-flux, KMS, entropy-current, dissipative-balance, SI-alpha, and beta lanes; retain the boundary that this is not a bulk Fourier conductivity or complete external validation.",
        "claim_boundary": package["claim_boundary"],
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "eta_Pa_s": record["value"], "uncertainty_Pa_s": record["uncertainty"], "record_validation": validation["status"], "artifact": str(OUT.relative_to(ROOT)).replace("\\", "/")}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
