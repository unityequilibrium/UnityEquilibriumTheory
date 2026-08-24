"""Record the scoped Topic 13 base-Phi registry audit in the topic log."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/artifacts/t13_base_phi_registry_completeness_audit.json"
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
MARKER = "### 2026-08-24 - Topic 13 base-Phi registry completeness audit"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    audit = json.loads((ROOT / AUDIT_REL).read_text(encoding="utf-8"))
    current = UPDATE_LOG.read_text(encoding="utf-8")
    if MARKER in current:
        print(json.dumps({"status": "PASS_T13_BASE_PHI_REGISTRY_AUDIT_ALREADY_LOGGED"}))
        return 0

    entry = f"""{MARKER}

MAJOR_RESULT_CLOSURE:
- `T13_BASE_PHI_REGISTRY_COMPLETENESS_AUDIT` is `CLOSED_FOR_LANE`; the physical base-Phi SI anchor remains open.

WHAT_IS_ACTUALLY_CLOSED:
- The audit checked the canonical thermal lane, SI conversion module, named energy branch, alpha candidate audit, calibration requirement, and public-source boundary.
- These inputs consistently declare normalized Phi, an open alpha_Phi_K scale, and external E_ref/Phi_scale/e0 inputs; no hidden SI anchor was found.

WHAT_REMAINS_OPEN:
- `base_phi_si_anchor`, `independent_alpha_record`, `normalized_beta_si_map`, and their downstream physical EOS/heat-flux dependencies remain open.

DEPENDENCY_UNLOCKED:
- None. This is a registry completeness result only; Full Topic 13, Core, Gravity, and constitutive transport remain locked.

STATUS:
- `{audit['status']}`; `numeric_alpha_emitted=false`; `holdout_used=false`.

WHAT_CHANGED:
- Added `{AUDIT_REL}` and its reproducible audit script. No equation, threshold, source role, or claim status was changed.

EQUATION_OR_MAPPING:
- `y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)`.
- `Delta_Tq = alpha_Phi_K * Delta_Phi`.
- `alpha_Phi_K = (E_ref/k_B) * alpha_Phi_theta` only after external E_ref and Phi normalization are supplied.

VERIFICATION:
- All `{len(audit['checks'])}` registry/provenance checks passed across `{len(audit['major_result']['evidence_artifacts'])}` evidence inputs.
- The audit emitted no numeric alpha, e0, or SI Phi map and did not access Xie 2026 or fit a target curve.

CONTROLLING_BLOCKER:
- `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`.

NEXT_ACTION:
- Obtain a declared dimensionful action/free-energy anchor or an independent paired base-Phi/SI response record; then rerun the input-package audit and full gate after the source hash changes.

CLAIM_BOUNDARY:
- This is a scoped negative registry audit. It rules out a hidden anchor in the audited canonical inputs, not a future derivation or independent calibration, and does not close Full Topic 13.

EVIDENCE_PATHS:
- `{AUDIT_REL}`
- `docs/scripts/audit/audit_topic13_base_phi_registry_completeness.py`

EVIDENCE_HASH:
- `{digest(AUDIT_REL)}`
"""
    UPDATE_LOG.write_text(current.rstrip() + "\n\n" + entry.rstrip() + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "PASS_T13_BASE_PHI_REGISTRY_AUDIT_RECORDED",
                "audit_sha256": digest(AUDIT_REL),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
