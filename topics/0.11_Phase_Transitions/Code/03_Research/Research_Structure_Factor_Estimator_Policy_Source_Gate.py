"""
Wave 34 estimator-policy source-support gate.

Wave 33 tested S(0) lanes and found that the source-closer ensemble
susceptibility lane is blocked by conserved mean while the spatial-variance
proxy remains diagnostic-only. This verifier checks whether the local source
package is sufficient to choose a next estimator policy:

1. source-back a conserved-order/fixed-composition susceptibility policy;
2. switch to a source-backed finite-k/canonical estimator policy;
3. promote the spatial-variance proxy.

The expected result is conservative: requirements can be explicit while policy
source support remains missing.
"""

from __future__ import annotations

import json
import platform
import re
import sys
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
ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_estimator_policy_source_gate.json"
SOURCE_MANIFEST_PATH = (
    TOPIC_DIR / "Data" / "03_Research" / "structure_factor_estimator_source_manifest.json"
)
FORMULA_BOUNDARY_PATH = (
    TOPIC_DIR / "Data" / "03_Research" / "structure_factor_estimator_formula_boundary.json"
)
POLICY_REQUIREMENTS_PATH = (
    TOPIC_DIR / "Data" / "03_Research" / "structure_factor_estimator_policy_requirements.json"
)
WAVE33_ARTIFACT_PATH = ARTIFACT_DIR / "0_11_structure_factor_ensemble_susceptibility_lane_gate.json"

POLICY_KEYWORDS = {
    "conserved_order_fixed_composition_susceptibility_policy": [
        r"fixed[-_\s]?composition",
        r"conserved[-_\s]?order",
        r"mass[-_\s]?conservation",
        r"canonical",
        r"ensemble.{0,80}susceptibility",
        r"connected.{0,80}S\\(0\\)",
    ],
    "finite_k_or_canonical_estimator_policy": [
        r"finite[-_\s]?k",
        r"finite[-_\s]?momentum",
        r"canonical",
        r"zero[-_\s]?mode.{0,80}avoid",
        r"fixed[-_\s]?composition",
        r"k_min.{0,80}without.{0,80}S\\(0\\)",
    ],
    "spatial_variance_proxy_policy": [
        r"spatial[-_\s]?variance",
        r"Var_space",
        r"N\\s*\\*\\s*Var",
        r"source[-_\s]?equivalent",
    ],
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


def flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(flatten_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flatten_text(item) for item in value)
    return str(value)


def keyword_hits(text: str, patterns: list[str]) -> list[str]:
    hits = []
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            hits.append(pattern)
    return hits


def policy_requirement_ready(policy: dict[str, Any]) -> bool:
    required_fields = [
        "policy_id",
        "policy_question",
        "required_source_support",
        "current_support_status",
        "accepted_now",
        "why_needed",
    ]
    return all(policy.get(field) not in (None, "") for field in required_fields)


def run_estimator_policy_source_gate() -> dict[str, Any]:
    wave33 = load_json(WAVE33_ARTIFACT_PATH) if WAVE33_ARTIFACT_PATH.exists() else {}
    source_manifest = load_json(SOURCE_MANIFEST_PATH) if SOURCE_MANIFEST_PATH.exists() else {}
    formula_boundary = load_json(FORMULA_BOUNDARY_PATH) if FORMULA_BOUNDARY_PATH.exists() else {}
    policy_requirements = (
        load_json(POLICY_REQUIREMENTS_PATH) if POLICY_REQUIREMENTS_PATH.exists() else {}
    )
    policies = policy_requirements.get("policy_candidates", [])
    policy_ids = {str(policy.get("policy_id")) for policy in policies}
    ready_policies = [policy for policy in policies if policy_requirement_ready(policy)]
    source_text = flatten_text(source_manifest)
    formula_text = flatten_text(formula_boundary)
    packaged_text = f"{source_text} {formula_text}"

    policy_scan = {}
    for policy_id in sorted(POLICY_KEYWORDS):
        policy = next((row for row in policies if row.get("policy_id") == policy_id), {})
        hits = keyword_hits(packaged_text, POLICY_KEYWORDS[policy_id])
        source_support_status = policy.get("current_support_status")
        policy_scan[policy_id] = {
            "manifest_row_present": bool(policy),
            "manifest_support_status": source_support_status,
            "keyword_hits": hits,
            "keyword_hit_count": len(hits),
            "accepted_now": bool(policy.get("accepted_now")) if policy else False,
            "claim_boundary": (
                "Keyword hits are triage only; a policy is accepted only if a source-backed policy row says accepted_now true."
            ),
        }

    expected_policy_ids = set(POLICY_KEYWORDS)
    missing_policy_ids = sorted(expected_policy_ids - policy_ids)

    wave33_chain_gate = {
        "status": (
            "PASS"
            if wave33.get("blocker_label")
            == "ensemble_susceptibility_lane_blocked_by_conserved_mean_constraint"
            else "BLOCKED"
        ),
        "required_condition": "Wave 34 must start from the Wave 33 conserved-mean susceptibility policy blocker.",
        "wave33_status": wave33.get("status"),
        "wave33_blocker_label": wave33.get("blocker_label"),
    }
    policy_requirement_manifest_gate = {
        "status": (
            "PASS"
            if POLICY_REQUIREMENTS_PATH.exists()
            and policy_requirements.get("schema_version")
            and not missing_policy_ids
            and len(ready_policies) == len(policies)
            else "BLOCKED"
        ),
        "required_condition": "A policy requirements manifest must define conserved-order susceptibility, finite-k/canonical, and spatial-variance proxy policy rows.",
        "policy_manifest_path": relpath(POLICY_REQUIREMENTS_PATH),
        "policy_manifest_sha256": hash_file(POLICY_REQUIREMENTS_PATH)
        if POLICY_REQUIREMENTS_PATH.exists()
        else None,
        "observed_policy_ids": sorted(policy_ids),
        "missing_policy_ids": missing_policy_ids,
        "ready_policy_count": len(ready_policies),
        "policy_count": len(policies),
    }
    conserved_susceptibility_source_gate = {
        "status": (
            "PASS"
            if policy_scan["conserved_order_fixed_composition_susceptibility_policy"][
                "accepted_now"
            ]
            else "BLOCKED"
        ),
        "required_condition": "A source-backed policy must accept S(0) for conserved-order/fixed-composition fields before the lowest-mode estimator can be used.",
        **policy_scan["conserved_order_fixed_composition_susceptibility_policy"],
    }
    finite_k_policy_source_gate = {
        "status": (
            "PASS"
            if policy_scan["finite_k_or_canonical_estimator_policy"]["accepted_now"]
            else "BLOCKED"
        ),
        "required_condition": "A source-backed finite-k or canonical estimator policy must exist before replacing the blocked S(0) lane.",
        **policy_scan["finite_k_or_canonical_estimator_policy"],
    }
    spatial_variance_proxy_policy_gate = {
        "status": "PASS"
        if not policy_scan["spatial_variance_proxy_policy"]["accepted_now"]
        else "BLOCKED",
        "required_condition": "The spatial-variance proxy must remain diagnostic-only unless separately source-backed.",
        **policy_scan["spatial_variance_proxy_policy"],
    }
    estimator_policy_selection_gate = {
        "status": (
            "PASS"
            if conserved_susceptibility_source_gate["status"] == "PASS"
            or finite_k_policy_source_gate["status"] == "PASS"
            else "BLOCKED"
        ),
        "required_condition": "At least one source-backed estimator policy path must be accepted before exponent gates rerun.",
        "accepted_policy_paths": [
            name
            for name, gate in {
                "conserved_susceptibility_source_gate": conserved_susceptibility_source_gate,
                "finite_k_policy_source_gate": finite_k_policy_source_gate,
            }.items()
            if gate["status"] == "PASS"
        ],
    }
    next_path_gate = {
        "status": "BLOCKED",
        "required_condition": "Do not rerun exponent gates until policy source support is packaged and accepted, or the window/dynamics path is chosen explicitly.",
        "next_controller": "package_conserved_order_or_finite_k_estimator_policy_sources",
        "next_options": [
            "package source support for conserved-order/fixed-composition susceptibility",
            "package source support for a finite-k/canonical estimator policy",
            "choose window/dynamics repair without pretending an estimator is accepted",
        ],
    }
    claim_boundary_gate = {
        "status": "WARN",
        "required_condition": "Estimator-policy source triage cannot promote estimator, exponent, material, RG, or universality claims.",
        "claim_boundary": "Wave 34 defines required estimator policy source support but accepts no policy path.",
    }

    if wave33_chain_gate["status"] != "PASS":
        blocker_label = "estimator_policy_source_gate_chain_missing"
    elif estimator_policy_selection_gate["status"] == "BLOCKED":
        blocker_label = "estimator_policy_source_support_missing_for_conserved_susceptibility_or_finite_k_path"
    else:
        blocker_label = "estimator_policy_source_support_present_needs_acceptance_rerun"

    artifact = {
        "schema_version": "1.0",
        "topic": "0.11_Phase_Transitions",
        "wave": "Wave 34 estimator policy source-support gate",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python docs/topics/0.11_Phase_Transitions/Code/03_Research/Research_Structure_Factor_Estimator_Policy_Source_Gate.py",
        "status": "WARN",
        "blocker_label": blocker_label,
        "claim_class": "estimator_policy_source_triage_only",
        "inputs": [
            artifact_record(WAVE33_ARTIFACT_PATH, "Wave 33 conserved susceptibility policy controller"),
            source_record(SOURCE_MANIFEST_PATH, "estimator source manifest"),
            source_record(FORMULA_BOUNDARY_PATH, "formula-boundary manifest"),
            source_record(POLICY_REQUIREMENTS_PATH, "Wave 34 estimator policy requirements manifest"),
        ],
        "metrics": {
            "policy_count": len(policies),
            "ready_policy_count": len(ready_policies),
            "missing_policy_ids": missing_policy_ids,
            "policy_scan": policy_scan,
        },
        "gates": {
            "wave33_chain_gate": wave33_chain_gate,
            "policy_requirement_manifest_gate": policy_requirement_manifest_gate,
            "conserved_susceptibility_source_gate": conserved_susceptibility_source_gate,
            "finite_k_policy_source_gate": finite_k_policy_source_gate,
            "spatial_variance_proxy_policy_gate": spatial_variance_proxy_policy_gate,
            "estimator_policy_selection_gate": estimator_policy_selection_gate,
            "next_path_gate": next_path_gate,
            "claim_boundary_gate": claim_boundary_gate,
        },
        "limitations": [
            "Keyword hits are triage only and do not accept a policy.",
            "The current source package does not source-back conserved-order/fixed-composition S(0).",
            "The current source package does not source-back a finite-k/canonical estimator alternative.",
            "The spatial-variance proxy remains diagnostic-only.",
            "No exponent, universality, material, or RG claim may be upgraded from this source triage.",
        ],
        "claim_boundary": "Do not promote conserved_order_spectral_v1 scaling claims. Wave 34 defines policy requirements and blocks estimator replacement until conserved-order or finite-k policy sources are packaged.",
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
        },
    }

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    result = run_estimator_policy_source_gate()
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
