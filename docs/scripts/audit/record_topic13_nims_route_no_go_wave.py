"""Record the NIMS graphite source-route no-go wave in Topic 13 logs."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARTIFACT = ROOT / "docs/core/07_artifacts/topic13/t13_nims_graphite_ltc_route_no_go.json"
FULL_GATE = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
MANIFEST = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md"
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
CURRENT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-13.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_once(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8-sig")
    if marker in text:
        return
    path.write_text(text.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")


def main() -> int:
    artifact_hash = sha256(ARTIFACT)
    full_hash = sha256(FULL_GATE)
    common = """MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_NIMS_GRAPHITE_LTC_ROUTE_NO_GO`.
WHAT_IS_ACTUALLY_CLOSED: The public NIMS lattice-thermal-conductivity collection was searched with exact `C`, `Graphite`, `Carbon`, `graphite`, and `specimen:graphite` terms. Exact graphite/carbon searches returned zero records; the 349-row carbon full-text result was scanned across 35 pages with zero elemental-carbon formula `C` material records. The two public API `specimen:\"graphite\"` records belong to `MDR XAFS DB`, not the LTC collection.
WHAT_REMAINS_OPEN: Ding numeric `C_src` or a permitted same-regime PBTE reproduction with mode-resolved rows, SI units, uncertainty, convergence, and material-state mapping remains open. The independent `alpha_Phi_K` calibration remains open. :codex-annotation{index="1"}
DEPENDENCY_UNLOCKED: NIMS graphite-source route exclusion only; no `C_src`, alpha, bridge, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_NIMS_GRAPHITE_ROUTE_NO_GO`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added `docs/core/07_artifacts/topic13/t13_nims_graphite_ltc_route_no_go.json` (SHA-256 `""" + artifact_hash + """`), integrated it into the full-gate source-package lane, and added a focused test. The regenerated full gate is `""" + full_hash + """`.
EQUATION_OR_MAPPING: Required source quantity remains `C_src(T)=sum_mu c_mu(T)` with `C_src` in `J m^-3 K^-1`; `Delta_Tq=Delta_u_ph/C_src`. This route emits no numeric `C_src` and no `Delta_Tq=alpha_Phi_K*Delta_Phi` calibration.
VERIFICATION: Public NIMS collection/API metadata was source-located, query outcomes and response hashes were recorded, no numeric research payload was consumed, no fit/tuning/alpha emission occurred, Xie 2026 was not accessed, and focused source-route tests passed (`6 passed`).
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`; full Topic 13 remains additionally controlled by the dimensional Phi anchor/independent alpha, bridge/beta, EOS/transport/KMS/entropy, and uncertainty blockers.
NEXT_ACTION: Pursue the Ding author route or another permitted same-regime PBTE source. Do not reopen the NIMS route unless its collection metadata changes, and do not substitute XAFS, harmonic DOS, graphene, or unrelated graphite comparators.
CLAIM_BOUNDARY: This closes only the NIMS source-route no-go. It is not `C_src` evidence, an independent alpha calibration, TTG prediction, external validation, Core closure, or global UET closure."""

    append_once(
        MANIFEST,
        "## NIMS Graphite LTC Route No-Go (2026-08-13)",
        """## NIMS Graphite LTC Route No-Go (2026-08-13)

The public [NIMS MDR lattice thermal conductivity collection](https://mdr.nims.go.jp/collections/0113dccc-ec45-42ed-86db-f455f9b63fb1?locale=en) was checked through its exact subject and full-text search routes. `C`, `Graphite`, `Carbon`, `graphite`, and `specimen:graphite` searches returned no record in that collection. The `carbon` full-text result set (349 records over 35 pages) contained no elemental-carbon formula `C` material record. A public API cross-check returned two `specimen:"graphite"` records, both in the unrelated `MDR XAFS DB` collection.

Artifact: `docs/core/07_artifacts/topic13/t13_nims_graphite_ltc_route_no_go.json` (SHA-256 `""" + artifact_hash + """). This is a source-route no-go only; it does not produce `C_src`, replace Ding, or unlock `alpha_Phi_K`.
""",
    )
    append_once(UPDATE_LOG, "### 2026-08-13 - NIMS graphite LTC source-route no-go", "### 2026-08-13 - NIMS graphite LTC source-route no-go\n\n" + common)
    append_once(CURRENT, "### 2026-08-13 - NIMS graphite LTC source-route no-go", "### 2026-08-13 - NIMS graphite LTC source-route no-go\n\n" + common)
    append_once(
        LEDGER,
        "## Topic 13 NIMS graphite LTC source-route no-go wave",
        """## Topic 13 NIMS graphite LTC source-route no-go wave
- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: NIMS source-route no-go artifact; full-gate source-package integration; focused source-route test; data manifest; update log; current full-bridge report
- verifier: `PASS_SCOPED_NIMS_GRAPHITE_ROUTE_NO_GO`; focused tests `6 passed`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: NIMS graphite LTC route is closed as a documented no-go; no numeric `C_src`, alpha, holdout, or claim promotion was emitted
- hashes: NIMS artifact `""" + artifact_hash + """`; full gate `""" + full_hash + """
- remains: Ding-compatible numeric `C_src` or accepted same-regime reproduction, independent `alpha_Phi_K`, base-Phi SI anchor, bridge/beta, physical transport/KMS/entropy, and source-grade uncertainty
- next action: pursue authorized Ding or same-regime PBTE source; keep Xie 2026 locked and do not relabel unrelated NIMS/XAFS/graphene/DOS data
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
""",
    )
    print({"artifact_sha256": artifact_hash, "full_gate_sha256": full_hash})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
