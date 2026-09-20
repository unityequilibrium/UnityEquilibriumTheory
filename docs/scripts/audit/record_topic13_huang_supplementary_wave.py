from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

update_block = "\n".join(
    [
        "### 2026-08-13 - Huang 2023 graphite supplementary source boundary",
        "",
        "MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_HUANG_2023_SUPPLEMENTARY_PAYLOAD_BOUNDARY`.",
        "WHAT_IS_ACTUALLY_CLOSED: The public Huang 2023 supplementary PDF is source-locked by article/repository/supplementary locators, size `2726877` bytes, SHA-256 `aaf2f325ddc797e7c309132e65d69379e4223e049e7411e6c3dc04cba9e09b90`, and a reviewed 9-page boundary. The package is classified as figure/method/narrative material only; no row-level PBTE, mode-resolved `C_src`, or force-constant payload is accepted.",
        "WHAT_REMAINS_OPEN: This route does not provide numeric PBTE input, does not establish equivalence to Ding's HOPG TTG regime, and does not close Ding `C_src`, base-Phi SI mapping, or independent `alpha_Phi_K`.",
        "DEPENDENCY_UNLOCKED: Huang graphite comparator provenance only; no Ding source, alpha, bridge, transport, Core, Gravity, or Galaxy unlock.",
        "STATUS: `PASS_HUANG_PUBLIC_SUPPLEMENTARY_BOUNDARY_NO_NUMERIC_PBTE_PAYLOAD`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.",
        "WHAT_CHANGED: Added `docs/scripts/audit/audit_topic13_huang_2023_supplementary_payload_boundary.py`, the raw supplementary PDF, `docs/core/07_artifacts/topic13/t13_huang_2023_supplementary_payload_boundary_audit.json` (SHA-256 `b7bf5b4c567d588a685be131e092e22af566f9068d73f5274961645a6ab18453`), a focused test, full-gate integration, and major-result/dependency register integration. Full gate SHA-256 is `888e2ff3cd23a2e4b1b4454b53039c76fd7b3a8083cb8dd6cf2427e7d25beaeb`; register SHA-256 is `730cd7ab782e51e5b29ddc4bb8d5f017724f34413ae34d5059d3863767e4db72`; dependency gate SHA-256 is `0187e8b5047cd49c5aca866e587f7e9d20c4f25e8adf808052a0094c4bb47c82`.",
        "EQUATION_OR_MAPPING: Comparator role remains `y_TTG = Delta_Tq(t) / Delta_Tq(0)`; no plotted curve was digitized and no PDF value was relabeled as `C_src` or `alpha_Phi_K`.",
        "VERIFICATION: Supplementary file header, size, SHA-256, page-marker count, repository inventory boundary, no machine-readable payload, no curve digitization, no target fit, no alpha fit, and no Xie 2026 holdout access pass. Focused source/register tests pass (`2 passed`).",
        "CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing` remains the source controller; the full gate also retains independent `alpha_Phi_K`, bridge/beta, EOS/transport/KMS/entropy, dimensional map, and material-regime blockers.",
        "NEXT_ACTION: Obtain an authorized numeric Ding PBTE payload or accepted same-regime reproduction with mode-resolved `C_src(T)`, convergence, uncertainty, and units; keep this public route as comparator provenance only.",
        "CLAIM_BOUNDARY: This closes only a public supplementary source-availability boundary for an independent graphite hydrodynamic comparator. It is not Ding PBTE reproduction, UET transport validation, temperature prediction, alpha calibration, external validation, or Full Topic 13 closure.",
        "",
    ]
)

manifest_block = "\n".join(
    [
        "",
        "## Huang 2023 Graphite Supplementary Source Boundary (2026-08-13)",
        "",
        "MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_HUANG_2023_SUPPLEMENTARY_PAYLOAD_BOUNDARY`.",
        "WHAT_IS_ACTUALLY_CLOSED: The public supplementary PDF is archived with SHA-256 `aaf2f325ddc797e7c309132e65d69379e4223e049e7411e6c3dc04cba9e09b90`; 9 pages were reviewed and no machine-readable PBTE, mode-resolved `C_src`, or force-constant payload was accepted.",
        "WHAT_REMAINS_OPEN: Numeric PBTE source, Ding material/regime mapping, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, and full thermal closure remain open.",
        "DEPENDENCY_UNLOCKED: Independent Huang graphite comparator provenance only; no Ding source or downstream dependency unlock.",
        "STATUS: `PASS_HUANG_PUBLIC_SUPPLEMENTARY_BOUNDARY_NO_NUMERIC_PBTE_PAYLOAD`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.",
        "WHAT_CHANGED: Added the raw PDF, source-boundary audit artifact, focused test, and full-gate/register links. Audit artifact SHA-256 `b7bf5b4c567d588a685be131e092e22af566f9068d73f5274961645a6ab18453`; full gate SHA-256 `888e2ff3cd23a2e4b1b4454b53039c76fd7b3a8083cb8dd6cf2427e7d25beaeb`.",
        "EQUATION_OR_MAPPING: `y_TTG = Delta_Tq(t) / Delta_Tq(0)` is retained only as the comparator measurement layer; figure curves were not digitized.",
        "VERIFICATION: Source hash and package boundary pass; no fit, no holdout access, and no alpha emission.",
        "CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.",
        "NEXT_ACTION: Use an authorized numeric PBTE payload or accepted same-regime reproduction; do not promote the PDF into `C_src`.",
        "CLAIM_BOUNDARY: Provenance boundary/comparator only, not Ding source closure or Full Topic 13 closure.",
        "",
    ]
)

current_block = "\n".join(
    [
        "",
        "## Huang 2023 Graphite Supplementary Boundary (2026-08-13)",
        "",
        "MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_HUANG_2023_SUPPLEMENTARY_PAYLOAD_BOUNDARY`.",
        "WHAT_IS_ACTUALLY_CLOSED: The NIMS/publisher supplementary PDF is source-locked at 2726877 bytes with SHA-256 `aaf2f325ddc797e7c309132e65d69379e4223e049e7411e6c3dc04cba9e09b90`. Review of all 9 pages found figures, methods, and narrative but no row-level PBTE or force-constant payload; curves were not digitized.",
        "WHAT_REMAINS_OPEN: This independent isotopically purified graphite-ribbon comparator is not declared equivalent to Ding's HOPG TTG/PBTE regime. Numeric Ding `C_src`, base-Phi SI mapping, and independent `alpha_Phi_K` remain open.",
        "DEPENDENCY_UNLOCKED: Huang comparator provenance only; no source, alpha, bridge, transport, Core, Gravity, or Galaxy unlock.",
        "STATUS: `PASS_HUANG_PUBLIC_SUPPLEMENTARY_BOUNDARY_NO_NUMERIC_PBTE_PAYLOAD`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.",
        "WHAT_CHANGED: Added the source-boundary artifact and integrated it into full gate SHA-256 `888e2ff3cd23a2e4b1b4454b53039c76fd7b3a8083cb8dd6cf2427e7d25beaeb` and register SHA-256 `730cd7ab782e51e5b29ddc4bb8d5f017724f34413ae34d5059d3863767e4db72`.",
        "EQUATION_OR_MAPPING: Comparator layer only: `y_TTG = Delta_Tq(t) / Delta_Tq(0)`; no `C_src`, `Delta_Tq = alpha_Phi_K * Delta_Phi`, or temperature prediction is emitted.",
        "VERIFICATION: Hash, size, PDF/page boundary, no numeric payload, no digitization, no fit, no alpha fit, and no Xie 2026 holdout access pass.",
        "CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing` plus the existing alpha, bridge/beta, EOS/transport/KMS/entropy, dimensional-map, and material-regime blockers.",
        "NEXT_ACTION: Obtain an authorized numeric Ding payload or accepted same-regime PBTE reproduction with convergence, uncertainty, and units.",
        "CLAIM_BOUNDARY: Independent public comparator provenance only; not Ding validation, UET transport validation, alpha calibration, or Full Topic 13 closure.",
        "",
    ]
)

ledger_block = "\n".join(
    [
        "",
        "## Topic 13 Huang 2023 supplementary boundary wave",
        "",
        "- area: `research-core` (secondary: `result-artifacts`)",
        "- workspace: `docs/topics/0.13_Thermodynamic_Bridge`",
        "- files/artifacts: Huang supplementary PDF; source-boundary audit script/artifact/test; full gate; major-result register and dependency gate",
        "- verifier: focused source/register tests passed (`2 passed`); full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`",
        "- public-safety: `partial`",
        "- result: public supplementary route is closed as a provenance boundary with zero accepted machine-readable PBTE payload files; it is not promoted to Ding `C_src`",
        "- hashes: raw source `aaf2f325ddc797e7c309132e65d69379e4223e049e7411e6c3dc04cba9e09b90`; audit artifact `b7bf5b4c567d588a685be131e092e22af566f9068d73f5274961645a6ab18453`; full gate `888e2ff3cd23a2e4b1b4454b53039c76fd7b3a8083cb8dd6cf2427e7d25beaeb`; register `730cd7ab782e51e5b29ddc4bb8d5f017724f34413ae34d5059d3863767e4db72`; dependency gate `0187e8b5047cd49c5aca866e587f7e9d20c4f25e8adf808052a0094c4bb47c82`",
        "- remains: Ding numeric `C_src`, material/regime mapping, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, EOS/transport/KMS/entropy, and dimensional closure",
        "- next action: obtain permitted numeric PBTE payload or accepted same-regime reproduction; no curve digitization, holdout access, or target fitting",
        "- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree",
        "",
    ]
)


def append_once(path: Path, marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        path.write_text(text.rstrip() + "\n" + block, encoding="utf-8")


append_once(ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md", "### 2026-08-13 - Huang 2023 graphite supplementary source boundary", update_block)
append_once(ROOT / "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md", "## Huang 2023 Graphite Supplementary Source Boundary (2026-08-13)", manifest_block)
append_once(ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md", "## Huang 2023 Graphite Supplementary Boundary (2026-08-13)", current_block)
append_once(ROOT / "WORK_LEDGER/2026/2026-08-13.md", "## Topic 13 Huang 2023 supplementary boundary wave", ledger_block)
print("recorded")
