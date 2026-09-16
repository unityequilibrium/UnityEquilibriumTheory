"""Generate Wave 10 fundamental-unification hypothesis gates."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from docs.core.core_paths import canonical_artifact_path

ARTIFACTS = ROOT / "docs/core/07_artifacts"


def _read(name: str) -> dict:
    return json.loads(canonical_artifact_path(name).read_text(encoding="utf-8"))


def _sha(name: str) -> str:
    return hashlib.sha256(canonical_artifact_path(name).read_bytes()).hexdigest()


def build_artifacts() -> tuple[dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    parent = _read("covariant_parent_verification.json")
    eos = _read("o2_finite_density_eos_verification.json")
    photon = _read("photon_observer_baseline_verification.json")
    gr = _read("uet_gr_research_program_gate.json")
    inventory = {
        "schema_version": "1.0", "artifact": "uet_fundamental_symmetry_inventory",
        "generated_at": now, "track_status": "HYPOTHESIS_TRACK",
        "components": {
            "lorentz_metric_parent": {"status": "INTERNAL_CONSERVATIVE_FORMULA", "evidence": "covariant_parent_verification.json"},
            "response_scalar": {"status": "CANDIDATE_EFFECTIVE_SCALAR", "evidence": "covariant_parent_verification.json"},
            "global_o2_scalar_matter": {"status": "INTERNAL_TREE_LEVEL", "evidence": "o2_finite_density_eos_verification.json"},
            "local_gauge_symmetry": {"status": "BLOCKED", "reason": "no local gauge group, connection, field strength, or Ward identity"},
            "dirac_spinor_action": {"status": "BLOCKED", "reason": "no spinor representation or covariant fermion parent action"},
            "c_p_t_cpt": {"status": "BLOCKED", "reason": "no complete field content and transformation convention"},
            "anomaly_cancellation": {"status": "BLOCKED", "reason": "no declared chiral spectrum"},
            "unitarity_ghost_tachyon": {"status": "PARTIAL_SCALAR_TREE_LEVEL_ONLY", "reason": "positive scalar kinetic/potential domain does not cover gauge, spinor, or loop sectors"},
            "renormalization": {"status": "BLOCKED", "reason": "no power counting, cutoff policy, counterterm basis, or loop audit"},
            "mass_generation": {"status": "BLOCKED_SM_IDENTITY", "reason": "effective scalar mass shift and O2 condensation do not derive Standard-Model masses"},
            "photon_source_detector": {"status": "STANDARD_BASELINE_ONLY", "evidence": "photon_observer_baseline_verification.json"},
            "neutrino_positron_uet_identity": {"status": "REJECTED_UNDERIVED", "reason": "R_gen is a derived trace, not a particle identity"},
        },
        "input_identity": {
            name: _sha(name) for name in (
                "covariant_parent_verification.json", "o2_finite_density_eos_verification.json",
                "photon_observer_baseline_verification.json", "uet_gr_research_program_gate.json")
        },
        "input_status_snapshot": {
            "parent": parent.get("audit_status"), "eos": eos.get("audit_status"),
            "photon": photon.get("audit_status", photon.get("status")),
            "gr_program": gr.get("status", gr.get("gate_status")),
        },
        "claim_boundary": "inventory of prerequisites; no fundamental unification derivation",
    }
    required = ("local_gauge_symmetry", "dirac_spinor_action", "c_p_t_cpt", "anomaly_cancellation", "renormalization", "mass_generation")
    checks = {
        "effective_parent_available": parent["audit_status"] == "PASS",
        "tree_level_o2_available": eos["audit_status"] == "PASS",
        "photon_kept_as_standard_baseline": inventory["components"]["photon_source_detector"]["status"] == "STANDARD_BASELINE_ONLY",
        "trace_particle_identity_rejected": inventory["components"]["neutrino_positron_uet_identity"]["status"] == "REJECTED_UNDERIVED",
        "all_fundamental_prerequisites_closed": all(inventory["components"][name]["status"] == "PASS" for name in required),
    }
    gate = {
        "schema_version": "1.0", "artifact": "uet_fundamental_track_gate",
        "generated_at": now, "audit_status": "PASS_ACCOUNTING" if all(checks[name] for name in ("effective_parent_available", "tree_level_o2_available", "photon_kept_as_standard_baseline", "trace_particle_identity_rejected")) else "FAIL",
        "fundamental_unification_status": "PASS" if checks["all_fundamental_prerequisites_closed"] else "HYPOTHESIS_TRACK_BLOCKED",
        "checks": checks,
        "controlling_blockers": [name for name in required if inventory["components"][name]["status"] != "PASS"],
        "primary_eft_dependency": "NON_BLOCKING",
        "claim_promotion": False,
        "next_controller": "declare a local symmetry and complete field representation before writing a Dirac/gauge parent action",
    }
    return inventory, gate


def main() -> int:
    inventory, gate = build_artifacts()
    for name, payload in (("uet_fundamental_symmetry_inventory.json", inventory), ("uet_fundamental_track_gate.json", gate), ("uet_main_theory_wave10_gate.json", {**gate, "artifact": "uet_main_theory_wave10_gate", "upstream_gate": "uet_main_theory_ontology_gate.json"})):
        canonical_artifact_path(name).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    print(f"audit_status={gate['audit_status']}")
    print(f"fundamental_unification_status={gate['fundamental_unification_status']}")
    print("controlling_blockers=" + ",".join(gate["controlling_blockers"]))
    return 0 if gate["audit_status"] == "PASS_ACCOUNTING" else 1


if __name__ == "__main__":
    raise SystemExit(main())
