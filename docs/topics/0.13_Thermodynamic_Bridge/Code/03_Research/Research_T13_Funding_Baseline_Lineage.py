"""Reconcile the funding-plan snapshot with this checkout without promoting G0."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
PLAN_PATH = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/funding_portfolio_14d_plan.json"
OUTPUT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_funding_baseline_lineage_audit.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inspect(record: dict) -> dict:
    path = ROOT / record["path"]
    actual = _sha256(path) if path.is_file() else None
    return {
        "path": record["path"],
        "expected_sha256": record["sha256"],
        "current_sha256": actual,
        "state": "MISSING" if actual is None else "MATCH" if actual == record["sha256"] else "DRIFT",
    }


def audit() -> dict:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    historical = [_inspect(item) for item in plan["baseline"]["evidence"]]
    pre_sprint = [_inspect(item) for item in plan["pre_sprint_evidence"]["results"]]
    route = _inspect(plan["source_route_screen"])
    protocol = plan["baseline"]["existing_protocol"]
    protocol_path = ROOT / protocol["path"]
    protocol_present = protocol_path.is_file()
    counts = {state: sum(row["state"] == state for row in historical) for state in ("MATCH", "DRIFT", "MISSING")}
    pre_sprint_reproduced = bool(pre_sprint) and all(row["state"] == "MATCH" for row in pre_sprint)
    source_route_current = route["state"] == "MATCH"
    clean_baseline_revalidated = bool(plan["baseline"]["clean_reproduction_completed"])
    # This screen cannot promote G0; a separate clean Core verifier must do that.
    g0_ready = False
    blockers = []
    if counts["DRIFT"] or counts["MISSING"]:
        blockers.append("historical_dirty_branch_evidence_requires_clean_equivalent_selection")
    if not clean_baseline_revalidated:
        blockers.append("full_clean_core_baseline_not_revalidated")
    if not protocol_present:
        blockers.append("j02_protocol_not_present_in_clean_checkout")
    return {
        "schema_version": "t13-funding-baseline-lineage-v1",
        "major_result_id": "T13_FUNDING_CLEAN_BASELINE_LINEAGE_SCREEN",
        "topic": "0.13",
        "closure_level": "PARTIAL",
        "what_is_closed": "Historical versus current-checkout identity is classified for each planned baseline input, while saved pre-sprint evidence is checked separately",
        "equation_or_mapping": "source identity is path plus SHA-256; a passing local audit is not a physical mapping",
        "units": "not applicable to source identity",
        "derivation_class": "deterministic file-identity reconciliation",
        "observable": "reproducibility of the proposed funding baseline in this checkout",
        "data_role": "PROVENANCE_AUDIT_NOT_PHYSICAL_VALIDATION",
        "historical_snapshot": {"branch": plan["baseline"]["branch"], "head": plan["baseline"]["head"],
                                "dirty_worktree": plan["baseline"]["dirty_worktree"],
                                "evidence": historical, "counts": counts,
                                "hashes_are_historical_not_required_to_equal_selected_clean_equivalents": True},
        "pre_sprint_saved_evidence": {"records": pre_sprint, "all_match": pre_sprint_reproduced},
        "source_route_screen": {"record": route, "numeric_rows_admitted": plan["source_route_screen"]["numeric_response_rows_admitted"],
                                 "current": source_route_current},
        "referenced_j02_protocol": {"commit": protocol["commit"], "path": protocol["path"],
                                    "present_in_this_checkout": protocol_present},
        "clean_core_baseline_revalidated": clean_baseline_revalidated,
        "g0_evaluation_authority": "separate hash-backed clean Core baseline verifier and J02 dependency review; not this identity screen or a planning Boolean",
        "g0_baseline_ready": g0_ready,
        "g0_status": "BLOCKED_LINEAGE_RECONCILIATION",
        "verification_status": "PASS_IDENTITY_SCREEN_WITH_OPEN_G0" if pre_sprint_reproduced and source_route_current else "REVIEW_REQUIRED",
        "evidence_artifacts": [
            {"path": PLAN_PATH.relative_to(ROOT).as_posix(), "sha256": _sha256(PLAN_PATH)},
            {"path": Path(__file__).resolve().relative_to(ROOT).as_posix(), "sha256": _sha256(Path(__file__).resolve())},
            {"path": Path(__file__).with_name("test_t13_funding_baseline_lineage.py").relative_to(ROOT).as_posix(),
             "sha256": _sha256(Path(__file__).with_name("test_t13_funding_baseline_lineage.py"))},
        ],
        "open_blockers": blockers,
        "controlling_blocker": "full_clean_core_baseline_not_revalidated",
        "dependency_unlocked": [],
        "full_core_unlock": False,
        "claim_boundary": "Five pre-sprint saved artifacts matching this checkout do not establish clean reproduction of the older Core baseline. G0 remains open; no J02 integration, Xie 2026 access, physical map, external validation or Full Topic 13 closure is asserted.",
    }


if __name__ == "__main__":
    result = audit()
    OUTPUT.write_bytes((json.dumps(result, indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print(OUTPUT)
