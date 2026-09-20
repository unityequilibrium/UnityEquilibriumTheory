"""Link the formal Topic 13 bridge-boundary result into dependency metadata."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ACTION_REL = "docs/core/07_artifacts/topic13/t13_formal_bridge_boundary_audit.json"
REGISTER_REL = "docs/core/07_artifacts/gates/uet_major_result_closure_register.json"
DEPENDENCY_REL = "docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json"
LOG_REL = "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"


def load(relative: str) -> dict:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {relative}")
    return value


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    action = load(ACTION_REL)
    if action.get("status") != "PASS_FORMAL_NONCIRCULAR_BRIDGE_BOUNDARY":
        raise SystemExit(f"formal bridge audit is not passing: {action.get('status')}")
    register = load(REGISTER_REL)
    dependency = load(DEPENDENCY_REL)
    evidence = {
        "path": ACTION_REL,
        "sha256": digest(ACTION_REL),
        "summary": {
            "status": action["status"],
            "major_result_id": action["major_result"]["major_result_id"],
            "full_core_unlock": False,
        },
    }
    partial = dependency.setdefault("topic13_partial_evidence", {})
    partial["formal_non_circular_bridge_boundary"] = evidence
    partial["reason"] = (
        "Formal beta, Phi_E, EOS, and SK/KMS/entropy interfaces are now composed into a bounded lane result; "
        "physical Phi normalization, independent alpha, source-backed beta, Kubo coefficients, and full closure remain open."
    )
    dependency["generated_at"] = date.today().isoformat()
    dependency.setdefault("register", {})["sha256"] = digest(REGISTER_REL)
    dependency["register_sha256"] = digest(REGISTER_REL)
    DEPENDENCY = ROOT / DEPENDENCY_REL
    DEPENDENCY.write_text(json.dumps(dependency, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    marker = "### 2026-08-12 - Formal non-circular bridge boundary"
    log_path = ROOT / LOG_REL
    log = log_path.read_text(encoding="utf-8-sig")
    if marker not in log:
        log += f"""

{marker}

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`
WHAT_IS_ACTUALLY_CLOSED: The beta, named `Phi_E`, conditional EOS, and formal SK/KMS/entropy interfaces are composed into one machine-readable boundary. The Landauer identity cannot supply a UET beta, and normalized or natural-unit field rescaling cannot supply a base-Phi SI anchor.
WHAT_REMAINS_OPEN: Physical base-Phi normalization, independent `alpha_Phi_K`, source-backed `beta_T13`, numeric Ding `C_src` or an accepted reproduction package, physical Kubo coefficients, finite-temperature normal response, and full entropy/dissipative closure.
DEPENDENCY_UNLOCKED: No downstream dependency. This is a lane-level claim boundary only.
STATUS: `{action['status']}`
WHAT_CHANGED: Added `{action['major_result']['major_result_id']}` and linked its artifact/hash into dependency metadata.
EQUATION_OR_MAPPING: `Phi_E=Delta_u/e0`; `Delta_Tq=(e0/c_v)*Phi_E`; `Delta_Tq=alpha_Phi_K*Delta_Phi`; `beta_T13=T0*(da_Phi/dT)|T0`.
VERIFICATION: All source artifacts report lane-level PASS; no numeric base alpha, fit, target data, or Xie 2026 holdout was used.
CONTROLLING_BLOCKER: `physical_Phi_SI_anchor_and_independent_alpha_Phi_K_missing`.
NEXT_ACTION: Obtain an independent paired base-Phi amplitude and SI observable, then source-lock beta and one state-matched physical Kubo coefficient.
CLAIM_BOUNDARY: This closes the formal bridge boundary only. It is not physical thermal validation, Full Topic 13 closure, or global UET closure.
"""
        log_path.write_text(log, encoding="utf-8")
    print(json.dumps({"status": "PASS_INTEGRATED_FORMAL_BRIDGE_BOUNDARY", "dependency_unlock": False, "action_sha256": digest(ACTION_REL)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
