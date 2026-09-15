"""Generate Wave 11 downstream application unlock decisions."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "docs/core/artifacts"
PHASE = ROOT / "docs/topics/0.11_Phase_Transitions/Result/artifacts/0_11_matter_space_phase_coupling_diagnostic.json"
THERMAL = ROOT / "docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/matter_space_thermal_control.json"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_artifacts() -> tuple[dict, dict]:
    now = datetime.now(timezone.utc).isoformat()
    phase, thermal = _read(PHASE), _read(THERMAL)
    wave8 = _read(CORE / "uet_main_theory_wave8_gate.json")
    wave9 = _read(CORE / "uet_main_theory_wave9_gate.json")
    fundamental = _read(CORE / "uet_fundamental_track_gate.json")
    decisions = {
        "thermal_internal_diagnostic": {"status": "BLOCKED", "controller": thermal["controlling_blocker"], "allowed": "synthetic analytical control only"},
        "thermal_external_comparison": {"status": "BLOCKED", "controller": wave8["controlling_blockers"], "allowed": "source metadata and normalized observable definition only"},
        "phase_internal_diagnostic": {"status": "PASS_INTERNAL_ONLY" if phase["verification_status"] == "PASS" else "BLOCKED", "controller": phase["controller"], "allowed": "normalized mechanism diagnostic"},
        "phase_external_or_universality": {"status": "BLOCKED", "controller": phase["controller"], "allowed": "none"},
        "fluid_vacuum_covariant_stress": {"status": "BLOCKED", "controller": ["dimensional_observable_closure", "curved_3p1_evolution"], "allowed": "internal constitutive controls"},
        "gravity_orbit": {"status": "BLOCKED", "controller": wave9["controlling_blockers"], "allowed": "analytic GR tensor-input controls"},
        "galaxy_cosmology": {"status": "BLOCKED", "controller": ["gravity_orbit", "metric_observable_uncertainty_holdout"], "allowed": "legacy/internal comparison only"},
        "particle_dirac": {"status": "BLOCKED", "controller": fundamental["controlling_blockers"], "allowed": "standard photon baseline and tree-level O2 controls"},
    }
    checks = {
        "phase_not_overpromoted": decisions["phase_external_or_universality"]["status"] == "BLOCKED",
        "thermal_not_overpromoted": decisions["thermal_external_comparison"]["status"] == "BLOCKED",
        "gravity_not_overpromoted": decisions["gravity_orbit"]["status"] == "BLOCKED",
        "galaxy_not_overpromoted": decisions["galaxy_cosmology"]["status"] == "BLOCKED",
        "particle_not_overpromoted": decisions["particle_dirac"]["status"] == "BLOCKED",
        "one_internal_phase_lane_visible": decisions["phase_internal_diagnostic"]["status"] == "PASS_INTERNAL_ONLY",
    }
    audit = {
        "schema_version": "1.0", "artifact": "uet_downstream_unlock_gate",
        "generated_at": now, "audit_status": "PASS" if all(checks.values()) else "FAIL",
        "decisions": decisions, "checks": checks,
        "input_identity": {
            PHASE.relative_to(ROOT).as_posix(): _sha(PHASE),
            THERMAL.relative_to(ROOT).as_posix(): _sha(THERMAL),
            "docs/core/07_artifacts/gates/uet_main_theory_wave8_gate.json": _sha(CORE / "uet_main_theory_wave8_gate.json"),
            "docs/core/07_artifacts/gates/uet_main_theory_wave9_gate.json": _sha(CORE / "uet_main_theory_wave9_gate.json"),
            "docs/core/07_artifacts/gates/uet_fundamental_track_gate.json": _sha(CORE / "uet_fundamental_track_gate.json"),
        },
        "unlock_order": ["thermal/phase internal pilots", "fluid/vacuum/covariant stress-energy", "gravity/orbit", "galaxy/cosmology", "particle/Dirac"],
        "claim_boundary": "dependency decisions only; PASS_INTERNAL_ONLY is not physical or external validation",
    }
    wave = {
        "schema_version": "1.0", "artifact": "uet_main_theory_wave11_gate",
        "generated_at": now, "audit_status": audit["audit_status"],
        "downstream_unlock_status": "BLOCKED_EXCEPT_PHASE_INTERNAL_DIAGNOSTIC",
        "checks": checks, "decisions": decisions,
        "controlling_blocker": "dimensional_observable_curved_gr_and_fundamental_prerequisites_incomplete",
        "claim_promotion": False,
        "next_controller": "final closure audit must report each blocked category separately without averaging",
    }
    return audit, wave


def main() -> int:
    audit, wave = build_artifacts()
    for name, payload in (("uet_downstream_unlock_gate.json", audit), ("uet_main_theory_wave11_gate.json", wave)):
        (CORE / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"audit_status={wave['audit_status']}")
    print(f"downstream_unlock_status={wave['downstream_unlock_status']}")
    print(f"controlling_blocker={wave['controlling_blocker']}")
    return 0 if wave["audit_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
