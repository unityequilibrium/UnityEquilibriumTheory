"""Reconcile existing collision evidence without rerunning or promoting it."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main():
    rows = []
    for name in ("t13_invariant_galerkin_collision_operator_audit.json",
                 "t13_coupled_gain_loss_operator_audit.json",
                 "t13_integrated_elastic_events_audit.json"):
        path = ROOT/"docs/core/artifacts"/name
        a = json.loads(path.read_text(encoding="utf-8"))
        references = dict(a.get("source_hashes", {}))
        references.update({e["path"]: e["sha256"] for e in a.get("evidence_artifacts", [])})
        checks = {p: (ROOT/p).exists() and sha256((ROOT/p).read_bytes()).hexdigest() == h
                  for p,h in references.items()}
        rows.append(dict(path=str(path.relative_to(ROOT)).replace("\\", "/"),
                         sha256=sha256(path.read_bytes()).hexdigest(),
                         recorded_status=a.get("verification_status"),
                         reference_hash_matches=checks,
                         all_declared_references_match=bool(checks) and all(checks.values()),
                         recorded_blocker=a.get("controlling_blocker",a.get("open_blockers")),
                         diagnostic_refinement_pass=a.get("diagnostic_refinement_pass")))
    result = dict(major_result_id="T13_COLLISION_EVIDENCE_RECONCILIATION",topic="0.13",
        closure_level="PARTIAL", rows=rows,
        what_is_closed="Current-source reuse of existing gain-loss evidence assessed; creation from scratch is not the next task",
        verification_status="REFERENCE_HASH_RECONCILIATION_NOT_NEW_PHYSICS",
        controlling_blocker="basis_completeness_and_physical_collision_current_matching",
        next_action="Review existing vector/current/material handoffs before extending basis; do not repeat solved scalar or gain-loss construction",
        full_core_unlock=False, dependency_unlocked=[],
        claim_boundary="Matching hashes do not prove continuum completeness. Historical mismatches are disclosed, not repaired by rewriting archived results.")
    (ROOT/"docs/core/07_artifacts/topic13/t13_collision_evidence_reconciliation.json").write_text(
        json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    for row in rows:
        print(row["path"],row["all_declared_references_match"])
        for p,ok in row["reference_hash_matches"].items():
            if not ok: print("HISTORICAL_SOURCE_DRIFT",p)


if __name__ == "__main__":
    main()
