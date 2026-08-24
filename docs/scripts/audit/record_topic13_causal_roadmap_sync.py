"""Synchronize Topic 13 causal-branch wording with the canonical artifacts."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROADMAP = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/TOPIC13_FULL_CLOSURE_ROADMAP.md"
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-24.md"
CAUSAL = ROOT / "docs/core/artifacts/t13_causal_named_branch_core_compatibility.json"
MATRIX = ROOT / "docs/core/artifacts/t13_topic13_closure_matrix.json"

MARKER = "### 2026-08-24 - Causal branch roadmap synchronization"
OLD = """The causal structural question is already a scoped no-go for the declared
conserved-C local-gradient class. Its named coupled flux-Phi branch is still
lane-level; the full-topic causal exception requires that named branch to be
promoted to `CLOSED_FOR_CORE` without replacing the original baseline silently.
"""
NEW = """The causal structural question is already a scoped no-go for the declared
conserved-C local-gradient class. The named coupled flux-Phi branch has a
separate bounded Core handoff record,
`T13_CAUSAL_FLUX_PHI_COUPLED_CORE_COMPATIBILITY`, at `CLOSED_FOR_CORE`.
That is a causal exception only: it does not convert any of the 36 Full Topic
13 subresults to `CLOSED_FOR_CORE`, replace the original blocked baseline, or
unlock SI thermal mapping, physical transport, curved 3+1, or Gravity.
"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def append_once(path: Path, marker: str, text: str) -> bool:
    current = path.read_text(encoding="utf-8")
    if marker in current:
        return False
    path.write_text(current.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")
    return True


def main() -> int:
    causal = load(CAUSAL)
    matrix = load(MATRIX)
    causal_result = causal["major_result"]
    counts = matrix["closure_summary"]["current_subresult_counts"]

    if causal_result["major_result_id"] != "T13_CAUSAL_FLUX_PHI_COUPLED_CORE_COMPATIBILITY":
        raise SystemExit("unexpected causal major_result_id")
    if causal_result["closure_level"] != "CLOSED_FOR_CORE":
        raise SystemExit("causal branch is not CLOSED_FOR_CORE")
    if matrix["full_core_unlock"] is not False or counts.get("CLOSED_FOR_CORE", 0) != 0:
        raise SystemExit("full-topic matrix boundary changed unexpectedly")

    roadmap = ROADMAP.read_text(encoding="utf-8")
    if OLD in roadmap:
        roadmap = roadmap.replace(OLD, NEW, 1)
        ROADMAP.write_text(roadmap, encoding="utf-8")
        roadmap_changed = True
    elif NEW in roadmap:
        roadmap_changed = False
    else:
        raise SystemExit("expected stale causal roadmap paragraph was not found")

    stamp = datetime.now(timezone.utc).isoformat()
    causal_hash = sha256(CAUSAL)
    matrix_hash = sha256(MATRIX)
    log_entry = f"""{MARKER}

MAJOR_RESULT_CLOSURE:
- `T13_CAUSAL_FLUX_PHI_COUPLED_CORE_COMPATIBILITY` is `CLOSED_FOR_CORE` as a bounded causal exception.

WHAT_IS_ACTUALLY_CLOSED:
- The scoped conserved-C local-gradient no-go and the named coupled flux-Phi finite-cone branch handoff are recorded.
- The original conserved-C baseline remains preserved and blocked.

WHAT_REMAINS_OPEN:
- The 36-subresult Full Topic 13 matrix remains `CLOSED_FOR_LANE=21`, `CLOSED_AS_NO_GO=5`, `CLOSED_FOR_CORE=0`, `OPEN=10`.

DEPENDENCY_UNLOCKED:
- Causal exception input only. No SI thermal, physical transport, curved 3+1, Gravity, or Full Topic 13 unlock.

STATUS:
- `PASS_SCOPED_CAUSAL_CORE_EXCEPTION_ROADMAP_SYNC`

WHAT_CHANGED:
- Synchronized the roadmap wording with the canonical causal compatibility artifact without changing thresholds, branch equations, or closure gates.

EQUATION_OR_MAPPING:
- Named normalized conserved flux-Phi telegraph branch; no dimensional Phi-to-temperature mapping is implied.

VERIFICATION:
- Causal artifact status=`{causal["status"]}`; closure=`{causal_result["closure_level"]}`; matrix full_core_unlock=`{matrix["full_core_unlock"]}`; generated_at=`{stamp}`.

CONTROLLING_BLOCKER:
- Full Topic 13 remains controlled by the seven blocker groups in the canonical gate, including missing independent `alpha_Phi_K`, dimensional SI map, accepted Ding-compatible `C_src`, and physical transport evidence.

NEXT_ACTION:
- Keep the causal exception separate while closing the three remaining input packages: Ding-compatible source/material uncertainty, base-Phi/alpha/beta, and physical Kubo/SK/KMS/entropy.

CLAIM_BOUNDARY:
- `CLOSED_FOR_CORE` applies only to the named causal branch. It is not Full Topic 13 closure, external validation, or global UET closure.

EVIDENCE_PATHS:
- `{CAUSAL.relative_to(ROOT).as_posix()}`
- `{MATRIX.relative_to(ROOT).as_posix()}`

EVIDENCE_HASHES:
- causal artifact SHA-256: `{causal_hash}`
- closure matrix SHA-256: `{matrix_hash}`
"""
    log_changed = append_once(UPDATE_LOG, MARKER, log_entry)

    ledger_marker = "## Topic 13 Causal Branch Roadmap Synchronization"
    ledger_entry = f"""{ledger_marker}

- area: `research-core`
- workspace: `Topic 13 Thermodynamic Bridge`
- files/artifacts: `TOPIC13_FULL_CLOSURE_ROADMAP.md`, causal compatibility artifact, closure matrix
- verification: causal branch `CLOSED_FOR_CORE`; Full Topic matrix remains `21/5/0/10`; no dependency unlock
- public-safety: `blocked` for Full Topic 13 promotion
- remaining: preserve the original conserved-C baseline blocker and close the three missing input packages
- next action: obtain accepted source/calibration/physical-transport evidence; do not relabel the causal exception as Full Topic closure
"""
    ledger_changed = append_once(LEDGER, ledger_marker, ledger_entry)

    print(json.dumps({
        "status": "PASS_T13_CAUSAL_ROADMAP_SYNC",
        "roadmap_changed": roadmap_changed,
        "update_log_changed": log_changed,
        "ledger_changed": ledger_changed,
        "causal_closure_level": causal_result["closure_level"],
        "full_topic_matrix_counts": counts,
        "full_core_unlock": matrix["full_core_unlock"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
