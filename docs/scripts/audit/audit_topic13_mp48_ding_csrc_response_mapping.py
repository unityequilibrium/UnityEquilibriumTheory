"""Audit the standard mode-sum response mapping used by Topic 13.

This lane connects the source-located Ding mode-capacity notation to the
independent MP48 harmonic mode sum and an explicit volumetric unit conversion.
It does not accept MP48 as Ding PBTE data, infer alpha_Phi_K, or consume the
locked holdout.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw"
DING_TEXT = RAW / "ding_2022_pmc_full_text.txt"
MESH_ARTIFACT = ROOT / "docs/core/artifacts/t13_mp48_force_constant_csrc_mesh_convergence_audit.json"
SOURCE_PACKAGE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/mp48_independent_graphite_cv_source_package.json"
OUT = ROOT / "docs/core/artifacts/t13_mp48_ding_csrc_response_mapping_audit.json"

RESULT_ID = "T13_MP48_DING_C_SRC_MODE_SUM_RESPONSE_MAPPING"
STATUS = "PASS_T13_DING_C_SRC_MODE_SUM_RESPONSE_MAPPING"
SELECTED_MESH = "35x35x14"
REQUIRED_DING_LOCATORS = (
    "mode-specific heat capacity",
    "summation over all the phonon modes",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def locate(path: Path, needle: str) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, start=1):
        if needle in line:
            return {
                "path": relative(path),
                "line": line_number,
                "needle": needle,
                "sha256": sha256(path),
            }
    raise ValueError(f"source locator not found: {needle}")


def finite_positive(value: object) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and float(value) > 0.0


def main() -> int:
    mesh = json.loads(MESH_ARTIFACT.read_text(encoding="utf-8-sig"))
    package = json.loads(SOURCE_PACKAGE.read_text(encoding="utf-8-sig"))
    ding_locators = [locate(DING_TEXT, needle) for needle in REQUIRED_DING_LOCATORS]

    mesh_rows = mesh["mesh_results"][SELECTED_MESH]["rows"]
    volume = float(package["experimental_volume_anchor"]["molar_primitive_cell_volume_m3_per_mol"])
    if not finite_positive(volume):
        raise ValueError("MP48 molar primitive-cell volume must be positive")

    derived_rows = []
    for row in mesh_rows:
        temperature = float(row["temperature_K"])
        molar_capacity = float(row["heat_capacity_J_per_mol_cell_K"])
        volumetric_capacity = molar_capacity / volume
        if not finite_positive(volumetric_capacity):
            raise ValueError("derived volumetric C_src row is not finite and positive")
        derived_rows.append(
            {
                "temperature_K": temperature,
                "heat_capacity_J_per_mol_cell_K": molar_capacity,
                "c_src_volumetric_J_per_m3_K": volumetric_capacity,
                "row_identity": f"mp48_force_constant_mode_sum_{SELECTED_MESH}",
            }
        )

    source_files = []
    for source_path, expected_hash in (
        (RAW / "mp48_FORCE_CONSTANTS.gz", mesh["source"]["force_constants_sha256"]),
        (RAW / "mp48_phonopy.yaml.gz", mesh["source"]["phonopy_metadata_sha256"]),
    ):
        observed_hash = sha256(source_path)
        if observed_hash != expected_hash:
            raise ValueError(f"source hash mismatch: {relative(source_path)}")
        source_files.append(
            {
                "path": relative(source_path),
                "sha256": observed_hash,
                "role": "mode-frequency-input",
            }
        )

    checks = {
        "ding_mode_capacity_locator_present": len(ding_locators) == len(REQUIRED_DING_LOCATORS),
        "mp48_mesh_artifact_status_is_converged_harmonic_lane": mesh["status"] == "PASS_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE",
        "selected_mesh_is_declared": SELECTED_MESH in mesh["mesh_results"],
        "selected_mesh_rows_are_finite_positive": len(derived_rows) == len(mesh_rows)
        and all(finite_positive(row["c_src_volumetric_J_per_m3_K"]) for row in derived_rows),
        "volume_anchor_is_source_package_locked": package["unit_contract"]["no_Cp_to_Cv_correction"] is True,
        "force_constant_and_phonopy_hashes_match": all(source["sha256"] for source in source_files),
        "route_wide_convergence_is_not_silently_promoted": mesh["mesh_policy"]["continuum_convergence_required_for_Ding_acceptance"] is True,
        "numeric_alpha_Phi_K_not_emitted": not mesh.get("numeric_alpha_Phi_K_emitted", False),
        "target_fit_not_performed": not mesh.get("target_fit_performed", False),
        "holdout_not_accessed": not mesh.get("holdout_accessed", False),
    }
    if not all(checks.values()):
        raise ValueError(f"mapping checks failed: {checks}")

    major_result = {
        "major_result_id": RESULT_ID,
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": [
            "the Ding source locator explicitly identifies mode-specific heat capacity and the summation over phonon modes",
            "the standard harmonic mode-sum response mapping is declared without relabeling MP48 as Ding PBTE data",
            "the existing MP48 force-constant mode sum is converted from J K^-1 mol^-1 primitive cell to J m^-3 K^-1 using the locked volume anchor",
            "the response identity Delta_Tq = Delta_u_ph / C_src is kept separate from any Phi-to-energy or alpha_Phi_K calibration",
        ],
        "equation_or_mapping": {
            "ding_mode_quantity": "C_q is the mode-specific heat capacity; the source states that the angle-bracket sum is over all phonon modes",
            "mode_sum": "C_src^mol(T) = N_A/N_q * sum_(q,mu) c_mu(q,T)",
            "mode_kernel": "c_mu(T) = k_B*x_mu^2*exp(x_mu)/(exp(x_mu)-1)^2; x_mu=h*nu_mu/(k_B*T)",
            "volumetric_conversion": "C_src^vol(T) = C_src^mol(T) / V_mol,cell",
            "thermal_response": "Delta_Tq = Delta_u_ph / C_src^vol",
            "mapping_scope": "standard harmonic response mapping only; not Ding PBTE acceptance",
        },
        "units": {
            "mode_capacity": "J K^-1 per mode",
            "molar_capacity": "J K^-1 mol^-1 primitive cell",
            "volume": "m^3 mol^-1 primitive cell",
            "volumetric_capacity": "J m^-3 K^-1",
            "temperature": "K",
        },
        "derivation_class": "source-located standard-physics mode-sum mapping plus independent harmonic force-constant reproduction and explicit unit conversion; no UET derivation",
        "observable": "independent MP48 harmonic mode-sum C_src comparator in volumetric units",
        "data_role": "STANDARD_RESPONSE_MAPPING_NOT_DING_ACCEPTANCE",
        "evidence_artifacts": [
            {"path": relative(DING_TEXT), "sha256": sha256(DING_TEXT), "locators": ding_locators},
            {"path": relative(MESH_ARTIFACT), "sha256": sha256(MESH_ARTIFACT)},
            {"path": relative(SOURCE_PACKAGE), "sha256": sha256(SOURCE_PACKAGE)},
            *source_files,
        ],
        "verification_status": STATUS,
        "open_blockers": [
            "Ding-compatible PBTE numeric C_src or accepted same-regime independent reproduction is still missing",
            "MP48 material/state equivalence, route-wide convergence, and source-grade uncertainty are still open",
            "base Phi-to-energy mapping and independent alpha_Phi_K are still open",
            "EOS, covariant transport, SK/KMS, entropy current, and dissipative balance remain open",
        ],
        "dependency_unlocked": "Only the explicit C_q-to-C_src response-mapping lane; no Ding-source, alpha, Full Topic 13, Core, Gravity, or transport dependency unlock",
        "claim_boundary": "This closes a standard response-mapping contract for an independent harmonic comparator. It is not Ding PBTE C_src acceptance, same-regime material validation, a Phi-to-temperature prediction, alpha_Phi_K calibration, or Full Topic 13 closure.",
    }

    artifact = {
        "schema_version": "t13-mp48-ding-csrc-response-mapping-v1",
        "artifact": "t13_mp48_ding_csrc_response_mapping_audit",
        "generated_at": date.today().isoformat(),
        "status": STATUS,
        "major_result": major_result,
        "source": {
            "ding_text_path": relative(DING_TEXT),
            "ding_text_sha256": sha256(DING_TEXT),
            "ding_locators": ding_locators,
            "mp48_mesh_artifact": relative(MESH_ARTIFACT),
            "mp48_mesh_artifact_sha256": sha256(MESH_ARTIFACT),
            "mp48_source_package": relative(SOURCE_PACKAGE),
            "mp48_source_package_sha256": sha256(SOURCE_PACKAGE),
            "mode_input_files": source_files,
        },
        "mapping_contract": {
            "selected_mesh": SELECTED_MESH,
            "volume_anchor_m3_per_mol_primitive_cell": volume,
            "volume_anchor_source_id": package["experimental_volume_anchor"]["source_id"],
            "rows": derived_rows,
            "material_mapping_status": "OPEN",
            "source_uncertainty_status": "OPEN",
            "route_wide_convergence_status": "OPEN",
            "ding_numeric_payload_present": False,
            "accepted_for_full_topic13": False,
            "numeric_alpha_Phi_K_emitted": False,
        },
        "checks": checks,
        "holdout_accessed": False,
        "target_fit_performed": False,
        "numeric_alpha_Phi_K_emitted": False,
        "controlling_blocker": "ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing",
        "next_controller": "obtain authorized Ding-compatible numeric C_src or accepted same-regime PBTE reproduction with source-grade uncertainty and state mapping; keep alpha_Phi_K independently calibrated",
        "claim_boundary": major_result["claim_boundary"],
    }
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": STATUS, "artifact": relative(OUT), "row_count": len(derived_rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
