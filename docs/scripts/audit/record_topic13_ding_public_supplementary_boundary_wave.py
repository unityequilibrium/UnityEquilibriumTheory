"""Record the completed Ding public-supplementary boundary wave."""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LANE = ROOT / "docs/core/07_artifacts/topic13/t13_ding_public_supplementary_payload_boundary_audit.json"
FULL = ROOT / (
    "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/"
    "topic13_full_thermodynamic_bridge_core_ready_gate.json"
)
REGISTER = ROOT / "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
MANIFEST = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md"
REPORT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-12.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_once(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"already recorded {path.relative_to(ROOT).as_posix()}")
        return
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + "\n" + block.strip() + "\n", encoding="utf-8")
    print(f"recorded {path.relative_to(ROOT).as_posix()}")


def main() -> int:
    lane_hash = sha256(LANE)
    full_hash = sha256(FULL)
    register_hash = sha256(REGISTER)
    today = date.today().isoformat()

    manifest_block = f"""
## Ding 2022 Public Supplementary Payload Boundary ({today})

The official PMC S3 inventory is pinned at
`docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_pmc_s3_inventory.xml`
with SHA-256 `{sha256(ROOT / 'docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_pmc_s3_inventory.xml')}`.
It contains 11 objects. The three MOESM supplementary objects are archived locally
as PDF bytes; no machine-readable numeric payload object for PBTE `C_src` was
identified.

| Object | Local path | Size | SHA-256 | Role |
|:--|:--|--:|:--|:--|
| MOESM1 | `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_supplementary_information.pdf` | 1,893,976 | `a50c1a6347775de72f705f4395507d3136cbf4e5cadfb6638caca2876c52b8f7` | methods/equations/figures |
| MOESM2 | `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_supplementary_materials_2.pdf` | 4,537,623 | `2f7d1d057df83b8d3408f65c833dad7542fca8b24aeec087e304842fa5aca6e7` | reviewer response |
| MOESM3 | `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/ding_2022_supplementary_materials_3.pdf` | 927,333 | `4405683b720a24437d64fe3429d409503fcc91bd33c1e8616a3252cc50d94c5f` | reporting summary |

The machine-readable boundary result is
`docs/core/07_artifacts/topic13/t13_ding_public_supplementary_payload_boundary_audit.json`
with SHA-256 `{lane_hash}`. This closes only the public supplementary
availability lane; the author-request or accepted PBTE reproduction route remains open.
"""
    append_once(MANIFEST, "## Ding 2022 Public Supplementary Payload Boundary", manifest_block)

    report_block = f"""
## Ding Public Supplementary Payload Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The official 11-object Ding PMC inventory and all three MOESM PDFs are locally hash-pinned. The public machine-readable route contains no raw numeric `C_src` or PBTE input payload object.

WHAT_REMAINS_OPEN: Ding mode-resolved numeric `C_src`, an accepted same-regime PBTE reproduction, independent `alpha_Phi_K`, the non-circular bridge/beta, EOS/transport/KMS/entropy, and the dimensional `Phi` to thermal-observable map.

DEPENDENCY_UNLOCKED: Public Ding supplementary provenance boundary only. No full-source, alpha, Core, Gravity, or constitutive-transport dependency is unlocked.

STATUS: `PASS_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY_NO_NUMERIC_C_SRC`

WHAT_CHANGED: Added `docs/core/07_artifacts/topic13/t13_ding_public_supplementary_payload_boundary_audit.json`, integrated it into the Topic 13 full gate under `verification_status.source_package`, and recorded the MOESM1-3 hashes in `DATA_MANIFEST.md`.

EQUATION_OR_MAPPING: `C_src(T) = sum_mu c_mu(T)` and `Delta_Tq = Delta_u_ph / C_src` remain Ding source definitions; the audited PDFs and figures are not relabeled as numeric `C_src` rows. The measurement layer remains `y_TTG = Delta_Tq(t) / Delta_Tq(0)`.

VERIFICATION: Public inventory count, object-key set, PDF sizes, local hashes, no machine-readable numeric payload extension, holdout exclusion, and no alpha fitting pass. Focused Topic 13 suite: `16 passed`. Full gate hash: `{full_hash}`. Major-result register hash: `{register_hash}`.

CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.

NEXT_ACTION: Use the recorded corresponding-author request route if authorized, or build an accepted Ding-regime PBTE reproduction with mode-resolved `C_src(T)`, convergence, uncertainty, and unit contracts. Do not relabel MP48, figures, or PDFs as `C_src`.

CLAIM_BOUNDARY: This closes only the public supplementary payload-availability boundary. Full Topic 13 remains `PARTIAL / BLOCKED`; no external validation, independent `alpha_Phi_K`, or global UET closure is claimed.
"""
    append_once(REPORT, "## Ding Public Supplementary Payload Boundary", report_block)

    update_block = f"""
### {today} - Ding public supplementary payload boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_DING_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY`.

WHAT_IS_ACTUALLY_CLOSED: The official 11-object inventory and MOESM1-3 PDF hashes are locked; no machine-readable numeric PBTE payload for `C_src` is present in the audited public route.

WHAT_REMAINS_OPEN: Raw-author or accepted independent Ding-regime `C_src`, independent `alpha_Phi_K`, physical bridge/beta, EOS/transport/KMS/entropy, and dimensional `Phi` mapping.

DEPENDENCY_UNLOCKED: Public source-provenance boundary only; no full Topic 13 dependency unlock.

STATUS: `PASS_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY_NO_NUMERIC_C_SRC`

WHAT_CHANGED: Added and integrated `docs/core/07_artifacts/topic13/t13_ding_public_supplementary_payload_boundary_audit.json` (SHA-256 `{lane_hash}`); updated the data manifest, full gate, closure register, and dependency record.

EQUATION_OR_MAPPING: `C_src(T) = sum_mu c_mu(T)` and `Delta_Tq = Delta_u_ph / C_src`; equations/figures remain source context, not machine-readable numeric `C_src`.

VERIFICATION: Full gate rebuilt as `BLOCKED_OPEN_T13_FULL_BRIDGE`; focused source/alpha integration suite `16 passed`; Xie 2026 was not accessed and no alpha fit was performed.

CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.

NEXT_ACTION: Author request if authorized, otherwise accepted PBTE reproduction with convergence/uncertainty/unit contracts; keep the source lane and full bridge lane separate.

CLAIM_BOUNDARY: Public supplementary availability is closed for lane only. Full Topic 13 remains `PARTIAL / BLOCKED` and `claim_promotion=false`.
"""
    append_once(UPDATE_LOG, "### 2026-08-12 - Ding public supplementary payload boundary", update_block)

    ledger_block = f"""
## Topic 13 Ding Public Supplementary Payload Boundary

- area id: `research-core` (secondary: `data-provenance`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge` Ding 2022 public supplementary route
- changed: archived MOESM1-3, added the public inventory/payload boundary audit, integrated the lane into the full gate, and synchronized manifest/report/register/dependency evidence
- verification: `PASS_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY_NO_NUMERIC_C_SRC`; inventory 11, numeric payload objects 0, local hashes match, focused suite 16 passed
- public-safety status: `partial`; source provenance boundary is closed, but raw `C_src`, alpha, bridge, transport, and full Topic 13 remain blocked
- current claim boundary: `T13_DING_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL / BLOCKED`
- artifacts: lane SHA `{lane_hash}`, full-gate SHA `{full_hash}`, register SHA `{register_hash}`
- next action: use the corresponding-author request route if authorized or build an accepted Ding-regime PBTE reproduction; do not relabel PDFs/figures/MP48 as `C_src`
"""
    append_once(LEDGER, "## Topic 13 Ding Public Supplementary Payload Boundary", ledger_block)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
