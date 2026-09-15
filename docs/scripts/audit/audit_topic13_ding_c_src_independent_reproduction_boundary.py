"""Audit whether the independent MP48 heat-capacity route can stand in for Ding C_src."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DING_TEXT = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "ding_2022_pmc_full_text.txt"
)
MP48_PACKAGE = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "mp48_independent_graphite_cv_source_package.json"
)
MP48_AUDIT = ROOT / "docs/core/07_artifacts/topic13/t13_mp48_independent_graphite_cv_audit.json"
OUT = ROOT / "docs/core/07_artifacts/topic13/t13_ding_c_src_independent_reproduction_boundary_audit.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def line_locator(path: Path, needle: str) -> str | None:
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if needle.lower() in line.lower():
            return f"{path.relative_to(ROOT).as_posix()}:{number}"
    return None


def main() -> int:
    ding_text = DING_TEXT.read_text(encoding="utf-8") if DING_TEXT.is_file() else ""
    package = json.loads(MP48_PACKAGE.read_text(encoding="utf-8-sig"))
    audit = json.loads(MP48_AUDIT.read_text(encoding="utf-8-sig"))

    checks = {
        "ding_source_text_present": DING_TEXT.is_file(),
        "ding_defines_mode_specific_heat_capacity": "mode-specific heat capacity" in ding_text.lower(),
        "ding_defines_mode_sum": "summation over all the phonon modes" in ding_text.lower(),
        "ding_temperature_response_is_pbte": "temperature response calculation" in ding_text.lower(),
        "mp48_audit_passes": audit.get("status") == "PASS_INDEPENDENT_NUMERIC_CV_WITH_EPISTEMIC_ENVELOPE",
        "mp48_is_independent_reproduction_lane": package.get("major_result", {}).get("data_role") == "INDEPENDENT_REPRODUCTION_NOT_CALIBRATION",
        "mp48_has_numeric_volumetric_cv_rows": bool(package.get("representative_rows")),
        "mp48_holdout_excluded": package.get("holdout_policy", {}).get("xie_2026_accessed") is False,
        "mp48_alpha_fit_excluded": package.get("holdout_policy", {}).get("alpha_fit_used") is False,
        "mp48_declares_no_uet_energy_anchor": package.get("unit_contract", {}).get("no_UET_energy_anchor") is True,
        "mp48_declares_ding_c_src_open": any(
            "Ding-specific PBTE" in item
            for item in package.get("major_result", {}).get("open_blockers", [])
        ),
    }

    result = {
        "schema_version": "t13-ding-c-src-independent-reproduction-boundary-v1",
        "artifact": "t13_ding_c_src_independent_reproduction_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": "PASS_SCOPED_INDEPENDENT_CV_NOT_DING_C_SRC" if all(checks.values()) else "FAIL_DING_C_SRC_REPRODUCTION_BOUNDARY_AUDIT",
        "major_result": {
            "major_result_id": "T13_DING_C_SRC_INDEPENDENT_REPRODUCTION_BOUNDARY",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": "CLOSED_FOR_LANE" if all(checks.values()) else "OPEN",
            "what_is_closed": [
                "the MP48 package is accepted as an independent harmonic graphite c_v comparator with numeric rows and provenance",
                "Ding's C_src boundary is identified as a PBTE mode-specific heat-capacity quantity rather than an unqualified c_v alias",
                "MP48 is explicitly prevented from silently replacing Ding C_src or calibrating alpha_Phi_K",
            ],
            "equation_or_mapping": {
                "ding_mode_sum": "C_src(T) = sum_mu c_mu(T)",
                "ding_temperature_response": "Delta_Tq = Delta_u_ph / C_src",
                "mp48_comparator": "C_v^vol(T) = C_v^mol,cell(T) / V_mol,cell",
            },
            "units": {
                "ding_C_src": "J m^-3 K^-1",
                "mp48_source": "J K^-1 mol^-1 primitive cell",
                "mp48_derived": "J m^-3 K^-1",
            },
            "derivation_class": "source qualification and non-equivalence boundary; no UET derivation",
            "observable": "Ding PBTE quasi-temperature response versus independent harmonic graphite heat-capacity comparator",
            "data_role": "INDEPENDENT_REPRODUCTION_BOUNDARY_NOT_CALIBRATION",
            "evidence_artifacts": [
                {"path": str(OUT.relative_to(ROOT)).replace("\\", "/")},
                {"path": str(MP48_PACKAGE.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(MP48_PACKAGE)},
                {"path": str(MP48_AUDIT.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(MP48_AUDIT)},
                {"path": str(DING_TEXT.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(DING_TEXT)},
            ],
            "verification_status": "PASS_SCOPED_INDEPENDENT_CV_NOT_DING_C_SRC" if all(checks.values()) else "FAIL_DING_C_SRC_REPRODUCTION_BOUNDARY_AUDIT",
            "open_blockers": [
                "ding_C_src_mode_resolved_PBTE_reproduction_or_author_numeric_package_missing",
                "Ding_material_regime_and_temperature_volume_mapping_to_independent_c_v_missing",
                "Ding_C_src_convergence_and_uncertainty_contract_missing",
                "base_Phi_to_Delta_u_ph_mapping_and_alpha_Phi_K_missing",
            ] if all(checks.values()) else ["boundary_audit_checks_failed"],
            "dependency_unlocked": "independent harmonic c_v comparator boundary only; no full-source, alpha, transport, Core, or Gravity unlock",
            "claim_boundary": "MP48 is a source-traceable independent harmonic c_v comparator. It is not Ding's PBTE C_src, not an accepted Ding reproduction, not a base-Phi calibration, and not external validation of UET.",
        },
        "source_locators": {
            "ding_mode_specific_heat_capacity": line_locator(DING_TEXT, "mode-specific heat capacity"),
            "ding_mode_sum": line_locator(DING_TEXT, "summation over all the phonon modes"),
            "ding_temperature_response": line_locator(DING_TEXT, "Temperature response calculation"),
        },
        "checks": checks,
        "mp48": {
            "package_path": str(MP48_PACKAGE.relative_to(ROOT)).replace("\\", "/"),
            "package_sha256": digest(MP48_PACKAGE),
            "audit_path": str(MP48_AUDIT.relative_to(ROOT)).replace("\\", "/"),
            "audit_sha256": digest(MP48_AUDIT),
            "source_id": package.get("source", {}).get("source_id"),
            "doi": package.get("source", {}).get("doi"),
            "temperature_rows": [row.get("temperature_K") for row in package.get("representative_rows", [])],
            "data_role": package.get("major_result", {}).get("data_role"),
        },
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_controller": "Obtain Ding mode-resolved C_src(T) or build an accepted PBTE reproduction with material-regime, convergence, uncertainty, and unit contracts; do not relabel MP48 c_v or use it to fit alpha_Phi_K.",
        "claim_boundary": "This result closes a source-equivalence boundary only. Full Topic 13 remains blocked on accepted C_src, independent alpha, non-circular bridge/beta, EOS/transport/KMS/entropy, and dimensional observable mapping.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks_pass": all(checks.values()), "controlling_blocker": result["controlling_blocker"]}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
