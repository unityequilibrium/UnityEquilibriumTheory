"""Integrate the named regularized continuum heat-current lane."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/07_artifacts/topic13/t13_uet_o2_regularized_continuum_heat_current_audit.json"
FULL_REL = "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json"
REPORT_REL = "docs/topics/0.13_Thermodynamic_Bridge/FULL_THERMODYNAMIC_BRIDGE_CORE_READY_CURRENT.md"
MANIFEST_REL = "docs/topics/0.13_Thermodynamic_Bridge/DATA_MANIFEST.md"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
LEDGER_REL = "WORK_LEDGER/2026/2026-08-20.md"
LANE_KEY = "uet_o2_regularized_continuum_heat_current_lane"
LANE_ID = "T13_UET_O2_REGULARIZED_CONTINUUM_HEAT_CURRENT_LANE"


def load(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def append_unique(items: list[Any], value: Any) -> None:
    if value not in items:
        items.append(value)


def append_marker(relative: str, marker: str, content: str) -> None:
    path = ROOT / relative
    current = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
    if marker not in current:
        path.write_text(current.rstrip() + "\n\n" + content.strip() + "\n", encoding="utf-8")


def main() -> int:
    action = load(ACTION_REL)
    if action.get("status") != "PASS_ACTION_DERIVED_REGULARIZED_CONTINUUM_HEAT_CURRENT_LANE":
        raise SystemExit(f"regularized lane is not passing: {action.get('status')}")
    major = action.get("major_result")
    if not isinstance(major, dict) or major.get("major_result_id") != LANE_ID:
        raise SystemExit("regularized lane major-result identity mismatch")
    state = action["state"]
    evidence = {"path": ACTION_REL, "sha256": digest(ACTION_REL)}

    full = load(FULL_REL)
    full_major = full["major_result"]
    append_unique(
        full_major["what_is_closed"],
        "a named normal-branch compactified regularized continuum heat-current lane passes the unchanged convergence and conservation contract without replacing the failed finite-cutoff baseline",
    )
    for blocker in major["open_blockers"]:
        append_unique(full_major["what_remains_open"], blocker)
    append_unique(full.setdefault("evidence_artifacts", []), evidence)
    full["claim_promotion"] = False
    full["next_action"] = (
        "Retain the named regularized natural-unit lane as scoped evidence; close loop-renormalized self-energy and physical Kubo provenance, condensed two-fluid/SK-KMS completion, dimensional Phi mapping, independent alpha calibration, and Ding C_src before any Core-ready promotion."
    )
    full["generated_at"] = date.today().isoformat()
    transport = full.setdefault("verification_status", {}).setdefault(
        "eos_transport_kms_entropy", {}
    )
    lane = transport.get(LANE_KEY)
    if not isinstance(lane, dict) or lane.get("major_result_id") != LANE_ID:
        raise SystemExit("full gate did not discover regularized lane")
    lane["integration_evidence"] = evidence
    lane["full_core_unlock"] = False
    (ROOT / FULL_REL).write_text(
        json.dumps(full, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )

    report_marker = "## Regularized Continuum Heat-Current Lane (T13-142)"
    append_marker(
        REPORT_REL,
        report_marker,
        f"""{report_marker}

MAJOR_RESULT_CLOSURE: `{major['closure_level']}`
WHAT_IS_ACTUALLY_CLOSED: A named normal-branch compactified radial heat-current scheme is closed for lane. It uses the existing action-derived normal dispersion and constant-amplitude collision width, projects charge/energy/three-momentum invariants, and passes the unchanged `1e-2` radial/angular/scale controller.
WHAT_REMAINS_OPEN: Loop-renormalized off-shell self-energy, physical Kubo provenance, condensed finite-temperature two-fluid completion, full SK/KMS matching, dimensional `Phi` to thermal observable mapping, independent `alpha_Phi_K`, and Ding `C_src` remain open.
DEPENDENCY_UNLOCKED: This unlocks only the named natural-unit normal-branch lane; it does not unlock physical transport, SI mapping, TTG, Core, Gravity, or Full Topic 13.
STATUS: `{action['status']}`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added `{ACTION_REL}` and synchronized the full gate and research-room reporting surfaces.
EQUATION_OR_MAPPING: `k=Lambda*u/(1-u)`; `b_q=(E-h*q)*(p_x/E)*sqrt(w)`; `L_reg=P*diag(Gamma_s(k))*P`; `kappa=Re[b_q^T(L_reg-i*omega*I)^(-1)b_q]`.
VERIFICATION: `kappa_natural={state['kappa_natural']:.9g}`; radial maximum change `{state['radial_max_relative_change']:.6g}`, angular change `{state['angular_refined_relative_change']:.6g}`, scale change `{state['scale_refined_relative_change']:.6g}`; conservation residual `{state['conservation_residual']:.6g}`; source residual `{state['source_constraint_residual']:.6g}`; entropy `{state['entropy_production']:.6g}`; KMS residual `{state['kms_ratio_residual']:.6g}`. No fit, target, physical coefficient, numeric alpha, or Xie 2026 holdout was used.
CONTROLLING_BLOCKER: `{action['controlling_blocker']}` for this lane; full Topic 13 still retains the source, dimensional, alpha, EOS/transport/KMS/entropy, and material-regime blockers.
NEXT_ACTION: Keep this branch as scoped natural-unit evidence and close physical Kubo/source provenance and the remaining independent dimensional bridge before promotion.
CLAIM_BOUNDARY: `CLOSED_FOR_LANE` only. The branch does not replace the failed finite-cutoff baseline, prove a physical transport coefficient, or close Full Topic 13.
""",
    )

    log_marker = "## 2026-08-20 - Regularized continuum heat-current lane (T13-142)"
    append_marker(
        LOG_REL,
        log_marker,
        f"""{log_marker}

MAJOR_RESULT_CLOSURE: `{major['closure_level']}`
WHAT_IS_ACTUALLY_CLOSED: Named normal-branch compactified radial heat-current lane passes radial, angular, scale, conservation, positivity, entropy, KMS, and FDT checks.
WHAT_REMAINS_OPEN: Physical Kubo/SI provenance, condensed two-fluid/SK-KMS completion, dimensional `Phi` map, independent alpha, and Ding `C_src` remain open.
DEPENDENCY_UNLOCKED: Named natural-unit lane only; no Core or Full Topic 13 unlock.
STATUS: `{action['status']}` with global claim promotion disabled.
WHAT_CHANGED: Added the regularized continuum module, audit artifact, regression test, full-gate discovery, and report synchronization.
EQUATION_OR_MAPPING: Compactified `k=Lambda*u/(1-u)` with `L_reg=P*diag(Gamma_s(k))*P` and heat source `b_q=(E-h*q)*(p_x/E)*sqrt(w)`.
VERIFICATION: Radial `{state['radial_max_relative_change']:.6g}`, angular `{state['angular_refined_relative_change']:.6g}`, scale `{state['scale_refined_relative_change']:.6g}` all pass `1e-2`; no fit, target, physical coefficient, alpha, or holdout access.
CONTROLLING_BLOCKER: `{action['controlling_blocker']}` for the named lane; full bridge blockers remain controlling globally.
NEXT_ACTION: Physical Kubo/source provenance and the independent dimensional bridge remain next.
CLAIM_BOUNDARY: Lane-level natural-unit result only; no external validation or Full Topic 13 closure.
""",
    )

    manifest_marker = "### T13-142 — Regularized continuum heat-current lane"
    append_marker(
        MANIFEST_REL,
        manifest_marker,
        f"""{manifest_marker}

MAJOR_RESULT_CLOSURE: `{major['closure_level']}`
WHAT_IS_ACTUALLY_CLOSED: The named normal-branch compactified radial heat-current scheme passes the unchanged `1e-2` convergence controller and explicit conservation/positivity/entropy checks.
WHAT_REMAINS_OPEN: Physical Kubo/SI provenance, condensed two-fluid/SK-KMS completion, dimensional `Phi` map, independent `alpha_Phi_K`, and Ding `C_src` remain open.
DEPENDENCY_UNLOCKED: Named natural-unit lane only.
STATUS: `{action['status']}`.
WHAT_CHANGED: `{ACTION_REL}` with SHA256 `{digest(ACTION_REL)}`.
EQUATION_OR_MAPPING: `k=Lambda*u/(1-u)` and `L_reg=P*diag(Gamma_s(k))*P`.
VERIFICATION: `kappa_natural={state['kappa_natural']:.9g}`, radial max `{state['radial_max_relative_change']:.6g}`, angular `{state['angular_refined_relative_change']:.6g}`, scale `{state['scale_refined_relative_change']:.6g}`.
CONTROLLING_BLOCKER: `{action['controlling_blocker']}` for this lane.
NEXT_ACTION: Source-lock physical Kubo and close the remaining dimensional/thermal bridge dependencies.
CLAIM_BOUNDARY: Natural-unit lane evidence only; no physical coefficient or external validation.
""",
    )

    ledger_marker = "## Topic 13 Regularized Continuum Heat-Current Lane"
    append_marker(
        LEDGER_REL,
        ledger_marker,
        f"""{ledger_marker}

- area id: `research-core` (secondary: `result-artifacts`)
- workspace: `docs/core` and `docs/topics/0.13_Thermodynamic_Bridge`
- changed: added the named compactified normal-branch heat-current lane, audit, test, full-gate integration, and reporting sync
- verification: `{action['status']}`; radial `{state['radial_max_relative_change']:.6g}`, angular `{state['angular_refined_relative_change']:.6g}`, scale `{state['scale_refined_relative_change']:.6g}`, threshold `0.01`
- public-safety status: `partial`; natural-unit lane only, no physical Kubo/SI/alpha promotion
- current claim boundary: `{LANE_ID}` is `{major['closure_level']}`; Full Topic 13 remains blocked
- uncommitted: scoped Topic 13/Core files remain uncommitted; unrelated worktree changes were not edited
- next action: close physical Kubo/source provenance and the independent dimensional bridge
""",
    )
    print(
        json.dumps(
            {
                "status": "PASS_INTEGRATED_T13_REGULARIZED_CONTINUUM_HEAT_CURRENT",
                "major_result_id": LANE_ID,
                "full_topic13_status": full["status"],
                "full_core_unlock": False,
                "action_sha256": digest(ACTION_REL),
                "full_gate_sha256": digest(FULL_REL),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
