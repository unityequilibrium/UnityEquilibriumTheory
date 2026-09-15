"""Record the Topic 13 MP48 mesh-convergence hardening wave."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
MANIFEST = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md"
CURRENT = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
LEDGER = ROOT / "WORK_LEDGER/2026/2026-08-13.md"

MARKER = "### 2026-08-13 - MP48 force-constant C_src mesh-convergence boundary"

UPDATE_ENTRY = f"""

{MARKER}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE`; this closes the convergence question as a scoped no-go, not the source itself.
WHAT_IS_ACTUALLY_CLOSED: The deposited MP48 second-order force constants were evaluated on `5x5x2`, `10x10x4`, and `15x15x6` meshes with the declared Bose heat-capacity kernel. Source integrity and non-negative-mode checks pass, but the largest adjacent-mesh change is `0.513481935500736`, above the declared `0.01` acceptance tolerance.
WHAT_REMAINS_OPEN: MP48 is not accepted as Ding PBTE `C_src`; Ding-compatible mode-resolved `C_src`, material-regime mapping, convergence/uncertainty contract, base-Phi energy anchor, independent `alpha_Phi_K`, bridge/beta, EOS/transport/KMS/entropy, and dimensional observable closure remain open.
DEPENDENCY_UNLOCKED: Only the independent MP48 convergence-boundary lane; no Ding source, alpha, Core, Gravity, transport, or Galaxy unlock.
STATUS: `BLOCKED_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE`; full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added `docs/scripts/audit/audit_topic13_mp48_force_constant_csrc_mesh_convergence.py`, artifact `docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json` (SHA-256 `e7414905d99f4f412c0516d54024d584991e84f2797a4f20d3ec0215cfb39605`), and full-gate/register integration. Latest full-gate SHA-256 is `12a05bc4009fcf836b405309163302dcd54659e49861c3f0b6cee30f06e92846`; register SHA-256 is `c90894f39f18d64b5976b56d80f2ee35799020f78d963a05b0ac6142ea75e43f`.
EQUATION_OR_MAPPING: `C_src^mesh(T) = N_A/N_q * sum_(q,mu) c_mu(q,T)` with `c_mu(T)=k_B*x^2 exp(x)/(exp(x)-1)^2`; the Ding boundary remains `Delta_Tq=Delta_u_ph/C_src` and no MP48 quantity is relabeled as Ding `C_src`.
VERIFICATION: Mesh audit completed; focused no-go and register-sync tests passed (`2 passed`). No fit, no target curve, no Xie 2026 holdout access, and no numeric `alpha_Phi_K` emission.
CONTROLLING_BLOCKER: `mp48_force_constant_C_src_mesh_convergence_missing` controls this independent route; the full gate still retains `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing` and the existing alpha/bridge/transport blockers.
NEXT_ACTION: Obtain a Ding-compatible mode-resolved PBTE package or permissioned author payload with material state, mesh convergence, units, and uncertainty; do not promote the native MP48 mesh by matching one temperature row.
CLAIM_BOUNDARY: This is a source-traceable harmonic convergence boundary. It is not Ding PBTE reproduction, UET transport, a Phi calibration, a TTG prediction, external validation, or Full Topic 13 closure.
"""

MANIFEST_ENTRY = """

## MP48 Force-constant C_src Mesh-Convergence Boundary (2026-08-13)

The independent MP48 force-constant route was tested on `5x5x2`, `10x10x4`,
and `15x15x6` q-meshes. The machine-readable artifact is
`docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json`
with SHA-256 `e7414905d99f4f412c0516d54024d584991e84f2797a4f20d3ec0215cfb39605`.

The maximum adjacent-mesh relative change is `0.513481935500736`, above the
declared `0.01` source-acceptance tolerance. This closes the convergence
question as a scoped no-go for this route; it does not turn MP48 into Ding
PBTE `C_src`, does not close the material-regime map, and does not emit
`alpha_Phi_K`. No target fit or Xie 2026 holdout access occurred.
"""

CURRENT_ENTRY = """

## Latest Source-Route Boundary: MP48 C_src Mesh Convergence (2026-08-13)

The latest independent MP48 force-constant route is machine-readable in
`docs/core/07_artifacts/topic13/t13_mp48_force_constant_csrc_mesh_convergence_audit.json`.
It passes source-integrity and stability checks but fails the declared mesh
convergence criterion: the maximum adjacent-mesh change is `0.513481935500736`
against `0.01`. The route is therefore `CLOSED_FOR_LANE` as a no-go boundary,
while full Topic 13 remains `PARTIAL/BLOCKED` and the Ding `C_src` blocker is
not removed.
"""

LEDGER_ENTRY = """

## Topic 13 MP48 C_src mesh-convergence boundary wave

- area: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/topics/0.13_Thermodynamic_Bridge`
- files/artifacts: force-constant mesh-convergence audit, artifact/test, full-gate integration, major-result register/dependency sync, topic manifest, current report, update log
- verifier: mesh audit completed; focused no-go/register tests passed (`2 passed`); full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`
- public-safety: `partial`
- result: independent MP48 C_src route is closed as a scoped convergence no-go; maximum adjacent-mesh change `0.513481935500736` exceeds declared `0.01`
- hashes: mesh artifact `e7414905d99f4f412c0516d54024d584991e84f2797a4f20d3ec0215cfb39605`; full gate `12a05bc4009fcf836b405309163302dcd54659e49861c3f0b6cee30f06e92846`; register `c90894f39f18d64b5976b56d80f2ee35799020f78d963a05b0ac6142ea75e43f`
- remains: Ding-compatible mode-resolved C_src/material mapping, independent alpha, base-Phi SI anchor, bridge/beta, physical EOS/transport/KMS/entropy, and dimensional closure
- next action: obtain a permitted Ding-compatible PBTE input package or author payload with convergence and uncertainty; do not relabel MP48
- commit/push action: no commit requested; keep scoped changes identifiable in the dirty worktree
"""


def append_once(path: Path, marker: str, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker not in text:
        path.write_text(text.rstrip() + content + "\n", encoding="utf-8")


def main() -> None:
    append_once(UPDATE_LOG, MARKER, UPDATE_ENTRY)
    append_once(MANIFEST, "## MP48 Force-constant C_src Mesh-Convergence Boundary (2026-08-13)", MANIFEST_ENTRY)
    append_once(CURRENT, "## Latest Source-Route Boundary: MP48 C_src Mesh Convergence (2026-08-13)", CURRENT_ENTRY)
    append_once(LEDGER, "## Topic 13 MP48 C_src mesh-convergence boundary wave", LEDGER_ENTRY)


if __name__ == "__main__":
    main()
