"""Record the central Phi equation-registry boundary audit in the topic log."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT_REL = "docs/core/artifacts/t13_phi_equation_registry_mapping_boundary_audit.json"
UPDATE_LOG = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md"
MARKER = "### 2026-08-24 - Topic 13 Phi equation-registry mapping boundary audit"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> int:
    audit = json.loads((ROOT / AUDIT_REL).read_text(encoding="utf-8"))
    current = UPDATE_LOG.read_text(encoding="utf-8")
    if MARKER in current:
        print(json.dumps({"status": "PASS_T13_PHI_REGISTRY_BOUNDARY_ALREADY_LOGGED"}))
        return 0

    entry = f"""{MARKER}

MAJOR_RESULT_CLOSURE:
- `T13_PHI_EQUATION_REGISTRY_MAPPING_BOUNDARY` is `CLOSED_FOR_LANE`; the dimensionful Phi-to-observable result remains open.

WHAT_IS_ACTUALLY_CLOSED:
- The central registry contains `{audit['major_result']['units']['registry_entry_count']}` entries, including `{audit['major_result']['units']['Phi_entry_count']}` entries that mention Phi.
- The thermal registry entry and active-lane register agree that the normalized TTG operator is defined while the dimensional map and alpha_Phi_K remain blocked.
- No current Phi entry declares an accepted SI mapping; the covariant parent remains natural-only.

WHAT_REMAINS_OPEN:
- `base_phi_si_anchor`, `independent_alpha_record`, `normalized_beta_si_map`, and downstream physical EOS/heat-flux results remain open.

DEPENDENCY_UNLOCKED:
- None. This closes only the registry boundary and does not unlock Full Topic 13, Core, Gravity, or constitutive transport.

STATUS:
- `{audit['status']}`; `holdout_used=false`; no numeric alpha emitted.

WHAT_CHANGED:
- Added `{AUDIT_REL}` and its reproducible audit script. No equation, threshold, ontology, source role, or claim status was changed.

EQUATION_OR_MAPPING:
- Registry thermal entry: `y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)` and `Delta_Tq = alpha_Phi_K * Delta_Phi`.
- Registered status remains `NORMALIZED_DEFINED_DIMENSIONAL_BLOCKED`; covariant parent remains `natural_only_v1`.

VERIFICATION:
- All `{len(audit['checks'])}` registry consistency checks passed across `{len(audit['major_result']['evidence_artifacts'])}` evidence artifacts.
- No target fit, Landauer inference, or Xie 2026 holdout access was used.

CONTROLLING_BLOCKER:
- `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`.

NEXT_ACTION:
- Register a dimensionful Phi/observable map only after derivation or independent calibration supplies units, uncertainty, and source provenance; then rerun the input-package and full gates.

CLAIM_BOUNDARY:
- Scoped registry boundary only. This does not prove a future anchor impossible and does not close Full Topic 13.

EVIDENCE_PATHS:
- `{AUDIT_REL}`
- `docs/scripts/audit/audit_topic13_phi_equation_registry_boundary.py`

EVIDENCE_HASH:
- `{digest(AUDIT_REL)}`
"""
    UPDATE_LOG.write_text(current.rstrip() + "\n\n" + entry.rstrip() + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "PASS_T13_PHI_REGISTRY_BOUNDARY_RECORDED",
                "audit_sha256": digest(AUDIT_REL),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
