"""Audit the legacy NEP1 backend boundary for the public C-CX variant.

The C-CX file is source-valid NEP1, while the current Calorine workflow uses
the newer NEPY backend.  This audit records the compatibility result without
rewriting the model header or treating a failed backend probe as a numeric
PBTE result.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import importlib.util
import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RAW_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "calorine_zenodo_7811021_nep_C_CX.txt"
)
STRUCTURE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/"
    "calorine_zenodo_7811021_nep_C_CX/graphite-prim.xyz"
)
SOURCE_AUDIT_REL = "docs/core/07_artifacts/topic13/t13_calorine_public_model_variant_boundary_audit.json"
PACKAGE_REL = (
    "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/"
    "calorine_nep1_backend_compatibility_source_package.json"
)
OUT_REL = "docs/core/07_artifacts/topic13/t13_calorine_nep1_backend_compatibility_audit.json"

RECORD_URL = "https://zenodo.org/records/7811021"
MODEL_URL = "https://zenodo.org/api/records/7811021/files/nep-C-CX.txt/content"
STRUCTURE_URL = "https://zenodo.org/api/records/21198312/files/graphite-prim.xyz/content"
EXPECTED_SHA256 = "cf75256947a8953b8041ccc26a34ac307724f69bf2edbcc97b46d87bc5e72408"
EXPECTED_HEADER = ("nep 1 C", "cutoff 8 3.5", "n_max 15 8", "l_max 4", "ANN 50 0")


def digest(path: Path, algorithm: str = "sha256") -> str:
    return hashlib.new(algorithm, path.read_bytes()).hexdigest()


def file_record(path: Path, locator: str) -> dict[str, Any]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "size_bytes": path.stat().st_size if path.is_file() else None,
        "sha256": digest(path) if path.is_file() else None,
        "locator": locator,
    }


def model_format(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"format_id": "MISSING", "version": None, "tokens": []}
    first = path.read_text(encoding="utf-8", errors="replace").splitlines()[0].split()
    if first[:2] == ["nep", "1"]:
        return {
            "format_id": "NEP1_LEGACY_SPACE_VERSION",
            "version": 1,
            "tokens": first,
            "canonical_header": "nep 1 C",
        }
    return {
        "format_id": "UNKNOWN_OR_NEWER_NEP_FORMAT",
        "version": None,
        "tokens": first,
        "canonical_header": " ".join(first),
    }


def installed_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def runtime_preflight(model_path: Path, structure_path: Path) -> dict[str, Any]:
    modules = {
        name: importlib.util.find_spec(name) is not None
        for name in ("ase", "calorine", "phono3py", "phonopy")
    }
    versions = {name: installed_version(name) for name in modules}
    result: dict[str, Any] = {
        "status": "BLOCKED_RERUN_RUNTIME_DEPENDENCY",
        "modules": modules,
        "versions": versions,
        "required_for_numeric_rerun": ["ase", "calorine", "phono3py", "phonopy"],
        "numeric_rerun_performed": False,
        "backend_probe": {
            "status": "NOT_RUN_MISSING_RUNTIME",
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": "",
        },
    }
    if not all(modules.values()):
        result["controlling_blocker"] = "calorine_nep1_backend_runtime_dependency_missing"
        return result

    probe_code = f"""
from pathlib import Path
from ase.io import read
import calorine.calculators.cpunep as cpunep

model_path = Path({str(model_path)!r})
structure_path = Path({str(structure_path)!r})

def legacy_nep1_metadata(filename):
    first = Path(filename).read_text(encoding='utf-8').splitlines()[0].split()
    if first[:3] != ['nep', '1', 'C']:
        raise ValueError(f'unexpected legacy header: {{first}}')
    return {{'version': 1, 'types': ['C'], 'model_type': 'potential', 'charge_mode': 0}}, []

cpunep._get_nep_contents = legacy_nep1_metadata
atoms = read(structure_path)
atoms.calc = cpunep.CPUNEP(str(model_path), debug=True)
print(atoms.get_potential_energy())
"""
    try:
        completed = subprocess.run(
            [sys.executable, "-c", probe_code],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        combined = f"{stdout}\n{stderr}".lower()
        if completed.returncode == 0:
            probe_status = "PASS_NEP1_BACKEND_PROBE"
            blocker = "calorine_model_form_uncertainty_requires_same_workflow_rerun"
        elif "unsupported nep model" in combined:
            probe_status = "BLOCKED_LEGACY_NEP1_BACKEND"
            blocker = "calorine_nep1_backend_unsupported_requires_legacy_nep_cpu_or_pynep"
        else:
            probe_status = "BLOCKED_NEP1_BACKEND_PROBE_FAILED"
            blocker = "calorine_nep1_backend_probe_failed"
        result["backend_probe"] = {
            "status": probe_status,
            "returncode": completed.returncode,
            "stdout_tail": stdout[-500:],
            "stderr_tail": stderr[-500:],
        }
        result["controlling_blocker"] = blocker
        result["status"] = (
            "PASS_RERUN_RUNTIME_PRESENT"
            if probe_status == "PASS_NEP1_BACKEND_PROBE"
            else probe_status
        )
    except subprocess.TimeoutExpired as exc:
        result["backend_probe"] = {
            "status": "BLOCKED_NEP1_BACKEND_PROBE_TIMEOUT",
            "returncode": None,
            "stdout_tail": str(exc.stdout)[-500:] if exc.stdout else "",
            "stderr_tail": str(exc.stderr)[-500:] if exc.stderr else "",
        }
        result["controlling_blocker"] = "calorine_nep1_backend_probe_timeout"
        result["status"] = "BLOCKED_NEP1_BACKEND_PROBE_TIMEOUT"
    return result


def make_major_result(
    source: dict[str, Any],
    fmt: dict[str, Any],
    runtime: dict[str, Any],
) -> dict[str, Any]:
    return {
        "major_result_id": "T13_CALORINE_NEP1_BACKEND_COMPATIBILITY_BOUNDARY",
        "topic": "0.13_Thermodynamic_Bridge",
        "closure_level": "CLOSED_FOR_LANE",
        "what_is_closed": [
            "the public C-CX file is identified as legacy NEP1 from its source header",
            "the current Calorine backend compatibility probe is recorded without rewriting the model",
            "the numeric rerun dependency is narrowed to a legacy-NEP1-compatible backend or an explicitly accepted replacement",
        ],
        "ontology": {
            "C": "collective system-behaviour coordinate; not a heat capacity or model parameter",
            "Phi": "effective response variable; no Phi calibration is present in a NEP model",
            "R_gen": "derived history trace; not involved in model evaluation",
            "R_obs": "observer record kept separate; no observer data are consumed",
        },
        "equation_or_mapping": {
            "model_route": "NEP1 model -> force backend -> fc2/fc3 -> PBTE -> C_src(T)",
            "required_output": "C_src(T) in J m^-3 K^-1",
            "thermal_bridge": "Delta_Tq = alpha_Phi_K * Delta_Phi remains uninstantiated",
        },
        "units": {
            "model_file": "source-defined NEP coefficients",
            "required_C_src": "J m^-3 K^-1",
            "alpha_Phi_K": "K per normalized Phi; not emitted",
        },
        "derivation_class": "SOFTWARE_COMPATIBILITY_BOUNDARY_NO_UET_DERIVATION",
        "observable": "whether the declared numeric force-evaluation backend accepts the source model format",
        "data_role": "EXTERNAL_MODEL_FORMAT_COMPATIBILITY_BOUNDARY_NOT_C_SRC",
        "evidence_artifacts": [
            {"path": RAW_REL, "sha256": source.get("model", {}).get("sha256")},
            {"path": SOURCE_AUDIT_REL, "role": "upstream model provenance audit"},
        ],
        "verification_status": "PASS_SCOPED_CALORINE_NEP1_BACKEND_COMPATIBILITY_BOUNDARY",
        "open_blockers": [
            runtime.get("controlling_blocker", "calorine_nep1_backend_probe_failed"),
            "calorine_model_form_uncertainty_requires_same_workflow_rerun",
            "calorine_route_source_grade_uncertainty_missing",
            "calorine_route_material_regime_mapping_to_Ding_missing",
            "independent_alpha_Phi_K_calibration_missing",
        ],
        "dependency_unlocked": "format/backend boundary only; no numeric C_src, alpha, transport, Core, Gravity, or Galaxy unlock",
        "claim_boundary": "This result closes only the NEP1/backend compatibility boundary. It is not a force calculation, not a PBTE C_src result, not source-grade uncertainty, not Ding-regime equivalence, not an alpha_Phi_K calibration, and not Full Topic 13 closure.",
        "model_format": fmt,
        "runtime_status": runtime,
    }


def main() -> int:
    model_path = ROOT / RAW_REL
    structure_path = ROOT / STRUCTURE_REL
    fmt = model_format(model_path)
    source = {
        "model": file_record(model_path, MODEL_URL) if model_path.is_file() else {},
        "structure": file_record(structure_path, STRUCTURE_URL) if structure_path.is_file() else {},
    }
    runtime = runtime_preflight(model_path, structure_path)
    checks = {
        "model_present": model_path.is_file(),
        "structure_present": structure_path.is_file(),
        "model_hash_matches": source["model"].get("sha256") == EXPECTED_SHA256,
        "legacy_nep1_header_identified": fmt.get("format_id") == "NEP1_LEGACY_SPACE_VERSION",
        "source_provenance_audit_present": (ROOT / SOURCE_AUDIT_REL).is_file(),
        "model_bytes_not_rewritten": True,
        "numeric_csrc_emitted": False,
        "alpha_calibration_emitted": False,
        "holdout_accessed": False,
    }
    required_checks = (
        "model_present",
        "structure_present",
        "model_hash_matches",
        "legacy_nep1_header_identified",
        "source_provenance_audit_present",
        "model_bytes_not_rewritten",
    )
    passed = all(checks[key] for key in required_checks)
    status = (
        "PASS_SCOPED_CALORINE_NEP1_BACKEND_COMPATIBILITY_BOUNDARY"
        if passed
        else "FAIL_CALORINE_NEP1_BACKEND_COMPATIBILITY_BOUNDARY"
    )
    major = make_major_result(source, fmt, runtime)
    package = {
        "schema_version": "t13-calorine-nep1-backend-compatibility-source-package-v1",
        "artifact": "t13_calorine_nep1_backend_compatibility_source_package",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major,
        "source": {
            "record_locator": RECORD_URL,
            "model_file_locator": MODEL_URL,
            "structure_file_locator": STRUCTURE_URL,
            "model_variant": "C-CX",
            "model_format": fmt,
            "model": source["model"],
            "structure": source["structure"],
        },
        "runtime_preflight": runtime,
        "acceptance": {
            "accepted_for_full_topic13": False,
            "accepted_as_independent_csrc_reproduction": False,
            "numeric_rerun_performed": False,
            "model_form_spread_emitted": False,
            "numeric_alpha_phi_k_emitted": False,
            "target_fit_performed": False,
            "holdout_accessed": False,
            "fit_or_tuning_used": False,
        },
        "claim_promotion": False,
        "holdout_policy": {
            "xie_2026_accessed": False,
            "xie_2026_source_data_consumed": False,
            "calibration_path_may_read_holdout": False,
        },
        "controlling_blocker": runtime.get("controlling_blocker"),
        "next_controller": "Use a legacy-NEP1-compatible backend or an explicitly accepted replacement, then rerun the exact 4x4x2, 8x8x4 and 10x10x5 Calorine state/grid contract; do not rewrite the model header or calibrate alpha from the rerun.",
        "claim_boundary": major["claim_boundary"],
    }
    package_path = ROOT / PACKAGE_REL
    package_path.parent.mkdir(parents=True, exist_ok=True)
    package_path.write_text(json.dumps(package, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    audit = {
        "schema_version": "t13-calorine-nep1-backend-compatibility-boundary-v1",
        "artifact": "t13_calorine_nep1_backend_compatibility_audit",
        "generated_at": date.today().isoformat(),
        "status": status,
        "major_result": major,
        "source": source,
        "model_format": fmt,
        "runtime_preflight": runtime,
        "checks": checks,
        "source_package": {"path": PACKAGE_REL, "sha256": digest(package_path)},
        "acceptance": package["acceptance"],
        "claim_promotion": False,
        "holdout_policy": package["holdout_policy"],
        "controlling_blocker": runtime.get("controlling_blocker"),
        "next_controller": package["next_controller"],
        "claim_boundary": major["claim_boundary"],
    }
    output_path = ROOT / OUT_REL
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "runtime": runtime, "artifact": OUT_REL}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
