from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md"
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_independent_csrc_acceptance_contract.json"
FULL_GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


entry = f"""

## Independent C_src Acceptance Contract (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT`.
WHAT_IS_ACTUALLY_CLOSED: The source package now has an explicit acceptance contract separating raw-author Ding `C_src` from an accepted independent PBTE reproduction. Required fields include source identity/hash, raw payload, material/state mapping, mode-resolved response, SI units, uncertainty, convergence, independence, and holdout/fit audit.
WHAT_REMAINS_OPEN: Current acceptance is `BLOCKED`: Ding numeric author payload is absent and MP48 remains a harmonic ideal-graphite comparator, not a Ding-equivalent PBTE response.
DEPENDENCY_UNLOCKED: Source acceptance policy only; no Ding `C_src`, alpha, bridge, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_INDEPENDENT_C_SRC_ACCEPTANCE_CONTRACT`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added `docs/core/07_artifacts/topic13/t13_independent_csrc_acceptance_contract.json` (SHA-256 `{digest(ARTIFACT)}`) and linked it to the full gate (SHA-256 `{digest(FULL_GATE)}`).
EQUATION_OR_MAPPING: `C_src(T)=sum_mu c_mu(T)`; `Delta_Tq=Delta_u_ph/C_src`. Harmonic `c_v` and normalized TTG rows cannot satisfy this acceptance contract by relabeling.
VERIFICATION: The contract evaluates raw-author and independent routes as false, preserves no-fit/no-holdout rules, and focused acceptance tests pass. No synthetic source or numeric alpha is emitted.
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.
NEXT_ACTION: Obtain an authorized Ding numeric package or a permitted same-regime PBTE reproduction with source-grade units, uncertainty, convergence, and material-state mapping.
CLAIM_BOUNDARY: This is a source-acceptance policy and candidate boundary only. It is not Ding validation, `C_src` evidence, `alpha_Phi_K`, or Full Topic 13 closure.
"""

text = MANIFEST.read_text(encoding="utf-8-sig")
marker = "## Independent C_src Acceptance Contract (2026-08-13)"
if marker not in text:
    MANIFEST.write_text(text.rstrip() + entry, encoding="utf-8")
print("updated Topic 13 data manifest")
