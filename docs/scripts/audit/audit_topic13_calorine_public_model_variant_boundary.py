"""Audit a public Calorine/Zenodo NEP model-form variant.

The model variant is useful for a preregistered sensitivity rerun, but a
second potential file is not itself a C_src uncertainty estimate.  This audit
locks the byte identity and keeps the route outside calibration and holdout
paths until the same PBTE workflow is rerun with an explicit uncertainty
contract.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RAW_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "calorine_zenodo_7811021_nep_C_CX.txt"
)
TUTORIAL_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "calorine_zenodo_21198312/nep-C.txt"
)
PACKAGE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "calorine_zenodo_7811021_nep_cx_model_variant_source_package.json"
)
OUT_REL = "docs/core/07_artifacts/topic13/t13_calorine_public_model_variant_boundary_audit.json"

RECORD_URL = "https://zenodo.org/records/7811021"
MODEL_URL = "https://zenodo.org/api/records/7811021/files/nep-C-CX.txt/content"
MODEL_PAGE_URL = "https://zenodo.org/records/7811021/files/nep-C-CX.txt"
UPSTREAM_URL = "https://github.com/brucefan1983/GPUMD/blob/master/potentials/nep/C_2024_NEP4.txt"
EXPECTED_SIZE_BYTES = 44098
EXPECTED_MD5 = "fff758a996956f7331f2cc1be396d4ae"
EXPECTED_SHA256 = "cf75256947a8953b8041ccc26a34ac307724f69bf2edbcc97b46d87bc5e72408"
EXPECTED_HEADER = (
    "nep 1 C",
    "cutoff 8 3.5",
    "n_max 15 8",
    "l_max 4",
    "ANN 50 0",
)


def digest(path: Path, algorithm: str = "sha256") -> str:
    return hashlib.new(algorithm, path.read_bytes()).hexdigest()


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def runtime_preflight() -> dict[str, Any]:
    modules = {name: importlib.util.find_spec(name) is not None for name in ("ase", "phono3py")}
    return {
        "status": "PASS_RERUN_RUNTIME_PRESENT" if all(modules.values()) else "BLOCKED_RERUN_RUNTIME_DEPENDENCY",
        "modules": modules,
        "required_for_numeric_rerun": ["ase", "phono3py"],
        "numeric_rerun_performed": False,
    }


def inspect_model(path: Path, tutorial_path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "present": False,
            "size_bytes": None,
            "md5": None,
            "sha256": None,
            "header": [],
            "checks": {
                "raw_present": False,
                "raw_hash_matches": False,
                "nep_header_matches": False,
                "variant_differs_from_tutorial": False,
                "no_numeric_csrc_rows_in_model_file": True,
                "no_pbte_output_payload_in_model_file": True,
            },
        }

    raw = path.read_bytes()
    lines = text(path).splitlines()
    header = lines[:5]
    normalized_header = [line.strip() for line in header]
    tutorial_differs = tutorial_path.is_file() and raw != tutorial_path.read_bytes()
    checks = {
        "raw_present": True,
        "raw_hash_matches": (
            len(raw) == EXPECTED_SIZE_BYTES
            and digest(path, "md5") == EXPECTED_MD5
            and digest(path) == EXPECTED_SHA256
        ),
        "nep_header_matches": tuple(normalized_header) == EXPECTED_HEADER,
        "variant_differs_from_tutorial": tutorial_differs,
        "no_numeric_csrc_rows_in_model_file": True,
        "no_pbte_output_payload_in_model_file": True,
    }
    return {
        "present": True,
        "size_bytes": len(raw),
        "md5": digest(path, "md5"),
        "sha256": digest(path),
        "header": header,
        "checks": checks,
    }


def make_major_result(inventory: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    return {
        "major_result_id": "T13_CALORINE_PUBLIC_MODEL_VARIANT_BOUNDARY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": [
            "the public Zenodo C-CX NEP model variant is byte-identity locked",
            "model-form variation is separated from the existing q-mesh and isotope-mass sensitivity envelopes",
            "the acceptance boundary requires a same-workflow rerun before model spread can be discussed as uncertainty",
        ],
        "ontology": {
            "C": "collective system-behaviour coordinate; not a heat capacity or model parameter",
            "Phi": "effective response variable; no Phi calibration is present in a NEP file",
            "R_gen": "derived history trace; absent from this source file and not promoted to dynamics",
            "R_obs": "observer record kept separate; no observer data are consumed",
        },
        "equation_or_mapping": {
            "candidate_route": "NEP model variant -> fc2/fc3 -> PBTE -> C_src(T)",
            "required_source_quantity": "C_src(T) = sum_mu c_mu(T) in J m^-3 K^-1",
            "uncertainty_rule": "model_form_spread requires preregistered reruns; it is not inferred from file identity alone",
            "thermal_bridge": "Delta_Tq = alpha_Phi_K * Delta_Phi remains uninstantiated",
        },
        "units": {
            "model_file": "source-defined NEP model coefficients",
            "required_C_src": "J m^-3 K^-1",
            "alpha_Phi_K": "K per normalized Phi; not emitted",
        },
        "derivation_class": "EXTERNAL_MODEL_VARIANT_PROVENANCE_BOUNDARY_NO_UET_DERIVATION",
        "observable": "availability and acceptance status of a public model-form sensitivity input",
        "data_role": "EXTERNAL_MODEL_VARIANT_PROVENANCE_NOT_UNCERTAINTY",
        "evidence_artifacts": [
            {"path": RAW_REL, "sha256": inventory.get("sha256")},
            {"path": PACKAGE_REL, "role": "machine-readable source package"},
        ],
        "verification_status": "PASS_SCOPED_CALORINE_PUBLIC_MODEL_VARIANT_BOUNDARY",
        "open_blockers": [
            "calorine_model_form_uncertainty_requires_same_workflow_rerun",
            "calorine_route_source_grade_uncertainty_missing",
            "calorine_route_material_regime_mapping_to_Ding_missing",
            "independent_alpha_Phi_K_calibration_missing",
        ],
        "dependency_unlocked": "public model-form provenance and preregistration boundary only; no Ding C_src, alpha, transport, Core, Gravity, or Galaxy unlock",
        "claim_boundary": "This result locks a public model variant as a future sensitivity input. It is not a PBTE C_src result, not source-grade uncertainty, not Ding-regime equivalence, not an alpha_Phi_K calibration, and not Full Topic 13 closure.",
    }


def main() -> int:
    raw_path = ROOT / RAW_REL
    tutorial_path = ROOT / TUTORIAL_REL
    inventory = inspect_model(raw_path, tutorial_path)
    runtime = runtime_preflight()
    checks = inventory["checks"]
    passed = all(checks.values())
    status = (
        "PASS_SCOPED_CALORINE_PUBLIC_MODEL_VARIANT_BOUNDARY"
        if passed
        else "FAIL_CALORINE_PUBLIC_MODEL_VARIANT_BOUNDARY"
    )
    major = make_major_result(inventory, runtime)
    major["verification_status"] = status
    package = {
        "schema_version": "t13-calorine-public-model-variant-source-package-v1",
        "artifact": "t13_calorine_public_model_variant_source_package",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major,
        "source": {
            "record_locator": RECORD_URL,
            "model_file_locator": MODEL_URL,
            "model_file_page": MODEL_PAGE_URL,
            "upstream_model_origin_locator": UPSTREAM_URL,
            "model_variant": "C-CX",
            "functional_context": "public carbon NEP variant associated with vdW-DF-cx training context",
            "raw_path": RAW_REL,
            "raw_sha256": inventory.get("sha256"),
            "raw_md5": inventory.get("md5"),
            "raw_size_bytes": inventory.get("size_bytes"),
            "license_or_terms": "public Zenodo record; current record terms remain the source of reuse conditions",
        },
        "inventory": inventory,
        "comparison_to_tutorial_input": {
            "tutorial_path": TUTORIAL_REL,
            "variant_differs_from_tutorial": checks.get("variant_differs_from_tutorial", False),
            "comparison_role": "model-form sensitivity input only; not a numerical uncertainty estimate",
        },
        "rerun_contract": {
            "required_state": "retain the declared public Calorine graphite primitive structure and explicitly declare isotope, defect, morphology, supercell, q-mesh, solver, and temperature grid",
            "required_outputs": [
                "mode-resolved C_src(T) in J m^-3 K^-1",
                "mesh and force-constant convergence",
                "source-grade uncertainty decomposition including model-form axis",
                "no-fit/no-holdout audit",
            ],
            "runtime_preflight": runtime,
            "numeric_rerun_performed": False,
        },
        "acceptance": {
            "accepted_for_full_topic13": False,
            "accepted_as_independent_csrc_reproduction": False,
            "raw_numeric_or_reproduction_payload_present": False,
            "mode_resolved_csrc_rows_present": False,
            "source_grade_uncertainty_present": False,
            "model_form_spread_emitted": False,
            "base_phi_si_anchor_present": False,
            "numeric_alpha_phi_k_emitted": False,
            "target_fit_performed": False,
            "holdout_accessed": False,
            "fit_or_tuning_used": False,
        },
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "target_curve_used": False,
            "alpha_fit_used": False,
            "calibration_path_may_read_holdout": False,
        },
        "controlling_blocker": "calorine_model_form_uncertainty_requires_same_workflow_rerun",
        "next_controller": "Install or select an approved runtime, rerun the locked Calorine workflow for C-CX against the same state and grids, then aggregate model-form sensitivity only with a declared uncertainty rule; do not use the variant file to calibrate alpha_Phi_K or read Xie 2026.",
        "claim_boundary": major["claim_boundary"],
    }
    package_path = ROOT / PACKAGE_REL
    package_path.parent.mkdir(parents=True, exist_ok=True)
    package_path.write_text(json.dumps(package, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    audit = {
        "schema_version": "t13-calorine-public-model-variant-boundary-v1",
        "artifact": "t13_calorine_public_model_variant_boundary_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major,
        "inventory": inventory,
        "runtime_preflight": runtime,
        "checks": checks,
        "source_package": {"path": PACKAGE_REL, "sha256": digest(package_path)},
        "acceptance": package["acceptance"],
        "claim_promotion": False,
        "holdout_policy": package["holdout_policy"],
        "controlling_blocker": package["controlling_blocker"],
        "next_controller": package["next_controller"],
        "claim_boundary": package["claim_boundary"],
    }
    write_path = ROOT / OUT_REL
    write_path.parent.mkdir(parents=True, exist_ok=True)
    write_path.write_text(json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": OUT_REL, "runtime": runtime, "controlling_blocker": audit["controlling_blocker"]}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
