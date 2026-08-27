"""Build the repo-wide major-result closure register from current artifacts."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CONTRACT = ROOT / "docs/core/artifacts/uet_major_result_closure_contract.json"
T13 = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
MATRIX = ROOT / "docs/core/artifacts/t13_topic13_closure_matrix.json"
OUT = ROOT / "docs/core/artifacts/uet_major_result_closure_register.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def ref(rel_path: str, summary: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / rel_path
    return {"path": rel_path, "sha256": sha256(path), "summary": summary}


def main() -> int:
    t13 = load(T13)
    matrix = load(MATRIX)
    t13_evidence = [ref(rel(T13), {"status": t13["status"], "controlling_blocker": t13["controlling_blocker"]})]
    for item in t13.get("evidence_artifacts", []):
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        if not isinstance(path, str) or path == rel(T13) or not (ROOT / path).is_file():
            continue
        if any(existing.get("path") == path for existing in t13_evidence):
            continue
        t13_evidence.append(ref(path, item.get("summary", {})))

    entries = [
        {
            "major_result_id": "CORE_ONTOLOGY_AND_RESEARCH_ROOM_CONTRACT",
            "topic": "core",
            "closure_level": "PARTIAL",
            "what_is_closed": ["lane-separated ontology contract", "equation registry fields", "dependency-gated room coordination"],
            "equation_or_mapping": "C, Phi, R_gen, and R_obs remain distinct lane records",
            "units": "normalized/natural lanes; complete SI mapping open",
            "derivation_class": "workflow and registry contract",
            "observable": "registry-linked observable/dependency records",
            "data_role": "metadata and artifact integration",
            "evidence_artifacts": [ref("docs/core/UET_RESEARCH_ROOM_BRIEF.md", {"required_report_headings": True})],
            "verification_status": "PARTIAL_FOUNDATION_CONTRACT",
            "open_blockers": ["foundation correspondence, units, accepted physical observables, and external claim gates remain open"],
            "dependency_unlocked": "parallel room hardening only",
            "claim_boundary": "candidate effective theory; no global closure",
        },
        {
            "major_result_id": "T13_FULL_THERMODYNAMIC_BRIDGE",
            "topic": "0.13_Thermodynamic_Bridge",
            "closure_level": t13["major_result"]["closure_level"],
            "what_is_closed": t13["major_result"]["what_is_closed"],
            "equation_or_mapping": t13["equation_or_mapping"],
            "units": t13["units"],
            "derivation_class": t13["derivation_class"],
            "observable": t13["observable"],
            "data_role": t13["data_role"],
            "evidence_artifacts": t13_evidence,
            "verification_status": t13["status"],
            "open_blockers": t13["major_result"]["what_remains_open"],
            "resolved_blockers": t13["major_result"].get("resolved_blockers", []),
            "dependency_unlocked": t13["major_result"]["dependency_unlocked"],
            "claim_boundary": t13["claim_boundary"],
            "closure_summary": t13["major_result"].get("closure_summary", {}),
            "closure_matrix": {
                "path": rel(MATRIX),
                "sha256": sha256(MATRIX),
                "status": matrix.get("status"),
                "closure_level": matrix.get("major_result", {}).get("closure_level"),
                "full_core_unlock": matrix.get("full_core_unlock", False),
                "required_major_result_count": matrix.get("closure_summary", {}).get(
                    "required_major_result_count"
                ),
                "required_subresult_count": matrix.get("closure_summary", {}).get(
                    "required_subresult_count"
                ),
            },
        },
        {
            "major_result_id": "CORE_O2_TREE_LEVEL_EOS_LANE",
            "topic": "core O(2)",
            "closure_level": "PARTIAL",
            "what_is_closed": ["tree-level finite-density O(2) mean-field EOS", "T=0 ideal constitutive identities"],
            "equation_or_mapping": "P(X,Phi) -> N^mu and T^mu_nu in natural units",
            "units": "natural units; SI and finite-temperature lanes open",
            "derivation_class": "tree-level mean-field derivation",
            "observable": "formal EOS and ideal constitutive control",
            "data_role": "internal derivation and external structure references",
            "evidence_artifacts": [ref("docs/core/artifacts/o2_finite_density_eos_verification.json", {"audit_status": "PASS"})],
            "verification_status": "PASS_TREE_LEVEL_PARTIAL",
            "open_blockers": ["finite-temperature normal component", "physical Kubo coefficients", "full SK/KMS", "curved 3+1", "SI lane"],
            "dependency_unlocked": "formal O(2) constraint inheritance only",
            "claim_boundary": "no full two-fluid, physical transport, or GR closure",
        },
        {
            "major_result_id": "TOPIC_0_10_STANDARD_FLUID_COMPARATOR",
            "topic": "0.10_Fluid_Dynamics_Chaos",
            "closure_level": "PARTIAL",
            "what_is_closed": ["standard-fluid comparator definition", "formula audit boundary"],
            "equation_or_mapping": "simplified comparator runtime/stability metrics",
            "units": "declared benchmark units",
            "derivation_class": "internal comparator",
            "observable": "runtime, stability, and stress output",
            "data_role": "internal benchmark only",
            "evidence_artifacts": [ref("docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts/fluid_benchmark_validation.json", {"status": "FAIL"})],
            "verification_status": "FAIL_INTERNAL_BENCHMARK",
            "open_blockers": ["full UET constitutive transport is deferred and comparator speed threshold is not met"],
            "dependency_unlocked": "none",
            "claim_boundary": "not external CFD validation or Navier-Stokes proof",
        },
        {
            "major_result_id": "TOPIC_0_19_CANDIDATE_GR_PARENT",
            "topic": "0.19_Gravity_GR",
            "closure_level": "PARTIAL",
            "what_is_closed": ["exact implemented epsilon_nc=0 response-null", "local covariant balance", "flat local 1+1 causal kernel"],
            "equation_or_mapping": "candidate response parent -> bounded local GR dependency records",
            "units": "candidate/natural lanes; curved SI mapping open",
            "derivation_class": "candidate mathematical infrastructure",
            "observable": "response-null and local balance diagnostics",
            "data_role": "dependency artifact only; physical benchmarks not started",
            "evidence_artifacts": [ref("docs/topics/0.19_Gravity_GR/Result/artifacts/0_19_core_gr_program_dependency_gate.json", {"status": "BLOCKED"})],
            "verification_status": "BLOCKED_PHYSICAL_GR_VALIDATION",
            "open_blockers": ["curved 3+1", "classical GR tests", "Kubo/transport completion", "independent holdout comparison"],
            "dependency_unlocked": "none until Core curved 3+1 gate",
            "claim_boundary": "does not derive Einstein equations or validate GR",
        },
        {
            "major_result_id": "TOPIC_0_1_GALAXY_COMPATIBILITY_TRACK",
            "topic": "0.1_Galaxy_Rotation_Problem",
            "closure_level": "OPEN",
            "what_is_closed": [],
            "equation_or_mapping": "metric/density-to-rotation map not accepted",
            "units": "3D density and metric observable mapping open",
            "derivation_class": "comparison track",
            "observable": "rotation curve residuals after dependency closure",
            "data_role": "legacy/internal comparison only",
            "evidence_artifacts": [],
            "verification_status": "BLOCKED_DEPENDENCY_ORDER",
            "open_blockers": ["Gravity/GR and external 3D density observable map"],
            "dependency_unlocked": "none",
            "claim_boundary": "not a dark-matter or universal galaxy claim",
        },
    ]
    discovered_entries: list[dict[str, Any]] = []
    discovered_ids: set[str] = set()
    for artifact_root in (
        ROOT / "docs/core/artifacts",
        ROOT / "docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts",
        ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts",
    ):
        for artifact_path in sorted(artifact_root.rglob("*.json")):
            if artifact_path.resolve() == T13.resolve():
                continue
            try:
                candidate = load(artifact_path.relative_to(ROOT))
            except (OSError, json.JSONDecodeError, ValueError):
                continue
            major = candidate.get("major_result")
            if not isinstance(major, dict):
                continue
            result_id = major.get("major_result_id")
            if not isinstance(result_id, str) or not result_id or result_id in discovered_ids:
                continue
            if any(item.get("major_result_id") == result_id for item in entries):
                continue
            discovered_ids.add(result_id)
            artifact_evidence = {
                "path": rel(artifact_path),
                "sha256": sha256(artifact_path),
                "summary": {
                    "status": candidate.get("status"),
                    "major_result_id": result_id,
                    "closure_level": major.get("closure_level"),
                },
            }
            discovered_open_blockers = major.get("open_blockers", major.get("what_remains_open", []))
            if result_id == "T13_CAUSAL_FLUX_TELEGRAPH_BRANCH":
                discovered_open_blockers = [
                    item for item in discovered_open_blockers
                    if item not in {"full coupled Phi integration", "full-candidate leakage rerun"}
                ]
            discovered_entries.append({
                "major_result_id": result_id,
                "topic": major.get("topic", "0.13_Thermodynamic_Bridge"),
                "closure_level": major.get("closure_level", "OPEN"),
                "claim_promotion": bool(candidate.get("claim_promotion", False)),
                "what_is_closed": major.get("what_is_closed", []),
                "equation_or_mapping": major.get("equation_or_mapping", {}),
                "units": major.get("units", {}),
                "derivation_class": major.get("derivation_class", "artifact-reported"),
                "observable": major.get("observable", "artifact-reported"),
                "data_role": major.get("data_role", "artifact-reported"),
                "evidence_artifacts": [artifact_evidence],
                "verification_status": major.get("verification_status", candidate.get("status", "OPEN")),
                "open_blockers": discovered_open_blockers,
                "dependency_unlocked": major.get("dependency_unlocked", "none"),
                "claim_boundary": major.get("claim_boundary", "artifact-reported boundary"),
            })

    entries.extend(discovered_entries)

    # Preserve the detailed closure projection when this repo-wide generator
    # runs after the Topic 13 matrix generator. The matrix is a first-class
    # result, not a generic discovered artifact, so dropping its input-package
    # and subresult contract would create metadata drift on the next rebuild.
    matrix_entry = next(
        (item for item in entries if item.get("major_result_id") == "T13_TOPIC13_CLOSURE_MATRIX"),
        None,
    )
    if matrix_entry is not None:
        matrix_major = matrix.get("major_result", {})
        for field in (
            "closure_level",
            "what_is_closed",
            "equation_or_mapping",
            "units",
            "derivation_class",
            "observable",
            "data_role",
            "verification_status",
            "open_blockers",
            "dependency_unlocked",
            "claim_boundary",
        ):
            if field in matrix_major:
                matrix_entry[field] = matrix_major[field]
        matrix_entry["claim_promotion"] = False
        matrix_entry["evidence_artifacts"] = [
            ref(
                rel(MATRIX),
                {
                    "role": "compact Topic 13 closure projection",
                },
            ),
            ref(
                rel(T13),
                {
                    "role": "canonical readiness gate",
                },
            ),
        ]
        matrix_entry["closure_summary"] = matrix.get("closure_summary", {})
        full_contract = matrix.get("full_topic_closure_contract", {})
        matrix_entry["full_topic_closure_contract"] = {
            "required_major_result_count": full_contract.get("required_major_result_count"),
            "required_subresult_count": full_contract.get("required_subresult_count"),
            "current_major_result_counts": full_contract.get("current_major_result_counts", {}),
            "current_subresult_counts": full_contract.get("current_subresult_counts", {}),
            "full_topic_ready": full_contract.get("full_topic_ready", False),
        }
        matrix_entry["required_major_result_count"] = full_contract.get("required_major_result_count")
        matrix_entry["required_subresult_count"] = full_contract.get("required_subresult_count")
        matrix_entry["required_input_package_count"] = full_contract.get("required_input_package_count")
        matrix_entry["current_major_result_counts"] = matrix_entry["closure_summary"].get(
            "current_major_result_counts", {}
        )
        matrix_entry["current_subresult_counts"] = matrix_entry["closure_summary"].get(
            "current_subresult_counts", {}
        )
        if "closure_input_packages" in full_contract:
            matrix_entry["closure_input_packages"] = full_contract["closure_input_packages"]
        if isinstance(matrix.get("input_package_audit"), dict):
            matrix_entry["input_package_audit"] = matrix["input_package_audit"]
    topic13_core_ready = any(
        entry.get("major_result_id") == "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY"
        and entry.get("closure_level") == "CLOSED_FOR_CORE"
        for entry in entries
    )
    artifact = {
        "schema_version": "uet-major-result-closure-register-v1",
        "artifact": "uet_major_result_closure_register",
        "generated_at": date.today().isoformat(),
        "contract": {"path": rel(CONTRACT), "sha256": sha256(CONTRACT)},
        "claim_promotion": False,
        "closure_levels_are_progress_labels_not_readiness_labels": True,
        "entries": entries,
        "next_major_result": (
            "CORE_CURVED_3P1_OBSERVABLE_PARENT_READY"
            if topic13_core_ready
            else "T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY"
        ),
        "claim_boundary": "This register reports closed or partial research results; it never promotes the global UET claim.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    dependency_path = ROOT / "docs/core/artifacts/uet_major_result_dependency_unlock_gate.json"
    if dependency_path.is_file():
        dependency = load(dependency_path)
        dependency["generated_at"] = date.today().isoformat()
        dependency.setdefault("register", {})["path"] = rel(OUT)
        dependency["register"]["sha256"] = sha256(OUT)
        dependency_path.write_text(
            json.dumps(dependency, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({"artifact": rel(OUT), "entries": len(entries), "next_major_result": artifact["next_major_result"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
