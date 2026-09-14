"""Emit a focused energy/dissipation ledger artifact from the canonical core verifier."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.core.core_paths import canonical_artifact_path  # noqa: E402
from docs.scripts.audit.audit_matter_space_core import build_verification  # noqa: E402


OUTPUT = ROOT / canonical_artifact_path("matter_space_energy_ledger_verification.json", "verification")


def _metric(verification: dict[str, Any], name: str) -> dict[str, Any]:
    return verification["metrics"][name]


def build_artifact() -> dict[str, Any]:
    verification = build_verification()
    ledger_metrics = {
        name: _metric(verification, name)
        for name in (
            "minimum_dissipation_density",
            "closed_energy_increase",
            "ledger_closure",
            "open_space_ledger_closure",
            "trace_switch_invariance",
            "trace_history_no_backreaction",
        )
    }
    raw = verification["raw_diagnostics"]
    integrity = raw["closed_trajectory"]
    passed = all(entry["gate"] == "PASS" for entry in ledger_metrics.values()) and not any(
        integrity[key] for key in ("field_clipping_applied", "parameter_fitting_applied")
    )
    return {
        "schema_version": "matter-space-energy-ledger-verification-v1",
        "artifact": "matter_space_energy_ledger_verification",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed else "FAIL",
        "local_ledger_status": "PASS" if passed else "FAIL",
        "dependency_status": "BLOCKED" if verification["status"] != "PASS" else "NOT_AUTOMATIC",
        "operator_mode": verification["operator_mode"],
        "unit_lane": verification["run_contract"]["unit_lane"],
        "ledger_metrics": ledger_metrics,
        "raw_ledger_diagnostics": {
            "closed_trajectory": raw["closed_trajectory"],
            "open_space_drive": raw["open_space_drive"],
            "history_separation": raw["history_separation"],
        },
        "no_loss_language": {
            "normalized_ledger_only": True,
            "joule_claim": False,
            "trace_is_energy_reservoir": False,
            "environment_transfer_requires_dimensional_map": True,
        },
        "upstream_core_status": verification["status"],
        "upstream_core_controller": verification["controlling_blocker"],
        "claim_boundary": "normalized ledger verification only; not SI energy conservation or entropy proof",
        "next_controller": "repair compact causal-support discretization while preserving ledger and no-clipping gates",
    }


def main() -> int:
    artifact = build_artifact()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"local_ledger_status={artifact['local_ledger_status']}")
    print(f"dependency_status={artifact['dependency_status']}")
    print(f"upstream_core_controller={artifact['upstream_core_controller']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
