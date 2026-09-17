"""Audit a pinned legacy Calorine NEP2 backend probe for the public C-CX model.

This lane records a source-linked model/backend compatibility result.  It does
not convert forces into force constants, PBTE heat capacity, or a Phi bridge.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
MODEL_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "calorine_zenodo_7811021_nep_C_CX.txt"
)
STRUCTURE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "calorine_zenodo_7811021_nep_C_CX/graphite-prim.xyz"
)
RECEIPT_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "calorine_legacy_nep2_backend_probe_receipt.txt"
)
PACKAGE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "calorine_legacy_nep2_backend_probe_source_package.json"
)
OUT_REL = "docs/core/07_artifacts/topic13/t13_calorine_legacy_nep2_backend_probe_audit.json"

MODEL_URL = "https://zenodo.org/api/records/7811021/files/nep-C-CX.txt/content"
STRUCTURE_URL = "https://zenodo.org/api/records/21198312/files/graphite-prim.xyz/content"
BACKEND_URL = "https://gitlab.com/materials-modeling/calorine/-/tree/1.0"
BACKEND_TAG = "1.0"
BACKEND_COMMIT = "eedb2ac9f49cb60a64512e987b98993d3a44e186"
MODEL_SHA256 = "cf75256947a8953b8041ccc26a34ac307724f69bf2edbcc97b46d87bc5e72408"
STRUCTURE_SHA256 = "87fdd172bd5b77e1aa5bd9b4d85c3f21eb5df6521089cc4b769e12d481a1aed0"
RECEIPT_SHA256 = "5ecf57f7cf2ae9bb306af28d9b3001f9f8a6d5cdde2173d9c84c270041ece7e1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_record(path: Path, locator: str) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "size_bytes": path.stat().st_size if path.is_file() else None,
        "sha256": digest(path) if path.is_file() else None,
        "locator": locator,
    }


def parse_receipt(path: Path) -> dict[str, Any]:
    text = (
        path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        if path.is_file()
        else ""
    )

    def match(pattern: str) -> str | None:
        found = re.search(pattern, text, re.MULTILINE)
        return found.group(1) if found else None

    observed = {
        "source_commit": match(r"^source_commit:\s*(\S+)$"),
        "source_tag": match(r"^source_tag:\s*(\S+)$"),
        "model_sha256": match(r"^model_sha256:\s*(\S+)$"),
        "structure_sha256": match(r"^structure_sha256:\s*(\S+)$"),
        "returncode": match(r"^returncode:\s*(\d+)$"),
        "total_potential_eV": match(r"^total_potential_eV\s+([-+0-9.eE]+)$"),
        "potential_count": match(r"^potential_count\s+(\d+)$"),
        "force_l2": match(r"^force_l2\s+([-+0-9.eE]+)$"),
        "virial_count": match(r"^virial_count\s+(\d+)$"),
    }
    checks = {
        "receipt_present": path.is_file(),
        "receipt_hash_matches": path.is_file() and digest(path) == RECEIPT_SHA256,
        "legacy_backend_commit_matches": observed["source_commit"] == BACKEND_COMMIT,
        "legacy_backend_tag_matches": observed["source_tag"] == BACKEND_TAG,
        "model_hash_matches": observed["model_sha256"] == MODEL_SHA256,
        "structure_hash_matches": observed["structure_sha256"] == STRUCTURE_SHA256,
        "returncode_zero": observed["returncode"] == "0",
        "nep2_header_accepted": "Use the NEP2 potential" in text,
        "potential_count_matches": observed["potential_count"] == "4",
        "force_diagnostic_present": observed["force_l2"] is not None,
        "virial_count_matches": observed["virial_count"] == "36",
    }
    return {
        "status": (
            "PASS_LEGACY_NEP2_MODEL_PROBE"
            if all(checks.values())
            else "FAIL_LEGACY_NEP2_MODEL_PROBE_RECEIPT"
        ),
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(path) if path.is_file() else None,
        "backend": {
            "locator": BACKEND_URL,
            "tag": BACKEND_TAG,
            "commit": BACKEND_COMMIT,
            "engine": "Calorine 1.0 legacy NEP3 class, NEP2 model branch",
            "source_files": [
                {
                    "upstream_path": "src/nepy/nep.cpp",
                    "sha256": "433a919d15b320d8d301f8b7c345762cbf4a2bd99133521a94470f8df8a2ddb3",
                },
                {
                    "upstream_path": "src/nepy/nep.h",
                    "sha256": "44a9eb6adb871b5f0e7af89b0d5ac79481f1c0c0032813f90177153983c6ddf7",
                },
            ],
        },
        "observed": observed,
        "checks": checks,
        "execution": {
            "environment": "Ubuntu 24.04 WSL2, Python 3.12.3, GCC 13.3",
            "compile_contract": "g++ -std=c++11 -O3 -fopenmp legacy_probe.cpp nep.cpp",
            "binary_sha256": "dc6e65c21b4b5d090f66ab88fea3c12da54126b04ab657517c51021df7976580",
            "probe_kind": "four-atom graphite primitive-cell force evaluation",
            "fit_or_tuning_used": False,
        },
    }


def major_result(source: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "major_result_id": "T13_CALORINE_LEGACY_NEP2_BACKEND_PROBE",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": [
            "the hash-locked public C-CX model and graphite primitive structure are accepted by a pinned legacy Calorine 1.0 NEP2 engine",
            "the backend route is source-linked to Calorine tag 1.0 and commit eedb2ac9f49cb60a64512e987b98993d3a44e186",
            "the four-atom force probe completed without rewriting the C-CX model bytes",
        ],
        "what_remains_open": [
            "same-workflow fc2/fc3 generation and exact 4x4x2, 8x8x4, 10x10x5 PBTE rerun",
            "source-grade C_src uncertainty and Ding material/regime equivalence",
            "independent base-Phi SI anchor and alpha_Phi_K calibration",
        ],
        "ontology": {
            "C": "collective system-behaviour coordinate; not heat capacity or model parameter",
            "Phi": "effective response variable; no Phi calibration is present in this backend probe",
            "R_gen": "derived history trace; not involved in model evaluation",
            "R_obs": "observer record kept separate; no observer data are consumed",
        },
        "equation_or_mapping": {
            "model_route": "NEP2 model -> force backend -> fc2/fc3 -> PBTE -> C_src(T)",
            "required_output": "C_src(T) in J m^-3 K^-1",
            "thermal_bridge": "Delta_Tq = alpha_Phi_K * Delta_Phi remains uninstantiated",
        },
        "units": {
            "probe_energy": "eV",
            "probe_force_diagnostic": "source/backend diagnostic; no SI transport unit emitted",
            "required_C_src": "J m^-3 K^-1",
            "alpha_Phi_K": "K per normalized Phi; not emitted",
        },
        "derivation_class": "SOFTWARE_COMPATIBILITY_BOUNDARY_NO_UET_DERIVATION",
        "observable": "whether the pinned legacy force backend accepts the source model format",
        "data_role": "EXTERNAL_MODEL_BACKEND_PROBE_NOT_C_SRC",
        "evidence_artifacts": [
            {"path": MODEL_REL, "sha256": source["model"]["sha256"]},
            {"path": STRUCTURE_REL, "sha256": source["structure"]["sha256"]},
            {"path": RECEIPT_REL, "sha256": receipt["sha256"]},
        ],
        "verification_status": receipt["status"],
        "open_blockers": [
            "calorine_legacy_backend_same_workflow_pbte_rerun_missing",
            "calorine_route_source_grade_uncertainty_missing",
            "calorine_route_material_regime_mapping_to_Ding_missing",
            "independent_alpha_Phi_K_calibration_missing",
        ],
        "dependency_unlocked": "legacy force-backend route only; no numeric C_src, alpha, transport, Core, Gravity, or Galaxy unlock",
        "claim_boundary": "This result closes only the legacy force-backend compatibility lane. It is not a PBTE C_src result, not source-grade uncertainty, not Ding-regime equivalence, not an alpha_Phi_K calibration, and not Full Topic 13 closure.",
    }


def main() -> int:
    model = ROOT / MODEL_REL
    structure = ROOT / STRUCTURE_REL
    receipt_path = ROOT / RECEIPT_REL
    source = {
        "model": file_record(model, MODEL_URL) if model.is_file() else {},
        "structure": file_record(structure, STRUCTURE_URL) if structure.is_file() else {},
    }
    receipt = parse_receipt(receipt_path)
    checks = {
        "model_present": model.is_file(),
        "structure_present": structure.is_file(),
        "model_hash_matches": source.get("model", {}).get("sha256") == MODEL_SHA256,
        "structure_hash_matches": source.get("structure", {}).get("sha256") == STRUCTURE_SHA256,
        "receipt_status_pass": receipt["status"] == "PASS_LEGACY_NEP2_MODEL_PROBE",
        "holdout_accessed": False,
        "numeric_csrc_emitted": False,
        "numeric_alpha_phi_k_emitted": False,
        "fit_or_tuning_used": False,
    }
    required = (
        "model_present",
        "structure_present",
        "model_hash_matches",
        "structure_hash_matches",
        "receipt_status_pass",
    )
    passed = all(checks[key] for key in required)
    status = (
        "PASS_SCOPED_CALORINE_LEGACY_NEP2_BACKEND_PROBE"
        if passed
        else "FAIL_CALORINE_LEGACY_NEP2_BACKEND_PROBE"
    )
    major = major_result(source, receipt)
    package = {
        "schema_version": "t13-calorine-legacy-nep2-backend-probe-source-package-v1",
        "artifact": "t13_calorine_legacy_nep2_backend_probe_source_package",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major,
        "source": {
            "model": source.get("model", {}),
            "structure": source.get("structure", {}),
            "backend": receipt["backend"],
            "receipt": {
                "path": RECEIPT_REL,
                "sha256": receipt["sha256"],
            },
        },
        "runtime_probe": receipt,
        "acceptance": {
            "accepted_for_full_topic13": False,
            "accepted_as_independent_csrc_reproduction": False,
            "legacy_backend_model_probe_performed": passed,
            "numeric_rerun_performed": False,
            "numeric_csrc_emitted": False,
            "numeric_alpha_phi_k_emitted": False,
            "holdout_accessed": False,
            "fit_or_tuning_used": False,
        },
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "calibration_path_may_read_holdout": False,
        },
        "controlling_blocker": "calorine_legacy_backend_same_workflow_pbte_rerun_missing",
        "next_controller": "Run the exact 4x4x2 state and 8x8x4/10x10x5 mesh workflow with this pinned legacy backend, then package fc2/fc3, mode-resolved C_src, convergence, and source-grade uncertainty; do not calibrate alpha from the rerun.",
        "claim_boundary": major["claim_boundary"],
    }
    package_path = ROOT / PACKAGE_REL
    package_path.parent.mkdir(parents=True, exist_ok=True)
    package_path.write_text(json.dumps(package, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    artifact = {
        "schema_version": "t13-calorine-legacy-nep2-backend-probe-v1",
        "artifact": "t13_calorine_legacy_nep2_backend_probe_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major,
        "source": source,
        "runtime_probe": receipt,
        "checks": checks,
        "source_package": {"path": PACKAGE_REL, "sha256": digest(package_path)},
        "acceptance": package["acceptance"],
        "claim_promotion": False,
        "holdout_policy": package["holdout_policy"],
        "controlling_blocker": package["controlling_blocker"],
        "next_controller": package["next_controller"],
        "claim_boundary": major["claim_boundary"],
    }
    output_path = ROOT / OUT_REL
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "artifact": OUT_REL, "receipt": receipt}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
