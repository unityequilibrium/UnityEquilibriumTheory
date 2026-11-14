"""
Wave 43 TeX formula-fragment extraction gate.

Wave 38 localized arXiv source archives and identified main TeX members. This
verifier extracts exact TeX formula fragments relevant to fixed-composition,
canonical finite-size, and Cahn-Hilliard structure-factor policy review. It
does not accept an estimator policy until the fragments are mapped into UET
normalization and an admissibility rule.
"""

from __future__ import annotations

import json
import platform
import re
import sys
import tarfile
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any


def _bootstrap() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs").exists() and (parent / "docs" / "core").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError("UET docs root not found")


ROOT = _bootstrap()
TOPIC_DIR = ROOT / "docs" / "topics" / "0.11_Phase_Transitions"
ARTIFACT_DIR = TOPIC_DIR / "Result" / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_tex_formula_fragment_gate.json"
WAVE38_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_source_archive_localization_gate.json"
LOCALIZATION_MANIFEST_PATH = (
    TOPIC_DIR
    / "Data"
    / "03_Research"
    / "structure_factor_source_archive_localization_manifest.json"
)
SOURCE_ARCHIVE_POLICY_PATH = (
    TOPIC_DIR
    / "Data"
    / "03_Research"
    / "structure_factor_source_archive_policy.json"
)
FORMULA_FRAGMENT_MANIFEST_PATH = (
    TOPIC_DIR
    / "Data"
    / "03_Research"
    / "structure_factor_tex_formula_fragments.json"
)

FRAGMENT_PLAN: dict[str, dict[str, Any]] = {
    "blote_heringa_tsypin_1999_fixed_magnetization_ising": {
        "policy_role": "fixed_magnetization_effective_field_boundary",
        "wanted_labels": ["lnP_RS", "P_RS", "dV_RS", "hVeff", "hVeff_canon"],
        "accepted_for_estimator_policy_now": False,
        "policy_implication": (
            "Supports a fixed-magnetization effective-field/free-energy boundary; "
            "does not provide a source-equivalent conserved-order S(0) susceptibility "
            "for the current UET snapshots."
        ),
    },
    "deng_blote_2005_canonical_fss": {
        "policy_role": "canonical_finite_size_scaling_boundary",
        "wanted_labels": ["ACs", "rhos", "AGs2"],
        "inline_needles": ["\\chi^{(c)} (L)=\\chi^{(g)}(L)"],
        "accepted_for_estimator_policy_now": False,
        "policy_implication": (
            "Supports canonical finite-size correction boundaries and susceptibility "
            "correction language; still lacks a direct accepted mapping to the current "
            "structure-factor length proxy."
        ),
    },
    "longo_2021_cahn_hilliard_structure_factor": {
        "policy_role": "cahn_hilliard_structure_factor_boundary",
        "wanted_labels": [
            "Eqn_Gen_OrdParam_Evo",
            "Eqn_Gen_Chem_Pot",
            "Eqn-omega(q)",
            "Eqn_Char_Wavenums",
            "Eqn_Sqt_long",
            "Eq-Schi",
            "Eqn-SCH",
            "Eq_Empir_Schi",
        ],
        "inline_needles": ["S(q,t) = \\int", "\\pdv{S(q,t)}{t}"],
        "accepted_for_estimator_policy_now": False,
        "policy_implication": (
            "Supports a Cahn-Hilliard/interconversion structure-factor source lane; "
            "UET normalization, finite-size admissibility, and estimator replacement "
            "are still open."
        ),
    },
}


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_record(path: Path, role: str) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": relpath(path),
        "role": role,
        "exists": exists,
        "sha256": hash_file(path) if exists else None,
    }


def artifact_record(path: Path, role: str) -> dict[str, Any]:
    exists = path.exists()
    data = load_json(path) if exists else {}
    return {
        "path": relpath(path),
        "role": role,
        "exists": exists,
        "sha256": hash_file(path) if exists else None,
        "status": data.get("status"),
        "blocker_label": data.get("blocker_label"),
        "claim_class": data.get("claim_class"),
    }


def equation_blocks(tex_text: str) -> list[dict[str, Any]]:
    pattern = re.compile(r"\\begin\{equation\}(.*?)\\end\{equation\}", re.DOTALL)
    line_starts = [0]
    for match in re.finditer("\n", tex_text):
        line_starts.append(match.end())

    def line_number(offset: int) -> int:
        # Small files, simple scan is clear enough and avoids an extra dependency.
        return sum(1 for start in line_starts if start <= offset)

    blocks: list[dict[str, Any]] = []
    for match in pattern.finditer(tex_text):
        body = match.group(1).strip()
        labels = re.findall(r"\\label\{([^}]+)\}", body)
        clean_body = re.sub(r"\s+", " ", body).strip()
        blocks.append(
            {
                "labels": labels,
                "line_start": line_number(match.start()),
                "line_end": line_number(match.end()),
                "tex": clean_body,
            }
        )
    return blocks


def inline_fragments(tex_text: str, needles: list[str]) -> list[dict[str, Any]]:
    lines = tex_text.splitlines()
    fragments: list[dict[str, Any]] = []
    for needle in needles:
        for idx, line in enumerate(lines, 1):
            if needle in line:
                fragments.append(
                    {
                        "labels": [],
                        "line_start": idx,
                        "line_end": idx,
                        "tex": line.strip(),
                        "needle": needle,
                    }
                )
                break
    return fragments


def extract_tex_member(archive_path: Path, member_name: str) -> str:
    with tarfile.open(archive_path) as archive:
        member = archive.extractfile(member_name)
        if member is None:
            raise RuntimeError(f"Missing TeX member {member_name} in {archive_path}")
        return member.read().decode("utf-8", errors="replace")


def policy_archive_map() -> dict[str, str]:
    if not SOURCE_ARCHIVE_POLICY_PATH.exists():
        return {}
    policy = load_json(SOURCE_ARCHIVE_POLICY_PATH)
    return {
        str(row.get("source_id")): str(row.get("repo_archive_candidate_path"))
        for row in policy.get("source_archives", [])
        if row.get("source_id") and row.get("repo_archive_candidate_path")
    }


def resolve_archive_path(record: dict[str, Any], repo_archive_by_source: dict[str, str]) -> tuple[Path, str]:
    source_id = str(record["source_id"])
    temp_path = Path(str(record["local_cache_path"]))
    if temp_path.exists():
        return temp_path, "temporary_cache"
    repo_rel = repo_archive_by_source.get(source_id)
    if repo_rel:
        repo_path = ROOT / repo_rel
        if repo_path.exists():
            return repo_path, "repo_archive"
    return temp_path, "missing"


def fragment_observation(record: dict[str, Any], repo_archive_by_source: dict[str, str]) -> dict[str, Any]:
    source_id = str(record["source_id"])
    plan = FRAGMENT_PLAN[source_id]
    archive_path, archive_source = resolve_archive_path(record, repo_archive_by_source)
    tex_member = str(record["expected_tex_members"][0]["name"])
    tex_text = extract_tex_member(archive_path, tex_member)
    blocks = equation_blocks(tex_text)
    by_label = {
        label: block
        for block in blocks
        for label in block.get("labels", [])
    }
    wanted_labels = plan.get("wanted_labels", [])
    label_fragments = [
        {
            "fragment_id": f"{source_id}:{label}",
            "source_id": source_id,
            "tex_member": tex_member,
            "formula_label": label,
            "line_start": by_label[label]["line_start"],
            "line_end": by_label[label]["line_end"],
            "tex": by_label[label]["tex"],
            "fragment_status": "extracted",
        }
        for label in wanted_labels
        if label in by_label
    ]
    inline = [
        {
            "fragment_id": f"{source_id}:inline:{idx}",
            "source_id": source_id,
            "tex_member": tex_member,
            "formula_label": row.get("needle"),
            "line_start": row["line_start"],
            "line_end": row["line_end"],
            "tex": row["tex"],
            "fragment_status": "extracted_inline",
        }
        for idx, row in enumerate(inline_fragments(tex_text, plan.get("inline_needles", [])), 1)
    ]
    missing_labels = sorted(set(wanted_labels) - set(by_label))
    return {
        "source_id": source_id,
        "source_url": record.get("source_url"),
        "archive_path": str(archive_path).replace("\\", "/"),
        "archive_sha256": hash_file(archive_path),
        "tex_member": tex_member,
        "tex_member_sha256": sha256(tex_text.encode("utf-8", errors="replace")).hexdigest(),
        "policy_role": plan["policy_role"],
        "policy_implication": plan["policy_implication"],
        "accepted_for_estimator_policy_now": plan["accepted_for_estimator_policy_now"],
        "missing_expected_labels": missing_labels,
        "fragments": label_fragments + inline,
        "extracted_fragment_count": len(label_fragments) + len(inline),
        "claim_boundary": "Formula fragments are extracted for review only; estimator policy is not accepted.",
    }


def write_manifest(observations: list[dict[str, Any]]) -> dict[str, Any]:
    manifest = {
        "schema_version": "1.0",
        "manifest_id": "0_11_structure_factor_tex_formula_fragments",
        "topic": "0.11_Phase_Transitions",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim_boundary": (
            "This manifest records exact TeX formula fragments from localized source archives. "
            "It does not accept a conserved-order estimator policy, UET normalization mapping, "
            "finite-size admissibility rule, exponent result, RG closure, or universality claim."
        ),
        "source_formula_fragments": observations,
        "formula_fragment_decision": {
            "decision": "tex_formula_fragments_extracted_estimator_policy_open",
            "next_controller": "uet_normalization_mapping_and_estimator_policy_acceptance",
            "reason": (
                "Relevant source formulas were extracted, but none is accepted for the current "
                "UET conserved-order scaling lane until normalization and admissibility are mapped."
            ),
        },
    }
    FORMULA_FRAGMENT_MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return manifest


def run_tex_formula_fragment_gate() -> dict[str, Any]:
    wave38 = load_json(WAVE38_ARTIFACT_PATH) if WAVE38_ARTIFACT_PATH.exists() else {}
    localization = load_json(LOCALIZATION_MANIFEST_PATH)
    repo_archive_by_source = policy_archive_map()
    source_archives = [
        row
        for row in localization.get("source_archives", [])
        if row.get("source_id") in FRAGMENT_PLAN
    ]
    missing_archives = []
    for row in source_archives:
        _, archive_source = resolve_archive_path(row, repo_archive_by_source)
        if archive_source == "missing":
            missing_archives.append(
                {
                    "source_id": row.get("source_id"),
                    "local_cache_path": str(row.get("local_cache_path")),
                    "repo_archive_candidate_path": repo_archive_by_source.get(str(row.get("source_id"))),
                }
            )
    prior_manifest = (
        load_json(FORMULA_FRAGMENT_MANIFEST_PATH)
        if FORMULA_FRAGMENT_MANIFEST_PATH.exists()
        else {}
    )
    if missing_archives:
        observations = prior_manifest.get("source_formula_fragments", [])
        manifest = prior_manifest
    else:
        observations = [fragment_observation(row, repo_archive_by_source) for row in source_archives]
        manifest = write_manifest(observations)

    expected_sources = set(FRAGMENT_PLAN)
    observed_sources = {row["source_id"] for row in observations}
    extracted_count = sum(row["extracted_fragment_count"] for row in observations)
    accepted_count = sum(1 for row in observations if row["accepted_for_estimator_policy_now"])
    missing_labels = {
        row["source_id"]: row["missing_expected_labels"]
        for row in observations
        if row["missing_expected_labels"]
    }

    wave38_chain_gate = {
        "status": (
            "PASS"
            if wave38.get("blocker_label")
            == "localized_source_archives_present_tex_formula_extraction_open"
            else "BLOCKED"
        ),
        "required_condition": "Wave 43 must start from the Wave 38 TeX formula extraction blocker.",
        "wave38_status": wave38.get("status"),
        "wave38_blocker_label": wave38.get("blocker_label"),
    }
    source_archive_availability_gate = {
        "status": "PASS" if not missing_archives else "BLOCKED",
        "required_condition": "All temporary source archives referenced by the localization manifest must be available before formula fragments can be refreshed.",
        "missing_archives": missing_archives,
        "cache_policy": localization.get("local_cache_policy", {}),
    }
    formula_fragment_manifest_gate = {
        "status": (
            "PASS"
            if FORMULA_FRAGMENT_MANIFEST_PATH.exists()
            and expected_sources.issubset(observed_sources)
            and extracted_count > 0
            else "BLOCKED"
        ),
        "required_condition": "A formula-fragment manifest must cover the expected source IDs and extract at least one formula fragment.",
        "manifest_path": relpath(FORMULA_FRAGMENT_MANIFEST_PATH),
        "manifest_sha256": hash_file(FORMULA_FRAGMENT_MANIFEST_PATH),
        "observed_source_ids": sorted(observed_sources),
        "missing_expected_source_ids": sorted(expected_sources - observed_sources),
        "extracted_fragment_count": extracted_count,
        "missing_expected_labels": missing_labels,
    }
    source_formula_fragment_gate = {
        "status": (
            "PASS"
            if extracted_count >= 3 and not missing_archives
            else "WARN"
            if extracted_count >= 3
            else "BLOCKED"
        ),
        "required_condition": "Formula fragments must be extracted from localized TeX sources before policy review can proceed.",
        "extracted_fragment_count": extracted_count,
        "fresh_extraction": not missing_archives,
    }
    accepted_estimator_policy_gate = {
        "status": "PASS" if accepted_count else "BLOCKED",
        "required_condition": "A source-backed estimator policy must be accepted before exponent or universality gates rerun.",
        "accepted_source_count": accepted_count,
    }
    uet_normalization_mapping_gate = {
        "status": "BLOCKED",
        "required_condition": "Extracted formulas must be mapped to UET normalized lattice units and finite-size admissibility before claim use.",
        "missing_mapping": [
            "conserved-order S(0) or finite-k policy choice",
            "normalization from source variables to UET lattice fields",
            "finite-size admissibility rule for L-series scaling",
        ],
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until formula fragments are mapped and an estimator policy is accepted.",
        "next_controller": "map_extracted_formulas_to_uet_estimator_policy",
        "next_options": [
            "accept a finite-k Cahn-Hilliard structure-factor policy with UET normalization",
            "accept a conserved-order susceptibility policy if S(0) can be source-mapped",
            "reject estimator replacement and return to window/dynamics repair",
        ],
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Formula extraction alone cannot promote estimator, exponent, material, RG, or universality claims.",
        "claim_boundary": "Wave 43 extracts formula fragments only; no estimator replacement is accepted.",
    }

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 43 TeX formula-fragment extraction gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Tex_Formula_Fragment_Gate.py",
        "status": "WARN",
        "blocker_label": (
            "tex_formula_fragments_extracted_source_cache_missing"
            if missing_archives
            else "tex_formula_fragments_extracted_estimator_policy_open"
        ),
        "claim_class": "formula_fragment_extraction_only",
        "inputs": [
            artifact_record(WAVE38_ARTIFACT_PATH, "Wave 38 source archive localization controller"),
            source_record(LOCALIZATION_MANIFEST_PATH, "Wave 38 source archive localization manifest"),
            source_record(SOURCE_ARCHIVE_POLICY_PATH, "Wave 44 source archive policy manifest"),
            source_record(FORMULA_FRAGMENT_MANIFEST_PATH, "Wave 43 formula-fragment manifest"),
        ],
        "metrics": {
            "source_count": len(observations),
            "extracted_fragment_count": extracted_count,
            "accepted_source_count": accepted_count,
            "observations": observations,
        },
        "gates": {
            "wave38_chain_gate": wave38_chain_gate,
            "source_archive_availability_gate": source_archive_availability_gate,
            "formula_fragment_manifest_gate": formula_fragment_manifest_gate,
            "source_formula_fragment_gate": source_formula_fragment_gate,
            "accepted_estimator_policy_gate": accepted_estimator_policy_gate,
            "uet_normalization_mapping_gate": uet_normalization_mapping_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "Extracted TeX fragments are source-review evidence only.",
            "Formula-fragment refresh depends on temporary source archives unless a repo archival policy is added.",
            "No source fragment is accepted as the current UET estimator policy in this wave.",
            "UET normalization and finite-size admissibility mapping remain open.",
            "No exponent, universality, RG, material, or Tier A claim may be upgraded.",
        ],
        "claim_boundary": "Wave 43 narrows the blocker from missing TeX extraction to UET normalization and estimator-policy acceptance.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_tex_formula_fragment_gate()
    print(
        json.dumps(
            {
                "status": result["status"],
                "blocker_label": result["blocker_label"],
                "gates": {name: gate["status"] for name, gate in result["gates"].items()},
                "artifact": relpath(ARTIFACT_PATH),
            },
            indent=2,
            sort_keys=True,
        )
    )
